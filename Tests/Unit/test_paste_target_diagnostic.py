"""Synthetic Win32/Qt diagnosis; no real Clipboard access or keyboard injection."""
import ctypes as C
from ctypes import wintypes as W
import os
import threading
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.infrastructure.windows_selection_copy import Target, SelectionCopyError, MSG
from f7hub.infrastructure.windows_latest_paste import (
    WindowsPasteAPI, PasteEffectError, PASTE_HOTKEY_ID, paste_latest, target_diagnostic_code,
)
from f7hub.services.clipboard_service import SelectionCaptureResult
from Tests.GUI.test_selection_capture import FakeHotkeyAPI
from Tests.Unit.test_windows_latest_paste import FakePasteAPI


class TargetNativeGuardTests(unittest.TestCase):
    def api(self):
        api = object.__new__(WindowsPasteAPI)
        api.user, api.kernel, api.advapi = Mock(), Mock(), Mock()
        api.kernel.OpenProcess.return_value = 900
        api.kernel.CloseHandle.return_value = True
        api.kernel.GetProcessTimes.return_value = True
        def image(handle, flags, buffer, length):
            buffer.value = 'synthetic-notepad.exe'
            return True
        api.kernel.QueryFullProcessImageNameW.side_effect = image
        def token(handle, access, output):
            output._obj.value = 901
            return True
        api.advapi.OpenProcessToken.side_effect = token
        def elevation(token, kind, output, size, used):
            used._obj.value = 4
            output._obj.value = 0
            return True
        api.advapi.GetTokenInformation.side_effect = elevation
        return api

    def test_each_native_pin_rejection_reports_actual_guard_and_legacy_code(self):
        def fail(method):
            method.side_effect = None
            method.return_value = False
        def set_image(api, name):
            def image(handle, flags, buffer, length):
                buffer.value = name
                return True
            api.kernel.QueryFullProcessImageNameW.side_effect = image
        def token_result(api, size, elevated):
            def result(token, kind, output, length, used):
                used._obj.value = size
                output._obj.value = elevated
                return True
            api.advapi.GetTokenInformation.side_effect = result
        cases = [
            ('SELF_TARGET', 'TARGET_UNAVAILABLE', lambda a: None, True),
            ('PROCESS_OPEN_FAILED', 'TARGET_UNAVAILABLE', lambda a: fail(a.kernel.OpenProcess), False),
            ('IMAGE_QUERY_FAILED', 'TARGET_UNAVAILABLE', lambda a: fail(a.kernel.QueryFullProcessImageNameW), False),
            ('TERMINAL_POLICY', 'UNSUPPORTED_TARGET', lambda a: set_image(a, 'cmd.exe'), False),
            ('PROCESS_TIMES_FAILED', 'TARGET_UNAVAILABLE', lambda a: fail(a.kernel.GetProcessTimes), False),
            ('TOKEN_OPEN_FAILED', 'TARGET_UNAVAILABLE', lambda a: fail(a.advapi.OpenProcessToken), False),
            ('TOKEN_QUERY_FAILED', 'TARGET_UNAVAILABLE', lambda a: fail(a.advapi.GetTokenInformation), False),
            ('TOKEN_SIZE_INVALID', 'TARGET_UNAVAILABLE', lambda a: token_result(a, 0, 0), False),
            ('ELEVATED_POLICY', 'TARGET_UNAVAILABLE', lambda a: token_result(a, 4, 1), False),
            ('TOKEN_CLOSE_FAILED', 'CLEANUP_FAILED', lambda a: setattr(a.kernel.CloseHandle, 'side_effect', [False, True]), False),
            ('REJECTED_HANDLE_CLOSE_FAILED', 'CLEANUP_FAILED', lambda a: (fail(a.kernel.GetProcessTimes), fail(a.kernel.CloseHandle)), False),
            ('OFFICE_POLICY', 'UNSUPPORTED_TARGET', lambda a: set_image(a, 'WINWORD.EXE'), False),
        ]
        seen = set()
        for guard, legacy, configure, self_target in cases:
            with self.subTest(guard=guard):
                api = self.api(); configure(api)
                target = Target(100, os.getpid() if self_target else 200)
                with self.assertRaises(SelectionCopyError) as caught:
                    api.pin_paste(target)
                self.assertEqual((str(caught.exception), caught.exception.guard), (legacy, guard))
                self.assertEqual(target_diagnostic_code('PIN_' + guard), 'PIN_' + guard)
                api.user.SendInput.assert_not_called()
                api.user.OpenClipboard.assert_not_called()
                seen.add(guard)
        self.assertEqual(len(seen), len(cases))

    def test_second_image_query_is_distinct_and_closes_pin(self):
        api = self.api(); original = api.kernel.QueryFullProcessImageNameW.side_effect
        calls = []
        def second_fails(*args):
            calls.append(1)
            return original(*args) if len(calls) == 1 else False
        api.kernel.QueryFullProcessImageNameW.side_effect = second_fails
        with self.assertRaises(SelectionCopyError) as caught:
            api.pin_paste(Target(100, 200))
        self.assertEqual(caught.exception.guard, 'PASTE_IMAGE_QUERY_FAILED')
        self.assertEqual(api.kernel.CloseHandle.call_args_list[-1].args, (900,))

    def test_paste_rejection_handle_close_failure_is_distinct(self):
        api = self.api(); original = api.kernel.QueryFullProcessImageNameW.side_effect
        calls = []
        def second_fails(*args):
            calls.append(1)
            return original(*args) if len(calls) == 1 else False
        api.kernel.QueryFullProcessImageNameW.side_effect = second_fails
        api.kernel.CloseHandle.side_effect = [True, False]
        with self.assertRaises(SelectionCopyError) as caught:
            api.pin_paste(Target(100, 200))
        self.assertEqual((str(caught.exception), caught.exception.guard), ('CLEANUP_FAILED', 'HANDLE_CLOSE_FAILED'))

    def test_binding_native_failures_are_distinct_without_metadata(self):
        cases = [('NO_WINDOW', 0, 1, 200), ('WINDOW_QUERY_FAILED', 100, 0, 200),
                 ('WINDOW_PROCESS_MISSING', 100, 1, 0)]
        for guard, hwnd, result, pid in cases:
            with self.subTest(guard=guard):
                api = self.api(); api.user.GetForegroundWindow.return_value = hwnd
                def query(window, output):
                    output._obj.value = pid
                    return result
                api.user.GetWindowThreadProcessId.side_effect = query
                with self.assertRaises(SelectionCopyError) as caught: api.foreground()
                self.assertEqual((str(caught.exception), caught.exception.guard), ('TARGET_UNAVAILABLE', guard))
                self.assertEqual(target_diagnostic_code('INITIAL_' + guard), 'INITIAL_' + guard)


class TargetDiagnosticFlowTests(unittest.TestCase):
    def setUp(self):
        self.api = FakePasteAPI()
        self.cancelled = threading.Event()
        self.now = 0.
        self.prepare, self.consume = Mock(), Mock()
        self.api.sequence = Mock()
        self.api.owner_pid = Mock()
        self.api.write_text = Mock()
        self.api.send_paste = Mock()
        self.addCleanup(self.no_effects)
    def no_effects(self):
        for callback in (self.prepare, self.consume, self.api.sequence, self.api.owner_pid,
                         self.api.write_text, self.api.send_paste): callback.assert_not_called()
    def sleep(self, seconds): self.now += seconds
    def run_diagnostic(self):
        return paste_latest(self.api, self.api.target, 123, self.cancelled, self.prepare,
                            self.consume, clock=lambda: self.now, sleep=self.sleep, diagnostic=True)
    def denied(self, expected):
        with self.assertRaises(PasteEffectError) as caught: self.run_diagnostic()
        self.assertEqual(caught.exception.guard, expected)
        self.assertEqual(target_diagnostic_code(expected), expected)
        self.assertEqual((caught.exception.clipboard, caught.exception.dispatch), ('UNCHANGED', 'NOT_SENT'))
    def test_success_releases_keys_and_stops_without_authorization_or_effects(self):
        self.api.held = True
        def release(seconds): self.now += seconds; self.api.held = False
        self.sleep = release
        self.assertEqual(self.run_diagnostic(), 'TARGET_VALIDATED_AFTER_RELEASE')
        self.assertEqual(self.api.closed, 1)
    def test_pin_failure_preserves_exact_guard(self):
        self.api.pin_paste = Mock(side_effect=SelectionCopyError('TARGET_UNAVAILABLE', guard='TOKEN_OPEN_FAILED'))
        self.denied('PIN_TOKEN_OPEN_FAILED')
    def test_worker_process_and_foreground_guards_are_distinct(self):
        self.api.alive = False; self.denied('WORKER_PROCESS_NOT_LIVE')
        self.api.alive = True; self.api.focus = Target(300, 400)
        self.denied('WORKER_FOREGROUND_MISMATCH')
    def test_worker_cancellation(self):
        self.cancelled.set(); self.denied('WORKER_CANCELLED')
    def test_release_cancellation(self):
        self.api.held = True
        self.sleep = lambda seconds: self.cancelled.set()
        self.denied('RELEASE_CANCELLED')
    def test_release_timeout(self):
        self.api.held = True; self.denied('RELEASE_TIMEOUT')
    def test_release_process_and_foreground_guards(self):
        self.api.held = True
        self.api.live = Mock(side_effect=[True, False])
        self.denied('RELEASE_PROCESS_NOT_LIVE')
        self.api.live = Mock(return_value=True)
        self.api.foreground = Mock(side_effect=[self.api.target, Target(300, 400)])
        self.denied('RELEASE_FOREGROUND_MISMATCH')
    def test_post_release_process_and_foreground_guards(self):
        self.api.live = Mock(side_effect=[True, False])
        self.denied('POST_RELEASE_PROCESS_NOT_LIVE')
        self.api.live = Mock(return_value=True)
        self.api.foreground = Mock(side_effect=[self.api.target, Target(300, 400)])
        self.denied('POST_RELEASE_FOREGROUND_MISMATCH')
    def test_post_release_cancellation(self):
        self.api.paste_keys_down = Mock(side_effect=[True, False])
        self.sleep = lambda seconds: self.cancelled.set()
        self.denied('POST_RELEASE_CANCELLED')
    def test_foreground_query_failure_keeps_phase_and_native_branch(self):
        for stage in ('WORKER', 'RELEASE', 'POST_RELEASE'):
            with self.subTest(stage=stage):
                error = SelectionCopyError('TARGET_UNAVAILABLE', guard='WINDOW_QUERY_FAILED')
                self.api.held = stage == 'RELEASE'
                self.api.foreground = Mock(side_effect=([error] if stage == 'WORKER' else [self.api.target, error]))
                self.denied(stage + '_WINDOW_QUERY_FAILED')
    def test_arbitrary_native_exception_is_never_displayed(self):
        self.api.pin_paste = Mock(side_effect=RuntimeError('PRIVATE HWND PID TEXT TOKEN'))
        self.denied('PIN_NATIVE_EXCEPTION')
    def test_cleanup_failure_is_explicit(self):
        self.api.unpin = Mock(side_effect=RuntimeError('PRIVATE'))
        self.denied('CLEANUP_HANDLE_CLOSE_FAILED')


class DiagnosticHotkeyAPI(FakeHotkeyAPI):
    def pin_paste(self, target): return 999


class TargetDiagnosticQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.env = patch.dict(os.environ, {'F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC': '1'})
        self.env.start(); self.addCleanup(self.env.stop)
        self.window = QMainWindow(); self.api = DiagnosticHotkeyAPI(); self.service = Mock()
        self.owner = SelectionCapture(self.window, self.service, api=self.api); self.owner.start()
        self.assertTrue(self.owner.target_diagnostic)
    def wait(self):
        deadline = time.monotonic() + 2
        while self.owner.busy and time.monotonic() < deadline:
            self.app.processEvents(); self.owner.poll(); time.sleep(.002)
        self.assertFalse(self.owner.busy)
    def tearDown(self):
        self.wait(); self.api.cleanup_ok = True; self.owner.close()
        self.window.deleteLater(); self.app.processEvents()
    def message(self): return self.window.statusBar().currentMessage()
    def test_exact_hotkey_uses_diagnostic_worker_and_never_calls_service(self):
        message = MSG(); message.message = 0x312; message.wParam = PASTE_HOTKEY_ID
        message.lParam = (0x56 << 16) | 9
        self.assertEqual(self.owner.nativeEventFilter(b'windows_generic_MSG', C.addressof(message)), (True, 0))
        self.wait()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.message())
        self.assertIn('authorization: NOT_REQUESTED', self.message())
        self.assertEqual(self.service.mock_calls, [])
        self.assertEqual((self.api.sent, self.api.reads), (0, 0))
    def test_same_dispatch_reports_native_pin_guard_without_service_or_effects(self):
        api = TargetNativeGuardTests().api()
        api.user.GetForegroundWindow.return_value = 100
        def query(hwnd, output): output._obj.value = 200; return 1
        api.user.GetWindowThreadProcessId.side_effect = query
        api.user.GetAsyncKeyState.return_value = 0
        api.advapi.GetTokenInformation.side_effect = None
        api.advapi.GetTokenInformation.return_value = False
        self.owner.api = api
        message = MSG(); message.message = 0x312; message.wParam = PASTE_HOTKEY_ID
        message.lParam = (0x56 << 16) | 9
        self.owner.nativeEventFilter(b'windows_generic_MSG', C.addressof(message)); self.wait()
        self.assertIn('PIN_TOKEN_QUERY_FAILED', self.message())
        self.assertEqual(self.service.mock_calls, [])
        api.user.OpenClipboard.assert_not_called(); api.user.SendInput.assert_not_called()
    def test_native_gateway_success_stops_before_clipboard_and_input(self):
        api = TargetNativeGuardTests().api()
        api.user.GetForegroundWindow.return_value = 100
        def query(hwnd, output): output._obj.value = 200; return 1
        api.user.GetWindowThreadProcessId.side_effect = query
        api.kernel.WaitForSingleObject.return_value = 258
        api.user.GetAsyncKeyState.return_value = 0
        self.owner.api = api
        self.owner.trigger(action='paste'); self.wait()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.message())
        self.assertEqual(self.service.mock_calls, [])
        api.user.OpenClipboard.assert_not_called(); api.user.SetClipboardData.assert_not_called()
        api.user.SendInput.assert_not_called(); api.user.GetClipboardSequenceNumber.assert_not_called()
        self.assertEqual(api.kernel.CloseHandle.call_count, 2)
    def test_initial_native_guard_and_arbitrary_error_are_content_free(self):
        self.api.foreground = Mock(side_effect=SelectionCopyError('PRIVATE', guard='NO_WINDOW'))
        self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('INITIAL_NO_WINDOW', self.message()); self.assertNotIn('PRIVATE', self.message())
        self.owner._release_required = False
        self.api.foreground = Mock(side_effect=RuntimeError('PRIVATE title 100 200 secret text'))
        self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('INITIAL_NATIVE_EXCEPTION', self.message()); self.assertNotIn('PRIVATE', self.message())
    def test_owner_binding_and_worker_start_failures_are_distinct(self):
        with patch.object(self.window, 'winId', side_effect=RuntimeError('PRIVATE')):
            self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('INITIAL_OWNER_WINDOW_FAILED', self.message())
        self.owner._release_required = False
        with patch('f7hub.gui.selection_capture.threading.Thread.start', side_effect=RuntimeError('PRIVATE')):
            self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('WORKER_START_FAILED', self.message())
    def test_unknown_guard_is_allowlisted_without_sensitive_metadata(self):
        self.owner.diagnostic_feedback('PRIVATE title hwnd=100 pid=200 Clipboard=secret token')
        self.assertIn('UNCLASSIFIED_GUARD', self.message())
        for forbidden in ('PRIVATE', 'hwnd=', 'pid=', 'secret', 'token'): self.assertNotIn(forbidden, self.message())
    def test_admission_refusals_are_distinguishable(self):
        for attribute, value, code in (
            ('closed', True, 'ADMISSION_CLOSED'), ('cleanup_failed', True, 'ADMISSION_CLEANUP_DISABLED'),
            ('paste_registered', False, 'ADMISSION_UNREGISTERED'), ('_worker', object(), 'ADMISSION_BUSY'),
            ('_release_required', True, 'ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN'),
        ):
            with self.subTest(code=code):
                previous = getattr(self.owner, attribute); setattr(self.owner, attribute, value)
                self.api.held = code == 'ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN'
                try:
                    self.assertFalse(self.owner.trigger(action='paste')); self.assertIn(code, self.message())
                finally:
                    setattr(self.owner, attribute, previous)
                    self.api.held = False
    def test_capture_still_uses_original_service_and_copy(self):
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult(acquire().text)
        self.assertTrue(self.owner.trigger()); self.wait()
        self.service.begin_selection_capture.assert_called_once()
        self.service.capture_active_selection.assert_called_once()
        self.service.paste_latest.assert_not_called()
        self.assertEqual((self.api.sent, self.api.reads), (1, 1))
        self.assertNotIn('Diagnostic:', self.message())
    def test_normal_paste_requires_exact_explicit_development_enablement(self):
        for value in ('', 'true', '0'):
            with self.subTest(value=value), patch.dict(os.environ, {'F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC': value}):
                owner = SelectionCapture(self.window, self.service, api=self.api)
                self.assertFalse(owner.target_diagnostic)
        with patch('f7hub.gui.selection_capture.sys.frozen', True, create=True):
            self.assertFalse(SelectionCapture(self.window, self.service, api=self.api).target_diagnostic)
        with patch('f7hub.gui.selection_capture.Path.exists', return_value=False):
            self.assertFalse(SelectionCapture(self.window, self.service, api=self.api).target_diagnostic)
    def test_cleanup_failure_disables_operations_and_keeps_diagnostic(self):
        self.api.unpin = Mock(side_effect=RuntimeError('PRIVATE'))
        self.owner.trigger(action='paste'); self.wait()
        self.assertTrue(self.owner.cleanup_failed)
        self.assertFalse(self.owner.registered or self.owner.paste_registered)
        self.assertIn('CLEANUP_HANDLE_CLOSE_FAILED', self.message())
