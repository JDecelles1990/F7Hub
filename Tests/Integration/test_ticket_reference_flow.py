"""Real bootstrap, worker, service and SQLite reference-aware ticket flow."""

import os
from pathlib import Path
import tempfile
import time
import threading
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.services.ticket_service import TicketValidationError
from Tests.Database.test_ticket_references import seed_references


class TicketReferenceFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "reference-flow.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.a, self.b, self.empty, self.inactive, self.alice, self.bob, self.charlie = seed_references(self.path)
        self.context = bootstrap_application(database_path=self.path)
        self.window = self.context.main_window
        self.form = self.window.ticket_create_widget
        self.window.show()
        self.wait_idle()

    def wait_idle(self):
        self.app.processEvents()  # Includes the initial show-time reference load.
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Service worker timed out")

    def tearDown(self):
        self.wait_idle()
        self.form.reset_form()
        self.window.workspace._clear_drafts()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def select_company(self, company):
        self.form.company_input.setCurrentIndex(self.form.company_input.findData(company.company_id))
        self.wait_idle()

    def test_select_save_reopen_stores_ids_and_displays_names(self):
        self.assertEqual(self.form.company_input.count(), 4)
        self.assertEqual(self.form.company_input.findData(self.inactive.company_id), -1)
        self.select_company(self.a)
        self.assertEqual(self.form.contact_input.count(), 2)
        self.form.contact_input.setCurrentIndex(1)
        self.select_company(self.b)
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.form.contact_input.findData(self.alice.contact_id), -1)
        self.select_company(self.a)
        self.form.contact_input.setCurrentIndex(1)
        QTest.keyClicks(self.form.subject_input, "Reference flow")
        QTest.mouseClick(self.form.save_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        workspace = self.window.workspace
        ticket_id = workspace.details.ticket.ticket_id
        self.assertIs(self.window.pages.currentWidget(), workspace)
        with database_connection(self.path) as connection:
            row = connection.execute("SELECT company_id, contact_id FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
            self.assertEqual(tuple(row), (self.a.company_id, self.alice.contact_id))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.window.show_new_ticket()
        self.window.show_tickets()
        self.wait_idle()
        workspace.table.setCurrentIndex(workspace.model.index(0, 0))
        QTest.keyClick(workspace.table, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertIn("Company: Northwind Support Labs", workspace.summary.toPlainText())
        self.assertIn("Contact: Alice Example", workspace.summary.toPlainText())

    def test_mismatch_cannot_bypass_service_boundary(self):
        with self.assertRaises(TicketValidationError):
            self.context.ticket_service.create_ticket(subject="Mismatch", company_id=self.a.company_id,
                                                       contact_id=self.charlie.contact_id)
        self.assertEqual(self.context.ticket_service.list_tickets(), ())

    def test_empty_contacts_and_no_reference_tickets(self):
        self.select_company(self.empty)
        self.assertFalse(self.form.contact_input.isEnabled())
        self.assertIn("No active contacts", self.form.reference_feedback.text())
        self.form.subject_input.setText("Company only")
        self.form.save_button.click()
        self.wait_idle()
        self.assertIn("Company: Empty Test Company", self.window.workspace.summary.toPlainText())
        self.assertIn("Contact: Not selected", self.window.workspace.summary.toPlainText())
        self.window.show_new_ticket()
        self.form.subject_input.setText("Without references")
        self.form.save_button.click()
        self.wait_idle()
        self.assertIn("Company: Not selected", self.window.workspace.summary.toPlainText())
        self.assertIn("Contact: Not selected", self.window.workspace.summary.toPlainText())

    def test_background_query_failure_preserves_draft_and_recovers(self):
        self.form.subject_input.setText("Keep subject")
        self.form.description_input.setPlainText("Keep description")
        with patch.object(self.form._reference_service, "list_active_companies", side_effect=RuntimeError("private detail")):
            self.form.refresh_references_button.click()
            self.wait_idle()
        self.assertTrue(self.form.isEnabled())
        self.assertTrue(self.window.new_ticket_action.isEnabled())
        self.assertEqual(self.form.subject_input.text(), "Keep subject")
        self.assertEqual(self.form.description_input.toPlainText(), "Keep description")
        self.assertNotIn("private detail", self.form.reference_feedback.text())
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.assertEqual(self.form.company_input.count(), 4)

    def test_reference_worker_keeps_ui_responsive_and_blocks_conflicting_actions(self):
        gate = threading.Event()
        original = self.form._reference_service.list_active_companies

        def delayed():
            gate.wait(3)
            return original()

        with patch.object(self.form._reference_service, "list_active_companies", side_effect=delayed):
            try:
                self.form.refresh_references_button.click()
                ticks = []
                QTimer.singleShot(0, lambda: ticks.append(True))
                QTest.qWait(30)
                self.assertTrue(ticks)
                self.assertTrue(self.window.runner.busy)
                self.assertFalse(self.window.pages.isEnabled())
                self.assertFalse(self.window.close())
            finally:
                gate.set()
                self.wait_idle()

    def test_stale_selection_save_failure_keeps_draft_and_refresh_allows_recovery(self):
        self.select_company(self.a)
        self.form.contact_input.setCurrentIndex(1)
        self.form.subject_input.setText("Keep stale draft")
        with database_connection(self.path) as connection:
            connection.execute("UPDATE contacts SET is_active = 0 WHERE contact_id = ?", (self.alice.contact_id,))
        self.form.save_button.click()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.form)
        self.assertEqual(self.form.subject_input.text(), "Keep stale draft")
        self.assertEqual(self.form.contact_input.currentData(), self.alice.contact_id)
        self.assertIn("active contact", self.form.form_error.text())
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.assertIsNone(self.form.contact_input.currentData())
        self.form.save_button.click()
        self.wait_idle()
        self.assertIn("Contact: Not selected", self.window.workspace.summary.toPlainText())

    def test_inactive_and_deleted_historical_references_display_safely(self):
        ticket = self.context.ticket_service.create_ticket(subject="History", company_id=self.a.company_id,
                                                          contact_id=self.alice.contact_id)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE companies SET is_active = 0 WHERE company_id = ?", (self.a.company_id,))
            connection.execute("UPDATE contacts SET is_active = 0 WHERE contact_id = ?", (self.alice.contact_id,))
        self.window.pages.setCurrentWidget(self.window.workspace)
        self.window.workspace.open_ticket(ticket.ticket_id)
        self.wait_idle()
        self.assertIn("Northwind Support Labs", self.window.workspace.summary.toPlainText())
        self.assertIn("Alice Example", self.window.workspace.summary.toPlainText())
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM contacts WHERE contact_id = ?", (self.alice.contact_id,))
            connection.execute("DELETE FROM companies WHERE company_id = ?", (self.a.company_id,))
        self.window.workspace.reload_button.click()
        self.wait_idle()
        self.assertIn("Company: Not selected", self.window.workspace.summary.toPlainText())
        self.assertIn("Contact: Not selected", self.window.workspace.summary.toPlainText())
