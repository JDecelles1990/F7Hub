"""Exercise the saved-ticket window through real workers and isolated SQLite."""

import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.gui.main_window import MainWindow
from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories import TicketRepository
from f7hub.services import TicketService


class TicketWorkspaceFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "tickets.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repository = TicketRepository(self.path)
        self.service = TicketService(self.repository)
        self.window = MainWindow(self.service)
        self.workspace = self.window.workspace
        self.window.show()
        self.window.ticket_create_widget.subject_input.setText("Printer offline")
        self.window.ticket_create_widget.save_button.click()
        self.wait_idle()
        self.ticket_id = self.workspace.details.ticket.ticket_id

    def tearDown(self):
        self.wait_idle()
        self.workspace._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.temp.cleanup()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Service worker timed out")

    def set_status(self, status, resolution=None):
        index = self.workspace.status_input.findData(status)
        self.assertGreater(index, 0)
        self.workspace.status_input.setCurrentIndex(index)
        if resolution is not None:
            self.workspace.resolution_input.setPlainText(resolution)
        self.workspace.change_status_button.click()
        self.wait_idle()

    def test_create_note_resolve_close_reopen_and_reload(self):
        self.assertIs(self.window.pages.currentWidget(), self.workspace)
        self.workspace.note_input.setPlainText("Restarted spooler <literal text>")
        self.workspace.add_note_button.click()
        self.wait_idle()
        self.assertIn("<literal text>", self.workspace.notes_history.toPlainText())
        self.set_status("RESOLVED", "Replaced printer driver")
        self.set_status("CLOSED")
        self.set_status("OPEN")
        self.workspace.reload_button.click()
        self.wait_idle()
        details = self.service.get_ticket_details(self.ticket_id)
        self.assertEqual(details.ticket.status, "OPEN")
        self.assertIsNone(details.ticket.resolution)
        self.assertEqual([h.new_status for h in details.status_history],
                         ["NEW", "RESOLVED", "CLOSED", "OPEN"])
        self.assertIn("Replaced printer driver", self.workspace.notes_history.toPlainText())
        self.assertIn("CLOSED → OPEN", self.workspace.timeline.toPlainText())
        self.assertEqual(self.workspace.model.tickets[0].status, "OPEN")
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchall(), [("ok",)])
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_invalid_resolution_preserves_reason_and_status(self):
        self.workspace.reason_input.setText("Keep this reason")
        self.set_status("RESOLVED")
        self.assertEqual(self.workspace.status_input.currentData(), "RESOLVED")
        self.assertEqual(self.workspace.reason_input.text(), "Keep this reason")
        self.assertEqual(self.service.get_ticket_details(self.ticket_id).ticket.status, "NEW")
        self.assertIn("resolution", self.workspace.feedback.text().lower())

    def test_failed_note_save_preserves_draft_and_hides_internal_error(self):
        self.workspace.note_input.setPlainText("Keep my note")
        with patch.object(self.service, "add_note", side_effect=RuntimeError("private diagnostic")):
            self.workspace.add_note_button.click()
            self.wait_idle()
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep my note")
        self.assertNotIn("private diagnostic", self.workspace.feedback.text())
        self.assertEqual(len(self.repository.list_notes(self.ticket_id)), 0)

    def test_failed_status_save_preserves_all_drafts(self):
        self.workspace.note_input.setPlainText("Unrelated note")
        self.workspace.reason_input.setText("Reason draft")
        with patch.object(self.service, "change_status", side_effect=RuntimeError("private diagnostic")):
            self.set_status("RESOLVED", "Resolution draft")
        self.assertEqual(self.workspace.resolution_input.toPlainText(), "Resolution draft")
        self.assertEqual(self.workspace.reason_input.text(), "Reason draft")
        self.assertEqual(self.workspace.note_input.toPlainText(), "Unrelated note")
        self.assertEqual(self.workspace.status_input.currentData(), "RESOLVED")
        self.assertNotIn("private diagnostic", self.workspace.feedback.text())

    def test_committed_note_with_failed_reload_is_not_reported_as_failed_save(self):
        self.workspace.note_input.setPlainText("Saved exactly once")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private diagnostic")):
            self.workspace.add_note_button.click()
            self.wait_idle()
        self.assertIn("Note saved.", self.workspace.feedback.text())
        self.assertIn("Reload failed", self.workspace.feedback.text())
        self.assertEqual(self.workspace.note_input.toPlainText(), "")
        self.workspace.reload_button.click()
        self.wait_idle()
        self.assertEqual(len(self.repository.list_notes(self.ticket_id)), 1)
        self.assertIn("Saved exactly once", self.workspace.notes_history.toPlainText())

    def test_successful_status_with_failed_queue_refresh_retains_success(self):
        with patch.object(self.service, "list_tickets", side_effect=RuntimeError("private diagnostic")):
            self.set_status("OPEN")
        self.assertEqual(self.workspace.details.ticket.status, "OPEN")
        self.assertIn("Status changed to OPEN.", self.workspace.feedback.text())
        self.assertIn("Could not refresh", self.workspace.feedback.text())

    def test_cancel_switch_and_failed_load_preserve_existing_ticket_and_draft(self):
        other = self.service.create_ticket(subject="Other ticket")
        self.workspace.note_input.setPlainText("Do not lose this")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.workspace.open_ticket(other.ticket_id)
        self.assertFalse(self.window.runner.busy)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("unavailable")):
                self.workspace.open_ticket(other.ticket_id)
                self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Do not lose this")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.workspace.open_ticket(other.ticket_id)
            self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, other.ticket_id)
        self.assertFalse(self.workspace.has_draft())

    def test_paging_and_filter_reset(self):
        self.workspace.PAGE_SIZE = 2
        for number in range(4):
            self.service.create_ticket(subject=f"Ticket {number}")
        self.workspace.refresh_button.click()
        self.wait_idle()
        first_page = {t.ticket_id for t in self.workspace.model.tickets}
        self.workspace.next_button.click()
        self.wait_idle()
        self.assertTrue(first_page.isdisjoint(t.ticket_id for t in self.workspace.model.tickets))
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("CLOSED"))
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertFalse(self.workspace.previous_button.isEnabled())
        self.assertFalse(self.workspace.next_button.isEnabled())

    def test_created_ticket_with_failed_detail_load_is_recoverable_in_queue(self):
        self.window.show_new_ticket()
        self.window.ticket_create_widget.subject_input.setText("Saved despite reload failure")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private diagnostic")):
            self.window.ticket_create_widget.save_button.click()
            self.wait_idle()
        self.assertIn("Ticket created", self.workspace.feedback.text())
        self.assertIn("could not be loaded", self.workspace.feedback.text())
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), "")
        self.assertNotIn("private diagnostic", self.workspace.feedback.text())


if __name__ == "__main__":
    unittest.main()
