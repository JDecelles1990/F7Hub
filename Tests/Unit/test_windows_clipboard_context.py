"""Synthetic security checks; these observations do not prove native enrollment."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import struct
import unittest
from unittest.mock import Mock, patch

from f7hub.infrastructure import windows_clipboard_context as m
from f7hub.infrastructure.clipboard_native_session import EnrollmentContext, RetirementIdentity


USER = b'\x01\x01' + bytes(5) + b'\x05' + struct.pack('<I', 21)
LOGON = b'\x01\x03' + bytes(5) + b'\x05' + struct.pack('<III', 5, 100, 200)
MEDIUM = b'\x01\x01' + bytes(5) + b'\x10' + struct.pack('<I', 8192)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(server_handle=100, child_handle=200,
                         server_pin=(10, 1000), child_pin=(20, 2000))
        self.api = Mock()
        self.api.pin.side_effect = lambda h: self.args['server_pin' if h == 100 else 'child_pin']
        self.api.security.return_value = (3, USER, LOGON)
        self.patcher = patch.object(m, '_WindowsAPI', return_value=self.api)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def read(self, **changes):
        return m.read_pinned_context(b'G' * 16, **(self.args | changes))

    def denied(self, callback):
        with self.assertRaisesRegex(m.NativeContextError, '^NATIVE_CONTEXT_REJECTED$'):
            callback()

    def test_exact_adopted_layout_and_existing_policy_compatibility(self):
        raw = self.read()
        expected = b'G' * 16 + struct.pack('<IQIQI', 10, 1000, 20, 2000, 3)
        expected += hashlib.sha256(USER).digest() + hashlib.sha256(LOGON).digest()
        expected += struct.pack('<I', 8192)
        self.assertEqual(raw, expected)
        self.assertEqual(len(raw), 112)
        identity = RetirementIdentity(b'G' * 16, 20, 2000, 0, b'G' * 16, 0)
        EnrollmentContext(identity, b'K' * 32, raw)
        self.assertEqual(self.api.live.call_count, 4)

    def test_bad_generation_denied_before_api(self):
        for value in (None, b'', bytes(16), bytearray(b'G' * 16), b'G' * 17):
            with self.subTest(kind=type(value).__name__):
                self.denied(lambda: m.read_pinned_context(value, **self.args))
        self.api.pin.assert_not_called()

    def test_bad_handles_and_pseudo_handles_denied_before_api(self):
        for key in ('server_handle', 'child_handle'):
            for value in (None, 0, -1, -6, True, 1.0, 2**64, *range(2**64-6, 2**64)):
                with self.subTest(key=key, value=value):
                    self.denied(lambda: self.read(**{key: value}))
        self.api.pin.assert_not_called()

    def test_invalid_pins(self):
        for key in ('server_pin', 'child_pin'):
            for value in (None, [1, 2], (1,), (0, 1), (1, 0), (True, 1),
                          (1, True), (2**32, 1), (1, 2**64)):
                self.denied(lambda: self.read(**{key: value}))

    def test_same_process_or_handle_denied(self):
        self.denied(lambda: self.read(child_handle=100))
        self.denied(lambda: self.read(child_pin=(10, 9999)))

    def test_pid_or_creation_mismatch_denied(self):
        for observed in ((99, 1000), (10, 1001)):
            self.api.pin.side_effect = None
            self.api.pin.return_value = observed
            self.denied(self.read)
        self.api.security.assert_not_called()

    def test_security_mismatches_denied(self):
        for child in ((4, USER, LOGON), (3, USER + b'X', LOGON), (3, USER, LOGON + b'X')):
            self.api.security.side_effect = [(3, USER, LOGON), child]
            self.denied(self.read)

    def test_initial_or_final_liveness_failure_denied(self):
        for position in range(4):
            self.api.live.side_effect = [None] * position + [OSError('PRIVATE')]
            self.denied(self.read)

    def test_api_failures_do_not_reflect_diagnostics(self):
        self.api.security.side_effect = OSError('PRIVATE IDENTIFIER')
        self.denied(self.read)


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.api = object.__new__(m._WindowsAPI)
        self.api.kernel = Mock()
        self.api.advapi = Mock()

    def buffer(self, sid=USER, *, groups=False, count=1, attributes=0xC0000000):
        start = m._Groups.groups.offset if groups else 0
        minimum = start + C.sizeof(m._SidAttributes)
        buf = C.create_string_buffer(minimum + len(sid))
        if groups:
            W.DWORD.from_buffer(buf).value = count
        entry = m._SidAttributes.from_buffer(buf, start)
        entry.sid = C.addressof(buf) + minimum
        entry.attributes = attributes
        C.memmove(entry.sid, sid, len(sid))
        return buf, len(buf)

    def test_single_sid_exact_binary_copy(self):
        self.api._token_buffer = Mock(return_value=self.buffer())
        self.assertEqual(self.api._single_sid(100, 1), USER)

    def test_sid_pointer_cannot_escape_or_overlap_headers(self):
        for delta in (-1, 0, 8, 999):
            buf, length = self.buffer()
            m._SidAttributes.from_buffer(buf).sid = C.addressof(buf) + delta
            self.api._token_buffer = Mock(return_value=(buf, length))
            with self.assertRaises(m.NativeContextError):
                self.api._single_sid(100, 1)

    def test_truncated_or_malformed_sid(self):
        for sid in (b'\x02\x01' + bytes(10), b'\x01\x00' + bytes(6),
                    b'\x01\x10' + bytes(70), b'\x01\x02' + bytes(6)):
            self.api._token_buffer = Mock(return_value=self.buffer(sid))
            with self.assertRaises(m.NativeContextError):
                self.api._single_sid(100, 1)

    def test_short_structure_rejected(self):
        self.api._token_buffer = Mock(return_value=(C.create_string_buffer(2), 2))
        with self.assertRaises(m.NativeContextError):
            self.api._single_sid(100, 1)
        with self.assertRaises(m.NativeContextError):
            self.api._logon_sid(100)

    def test_exact_logon_group_and_attribute_required(self):
        self.api._token_buffer = Mock(return_value=self.buffer(LOGON, groups=True))
        self.assertEqual(self.api._logon_sid(100), LOGON)
        for changes in (dict(count=0), dict(count=2), dict(attributes=4), dict(sid=USER)):
            options = dict(sid=LOGON, groups=True) | changes
            self.api._token_buffer.return_value = self.buffer(**options)
            with self.assertRaises(m.NativeContextError):
                self.api._logon_sid(100)

    def test_only_wait_timeout_proves_live(self):
        self.api.kernel.WaitForSingleObject.return_value = 258
        self.api.live(100)
        self.api.kernel.WaitForSingleObject.assert_called_with(100, 0)
        for result in (0, 0xFFFFFFFF, 128):
            self.api.kernel.WaitForSingleObject.return_value = result
            with self.assertRaises(m.NativeContextError):
                self.api.live(100)

    def test_pin_api_failures(self):
        self.api.kernel.GetProcessId.return_value = 0
        with self.assertRaises(m.NativeContextError):
            self.api.pin(100)
        self.api.kernel.GetProcessId.return_value = 10
        self.api.kernel.GetProcessTimes.return_value = False
        with self.assertRaises(m.NativeContextError):
            self.api.pin(100)
        self.api.kernel.GetProcessTimes.return_value = True  # zero creation
        with self.assertRaises(m.NativeContextError):
            self.api.pin(100)

    def test_security_closes_only_temporary_token_once_on_failure(self):
        self.api.advapi.OpenProcessToken.return_value = True
        self.api._single_sid = Mock(side_effect=m.NativeContextError('NATIVE_CONTEXT_REJECTED'))
        with self.assertRaises(m.NativeContextError):
            self.api.security(100)
        self.assertEqual(self.api.kernel.CloseHandle.call_count, 1)
        self.assertIsInstance(self.api.kernel.CloseHandle.call_args.args[0], W.HANDLE)

    def test_failed_token_open_never_closes_borrowed_handle(self):
        self.api.advapi.OpenProcessToken.return_value = False
        with self.assertRaises(m.NativeContextError):
            self.api.security(100)
        self.api.kernel.CloseHandle.assert_not_called()

    def test_nonmedium_integrity_and_uncertain_close_denied(self):
        self.api.advapi.OpenProcessToken.return_value = True
        self.api._logon_sid = Mock(return_value=LOGON)
        self.api._token_buffer = Mock(return_value=(C.create_string_buffer(struct.pack('<I', 3), 4), 4))
        for label in (MEDIUM[:-2] + b'\x00\x01', USER):
            self.api._single_sid = Mock(side_effect=[USER, label])
            with self.assertRaises(m.NativeContextError):
                self.api.security(100)
        self.api._single_sid = Mock(side_effect=[USER, MEDIUM])
        self.api.kernel.CloseHandle.return_value = False
        with self.assertRaises(m.NativeContextError):
            self.api.security(100)
        self.assertEqual(self.api.kernel.CloseHandle.call_count, 3)

    def test_token_buffer_bounds_and_no_retry(self):
        # Windows-only ctypes last-error access is replaced for portable mocks.
        with patch.object(C, 'get_last_error', return_value=122, create=True):
            for size in (0, 65537):
                def oversized(token, kind, buf, capacity, returned):
                    returned._obj.value = size
                    return False
                self.api.advapi.GetTokenInformation.side_effect = oversized
                with self.assertRaises(m.NativeContextError):
                    self.api._token_buffer(100, 1)
            for used, success in ((0, True), (33, True), (32, False), (32, True)):
                calls = []
                def result(token, kind, buf, capacity, returned):
                    calls.append(capacity)
                    returned._obj.value = 32 if buf is None else used
                    return False if buf is None else success
                self.api.advapi.GetTokenInformation.side_effect = result
                if success and used == 32:
                    self.assertEqual(self.api._token_buffer(100, 1)[1], 32)
                else:
                    with self.assertRaises(m.NativeContextError):
                        self.api._token_buffer(100, 1)
                self.assertEqual(calls, [0, 32])


if __name__ == '__main__':
    unittest.main()
