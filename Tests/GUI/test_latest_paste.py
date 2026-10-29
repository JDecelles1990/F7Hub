"""Qt owner tests; service and native effect boundary are synthetic."""
import ctypes
import os
import threading
import time
import unittest
from unittest.mock import Mock
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.infrastructure.windows_selection_copy import MSG
from f7hub.infrastructure.windows_latest_paste import PASTE_HOTKEY_ID, PasteEffectError
from Tests.GUI.test_selection_capture import FakeHotkeyAPI

class LatestPasteOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.window=QMainWindow()
        self.api=FakeHotkeyAPI()
        self.service=Mock()
        self.service.paste_latest.return_value=('WRITTEN','DISPATCHED')
        self.owner=SelectionCapture(self.window,self.service,api=self.api)
        self.owner.start()
    def wait(self):
        end=time.monotonic()+3
        while self.owner.busy and time.monotonic()<end:
            self.app.processEvents(); self.owner.poll(); time.sleep(.005)
        self.assertFalse(self.owner.busy)
    def tearDown(self):
        self.wait(); self.api.cleanup_ok=True
        self.assertTrue(self.owner.close())
        self.window.deleteLater(); self.app.processEvents()
    def test_start_registers_without_pasting(self):
        self.assertTrue(self.owner.paste_registered)
        self.owner.start()
        self.assertEqual(self.api.paste_registrations,1)
        self.service.paste_latest.assert_not_called()
    def test_native_message_routes_exact_paste_chord(self):
        message=MSG(); message.message=0x312; message.wParam=PASTE_HOTKEY_ID; message.lParam=(0x56<<16)|9
        self.assertEqual(self.owner.nativeEventFilter(b'windows_generic_MSG',ctypes.addressof(message)),(True,0))
        self.wait(); self.service.paste_latest.assert_called_once()
    def test_wrong_chord_not_accepted(self):
        message=MSG(); message.message=0x312; message.wParam=PASTE_HOTKEY_ID; message.lParam=(0x43<<16)|9
        self.assertEqual(self.owner.nativeEventFilter(b'windows_generic_MSG',ctypes.addressof(message)),(False,0))
        self.service.paste_latest.assert_not_called()
    def test_held_chord_cannot_repeat_after_worker_completion(self):
        self.api.held=True
        self.assertTrue(self.owner.trigger(action='paste')); self.wait()
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held=False; self.owner.poll()
        self.assertTrue(self.owner.trigger(action='paste')); self.wait()
        self.assertEqual(self.service.paste_latest.call_count,2)
    def test_shared_single_flight_and_exit_cancel_drain(self):
        entered,release=threading.Event(),threading.Event()
        def block(deliver): entered.set(); release.wait(2); return ('WRITTEN','DISPATCHED')
        self.service.paste_latest.side_effect=block
        self.owner.trigger(action='paste'); self.assertTrue(entered.wait(1))
        try:
            self.assertFalse(self.owner.trigger())
            self.assertFalse(self.owner.trigger(action='paste'))
            self.assertFalse(self.owner.close())
            self.assertTrue(self.owner._cancelled.is_set())
            self.app.processEvents()
        finally: release.set()
        self.wait(); self.assertTrue(self.owner.close())
        self.assertFalse(self.owner.registered or self.owner.paste_registered)
    def test_write_and_dispatch_outcomes_are_content_free(self):
        self.service.paste_latest.side_effect=PasteEffectError('INPUT_DENIED','WRITTEN','UNCERTAIN')
        self.owner.trigger(action='paste'); self.wait()
        message=self.window.statusBar().currentMessage()
        self.assertIn('WRITTEN',message); self.assertIn('UNCERTAIN',message)
        self.assertNotIn('dispatched once',message)
    def test_capture_attempt_fence_precedes_foreground_failure(self):
        self.api.foreground=Mock(side_effect=RuntimeError('PRIVATE'))
        self.assertFalse(self.owner.trigger())
        self.service.begin_selection_capture.assert_called_once()
        self.assertNotIn('PRIVATE',self.window.statusBar().currentMessage())
    def test_paste_cleanup_failure_disables_both_actions(self):
        self.service.paste_latest.side_effect=PasteEffectError('CLEANUP_FAILED','WRITTEN','UNCERTAIN')
        self.owner.trigger(action='paste'); self.wait()
        self.assertTrue(self.owner.cleanup_failed)
        self.assertFalse(self.owner.trigger()); self.assertFalse(self.owner.trigger(action='paste'))

    def test_paste_collision_does_not_disable_capture_registration(self):
        self.assertTrue(self.owner.close())
        self.api.paste_registration_ok=False
        self.owner=SelectionCapture(self.window,self.service,api=self.api);self.owner.start()
        self.assertTrue(self.owner.registered)
        self.assertFalse(self.owner.paste_registered)
        self.assertFalse(self.owner.trigger(action='paste'))
    def test_arbitrary_paste_exception_is_safe_and_names_paste(self):
        self.service.paste_latest.side_effect=RuntimeError('PRIVATE SENTINEL')
        self.owner.trigger(action='paste');self.wait()
        message=self.window.statusBar().currentMessage()
        self.assertIn('Paste Latest',message)
        self.assertNotIn('PRIVATE SENTINEL',message)
        self.assertNotIn('Selection not captured',message)
