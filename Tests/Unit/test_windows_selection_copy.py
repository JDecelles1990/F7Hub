"""Synthetic native-policy checks; no Windows Clipboard or input effects."""

import threading
import unittest

from unittest.mock import Mock
from f7hub.infrastructure.windows_selection_copy import copy_selection, decode_unicode, Target, SelectionCopyError, WindowsSelectionAPI


class FakeAPI:
    def __init__(self):
        self.target = Target(100, 200)
        self.sequences = [10, 11, 11]
        self.owner = 200
        self.sent = self.reads = self.closed = 0
        self.held = False
        self.focus = self.target
        self.alive = True
        self.text = 'NEW SELECTED TEXT'
        self.read_effect = lambda: None

    def pin(self, target): return 999
    def unpin(self, handle): self.closed += 1
    def live(self, handle): return self.alive
    def foreground(self): return self.focus
    def keys_down(self): return self.held
    def sequence(self):
        return self.sequences.pop(0) if len(self.sequences) > 1 else self.sequences[0]
    def owner_pid(self): return self.owner
    def send_copy(self): self.sent += 1
    def read_text(self, target, sequence):
        self.reads += 1
        self.read_effect()
        return self.text


class SelectionCopyTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()
        self.cancelled = threading.Event()
        self.now = 0

    def clock(self): return self.now
    def sleep(self, seconds): self.now += seconds
    def run_copy(self):
        return copy_selection(self.api, self.api.target, self.cancelled, clock=self.clock, sleep=self.sleep)

    def test_fresh_copy_sends_once_and_reads_new_text(self):
        self.assertEqual(self.run_copy(), 'NEW SELECTED TEXT')
        self.assertEqual((self.api.sent, self.api.reads, self.api.closed), (1, 1, 1))

    def test_old_sequence_never_reads_existing_text(self):
        self.api.sequences = [10]
        self.api.text = 'OLD TEXT'
        with self.assertRaisesRegex(SelectionCopyError, 'NO_FRESH_COPY'): self.run_copy()
        self.assertEqual((self.api.sent, self.api.reads, self.api.closed), (1, 0, 1))

    def test_zero_sequence_does_not_send(self):
        self.api.sequences = [0]
        with self.assertRaisesRegex(SelectionCopyError, 'SEQUENCE_UNAVAILABLE'): self.run_copy()
        self.assertEqual(self.api.sent, 0)

    def test_held_chord_times_out_without_input(self):
        self.api.held = True
        with self.assertRaisesRegex(SelectionCopyError, 'RELEASE_TIMEOUT'): self.run_copy()
        self.assertEqual(self.api.sent, 0)

    def test_release_before_copy(self):
        self.api.held = True
        def release(seconds):
            self.assertEqual(self.api.sent, 0)
            self.api.held = False
            self.now += seconds
        self.sleep = release
        self.assertEqual(self.run_copy(), 'NEW SELECTED TEXT')

    def test_target_change_before_input(self):
        self.api.focus = Target(300, 400)
        with self.assertRaisesRegex(SelectionCopyError, 'TARGET_CHANGED'): self.run_copy()
        self.assertEqual(self.api.sent, 0)

    def test_unrelated_owner_is_not_read(self):
        self.api.owner = 999
        with self.assertRaisesRegex(SelectionCopyError, 'AMBIGUOUS_UPDATE'): self.run_copy()
        self.assertEqual(self.api.reads, 0)

    def test_update_during_read_is_not_success(self):
        self.api.sequences = [10, 11, 12]
        with self.assertRaisesRegex(SelectionCopyError, 'LATE_OR_UNSTABLE'): self.run_copy()

    def test_late_native_completion_is_rejected(self):
        self.api.read_effect = lambda: setattr(self, 'now', 30)
        with self.assertRaisesRegex(SelectionCopyError, 'LATE_OR_UNSTABLE'): self.run_copy()
        self.assertEqual(self.api.closed, 1)

    def test_cancel_after_read_rejects_and_unpins(self):
        self.api.read_effect = self.cancelled.set
        with self.assertRaisesRegex(SelectionCopyError, 'CANCELLED'): self.run_copy()
        self.assertEqual(self.api.closed, 1)

    def test_identical_but_fresh_content_is_valid(self):
        self.api.text = 'OLD TEXT'
        self.assertEqual(self.run_copy(), 'OLD TEXT')  # Freshness is sequence, not text inequality.

    def test_unicode_and_allocation_limits(self):
        self.assertEqual(decode_unicode('Synthetic 🙂\0'.encode('utf-16-le')), 'Synthetic 🙂')
        for raw in (b'', b'x', b'\0\0', b'x\0', b'\0\xd8\0\0', b'x\0' * 65537 + b'\0\0'):
            with self.subTest(size=len(raw)), self.assertRaises(SelectionCopyError): decode_unicode(raw)


class NativeReadBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.api = object.__new__(WindowsSelectionAPI)
        self.api.user = Mock()
        self.api.user.OpenClipboard.return_value = True
        self.api.user.CloseClipboard.return_value = True
        self.api.exclusions = (100, 101)
        self.api.permissions = (102, 103)
        self.api.sequence = Mock(return_value=11)
        self.api.owner_pid = Mock(return_value=200)
        self.api._bytes = Mock(return_value='NEW SELECTED TEXT\0'.encode('utf-16-le'))
        self.api.user.IsClipboardFormatAvailable.side_effect = lambda fmt: fmt == 13
        self.target = Target(100, 200)

    def test_stable_plain_unicode_is_closed_once(self):
        self.assertEqual(self.api.read_text(self.target, 11), 'NEW SELECTED TEXT')
        self.api._bytes.assert_called_once_with(13, 131074)
        self.api.user.CloseClipboard.assert_called_once()

    def test_exclusion_marker_denies_without_reading_content(self):
        self.api.user.IsClipboardFormatAvailable.side_effect = lambda fmt: fmt in (13, 100)
        with self.assertRaisesRegex(SelectionCopyError, 'PRIVACY_DENIED'): self.api.read_text(self.target, 11)
        self.api._bytes.assert_not_called()
        self.api.user.CloseClipboard.assert_called_once()

    def test_history_exclusion_dword_denies(self):
        self.api.user.IsClipboardFormatAvailable.side_effect = lambda fmt: fmt in (13, 102)
        self.api._bytes.return_value = b'\0' * 4
        with self.assertRaisesRegex(SelectionCopyError, 'PRIVACY_DENIED'): self.api.read_text(self.target, 11)
        self.api._bytes.assert_called_once_with(102, 4)

    def test_unsupported_content_closes_without_read(self):
        self.api.user.IsClipboardFormatAvailable.return_value = False
        self.api.user.IsClipboardFormatAvailable.side_effect = None
        with self.assertRaisesRegex(SelectionCopyError, 'UNSUPPORTED_TEXT'): self.api.read_text(self.target, 11)
        self.api._bytes.assert_not_called()
        self.api.user.CloseClipboard.assert_called_once()

    def test_owner_change_during_read_is_rejected(self):
        self.api.owner_pid.side_effect = [200, 300]
        with self.assertRaisesRegex(SelectionCopyError, 'AMBIGUOUS_UPDATE'): self.api.read_text(self.target, 11)
        self.api.user.CloseClipboard.assert_called_once()

    def test_native_read_failure_still_closes(self):
        self.api._bytes.side_effect = SelectionCopyError('UNSUPPORTED_TEXT')
        with self.assertRaises(SelectionCopyError): self.api.read_text(self.target, 11)
        self.api.user.CloseClipboard.assert_called_once()

    def test_lock_failure_does_not_read_or_close_unowned_clipboard(self):
        self.api.user.OpenClipboard.return_value = False
        with self.assertRaisesRegex(SelectionCopyError, 'CLIPBOARD_LOCKED'): self.api.read_text(self.target, 11)
        self.api._bytes.assert_not_called()
        self.api.user.CloseClipboard.assert_not_called()

    def test_partial_input_cleanup_failure_is_explicit(self):
        self.api.user.SendInput.side_effect = [1, 0]
        with self.assertRaisesRegex(SelectionCopyError, 'CLEANUP_FAILED'): self.api.send_copy()
        self.assertEqual(self.api.user.SendInput.call_count, 2)


class NativeTargetPinTests(unittest.TestCase):
    def test_known_terminal_is_denied_before_input_and_handle_closed(self):
        import ctypes
        from ctypes import wintypes
        api = object.__new__(WindowsSelectionAPI)
        api.kernel, api.user = Mock(), Mock()
        api.kernel.OpenProcess.return_value = 999
        def image(handle, flags, buffer, size):
            buffer.value = 'C:\\Windows\\System32\\cmd.exe'
            return True
        api.kernel.QueryFullProcessImageNameW.side_effect = image
        with self.assertRaisesRegex(SelectionCopyError, 'UNSUPPORTED_TARGET'):
            api.pin(Target(100, 987654))
        api.kernel.CloseHandle.assert_called_once_with(999)
        api.user.SendInput.assert_not_called()

    def test_rejected_pin_with_failed_close_reports_cleanup_failure(self):
        api = object.__new__(WindowsSelectionAPI)
        api.kernel = Mock()
        api.kernel.OpenProcess.return_value = 999
        api.kernel.QueryFullProcessImageNameW.return_value = False
        api.kernel.CloseHandle.return_value = False
        with self.assertRaisesRegex(SelectionCopyError, 'CLEANUP_FAILED'):
            api.pin(Target(100, 987654))


if __name__ == '__main__': unittest.main()
