import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import uuid

from PySide6.QtCore import QLockFile
from PySide6.QtNetwork import QLocalSocket
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QColor
from PySide6.QtTest import QTest

from f7hub.domain.mochi_protocol import *
from f7hub.infrastructure.mochi_channel import CheckoutIdentity, Channel
from f7hub.infrastructure.mochi_gateway import MochiGateway
from f7hub.services.mochi_service import MochiService
from mochi.core.config import Settings
from mochi.pet.animation import Animation
from mochi.pet.animation_loader import LoadedAnimation
from mochi.services.pet_runtime import PetRuntime
from mochi.ui.pet_window import PetWindow
from mochi.integrations.local_server import LocalController


def wait_until(predicate, milliseconds=1000):
    for _ in range(milliseconds // 5):
        if predicate():
            return True
        QTest.qWait(5)
    return bool(predicate())


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.request = dict(version=1, request_id='r', controller_id='c', session_id='s',
                            checkout_id='checkout', command='wave', payload={})

    def test_valid_commands_and_round_trip(self):
        for command in COMMANDS:
            r = deepcopy(self.request)
            r['command'] = command
            if command == 'attach':
                r['payload'] = dict(greeting_requested=True, connection_generation=1)
            self.assertEqual(validate_request(decode(encode(r)[:-1]), 'checkout'), r)

    def test_malformed_utf8_json_top_level_and_duplicate_fields(self):
        for raw in (b'\xff', b'{', b'[]', b'null', b'1', b'{"a":1,"a":2}', b'{"a":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ProtocolError):
                decode(raw)

    def test_full_schema_rejects_types_ids_commands_and_payloads(self):
        changes = [('version', True), ('version', 2), ('request_id', ''), ('request_id', 'x'*65),
                   ('controller_id', '../x'), ('session_id', 3), ('checkout_id', 'wrong'),
                   ('command', 'execute'), ('command', []), ('payload', []), ('payload', {'extra': 1})]
        for field, value in changes:
            with self.subTest(field=field, value=value), self.assertRaises(ProtocolError):
                validate_request({**self.request, field: value}, 'checkout')
        for r in ({k:v for k,v in self.request.items() if k != 'request_id'}, {**self.request, 'extra': 1}):
            with self.assertRaises(ProtocolError):
                validate_request(r, 'checkout')

    def test_attach_payload_strict_boolean_and_generation(self):
        r = {**self.request, 'command': 'attach'}
        for p in ({}, {'greeting_requested': 1, 'connection_generation': 1},
                  {'greeting_requested': True, 'connection_generation': True},
                  {'greeting_requested': True, 'connection_generation': 0},
                  {'greeting_requested': True, 'connection_generation': 1, 'extra': False}):
            with self.assertRaises(ProtocolError):
                validate_request({**r, 'payload': p}, 'checkout')

    def test_partial_coalesced_frames_and_size_boundaries(self):
        f = Framer()
        raw = encode(self.request)
        self.assertEqual(f.feed(raw[:5]), [])
        self.assertEqual(len(f.feed(raw[5:] + raw)), 2)
        self.assertFalse(f.buffer)
        self.assertEqual(Framer().feed(b'x'*(MAX_MESSAGE-1)+b'\n'), [b'x'*(MAX_MESSAGE-1)])
        for raw in (b'x'*MAX_MESSAGE, b'x'*MAX_MESSAGE+b'\n', b'{}\n'*(MAX_QUEUE+1)):
            with self.assertRaises(ProtocolError):
                Framer().feed(raw)


class LocalControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = CheckoutIdentity.from_root(self.root)
        idle = Animation((Path('i0'), Path('i1')), 120)
        wave = Animation(tuple(Path(f'w{i}') for i in range(4)), 120)
        images = tuple(QImage(24, 30, QImage.Format.Format_ARGB32) for _ in range(4))
        for image in images:
            image.fill(QColor('red'))
        self.runtime = PetRuntime(idle, wave)
        self.window = PetWindow(Settings(), LoadedAnimation(idle, images[:2]), self.runtime,
                                LoadedAnimation(wave, images))
        self.window.start()
        self.window.show()
        self.server = LocalController(self.identity, self.window)
        self.assertTrue(self.server.listen())
        self.services = []
        self.sockets = []

    def tearDown(self):
        self.window.shutdown()
        for s in self.services:
            s.close()
        for s in self.sockets:
            s.abort()
            s.deleteLater()
        self.server.close()
        self.server.deleteLater()
        self.window.deleteLater()
        self.app.processEvents()

    def service(self):
        gateway = MochiGateway(self.root)
        gateway.launch = lambda: self.fail('Attach-first must not launch with ready runtime')
        service = MochiService(gateway)
        self.services.append(service)
        service.automatic_start()
        self.assertTrue(wait_until(lambda: gateway.attached))
        return service

    def command(self, service, command):
        self.assertTrue(service.command(command))
        self.assertTrue(wait_until(lambda: not service.busy))

    def socket(self):
        socket = QLocalSocket()
        self.sockets.append(socket)
        socket.connectToServer(self.identity.endpoint)
        self.assertTrue(wait_until(lambda: socket.state() == QLocalSocket.LocalSocketState.ConnectedState))
        self.app.processEvents()
        return socket

    def request(self, command='attach', payload=None):
        return dict(version=1, request_id=uuid.uuid4().hex, controller_id='raw', session_id='rawsession',
                    checkout_id=self.identity.checkout_id, command=command,
                    payload=payload if payload is not None else dict(greeting_requested=False, connection_generation=1))

    def test_first_attach_greeting_and_status_updates_return_idle(self):
        service = self.service()
        self.assertTrue(service.greeting_consumed)
        self.assertEqual(self.runtime.state.name, 'WAVE')
        for _ in range(4):
            self.window._advance()
        self.assertEqual(self.runtime.state.name, 'IDLE')
        self.assertTrue(wait_until(lambda: service.snapshot['behavior'] == 'IDLE'))
        self.command(service, 'status')

    def test_commands_and_hidden_paused_restoration(self):
        service = self.service()
        for command in ('wave', 'idle', 'wave', 'pause', 'hide', 'show', 'resume', 'idle'):
            self.command(service, command)
            self.assertIn(service.last_outcome, ('CHANGED', 'UNCHANGED'))
        self.command(service, 'pause')
        self.command(service, 'hide')
        frame = self.runtime.frame_index
        service.close()
        self.assertTrue(wait_until(lambda: self.runtime.visible))
        self.assertEqual(self.runtime.state.name, 'PAUSED')
        self.assertEqual(self.runtime.frame_index, frame)

    def test_two_controllers_final_hidden_disconnect(self):
        first, second = self.service(), self.service()
        self.assertEqual(self.server.controller_count, 2)
        self.command(first, 'hide')
        first.close()
        self.assertTrue(wait_until(lambda: self.server.controller_count == 1))
        self.assertFalse(self.runtime.visible)
        second.close()
        self.assertTrue(wait_until(lambda: self.runtime.visible))
        self.assertEqual(self.server.controller_count, 0)

    def test_final_visible_disconnect_and_exiting_do_not_restore(self):
        service = self.service()
        self.command(service, 'idle')
        before = self.runtime.snapshot(self.identity.checkout_id)
        service.close()
        self.assertTrue(wait_until(lambda: self.server.controller_count == 0))
        self.assertEqual(self.runtime.snapshot(self.identity.checkout_id), before)
        service = self.service()
        self.command(service, 'hide')
        self.runtime.exit()
        service.close()
        self.assertTrue(wait_until(lambda: self.server.controller_count == 0))
        self.assertFalse(self.runtime.visible)

    def test_unvalidated_connections_do_not_enable_hide(self):
        self.socket()
        self.assertEqual(self.server.controller_count, 0)
        self.assertEqual(self.window.apply('hide', self.server.controller_count), 'NO_CONTROLLER')
        self.assertTrue(self.runtime.visible)

    def test_reconnect_lost_attach_ack_and_empty_new_runtime_do_not_regreet(self):
        original = self.server.reply
        self.server.reply = lambda c,r,o: None if o == 'ATTACHED' else original(c,r,o)
        gateway = MochiGateway(self.root)
        gateway.command_deadline.setInterval(40)
        gateway.launch = lambda: True
        service = MochiService(gateway)
        self.services.append(service)
        service.automatic_start()
        self.assertTrue(wait_until(lambda: service.greeting_consumed))
        self.assertTrue(wait_until(lambda: self.runtime.state.name == 'WAVE'))
        self.assertEqual(self.runtime.state.name, 'WAVE')
        for _ in range(4):
            self.window._advance()
        self.server.reply = original
        self.runtime.greeted_sessions.clear()  # restart/eviction cannot renew F7Hub eligibility
        self.assertTrue(wait_until(lambda: gateway.attached))
        self.assertEqual(self.runtime.state.name, 'IDLE')
        gateway._unavailable('UNAVAILABLE')
        service.start_show()
        self.assertTrue(wait_until(lambda: gateway.attached and not gateway.busy))
        self.assertEqual(self.runtime.state.name, 'IDLE')

    def test_duplicate_greeting_attach_and_identity_binding(self):
        socket = self.socket()
        request = self.request(payload=dict(greeting_requested=True, connection_generation=1))
        socket.write(encode(request))
        self.assertTrue(wait_until(lambda: self.server.controller_count == 1))
        for _ in range(4):
            self.window._advance()
        request['request_id'] = uuid.uuid4().hex
        socket.write(encode(request))
        QTest.qWait(20)
        self.assertEqual(self.runtime.state.name, 'IDLE')
        request['controller_id'] = 'different'
        socket.write(encode(request))
        self.assertTrue(wait_until(lambda: self.server.controller_count == 0))

    def test_lost_mutation_ack_reconciles_without_replay(self):
        service = self.service()
        self.command(service, 'idle')
        original = self.server.reply
        mutations = []
        apply = self.window.apply
        self.window.apply = lambda c,n=0: (mutations.append(c), apply(c,n))[1]
        self.server.reply = lambda c,r,o: None if o == 'CHANGED' else original(c,r,o)
        service.gateway.command_deadline.setInterval(40)
        service.command('wave')
        self.assertTrue(wait_until(lambda: service.last_outcome == 'UNCERTAIN'))
        self.assertTrue(wait_until(lambda: service.gateway.attached and not service.busy))
        self.assertEqual(mutations.count('wave'), 1)
        self.assertEqual(service.snapshot['behavior'], 'WAVE')

    def test_stale_generation_and_request_cannot_replace_snapshot(self):
        service = self.service()
        gateway = service.gateway
        before = deepcopy(service.snapshot)
        stale = dict(version=1, request_id='event', runtime_id=gateway.runtime_id,
                     connection_generation=gateway.connection_generation-1, ok=True,
                     outcome='STATE', snapshot={**before, 'visibility':'HIDDEN'})
        gateway._response(gateway.connection_generation-1, stale)
        self.assertEqual(service.snapshot, before)
        stale['connection_generation'] = gateway.connection_generation
        stale['request_id'] = 'unknown'
        gateway._response(gateway.connection_generation, stale)
        self.assertEqual(service.snapshot, before)

    def test_partial_attach_then_coalesced_status(self):
        socket = self.socket()
        raw = encode(self.request())
        socket.write(raw[:8])
        QTest.qWait(10)
        self.assertEqual(self.server.controller_count, 0)
        socket.write(raw[8:])
        self.assertTrue(wait_until(lambda: self.server.controller_count == 1))
        socket.write(encode(self.request('status', {})) + encode(self.request('status', {})))
        self.assertTrue(wait_until(lambda: socket.bytesAvailable() > 0))

    def test_invalid_input_disconnects_before_mutation(self):
        for raw in (b'\xff\n', b'[]\n', encode({**self.request(), 'extra':1}),
                    encode({**self.request(), 'checkout_id':'wrong'}), b'x'*4096,
                    b'x'*4096+b'\n', encode(self.request('wave', {}))):
            socket = self.socket()
            before = self.runtime.snapshot(self.identity.checkout_id)
            socket.write(raw)
            self.assertTrue(wait_until(lambda: socket.state() == QLocalSocket.LocalSocketState.UnconnectedState))
            self.assertEqual(self.runtime.snapshot(self.identity.checkout_id), before)

    def test_incomplete_and_unvalidated_deadlines(self):
        socket = self.socket()
        client = next(c for c in self.server.clients.values() if c['socket'].state() == QLocalSocket.LocalSocketState.ConnectedState)
        channel = next(c for c in self.server.clients if self.server.clients[c] is client)
        channel.deadline.setInterval(25)
        socket.write(b'{')
        self.assertTrue(wait_until(lambda: socket.state() == QLocalSocket.LocalSocketState.UnconnectedState))
        socket = self.socket()
        for client in self.server.clients.values():
            client['deadline'].start(25)
        self.assertTrue(wait_until(lambda: socket.state() == QLocalSocket.LocalSocketState.UnconnectedState))

    def test_connection_read_buffer_and_request_queue_caps(self):
        sockets = [self.socket() for _ in range(MAX_CONNECTIONS)]
        extra = QLocalSocket()
        self.sockets.append(extra)
        extra.connectToServer(self.identity.endpoint)
        QTest.qWait(30)
        self.assertEqual(len(self.server.clients), MAX_CONNECTIONS)
        self.assertEqual(self.server.server.maxPendingConnections(), MAX_CONNECTIONS)
        self.assertTrue(all(c['socket'].readBufferSize() == READ_BUFFER for c in self.server.clients.values()))
        socket = sockets[0]
        socket.write(encode(self.request()))
        self.assertTrue(wait_until(lambda: self.server.controller_count == 1))
        before = self.runtime.snapshot(self.identity.checkout_id)
        socket.write(b''.join(encode(self.request('wave', {})) for _ in range(MAX_QUEUE+1)))
        self.assertTrue(wait_until(lambda: socket.state() == QLocalSocket.LocalSocketState.UnconnectedState))
        self.assertEqual(self.runtime.snapshot(self.identity.checkout_id), before)

    def test_hide_eligibility_rechecked_at_dispatch(self):
        service = self.service()
        self.command(service, 'idle')
        channel = next(iter(self.server.clients))
        request = dict(version=1, request_id='race', controller_id=service.gateway.controller_id,
                       session_id=service.session_id, checkout_id=self.identity.checkout_id, command='hide', payload={})
        self.server.enqueue(channel, request)
        service.close()
        self.assertTrue(wait_until(lambda: self.server.controller_count == 0))
        self.assertTrue(self.runtime.visible)

    def test_singleton_contended_and_release(self):
        Path(self.identity.lock_path).parent.mkdir(parents=True, exist_ok=True)
        lock = QLockFile(self.identity.lock_path)
        lock.setStaleLockTime(0)
        self.assertTrue(lock.tryLock(0))
        duplicate = QLockFile(self.identity.lock_path)
        duplicate.setStaleLockTime(0)
        self.assertFalse(duplicate.tryLock(0))
        lock.unlock()
        self.assertTrue(duplicate.tryLock(0))
        duplicate.unlock()
