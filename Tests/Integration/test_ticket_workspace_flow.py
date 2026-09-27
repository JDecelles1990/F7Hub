"""Exercise the saved-ticket window through real workers and isolated SQLite."""

import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
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

    def test_priority_and_status_filter_compose_with_page_refresh_and_number_open(self):
        self.assertEqual(
            [self.workspace.priority_filter.itemData(index)
             for index in range(self.workspace.priority_filter.count())],
            [None, "CRITICAL", "HIGH", "MEDIUM", "LOW"],
        )
        self.assertEqual(self.workspace.priority_filter.accessibleName(), "Filter tickets by priority")
        first = self.service.create_ticket(subject="First high", priority="HIGH", ticket_number="P28-FIRST")
        self.service.change_status(first.ticket_id, new_status="OPEN")
        second = self.service.create_ticket(subject="Second high", priority="HIGH", ticket_number="P28-SECOND")
        self.service.change_status(second.ticket_id, new_status="OPEN")
        self.service.create_ticket(subject="Other priority", priority="LOW")
        self.workspace.PAGE_SIZE = 1
        self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("HIGH"))
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("OPEN"))
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.assertEqual(self.workspace.model.tickets, (self.repository.get_ticket(second.ticket_id),))
        self.workspace.next_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.tickets, (self.repository.get_ticket(first.ticket_id),))
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace.model.tickets, (self.repository.get_ticket(first.ticket_id),))
        self.workspace.ticket_number_input.setText(self.repository.get_ticket(self.ticket_id).ticket_number)
        self.workspace.open_number_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace.priority_filter.currentData(), "HIGH")
        self.assertEqual(self.workspace.status_filter.currentData(), "OPEN")
        self.workspace.priority_filter.setCurrentIndex(0)
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.assertIsNone(self.workspace.priority_filter.currentData())

    def test_failed_priority_read_keeps_rows_detail_draft_and_retry(self):
        high = self.service.create_ticket(subject="High ticket", priority="HIGH")
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("NEW"))
        self.wait_idle()
        self.workspace.PAGE_SIZE = 1
        self.workspace.refresh_list(offset=0)
        self.wait_idle()
        self.workspace.next_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        previous_rows = self.workspace.model.tickets
        previous_page = self.workspace.page_label.text()
        self.workspace.note_input.setPlainText("Keep draft")
        started = threading.Event()
        release = threading.Event()
        original = self.service.list_tickets

        def delayed_failure(**kwargs):
            started.set()
            if not release.wait(5):
                raise TimeoutError("Priority read gate timed out")
            raise sqlite3.OperationalError("private")

        try:
            with patch.object(self.service, "list_tickets", side_effect=delayed_failure):
                self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("HIGH"))
                self.assertTrue(started.wait(5))
                self.assertFalse(self.workspace.status_filter.isEnabled())
                self.assertFalse(self.workspace.priority_filter.isEnabled())
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(self.workspace.model.tickets, previous_rows)
        self.assertEqual(self.workspace.page_label.text(), previous_page)
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep draft")
        self.assertEqual(self.workspace.priority_filter.currentData(), "HIGH")
        self.assertEqual(self.workspace.status_filter.currentData(), "NEW")
        self.assertTrue(self.workspace.status_filter.isEnabled())
        self.assertTrue(self.workspace.priority_filter.isEnabled())
        self.assertIn("Previous results are still shown", self.workspace.feedback.text())
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.tickets, (self.repository.get_ticket(high.ticket_id),))
        self.assertEqual(self.workspace.page_label.text(), "Page 1")

    def test_open_exact_number_outside_queue_filter_and_page(self):
        other = self.service.create_ticket(subject="Target", ticket_number="INC-SEARCH-27")
        self.service.create_ticket(subject="Newer ticket", ticket_number="INC-NEWER-27")
        self.service.create_ticket(subject="Newest ticket", ticket_number="INC-NEWEST-27")
        self.workspace.PAGE_SIZE = 1
        self.workspace.refresh_list(offset=0)
        self.wait_idle()
        self.workspace.next_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertNotIn(other.ticket_id, [ticket.ticket_id for ticket in self.workspace.model.tickets])
        self.workspace.ticket_number_input.setText("  inc-search-27  ")
        self.workspace.open_number_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, other.ticket_id)
        self.assertIsNone(self.workspace.status_filter.currentData())
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace.ticket_number_input.text(), "  inc-search-27  ")
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("CLOSED"))
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.workspace.open_number_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, other.ticket_id)
        self.assertEqual(self.workspace.status_filter.currentData(), "CLOSED")
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.workspace.ticket_number_input.setText(self.repository.get_ticket(self.ticket_id).ticket_number)
        QTest.keyClick(self.workspace.ticket_number_input, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)

    def test_number_lookup_blank_missing_and_read_error_preserve_detail_and_draft(self):
        self.workspace.note_input.setPlainText("Keep this draft")
        with patch.object(self.service, "get_ticket_details_by_number") as lookup:
            self.workspace.ticket_number_input.setText("  ")
            self.workspace.open_number_button.click()
            lookup.assert_not_called()
        self.assertIn("Enter a ticket number", self.workspace.feedback.text())
        self.workspace.ticket_number_input.setText("INC-MISSING")
        self.workspace.open_number_button.click()
        self.wait_idle()
        self.assertIn("No ticket has that number", self.workspace.feedback.text())
        with patch.object(self.service, "get_ticket_details_by_number", side_effect=RuntimeError("private")):
            self.workspace.open_number_button.click()
            self.wait_idle()
        self.assertNotIn("private", self.workspace.feedback.text())
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep this draft")
        self.assertEqual(self.workspace.ticket_number_input.text(), "INC-MISSING")

    def test_number_lookup_cancel_preserves_draft_and_busy_lookup_is_single(self):
        other = self.service.create_ticket(subject="Other", ticket_number="INC-OTHER-27")
        self.workspace.note_input.setPlainText("Keep this draft")
        self.workspace.ticket_number_input.setText("INC-OTHER-27")
        started = threading.Event()
        release = threading.Event()
        original = self.service.get_ticket_details_by_number
        calls = []

        def delayed_lookup(number):
            calls.append(number)
            started.set()
            if not release.wait(5):
                raise TimeoutError("Lookup gate timed out")
            return original(number)

        try:
            with patch.object(self.service, "get_ticket_details_by_number", side_effect=delayed_lookup):
                with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
                    self.workspace.open_number_button.click()
                    self.assertTrue(started.wait(5))
                    self.assertFalse(self.workspace.open_number_button.isEnabled())
                    self.workspace.open_ticket_by_number()
                    self.assertEqual(calls, ["INC-OTHER-27"])
                    release.set()
                    self.wait_idle()
        finally:
            release.set()
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep this draft")
        self.assertIn("cancelled", self.workspace.feedback.text())
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.workspace.open_number_button.click()
            self.wait_idle()
        self.assertEqual(self.workspace.details.ticket.ticket_id, other.ticket_id)
        self.assertFalse(self.workspace.has_draft())

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
