"""Data-free Windows fixture for test_f7hub_restore.ahk; not production IPC.

The external supervisor owns its unique directory/title, command allowlist,
whole-run timeout and process cleanup. No database, Clipboard API or real Mochi.
"""

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

os.environ['QT_QPA_PLATFORM'] = 'windows'

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.gui.application_lifecycle import ApplicationLifecycle
from f7hub.gui.main_window import MainWindow
from Tests.GUI.test_clipboard_setup import RecordingSettingsService
from Tests.GUI.test_main_window import RecordingScriptService, RecordingTicketService


def main():
    directory = Path(os.environ['F7HUB_RESTORE_FIXTURE_DIR']).resolve(strict=True)
    title = os.environ['F7HUB_RESTORE_FIXTURE_TITLE']
    assert title.startswith('F7Hub Restore Fixture ')
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    application = QApplication([])
    window = MainWindow(RecordingTicketService(), script_service=RecordingScriptService(),
                        mochi_service=Mock(), settings_service=RecordingSettingsService())
    window.setWindowTitle(title)
    metrics = dict(expose_events=0, suppressed_repair_notifications=0,
                   callback_queued=0, callback_executed=0,
                   recovery_ticks=0, restores=0, heartbeats=0, metadata_busy=0)
    suppress_exposure = os.environ.get('F7HUB_RESTORE_SUPPRESS_EXPOSURE') == '1'

    class ObservedLifecycle(ApplicationLifecycle):
        def eventFilter(self, watched, event):
            if event.type() == QEvent.Type.Expose:
                metrics['expose_events'] += 1
                if suppress_exposure:
                    metrics['suppressed_repair_notifications'] += 1
                    # Model a missing repair notification without consuming
                    # Qt's own event or changing native visibility/rendering.
                    return QObject.eventFilter(self, watched, event)
            pending = getattr(self, '_exposed_restore_pending', False)
            result = super().eventFilter(watched, event)
            if not pending and getattr(self, '_exposed_restore_pending', False):
                metrics['callback_queued'] += 1
            return result

        def _restore_exposed_window(self):
            metrics['callback_executed'] += 1
            return super()._restore_exposed_window()

        def check_recovery(self):
            metrics['recovery_ticks'] += 1
            return super().check_recovery()

        def restore(self, **options):
            metrics['restores'] += 1
            return super().restore(**options)

    lifecycle = ObservedLifecycle(window)
    last_sequence = -1

    def publish(sequence, action):
        handle = int(window.winId())
        state = dict(sequence=sequence, action=action, pid=os.getpid(),
                     parent_pid=os.getppid(), hwnd=handle,
                     qt_visible=window.isVisible(), rail_visible=window.navigation_rail.isVisible(),
                     win32_visible=bool(user32.IsWindowVisible(handle)),
                     lifecycle_hidden=lifecycle._hidden, maximized=window.isMaximized(),
                     minimized=window.isMinimized(), accepted=lifecycle.accepted,
                     draft_present=window.ticket_create_widget.has_draft(),
                     draft_preserved=window.ticket_create_widget.subject_input.text() == 'Synthetic retained F7 draft',
                     main_windows=sum(isinstance(w, MainWindow) for w in application.topLevelWidgets()),
                     settings_writes=len(window.settings_service.calls),
                     recovery_available=lifecycle.recovery_available(),
                     qwindow_visible=window.windowHandle().isVisible(),
                     qwindow_exposed=window.windowHandle().isExposed(),
                     metrics=dict(metrics), exposure_suppressed=suppress_exposure)
        if state['win32_visible'] and not state['minimized']:
            image = window.screen().grabWindow(handle).toImage()
            sample = image.scaled(160, 100)
            pixels = [sample.pixelColor(x, y) for x in range(sample.width()) for y in range(sample.height())]
            state['white_fraction'] = sum(c.red() > 245 and c.green() > 245 and c.blue() > 245 for c in pixels) / len(pixels)
        temporary = directory / ('state-' + str(sequence) + '.tmp')
        temporary.write_text(json.dumps(state), encoding='utf-8')
        temporary.rename(directory / ('state-' + str(sequence) + '.json'))

    def dispatch():
        nonlocal last_sequence
        metrics['heartbeats'] += 1
        path = directory / 'command.json'
        if not path.exists():
            return
        try:
            command = json.loads(path.read_text(encoding='utf-8'))
        except PermissionError:
            metrics['metadata_busy'] += 1
            return  # Observe the same command later; never dispatch it twice.
        sequence, action = command['sequence'], command['action']
        if sequence <= last_sequence:
            return
        last_sequence = sequence
        if action == 'hide':
            assert lifecycle.recovery_available(), 'Fixture tray must be ready before hide'
            window.close()
        elif action == 'tray-open':
            lifecycle.open_action.trigger()
        elif action == 'maximize':
            window.showMaximized()
        elif action == 'minimize':
            window.showMinimized()
        elif action == 'exit-cancel':
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Cancel) as guard:
                lifecycle.exit_action.trigger()
                guard.assert_called_once()
            assert not lifecycle.accepted
        elif action == 'exit':
            poll.stop()
            window.workspace._clear_drafts()
            window.ticket_create_widget.subject_input.clear()
            assert not window.ticket_create_widget.has_draft()
            lifecycle.exit_action.trigger()
            assert lifecycle.accepted
            publish(sequence, action)
            return
        elif action != 'snapshot':
            raise ValueError('Unknown fixture command')
        QTimer.singleShot(100, lambda: publish(sequence, action))

    poll = QTimer(window)
    poll.setInterval(20)
    poll.timeout.connect(dispatch)
    lifecycle.start()
    window.show()
    window.windowHandle().installEventFilter(lifecycle)
    window.show_new_ticket()
    window.ticket_create_widget.subject_input.setText('Synthetic retained F7 draft')
    poll.start()
    QTimer.singleShot(150, lambda: publish(0, 'ready'))
    exit_code = application.exec()
    (directory / 'exit.json').write_text(json.dumps(dict(exit_code=exit_code, accepted=lifecycle.accepted)))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
