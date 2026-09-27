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
from f7hub.services.ticket_service import (
    TICKET_PRIORITIES, TICKET_TYPES, TicketReadError, TicketValidationError,
)


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

    def test_type_filter_composes_and_retains_page_through_refresh_and_open_number(self):
        self.assertIsNone(self.workspace.type_filter.itemData(0))
        selected_types = [self.workspace.type_filter.itemData(i)
                          for i in range(1, self.workspace.type_filter.count())]
        self.assertEqual(selected_types, list(TICKET_TYPES))
        self.assertEqual(len(selected_types), len(set(selected_types)))
        self.assertEqual(
            [(self.workspace.type_filter.itemText(i), self.workspace.type_filter.itemData(i))
             for i in range(self.workspace.type_filter.count())],
            [("All types", None), ("Incident", "INCIDENT"),
             ("Service request", "SERVICE_REQUEST"), ("Problem", "PROBLEM"),
             ("Task", "TASK")],
        )
        self.assertEqual(self.workspace.type_filter.accessibleName(), "Filter tickets by type")
        first = self.service.create_ticket(subject="First request", ticket_type="SERVICE_REQUEST",
                                           priority="HIGH", ticket_number="S29-FIRST")
        self.service.change_status(first.ticket_id, new_status="OPEN")
        second = self.service.create_ticket(subject="Second request", ticket_type="SERVICE_REQUEST",
                                            priority="HIGH", ticket_number="S29-SECOND")
        self.service.change_status(second.ticket_id, new_status="OPEN")
        self.service.create_ticket(subject="Other type", ticket_type="TASK", priority="HIGH")
        self.workspace.PAGE_SIZE = 1
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("OPEN"))
        self.wait_idle()
        self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("HIGH"))
        self.wait_idle()
        self.workspace.next_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.workspace.type_filter.setCurrentIndex(self.workspace.type_filter.findData("SERVICE_REQUEST"))
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
        self.assertEqual(self.workspace.status_filter.currentData(), "OPEN")
        self.assertEqual(self.workspace.priority_filter.currentData(), "HIGH")
        self.assertEqual(self.workspace.type_filter.currentData(), "SERVICE_REQUEST")
        self.workspace.priority_filter.setCurrentIndex(0)
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.assertEqual(self.workspace.type_filter.currentData(), "SERVICE_REQUEST")

    def test_failed_type_filter_read_keeps_requested_retry_and_drafts(self):
        target = self.service.create_ticket(subject="Target task", ticket_type="TASK",
                                            priority="HIGH")
        self.service.change_status(target.ticket_id, new_status="OPEN")
        other = self.service.create_ticket(subject="Other incident", ticket_type="INCIDENT",
                                           priority="HIGH")
        self.service.change_status(other.ticket_id, new_status="OPEN")
        self.workspace.PAGE_SIZE = 1
        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("OPEN"))
        self.wait_idle()
        self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("HIGH"))
        self.wait_idle()
        self.workspace.next_button.click()
        self.wait_idle()
        previous_rows = self.workspace.model.tickets
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(previous_rows, (self.repository.get_ticket(target.ticket_id),))
        self.workspace.note_input.setPlainText("Keep note draft")
        started = threading.Event()
        release = threading.Event()

        def delayed_failure(**kwargs):
            started.set()
            if not release.wait(5):
                raise TimeoutError("Type read gate timed out")
            raise sqlite3.OperationalError("private")

        try:
            with patch.object(self.service, "list_tickets", side_effect=delayed_failure):
                self.workspace.type_filter.setCurrentIndex(self.workspace.type_filter.findData("TASK"))
                self.assertTrue(started.wait(5))
                self.assertFalse(self.workspace.status_filter.isEnabled())
                self.assertFalse(self.workspace.priority_filter.isEnabled())
                self.assertFalse(self.workspace.type_filter.isEnabled())
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(self.workspace.model.tickets, previous_rows)
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep note draft")
        self.assertEqual(self.workspace.type_filter.currentData(), "TASK")
        self.assertEqual(self.workspace.status_filter.currentData(), "OPEN")
        self.assertEqual(self.workspace.priority_filter.currentData(), "HIGH")
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 1")
        self.assertEqual(self.workspace.model.tickets, (self.repository.get_ticket(target.ticket_id),))

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

    def test_subject_dialog_cancel_validation_and_success_refresh(self):
        ticket = self.workspace.details.ticket
        self.workspace.note_input.setPlainText("Keep note draft")
        cancelled = self.workspace.open_edit_subject()
        self.assertEqual(cancelled.subject_input.text(), ticket.subject)
        cancelled.cancel_button.click()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        dialog = self.workspace.open_edit_subject()
        dialog.subject_input.setText("  ")
        dialog.save_button.click()
        self.wait_idle()
        self.assertIn("non-blank", dialog.feedback.text())
        self.assertEqual(dialog.subject_input.text(), "  ")
        dialog.subject_input.setText("  Printer repaired  ")
        dialog.save_button.click()
        self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).subject, "Printer repaired")
        self.assertEqual(self.workspace.details.ticket.subject, "Printer repaired")
        self.assertEqual(self.workspace.model.tickets[0].subject, "Printer repaired")
        self.assertIn("Subject saved", self.workspace.feedback.text())
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep note draft")
        self.assertEqual([e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                         .count("SUBJECT_CHANGED"), 1)

    def test_subject_dialog_stale_and_save_failure_retain_entry(self):
        ticket = self.workspace.details.ticket
        dialog = self.workspace.open_edit_subject()
        dialog.subject_input.setText("Wanted subject")
        self.service.update_ticket_subject(
            ticket.ticket_id, expected_subject=ticket.subject,
            expected_updated_at=ticket.updated_at, subject="External change",
        )
        dialog.save_button.click()
        self.wait_idle()
        self.assertIn("Reload", dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(dialog.subject_input.text(), "Wanted subject")
        dialog.cancel_button.click()
        self.workspace.open_ticket(ticket.ticket_id)
        self.wait_idle()
        failed = self.workspace.open_edit_subject()
        failed.subject_input.setText("Retry this")
        with patch.object(self.service, "update_ticket_subject", side_effect=RuntimeError("private")):
            failed.save_button.click()
            self.wait_idle()
        self.assertEqual(failed.subject_input.text(), "Retry this")
        self.assertIn("Could not save the subject", failed.feedback.text())
        self.assertNotIn("private", failed.feedback.text())
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).subject, "External change")
        failed.cancel_button.click()

    def test_subject_dialog_blocks_duplicate_save_and_close_while_busy(self):
        dialog = self.workspace.open_edit_subject()
        dialog.subject_input.setText("Delayed subject")
        started = threading.Event()
        release = threading.Event()
        original = self.service.update_ticket_subject
        calls = []

        def delayed_update(*args, **kwargs):
            calls.append(kwargs["subject"])
            started.set()
            if not release.wait(5):
                raise TimeoutError("Update gate timed out")
            return original(*args, **kwargs)

        try:
            with patch.object(self.service, "update_ticket_subject", side_effect=delayed_update):
                dialog.save_button.click()
                self.assertTrue(started.wait(5))
                self.assertFalse(dialog.save_button.isEnabled())
                self.assertFalse(dialog.cancel_button.isEnabled())
                dialog.submit()
                dialog.reject()
                self.assertTrue(dialog.isVisible())
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(calls, ["Delayed subject"])
        self.assertEqual(self.repository.get_ticket(self.ticket_id).subject, "Delayed subject")

    def test_committed_subject_edit_survives_detail_and_queue_reload_failures(self):
        ticket = self.workspace.details.ticket
        first = self.workspace.open_edit_subject()
        first.subject_input.setText("Saved despite detail failure")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private")):
            first.save_button.click()
            self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).subject,
                         "Saved despite detail failure")
        self.assertIn("Subject saved", self.workspace.feedback.text())
        self.assertIn("Reload ticket", self.workspace.feedback.text())
        self.assertNotIn("private", self.workspace.feedback.text())
        self.workspace.reload_button.click()
        self.wait_idle()
        errors = (
            RuntimeError("private"),
            TicketValidationError("Invalid queue filter."),
            TicketReadError("F7Hub could not load the ticket list."),
        )
        for index, error in enumerate(errors, start=1):
            with self.subTest(error=type(error).__name__):
                subject = f"Saved despite queue failure {index}"
                dialog = self.workspace.open_edit_subject()
                dialog.subject_input.setText(subject)
                original_update = self.service.update_ticket_subject
                with patch.object(self.service, "update_ticket_subject", wraps=original_update) as update:
                    with patch.object(self.service, "list_tickets", side_effect=error):
                        dialog.save_button.click()
                        self.wait_idle()
                self.assertEqual(update.call_count, 1)
                self.assertEqual(self.repository.get_ticket(ticket.ticket_id).subject, subject)
                self.assertEqual(self.workspace.details.ticket.subject, subject)
                self.assertIn("Subject saved", self.workspace.feedback.text())
                self.assertIn("Could not refresh tickets", self.workspace.feedback.text())
                self.assertIn("Refresh to retry", self.workspace.feedback.text())
                if isinstance(error, TicketValidationError):
                    self.assertIn(str(error), self.workspace.feedback.text())
                else:
                    self.assertNotIn("private", self.workspace.feedback.text())
                event_count = [e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                self.assertEqual(event_count.count("SUBJECT_CHANGED"), index + 1)
                self.workspace.refresh_button.click()
                self.wait_idle()
                self.assertEqual(self.workspace.model.tickets[0].subject, subject)
                self.assertEqual([e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                                 .count("SUBJECT_CHANGED"), index + 1)

    def test_ordinary_queue_validation_failure_keeps_existing_feedback(self):
        previous_rows = self.workspace.model.tickets
        with patch.object(self.service, "list_tickets",
                          side_effect=TicketValidationError("Invalid queue filter.")):
            self.workspace.refresh_button.click()
            self.wait_idle()
        self.assertEqual(self.workspace.feedback.text(), "Invalid queue filter.")
        self.assertEqual(self.workspace.model.tickets, previous_rows)

    def test_description_dialog_null_prefill_cancel_multiline_save_and_clear(self):
        ticket = self.workspace.details.ticket
        self.assertIsNone(ticket.description)
        self.workspace.note_input.setPlainText("Keep note draft")
        cancelled = self.workspace.open_edit_description()
        self.assertEqual(cancelled.description_input.toPlainText(), "")
        cancelled.description_input.setPlainText("Unsaved draft")
        cancelled.cancel_button.click()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        unchanged = self.workspace.open_edit_description()
        unchanged.description_input.setPlainText(" \n ")
        unchanged.save_button.click()
        self.wait_idle()
        self.assertIn("Description unchanged", self.workspace.feedback.text())
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        dialog = self.workspace.open_edit_description()
        dialog.description_input.setPlainText("  First line\n  Second line\n")
        dialog.save_button.click()
        self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).description,
                         "First line\n  Second line")
        self.assertEqual(self.workspace.details.ticket.description, "First line\n  Second line")
        self.assertIn("First line\n  Second line", self.workspace.summary.toPlainText())
        self.assertIn("Description saved", self.workspace.feedback.text())
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep note draft")
        self.assertEqual([e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                         .count("DESCRIPTION_CHANGED"), 1)
        clear = self.workspace.open_edit_description()
        self.assertEqual(clear.description_input.toPlainText(), "First line\n  Second line")
        clear.description_input.setPlainText(" \n ")
        clear.save_button.click()
        self.wait_idle()
        self.assertIsNone(self.repository.get_ticket(ticket.ticket_id).description)
        self.assertIn("(No description)", self.workspace.summary.toPlainText())

    def test_description_dialog_stale_and_failures_preserve_multiline_draft(self):
        ticket = self.workspace.details.ticket
        dialog = self.workspace.open_edit_description()
        wanted = "Wanted\n  multiline draft"
        dialog.description_input.setPlainText(wanted)
        self.service.update_ticket_description(
            ticket.ticket_id, expected_description=None,
            expected_updated_at=ticket.updated_at, description="External change",
        )
        dialog.save_button.click()
        self.wait_idle()
        self.assertIn("Reload", dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(dialog.description_input.toPlainText(), wanted)
        dialog.cancel_button.click()
        self.workspace.reload_button.click()
        self.wait_idle()
        failed = self.workspace.open_edit_description()
        self.assertEqual(failed.description_input.toPlainText(), "External change")
        failed.description_input.setPlainText(wanted)
        with patch.object(self.service, "update_ticket_description",
                          side_effect=TicketValidationError("Invalid description.")):
            failed.save_button.click()
            self.wait_idle()
        self.assertEqual(failed.description_input.toPlainText(), wanted)
        self.assertIn("Invalid description", failed.feedback.text())
        with patch.object(self.service, "update_ticket_description",
                          side_effect=RuntimeError("private")):
            failed.save_button.click()
            self.wait_idle()
        self.assertEqual(failed.description_input.toPlainText(), wanted)
        self.assertIn("Could not save the description", failed.feedback.text())
        self.assertNotIn("private", failed.feedback.text())
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).description,
                         "External change")
        failed.cancel_button.click()

    def test_description_dialog_blocks_duplicate_save_and_close_while_busy(self):
        dialog = self.workspace.open_edit_description()
        dialog.description_input.setPlainText("Delayed\nupdate")
        started = threading.Event()
        release = threading.Event()
        original = self.service.update_ticket_description
        calls = []

        def delayed_update(*args, **kwargs):
            calls.append(kwargs["description"])
            started.set()
            if not release.wait(5):
                raise TimeoutError("Update gate timed out")
            return original(*args, **kwargs)

        try:
            with patch.object(self.service, "update_ticket_description", side_effect=delayed_update):
                dialog.save_button.click()
                self.assertTrue(started.wait(5))
                self.assertFalse(dialog.save_button.isEnabled())
                self.assertFalse(dialog.cancel_button.isEnabled())
                dialog.submit()
                dialog.reject()
                self.assertTrue(dialog.isVisible())
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(calls, ["Delayed\nupdate"])
        self.assertEqual(self.repository.get_ticket(self.ticket_id).description,
                         "Delayed\nupdate")

    def test_committed_description_edit_survives_refresh_failures_and_preserves_filters(self):
        ticket = self.workspace.details.ticket
        self.workspace.note_input.setPlainText("Keep note draft")
        self.workspace.reason_input.setText("Keep reason")
        self.workspace.status_filter.setCurrentIndex(
            self.workspace.status_filter.findData("NEW")
        )
        self.wait_idle()
        self.workspace.priority_filter.setCurrentIndex(
            self.workspace.priority_filter.findData("MEDIUM")
        )
        self.wait_idle()
        self.workspace.type_filter.setCurrentIndex(
            self.workspace.type_filter.findData("INCIDENT")
        )
        self.wait_idle()
        first = self.workspace.open_edit_description()
        first.description_input.setPlainText("Saved despite detail failure")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private")):
            first.save_button.click()
            self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).description,
                         "Saved despite detail failure")
        self.assertIn("Description saved", self.workspace.feedback.text())
        self.assertIn("Reload ticket", self.workspace.feedback.text())
        self.assertNotIn("private", self.workspace.feedback.text())
        self.workspace.reload_button.click()
        self.wait_idle()
        errors = (
            RuntimeError("private"),
            TicketValidationError("Invalid queue filter."),
            TicketReadError("F7Hub could not load the ticket list."),
        )
        for index, error in enumerate(errors, start=1):
            with self.subTest(error=type(error).__name__):
                description = f"Saved despite queue failure {index}\nMore detail"
                dialog = self.workspace.open_edit_description()
                dialog.description_input.setPlainText(description)
                original_update = self.service.update_ticket_description
                with patch.object(self.service, "update_ticket_description",
                                  wraps=original_update) as update:
                    with patch.object(self.service, "list_tickets", side_effect=error):
                        dialog.save_button.click()
                        self.wait_idle()
                self.assertEqual(update.call_count, 1)
                self.assertEqual(self.repository.get_ticket(ticket.ticket_id).description,
                                 description)
                self.assertEqual(self.workspace.details.ticket.description, description)
                self.assertIn("Description saved", self.workspace.feedback.text())
                self.assertIn("Could not refresh tickets", self.workspace.feedback.text())
                self.assertIn("Refresh to retry", self.workspace.feedback.text())
                if isinstance(error, TicketValidationError):
                    self.assertIn(str(error), self.workspace.feedback.text())
                else:
                    self.assertNotIn("private", self.workspace.feedback.text())
                event_count = [e.event_type for e in
                               self.repository.list_timeline_events(ticket.ticket_id)]
                self.workspace.refresh_button.click()
                self.wait_idle()
                self.assertEqual(self.workspace.model.tickets[0].description, description)
                self.assertEqual([e.event_type for e in
                                  self.repository.list_timeline_events(ticket.ticket_id)],
                                 event_count)
        self.assertEqual(self.workspace.status_filter.currentData(), "NEW")
        self.assertEqual(self.workspace.priority_filter.currentData(), "MEDIUM")
        self.assertEqual(self.workspace.type_filter.currentData(), "INCIDENT")
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep note draft")
        self.assertEqual(self.workspace.reason_input.text(), "Keep reason")

    def test_description_save_keeps_current_queue_page_and_open_detail(self):
        for index in range(self.workspace.PAGE_SIZE + 1):
            self.repository.create_ticket(
                ticket_number=f"PAGE-32-{index}", subject=f"Older ticket {index}",
                created_at="2026-09-01T00:00:00.000Z",
                updated_at="2026-09-01T00:00:00.000Z",
            )
        self.workspace.refresh_list(offset=self.workspace.PAGE_SIZE)
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace._offset, self.workspace.PAGE_SIZE)
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        dialog = self.workspace.open_edit_description()
        dialog.description_input.setPlainText("Saved while on page two")
        dialog.save_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.page_label.text(), "Page 2")
        self.assertEqual(self.workspace._offset, self.workspace.PAGE_SIZE)
        self.assertEqual(self.workspace.details.ticket.ticket_id, self.ticket_id)
        self.assertEqual(self.workspace.details.ticket.description,
                         "Saved while on page two")
        self.assertIn("Description saved", self.workspace.feedback.text())

    def test_priority_dialog_choices_cancel_no_op_and_success(self):
        ticket = self.workspace.details.ticket
        self.workspace.note_input.setPlainText("Keep note draft")
        cancelled = self.workspace.open_edit_priority()
        self.assertEqual(cancelled.priority_input.currentData(), ticket.priority)
        self.assertEqual({cancelled.priority_input.itemData(index)
                          for index in range(cancelled.priority_input.count())}, TICKET_PRIORITIES)
        cancelled.cancel_button.click()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        unchanged = self.workspace.open_edit_priority()
        unchanged.save_button.click()
        self.wait_idle()
        self.assertIn("Priority unchanged", self.workspace.feedback.text())
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        dialog = self.workspace.open_edit_priority()
        dialog.priority_input.setCurrentIndex(dialog.priority_input.findData("HIGH"))
        dialog.save_button.click()
        self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).priority, "HIGH")
        self.assertEqual(self.workspace.details.ticket.priority, "HIGH")
        self.assertEqual(self.workspace.model.tickets[0].priority, "HIGH")
        self.assertIn("Priority saved", self.workspace.feedback.text())
        self.assertEqual(self.workspace.note_input.toPlainText(), "Keep note draft")
        self.assertEqual([e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                         .count("PRIORITY_CHANGED"), 1)

    def test_priority_dialog_stale_and_failure_keep_selection(self):
        ticket = self.workspace.details.ticket
        dialog = self.workspace.open_edit_priority()
        dialog.priority_input.setCurrentIndex(dialog.priority_input.findData("HIGH"))
        self.service.update_ticket_priority(
            ticket.ticket_id, expected_priority=ticket.priority,
            expected_updated_at=ticket.updated_at, priority="LOW",
        )
        dialog.save_button.click()
        self.wait_idle()
        self.assertIn("Reload", dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(dialog.priority_input.currentData(), "HIGH")
        dialog.cancel_button.click()
        self.workspace.reload_button.click()
        self.wait_idle()
        failed = self.workspace.open_edit_priority()
        failed.priority_input.setCurrentIndex(failed.priority_input.findData("CRITICAL"))
        with patch.object(self.service, "update_ticket_priority",
                          side_effect=TicketValidationError("Invalid priority.")):
            failed.save_button.click()
            self.wait_idle()
        self.assertEqual(failed.priority_input.currentData(), "CRITICAL")
        self.assertIn("Invalid priority", failed.feedback.text())
        with patch.object(self.service, "update_ticket_priority", side_effect=RuntimeError("private")):
            failed.save_button.click()
            self.wait_idle()
        self.assertEqual(failed.priority_input.currentData(), "CRITICAL")
        self.assertIn("Could not save the priority", failed.feedback.text())
        self.assertNotIn("private", failed.feedback.text())
        failed.cancel_button.click()

    def test_priority_dialog_blocks_duplicate_save_and_close_while_busy(self):
        dialog = self.workspace.open_edit_priority()
        dialog.priority_input.setCurrentIndex(dialog.priority_input.findData("HIGH"))
        started = threading.Event()
        release = threading.Event()
        original = self.service.update_ticket_priority
        calls = []

        def delayed_update(*args, **kwargs):
            calls.append(kwargs["priority"])
            started.set()
            if not release.wait(5):
                raise TimeoutError("Update gate timed out")
            return original(*args, **kwargs)

        try:
            with patch.object(self.service, "update_ticket_priority", side_effect=delayed_update):
                dialog.save_button.click()
                self.assertTrue(started.wait(5))
                self.assertFalse(dialog.save_button.isEnabled())
                self.assertFalse(dialog.cancel_button.isEnabled())
                dialog.submit()
                dialog.reject()
                self.assertTrue(dialog.isVisible())
                release.set()
                self.wait_idle()
        finally:
            release.set()
        self.assertEqual(calls, ["HIGH"])
        self.assertEqual(self.repository.get_ticket(self.ticket_id).priority, "HIGH")

    def test_committed_priority_edit_survives_refresh_failures_and_filter_exit(self):
        ticket = self.workspace.details.ticket
        first = self.workspace.open_edit_priority()
        first.priority_input.setCurrentIndex(first.priority_input.findData("LOW"))
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private")):
            first.save_button.click()
            self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).priority, "LOW")
        self.assertIn("Priority saved", self.workspace.feedback.text())
        self.assertIn("Reload ticket", self.workspace.feedback.text())
        self.workspace.reload_button.click()
        self.wait_idle()
        errors = (
            RuntimeError("private"),
            TicketValidationError("Invalid queue filter."),
            TicketReadError("F7Hub could not load the ticket list."),
        )
        for priority, error in zip(("MEDIUM", "HIGH", "CRITICAL"), errors):
            with self.subTest(error=type(error).__name__):
                dialog = self.workspace.open_edit_priority()
                dialog.priority_input.setCurrentIndex(dialog.priority_input.findData(priority))
                original_update = self.service.update_ticket_priority
                with patch.object(self.service, "update_ticket_priority", wraps=original_update) as update:
                    with patch.object(self.service, "list_tickets", side_effect=error):
                        dialog.save_button.click()
                        self.wait_idle()
                self.assertEqual(update.call_count, 1)
                self.assertEqual(self.repository.get_ticket(ticket.ticket_id).priority, priority)
                self.assertEqual(self.workspace.details.ticket.priority, priority)
                self.assertIn("Priority saved", self.workspace.feedback.text())
                self.assertIn("Could not refresh tickets", self.workspace.feedback.text())
                self.assertIn("Refresh to retry", self.workspace.feedback.text())
                if isinstance(error, TicketValidationError):
                    self.assertIn(str(error), self.workspace.feedback.text())
                else:
                    self.assertNotIn("private", self.workspace.feedback.text())
                before_retry = [e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)]
                self.workspace.refresh_button.click()
                self.wait_idle()
                self.assertEqual(self.workspace.model.tickets[0].priority, priority)
                self.assertEqual([e.event_type for e in self.repository.list_timeline_events(ticket.ticket_id)],
                                 before_retry)

        self.workspace.status_filter.setCurrentIndex(self.workspace.status_filter.findData("NEW"))
        self.wait_idle()
        self.workspace.type_filter.setCurrentIndex(self.workspace.type_filter.findData("INCIDENT"))
        self.wait_idle()
        self.workspace.priority_filter.setCurrentIndex(self.workspace.priority_filter.findData("CRITICAL"))
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 1)
        dialog = self.workspace.open_edit_priority()
        dialog.priority_input.setCurrentIndex(dialog.priority_input.findData("LOW"))
        dialog.save_button.click()
        self.wait_idle()
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id).priority, "LOW")
        self.assertEqual(self.workspace.details.ticket.priority, "LOW")
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertEqual(self.workspace.status_filter.currentData(), "NEW")
        self.assertEqual(self.workspace.priority_filter.currentData(), "CRITICAL")
        self.assertEqual(self.workspace.type_filter.currentData(), "INCIDENT")
        self.assertIn("Priority saved", self.workspace.feedback.text())


if __name__ == "__main__":
    unittest.main()
