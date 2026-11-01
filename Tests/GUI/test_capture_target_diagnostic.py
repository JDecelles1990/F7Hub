"""Opt-in capture diagnostics: synthetic targets only; no native effects or DB."""
import os
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture, _capture_diagnostic
from f7hub.infrastructure.windows_selection_copy import SelectionCopyError, copy_selection
from f7hub.services.clipboard_service import SelectionCaptureResult
from Tests.GUI.test_selection_capture import FakeHotkeyAPI
from Tests.Unit.test_windows_selection_copy import FakeAPI


class DiagnosticVocabularyTests(unittest.TestCase):
    def test_allowlisted_fields_survive_and_unknown_fields_are_redacted(self):
        self.assertEqual(
            _capture_diagnostic("PIN", "TARGET_UNAVAILABLE", "PROCESS_OPEN_FAILED"),
            "Capture Target Diagnostic: STAGE=PIN; CODE=TARGET_UNAVAILABLE; GUARD=PROCESS_OPEN_FAILED.")
        for stage, code, guard in (
            ("PRIVATE TITLE", "PRIVATE TEXT", "C:/private/token"),
            ([], {}, ["private"]), (0, True, 123),
        ):
            self.assertEqual(_capture_diagnostic(stage, code, guard),
                             "Capture Target Diagnostic: STAGE=UNCLASSIFIED; CODE=UNCLASSIFIED; GUARD=UNCLASSIFIED.")
        self.assertIn("GUARD=NONE", _capture_diagnostic("WORKER", "NATIVE_EXCEPTION"))

    def test_unknown_objects_are_never_formatted(self):
        class Private:
            def __str__(self):
                raise AssertionError("Must not format arbitrary objects")
        self.assertNotIn("private", _capture_diagnostic(Private(), Private(), Private()).lower())


class NativeStageTests(unittest.TestCase):
    def test_pin_failure_preserves_error_identity_code_and_guard_without_input(self):
        api = FakeAPI()
        error = SelectionCopyError("TARGET_UNAVAILABLE", guard="PROCESS_OPEN_FAILED")
        api.pin = Mock(side_effect=error)
        with self.assertRaises(SelectionCopyError) as caught:
            copy_selection(api, api.target, threading.Event())
        self.assertIs(caught.exception, error)
        self.assertEqual((str(error), error.guard, error.stage),
                         ("TARGET_UNAVAILABLE", "PROCESS_OPEN_FAILED", "PIN"))
        self.assertEqual((api.sent, api.reads, api.closed), (0, 0, 0))

    def test_post_pin_identity_failure_is_not_attributed_to_pin(self):
        api = FakeAPI()
        error = SelectionCopyError("TARGET_UNAVAILABLE", guard="NO_WINDOW")
        api.foreground = Mock(side_effect=error)
        with self.assertRaises(SelectionCopyError) as caught:
            copy_selection(api, api.target, threading.Event())
        self.assertIs(caught.exception, error)
        self.assertEqual(error.stage, "CHECK_SOURCE")
        self.assertEqual((api.sent, api.closed), (0, 1))

    def test_cleanup_failure_retains_cleanup_stage(self):
        api = FakeAPI()
        api.unpin = Mock(side_effect=SelectionCopyError("CLEANUP_FAILED", guard="HANDLE_CLOSE_FAILED"))
        with self.assertRaises(SelectionCopyError) as caught:
            copy_selection(api, api.target, threading.Event())
        self.assertEqual((str(caught.exception), caught.exception.guard, caught.exception.stage),
                         ("CLEANUP_FAILED", "HANDLE_CLOSE_FAILED", "CLEANUP"))

    def test_cancellation_unpins_without_sending_input(self):
        api = FakeAPI()
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(SelectionCopyError) as caught:
            copy_selection(api, api.target, cancelled)
        self.assertEqual((str(caught.exception), caught.exception.stage), ("CANCELLED", "CHECK_SOURCE"))
        self.assertEqual((api.sent, api.closed), (0, 1))


class CaptureTargetDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.env = patch.dict(os.environ, {
            "F7HUB_DEV_CAPTURE_TARGET_DIAGNOSTIC": "1",
            "F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC": "1",
            "F7HUB_DEV_PASTE_SEQUENCE_DIAGNOSTIC": "0"})
        self.env.start()
        self.window = QMainWindow()
        self.api = FakeHotkeyAPI()
        self.service = Mock()
        self.service.capture_active_selection.side_effect = (
            lambda acquire, cancel: SelectionCaptureResult(acquire().text))
        self.owner = SelectionCapture(self.window, self.service, api=self.api)
        self.owner.start()

    def wait(self):
        end = time.monotonic() + 3
        while self.owner.busy and time.monotonic() < end:
            self.app.processEvents()
            self.owner.poll()
            time.sleep(.005)
        self.assertFalse(self.owner.busy)

    def tearDown(self):
        self.wait()
        self.api.cleanup_ok = True
        self.assertTrue(self.owner.close())
        self.window.deleteLater()
        self.app.processEvents()
        self.env.stop()

    def message(self):
        return self.window.statusBar().currentMessage()

    def test_opt_in_requires_exact_flag_and_source_development_runtime(self):
        self.assertTrue(self.owner.capture_target_diagnostic)
        for flag in ("0", "", "true"):
            with patch.dict(os.environ, {"F7HUB_DEV_CAPTURE_TARGET_DIAGNOSTIC": flag}):
                owner = SelectionCapture(self.window, self.service, api=self.api)
                self.assertFalse(owner.capture_target_diagnostic)
                self.assertTrue(owner.close())
        with patch.object(sys, "frozen", True, create=True):
            owner = SelectionCapture(self.window, self.service, api=self.api)
            self.assertFalse(owner.capture_target_diagnostic)
            self.assertTrue(owner.close())
        with patch("f7hub.gui.selection_capture.Path.exists", return_value=False):
            owner = SelectionCapture(self.window, self.service, api=self.api)
            self.assertFalse(owner.capture_target_diagnostic)
            self.assertTrue(owner.close())

    def test_initial_binding_refusal_has_exact_stage_and_no_worker(self):
        self.api.foreground = Mock(side_effect=SelectionCopyError("TARGET_UNAVAILABLE", guard="NO_WINDOW"))
        self.assertFalse(self.owner.trigger())
        self.assertEqual(self.message(),
                         "Capture Target Diagnostic: STAGE=INITIAL_BINDING; CODE=TARGET_UNAVAILABLE; GUARD=NO_WINDOW.")
        self.assertFalse(self.owner.busy)
        self.assertEqual(self.api.sent, 0)

    def test_worker_pin_refusal_reaches_gui_with_fixed_code_and_guard(self):
        self.api.pin = Mock(side_effect=SelectionCopyError("TARGET_UNAVAILABLE", guard="ELEVATED_POLICY"))
        self.assertTrue(self.owner.trigger())
        self.wait()
        self.assertEqual(self.message(),
                         "Capture Target Diagnostic: STAGE=PIN; CODE=TARGET_UNAVAILABLE; GUARD=ELEVATED_POLICY.")
        self.assertEqual(self.api.sent, 0)

    def test_unknown_native_code_and_guard_do_not_escape(self):
        self.api.pin = Mock(side_effect=SelectionCopyError("PRIVATE TEXT", guard="PRIVATE PID PATH TITLE"))
        self.owner.trigger()
        self.wait()
        self.assertEqual(self.message(),
                         "Capture Target Diagnostic: STAGE=PIN; CODE=UNCLASSIFIED; GUARD=UNCLASSIFIED.")

    def test_arbitrary_initial_and_worker_exceptions_are_content_free(self):
        self.api.foreground = Mock(side_effect=RuntimeError("PRIVATE INITIAL"))
        self.assertFalse(self.owner.trigger())
        self.assertIn("STAGE=INITIAL_BINDING; CODE=NATIVE_EXCEPTION", self.message())
        self.api.foreground = lambda: self.api.target
        self.service.capture_active_selection.side_effect = RuntimeError("PRIVATE WORKER")
        self.assertTrue(self.owner.trigger())
        self.wait()
        self.assertIn("STAGE=WORKER; CODE=NATIVE_EXCEPTION", self.message())
        self.assertNotIn("PRIVATE", self.message())

    def test_diagnostic_success_acquires_once_without_exposing_text(self):
        self.api.text = "SYNTHETIC PRIVATE SENTINEL"
        self.assertTrue(self.owner.trigger())
        self.wait()
        self.assertEqual(self.api.sent, 1)
        self.assertEqual(self.message(),
                         "Capture Target Diagnostic: STAGE=COMPLETE; CODE=ACQUIRED; GUARD=NONE.")
        self.assertNotIn(self.api.text, self.message())

    def test_opt_out_preserves_original_failure_feedback(self):
        self.owner.capture_target_diagnostic = False
        self.api.pin = Mock(side_effect=SelectionCopyError("TARGET_UNAVAILABLE", guard="ELEVATED_POLICY"))
        self.owner.trigger()
        self.wait()
        self.assertEqual(self.message(),
                         "Selection not captured: TARGET_UNAVAILABLE. No old Clipboard fallback was used.")

    def test_cleanup_failure_still_fences_both_hotkeys(self):
        self.api.unpin = Mock(side_effect=SelectionCopyError("CLEANUP_FAILED", guard="HANDLE_CLOSE_FAILED"))
        self.owner.trigger()
        self.wait()
        self.assertTrue(self.owner.cleanup_failed)
        self.assertFalse(self.owner.registered or self.owner.paste_registered)
        self.assertIn("STAGE=CLEANUP; CODE=CLEANUP_FAILED; GUARD=HANDLE_CLOSE_FAILED", self.message())
        self.assertFalse(self.owner.trigger())
        self.assertFalse(self.owner.trigger(action="paste"))

    def test_both_registrations_remain_independent_and_idempotent(self):
        self.owner.start()
        self.assertTrue(self.owner.registered and self.owner.paste_registered)
        self.assertEqual((self.api.registrations, self.api.paste_registrations), (1, 1))
        self.service.capture_active_selection.assert_not_called()
        self.service.paste_latest.assert_not_called()

    def test_worker_start_failure_does_not_expose_exception_or_keep_worker(self):
        with patch("f7hub.gui.selection_capture.threading.Thread.start", side_effect=RuntimeError("PRIVATE")):
            self.assertFalse(self.owner.trigger())
        self.assertFalse(self.owner.busy)
        self.assertEqual(self.message(),
                         "Capture Target Diagnostic: STAGE=WORKER_START; CODE=WORKER_START_FAILED; GUARD=NONE.")
