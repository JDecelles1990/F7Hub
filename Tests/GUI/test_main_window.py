from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import QTimer

from f7hub.gui.main_window import MainWindow
from f7hub.services.ticket_service import TicketService


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

    def list_scripts(self):
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

    def tearDown(self) -> None:
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

    def test_window_hosts_ticket_form_and_application_chrome(self) -> None:
        self.assertEqual(self.window.windowTitle(), "F7Hub")
        self.assertIs(self.window.centralWidget(), self.window.pages)
        self.assertIs(self.window.pages.currentWidget(), self.window.ticket_create_widget)
        self.assertEqual(self.window.statusBar().currentMessage(), "Ready")
        self.assertEqual(self.window.exit_action.objectName(), "exitAction")

    def test_created_ticket_updates_application_status(self) -> None:
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
        self.window.ticket_create_widget.subject_input.setText("Keep draft")
        self.window.ticket_create_widget.submit()
        self.wait_idle()
        form = self.window.ticket_create_widget
        self.assertEqual(form.subject_input.text(), "Keep draft")
        self.assertNotIn("Sensitive", form.form_error.text())
        self.assertTrue(form.save_button.isEnabled())
        self.assertIs(self.window.pages.currentWidget(), form)

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
        self.assertEqual(self.window.pages.indexOf(self.window.script_workspace), 2)
        self.window.scripts_action.trigger()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.script_workspace)
        self.assertEqual(self.window.script_workspace.heading.text(), "Scripts")
        self.assertEqual(self.scripts.calls, 1)
        self.window.show_new_ticket()
        self.assertIs(self.window.pages.currentWidget(), self.window.ticket_create_widget)

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

    def test_five_saved_ticket_detail_actions_fit_1000_by_700(self):
        self.window.show_tickets()
        self.wait_idle()
        self.window.resize(1000, 700)
        self.application.processEvents()
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        workspace = self.window.workspace
        for button in (workspace.edit_subject_button, workspace.edit_priority_button,
                       workspace.edit_type_button, workspace.edit_description_button,
                       workspace.reload_button):
            self.assertTrue(button.isVisible())

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


if __name__ == "__main__":
    unittest.main()
