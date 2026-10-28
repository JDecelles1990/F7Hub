"""App-owned native hotkey adapter; one retained worker, existing status feedback."""

import ctypes
import os
import queue
import threading

from PySide6.QtCore import QAbstractNativeEventFilter, QTimer
from PySide6.QtWidgets import QApplication

from f7hub.domain.clipboard import normalize_preview
from f7hub.infrastructure.windows_selection_copy import (
    WindowsSelectionAPI, SelectionCopyError, copy_selection, MSG, HOTKEY_ID,
    HOTKEY_MODIFIERS,
)


class SelectionCapture(QAbstractNativeEventFilter):
    def __init__(self, window, service, *, api=None):
        super().__init__()
        self.window, self.service = window, service
        self.api = api
        self.started = False
        self.registered = False
        self.closed = False
        self.cleanup_failed = False
        self._worker = None
        self._cancelled = threading.Event()
        self._results = queue.Queue(maxsize=1)
        self._release_required = False
        self.timer = QTimer(window)
        self.timer.setInterval(25)
        self.timer.timeout.connect(self.poll)

    @property
    def busy(self):
        return self._worker is not None

    def feedback(self, message):
        self.window.statusBar().showMessage(message, 15000)

    def start(self):
        if self.started or self.closed:
            return
        self.started = True
        if self.api is None:
            if os.name != 'nt':
                return
            try:
                self.api = WindowsSelectionAPI()
            except Exception:
                self.feedback('Selection capture unavailable: native initialization failed.')
                return
        if not self.api.register():
            self.feedback('Win+Alt+C is unavailable or already registered. Close the conflicting application and restart F7Hub.')
            return
        self.registered = True
        QApplication.instance().installNativeEventFilter(self)
        self.timer.start()
        self.feedback('Win+Alt+C ready: highlight text in another app, press the chord, then release it.')

    def nativeEventFilter(self, event_type, message):
        if self.closed or not self.registered or not bytes(event_type).startswith(b'windows_'):
            return False, 0
        native = ctypes.cast(int(message), ctypes.POINTER(MSG)).contents
        if native.message == 0x0312 and native.wParam == HOTKEY_ID:
            if (int(native.lParam) & 0xFFFF) != (HOTKEY_MODIFIERS & ~0x4000) or (int(native.lParam) >> 16) & 0xFFFF != 0x43:
                return False, 0
            self.trigger()
            return True, 0
        return False, 0

    def trigger(self):
        if self.closed or self.cleanup_failed or not self.registered or self.busy or self._release_required:
            return False
        self._release_required = True
        try:
            target = self.api.foreground()
        except Exception:
            self.feedback('Selection not captured: target unavailable.')
            return False
        self._cancelled.clear()
        self.feedback('Copying highlighted text. Release Win, Alt and C.')

        def work():
            try:
                result = self.service.capture_active_selection(
                    lambda: copy_selection(self.api, target, self._cancelled), self._cancelled)
                outcome = ('success', result)
            except SelectionCopyError as error:
                # Fixed native code only. Never stringify arbitrary exceptions.
                outcome = ('failure', str(error))
            except Exception:
                outcome = ('failure', 'ADMISSION_OR_SERVICE_UNAVAILABLE')
            self._results.put_nowait(outcome)

        self._worker = threading.Thread(target=work, name='f7hub-selection-copy', daemon=True)
        try:
            self._worker.start()
        except RuntimeError:
            self._worker = None
            self.feedback('Selection not captured: worker unavailable.')
            return False
        return True

    def poll(self):
        if self.closed:
            return
        if self._release_required and not self.api.keys_down():
            self._release_required = False
        if self._worker is None or self._worker.is_alive():
            return
        self._worker.join(0)
        self._worker = None
        kind, result = self._results.get_nowait()
        if kind == 'failure':
            if result == 'CLEANUP_FAILED':
                self.cleanup_failed = True
                self._unregister()
            self.feedback('Selection not captured: ' + result + '. No old Clipboard fallback was used.')
            return
        preview, truncated = normalize_preview(result.text[:241])
        label = {'PERSISTED': 'saved to Recent', 'PREVIEW_ONLY': 'not saved; explicit history consent is unavailable',
                 'NOT_SAVED': 'not saved; consent changed or persistence was denied',
                 'PERSISTENCE_UNCERTAIN': 'save outcome uncertain; do not repeat to retry saving'}[result.persistence]
        self.feedback('Fresh selection received (' + label + '): ' + preview + (' … [truncated]' if truncated else ''))
        # No extra raw-content cache, model, widget, clipboard write or automatic navigation.

    def _unregister(self):
        if self.registered:
            if not self.api.unregister():
                self.cleanup_failed = True
                self.feedback('Selection hotkey cleanup failed. Exit F7Hub before restarting capture.')
            else:
                self.registered = False
                QApplication.instance().removeNativeEventFilter(self)

    def cancel(self):
        self._cancelled.set()

    def close(self):
        # A worker in delayed native rendering cannot be safely killed in-process.
        # Normal Exit guards call this only after it has drained.
        if self.busy:
            self._cancelled.set()
            return False
        self._unregister()
        if self.registered:
            return False
        self.closed = True
        self.timer.stop()
        self.window.statusBar().clearMessage()
        return True
