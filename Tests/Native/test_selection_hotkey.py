"""Native registration and WM_HOTKEY delivery only. No copy, Clipboard read or input."""

import ctypes as C
from ctypes import wintypes as W
import os
import time
import unittest
from unittest.mock import Mock

from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.infrastructure.windows_selection_copy import WindowsSelectionAPI, HOTKEY_ID
from f7hub.services.clipboard_service import SelectionCaptureResult


@unittest.skipUnless(os.name == 'nt', 'Windows native APIs required')
class NativeSelectionHotkeyTests(unittest.TestCase):
    def test_register_native_dispatch_and_unregister(self):
        app = QApplication.instance() or QApplication([])
        window = QMainWindow()
        api = WindowsSelectionAPI()
        service = Mock()
        # Isolates real Qt/Windows registration and delivery, intentionally no acquisition.
        service.capture_active_selection.return_value = SelectionCaptureResult('Synthetic native dispatch')
        capture = SelectionCapture(window, service, api=api)
        try:
            capture.start()
            self.assertTrue(capture.registered, 'Win+Alt+C collision or unavailable desktop')
            capture.start()
            user = C.WinDLL('user32', use_last_error=True)
            kernel = C.WinDLL('kernel32', use_last_error=True)
            kernel.GetCurrentThreadId.argtypes, kernel.GetCurrentThreadId.restype = [], W.DWORD
            user.PostThreadMessageW.argtypes = [W.DWORD, W.UINT, W.WPARAM, W.LPARAM]
            user.PostThreadMessageW.restype = W.BOOL
            self.assertTrue(user.PostThreadMessageW(kernel.GetCurrentThreadId(), 0x312, HOTKEY_ID, (0x43 << 16) | 9))
            deadline = time.monotonic() + 3
            while not service.capture_active_selection.called and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(.005)
            self.assertEqual(service.capture_active_selection.call_count, 1)
            while capture.busy and time.monotonic() < deadline:
                app.processEvents()
                capture.poll()
                time.sleep(.005)
            self.assertFalse(capture.busy)
            self.assertIn('Synthetic native dispatch', window.statusBar().currentMessage())
            self.assertTrue(capture.close())
            self.assertFalse(capture.registered)
            # Registration becomes available again after our exact owner releases it.
            self.assertTrue(api.register())
            self.assertTrue(api.unregister())
        finally:
            end = time.monotonic() + 3
            while capture.busy and time.monotonic() < end:
                capture.poll()
                time.sleep(.005)
            capture.close()
            window.close()
            window.deleteLater()
            app.processEvents()
