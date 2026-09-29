"""Company context in Saved Tickets through real workers and isolated SQLite."""

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.gui.main_window import MainWindow
from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import TicketReadError, TicketService


class TicketCompanyContextFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "company-context.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repository = TicketRepository(self.path)
        self.service = TicketService(self.repository)
        self.stamp = "2026-09-04T00:00:00.000Z"
        with database_connection(self.path) as connection:
            self.a = connection.execute(
                "INSERT INTO companies (name, is_active, created_at, updated_at) VALUES (?, 1, ?, ?)",
                ("Northwind Support", self.stamp, self.stamp),
            ).lastrowid
            self.b = connection.execute(
                "INSERT INTO companies (name, is_active, created_at, updated_at) VALUES (?, 0, ?, ?)",
                ("Inactive Company", self.stamp, self.stamp),
            ).lastrowid
        self.first = self.make_ticket("COMPANY-A", self.a)
        self.second = self.make_ticket("COMPANY-B", self.b)
        self.none = self.make_ticket("NO-COMPANY", None)
        self.window = MainWindow(self.service)
        self.workspace = self.window.workspace
        self.window.show()
        self.workspace.open_ticket(self.first.ticket_id)
        self.wait_idle()

    def make_ticket(self, number, company_id):
        return self.repository.create_ticket(
            ticket_number=number, subject=f"Shared issue {number}", company_id=company_id,
            status="OPEN", priority="HIGH", ticket_type="INCIDENT",
            created_at=self.stamp, updated_at=self.stamp,
        )

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Service worker timed out")

    def tearDown(self):
        self.wait_idle()
        self.workspace._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.temp.cleanup()

    def test_company_tab_is_separate_bounded_and_leaves_main_queue_state_unchanged(self):
        for index in range(24):
            self.make_ticket(f"A-{index}", self.a)
        self.workspace.PAGE_SIZE = 1
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("OPEN"))
        self.wait_idle()
        self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("HIGH"))
        self.wait_idle()
        self.workspace.type_filter.setCurrentIndex(self.workspace.type_filter.findData("INCIDENT"))
        self.wait_idle()
        self.workspace.subject_search_input.setText("Shared")
        self.workspace.search_subjects()
        self.wait_idle()
        self.workspace.subject_search_input.setText("Unsubmitted draft")
        self.workspace.refresh_list(offset=1)
        self.wait_idle()
        state = (self.workspace.model.tickets, self.workspace._offset,
                 self.workspace.status_filter.currentData(),
                 self.workspace.priority_filter.currentData(),
                 self.workspace.type_filter.currentData(), self.workspace._subject_query,
                 self.workspace.subject_search_input.text())
        self.assertIsNot(self.workspace.company_model, self.workspace.model)
        self.assertIn("Northwind Support", self.workspace.company_heading.text())
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(len(self.workspace.company_model.tickets), 20)
        self.assertNotIn(self.first, self.workspace.company_model.tickets)
        self.assertNotIn(self.second, self.workspace.company_model.tickets)
        self.assertEqual(self.workspace.company_model.tickets[0].ticket_number, "A-23")
        self.assertEqual(state, (self.workspace.model.tickets, self.workspace._offset,
                                 self.workspace.status_filter.currentData(),
                                 self.workspace.priority_filter.currentData(),
                                 self.workspace.type_filter.currentData(), self.workspace._subject_query,
                                 self.workspace.subject_search_input.text()))
        newest = self.workspace.company_model.tickets[0]
        self.workspace.open_ticket(newest.ticket_id)
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertIn(newest, self.workspace.company_model.tickets)

    def test_switch_clears_old_company_rows_and_no_company_disables_loading(self):
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, (self.first,))
        self.workspace.open_ticket(self.second.ticket_id)
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.assertIn("Inactive Company", self.workspace.company_heading.text())
        self.assertTrue(self.workspace.company_load_button.isEnabled())
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, (self.second,))
        self.workspace.open_ticket(self.none.ticket_id)
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.assertIn("No company", self.workspace.company_heading.text())
        self.assertFalse(self.workspace.company_load_button.isEnabled())

    def test_failed_company_refresh_retains_only_same_context_and_retries(self):
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.workspace.note_input.setPlainText("Keep this draft")
        with patch.object(self.service, "list_tickets", side_effect=TicketReadError("private")):
            self.workspace.company_load_button.click()
            self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, (self.first,))
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep this draft")
        self.assertIn("retry", self.workspace.company_feedback.text())
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, (self.first,))
        self.workspace._clear_drafts()
        self.workspace.open_ticket(self.second.ticket_id)
        self.wait_idle()
        with patch.object(self.service, "list_tickets", side_effect=TicketReadError("private")):
            self.workspace.company_load_button.click()
            self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.assertIn("retry", self.workspace.company_feedback.text())
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets, (self.second,))

    def test_open_related_ticket_reuses_draft_confirmation_and_keeps_queue(self):
        related = self.make_ticket("RELATED-A", self.a)
        self.workspace.refresh_list(offset=0)
        self.wait_idle()
        main_rows = self.workspace.model.tickets
        self.workspace.company_load_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.company_model.tickets[0], related)
        self.workspace.note_input.setPlainText("Unsaved note")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.workspace.company_open_button.click()
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.first.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Unsaved note")
        self.assertEqual(self.workspace.company_model.tickets[0], related)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.workspace.company_open_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, related.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "")
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.assertEqual(self.workspace.model.tickets, main_rows)

    def test_busy_and_stale_completion_cannot_populate_another_company(self):
        started = threading.Event()
        release = threading.Event()
        calls = []
        original = self.service.list_tickets

        def delayed_read(**kwargs):
            calls.append(kwargs)
            started.set()
            if not release.wait(5):
                raise TimeoutError("Company read gate timed out")
            return original(**kwargs)

        try:
            with patch.object(self.service, "list_tickets", side_effect=delayed_read):
                self.workspace.company_load_button.click()
                self.assertTrue(started.wait(5))
                self.assertFalse(self.workspace.company_load_button.isEnabled())
                self.workspace.load_company_tickets()
                self.workspace._display_details(self.service.get_ticket_details(self.second.ticket_id))
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["company_id"], self.a)
        self.assertEqual(calls[0]["limit"], 20)
        self.assertEqual(calls[0]["offset"], 0)
        self.assertEqual(self.workspace.company_model.tickets, ())
        self.assertIn("Inactive Company", self.workspace.company_heading.text())
