"""Deterministic lifecycle checks; these do not prove native tray recovery."""

import os
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from f7hub.gui.application_lifecycle import ApplicationLifecycle
from f7hub.gui.main_window import MainWindow
from Tests.GUI.test_main_window import RecordingTicketService, RecordingScriptService
from Tests.GUI.test_clipboard_setup import RecordingSettingsService


class ApplicationLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.mochi = Mock()
        self.window = MainWindow(RecordingTicketService(), mochi_service=self.mochi,
                                 script_service=RecordingScriptService(),
                                 settings_service=RecordingSettingsService())
        self.lifecycle = ApplicationLifecycle(self.window)
        self.quit = patch.object(self.app, 'quit').start()
        self.addCleanup(patch.stopall)
        self.window.show()
        self.wait_idle()
        self.recovery = patch.object(self.lifecycle, 'recovery_available', return_value=True).start()

    def wait_idle(self):
        end = time.monotonic() + 5
        while True:
            self.app.processEvents()
            clipboard = self.window.clipboard_workspace
            if not self.window.runner.busy and not self.window.runner.completing and not (
                    clipboard is not None and (clipboard.loading or clipboard.settings_pending)):
                return
            if time.monotonic() > end:
                self.fail('Fixture did not become idle')
            QTest.qWait(5)
            time.sleep(.001)

    def tearDown(self):
        self.wait_idle()
        self.lifecycle.recovery_timer.stop()
        self.lifecycle.tray.hide()
        self.window.deleteLater()
        self.app.sendPostedEvents()
        self.app.processEvents()

    def test_x_hides_without_guards_leave_or_shutdown(self):
        with patch.object(self.window, 'confirm_exit') as guards, patch.object(
                self.window, '_leave_clipboard') as leave:
            self.assertFalse(self.window.close())
        self.assertFalse(self.window.isVisible())
        guards.assert_not_called()
        leave.assert_not_called()
        self.mochi.close.assert_not_called()
        self.quit.assert_not_called()

    def test_repeat_open_preserves_identity_draft_page_selection_and_focus(self):
        self.window.show_new_ticket()
        self.wait_idle()
        editor = self.window.ticket_create_widget.subject_input
        editor.setText('Synthetic retained draft')
        editor.setSelection(3, 9)
        editor.setFocus()
        self.app.processEvents()
        page = self.window.pages.currentWidget()
        count = len([w for w in QApplication.topLevelWidgets() if isinstance(w, MainWindow)])
        tray = self.lifecycle.tray
        for _ in range(3):
            self.window.close()
            self.lifecycle.open_action.trigger()
            self.assertTrue(self.window.isVisible())
            self.assertIs(self.window.pages.currentWidget(), page)
            self.assertEqual(editor.text(), 'Synthetic retained draft')
            self.assertEqual(editor.selectedText(), 'thetic re')
            self.assertIs(self.window.focusWidget(), editor)
            self.assertIs(self.lifecycle.tray, tray)
        self.assertEqual(len([w for w in QApplication.topLevelWidgets() if isinstance(w, MainWindow)]), count)

    def test_clipboard_setup_draft_survives_hide_and_restore(self):
        self.window.show_clipboard()
        self.wait_idle()
        clipboard = self.window.clipboard_workspace
        self.assertTrue(clipboard.show_setup())
        self.wait_idle()
        setup = clipboard.setup
        checkbox = next(iter(setup.checkboxes.values()))
        checkbox.setChecked(not checkbox.isChecked())
        before = setup._draft.copy()
        self.assertTrue(setup.dirty)
        self.window.close()
        self.lifecycle.open_action.trigger()
        self.assertEqual(setup._draft, before)
        self.assertEqual(checkbox.isChecked(), before[checkbox.objectName()])
        self.assertIs(clipboard.sections.currentWidget(), setup)

    def test_all_explicit_entry_points_share_guards_and_cancel(self):
        for entry in (self.window.exit_action.trigger, self.lifecycle.exit_action.trigger,
                      self.window.request_exit):
            with self.subTest(entry=entry), patch.object(self.window, 'confirm_exit', return_value=False) as guard:
                self.window.close()
                entry()
                guard.assert_called_once_with()
                self.assertTrue(self.window.isVisible())
                self.assertFalse(self.lifecycle.accepted)
        self.mochi.close.assert_not_called()
        self.quit.assert_not_called()

    def test_quit_shortcut_uses_shared_exit(self):
        self.assertFalse(self.window.exit_action.shortcut().isEmpty())
        with patch.object(self.window, 'confirm_exit', return_value=False) as guard:
            self.window.activateWindow()
            QTest.keySequence(self.window, self.window.exit_action.shortcut())
            self.app.processEvents()
            guard.assert_called_once_with()

    def test_cancelled_real_ticket_guard_preserves_draft(self):
        self.window.ticket_create_widget.subject_input.setText('Synthetic unsaved')
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.window.request_exit())
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), 'Synthetic unsaved')
        self.assertTrue(self.window.isVisible())
        self.mochi.close.assert_not_called()

    def test_cancelled_clipboard_guard_does_not_end_session(self):
        self.window.show_clipboard()
        self.wait_idle()
        clipboard = self.window.clipboard_workspace
        with patch.object(clipboard, 'confirm_leave', return_value=False), patch.object(clipboard, 'leave') as leave:
            self.assertFalse(self.window.request_exit())
            leave.assert_not_called()
        self.assertTrue(self.window.isVisible())

    def test_pending_ticket_flags_block_exit_but_allow_hide(self):
        for name in ('note_pending', 'creation_pending', 'status_pending', 'classification_pending'):
            # Existing workspace-owned flags guard the idle-before-callback gap.
            owner = self.window.workspace
            pending = (patch.object(type(owner), name, new_callable=lambda: property(lambda _: True))
                       if isinstance(getattr(type(owner), name, None), property)
                       else patch.object(owner, name, True))
            with self.subTest(flag=name), pending:
                self.window.close()
                self.assertFalse(self.window.isVisible())
                self.assertFalse(self.window.request_exit())
                self.assertTrue(self.window.isVisible())
                self.assertIn('try Exit again', self.window.statusBar().currentMessage())
        self.quit.assert_not_called()

    def test_pending_clipboard_blocks_exit(self):
        self.window.show_clipboard()
        self.wait_idle()
        with patch.object(type(self.window.clipboard_workspace), 'settings_pending', new_callable=lambda: property(lambda _: True)):
            self.assertFalse(self.window.request_exit())
        self.mochi.close.assert_not_called()

    def test_accepted_exit_cleans_and_quits_once_including_about_to_quit(self):
        self.assertTrue(self.window.request_exit())
        self.assertFalse(self.window.isVisible())
        self.assertFalse(self.window.request_exit())
        self.lifecycle._about_to_quit()
        self.mochi.close.assert_called_once_with()
        self.quit.assert_called_once_with()

    def test_reentrant_exit_does_not_repeat_guards(self):
        def guard():
            self.assertFalse(self.window.request_exit())
            return False
        with patch.object(self.window, 'confirm_exit', side_effect=guard) as guards:
            self.window.request_exit()
            guards.assert_called_once_with()

    def test_unavailable_tray_keeps_visible_draft_and_no_cleanup(self):
        self.recovery.return_value = False
        self.window.ticket_create_widget.subject_input.setText('Synthetic recovery')
        self.window.close()
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), 'Synthetic recovery')
        self.mochi.close.assert_not_called()

    def test_disappeared_tray_restores_window(self):
        self.window.close()
        self.recovery.return_value = False
        self.lifecycle.check_recovery()
        self.assertTrue(self.window.isVisible())

    def test_activation_recovers_minimized_window(self):
        self.window.showMinimized()
        self.lifecycle._activated(QSystemTrayIcon.ActivationReason.Trigger)
        self.assertTrue(self.window.isVisible())
        self.assertFalse(self.window.isMinimized())

    def test_native_visibility_repairs_hidden_widgets_without_expose_or_activation(self):
        self.window.showMaximized()
        self.window.close()
        with patch('f7hub.gui.application_lifecycle.is_native_window_visible', return_value=True), patch.object(
                self.window, 'raise_') as raise_window, patch.object(
                self.window, 'activateWindow') as activate, patch.object(
                self.window, 'showNormal', wraps=self.window.showNormal) as show:
            self.lifecycle.check_recovery()
            self.lifecycle.check_recovery()
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.navigation_rail.isVisible())
        self.assertFalse(self.window.isMaximized())
        self.assertFalse(self.lifecycle._hidden)
        self.assertFalse(self.window.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating))
        show.assert_called_once_with()
        raise_window.assert_not_called()
        activate.assert_not_called()
        self.assertEqual(self.lifecycle.recovery_timer.interval(), 1000)

    def test_hidden_native_window_does_not_reopen_without_show(self):
        self.window.close()
        with patch('f7hub.gui.application_lifecycle.is_native_window_visible', return_value=False):
            self.lifecycle.check_recovery()
        self.assertFalse(self.window.isVisible())
        self.assertTrue(self.lifecycle._hidden)
        self.assertEqual(self.lifecycle.recovery_timer.interval(), 100)

    def test_accepted_exit_ignores_native_visibility(self):
        self.assertTrue(self.lifecycle.request_exit())
        with patch('f7hub.gui.application_lifecycle.is_native_window_visible', return_value=True) as query, patch.object(
                self.window, 'showNormal') as show:
            self.lifecycle.check_recovery()
        show.assert_not_called()
        query.assert_not_called()
        self.assertFalse(self.window.isVisible())

    def test_in_progress_exit_does_not_reenter_recovery(self):
        self.window.close()
        self.lifecycle.exiting = True
        try:
            with patch('f7hub.gui.application_lifecycle.is_native_window_visible', return_value=True) as query:
                self.lifecycle.check_recovery()
            query.assert_not_called()
            self.assertFalse(self.window.isVisible())
        finally:
            self.lifecycle.exiting = False

    def test_availability_alone_does_not_authorize_hiding(self):
        self.lifecycle.started = True
        with patch.object(QSystemTrayIcon, 'isSystemTrayAvailable', return_value=True), patch.object(
                self.lifecycle.tray, 'isVisible', return_value=True), patch.object(
                self.lifecycle.tray, 'geometry', return_value=QRect()):
            self.assertFalse(ApplicationLifecycle.recovery_available(self.lifecycle))

    def test_duplicate_lifecycle_rejected(self):
        with self.assertRaises(ValueError):
            ApplicationLifecycle(self.window)

    def test_tray_start_is_idempotent(self):
        previous = self.app.quitOnLastWindowClosed()
        try:
            with patch.object(self.lifecycle.tray, 'show') as show:
                self.lifecycle.start()
                self.lifecycle.start()
            show.assert_called_once_with()
            self.assertFalse(self.app.quitOnLastWindowClosed())
            self.assertTrue(self.lifecycle.recovery_timer.isActive())
        finally:
            self.app.setQuitOnLastWindowClosed(previous)

    def test_hide_restore_never_reads_clipboard_or_changes_settings(self):
        with patch.object(QApplication, 'clipboard') as clipboard:
            for _ in range(2):
                self.window.close()
                self.lifecycle.open_action.trigger()
            clipboard.assert_not_called()
        self.assertEqual(self.window.settings_service.calls, [])

    def test_maximized_restore_and_failed_activation_keep_visible_recovery(self):
        self.window.showMaximized()
        self.window.close()
        with patch.object(self.window, 'activateWindow'):
            self.assertTrue(self.lifecycle.restore())
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.isMaximized())

    def test_cancel_from_visible_window_preserves_maximization_and_current_focus(self):
        self.window.showMaximized()
        self.window.ticket_create_widget.subject_input.setFocus()
        self.window.close()
        self.lifecycle.restore()
        editor = self.window.workspace.subject_search_input
        editor.setFocus()
        with patch.object(self.window, 'confirm_exit', return_value=False):
            self.assertFalse(self.window.request_exit())
        self.assertTrue(self.window.isMaximized())
        self.assertIs(self.window.focusWidget(), editor)


if __name__ == '__main__':
    unittest.main()
