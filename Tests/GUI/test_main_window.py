from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
import threading
import time
import unittest
from collections import Counter
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox, QToolBar, QToolButton, QLabel
from PySide6.QtTest import QTest
from PySide6.QtCore import QEvent, QPoint, QTimer, Qt
from PySide6.QtGui import QColor, QIcon, QPalette

from f7hub.gui.main_window import MainWindow
from f7hub.services.ticket_service import TicketService
from f7hub.services.altf7hub_service import AltF7HubService, AltF7HubOpenError
from Tests.GUI.test_clipboard_workspace import RecordingClipboardService


class RecordingTicketService:
    def __init__(self):
        self.calls = 0
        self.gate = None
        self.error = None
        self.ticket = SimpleNamespace(
            ticket_id=1, ticket_number="TKT-1001", subject="Printer offline",
            description="Test printer", status="NEW", priority="MEDIUM",
            ticket_type="INCIDENT",
            assigned_to=None, created_at="2026-09-04T15:00:00.000Z",
            updated_at="2026-09-04T15:00:00.000Z", resolved_at=None,
            closed_at=None, resolution=None,
            company_id=None, contact_id=None, category_id=None,
        )

    def create_ticket(self, **values: object) -> object:
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        return self.ticket

    def list_tickets(self, **values):
        return (self.ticket,)

    def get_ticket_details(self, ticket_id):
        return SimpleNamespace(ticket=self.ticket, notes=(), status_history=(), timeline_events=(),
                               company_name=None, contact_name=None, category_name=None)

    allowed_statuses = staticmethod(TicketService.allowed_statuses)


class RecordingBackupService:
    def __init__(self):
        self.calls = 0
        self.gate = None
        self.error = None
        self.path = Path(r"C:\local\F7Hub\Backups\F7Hub-Database-example.db")

    def create_backup(self):
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        return self.path


class RecordingScriptService:
    def __init__(self):
        self.calls = 0
        self.gate = None

    def list_scripts(self, *, text_query=None):
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        return ()


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.service = RecordingTicketService()
        self.backup = RecordingBackupService()
        self.scripts = RecordingScriptService()
        self.window = MainWindow(self.service, backup_service=self.backup,
                                 script_service=self.scripts)
        self.window.show()
        self.application.processEvents()
        self.wait_idle()

    def tearDown(self) -> None:
        if self.window.clipboard_workspace is not None:
            service = self.window.clipboard_workspace._service
            if getattr(service, "gate", None) is not None:
                service.gate.set()
            deadline = time.monotonic() + 5
            while self.window.clipboard_workspace.loading and time.monotonic() < deadline:
                QTest.qWait(5)
                time.sleep(0.001)
            self.assertFalse(self.window.clipboard_workspace.loading)
        if self.service.gate:
            self.service.gate.set()
        if self.backup.gate:
            self.backup.gate.set()
        if self.scripts.gate:
            self.scripts.gate.set()
        self.wait_idle()
        self.window.workspace._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    @staticmethod
    def _icon_colors(button, mode=QIcon.Mode.Normal):
        image = button.icon().pixmap(24, 24, mode).toImage()
        return {image.pixelColor(x, y).name() for y in range(image.height())
                for x in range(image.width()) if image.pixelColor(x, y).alpha() == 255}

    def test_navigation_rail_uses_effective_palette_at_creation_and_runtime(self):
        original = QPalette(self.application.palette())
        try:
            for background, foreground, hover, highlight, selected in (
                ("#000000", "#ffff00", "#008800", "#ff00ff", "#000000"),
                ("#ffffff", "#000080", "#dddddd", "#0000aa", "#ffffff"),
            ):
                palette = QPalette(original)
                palette.setColor(QPalette.ColorRole.Window, QColor(background))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(foreground))
                palette.setColor(QPalette.ColorRole.Button, QColor(hover))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(foreground))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(highlight))
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor(selected))
                palette.setColor(QPalette.ColorGroup.Disabled,
                                 QPalette.ColorRole.WindowText, QColor("#777777"))
                self.application.setPalette(palette)
                self.application.processEvents()
                rail = self.window.navigation_rail
                tickets = self.window.navigation_buttons["tickets"]
                scripts = self.window.navigation_buttons["scripts"]
                self.assertIn(f"background: {background}", rail.styleSheet())
                self.assertIn(f"background: {hover}", rail.styleSheet())
                self.assertIn(f"background: {highlight}", rail.styleSheet())
                self.assertIn(f"border: 2px dashed {foreground}", rail.styleSheet())
                self.assertTrue(tickets.property("active"))
                self.assertIn(selected, self._icon_colors(tickets))
                self.assertIn(foreground, self._icon_colors(self.window.navigation_buttons["clipboard"]))
                self.assertIn("#777777", self._icon_colors(scripts, QIcon.Mode.Disabled))
                self.assertEqual(tickets.grab().toImage().pixelColor(38, 22).name(), highlight)
                self.window.scripts_action.setEnabled(False)
                self.application.processEvents()
                self.assertFalse(scripts.isEnabled())
                self.assertIn("#777777", self._icon_colors(scripts, QIcon.Mode.Disabled))
                self.window.scripts_action.setEnabled(True)
                tickets.setFocus()
                self.application.processEvents()
                self.assertTrue(tickets.hasFocus())
                QTest.mouseMove(tickets, QPoint(12, 12))
                self.application.processEvents()
                self.assertEqual(tickets.grab().toImage().pixelColor(1, 22).name(), selected)
                clipboard = self.window.navigation_buttons["clipboard"]
                QTest.mouseMove(clipboard, QPoint(12, 12))
                self.application.processEvents()
                if self.application.platformName() == "offscreen":
                    self.assertTrue(clipboard.underMouse())
                    self.assertEqual(clipboard.grab().toImage().pixelColor(38, 22).name(), hover)

            alternate = MainWindow(RecordingTicketService())
            try:
                alternate.show()
                self.application.processEvents()
                self.assertIn("#ffffff", alternate.navigation_rail.styleSheet())
                self.assertIn("#ffffff", self._icon_colors(alternate.navigation_buttons["tickets"]))
            finally:
                alternate.close()
                alternate.deleteLater()
                self.application.processEvents()
        finally:
            self.application.setPalette(original)
            self.application.processEvents()

    def test_window_hosts_ticket_form_and_application_chrome(self) -> None:
        self.assertEqual(self.window.windowTitle(), "F7Hub")
        shell = self.window.centralWidget()
        self.assertEqual(shell.objectName(), "navigationShell")
        self.assertIs(shell.layout().itemAt(0).widget(), self.window.navigation_rail)
        self.assertIs(shell.layout().itemAt(1).widget(), self.window.workspace_viewport)
        self.assertIs(self.window.workspace_viewport.widget(), self.window.pages)
        self.assertIs(self.window.pages.parentWidget(), self.window.workspace_viewport.viewport())
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertEqual(self.window.statusBar().currentMessage(), "Ready")
        self.assertEqual(self.window.exit_action.objectName(), "exitAction")

    def test_guide_action_preserves_workspace_and_unsaved_ticket(self):
        gate = threading.Event()
        calls = []

        class Gateway:
            def show_guide(self):
                calls.append(True)
                gate.wait(3)
                return "SHOWN"

        self.window.altf7hub_service = AltF7HubService(Gateway())
        self.window._set_busy(False)
        self.window.ticket_create_widget.subject_input.setText("Unsaved ticket")
        page = self.window.pages.currentWidget()
        self.window.altf7hub_action.trigger()
        self.window.show_altf7hub()
        QTest.qWait(25)
        self.assertTrue(self.window.runner.busy)
        self.assertFalse(self.window.altf7hub_action.isEnabled())
        gate.set()
        self.wait_idle()
        self.assertEqual(len(calls), 1)
        self.assertIs(self.window.pages.currentWidget(), page)
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), "Unsaved ticket")
        self.assertIn("Guide opened", self.window.statusBar().currentMessage())

    def test_composed_clipboard_has_its_own_runner_and_retains_one_read(self):
        service = RecordingClipboardService()
        service.gate = threading.Event()
        self.addCleanup(service.gate.set)
        self.window.clipboard_service = service
        self.assertIsNone(self.window.clipboard_workspace)
        self.assertTrue(self.window.show_clipboard())
        clipboard = self.window.clipboard_workspace
        self.assertIs(clipboard._service, service)
        self.assertIsNot(clipboard.runner, self.window.runner)
        self.assertTrue(clipboard.loading)
        self.assertFalse(self.window.runner.busy)
        self.assertTrue(self.window.pages.isEnabled())
        self.assertTrue(self.window.tickets_action.isEnabled())
        self.assertTrue(self.window.scripts_action.isEnabled())
        self.assertTrue(self.window.show_clipboard())
        self.assertIs(self.window.clipboard_workspace, clipboard)
        self.assertFalse(self.window.close())
        self.window.show_scripts()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.window.show_tickets()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertTrue(clipboard.loading)
        service.gate.set()
        deadline = time.monotonic() + 5
        while clipboard.loading and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(clipboard.loading)
        self.assertEqual(service.calls, [50])
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.window.show_clipboard()
        self.assertEqual(service.calls, [50])

    def test_clipboard_close_guard_covers_idle_before_callback(self):
        service = RecordingClipboardService()
        self.window.clipboard_service = service
        self.window.show_clipboard()
        clipboard = self.window.clipboard_workspace
        observed = []
        clipboard.runner.busy_changed.connect(
            lambda busy: observed.append(self.window.close()) if not busy else None)
        deadline = time.monotonic() + 5
        while clipboard.loading and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(clipboard.loading)
        self.assertEqual(observed, [False])
        self.assertTrue(self.window.close())

    def test_composed_clipboard_cancel_does_not_start_read(self):
        service = RecordingClipboardService()
        self.window.clipboard_service = service
        with patch.object(self.window.workspace, "confirm_discard", return_value=False):
            self.assertFalse(self.window.show_clipboard())
        self.assertIsNone(self.window.clipboard_workspace)
        self.assertEqual(service.calls, [])

    def test_clipboard_action_is_shared_and_follows_scripts(self):
        action = self.window.clipboard_action
        self.assertEqual(action.objectName(), "clipboardCenterAction")
        self.assertEqual(action.data(), "clipboard.center")
        self.assertTrue(action.shortcut().isEmpty())
        file_actions = self.window.menuBar().actions()[0].menu().actions()
        toolbar_actions = self.window.findChildren(QToolBar)[0].actions()
        for actions in (file_actions, toolbar_actions):
            self.assertIs(actions[actions.index(self.window.scripts_action) + 1], action)
        self.assertIsNone(self.window.clipboard_workspace)
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)

    def test_clipboard_activation_is_lazy_retained_and_restores_focus(self):
        count = self.window.pages.count()
        self.window.clipboard_action.trigger()
        clipboard = self.window.clipboard_workspace
        self.assertIsNotNone(clipboard)
        self.assertIs(self.window.pages.currentWidget(), clipboard)
        self.assertEqual(self.window.pages.count(), count + 1)
        self.assertTrue(clipboard.back_button.hasFocus())
        for _ in range(3):
            self.assertTrue(self.window.show_clipboard())
            self.assertIs(self.window.clipboard_workspace, clipboard)
            self.assertEqual(self.window.pages.count(), count + 1)
        clipboard.back_button.click()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertTrue(self.window.show_clipboard())
        self.assertIs(self.window.pages.currentWidget(), clipboard)
        self.assertTrue(clipboard.back_button.hasFocus())
        self.window.scripts_action.trigger()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.window.clipboard_action.trigger()
        self.assertIs(self.window.pages.currentWidget(), clipboard)
        self.assertEqual(self.window.pages.count(), count + 1)

    def test_clipboard_without_optional_services_and_idle_close(self):
        window = MainWindow(self.service)
        self.addCleanup(window.deleteLater)
        self.assertFalse(window.knowledge_action.isEnabled())
        self.assertFalse(window.scripts_action.isEnabled())
        self.assertTrue(window.clipboard_action.isEnabled())
        self.assertTrue(window.show_clipboard())
        self.assertEqual(window.clipboard_workspace.unavailable_message.text(),
                         "Clipboard history is not available yet.")
        self.assertTrue(window.close())

    def test_clipboard_pending_owner_guards_cover_idle_callback_gap(self):
        workspace = self.window.workspace
        for owner, field, value in (
            (workspace, "_note_pending", True),
            (workspace, "_creation_pending", True),
            (workspace, "status_pending", True),
            (workspace, "classification_pending", True),
            (self.window.script_workspace, "_run_identity", object()),
            (self.window.ticket_create_widget, "_submitting", True),
        ):
            with self.subTest(field=field), patch.object(owner, field, value):
                self.assertFalse(self.window.runner.busy)
                focus = self.window.focusWidget()
                self.window._set_busy(False)
                self.assertFalse(self.window.clipboard_action.isEnabled())
                self.assertFalse(self.window.show_clipboard())
                self.assertIsNone(self.window.clipboard_workspace)
                self.assertIs(self.window.pages.currentWidget(), workspace)
                self.assertIs(self.window.focusWidget(), focus)
                self.assertFalse(self.window.close())
            self.window._set_busy(False)
        self.assertTrue(self.window.clipboard_action.isEnabled())
        self.assertTrue(self.window.show_clipboard())

    def test_clipboard_shared_worker_refusal_then_recovery(self):
        self.scripts.gate = threading.Event()
        self.window.show_scripts()
        self.assertTrue(self.window.runner.busy)
        count = self.window.pages.count()
        focus = self.window.focusWidget()
        self.assertFalse(self.window.clipboard_action.isEnabled())
        self.assertFalse(self.window.show_clipboard())
        self.assertIsNone(self.window.clipboard_workspace)
        self.assertEqual(self.window.pages.count(), count)
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.assertIs(self.window.focusWidget(), focus)
        self.scripts.gate.set()
        self.wait_idle()
        self.assertTrue(self.window.clipboard_action.isEnabled())
        self.assertTrue(self.window.show_clipboard())

    def test_clipboard_ticket_draft_cancel_preserves_page_values_and_focus(self):
        workspace = self.window.workspace
        workspace.note_input.setPlainText("Keep this note")
        workspace.reason_input.setText("Keep this reason")
        workspace.subject_search_input.setFocus()
        focus = self.window.focusWidget()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
            self.assertFalse(self.window.show_clipboard())
        prompt.assert_called_once()
        self.assertEqual(prompt.call_args.args[-1], QMessageBox.StandardButton.Cancel)
        self.assertIsNone(self.window.clipboard_workspace)
        self.assertIs(self.window.pages.currentWidget(), workspace)
        self.assertEqual(workspace.note_input.toPlainText(), "Keep this note")
        self.assertEqual(workspace.reason_input.text(), "Keep this reason")
        self.assertIs(self.window.focusWidget(), focus)

    def test_clipboard_ticket_discard_cleans_only_after_confirmation(self):
        workspace = self.window.workspace
        workspace.note_input.setPlainText("Discard this note")
        workspace.reason_input.setText("Discard this reason")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard) as prompt:
            self.assertTrue(self.window.show_clipboard())
        prompt.assert_called_once()
        self.assertEqual(workspace.note_input.toPlainText(), "")
        self.assertEqual(workspace.reason_input.text(), "")
        with patch.object(workspace, "confirm_discard", side_effect=AssertionError("Repeated activation must not discard")):
            self.assertTrue(self.window.show_clipboard())

    def test_clipboard_retains_creation_draft_and_hidden_close_guard(self):
        self.window.show_new_ticket()
        form = self.window.ticket_create_widget
        form.subject_input.setText("Keep unsaved creation")
        self.assertTrue(self.window.show_clipboard())
        self.assertTrue(self.window.workspace.creating)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
            self.assertFalse(self.window.close())
        self.assertEqual(prompt.call_args.args[1], "Unsaved new ticket")
        self.assertEqual(form.subject_input.text(), "Keep unsaved creation")
        self.assertIs(self.window.pages.currentWidget(), self.window.clipboard_workspace)
        self.window.clipboard_workspace.back_button.click()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertTrue(self.window.workspace.creating)
        self.assertEqual(form.subject_input.text(), "Keep unsaved creation")
        self.assertEqual(self.service.calls, 0)

    def test_guide_failure_is_safe_and_retryable(self):
        class Gateway:
            def show_guide(self):
                raise AltF7HubOpenError("Install AutoHotkey v2 and retry.")

        self.window.altf7hub_service = AltF7HubService(Gateway())
        self.window._set_busy(False)
        with patch("f7hub.gui.main_window.QMessageBox.warning") as warning:
            self.window.altf7hub_action.trigger()
            self.wait_idle()
        self.assertIn("Install AutoHotkey v2", warning.call_args.args[2])
        self.assertTrue(self.window.altf7hub_action.isEnabled())
        self.assertIn("not confirmed", self.window.statusBar().currentMessage())

    def test_guide_unexpected_error_does_not_expose_internal_detail(self):
        class Gateway:
            def show_guide(self):
                raise RuntimeError("private internal value")

        self.window.altf7hub_service = AltF7HubService(Gateway())
        self.window._set_busy(False)
        with patch("f7hub.gui.main_window.QMessageBox.warning") as warning:
            self.window.altf7hub_action.trigger()
            self.wait_idle()
        self.assertNotIn("private", warning.call_args.args[2])

    def test_created_ticket_updates_application_status(self) -> None:
        self.window.show_new_ticket()
        self.window.ticket_create_widget.subject_input.setText("Printer offline")

        self.window.ticket_create_widget.submit()
        self.wait_idle()

        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertEqual(self.window.workspace.details.ticket.ticket_number, "TKT-1001")
        self.assertEqual(self.window.workspace.model.rowCount(), 1)
        self.assertIn("Category: Not selected", self.window.workspace.summary.toPlainText())
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), "")

    def test_worker_keeps_event_loop_responsive_and_prevents_duplicate_submission(self):
        self.service.gate = threading.Event()
        self.window.show_new_ticket()
        self.window.ticket_create_widget.subject_input.setText("Pending save")
        self.window.ticket_create_widget.submit()
        self.window.ticket_create_widget.submit()
        ticks = []
        QTimer.singleShot(0, lambda: ticks.append(True))
        QTest.qWait(30)
        self.assertTrue(ticks)
        self.assertTrue(self.window.runner.busy)
        self.assertFalse(self.window.pages.isEnabled())
        self.assertFalse(self.window.close())
        self.assertTrue(self.window.isVisible())
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(self.service.calls, 1)

    def test_failed_background_save_preserves_new_ticket_draft(self):
        self.service.error = RuntimeError("Sensitive internal details")
        self.window.show_new_ticket()
        self.window.ticket_create_widget.subject_input.setText("Keep draft")
        self.window.ticket_create_widget.submit()
        self.wait_idle()
        form = self.window.ticket_create_widget
        self.assertEqual(form.subject_input.text(), "Keep draft")
        self.assertNotIn("Sensitive", form.form_error.text())
        self.assertTrue(form.save_button.isEnabled())
        self.assertIs(self.window.workspace.detail_stack.currentWidget(), self.window.workspace.creation_panel)

    def test_saved_ticket_navigation_loads_and_opens_selected_row(self):
        self.window.show_tickets()
        self.wait_idle()
        workspace = self.window.workspace
        workspace._activate_row(workspace.model.index(0, 0))
        self.wait_idle()
        self.assertEqual(workspace.details.ticket.ticket_id, 1)
        self.assertIn("Printer offline", workspace.heading.text())
        self.assertIn("Type: Incident", workspace.summary.toPlainText())

    def test_scripts_action_opens_stacked_workspace_and_loads_catalog(self):
        self.assertEqual(self.window.scripts_action.text(), "Scripts")
        self.assertIn(self.window.scripts_action, self.window.menuBar().actions()[0].menu().actions())
        self.assertIn(self.window.scripts_action, self.window.findChildren(type(self.window.scripts_action)))
        self.assertEqual(self.window.pages.indexOf(self.window.script_workspace), 1)
        self.window.scripts_action.trigger()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.assertEqual(self.window.script_workspace.heading.text(), "Scripts")
        self.assertEqual(self.scripts.calls, 1)
        self.window.show_new_ticket()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)

    def test_script_load_keeps_window_and_page_alive_until_worker_finishes(self):
        self.scripts.gate = threading.Event()
        self.window.show_scripts()
        self.assertTrue(self.window.runner.busy)
        self.assertFalse(self.window.scripts_action.isEnabled())
        self.assertFalse(self.window.pages.isEnabled())
        self.assertFalse(self.window.close())
        self.assertTrue(self.window.isVisible())
        self.window.show_tickets()
        self.window.show_scripts()
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.scripts.gate.set()
        self.wait_idle()
        self.assertEqual(self.scripts.calls, 1)
        self.assertTrue(self.window.scripts_action.isEnabled())

    def test_inline_and_remaining_ticket_actions_fit_1000_by_700(self):
        self.window.show_tickets()
        self.wait_idle()
        self.window.resize(1000, 700)
        self.application.processEvents()
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        workspace = self.window.workspace
        for button in (workspace.edit_subject_button, workspace.apply_properties_button,
                       workspace.edit_description_button,
                       workspace.reload_button):
            self.assertTrue(button.isVisible())

    def test_quick_note_requires_loaded_ticket_and_nonblank_input(self):
        workspace = self.window.workspace
        self.assertFalse(workspace.add_note_button.isEnabled())
        workspace.note_input.setPlainText("No ticket loaded")
        workspace.add_note()
        self.assertFalse(self.window.runner.busy)
        self.assertFalse(workspace.note_pending)
        self.window.show_tickets()
        self.wait_idle()
        workspace.open_ticket(1)
        self.wait_idle()
        self.assertTrue(workspace.add_note_button.isEnabled())
        workspace.note_input.setPlainText(" \n\t")
        self.assertFalse(workspace.add_note_button.isEnabled())

    def test_quick_note_controls_remain_reachable_all_tabs_at_1000_by_700(self):
        self.window.show_tickets()
        self.wait_idle()
        self.window.workspace.open_ticket(1)
        self.wait_idle()
        self.window.resize(1000, 700)
        workspace = self.window.workspace
        for index in range(workspace.detail_tabs.count()):
            workspace.detail_tabs.setCurrentIndex(index)
            self.application.processEvents()
            self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
            for control in (workspace.author_input, workspace.note_type,
                            workspace.note_input, workspace.add_note_button):
                self.assertTrue(control.isVisible())
                scroll = self.window.workspace_viewport
                for corner in (control.rect().topLeft(), control.rect().bottomRight()):
                    point = control.mapTo(self.window.pages, corner)
                    scroll.ensureVisible(point.x(), point.y(), 1, 1)
                    self.application.processEvents()
                    self.assertTrue(scroll.viewport().rect().contains(
                        control.mapTo(scroll.viewport(), corner)))

    def test_backup_action_runs_once_on_worker_and_reports_local_snapshot(self):
        self.assertIn(self.window.backup_action, self.window.menuBar().actions()[0].menu().actions())
        self.assertEqual(self.window.backup_action.text(), "Back up database")
        self.backup.gate = threading.Event()
        with patch("f7hub.gui.main_window.QMessageBox.information") as message:
            self.window.backup_action.trigger()
            self.assertTrue(self.window.runner.busy)
            self.assertFalse(self.window.backup_action.isEnabled())
            ticks = []
            QTimer.singleShot(0, lambda: ticks.append(True))
            QTest.qWait(20)
            self.assertTrue(ticks)
            self.window.back_up_database()
            self.assertFalse(self.window.close())
            self.backup.gate.set()
            self.wait_idle()
        self.assertEqual(self.backup.calls, 1)
        self.assertTrue(self.window.backup_action.isEnabled())
        self.assertIn("completed", self.window.statusBar().currentMessage())
        body = message.call_args.args[2]
        self.assertIn(str(self.backup.path), body)
        self.assertIn("local SQLite data only", body)
        self.assertIn("another location", body)

    def test_backup_failure_is_safe_and_restores_action(self):
        self.backup.error = RuntimeError("PRIVATE_BACKUP_ERROR")
        with patch("f7hub.gui.main_window.QMessageBox.warning") as message:
            self.window.backup_action.trigger()
            self.wait_idle()
        self.assertEqual(self.backup.calls, 1)
        self.assertTrue(self.window.backup_action.isEnabled())
        self.assertIn("failed", self.window.statusBar().currentMessage())
        self.assertNotIn("PRIVATE_BACKUP_ERROR", message.call_args.args[2])
        self.assertIn("No completed backup", message.call_args.args[2])

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Background task did not finish")


class NavigationRailTests(unittest.TestCase):
    """Activate the real shared-action controls, including modal Cancel paths."""

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        from Tests.GUI.test_knowledge_workspace import RecordingKnowledgeService
        from Tests.GUI.test_clipboard_setup import RecordingSettingsService
        self.service = RecordingTicketService()
        self.backup = RecordingBackupService()
        self.scripts = RecordingScriptService()
        self.knowledge = RecordingKnowledgeService()
        self.settings = RecordingSettingsService()
        self.window = MainWindow(
            self.service, knowledge_service=self.knowledge, script_service=self.scripts,
            clipboard_service=RecordingClipboardService(), settings_service=self.settings,
        )
        self.window.show()
        self.application.processEvents()
        self.wait_idle()

    def tearDown(self):
        if self.window.clipboard_workspace is not None and self.window.clipboard_workspace.setup is not None:
            self.window.clipboard_workspace.setup.cancel()
        MainWindowTests.tearDown(self)
    wait_idle = MainWindowTests.wait_idle

    def active(self, key):
        self.assertEqual([name for name, button in self.window.navigation_buttons.items()
                          if button.property("active")], [key])

    def test_startup_tab_enters_rail_before_workspace_and_reverse_order(self):
        self.assertIs(self.application.activeWindow(), self.window)
        self.assertIs(self.window.focusWidget(), self.window.workspace_viewport)
        keys = ("tickets", "knowledge", "scripts", "clipboard")
        for key in keys:
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])
        QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
        self.application.processEvents()
        self.assertIs(self.application.focusWidget(), self.window.workspace.new_ticket_button)
        for key in reversed(keys):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Backtab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])

    def test_ticket_queue_tab_route_exits_and_preserves_keyboard_selection(self):
        """Traverse from the active window; never inject focus into the queue."""
        workspace = self.window.workspace
        second_ticket = SimpleNamespace(**{**vars(self.service.ticket), "ticket_id": 2,
                                           "ticket_number": "TKT-1002"})
        workspace.model.replace_tickets((self.service.ticket, second_ticket))
        path = []

        def step(key):
            before = self.application.focusWidget()
            QTest.keyClick(before, key)
            self.application.processEvents()
            after = self.application.focusWidget()
            path.append((type(before).__name__, before.objectName(),
                         key.name, type(after).__name__, after.objectName(),
                         workspace.table.currentIndex().row(),
                         workspace.table.currentIndex().column()))
            return after

        try:
            self.assertIs(self.application.activeWindow(), self.window)
            self.assertIs(self.application.focusWidget(), self.window.workspace_viewport)
            for rail_key in ("tickets", "knowledge", "scripts", "clipboard"):
                self.assertIs(step(Qt.Key.Key_Tab), self.window.navigation_buttons[rail_key])
            self.assertIs(step(Qt.Key.Key_Tab), workspace.new_ticket_button)
            for rail_key in ("clipboard", "scripts", "knowledge", "tickets"):
                self.assertIs(step(Qt.Key.Key_Backtab), self.window.navigation_buttons[rail_key])
            for _ in range(4):
                step(Qt.Key.Key_Tab)
            self.assertIs(self.application.focusWidget(), workspace.new_ticket_button)

            for _ in range(24):
                if self.application.focusWidget() is workspace.table:
                    break
                step(Qt.Key.Key_Tab)
            self.assertIs(self.application.focusWidget(), workspace.table)
            self.assertFalse(workspace.table.tabKeyNavigation())
            selected = workspace.table.currentIndex()
            self.assertTrue(selected.isValid())
            step(Qt.Key.Key_Down)
            self.assertIs(self.application.focusWidget(), workspace.table)
            self.assertEqual(workspace.table.currentIndex().row(), 1)
            self.assertTrue(workspace.table.selectionModel().isRowSelected(1))
            step(Qt.Key.Key_Space)
            self.assertEqual(workspace.table.currentIndex().row(), 1)
            selected = workspace.table.currentIndex()
            left = step(Qt.Key.Key_Backtab)
            self.assertIsNot(left, workspace.table)
            self.assertTrue(left.isEnabled())
            self.assertIs(step(Qt.Key.Key_Tab), workspace.table)
            self.assertEqual(workspace.table.currentIndex(), selected)
            right = step(Qt.Key.Key_Tab)
            self.assertIsNot(right, workspace.table)
            self.assertTrue(right.isEnabled())
            self.assertEqual(workspace.table.currentIndex(), selected)
            self.assertIs(step(Qt.Key.Key_Backtab), workspace.table)
            # The rail remains reachable by reverse traversal after queue entry.
            for _ in range(24):
                if self.application.focusWidget() is self.window.navigation_buttons["scripts"]:
                    break
                step(Qt.Key.Key_Backtab)
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons["scripts"])
            self.scripts.gate = threading.Event()
            calls = self.scripts.calls
            step(Qt.Key.Key_Space)
            self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
            self.assertEqual(self.scripts.calls, calls + 1)
            self.scripts.gate.set()
            self.wait_idle()
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons["scripts"])
            chosen = self.window.menuBar()
            chosen.setFocus()
            self.application.processEvents()
            QTest.qWait(5)
            self.assertIs(self.application.focusWidget(), chosen)
        except AssertionError:
            self.fail(f"Ticket keyboard path: {path!r}")

    def test_ticket_queue_enter_keeps_existing_open_action(self):
        path = []
        table = self.window.workspace.table
        try:
            self.assertIs(self.application.focusWidget(), self.window.workspace_viewport)
            for _ in range(24):
                before = self.application.focusWidget()
                if before is table:
                    break
                QTest.keyClick(before, Qt.Key.Key_Tab)
                self.application.processEvents()
                after = self.application.focusWidget()
                path.append((type(before).__name__, before.objectName(),
                             type(after).__name__, after.objectName()))
            self.assertIs(self.application.focusWidget(), table)
            with patch.object(self.service, "get_ticket_details",
                              wraps=self.service.get_ticket_details) as details:
                QTest.keyClick(table, Qt.Key.Key_Return)
                self.wait_idle()
                details.assert_called_once_with(self.service.ticket.ticket_id)
            self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
            self.assertTrue(table.currentIndex().isValid())
        except AssertionError:
            self.fail(f"Ticket Enter path: {path!r}")

    def test_tab_skips_unavailable_modules(self):
        window = MainWindow(self.service)
        try:
            window.show()
            self.application.processEvents()
            deadline = time.monotonic() + 5
            while window.runner.busy and time.monotonic() < deadline:
                QTest.qWait(5)
            self.assertFalse(window.runner.busy)
            self.assertFalse(window.navigation_buttons["knowledge"].isEnabled())
            self.assertFalse(window.navigation_buttons["scripts"].isEnabled())
            window.workspace_viewport.setFocus()
            self.application.processEvents()
            for key in ("tickets", "clipboard"):
                QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
                self.application.processEvents()
                self.assertIs(self.application.focusWidget(), window.navigation_buttons[key])
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Backtab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), window.navigation_buttons["tickets"])
        finally:
            window.close()
            window.deleteLater()
            self.window.activateWindow()
            self.application.processEvents()

    def test_tab_traversal_after_lazy_clipboard_creation(self):
        self.activate("clipboard")
        self.assertIsNotNone(self.window.clipboard_workspace)
        self.window.workspace_viewport.setFocus()
        self.application.processEvents()
        keys = ("tickets", "knowledge", "scripts", "clipboard")
        for key in keys:
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])
        QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
        self.application.processEvents()
        focus = self.application.focusWidget()
        self.assertIsNotNone(focus)
        self.assertTrue(self.window.clipboard_workspace.isAncestorOf(focus))
        self.assertTrue(focus.isVisible() and focus.isEnabled())
        for key in reversed(keys):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Backtab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])

    def test_keyboard_route_restores_focus_after_pending_scripts_refresh(self):
        self.scripts.gate = threading.Event()
        for key in ("tickets", "knowledge", "scripts"):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])
        button = self.window.navigation_buttons["scripts"]
        QTest.keyClick(button, Qt.Key.Key_Space)
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.assertTrue(self.window.runner.busy)
        self.assertFalse(button.isEnabled())
        self.scripts.gate.set()
        self.wait_idle()
        self.application.processEvents()
        self.assertIs(self.application.focusWidget(), button)

    def test_deliberate_focus_choice_wins_over_pending_rail_restore(self):
        self.scripts.gate = threading.Event()
        for _ in range(3):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
        QTest.keyClick(self.window.navigation_buttons["scripts"], Qt.Key.Key_Space)
        self.assertTrue(self.window.runner.busy)
        chosen = self.window.menuBar()
        chosen.setFocus()
        self.application.processEvents()
        self.scripts.gate.set()
        self.wait_idle()
        self.application.processEvents()
        self.assertIs(self.application.focusWidget(), chosen)

    def activate(self, key, keyboard=False):
        button = self.window.navigation_buttons[key]
        if keyboard:
            button.setFocus(Qt.FocusReason.TabFocusReason)
            QTest.keyClick(button, Qt.Key.Key_Space)
        else:
            QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        if self.application.platformName() == "offscreen":
            # Offscreen does not reactivate the owner after a real modal closes.
            self.window.activateWindow()
            self.application.processEvents()

    def test_four_accessible_icon_controls_reuse_actions_and_start_on_tickets(self):
        self.assertEqual(self.window.navigation_rail.width(), 52)
        self.assertEqual(len(self.window.navigation_rail.findChildren(QToolButton)), 4)
        self.assertIsNone(self.window.clipboard_workspace)
        for key, label in (("tickets", "Tickets"), ("knowledge", "Knowledge Base"),
                           ("scripts", "Scripts"), ("clipboard", "Clipboard Center")):
            button = self.window.navigation_buttons[key]
            action = getattr(self.window, key + "_action")
            self.assertIs(button.defaultAction(), action)
            self.assertEqual(button.objectName(), key + "NavigationButton")
            self.assertEqual(button.accessibleName(), label)
            self.assertEqual(button.toolTip(), label)
            self.assertEqual(button.focusPolicy(), Qt.FocusPolicy.TabFocus)
            self.assertEqual(button.toolButtonStyle(), Qt.ToolButtonStyle.ToolButtonIconOnly)
            self.assertFalse(button.icon().isNull())
            self.assertFalse(action.isCheckable())
        self.active("tickets")
        self.assertEqual(self.window.navigation_buttons["tickets"].accessibleDescription(),
                         "Current workspace")

    def test_mouse_and_keyboard_reach_all_retained_workspaces(self):
        for keyboard in (False, True):
            for key in ("knowledge", "scripts", "clipboard", "tickets"):
                self.activate(key, keyboard)
                self.active(key)
                page = {"tickets": self.window.workspace, "knowledge": self.window.knowledge_workspace,
                        "scripts": self.window.script_workspace, "clipboard": self.window.clipboard_workspace}[key]
                self.assertIs(self.window.pages.currentWidget(), page)
                self.assertFalse(self.window.navigation_buttons[key].icon().isNull())
        count = self.window.pages.count()
        clipboard = self.window.clipboard_workspace
        for _ in range(3):
            self.activate("clipboard")
            self.assertIs(self.window.clipboard_workspace, clipboard)
            self.assertEqual(self.window.pages.count(), count)
        clipboard.back_button.click()
        self.wait_idle()
        self.active("tickets")

    def test_menu_toolbar_new_ticket_and_article_routes_sync_actual_page(self):
        toolbar = self.window.findChildren(QToolBar)[0]
        QTest.mouseClick(toolbar.widgetForAction(self.window.scripts_action), Qt.MouseButton.LeftButton)
        self.wait_idle()
        self.active("scripts")
        menu = self.window.menuBar().actions()[0].menu()
        menu.popup(self.window.mapToGlobal(self.window.rect().topLeft()))
        self.application.processEvents()
        QTest.mouseClick(menu, Qt.MouseButton.LeftButton,
                         pos=menu.actionGeometry(self.window.knowledge_action).center())
        self.wait_idle()
        self.active("knowledge")
        self.window.show_new_ticket()
        self.active("tickets")
        self.window.ticket_create_widget.reset_form()
        self.window.open_knowledge_article(999)
        self.wait_idle()
        self.active("knowledge")

    def cancel_dialog(self):
        dialogs = []
        def cancel():
            dialog = QApplication.activeModalWidget()
            if isinstance(dialog, QMessageBox):
                dialogs.append(dialog.windowTitle())
                QTest.mouseClick(dialog.button(QMessageBox.StandardButton.Cancel), Qt.MouseButton.LeftButton)
        QTimer.singleShot(0, cancel)
        return dialogs

    def test_real_modal_cancel_preserves_note_selection_page_and_editor_focus(self):
        workspace = self.window.workspace
        workspace._activate_row(workspace.model.index(0, 0))
        self.wait_idle()
        editor = workspace.note_input
        for keyboard in (False, True):
            editor.setPlainText("Keep this unsaved note")
            cursor = editor.textCursor()
            cursor.setPosition(5)
            cursor.setPosition(9, cursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
            editor.setFocus()
            self.application.processEvents()
            dialogs = self.cancel_dialog()
            self.activate("knowledge", keyboard)
            self.assertEqual(len(dialogs), 1)
            self.assertIs(self.window.pages.currentWidget(), workspace)
            self.assertEqual(editor.toPlainText(), "Keep this unsaved note")
            self.assertEqual(editor.textCursor().selectedText(), "this")
            self.assertTrue(editor.hasFocus())
            self.active("tickets")
            # Restoration is synchronous: a later intentional focus choice wins.
            workspace.subject_search_input.setFocus()
            QTest.qWait(5)
            self.assertTrue(workspace.subject_search_input.hasFocus())

    def test_clipboard_setup_cancel_and_pending_refusal_preserve_focus_and_draft(self):
        from Tests.GUI.test_clipboard_setup import wait_idle
        from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED
        self.activate("clipboard")
        clipboard = self.window.clipboard_workspace
        self.assertTrue(clipboard.show_setup())
        wait_idle(self.application, lambda: clipboard.settings_pending or clipboard.loading)
        checkbox = clipboard.setup.checkboxes[WORKFLOW_ENABLED]
        for keyboard in (False, True):
            checkbox.setChecked(True)
            checkbox.setFocus()
            dialogs = self.cancel_dialog()
            self.activate("scripts", keyboard)
            self.assertEqual(dialogs, ["Unsaved Clipboard preferences"])
            self.assertTrue(clipboard.setup.dirty)
            self.assertTrue(checkbox.isChecked())
            self.assertTrue(checkbox.hasFocus())
            self.active("clipboard")
        for keyboard in (False, True):
            checkbox.setFocus()
            with patch.object(clipboard.setup, "_pending", True):
                self.activate("tickets", keyboard)
                self.active("clipboard")
                self.assertTrue(checkbox.hasFocus())
                self.assertFalse(self.window.close())
        self.assertEqual(self.settings.calls, [])
        clipboard.setup.cancel()

    def test_optional_modules_disabled_and_busy_callback_gaps_cannot_route(self):
        unavailable = MainWindow(self.service)
        self.addCleanup(unavailable.deleteLater)
        for key in ("knowledge", "scripts"):
            button = unavailable.navigation_buttons[key]
            self.assertFalse(button.isEnabled())
            button.click()
            self.assertIs(unavailable.pages.currentWidget(), unavailable.workspace)
        self.assertTrue(unavailable.close())
        for owner, field, value in (
            (self.window.workspace, "_note_pending", True),
            (self.window.workspace, "_creation_pending", True),
            (self.window.workspace, "status_pending", True),
            (self.window.workspace, "classification_pending", True),
            (self.window.script_workspace, "_run_identity", object()),
        ):
            with self.subTest(field=field), patch.object(owner, field, value):
                self.window._set_busy(False)
                for key, button in self.window.navigation_buttons.items():
                    self.assertFalse(button.isEnabled())
                    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                    self.active("tickets")
                self.assertIsNone(self.window.clipboard_workspace)
            self.window._set_busy(False)
        self.scripts.gate = threading.Event()
        QTest.mouseClick(self.window.navigation_buttons["scripts"], Qt.MouseButton.LeftButton)
        self.assertTrue(self.window.runner.busy)
        QTest.mouseClick(self.window.navigation_buttons["clipboard"], Qt.MouseButton.LeftButton)
        self.assertIsNone(self.window.clipboard_workspace)
        self.active("scripts")
        self.scripts.gate.set()
        self.wait_idle()
        self.activate("clipboard")
        self.active("clipboard")

    def test_compact_standard_desktop_keep_rail_visible_and_workspace_reachable(self):
        for width, height in ((660, 592), (1000, 700), (1180, 850)):
            self.window.resize(width, height)
            self.application.processEvents()
            self.assertEqual(self.window.size().toTuple(), (width, height))
            for key in ("knowledge", "scripts", "clipboard", "tickets"):
                self.activate(key)
                self.active(key)
                for button in self.window.navigation_buttons.values():
                    self.assertTrue(button.isVisible())
                    self.assertTrue(self.window.navigation_rail.rect().contains(button.geometry()))
                scroll = self.window.workspace_viewport
                page = self.window.pages.currentWidget()
                for corner in (page.rect().topLeft(), page.rect().bottomRight()):
                    point = page.mapTo(self.window.pages, corner)
                    scroll.ensureVisible(point.x(), point.y(), 1, 1)
                    self.application.processEvents()
                    self.assertTrue(scroll.viewport().rect().contains(page.mapTo(scroll.viewport(), corner)))

    def test_creation_draft_survives_rail_routes_and_exit_cancel(self):
        from Tests.GUI.test_clipboard_setup import wait_idle
        self.window.show_new_ticket()
        self.window.ticket_create_widget.subject_input.setText("Keep creation draft")
        self.activate("clipboard")
        wait_idle(self.application, lambda: self.window.clipboard_workspace.loading)
        dialogs = self.cancel_dialog()
        self.window.exit_action.trigger()
        self.assertEqual(dialogs, ["Unsaved new ticket"])
        self.assertTrue(self.window.isVisible())
        self.active("clipboard")
        self.activate("tickets")
        self.assertTrue(self.window.workspace.creating)
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), "Keep creation draft")
        self.assertEqual(self.service.calls, 0)

    def test_classification_cancel_through_rail_preserves_unsaved_value_and_focus(self):
        workspace = self.window.workspace
        workspace.open_ticket(1)
        self.wait_idle()
        combo = workspace.priority_input
        combo.setCurrentIndex(combo.findData("HIGH"))
        combo.setFocus()
        dialogs = self.cancel_dialog()
        self.activate("scripts", keyboard=True)
        self.assertEqual(dialogs, ["Unsaved ticket activity"])
        self.assertEqual(combo.currentData(), "HIGH")
        self.assertTrue(combo.hasFocus())
        self.active("tickets")

    def scroll_values(self):
        scroll = self.window.workspace_viewport
        return (scroll.horizontalScrollBar().value(), scroll.verticalScrollBar().value())

    def scroll_source(self):
        scroll = self.window.workspace_viewport
        scroll.horizontalScrollBar().setValue(scroll.horizontalScrollBar().maximum())
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
        return self.scroll_values()

    def assert_origin(self, key):
        QTest.qWait(10)  # Include deferred Qt layout after the accepted route.
        self.active(key)
        self.assertEqual(self.scroll_values(), (0, 0))
        page = self.window.pages.currentWidget()
        viewport = self.window.workspace_viewport.viewport()
        heading = next(label for label in page.findChildren(QLabel)
                       if label.text() == {"tickets": "Tickets", "knowledge": "Knowledge Base",
                                          "scripts": "Scripts", "clipboard": "Clipboard Center"}[key])
        self.assertTrue(viewport.rect().contains(heading.mapTo(viewport, heading.rect().topLeft())))
        self.assertTrue(viewport.rect().contains(heading.mapTo(
            viewport, QPoint(heading.fontMetrics().horizontalAdvance(heading.text()) - 1,
                             heading.fontMetrics().height() - 1))))
        primary = {"tickets": self.window.workspace.subject_search_input,
                   "knowledge": self.window.knowledge_workspace.search_input,
                   "scripts": self.window.script_workspace.search_input,
                   "clipboard": (self.window.clipboard_workspace.refresh_button
                                 if self.window.clipboard_workspace is not None else None)}[key]
        self.assertTrue(primary.isVisible())
        self.assertTrue(viewport.rect().contains(primary.mapTo(viewport, primary.rect().topLeft())))

    def test_scrolled_sources_reset_on_rail_and_clipboard_return_at_three_sizes(self):
        for size in ((660, 592), (1000, 700), (1180, 850)):
            with self.subTest(size=size):
                self.window.resize(*size)
                QTest.qWait(10)
                self.activate("tickets")
                for key in ("knowledge", "scripts", "clipboard"):
                    before = self.scroll_source()
                    if size == (660, 592):
                        self.assertGreater(before[0], 0)
                        self.assertGreater(before[1], 0)
                    self.activate(key)
                    self.assert_origin(key)
                self.scroll_source()
                QTest.mouseClick(self.window.clipboard_workspace.back_button, Qt.MouseButton.LeftButton)
                self.wait_idle()
                self.assert_origin("tickets")

    def test_scrolled_sources_reset_on_menu_and_toolbar_routes(self):
        self.window.resize(660, 592)
        QTest.qWait(10)
        self.scroll_source()
        menu = self.window.menuBar().actions()[0].menu()
        menu.popup(self.window.mapToGlobal(self.window.rect().topLeft()))
        self.application.processEvents()
        QTest.mouseClick(menu, Qt.MouseButton.LeftButton,
                         pos=menu.actionGeometry(self.window.knowledge_action).center())
        self.wait_idle()
        self.assert_origin("knowledge")
        self.scroll_source()
        toolbar = self.window.findChildren(QToolBar)[0]
        QTest.mouseClick(toolbar.widgetForAction(self.window.scripts_action), Qt.MouseButton.LeftButton)
        self.wait_idle()
        self.assert_origin("scripts")

    def test_ticket_cancel_keeps_both_scrollbars_selection_and_visible_editor_focus(self):
        self.window.resize(660, 592)
        workspace = self.window.workspace
        workspace.open_ticket(1)
        self.wait_idle()
        editor = workspace.note_input
        for keyboard in (False, True):
            editor.setPlainText("Keep this unsaved note")
            cursor = editor.textCursor()
            cursor.setPosition(5)
            cursor.setPosition(9, cursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
            editor.setFocus()
            QTest.qWait(10)
            self.scroll_source()
            scroll = self.window.workspace_viewport
            # Keep the selection visible even when the editor is wider than the
            # offscreen viewport; overflowing control edges need not fit at once.
            scroll.horizontalScrollBar().setValue(min(
                scroll.horizontalScrollBar().maximum(),
                editor.mapTo(self.window.pages, QPoint()).x() - 4))
            before = self.scroll_values()
            self.assertGreater(before[0], 0)
            self.assertGreater(before[1], 0)
            dialogs = self.cancel_dialog()
            with patch.object(self.service, "list_tickets", wraps=self.service.list_tickets) as refresh:
                self.activate("knowledge", keyboard)
                refresh.assert_not_called()
            self.assertEqual(dialogs, ["Unsaved ticket activity"])
            self.assertEqual(self.scroll_values(), before)
            self.assertIs(self.window.pages.currentWidget(), workspace)
            self.assertEqual(editor.toPlainText(), "Keep this unsaved note")
            self.assertEqual(editor.textCursor().selectedText(), "this")
            self.assertTrue(editor.hasFocus())
            viewport = self.window.workspace_viewport.viewport()
            for position in (editor.textCursor().anchor(), editor.textCursor().position()):
                endpoint = editor.textCursor()
                endpoint.setPosition(position)
                self.assertTrue(viewport.rect().contains(editor.viewport().mapTo(
                    viewport, editor.cursorRect(endpoint).center())))
            self.active("tickets")

    def test_setup_cancel_and_pending_refusal_keep_both_scrollbars_and_draft(self):
        from Tests.GUI.test_clipboard_setup import wait_idle
        from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED
        self.window.resize(660, 592)
        self.activate("clipboard")
        clipboard = self.window.clipboard_workspace
        self.assertTrue(clipboard.show_setup())
        wait_idle(self.application, lambda: clipboard.loading or clipboard.settings_pending)
        checkbox = clipboard.setup.checkboxes[WORKFLOW_ENABLED]
        checkbox.setChecked(True)
        for keyboard in (False, True):
            checkbox.setFocus()
            scroll = self.window.workspace_viewport
            scroll.horizontalScrollBar().setValue(10)
            scroll.verticalScrollBar().setValue(60)
            before = self.scroll_values()
            self.assertEqual(before, (10, 60))
            dialogs = self.cancel_dialog()
            self.activate("scripts", keyboard)
            self.assertEqual(dialogs, ["Unsaved Clipboard preferences"])
            self.assertEqual(self.scroll_values(), before)
            self.assertTrue(checkbox.hasFocus())
            self.assertTrue(checkbox.isChecked() and clipboard.setup.dirty)
            self.active("clipboard")
            with patch.object(clipboard.setup, "_pending", True):
                self.activate("tickets", keyboard)
                self.assertEqual(self.scroll_values(), before)
                self.assertTrue(checkbox.hasFocus())
                self.active("clipboard")
        self.assertEqual(self.settings.calls, [])

    def test_busy_and_hidden_pending_owners_do_not_reset_scroll(self):
        self.window.resize(660, 592)
        QTest.qWait(10)
        for owner, field in ((self.window.runner, "_task"),
                             (self.window.workspace, "_note_pending"),
                             (self.window.script_workspace, "_run_identity")):
            before = self.scroll_source()
            with patch.object(owner, field, True):
                self.window._set_busy(False)
                QTest.mouseClick(self.window.navigation_buttons["knowledge"], Qt.MouseButton.LeftButton)
                self.assertEqual(self.scroll_values(), before)
                self.active("tickets")
            self.window._set_busy(False)

    def test_same_page_activation_preserves_existing_scroll(self):
        self.window.resize(660, 592)
        QTest.qWait(10)
        for key in ("tickets", "knowledge", "scripts", "clipboard"):
            self.activate(key)
            before = self.scroll_source()
            self.activate(key)
            QTest.qWait(10)
            self.assertEqual(self.scroll_values(), before, key)
            self.active(key)

    def test_rapid_accepted_routes_and_later_scroll_have_no_stale_reset(self):
        self.window.resize(660, 592)
        self.activate("clipboard")  # Retain the lazy page before the rapid sequence.
        from Tests.GUI.test_clipboard_setup import wait_idle
        wait_idle(self.application, lambda: self.window.clipboard_workspace.loading)
        self.scroll_source()
        with patch.object(self.window.knowledge_workspace, "refresh_list", return_value=True), \
                patch.object(self.window.script_workspace, "refresh_list", return_value=True):
            QTest.mouseClick(self.window.navigation_buttons["knowledge"], Qt.MouseButton.LeftButton)
            QTest.mouseClick(self.window.navigation_buttons["scripts"], Qt.MouseButton.LeftButton)
        self.assert_origin("scripts")
        later = self.scroll_source()
        QTest.qWait(20)
        self.assertEqual(self.scroll_values(), later)
        self.active("scripts")


class ScriptsFocusLifecycleTests(unittest.TestCase):
    """Keyboard navigation through real runner callbacks and Qt focus events."""

    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])
    setUp = NavigationRailTests.setUp
    tearDown = NavigationRailTests.tearDown
    wait_idle = MainWindowTests.wait_idle

    def record(self, stage):
        focus = self.application.focusWidget()
        record = {"stage": stage, "focus_class": type(focus).__name__,
                  "focus_name": focus.objectName() if focus else None,
                  "busy": self.window.runner.busy,
                  "loading": self.window.script_workspace._loading,
                  "active": self.application.activeWindow() is self.window,
                  "scripts_page": self.window.pages.currentWidget() is self.window.script_workspace}
        print(f"focus evidence: {record!r}", flush=True)
        return focus

    def start_scripts(self):
        self.scripts.gate = threading.Event()
        self.assertIs(self.application.activeWindow(), self.window)
        for key in ("tickets", "knowledge", "scripts"):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.record("Tab to " + key)
            self.assertIs(self.application.focusWidget(), self.window.navigation_buttons[key])
        self.actions = []
        self.window.scripts_action.triggered.connect(lambda: self.actions.append("scripts"))
        QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Space)
        self.record("Space / pending")
        self.assertEqual(self.actions, ["scripts"])
        self.assertTrue(self.window.runner.busy)

    def finish_scripts(self):
        self.scripts.gate.set()
        self.wait_idle()
        self.application.processEvents()
        self.record("completion settled")

    def test_normal_completion_restores_scripts(self):
        self.start_scripts()
        self.finish_scripts()
        focus = self.record("normal result")
        self.assertIs(focus, self.window.navigation_buttons["scripts"])
        self.assertTrue(focus.isEnabled() and focus.isVisible())

    def test_toolbar_follows_visual_order_from_rail_and_in_reverse(self):
        self.start_scripts()
        self.finish_scripts()
        page = self.window.script_workspace
        header = (page.run_button, page.copy_button, page.manage_button, page.refresh_button)
        positions = [control.mapTo(self.window, QPoint()).x() for control in header]
        self.assertEqual(positions, sorted(positions))
        self.assertFalse(page.run_button.isEnabled())
        self.assertFalse(page.copy_button.isEnabled())
        scripts = self.window.navigation_buttons["scripts"]
        self.assertIs(self.record("restored Scripts before toolbar traversal"), scripts)
        focused_image = scripts.grab().toImage()
        forward = (self.window.navigation_buttons["clipboard"], page.manage_button,
                   page.refresh_button, page.search_input, page.search_button,
                   page.clear_search_button)
        for target in forward:
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.assertIs(self.record("forward toolbar/search traversal"), target)
            self.assertTrue(target.isEnabled() and target.isVisible())
        # Compare the restored focus border with the same selected button after
        # traversal; the selected-module marker alone must not satisfy this check.
        selected_image = scripts.grab().toImage()
        edge_changes = sum(focused_image.pixelColor(x, y) != selected_image.pixelColor(x, y)
                           for x in range(focused_image.width())
                           for y in range(focused_image.height())
                           if y < 3 or y >= focused_image.height() - 3
                           or x >= focused_image.width() - 3)
        print(f"restored Scripts focus edge changes: {edge_changes}", flush=True)
        self.assertGreaterEqual(edge_changes, 20)
        for target in (*reversed(forward[:-1]), scripts):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Backtab)
            self.application.processEvents()
            self.assertIs(self.record("reverse toolbar/search traversal"), target)

    def test_toolbar_refresh_preserves_later_deliberate_focus(self):
        self.start_scripts()
        self.finish_scripts()
        page = self.window.script_workspace
        for target in (self.window.navigation_buttons["clipboard"],
                       page.manage_button, page.refresh_button):
            QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
            self.application.processEvents()
            self.assertIs(self.record("route to Refresh"), target)
        self.scripts.gate = threading.Event()
        calls = self.scripts.calls
        QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Space)
        self.record("toolbar Refresh pending")
        self.assertTrue(self.window.runner.busy)
        chosen = self.window.menuBar()
        chosen.setFocus(Qt.FocusReason.OtherFocusReason)
        self.application.processEvents()
        self.finish_scripts()
        self.assertIs(self.record("deliberate focus after toolbar Refresh"), chosen)
        self.assertEqual(self.scripts.calls, calls + 1)

    def test_automatic_clipboard_displacement_is_repaired_without_user_input(self):
        clipboard = self.window.navigation_buttons["clipboard"]
        loaded = self.window.script_workspace._loaded

        def complete(*args):
            loaded(*args)
            # Boundary fixture: the same TabFocusReason Qt emits automatically
            # when Scripts is disabled. No key or mouse event accompanies it.
            clipboard.setFocus(Qt.FocusReason.TabFocusReason)
            self.record("automatic Clipboard displacement in callback")

        with patch.object(self.window.script_workspace, "_loaded", side_effect=complete):
            self.start_scripts()
            self.finish_scripts()
        self.assertIs(self.record("automatic displacement result"),
                      self.window.navigation_buttons["scripts"])
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)

    def test_deliberate_tab_to_clipboard_wins(self):
        clipboard = self.window.navigation_buttons["clipboard"]
        loaded = self.window.script_workspace._loaded

        def complete(*args):
            loaded(*args)
            # Controls have been reenabled; the callback is still completing.
            for _ in range(24):
                if self.application.focusWidget() is clipboard:
                    break
                QTest.keyClick(self.application.focusWidget(), Qt.Key.Key_Tab)
                self.application.processEvents()
                self.record("deliberate Tab during completion")
            self.assertIs(self.application.focusWidget(), clipboard)

        with patch.object(self.window.script_workspace, "_loaded", side_effect=complete):
            self.start_scripts()
            self.finish_scripts()
        self.assertIs(self.record("deliberate Tab result"), clipboard)
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)

    def test_deactivation_cancels_obsolete_restore_without_reactivation(self):
        from PySide6.QtWidgets import QWidget
        other = QWidget()
        other.setObjectName("syntheticFocusDestination")
        try:
            self.start_scripts()
            other.show()
            other.activateWindow()
            self.application.processEvents()
            self.assertIs(self.application.activeWindow(), other)
            self.finish_scripts()
            self.assertIs(self.application.activeWindow(), other)
            self.assertIsNone(self.window._rail_pending_focus)
        finally:
            other.close()
            other.deleteLater()
            self.window.activateWindow()
            self.application.processEvents()

    def test_reentrant_completion_waits_for_outer_callback(self):
        loaded = self.window.script_workspace._loaded
        inside = []
        nested = []

        def complete(*args):
            self.application.processEvents()
            inside.append(self.record("inside callback after nested event dispatch"))
            self.assertTrue(self.window.runner.submit(lambda: None,
                            lambda _: nested.append("finished"), self.fail))
            deadline = time.monotonic() + 5
            while not nested and time.monotonic() < deadline:
                QTest.qWait(5)
            self.assertEqual(nested, ["finished"])
            inside.append(self.record("after reentrant task / outer callback pending"))
            loaded(*args)

        with patch.object(self.window.script_workspace, "_loaded", side_effect=complete):
            self.start_scripts()
            self.finish_scripts()
        self.assertNotIn(self.window.navigation_buttons["scripts"], inside)
        self.assertIs(self.record("reentrant result"), self.window.navigation_buttons["scripts"])


class NavigationRenderingTests(unittest.TestCase):
    """Measure actual button glyphs and focus edges across paired palette roles."""

    setUpClass = classmethod(MainWindowTests.setUpClass.__func__)
    setUp = MainWindowTests.setUp
    tearDown = MainWindowTests.tearDown
    wait_idle = MainWindowTests.wait_idle

    @staticmethod
    def contrast(first, second):
        def luminance(color):
            channels = (color.redF(), color.greenF(), color.blueF())
            return sum(weight * (value / 12.92 if value <= .04045 else
                                ((value + .055) / 1.055) ** 2.4)
                       for value, weight in zip(channels, (.2126, .7152, .0722)))
        low, high = sorted((luminance(first), luminance(second)))
        return (high + .05) / (low + .05)

    def palettes(self, original):
        yield "original", original
        for name, values in (
            ("split-role", ("#000000", "#ffffff", "#ffffff", "#000000", "#ffffff", "#000000")),
            ("yellow-magenta", ("#000000", "#ffff00", "#008800", "#ffff00", "#ff00ff", "#000000")),
            ("navy-white", ("#ffffff", "#000080", "#dddddd", "#000080", "#0000aa", "#ffffff")),
        ):
            palette = QPalette(original)
            for role, color in zip((QPalette.ColorRole.Window, QPalette.ColorRole.WindowText,
                                    QPalette.ColorRole.Button, QPalette.ColorRole.ButtonText,
                                    QPalette.ColorRole.Highlight, QPalette.ColorRole.HighlightedText), values):
                palette.setColor(role, QColor(color))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#777777"))
            yield name, palette

    def hover(self, button, enabled):
        # QTest delivers real Qt Enter/Leave on native and offscreen platforms.
        # Move away first: a stationary OS cursor need not generate another Enter.
        QTest.mouseMove(self.window, QPoint(500, 20))
        QTest.qWait(20)
        if enabled:
            QTest.mouseMove(button, QPoint(12, 12))
            QTest.qWait(20)
        if button.underMouse() != enabled:
            # Deterministic Qt event injection for a noninteractive native desktop.
            QApplication.sendEvent(button, QEvent(QEvent.Type.Enter if enabled else QEvent.Type.Leave))
            self.application.processEvents()
        self.assertEqual(button.underMouse(), enabled)

    def capture(self, name, button, minimum_pixels=60):
        self.application.processEvents()
        # Capture through the parent so transparent normal/disabled controls
        # include the actual rail fill rather than transparent black pixels.
        window_image = self.window.grab().toImage()
        dpr = window_image.devicePixelRatio()
        origin = button.mapTo(self.window, QPoint(0, 0))
        image = window_image.copy(round(origin.x()*dpr), round(origin.y()*dpr),
                                  round(button.width()*dpr), round(button.height()*dpr))
        # Use a whole clear strip to establish the rendered fill, and a full
        # glyph region to include antialiased strokes at every supported DPR.
        backgrounds = Counter(image.pixelColor(x, y).rgba()
                              for y in range(round(10*dpr), round(34*dpr))
                              for x in range(round(35*dpr), round(39*dpr)))
        background = QColor.fromRgba(backgrounds.most_common(1)[0][0])
        visible = sum(self.contrast(image.pixelColor(x, y), background) >= 3
                      for y in range(round(10*dpr), round(34*dpr))
                      for x in range(round(10*dpr), round(34*dpr)))
        metrics = dict(name=name, background=background.name(), glyph_pixels=visible, dpr=dpr)
        self.assertGreaterEqual(visible, minimum_pixels*dpr*dpr, metrics)
        return image, background, metrics

    def marker_coverage(self, image):
        """Count straight-edge rows whose full marker contrasts with selected fill."""
        dpr = image.devicePixelRatio()
        width = round(2*dpr)
        rows = range(round(10*dpr), round(34*dpr))
        return sum(all(self.contrast(image.pixelColor(x, y),
                                     image.pixelColor(round(6*dpr), y)) >= 3
                       for x in range(width)) for y in rows)

    def test_rendered_focus_is_distinct_from_selection_with_and_without_hover(self):
        original = QPalette(self.application.palette())
        try:
            self.window.activateWindow()
            self.application.processEvents()
            for name, palette in self.palettes(original):
                self.application.setPalette(palette)
                self.application.processEvents()
                for key in ("tickets", "clipboard"):
                    button = self.window.navigation_buttons[key]
                    for hovered in (False, True):
                        with self.subTest(palette=name, key=key, hover=hovered):
                            self.hover(button, hovered)
                            button.clearFocus()
                            before, background, _ = self.capture(f"{name}-{key}-{hovered}-unfocused", button)
                            button.setFocus(Qt.FocusReason.TabFocusReason)
                            self.application.processEvents()
                            self.assertTrue(button.hasFocus())
                            after, _, _ = self.capture(f"{name}-{key}-{hovered}-focused", button)
                            dpr = after.devicePixelRatio()
                            # Three perimeter bands exclude the solid left selection
                            # marker. Focus must add visible pixels elsewhere.
                            edge = [(x, y) for y in range(after.height()) for x in range(after.width())
                                    if ((6*dpr <= x < 38*dpr and (y < 3*dpr or y >= 41*dpr))
                                        or (x >= 41*dpr and 6*dpr <= y < 38*dpr))]
                            visible_changes = sum(before.pixelColor(x, y) != after.pixelColor(x, y)
                                                  and self.contrast(after.pixelColor(x, y), background) >= 3
                                                  for x, y in edge)
                            self.assertGreaterEqual(visible_changes, 40*dpr*dpr,
                                                    (name, key, hovered, visible_changes))
                            # The solid selection marker survives while focus adds
                            # a distinct dashed indicator on the other three sides.
                            if key == "tickets":
                                marker = sum(self.contrast(after.pixelColor(x, y), background) >= 3
                                             for x in range(round(2*dpr))
                                             for y in range(round(8*dpr), round(36*dpr)))
                                self.assertGreaterEqual(marker, 40*dpr*dpr)
                            button.clearFocus()
        finally:
            self.application.setPalette(original)
            self.application.processEvents()

    def test_rendered_active_disabled_marker_survives_in_contrasting_palettes(self):
        original = QPalette(self.application.palette())
        try:
            # The inherited application palette can vary with suite order and
            # platform; the three explicit palettes define this contrast case.
            for name, palette in tuple(self.palettes(original))[1:]:
                with self.subTest(palette=name):
                    self.application.setPalette(palette)
                    self.application.processEvents()
                    selected = self.window.navigation_buttons["tickets"]
                    inactive = self.window.navigation_buttons["scripts"]
                    selected.setEnabled(False)
                    inactive.setEnabled(False)
                    self.application.processEvents()
                    active_image, _, _ = self.capture(name + "-active-disabled", selected)
                    inactive_image, _, _ = self.capture(name + "-inactive-disabled", inactive,
                                                         minimum_pixels=32)
                    dpr = active_image.devicePixelRatio()
                    marker_rows = self.marker_coverage(active_image)
                    hidden = active_image.copy()
                    for y in range(round(10*dpr), round(34*dpr)):
                        fill_color = active_image.pixelColor(round(6*dpr), y)
                        for x in range(round(2*dpr)):
                            hidden.setPixelColor(x, y, fill_color)
                    hidden_rows = self.marker_coverage(hidden)
                    fill = sum(active_image.pixelColor(x, y) != inactive_image.pixelColor(x, y)
                               for x in range(round(35*dpr), round(39*dpr))
                               for y in range(round(10*dpr), round(34*dpr)))
                    print(f"marker {name}: {marker_rows}/{round(24*dpr)} rows, "
                          f"hidden control {hidden_rows}, fill {fill} pixels, DPR {dpr}")
                    self.assertGreaterEqual(marker_rows, round(18*dpr))
                    self.assertEqual(hidden_rows, 0)
                    self.assertGreaterEqual(fill, 60*dpr*dpr)
                    selected.setEnabled(True)
                    inactive.setEnabled(True)
        finally:
            self.application.setPalette(original)
            self.application.processEvents()

    def test_rendered_hover_disabled_icon_modes_and_runtime_palette_return(self):
        original = QPalette(self.application.palette())
        clipboard = self.window.navigation_buttons["clipboard"]
        tickets = self.window.navigation_buttons["tickets"]
        scripts = self.window.navigation_buttons["scripts"]
        try:
            self.hover(clipboard, False)
            clipboard.clearFocus()
            initial, _, _ = self.capture("original-before", clipboard)
            for name, palette in self.palettes(original):
                self.application.setPalette(palette)
                self.application.processEvents()
                for key in ("tickets", "clipboard"):
                    button = self.window.navigation_buttons[key]
                    for hovered in (False, True):
                        with self.subTest(palette=name, key=key, hover=hovered):
                            self.hover(button, hovered)
                            _, background, _ = self.capture(f"{name}-{key}-{hovered}-icon", button)
                            for mode in (QIcon.Mode.Normal, QIcon.Mode.Active, QIcon.Mode.Selected):
                                for state in (QIcon.State.Off, QIcon.State.On):
                                    image = button.icon().pixmap(24, 24, mode, state).toImage()
                                    visible = sum(image.pixelColor(x, y).alpha() >= 200
                                                  and self.contrast(image.pixelColor(x, y), background) >= 3
                                                  for y in range(image.height()) for x in range(image.width()))
                                    self.assertGreaterEqual(visible, 60, (name, key, hovered, mode, state))
                            # QAction icon refresh must retain the hovered/selected
                            # foreground rather than reverting to Normal artwork.
                            button.defaultAction().setIcon(tickets.icon())
                            self.capture(f"{name}-{key}-{hovered}-action-refresh", button)
                self.window.scripts_action.setEnabled(False)
                self.hover(scripts, False)
                # The Scripts chevrons are sparser than the rectangular icons.
                _, background, _ = self.capture(f"{name}-disabled", scripts, minimum_pixels=32)
                image = scripts.icon().pixmap(24, 24, QIcon.Mode.Disabled).toImage()
                self.assertGreaterEqual(sum(image.pixelColor(x, y).alpha() >= 200
                                            and self.contrast(image.pixelColor(x, y), background) >= 3
                                            for y in range(24) for x in range(24)), 32)
                self.window.scripts_action.setEnabled(True)
            self.application.setPalette(original)
            self.application.processEvents()
            self.hover(clipboard, False)
            clipboard.clearFocus()
            restored, _, _ = self.capture("original-restored", clipboard)
            self.assertEqual(initial, restored)
        finally:
            self.window.scripts_action.setEnabled(True)
            self.application.setPalette(original)
            self.application.processEvents()


if __name__ == "__main__":
    unittest.main()
