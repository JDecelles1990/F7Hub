"""Application-owned asynchronous local socket and coalesced detached startup."""

from pathlib import Path
import sys
import uuid
import logging

from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from PySide6.QtNetwork import QLocalSocket

from f7hub.domain.mochi_protocol import (VERSION, COMMANDS, MUTATIONS, COMMAND_MS, STARTUP_MS,
                                       ProtocolError, validate_response)
from f7hub.infrastructure.mochi_channel import Channel, CheckoutIdentity


class MochiGateway(QObject):
    changed = Signal(object)
    completed = Signal(str, str)
    availability = Signal(str)
    busy_changed = Signal(bool)

    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = Path(root).resolve()
        try:
            self.identity = CheckoutIdentity.from_root(self.root)
        except (OSError, ValueError) as error:
            logging.getLogger('f7hub.mochi').warning('Mochi identity unavailable; exception_type=%s', type(error).__name__)
            self.identity = None
        self.controller_id = uuid.uuid4().hex
        self.connection_generation = 0
        self.runtime_id = None
        self.socket = None
        self.channel = None
        self.pending = None
        self.attached = False
        self.starting = False
        self.closed = False
        self.busy = False
        self.session_id = None
        self.greeting_supplier = None
        self._want_show = False
        self._allow_launch = False
        self._launched = False
        self.launched_pid = None
        self._reconcile = False
        self._ignore_disconnect = False
        self.command_deadline = QTimer(self)
        self.command_deadline.setSingleShot(True)
        self.command_deadline.setInterval(COMMAND_MS)
        self.command_deadline.timeout.connect(self._timeout)
        self.readiness = QTimer(self)
        self.readiness.setSingleShot(True)
        self.readiness.setInterval(STARTUP_MS)
        self.readiness.timeout.connect(lambda: self._unavailable('TIMEOUT'))
        self.retry = QTimer(self)
        self.retry.setSingleShot(True)
        self.retry.setInterval(100)
        self.retry.timeout.connect(self._connect)
        self.connect_deadline = QTimer(self)
        self.connect_deadline.setSingleShot(True)
        self.connect_deadline.setInterval(250)
        self.connect_deadline.timeout.connect(self._connect_failed)

    def _busy(self, value):
        self.busy = value
        self.busy_changed.emit(value)

    def start(self, session_id, greeting_supplier, *, show=False, allow_launch=True):
        if self.closed or self.busy:
            return False
        if self.identity is None:
            self._unavailable('UNAVAILABLE')
            return False
        self.session_id, self.greeting_supplier = session_id, greeting_supplier
        if allow_launch:
            self._reconcile = False
        if self.attached and self.socket is not None and self.socket.state() == QLocalSocket.LocalSocketState.ConnectedState:
            return self.send('show' if show else 'status')
        self.attached = False
        self.starting = True
        self._want_show, self._allow_launch, self._launched = show, allow_launch, False
        self._busy(True)
        self.availability.emit('CONNECTING')
        self.readiness.start()
        self._connect()
        return True

    def _discard_socket(self):
        self._ignore_disconnect = True
        if self.channel is not None:
            self.channel.closed = True
            self.channel.deadline.stop()
            self.channel.deleteLater()
        if self.socket is not None:
            self.socket.abort()
            self.socket.deleteLater()
        self.socket = self.channel = None
        self.attached = False
        self.runtime_id = None
        self._ignore_disconnect = False

    def _connect(self):
        if not self.starting or self.closed:
            return
        self._discard_socket()
        self.connection_generation += 1
        generation = self.connection_generation
        socket = QLocalSocket(self)
        self.socket = socket
        self.channel = Channel(socket, self)
        self.channel.message.connect(lambda value, g=generation: self._response(g, value))
        socket.connected.connect(lambda g=generation: self._connected(g))
        socket.errorOccurred.connect(lambda _error, g=generation: self._connect_failed(g))
        socket.disconnected.connect(lambda g=generation: self._disconnected(g))
        self.channel.failed.connect(lambda g=generation: self._disconnected(g))
        self.connect_deadline.start()
        socket.connectToServer(self.identity.endpoint)

    def _connected(self, generation):
        if generation != self.connection_generation or not self.starting or self.closed:
            return
        self.connect_deadline.stop()
        # Supplier consumes the application opportunity before any write.
        self._request('attach', {'greeting_requested': self.greeting_supplier(),
                                'connection_generation': generation})

    def _connect_failed(self, generation=None):
        if generation is not None and generation != self.connection_generation:
            return
        if not self.starting or self.closed or self.retry.isActive():
            return
        self.connect_deadline.stop()
        if self.pending is not None:
            self.command_deadline.stop()
            self.pending = None
        self._discard_socket()
        if self._allow_launch and not self._launched:
            self._launched = True  # record before launch; never a second launch in this attempt
            if not self.launch():
                self._unavailable('LAUNCH_FAILED')
                return
        self.retry.start()

    def launch(self):
        result = QProcess.startDetached(sys.executable, ['-B', str(self.root / 'Mochi' / 'src' / 'main.py')], str(self.root))
        if isinstance(result, tuple) and result[0]:
            self.launched_pid = result[1]
        return result[0] if isinstance(result, tuple) else result

    def _request(self, command, payload=None):
        request_id = uuid.uuid4().hex
        self.pending = (request_id, command)
        self.command_deadline.start()
        sent = self.channel.send({'version': VERSION, 'request_id': request_id,
                                  'controller_id': self.controller_id, 'session_id': self.session_id,
                                  'checkout_id': self.identity.checkout_id, 'command': command,
                                  'payload': {} if payload is None else payload})
        if not sent and self.pending is not None:
            self._disconnected(self.connection_generation)

    def send(self, command):
        if self.closed or self.busy or not self.attached or command not in COMMANDS or command == 'attach':
            return False
        self._busy(True)
        self._request(command)
        return True

    def _response(self, generation, value):
        if generation != self.connection_generation or self.closed:
            return
        try:
            validate_response(value, self.identity.checkout_id)
        except (ProtocolError, TypeError):
            self.channel.reject()
            return
        if value['connection_generation'] != generation:
            return
        if self.runtime_id is not None and value['runtime_id'] != self.runtime_id:
            return
        if value['request_id'] == 'event' and value['outcome'] == 'STATE':
            if self.attached:
                self.changed.emit(value['snapshot'])
            return
        if self.pending is None or value['request_id'] != self.pending[0]:
            return
        command = self.pending[1]
        self.pending = None
        self.command_deadline.stop()
        if command == 'attach':
            if value['outcome'] != 'ATTACHED' or not value['ok']:
                self._unavailable('UNAVAILABLE')
                return
            self.runtime_id = value['runtime_id']
            self.attached = True
            self.starting = False
            self.readiness.stop()
            self.retry.stop()
            self._busy(False)
            self.availability.emit('AVAILABLE')
            self.changed.emit(value['snapshot'])
            if self._reconcile:
                self._reconcile = False
                self.send('status')
            elif self._want_show:
                self.send('show')
            return
        self.changed.emit(value['snapshot'])
        self._busy(False)
        self.completed.emit(command, value['outcome'])

    def _timeout(self):
        if self.pending is None:
            return
        command = self.pending[1]
        self.pending = None
        if command == 'attach' and self.starting:
            self._connect_failed()
        elif command in MUTATIONS:
            self._uncertain(command)
        else:
            self._unavailable('TIMEOUT')

    def _uncertain(self, command):
        self._busy(False)
        self.completed.emit(command, 'UNCERTAIN')
        self._discard_socket()
        # No mutation replay and no process launch during reconciliation. Exit is
        # deliberately left uncertain unless a terminal reply was received.
        self._reconcile = True
        self.start(self.session_id, self.greeting_supplier, allow_launch=False)

    def _disconnected(self, generation):
        if self._ignore_disconnect or self.closed or generation != self.connection_generation:
            return
        self.attached = False
        if self.pending is not None and self.pending[1] in MUTATIONS:
            command = self.pending[1]
            self.pending = None
            self.command_deadline.stop()
            self._uncertain(command)
        elif self.starting:
            self._connect_failed(generation)
        else:
            self._unavailable('UNAVAILABLE')

    def _unavailable(self, outcome):
        self.starting = False
        self.pending = None
        for timer in (self.command_deadline, self.readiness, self.retry, self.connect_deadline):
            timer.stop()
        self._discard_socket()
        self._busy(False)
        self.availability.emit(outcome)

    def close(self):
        self.closed = True
        self._unavailable('DISCONNECTED')
