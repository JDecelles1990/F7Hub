"""Validated persistent controllers; all dispatch runs on the Qt event loop."""

from collections import deque
import time
import uuid

from PySide6.QtCore import QObject, QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from f7hub.domain.mochi_protocol import (VERSION, MAX_CONNECTIONS, MAX_QUEUE, COMMAND_MS,
                                       ProtocolError, validate_request)
from f7hub.infrastructure.mochi_channel import Channel


class LocalController(QObject):
    def __init__(self, identity, window, parent=None):
        super().__init__(parent)
        self.identity, self.window = identity, window
        self.runtime_id = uuid.uuid4().hex
        self.clients = {}
        self.server = QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        self.server.setMaxPendingConnections(MAX_CONNECTIONS)
        self.server.newConnection.connect(self.accept)
        self.dispatch = QTimer(self)
        self.dispatch.setSingleShot(True)
        self.dispatch.timeout.connect(self.drain)
        window.state_changed.connect(self.broadcast)

    @property
    def controller_count(self):
        return sum(c['registration'] is not None and
                   c['socket'].state() == QLocalSocket.LocalSocketState.ConnectedState
                   for c in self.clients.values())

    def listen(self):
        return self.server.listen(self.identity.endpoint)

    def accept(self):
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            if len(self.clients) >= MAX_CONNECTIONS:
                socket.abort()
                socket.deleteLater()
                continue
            channel = Channel(socket, self)
            attach_deadline = QTimer(channel)
            attach_deadline.setSingleShot(True)
            attach_deadline.setInterval(COMMAND_MS)
            attach_deadline.timeout.connect(channel.reject)
            attach_deadline.start()
            self.clients[channel] = {'socket': socket, 'registration': None, 'generation': 1,
                                     'queue': deque(), 'deadline': attach_deadline, 'last_request': None}
            channel.message.connect(lambda value, c=channel: self.enqueue(c, value))
            socket.disconnected.connect(lambda c=channel: self.remove(c))
            channel.failed.connect(lambda c=channel: self.remove(c))
            channel.read()

    def enqueue(self, channel, value):
        client = self.clients.get(channel)
        if client is None:
            return
        try:
            validate_request(value, self.identity.checkout_id)
        except ProtocolError:
            channel.reject()
            return
        if len(client['queue']) >= MAX_QUEUE:
            channel.reject()
            return
        client['queue'].append((time.monotonic() + COMMAND_MS / 1000, value))
        if not self.dispatch.isActive():
            self.dispatch.start(0)

    def drain(self):
        # One synchronous mutation at a time, no nested event loop or external work.
        for channel, client in tuple(self.clients.items()):
            if channel not in self.clients or not client['queue']:
                continue
            expiry, value = client['queue'].popleft()
            if time.monotonic() >= expiry or channel.closed:
                channel.reject()
                continue
            registration = (value['controller_id'], value['session_id'])
            command = value['command']
            if command == 'attach':
                if client['registration'] is not None and client['registration'] != registration:
                    channel.reject()
                    continue
                if self.window.runtime.state.name == 'EXITING':
                    self.reply(channel, value['request_id'], 'EXITING')
                    continue
                client['registration'] = registration
                client['generation'] = value['payload']['connection_generation']
                client['deadline'].stop()
                if value['payload']['greeting_requested']:
                    self.window.greet(value['session_id'])
                outcome = 'ATTACHED'
            elif client['registration'] != registration:
                channel.reject()
                continue
            elif client['last_request'] == value['request_id']:
                channel.reject()
                continue
            elif command == 'status':
                outcome = 'STATUS'
            else:
                outcome = self.window.apply(command, self.controller_count)
            client['last_request'] = value['request_id']
            self.reply(channel, value['request_id'], outcome)
        if any(c['queue'] for c in self.clients.values()):
            self.dispatch.start(0)

    def reply(self, channel, request_id, outcome):
        client = self.clients.get(channel)
        if client is None:
            return
        channel.send({'version': VERSION, 'request_id': request_id, 'runtime_id': self.runtime_id,
                      'connection_generation': client['generation'],
                      'ok': outcome in ('ATTACHED', 'STATUS', 'STATE', 'CHANGED', 'UNCHANGED'),
                      'outcome': outcome, 'snapshot': self.window.runtime.snapshot(self.identity.checkout_id)})

    def broadcast(self):
        for channel, client in tuple(self.clients.items()):
            if client['registration'] is not None:
                self.reply(channel, 'event', 'STATE')

    def remove(self, channel):
        client = self.clients.pop(channel, None)
        if client is None:
            return
        client['deadline'].stop()
        channel.deadline.stop()
        if (client['registration'] is not None and self.controller_count == 0 and
                self.window.runtime.state.name != 'EXITING' and not self.window.runtime.visible):
            self.window.apply('show')
        client['socket'].deleteLater()
        channel.deleteLater()

    def close(self):
        self.dispatch.stop()
        self.server.close()
        for channel in tuple(self.clients):
            channel.reject()
