"""App-owned native hotkey adapter; one retained worker, existing status feedback."""

import ctypes
import os
import queue
import threading
import sys
from pathlib import Path

from PySide6.QtCore import QAbstractNativeEventFilter, QTimer
from PySide6.QtWidgets import QApplication

from f7hub.domain.clipboard import normalize_preview
from f7hub.infrastructure.windows_selection_copy import (
    SelectionCopyError, copy_selection, MSG, HOTKEY_ID,
    HOTKEY_MODIFIERS,
)

from f7hub.infrastructure.windows_latest_paste import (
    WindowsPasteAPI, PASTE_HOTKEY_ID, PasteEffectError, PasteSequenceDiagnostic, paste_latest, target_diagnostic_code,
)


class SelectionCapture(QAbstractNativeEventFilter):
    def __init__(self, window, service, *, api=None):
        super().__init__()
        self.window, self.service = window, service
        self.api = api
        self.target_diagnostic = (
            os.environ.get('F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC') == '1'
            and not getattr(sys, 'frozen', False)
            and (Path(__file__).resolve().parents[3] / '.git').exists()
        )
        self.sequence_diagnostic = (
            os.environ.get('F7HUB_DEV_PASTE_SEQUENCE_DIAGNOSTIC') == '1'
            and not self.target_diagnostic
            and not getattr(sys, 'frozen', False)
            and (Path(__file__).resolve().parents[3] / '.git').exists()
        )
        self._sequence_diagnostic_used = False
        self.started = False
        self.registered = False
        self.paste_registered = False
        self.closed = False
        self.cleanup_failed = False
        self._worker = None
        self._cancelled = threading.Event()
        self._results = queue.Queue(maxsize=1)
        self._release_required = False
        self._release_observed = threading.Event()
        self._release_action = None
        self._capture_release_diagnostic = None  # One bounded RAM record; diagnostic mode only.
        self.timer = QTimer(window)
        self.timer.setInterval(25)
        self.timer.timeout.connect(self.poll)

    @property
    def busy(self):
        return self._worker is not None

    def feedback(self, message):
        self.window.statusBar().showMessage(message, 15000)

    def _release_diagnostic_snapshot(self):
        record = self._capture_release_diagnostic
        if record is None:
            capture, relation = 'NONE', 'NONE'
        else:
            capture = 'A1 W%d R%d G%d L%d F%d D%d S%d' % (
                record['wait_entered'].is_set(), record['release'].is_set(),
                record['gui_seen'], record['latch_cleared'],
                record['finished'].is_set(), record['drained'], record['success'].is_set())
            relation = 'SAME' if record['release'] is self._release_observed else 'OTHER'
        owner = {'capture': 'CAPTURE', 'paste': 'PASTE'}.get(self._release_action, 'NONE')
        try:
            keys = 'DOWN' if self.api.paste_keys_down() else 'UP'
        except Exception:
            keys = 'UNKNOWN'
        return (' C[' + capture + ']; O=' + owner + '; E=' + relation
                + '; LATCH=%d; EVENT=%d; K=' % (self._release_required, self._release_observed.is_set()) + keys + '.')

    def diagnostic_feedback(self, code):
        self.window.statusBar().showMessage(
            'Paste Target Diagnostic: ' + target_diagnostic_code(code) + '.'
            + self._release_diagnostic_snapshot()
            + ' Clipboard: UNCHANGED; Ctrl+V: NOT_SENT; authorization: NOT_REQUESTED.', 0)

    def start(self):
        if self.started or self.closed:
            return
        self.started = True
        if self.api is None:
            if os.name != 'nt':
                return
            try:
                self.api = WindowsPasteAPI()
            except Exception:
                self.feedback('Selection capture unavailable: native initialization failed.')
                return
        self.registered = bool(self.api.register())
        self.paste_registered = bool(self.api.register_paste())
        if self.registered or self.paste_registered:
            QApplication.instance().installNativeEventFilter(self)
            self.timer.start()
        ready = []
        for chord, registered in (('Win+Alt+C', self.registered), ('Win+Alt+V', self.paste_registered)):
            ready.append(chord + (' ready' if registered else ' unavailable or already registered'))
        self.feedback('; '.join(ready) + '. Release the chord after each explicit operation.'
                      + (' Paste target diagnostic enabled; Win+Alt+V has no paste effects.'
                         if self.target_diagnostic else ''))

    def nativeEventFilter(self, event_type, message):
        if self.closed or not (self.registered or self.paste_registered) or not bytes(event_type).startswith(b'windows_'):
            return False, 0
        native = ctypes.cast(int(message), ctypes.POINTER(MSG)).contents
        if native.message != 0x0312 or (int(native.lParam) & 0xFFFF) != (HOTKEY_MODIFIERS & ~0x4000):
            return False, 0
        key = (int(native.lParam) >> 16) & 0xFFFF
        if self.registered and native.wParam == HOTKEY_ID and key == 0x43:
            self.trigger()
            return True, 0
        if self.paste_registered and native.wParam == PASTE_HOTKEY_ID and key == 0x56:
            self.trigger(action='paste')
            return True, 0
        return False, 0

    def _rearm_if_released(self):
        # Decisions are unchanged; diagnostic flags record the actual sampled event.
        if self._release_required:
            signaled = self._release_observed.is_set()
            record = self._capture_release_diagnostic
            capture_event = record is not None and record['release'] is self._release_observed
            if capture_event and signaled:
                record['gui_seen'] = True
            if signaled or not self.api.paste_keys_down():
                self._release_required = False
                if capture_event:
                    record['latch_cleared'] = True

    def trigger(self, *, action='capture'):
        registered = self.registered if action == 'capture' else self.paste_registered
        diagnostic = action == 'paste' and self.target_diagnostic
        for blocked, code in (
            (action not in ('capture', 'paste'), 'UNCLASSIFIED_GUARD'),
            (self.closed, 'ADMISSION_CLOSED'),
            (self.cleanup_failed, 'ADMISSION_CLEANUP_DISABLED'),
            (not registered, 'ADMISSION_UNREGISTERED'),
            (self.busy, 'ADMISSION_BUSY'),
        ):
            if blocked:
                if diagnostic:
                    if code == 'ADMISSION_BUSY' and isinstance(self._worker, threading.Thread):
                        if not self._worker.is_alive():
                            code = 'ADMISSION_WORKER_COMPLETE_PENDING_DRAIN'
                        elif self._release_action != action:
                            code = 'ADMISSION_OTHER_OPERATION_PENDING'
                    self.diagnostic_feedback(code)
                return False
        if action == 'paste' and self.sequence_diagnostic and self._sequence_diagnostic_used:
            return False  # Keep the first diagnostic result; never repeat its write.
        self._rearm_if_released()
        if self._release_required:
            if diagnostic:
                if self._release_observed.is_set():
                    code = 'ADMISSION_RELEASE_EVENT_SIGNALED_NOT_RECONCILED'
                else:
                    code = ('ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN'
                            if self.api.paste_keys_down() else 'ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_UP')
                self.diagnostic_feedback(code)
            return False
        sequence_record = PasteSequenceDiagnostic() if action == 'paste' and self.sequence_diagnostic else None
        if sequence_record is not None:
            self._sequence_diagnostic_used = True
        release_observed = threading.Event()
        self._release_observed = release_observed
        self._release_action = action
        capture_diagnostic = None
        if self.target_diagnostic and action == 'capture':
            capture_diagnostic = {
                'wait_entered': threading.Event(), 'release': release_observed,
                'gui_seen': False, 'latch_cleared': False,
                'finished': threading.Event(), 'drained': False, 'success': threading.Event(),
            }
            self._capture_release_diagnostic = capture_diagnostic
        self._release_required = True
        try:
            if action == 'capture':
                self.service.begin_selection_capture()
            target = self.api.foreground()
        except Exception as error:
            if sequence_record is not None:
                self.window.statusBar().showMessage(sequence_record.summary('INITIAL_BINDING_FAILED'), 0)
            elif diagnostic:
                code = ('INITIAL_' + (error.guard or 'UNCLASSIFIED')
                        if isinstance(error, SelectionCopyError) else 'INITIAL_NATIVE_EXCEPTION')
                self.diagnostic_feedback(code)
            else:
                self.feedback('Clipboard operation unavailable: target or service unavailable.')
            return False
        try:
            owner_hwnd = int(self.window.winId()) if action == 'paste' else None
        except Exception:
            if sequence_record is not None:
                self.window.statusBar().showMessage(sequence_record.summary('INITIAL_OWNER_FAILED'), 0)
            elif diagnostic:
                self.diagnostic_feedback('INITIAL_OWNER_WINDOW_FAILED')
            else:
                self.feedback('Clipboard operation unavailable: target or service unavailable.')
            return False
        self._cancelled.clear()
        self.feedback('Checking paste target only. Release Win, Alt and V.' if diagnostic else
                      'Preparing latest saved capture. Release Win, Alt and V.' if action == 'paste'
                      else 'Copying highlighted text. Release Win, Alt and C.')

        def work():
            try:
                if diagnostic:
                    try:
                        code = paste_latest(self.api, target, owner_hwnd, self._cancelled,
                                            None, None, diagnostic=True, on_release=release_observed.set)
                    except PasteEffectError as error:
                        code = error.guard
                        if str(error) == 'CLEANUP_FAILED':
                            self._results.put_nowait(('target_diagnostic_cleanup', code))
                            return
                    self._results.put_nowait(('target_diagnostic', code))
                    return
                if sequence_record is not None:
                    code, clipboard, cleanup = 'GUARDS_PASSED_NO_DISPATCH', 'WRITTEN', False
                    try:
                        self.service.paste_latest(lambda prepare, consume: paste_latest(
                            self.api, target, owner_hwnd, self._cancelled, prepare, consume,
                            on_release=release_observed.set, sequence_diagnostic=sequence_record))
                    except PasteEffectError as error:
                        code, clipboard = str(error), error.clipboard
                        cleanup = code == 'CLEANUP_FAILED'
                    except Exception:
                        code, clipboard = 'AUTHORIZATION_OR_SERVICE_UNAVAILABLE', 'UNCHANGED'
                    self._results.put_nowait(('sequence_diagnostic', (sequence_record.summary(code, clipboard), cleanup)))
                    return
                if action == 'paste':
                    result = self.service.paste_latest(lambda prepare, consume: paste_latest(
                        self.api, target, owner_hwnd, self._cancelled, prepare, consume,
                        on_release=release_observed.set))
                    self._results.put_nowait(('paste_success', result))
                    return
                result = self.service.capture_active_selection(
                    lambda: copy_selection(self.api, target, self._cancelled,
                                           on_release=release_observed.set, with_metadata=True,
                                           on_release_wait=(capture_diagnostic['wait_entered'].set
                                                            if capture_diagnostic is not None else None)), self._cancelled)
                outcome = ('success', result)
            except PasteEffectError as error:
                outcome = ('paste_failure', (str(error), error.clipboard, error.dispatch))
            except SelectionCopyError as error:
                # Fixed native code only. Never stringify arbitrary exceptions.
                outcome = ('failure', str(error))
            except Exception:
                outcome = (('paste_failure', ('AUTHORIZATION_OR_SERVICE_UNAVAILABLE', 'UNCHANGED', 'NOT_SENT'))
                           if action == 'paste' else ('failure', 'ADMISSION_OR_SERVICE_UNAVAILABLE'))
            self._results.put_nowait(outcome)
            if capture_diagnostic is not None:
                if outcome[0] == 'success':
                    capture_diagnostic['success'].set()
                capture_diagnostic['finished'].set()

        self._worker = threading.Thread(target=work, name='f7hub-clipboard-' + action, daemon=True)
        try:
            self._worker.start()
        except RuntimeError:
            self._worker = None
            if sequence_record is not None:
                self.window.statusBar().showMessage(sequence_record.summary('WORKER_START_FAILED'), 0)
            elif diagnostic:
                self.diagnostic_feedback('WORKER_START_FAILED')
            else:
                self.feedback('Clipboard operation not started: worker unavailable.')
            return False
        return True

    def poll(self):
        if self.closed:
            return
        self._rearm_if_released()
        if self._worker is None or self._worker.is_alive():
            return
        self._worker.join(0)
        record = self._capture_release_diagnostic
        if (record is not None and self._release_action == 'capture'
                and record['release'] is self._release_observed):
            record['drained'] = True
        self._worker = None
        kind, result = self._results.get_nowait()
        if kind in ('target_diagnostic', 'target_diagnostic_cleanup'):
            if kind == 'target_diagnostic_cleanup':
                self.cleanup_failed = True
                self._unregister()
            self.diagnostic_feedback(result)
            return
        if kind == 'sequence_diagnostic':
            message, cleanup = result
            if cleanup:
                self.cleanup_failed = True
                self._unregister()
            self.window.statusBar().showMessage(message, 0)
            return
        if kind == 'paste_success':
            self.feedback('Latest saved capture written to Clipboard; Ctrl+V dispatched once. Insertion is not confirmed.')
            return
        if kind == 'paste_failure':
            code, clipboard, dispatch = result
            if code == 'CLEANUP_FAILED':
                self.cleanup_failed = True
                self._unregister()
            self.feedback('Paste Latest: ' + code + '. Clipboard: ' + clipboard
                          + '; Ctrl+V: ' + dispatch + '. No automatic retry or older-item fallback.')
            return
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
        if self.api is None:
            return
        for attribute, unregister in (('registered', self.api.unregister),
                                      ('paste_registered', self.api.unregister_paste)):
            if getattr(self, attribute):
                if not unregister():
                    self.cleanup_failed = True
                    self.feedback('Clipboard hotkey cleanup failed. Exit F7Hub before restarting operations.')
                else:
                    setattr(self, attribute, False)
        if not (self.registered or self.paste_registered):
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
        if self.registered or self.paste_registered:
            return False
        self.closed = True
        self.timer.stop()
        self.window.statusBar().clearMessage()
        return True
