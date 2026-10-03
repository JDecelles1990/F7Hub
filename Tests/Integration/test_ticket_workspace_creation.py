"""Integrated creation modes, saved identities and callback ownership on SQLite."""
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from f7hub.gui.main_window import MainWindow
from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories import TicketRepository
from f7hub.services import TicketService


class WorkspaceCreationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "tickets.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repo = TicketRepository(self.path)
        self.service = TicketService(self.repo)
        self.old = self.service.create_ticket(subject="Original ticket")
        self.window = MainWindow(self.service)
        self.ws = self.window.workspace
        self.form = self.window.ticket_create_widget
        self.window.show()
        self.window.show_tickets()
        self.idle()
        self.ws.open_ticket(self.old.ticket_id)
        self.idle()

    def tearDown(self):
        self.idle()
        self.ws._clear_drafts()
        self.form.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def idle(self):
        deadline = time.monotonic() + 5
        while (self.window.runner.busy or self.ws.creation_pending or self.ws.status_pending) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy or self.ws.creation_pending or self.ws.status_pending)

    def state(self):
        return (self.ws._offset, self.ws._subject_query, self.ws.subject_search_input.text(),
                self.ws.status_filter.currentData(), self.ws.priority_filter.currentData(),
                self.ws.type_filter.currentData(), self.ws.table.currentIndex().row())

    def test_navigation_and_entry_reuse_form_without_writes(self):
        self.assertEqual(self.window.tickets_action.text(), "Tickets")
        self.assertFalse(hasattr(self.window, "new_ticket_action"))
        self.assertEqual(self.window.pages.indexOf(self.form), -1)
        actions = [a.text().casefold() for a in self.window.findChildren(QAction)]
        self.assertNotIn("saved tickets", actions)
        self.assertNotIn("new ticket", actions)
        before = self.path.read_bytes()
        self.ws.new_ticket_button.click()
        self.app.processEvents()
        self.assertTrue(self.ws.creating)
        self.assertIs(self.ws.creation_scroll.widget(), self.form)
        self.assertIs(self.window.pages.currentWidget(), self.ws)
        self.assertTrue(self.ws.table.isVisible())
        self.assertTrue(self.form.subject_input.hasFocus())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse(self.ws.new_ticket_button.isEnabled())

    def test_cancel_preserves_filters_search_page_selection_and_tabs(self):
        for combo, value in ((self.ws.status_filter, "OPEN"), (self.ws.priority_filter, "HIGH"),
                             (self.ws.type_filter, "TASK")):
            combo.setCurrentIndex(combo.findData(value))
            self.idle()
        self.ws.subject_search_input.setText("applied")
        self.ws.search_subjects()
        self.idle()
        self.ws.refresh_list(offset=100)
        self.idle()
        self.ws.subject_search_input.setText("unsubmitted")
        self.ws.detail_tabs.setCurrentIndex(2)
        state = self.state()
        before = self.path.read_bytes()
        self.ws.begin_creation()
        self.ws.cancel_create_button.click()
        self.assertFalse(self.ws.creating)
        self.assertEqual(self.ws.details.ticket.ticket_id, self.old.ticket_id)
        self.assertEqual(self.state(), state)
        self.assertEqual(self.ws.detail_tabs.currentIndex(), 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_activity_drafts_require_discard_and_quick_note_has_no_target_in_creation(self):
        self.ws.note_input.setPlainText("Keep note")
        self.ws.reason_input.setText("Keep reason")
        self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("RESOLVED"))
        self.ws.resolution_input.setPlainText("Keep resolution")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.ws.new_ticket_button.click()
        self.assertFalse(self.ws.creating)
        self.assertEqual(self.ws.note_input.toPlainText(), "Keep note")
        self.assertEqual(self.ws.reason_input.text(), "Keep reason")
        self.assertEqual(self.ws.resolution_input.toPlainText(), "Keep resolution")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.ws.new_ticket_button.click()
        self.assertIsNone(self.ws.details)
        self.assertFalse(self.ws.has_draft())
        self.assertFalse(self.ws.note_input.isVisible())
        self.assertFalse(self.ws.note_input.isEnabled())
        self.ws.note_input.setPlainText("Cannot write to old ticket")
        self.ws.add_note()
        self.ws.change_status()
        QTest.keyClick(self.ws.note_input, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(self.repo.list_notes(self.old.ticket_id), ())
        self.ws._clear_drafts()

    def test_cancel_discard_convention_and_zero_writes(self):
        previous_row = self.ws.table.currentIndex().row()
        self.ws.begin_creation()
        self.form.subject_input.setText("Unsaved")
        before = self.path.read_bytes()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.ws.cancel_create_button.click()
        self.assertTrue(self.ws.creating)
        self.assertEqual(self.form.subject_input.text(), "Unsaved")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.ws.cancel_create_button.click()
        self.assertFalse(self.ws.creating)
        self.assertEqual(self.form.subject_input.text(), "")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.ws.table.currentIndex().row(), previous_row)
        self.assertEqual(self.ws.details.ticket.ticket_id, self.old.ticket_id)

    def test_hidden_creation_shortcut_cannot_submit_from_saved_detail(self):
        self.form.subject_input.setText("Hidden form must not create")
        self.ws.note_input.setFocus()
        QTest.keyClick(self.ws.note_input, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
        self.idle()
        self.assertEqual(len(self.service.list_tickets()), 1)
        self.assertFalse(self.ws.creating)

    def test_success_one_atomic_ticket_authoritative_detail_and_selected_queue_row(self):
        self.ws.begin_creation()
        self.form.subject_input.setText("New saved ticket")
        self.form.description_input.setPlainText("Saved description")
        self.form.save_button.click()
        self.form.submit()
        self.idle()
        new = self.ws.details.ticket
        self.assertFalse(self.ws.creating)
        self.assertEqual(len(self.service.list_tickets()), 2)
        self.assertEqual(self.ws.details, self.service.get_ticket_details(new.ticket_id))
        self.assertEqual(self.ws.model.tickets[self.ws.table.currentIndex().row()].ticket_id, new.ticket_id)
        self.assertEqual(len(self.repo.list_status_history(new.ticket_id)), 1)
        self.assertEqual(len(self.repo.list_timeline_events(new.ticket_id)), 1)
        self.assertTrue(self.ws.note_input.isVisible())
        self.assertTrue(self.ws.note_input.isEnabled())
        self.assertTrue(self.ws.note_type.isEnabled())
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_success_preserves_excluding_filters_and_page_but_opens_created_detail(self):
        self.ws.status_filter.setCurrentIndex(self.ws.status_filter.findData("CLOSED"))
        self.idle()
        self.ws.refresh_list(offset=100)
        self.idle()
        before = self.state()
        self.ws.begin_creation()
        self.form.subject_input.setText("Outside the queue")
        self.form.submit()
        self.idle()
        self.assertEqual(self.state(), before)
        self.assertEqual(self.ws.model.rowCount(), 0)
        self.assertEqual(self.ws.details.ticket.subject, "Outside the queue")

    def test_failed_create_preserves_all_fields_and_retry_writes_once(self):
        self.ws.begin_creation()
        self.form.ticket_number_input.setText("CUSTOM-050")
        self.form.subject_input.setText("Retry subject")
        self.form.description_input.setPlainText("Multi\nline")
        self.form.priority_input.setCurrentIndex(2)
        self.form.ticket_type_input.setCurrentIndex(1)
        with patch.object(self.service, "create_ticket", side_effect=RuntimeError("private detail")):
            self.form.submit()
            self.idle()
        self.assertTrue(self.ws.creating)
        self.assertEqual(self.form.ticket_number_input.text(), "CUSTOM-050")
        self.assertEqual(self.form.description_input.toPlainText(), "Multi\nline")
        self.assertEqual(self.form.priority_input.currentData(), "HIGH")
        self.assertEqual(self.form.ticket_type_input.currentData(), "SERVICE_REQUEST")
        self.assertNotIn("private", self.form.form_error.text())
        self.form.submit()
        self.idle()
        self.assertEqual(len(self.service.list_tickets()), 2)

    def test_committed_detail_and_queue_failure_recovers_by_read_without_recreation(self):
        self.ws.begin_creation()
        self.form.subject_input.setText("Committed creation")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private")), \
             patch.object(self.service, "list_tickets", side_effect=RuntimeError("private")):
            self.form.submit()
            self.idle()
        self.assertIn("Ticket created successfully", self.ws.feedback.text())
        self.assertNotIn("private", self.ws.feedback.text())
        self.assertIsNone(self.ws.details)
        self.assertTrue(self.ws.retry_created_button.isVisible())
        self.assertEqual(self.form.subject_input.text(), "")
        with patch.object(self.service, "create_ticket", side_effect=AssertionError("No recreation")):
            self.ws.retry_created_button.click()
            self.idle()
        self.assertEqual(self.ws.details.ticket.subject, "Committed creation")
        self.assertEqual(len(self.service.list_tickets()), 2)
        self.assertFalse(self.ws.retry_created_button.isVisible())

    def test_committed_queue_failure_refresh_is_read_only(self):
        self.ws.begin_creation()
        self.form.subject_input.setText("Queue read failure")
        with patch.object(self.service, "list_tickets", side_effect=RuntimeError("private")):
            self.form.submit()
            self.idle()
        self.assertIn("Ticket created successfully", self.ws.feedback.text())
        self.assertIn("Use Refresh", self.ws.feedback.text())
        self.assertEqual(self.ws.details.ticket.subject, "Queue read failure")
        self.ws.refresh_button.click()
        self.idle()
        self.assertEqual(self.ws.model.rowCount(), 2)

    def _prepare_created_ticket_recovery_with_note_draft(self):
        self.assertTrue(self.ws.begin_creation())
        self.form.subject_input.setText("Committed recovery ticket")
        with patch.object(self.service, "get_ticket_details", side_effect=RuntimeError("private")):
            self.form.submit()
            self.idle()
        self.assertIsNone(self.ws.details)
        created_id = self.ws._created_ticket_id
        self.assertIsNotNone(created_id)
        self.ws.open_ticket(self.old.ticket_id)
        self.idle()
        self.ws.note_input.setPlainText("Keep this unsaved note")
        self.assertTrue(self.ws.retry_created_button.isEnabled())
        return created_id

    def test_cancelled_recovery_discard_releases_pending_without_dispatch_or_draft_loss(self):
        created_id = self._prepare_created_ticket_recovery_with_note_draft()
        before = self.path.read_bytes()
        try:
            with patch.object(self.window.runner, "submit", wraps=self.window.runner.submit) as dispatch, \
                 patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
                self.ws.retry_created_button.click()
                prompt.assert_called_once()
                dispatch.assert_not_called()
            self.assertFalse(self.window.runner.busy)
            self.assertFalse(self.ws.creation_pending)
            self.assertEqual(self.ws.details.ticket.ticket_id, self.old.ticket_id)
            self.assertEqual(self.ws.note_input.toPlainText(), "Keep this unsaved note")
            self.assertTrue(self.ws.note_input.isEnabled())
            self.assertTrue(self.ws.note_type.isEnabled())
            self.assertTrue(self.ws.add_note_button.isEnabled())
            self.assertTrue(self.window.pages.isEnabled())
            self.assertTrue(self.window.tickets_action.isEnabled())
            self.assertTrue(self.ws.retry_created_button.isEnabled())
            self.assertEqual(self.ws._created_ticket_id, created_id)
            with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as close_prompt:
                self.assertFalse(self.window.close())
                close_prompt.assert_called_once()  # Draft protection is reached; no phantom-operation block.
            self.window.show_tickets()
            self.idle()
            with patch.object(self.window.runner, "submit", wraps=self.window.runner.submit) as dispatch, \
                 patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
                self.ws.retry_created_button.click()
                dispatch.assert_not_called()
            self.assertFalse(self.ws.creation_pending)
            self.assertEqual(self.ws.note_input.toPlainText(), "Keep this unsaved note")
            self.assertEqual(self.path.read_bytes(), before)
            self.ws._clear_drafts()
            self.assertTrue(self.window.close())
        finally:
            # A failing pre-fix assertion must not strand this isolated test fixture.
            if not self.window.runner.busy:
                self.ws._creation_pending = False
                self.ws.creation_pending_changed.emit(False)

    def test_accepted_recovery_discard_keeps_pending_through_single_reopen_and_refresh(self):
        created_id = self._prepare_created_ticket_recovery_with_note_draft()
        before = self.path.read_bytes()
        gate = threading.Event()
        original_read = self.service.get_ticket_details

        def held_read(ticket_id):
            if not gate.wait(5):
                raise RuntimeError("Recovery read gate timed out")
            return original_read(ticket_id)

        with patch.object(self.service, "get_ticket_details", side_effect=held_read) as read, \
             patch.object(self.service, "create_ticket", side_effect=AssertionError("Recovery must not create")), \
             patch.object(self.window.runner, "submit", wraps=self.window.runner.submit) as dispatch, \
             patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard) as prompt:
            try:
                self.ws.retry_created_button.click()
                prompt.assert_called_once()
                self.assertTrue(self.window.runner.busy)
                self.assertTrue(self.ws.creation_pending)
                self.assertFalse(self.window.pages.isEnabled())
                self.ws._open_created_ticket()
                self.ws.retry_created_button.click()
                self.assertEqual(dispatch.call_count, 1)
            finally:
                gate.set()
                self.idle()
            read.assert_called_once_with(created_id)
            self.assertEqual(dispatch.call_count, 2)  # One authoritative reopen, then one queue read.
        self.assertFalse(self.ws.creation_pending)
        self.assertEqual(self.ws.details, self.service.get_ticket_details(created_id))
        self.assertEqual(self.ws.note_input.toPlainText(), "")
        self.assertTrue(self.ws.note_input.isEnabled())
        self.assertTrue(self.window.pages.isEnabled())
        self.assertFalse(self.ws.retry_created_button.isVisible())
        self.assertEqual(len(self.service.list_tickets()), 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_callback_gaps_block_mode_switch_duplicate_create_and_close(self):
        self.ws.begin_creation()
        self.form.subject_input.setText("Once across callbacks")
        observed = []
        def attempt(busy):
            if busy or not self.ws.creation_pending:
                return
            observed.append(True)
            self.assertFalse(self.window.pages.isEnabled())
            self.assertFalse(self.ws.new_ticket_button.isEnabled())
            self.assertFalse(self.ws.cancel_creation())
            self.assertFalse(self.ws.begin_creation())
            self.form.submit()
            self.window.show_new_ticket()
            self.window.show_scripts()
            self.ws.open_ticket(self.old.ticket_id)
            self.assertFalse(self.window.close())
        self.window.runner.busy_changed.connect(attempt)
        self.form.submit()
        self.idle()
        self.window.runner.busy_changed.disconnect(attempt)
        self.assertEqual(len(observed), 3)
        self.assertEqual(len(self.service.list_tickets()), 2)
        self.assertEqual(self.ws.details.ticket.subject, "Once across callbacks")

    def test_obsolete_detail_and_queue_callbacks_cannot_replace_form(self):
        callbacks = []
        with patch.object(self.window.runner, "submit", side_effect=lambda work, ok, fail: callbacks.append((ok, fail)) or True):
            self.ws.open_ticket(self.old.ticket_id)
            self.ws.refresh_list()
            self.ws.ticket_number_input.setText(self.old.ticket_number)
            self.ws.open_ticket_by_number()
            self.ws.begin_creation()
        before = self.ws.feedback.text()
        callbacks[0][0](self.service.get_ticket_details(self.old.ticket_id))
        callbacks[0][1](RuntimeError("stale"))
        callbacks[1][0](self.service.list_tickets())
        callbacks[1][1](RuntimeError("stale"))
        callbacks[2][0](self.service.get_ticket_details(self.old.ticket_id))
        callbacks[2][1](RuntimeError("stale"))
        self.assertTrue(self.ws.creating)
        self.assertIsNone(self.ws.details)
        self.assertEqual(self.ws.feedback.text(), before)
        self.assertIs(self.ws.detail_stack.currentWidget(), self.ws.creation_panel)

    def test_status_callback_gaps_protect_creation_and_release_after_owned_refresh(self):
        observed = []
        self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("OPEN"))
        self.ws.reason_input.setText("Captured reason")
        def attempt(busy):
            if busy or not self.ws.status_pending:
                return
            observed.append(True)
            self.assertFalse(self.ws.new_ticket_button.isEnabled())
            self.assertFalse(self.ws.begin_creation())
            self.assertFalse(self.window.close())
            self.ws.add_note()
            self.ws.change_status()
        self.window.runner.busy_changed.connect(attempt)
        self.ws.change_status_button.click()
        self.idle()
        self.window.runner.busy_changed.disconnect(attempt)
        self.assertEqual(len(observed), 3)
        self.assertEqual(self.ws.details.ticket.status, "OPEN")
        self.assertTrue(self.ws.new_ticket_button.isEnabled())
        self.assertTrue(self.ws.note_input.isEnabled())
        self.assertEqual(len(self.repo.list_status_history(self.old.ticket_id)), 2)
        self.assertEqual(self.repo.list_notes(self.old.ticket_id), ())

    def test_failed_status_and_rejected_dispatch_preserve_draft_and_release_creation_guard(self):
        self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("OPEN"))
        self.ws.reason_input.setText("Keep reason")
        with patch.object(self.service, "change_status", side_effect=RuntimeError("private")):
            self.ws.change_status()
            self.idle()
        self.assertEqual(self.ws.reason_input.text(), "Keep reason")
        self.assertFalse(self.ws.status_pending)
        self.assertTrue(self.ws.new_ticket_button.isEnabled())
        with patch.object(self.window.runner, "submit", return_value=False):
            self.ws.change_status()
        self.assertFalse(self.ws.status_pending)
        self.assertEqual(self.ws.reason_input.text(), "Keep reason")
