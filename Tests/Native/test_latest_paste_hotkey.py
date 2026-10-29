"""Native registration/Qt dispatch only; service stub performs no native effects."""
import ctypes as C
from ctypes import wintypes as W
import os
import time
import unittest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication,QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI,PASTE_HOTKEY_ID

@unittest.skipUnless(os.name=='nt','Windows required')
class NativeLatestPasteHotkeyTests(unittest.TestCase):
    def test_both_hotkeys_register_paste_dispatches_once_and_unregisters(self):
        app=QApplication.instance() or QApplication([])
        window=QMainWindow();api=WindowsPasteAPI();service=Mock()
        service.paste_latest.return_value=('WRITTEN','DISPATCHED')
        owner=SelectionCapture(window,service,api=api)
        try:
            owner.start();owner.start()
            self.assertTrue(owner.registered,'Win+Alt+C collision')
            self.assertTrue(owner.paste_registered,'Win+Alt+V collision')
            service.paste_latest.assert_not_called()
            user=C.WinDLL('user32',use_last_error=True);kernel=C.WinDLL('kernel32',use_last_error=True)
            kernel.GetCurrentThreadId.argtypes=[];kernel.GetCurrentThreadId.restype=W.DWORD
            user.PostThreadMessageW.argtypes=[W.DWORD,W.UINT,W.WPARAM,W.LPARAM];user.PostThreadMessageW.restype=W.BOOL
            self.assertTrue(user.PostThreadMessageW(kernel.GetCurrentThreadId(),0x312,PASTE_HOTKEY_ID,(0x56<<16)|9))
            end=time.monotonic()+3
            while not service.paste_latest.called and time.monotonic()<end:
                app.processEvents();time.sleep(.005)
            while owner.busy and time.monotonic()<end:
                app.processEvents();owner.poll();time.sleep(.005)
            self.assertFalse(owner.busy);service.paste_latest.assert_called_once()
            service.capture_active_selection.assert_not_called()
            self.assertIn('dispatched once',window.statusBar().currentMessage())
            self.assertTrue(owner.close())
            self.assertFalse(owner.registered or owner.paste_registered)
            self.assertTrue(api.register_paste());self.assertTrue(api.unregister_paste())
            self.assertTrue(api.register());self.assertTrue(api.unregister())
        finally:
            owner.cancel()
            end=time.monotonic()+3
            while owner.busy and time.monotonic()<end:
                owner.poll();time.sleep(.005)
            owner.close();window.deleteLater();app.processEvents()
