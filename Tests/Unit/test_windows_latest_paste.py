"""Synthetic native effects only: no real Clipboard write or keyboard injection."""
import ctypes
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
import threading
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from f7hub.domain.clipboard import AdmittedManualText, ClipboardItemRef, ClipboardPasteAuthorization, ClipboardPasteSource
from f7hub.infrastructure.windows_selection_copy import Target, SelectionCopyError, WindowsSelectionAPI
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI, PasteEffectError, paste_latest


class FakePasteAPI:
    def __init__(self):
        self.target = self.focus = Target(100, 200)
        self.held = False
        self.alive = True
        self.serial = 20
        self.writes = self.sent = self.closed = 0
        self.before_write = lambda: None
        self.after_write = lambda: None
    def pin_paste(self, target): return 999
    def live(self, handle): return self.alive
    def foreground(self): return self.focus
    def unpin(self, handle): self.closed += 1
    def paste_keys_down(self): return self.held
    def sequence(self): return self.serial
    def owner_pid(self): return os.getpid()
    def write_text(self, text, owner, check):
        self.before_write()
        check()
        self.writes += 1
        sequence = self.serial
        self.after_write()
        return sequence
    def send_paste(self): self.sent += 1


class PasteEffectTests(unittest.TestCase):
    def setUp(self):
        self.api = FakePasteAPI()
        self.cancelled = threading.Event()
        self.elapsed = 100.
        self.instant = datetime(2026, 10, 28, tzinfo=timezone.utc)
        self.prepare_count = self.consume_count = 0
    def prepare(self, target_token):
        self.prepare_count += 1
        return ClipboardPasteAuthorization(str(uuid4()), str(uuid4()), ClipboardItemRef(1), 1, target_token)
    def consume(self, authorization):
        self.consume_count += 1
        return ClipboardPasteSource(authorization, AdmittedManualText('Synthetic ordinary paste'),
            (self.instant + timedelta(seconds=1)).isoformat())
    def sleep(self, seconds): self.elapsed += seconds
    def run_effect(self):
        return paste_latest(self.api, self.api.target, 123, self.cancelled, self.prepare, self.consume,
            clock=lambda: self.elapsed, sleep=self.sleep, utc=lambda: self.instant)
    def deny(self, code):
        with self.assertRaisesRegex(PasteEffectError, code) as caught: self.run_effect()
        self.assertEqual(self.api.sent, 0)
        return caught.exception
    def test_normal_write_and_single_dispatch(self):
        self.assertEqual(self.run_effect(), ('WRITTEN', 'DISPATCHED'))
        self.assertEqual((self.prepare_count, self.consume_count, self.api.writes, self.api.sent, self.api.closed), (1,1,1,1,1))
    def test_held_chord_times_out_before_consume_or_write(self):
        self.api.held = True
        self.deny('RELEASE_TIMEOUT')
        self.assertEqual((self.consume_count,self.api.writes,self.api.closed), (0,0,1))
    def test_release_precedes_consume(self):
        self.api.held = True
        def release(seconds):
            self.assertEqual(self.consume_count, 0)
            self.api.held = False
            self.elapsed += seconds
        self.sleep = release
        self.run_effect()
    def test_focus_change_before_write(self):
        self.api.before_write = lambda: setattr(self.api, 'focus', Target(300,400))
        self.deny('TARGET_CHANGED')
        self.assertEqual(self.api.writes, 0)
    def test_focus_change_after_write_preserves_truthful_outcome(self):
        self.api.after_write = lambda: setattr(self.api, 'focus', Target(300,400))
        self.assertEqual(self.deny('TARGET_CHANGED').clipboard, 'WRITTEN')
    def test_newer_clipboard_change_never_rewrites_or_sends(self):
        self.api.after_write = lambda: setattr(self.api, 'serial', 21)
        self.deny('CLIPBOARD_CHANGED')
        self.assertEqual(self.api.writes, 1)
    def test_dead_process_denied(self):
        self.api.alive = False
        self.deny('TARGET_CHANGED')
        self.assertEqual(self.prepare_count, 0)
    def test_cancellation_before_effect(self):
        self.api.before_write = self.cancelled.set
        self.deny('CANCELLED')
        self.assertEqual(self.api.writes, 0)
    def test_cancellation_after_write(self):
        self.api.after_write = self.cancelled.set
        self.assertEqual(self.deny('CANCELLED').clipboard, 'WRITTEN')
    def test_slow_write_expires_effect_lease(self):
        self.api.after_write = lambda: setattr(self, 'elapsed', 102.)
        self.assertEqual(self.deny('EXPIRED').clipboard, 'WRITTEN')
    def test_wall_expiry_checked_after_native_wait(self):
        self.api.before_write = lambda: setattr(self, 'instant', self.instant + timedelta(seconds=2))
        self.deny('EXPIRED')
        self.assertEqual(self.api.writes, 0)
    def test_new_modifier_press_after_write_denied(self):
        self.api.after_write = lambda: setattr(self.api, 'held', True)
        self.deny('MODIFIERS_CHANGED')
    def test_failed_write_never_sends(self):
        self.api.write_text = Mock(side_effect=PasteEffectError('CLIPBOARD_LOCKED'))
        self.deny('CLIPBOARD_LOCKED')
    def test_failed_injection_never_retries(self):
        self.api.send_paste = Mock(side_effect=PasteEffectError('INPUT_DENIED','WRITTEN','UNCERTAIN'))
        with self.assertRaises(PasteEffectError) as caught: self.run_effect()
        self.assertEqual((caught.exception.clipboard,caught.exception.dispatch),('WRITTEN','UNCERTAIN'))
        self.api.send_paste.assert_called_once()
    def test_bad_target_authorization_denied(self):
        original = self.consume
        self.consume = lambda auth: replace(original(auth), authorization=replace(auth,target_token=str(uuid4())))
        self.deny('AUTHORIZATION_MISMATCH')
    def test_failed_cleanup_retains_dispatch_outcome(self):
        self.api.unpin = Mock(side_effect=RuntimeError('PRIVATE'))
        with self.assertRaises(PasteEffectError) as caught: self.run_effect()
        self.assertEqual((str(caught.exception),caught.exception.clipboard,caught.exception.dispatch),('CLEANUP_FAILED','WRITTEN','DISPATCHED'))


class PasteNativeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.api = object.__new__(WindowsPasteAPI)
        self.api.user, self.api.kernel = Mock(), Mock()
        self.api.permissions, self.api.exclusions = (101,102), (103,104)
        self.api.kernel.GlobalAlloc.side_effect = [1001,1002,1003,1004,1005]
        self.api.kernel.GlobalLock.return_value = 1
        self.api.kernel.GlobalUnlock.return_value = True
        self.api.kernel.GlobalFree.return_value = None
        self.api.user.SetClipboardData.side_effect = lambda fmt, handle: handle
        self.api.sequence = lambda: 20
        self.api.user.GetClipboardOwner.return_value = 123
        self.api._pid = lambda hwnd: os.getpid()
        self.api._bytes = Mock(side_effect=lambda fmt, limit: ('Synthetic note' + '\0').encode('utf-16-le')
            if fmt == 13 else b'\0' * 4 if fmt in self.api.permissions else b'\1')
        self.memmove = patch('f7hub.infrastructure.windows_latest_paste.C.memmove').start()
        self.addCleanup(patch.stopall)
    def write(self): return self.api.write_text('Synthetic note', 123, lambda: None)
    def test_success_transfers_all_buffers_and_uses_real_owner_hwnd(self):
        self.assertEqual(self.write(),20)
        self.assertEqual(self.api.user.OpenClipboard.call_args_list, [unittest.mock.call(123), unittest.mock.call(123)])
        self.api.kernel.GlobalFree.assert_not_called()
        self.assertEqual(self.api.user.CloseClipboard.call_count, 2)
        self.assertEqual([c.args[0] for c in self.api.user.SetClipboardData.call_args_list],[101,102,103,104,13])
    def test_locked_clipboard_frees_all_untransferred_buffers(self):
        self.api.user.OpenClipboard.return_value = False
        with self.assertRaisesRegex(PasteEffectError,'CLIPBOARD_LOCKED'): self.write()
        self.assertEqual(self.api.kernel.GlobalFree.call_count,5)
        self.api.user.EmptyClipboard.assert_not_called()
        self.api.user.CloseClipboard.assert_not_called()
    def test_allocation_failure_never_opens_clipboard(self):
        self.api.kernel.GlobalAlloc.side_effect = [None]
        with self.assertRaisesRegex(PasteEffectError,'ALLOCATION_FAILED'): self.write()
        self.api.user.OpenClipboard.assert_not_called()
    def test_partial_write_only_frees_buffers_still_owned(self):
        self.api.user.SetClipboardData.side_effect = [1001,None]
        with self.assertRaises(PasteEffectError) as caught: self.write()
        self.assertEqual(caught.exception.clipboard,'MAY_HAVE_CHANGED')
        self.assertEqual(self.api.kernel.GlobalFree.call_count,4)
        self.api.user.CloseClipboard.assert_called_once()
    def test_final_guard_runs_before_emptying(self):
        def deny(): raise PasteEffectError('TARGET_CHANGED')
        with self.assertRaisesRegex(PasteEffectError,'TARGET_CHANGED'):
            self.api.write_text('Synthetic note',123,deny)
        self.api.user.EmptyClipboard.assert_not_called()
        self.assertEqual(self.api.kernel.GlobalFree.call_count,5)
    def test_close_failure_is_explicit(self):
        self.api.user.CloseClipboard.return_value = False
        with self.assertRaisesRegex(PasteEffectError,'CLEANUP_FAILED'): self.write()
    def test_partial_input_has_only_keyup_cleanup_no_second_chord(self):
        self.api.user.SendInput.side_effect = [1,2]
        with self.assertRaises(PasteEffectError) as caught: self.api.send_paste()
        self.assertEqual(caught.exception.dispatch,'UNCERTAIN')
        self.assertEqual([c.args[0] for c in self.api.user.SendInput.call_args_list],[4,2])
    def test_input_cleanup_failure_is_explicit(self):
        self.api.user.SendInput.side_effect = [1,0]
        with self.assertRaisesRegex(PasteEffectError,'CLEANUP_FAILED'): self.api.send_paste()
    def test_office_policy_reuses_target_pin_and_closes_rejected_handle(self):
        def image(handle, flags, buffer, size):
            buffer.value = 'C:\\Office\\WINWORD.EXE'
            return True
        self.api.kernel.QueryFullProcessImageNameW.side_effect = image
        with patch.object(WindowsSelectionAPI,'pin',return_value=999):
            with self.assertRaisesRegex(SelectionCopyError,'UNSUPPORTED_TARGET'):
                self.api.pin_paste(Target(100,200))
        self.api.kernel.CloseHandle.assert_called_once_with(999)
        self.api.user.SendInput.assert_not_called()
