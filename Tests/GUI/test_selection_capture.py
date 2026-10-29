"""Qt synthetic checks: ownership, single-flight, feedback and drain/cleanup."""

import os
import threading
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.services.clipboard_service import SelectionCaptureResult
from Tests.Unit.test_windows_selection_copy import FakeAPI


class FakeHotkeyAPI(FakeAPI):
    def __init__(self):
        super().__init__()
        self.registrations = self.unregistrations = 0
        self.registration_ok = self.cleanup_ok = True
        self.paste_registration_ok = True
        self.paste_registrations = self.paste_unregistrations = 0
    def register_paste(self):
        self.paste_registrations += 1
        return self.registration_ok and self.paste_registration_ok
    def unregister_paste(self):
        self.paste_unregistrations += 1
        return self.cleanup_ok
    def paste_keys_down(self): return self.held
    def register(self):
        self.registrations += 1
        return self.registration_ok
    def unregister(self):
        self.unregistrations += 1
        return self.cleanup_ok


class SelectionCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = QMainWindow()
        self.api = FakeHotkeyAPI()
        self.service = Mock()
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult(acquire())
        self.capture = SelectionCapture(self.window, self.service, api=self.api)
        self.capture.start()

    def wait(self):
        end = time.monotonic() + 3
        while self.capture.busy and time.monotonic() < end:
            self.app.processEvents()
            self.capture.poll()
            time.sleep(.005)
        self.assertFalse(self.capture.busy)

    def tearDown(self):
        self.wait()
        self.api.cleanup_ok = True
        self.assertTrue(self.capture.close())
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_registration_once_and_cleanup_idempotent(self):
        self.capture.start()
        self.assertEqual(self.api.registrations, 1)
        self.assertTrue(self.capture.close())
        self.assertTrue(self.capture.close())
        self.assertEqual(self.api.unregistrations, 1)

    def test_success_uses_existing_status_bar_and_no_new_widget(self):
        self.assertTrue(self.capture.trigger())
        self.wait()
        message = self.window.statusBar().currentMessage()
        self.assertIn('NEW SELECTED TEXT', message)
        self.assertIn('not saved', message)
        self.assertEqual(self.api.sent, 1)

    def test_single_flight_keeps_gui_responsive_and_drains_before_close(self):
        entered, release = threading.Event(), threading.Event()
        def blocked(acquire, cancel):
            entered.set()
            release.wait(2)
            return SelectionCaptureResult('Synthetic delayed result')
        self.service.capture_active_selection.side_effect = blocked
        self.assertTrue(self.capture.trigger())
        self.assertTrue(entered.wait(1))
        try:
            self.assertFalse(self.capture.trigger())
            self.assertFalse(self.capture.close())
            self.assertTrue(self.capture.busy)
            self.app.processEvents()  # GUI thread remains available.
            self.assertEqual(self.api.unregistrations, 0)
        finally:
            release.set()
        self.wait()
        self.assertTrue(self.capture.close())
        self.assertEqual(self.api.unregistrations, 1)

    def test_held_press_does_not_start_another_operation(self):
        # Service fake avoids copy release waiting, isolates coordinator rearm.
        self.api.held = True
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult('Synthetic result')
        self.capture.trigger()
        self.wait()
        self.assertFalse(self.capture.trigger())
        self.api.held = False
        self.capture.poll()
        self.assertTrue(self.capture.trigger())
        self.wait()
        self.assertEqual(self.service.capture_active_selection.call_count, 2)

    def test_registration_collision_is_unavailable(self):
        self.assertTrue(self.capture.close())
        self.api.registration_ok = False
        self.capture = SelectionCapture(self.window, self.service, api=self.api)
        self.capture.start()
        self.assertFalse(self.capture.registered)
        self.assertFalse(self.capture.trigger())
        self.assertIn('already registered', self.window.statusBar().currentMessage())

    def test_arbitrary_exception_text_never_enters_feedback(self):
        self.service.capture_active_selection.side_effect = RuntimeError('SYNTHETIC PRIVATE SENTINEL')
        self.capture.trigger()
        self.wait()
        self.assertNotIn('SYNTHETIC PRIVATE SENTINEL', self.window.statusBar().currentMessage())
        self.assertIn('not captured', self.window.statusBar().currentMessage())

    def test_unregister_failure_retains_owner_until_confirmed(self):
        self.api.cleanup_ok = False
        self.assertFalse(self.capture.close())
        self.assertTrue(self.capture.registered)
        self.assertFalse(self.capture.closed)
        self.api.cleanup_ok = True
        self.assertTrue(self.capture.close())

    def test_failed_cleanup_fences_new_operations(self):
        self.capture.cleanup_failed = True
        self.assertFalse(self.capture.trigger())
        self.service.capture_active_selection.assert_not_called()

    def test_worker_start_failure_is_safe_and_not_busy(self):
        with patch('f7hub.gui.selection_capture.threading.Thread.start', side_effect=RuntimeError('synthetic')):
            self.assertFalse(self.capture.trigger())
        self.assertFalse(self.capture.busy)
        self.assertIn('worker unavailable', self.window.statusBar().currentMessage())
