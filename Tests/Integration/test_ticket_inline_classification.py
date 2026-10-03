"""Inline classification drafts, atomic saves and read-only recovery on real workers."""

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from f7hub.gui.main_window import MainWindow
from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import TicketService, TicketValidationError, TICKET_PRIORITIES, TICKET_TYPES


class InlineClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "inline.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repo = TicketRepository(self.path)
        self.service = TicketService(self.repo)
        self.ticket = self.service.create_ticket(subject="Synthetic printer", priority="HIGH")
        self.other = self.service.create_ticket(subject="Other ticket", priority="HIGH")
        self.window = MainWindow(self.service)
        self.ws = self.window.workspace
        self.window.show()
        self.idle()
        self.window.show_tickets()
        self.idle()
        self.ws.open_ticket(self.ticket.ticket_id)
        self.idle()

    def tearDown(self):
        self.idle()
        self.ws._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def idle(self):
        deadline = time.monotonic() + 5
        while (self.window.runner.busy or self.ws.classification_pending or self.ws.note_pending
               or self.ws.creation_pending or self.ws.status_pending) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy or self.ws.classification_pending or self.ws.note_pending
                         or self.ws.creation_pending or self.ws.status_pending, "Operation did not finish")

    def draft(self, priority="MEDIUM", ticket_type="TASK"):
        self.ws.priority_input.setCurrentIndex(self.ws.priority_input.findData(priority))
        self.ws.type_input.setCurrentIndex(self.ws.type_input.findData(ticket_type))

    def state(self):
        return (self.ws.details.ticket.ticket_id, self.ws.priority_input.currentData(),
                self.ws.type_input.currentData(), self.ws.note_input.toPlainText(),
                self.ws.reason_input.text(), self.ws.resolution_input.toPlainText(),
                self.ws._classification_baseline)

    def test_loaded_values_accessibility_dirty_revert_and_zero_write_selection(self):
        self.assertEqual(self.ws.priority_input.currentData(), "HIGH")
        self.assertEqual(self.ws.type_input.currentData(), "INCIDENT")
        self.assertEqual({self.ws.priority_input.itemData(i) for i in range(self.ws.priority_input.count())}, TICKET_PRIORITIES)
        self.assertEqual([self.ws.type_input.itemData(i) for i in range(self.ws.type_input.count())], list(TICKET_TYPES))
        self.assertEqual(self.ws.priority_input.accessibleName(), "Ticket priority")
        self.assertEqual(self.ws.type_input.accessibleName(), "Ticket type")
        self.assertEqual(self.ws.apply_properties_button.accessibleName(), "Apply ticket changes")
        with patch.object(self.service, "update_ticket_classification", wraps=self.service.update_ticket_classification) as update:
            self.assertFalse(self.ws.apply_properties_button.isEnabled())
            for priority, kind, dirty in (("LOW", "INCIDENT", True), ("HIGH", "TASK", True),
                                          ("LOW", "TASK", True), ("HIGH", "INCIDENT", False)):
                self.draft(priority, kind)
                self.assertEqual(self.ws.apply_properties_button.isEnabled(), dirty)
            self.ws.apply_classification()
            update.assert_not_called()
        self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), self.ticket)
        texts = [button.text() for button in self.ws.findChildren(QPushButton)]
        self.assertNotIn("Edit priority", texts)
        self.assertNotIn("Edit type", texts)
        self.assertIn("Edit subject", texts)
        self.assertIn("Edit description", texts)

    def test_priority_only_type_only_and_combined_saves(self):
        for priority, kind in (("LOW", "INCIDENT"), ("LOW", "PROBLEM"), ("CRITICAL", "TASK")):
            with self.subTest(priority=priority, kind=kind):
                self.draft(priority, kind)
                self.ws.apply_properties_button.click()
                self.idle()
                result = self.repo.get_ticket(self.ticket.ticket_id)
                self.assertEqual((result.priority, result.ticket_type), (priority, kind))
                self.assertEqual(self.ws.details.ticket, result)
                self.assertEqual(self.ws._classification_baseline, result)
                self.assertFalse(self.ws.apply_properties_button.isEnabled())
                self.assertIn("were saved", self.ws.feedback.text())

    def test_save_does_not_save_or_clear_note_status_or_resolution_drafts(self):
        self.draft()
        self.ws.note_input.setPlainText("Unsaved note")
        self.ws.reason_input.setText("Unsaved reason")
        self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("RESOLVED"))
        self.ws.resolution_input.setPlainText("Unsaved resolution")
        self.ws.apply_classification()
        self.idle()
        self.assertEqual(self.repo.list_notes(self.ticket.ticket_id), ())
        self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id).status, "NEW")
        self.assertEqual(self.ws.note_input.toPlainText(), "Unsaved note")
        self.assertEqual(self.ws.reason_input.text(), "Unsaved reason")
        self.assertEqual(self.ws.resolution_input.toPlainText(), "Unsaved resolution")
        self.assertEqual(self.ws.status_input.currentData(), "RESOLVED")

    def test_failures_preserve_drafts_and_baseline_and_enable_retry(self):
        for error in (TicketValidationError("Invalid classification"), RuntimeError("private detail")):
            with self.subTest(error=type(error).__name__):
                self.draft()
                before = self.state()
                with patch.object(self.service, "update_ticket_classification", side_effect=error):
                    self.ws.apply_classification()
                    self.idle()
                self.assertEqual(self.state(), before)
                self.assertTrue(self.ws.apply_properties_button.isEnabled())
                self.assertNotIn("private detail", self.ws.feedback.text())
                self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), self.ticket)

    def test_external_stale_edit_is_fail_closed_with_reload_guidance(self):
        self.draft()
        before = self.state()
        changed = self.service.update_ticket_priority(self.ticket.ticket_id, expected_priority="HIGH",
                                                      expected_updated_at=self.ticket.updated_at, priority="LOW")
        self.ws.apply_classification()
        self.idle()
        self.assertEqual(self.state(), before)
        self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), changed)
        self.assertIn("Reload", self.ws.feedback.text())
        self.assertTrue(self.ws.apply_properties_button.isEnabled())

    def test_quick_note_and_status_mutations_preserve_classification_token_then_reject_apply(self):
        for operation in ("note", "status"):
            with self.subTest(operation=operation):
                self.ws._clear_drafts()
                self.ws.open_ticket(self.ticket.ticket_id)
                self.idle()
                baseline = self.ws._classification_baseline
                self.draft()
                QTest.qWait(2)
                if operation == "note":
                    self.ws.note_input.setPlainText("Only a note")
                    self.ws.note_input.setFocus()
                    QTest.keyClick(self.ws.note_input, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
                else:
                    self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("OPEN"))
                    self.ws.change_status()
                self.idle()
                persisted = self.repo.get_ticket(self.ticket.ticket_id)
                self.assertNotEqual(persisted.updated_at, baseline.updated_at)
                self.assertEqual((persisted.priority, persisted.ticket_type), ("HIGH", "INCIDENT"))
                self.assertEqual(self.ws._classification_baseline, baseline)
                self.assertEqual((self.ws.priority_input.currentData(), self.ws.type_input.currentData()), ("MEDIUM", "TASK"))
                self.ws.apply_classification()
                self.idle()
                self.assertIn("Reload", self.ws.feedback.text())
                self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), persisted)
        self.assertEqual(len(self.repo.list_notes(self.ticket.ticket_id)), 1)

    def test_cancel_discard_for_every_existing_ticket_entry_and_reload_preserves_all_drafts(self):
        self.draft()
        self.ws.note_input.setPlainText("Keep note")
        self.ws.reason_input.setText("Keep reason")
        self.ws.resolution_input.setPlainText("Keep resolution")
        before = self.state()
        self.ws.ticket_number_input.setText(self.other.ticket_number)
        other_row = next(i for i,t in enumerate(self.ws.model.tickets) if t.ticket_id == self.other.ticket_id)
        self.ws.company_model.replace_tickets((self.other,))
        entries = (lambda: self.ws.open_ticket(self.other.ticket_id), self.ws.open_ticket_by_number,
                   lambda: self.ws._activate_row(self.ws.model.index(other_row, 0)),
                   lambda: self.ws._activate_company_row(self.ws.company_model.index(0, 0)),
                   self.ws.begin_creation, self.ws.reload_button.click, self.window.close)
        for enter in entries:
            with self.subTest(enter=enter), patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as question:
                enter()
                self.idle()
                question.assert_called_once()
                self.assertEqual(self.state(), before)
                self.assertFalse(self.ws.creating)
                self.assertTrue(self.window.isVisible())

    def test_accept_discard_switches_ticket_and_reload_resets_only_classification(self):
        self.draft()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.ws.open_ticket(self.other.ticket_id)
            self.idle()
        self.assertEqual(self.ws.details.ticket.ticket_id, self.other.ticket_id)
        self.assertFalse(self.ws.has_draft())
        self.draft()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.ws.reload_button.click()
            self.idle()
        self.assertEqual(self.ws.priority_input.currentData(), "HIGH")
        self.assertFalse(self.ws.apply_properties_button.isEnabled())

    def test_new_ticket_cannot_apply_to_previous_ticket_cancel_and_created_identity_restore(self):
        self.draft()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.ws.begin_creation()
        self.assertTrue(self.ws.creating)
        self.assertIsNone(self.ws.details)
        with patch.object(self.service, "update_ticket_classification") as update:
            self.ws.apply_classification()
            update.assert_not_called()
        self.assertFalse(self.ws.apply_properties_button.isEnabled())
        self.ws.cancel_creation()
        self.assertEqual(self.ws.details.ticket.ticket_id, self.ticket.ticket_id)
        self.assertEqual(self.ws.priority_input.currentData(), "HIGH")
        self.assertFalse(self.ws.apply_properties_button.isEnabled())
        self.ws.begin_creation()
        self.window.ticket_create_widget.subject_input.setText("Created identity")
        self.window.ticket_create_widget.save_button.click()
        self.idle()
        self.assertNotEqual(self.ws.details.ticket.ticket_id, self.ticket.ticket_id)
        self.assertEqual(self.ws._classification_baseline, self.ws.details.ticket)
        self.assertFalse(self.ws.apply_properties_button.isEnabled())

    def test_duplicate_navigation_close_and_callback_gap_blocked_until_completion(self):
        entered, release = threading.Event(), threading.Event()
        original = self.service.update_ticket_classification
        calls = []

        def delayed(*args, **kwargs):
            calls.append(kwargs)
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Test watchdog timeout")
            return original(*args, **kwargs)

        gaps = []

        def gap(busy):
            if busy or not self.ws.classification_pending:
                return
            gaps.append(True)
            self.assertFalse(self.window.pages.isEnabled())
            self.ws.apply_classification()
            self.ws.begin_creation()
            self.ws.open_ticket(self.other.ticket_id)
            self.ws.add_note()
            self.ws.change_status()
            self.window.close()
            self.assertEqual(self.ws.details.ticket.ticket_id, self.ticket.ticket_id)
            self.assertFalse(self.ws.creating)
            self.assertTrue(self.window.isVisible())

        self.window.runner.busy_changed.connect(gap)
        try:
            self.draft()
            with patch.object(self.service, "update_ticket_classification", side_effect=delayed):
                self.ws.apply_classification()
                self.assertTrue(entered.wait(1))
                self.ws.apply_classification()
                self.assertFalse(self.ws.priority_input.isEnabled())
                self.assertFalse(self.ws.type_input.isEnabled())
                self.assertFalse(self.ws.new_ticket_button.isEnabled())
                release.set()
                self.idle()
        finally:
            release.set()
            self.window.runner.busy_changed.disconnect(gap)
        self.assertEqual(len(calls), 1)
        self.assertGreaterEqual(len(gaps), 3)
        self.assertTrue(self.ws.new_ticket_button.isEnabled())

    def test_dispatch_rejection_and_exception_clear_pending_without_writes(self):
        for result in (False, RuntimeError("rejected")):
            self.draft()
            kwargs = dict(side_effect=result) if isinstance(result, Exception) else dict(return_value=result)
            with self.subTest(result=result), patch.object(self.window.runner, "submit", **kwargs):
                self.ws.apply_classification()
            self.assertFalse(self.ws.classification_pending)
            self.assertTrue(self.ws.apply_properties_button.isEnabled())
            self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), self.ticket)

    def test_priority_type_and_combined_filter_exit_preserve_search_filters_and_page(self):
        for priority_filter, type_filter, new_priority, new_type in (
            ("HIGH", None, "MEDIUM", "INCIDENT"), (None, "INCIDENT", "HIGH", "TASK"),
            ("HIGH", "INCIDENT", "LOW", "PROBLEM"),
        ):
            with self.subTest(priority_filter=priority_filter, type_filter=type_filter):
                current = self.repo.get_ticket(self.ticket.ticket_id)
                self.service.update_ticket_classification(current.ticket_id, expected_priority=current.priority,
                    expected_ticket_type=current.ticket_type, expected_updated_at=current.updated_at,
                    priority="HIGH", ticket_type="INCIDENT")
                self.ws.open_ticket(current.ticket_id)
                self.idle()
                self.ws.priority_filter.setCurrentIndex(self.ws.priority_filter.findData(priority_filter))
                self.idle()
                self.ws.type_filter.setCurrentIndex(self.ws.type_filter.findData(type_filter))
                self.idle()
                self.ws.subject_search_input.setText("Synthetic")
                self.ws.search_subjects()
                self.idle()
                self.ws.subject_search_input.setText("Unsubmitted search draft")
                self.draft(new_priority, new_type)
                self.ws.apply_classification()
                self.idle()
                self.assertEqual(self.ws.model.tickets, ())
                self.assertEqual(self.ws.priority_filter.currentData(), priority_filter)
                self.assertEqual(self.ws.type_filter.currentData(), type_filter)
                self.assertEqual(self.ws._subject_query, "Synthetic")
                self.assertEqual(self.ws.subject_search_input.text(), "Unsubmitted search draft")
                self.assertEqual(self.ws.details.ticket.ticket_id, current.ticket_id)
                self.assertIn("were saved", self.ws.feedback.text())

    def test_save_preserves_nonzero_page(self):
        self.ws.PAGE_SIZE = 1
        self.ws.refresh_list(offset=1)
        self.idle()
        self.draft()
        self.ws.apply_classification()
        self.idle()
        self.assertEqual(self.ws._offset, 1)
        self.assertEqual(self.ws.page_label.text(), "Page 2")
        self.assertEqual(self.ws.details.ticket.ticket_id, self.ticket.ticket_id)

    def test_committed_detail_and_queue_failures_have_truthful_read_only_recovery(self):
        for read in ("get_ticket_details", "list_tickets"):
            with self.subTest(read=read):
                destination = "LOW" if read == "get_ticket_details" else "MEDIUM"
                self.draft(destination, "TASK")
                with patch.object(self.service, "update_ticket_classification", wraps=self.service.update_ticket_classification) as mutation:
                    with patch.object(self.service, read, side_effect=RuntimeError("private")):
                        self.ws.apply_classification()
                        self.idle()
                    mutation.assert_called_once()
                    self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id).priority, destination)
                    self.assertIn("were saved", self.ws.feedback.text())
                    self.assertNotIn("private", self.ws.feedback.text())
                    self.assertFalse(self.ws.apply_properties_button.isEnabled())
                    self.ws.reload_button.click() if read == "get_ticket_details" else self.ws.refresh_button.click()
                    self.idle()
                    mutation.assert_called_once()
                self.assertEqual(self.ws.details.ticket.priority, destination)

    def test_postcommit_refresh_dispatch_rejection_clears_pending_and_disables_repeat(self):
        self.draft()
        original = self.window.runner.submit
        count = 0

        def submit(*args):
            nonlocal count
            count += 1
            return original(*args) if count == 1 else False

        with patch.object(self.window.runner, "submit", side_effect=submit):
            self.ws.apply_classification()
            self.idle()
        self.assertIn("were saved", self.ws.feedback.text())
        self.assertIn("Reload", self.ws.feedback.text())
        self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id).priority, "MEDIUM")
        self.assertFalse(self.ws.apply_properties_button.isEnabled())

    def test_obsolete_classification_callback_cannot_update_new_creation_mode(self):
        callbacks = []
        self.draft()
        with patch.object(self.window.runner, "submit", side_effect=lambda work, success, failure: callbacks.append((success, failure)) or True):
            self.ws.apply_classification()
        self.ws._creation_generation += 1  # Inject a superseded context at the callback boundary.
        self.ws.creating = True
        self.ws.details = None
        updated = self.service.update_ticket_classification(self.ticket.ticket_id, **dict(
            expected_priority="HIGH", expected_ticket_type="INCIDENT", expected_updated_at=self.ticket.updated_at,
            priority="MEDIUM", ticket_type="TASK"))
        callbacks[0][0](updated)
        self.assertFalse(self.ws.classification_pending)
        self.assertIsNone(self.ws.details)
        self.assertFalse(self.ws.apply_properties_button.isEnabled())
        self.ws.creating = False
        self.ws._display_details(self.service.get_ticket_details(self.ticket.ticket_id))

    def test_pending_clears_on_detail_or_queue_dispatch_exception_or_rejection(self):
        for rejected_call, exception in ((2, True), (3, True), (3, False)):
            with self.subTest(rejected_call=rejected_call, exception=exception):
                self.ws._clear_drafts()
                self.ws.open_ticket(self.ticket.ticket_id)
                self.idle()
                current = self.ws.details.ticket
                self.draft("LOW" if current.priority != "LOW" else "HIGH")
                original = self.window.runner.submit
                count = 0

                def submit(*args):
                    nonlocal count
                    count += 1
                    if count == rejected_call:
                        if exception:
                            raise RuntimeError("Synthetic dispatch failure")
                        return False
                    return original(*args)

                with patch.object(self.window.runner, "submit", side_effect=submit):
                    self.ws.apply_classification()
                    self.idle()
                self.assertIn("were saved", self.ws.feedback.text())
                self.assertFalse(self.ws.classification_pending)
                self.assertFalse(self.ws.apply_properties_button.isEnabled())

    def test_obsolete_postcommit_read_callbacks_clear_pending_without_overwriting_context(self):
        for read_stage, failed in ((2, False), (2, True), (3, False), (3, True)):
            with self.subTest(read_stage=read_stage, failed=failed):
                self.ws._clear_drafts()
                self.ws.open_ticket(self.ticket.ticket_id)
                self.idle()
                self.draft("LOW" if self.ws.details.ticket.priority != "LOW" else "HIGH")
                original = self.window.runner.submit
                callbacks = []
                count = 0

                def submit(work, success, failure):
                    nonlocal count
                    count += 1
                    if count == read_stage:
                        callbacks.append((work, success, failure))
                        return True
                    return original(work, success, failure)

                with patch.object(self.window.runner, "submit", side_effect=submit):
                    self.ws.apply_classification()
                    deadline = time.monotonic()+5
                    while not callbacks and time.monotonic()<deadline:
                        QTest.qWait(5)
                self.assertTrue(callbacks)
                self.ws._creation_generation += 1
                self.ws._display_details(self.service.get_ticket_details(self.other.ticket_id))
                old = self.state()
                work, success, failure = callbacks[0]
                failure(RuntimeError("obsolete")) if failed else success(work())
                self.assertFalse(self.ws.classification_pending)
                self.assertEqual(self.state(), old)

    def _assert_dialog_completion_restores_classification(self, editor, *, fail=False, close=False):
        for dirty in (False, True):
            with self.subTest(editor=editor, dirty=dirty):
                self.ws._clear_drafts()
                if dirty:
                    self.draft()
                baseline = self.ws._classification_baseline
                choices = (self.ws.priority_input.currentData(), self.ws.type_input.currentData())
                dialog = getattr(self.ws, "open_edit_" + editor)()
                if fail:
                    with patch.object(self.service, "update_ticket_" + editor,
                                      side_effect=TicketValidationError("Synthetic save failure")):
                        dialog.save_button.click()
                        self.idle()
                    self.assertTrue(dialog.isVisible())
                    self.assertTrue(dialog.save_button.isEnabled())
                    self.assertTrue(dialog.cancel_button.isEnabled())
                    self.assertFalse(self.ws.priority_input.isEnabled())
                    self.assertFalse(self.ws.type_input.isEnabled())
                    self.assertFalse(self.ws.apply_properties_button.isEnabled())
                    dialog.close() if close else dialog.cancel_button.click()
                else:
                    dialog.save_button.click()
                    self.idle()
                self.app.processEvents()
                self.assertIsNone(getattr(self.ws, "_edit_" + editor + "_dialog"))
                self.assertFalse(dialog.isVisible())
                self.assertFalse(self.window.runner.busy)
                self.assertFalse(self.ws.classification_pending or self.ws.note_pending
                                 or self.ws.status_pending or self.ws.creation_pending)
                self.assertTrue(self.ws.priority_input.isEnabled())
                self.assertTrue(self.ws.type_input.isEnabled())
                self.assertEqual(self.ws.apply_properties_button.isEnabled(), dirty)
                self.assertEqual((self.ws.priority_input.currentData(), self.ws.type_input.currentData()), choices)
                self.assertEqual(self.ws._classification_baseline, baseline)
                self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), self.ticket)
                self.assertTrue(self.ws.new_ticket_button.isEnabled())

    def test_subject_noop_completion(self):
        self._assert_dialog_completion_restores_classification("subject")

    def test_description_noop_completion(self):
        self._assert_dialog_completion_restores_classification("description")

    def test_subject_failed_save_then_cancel(self):
        self._assert_dialog_completion_restores_classification("subject", fail=True)

    def test_description_failed_save_then_cancel(self):
        self._assert_dialog_completion_restores_classification("description", fail=True)

    def test_failed_dialog_save_then_window_close_restores_inline_drafts(self):
        for editor in ("subject", "description"):
            self._assert_dialog_completion_restores_classification(editor, fail=True, close=True)

    def test_dialog_success_and_direct_cancel_preserve_inline_drafts(self):
        for editor in ("subject", "description"):
            for dirty in (False, True):
                for save in (False, True):
                    with self.subTest(editor=editor, dirty=dirty, save=save):
                        self.ws._clear_drafts()
                        self.ws.open_ticket(self.ticket.ticket_id)
                        self.idle()
                        if dirty:
                            self.draft()
                        baseline = self.ws._classification_baseline
                        choices = (self.ws.priority_input.currentData(), self.ws.type_input.currentData())
                        dialog = getattr(self.ws, "open_edit_" + editor)()
                        self.assertFalse(self.ws.priority_input.isEnabled())
                        self.assertFalse(self.ws.type_input.isEnabled())
                        if save:
                            value = ((getattr(self.ws.details.ticket, editor) or "") + " edited").strip()
                            field = getattr(dialog, editor + "_input")
                            field.setText(value) if editor == "subject" else field.setPlainText(value)
                            dialog.save_button.click()
                            self.idle()
                        else:
                            dialog.cancel_button.click()
                        persisted = self.repo.get_ticket(self.ticket.ticket_id)
                        self.assertIsNone(getattr(self.ws, "_edit_" + editor + "_dialog"))
                        self.assertTrue(self.ws.priority_input.isEnabled())
                        self.assertTrue(self.ws.type_input.isEnabled())
                        self.assertEqual(self.ws.apply_properties_button.isEnabled(), dirty)
                        self.assertEqual((self.ws.priority_input.currentData(), self.ws.type_input.currentData()), choices)
                        self.assertEqual(self.ws._classification_baseline, baseline if dirty else persisted)
                        if save:
                            self.assertEqual(getattr(persisted, editor), value)
                        else:
                            self.assertEqual(persisted, baseline)

    def test_dialog_close_does_not_bypass_other_classification_blockers(self):
        self.draft()
        for editor in ("subject", "description"):
            other_editor = "_edit_description_dialog" if editor == "subject" else "_edit_subject_dialog"
            blockers = ((self.ws, "classification_pending", True),
                        (self.ws, "status_pending", True),
                        (self.ws, "_note_pending", True),
                        (self.ws, "_creation_pending", True),
                        (self.ws, "creating", True),
                        (self.ws, "details", None),
                        (self.ws, other_editor, object()),
                        (self.window.runner, "_task", object()))
            for owner, attribute, value in blockers:
                with self.subTest(editor=editor, blocker=attribute):
                    dialog = getattr(self.ws, "open_edit_" + editor)()
                    with patch.object(owner, attribute, value):
                        dialog.cancel_button.click()
                        self.assertIsNone(getattr(self.ws, "_edit_" + editor + "_dialog"))
                        self.assertFalse(self.ws.priority_input.isEnabled())
                        self.assertFalse(self.ws.type_input.isEnabled())
                        self.assertFalse(self.ws.apply_properties_button.isEnabled())

    def test_classification_apply_is_blocked_while_subject_or_description_dialog_is_open(self):
        for open_dialog in (self.ws.open_edit_subject, self.ws.open_edit_description):
            self.draft()
            dialog = open_dialog()
            with patch.object(self.service, "update_ticket_classification") as update:
                self.ws.apply_classification()
                update.assert_not_called()
            dialog.reject()
            self.assertTrue(self.ws.priority_input.isEnabled())
            self.assertTrue(self.ws.type_input.isEnabled())
            self.assertTrue(self.ws.apply_properties_button.isEnabled())

    def test_expanded_resolution_and_inline_controls_fit_1000_by_700(self):
        self.window.resize(1000, 700)
        self.ws.status_input.setCurrentIndex(self.ws.status_input.findData("RESOLVED"))
        self.app.processEvents()
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        self.assertTrue(self.ws.resolution_input.isVisible())
        for widget in (self.ws.priority_input, self.ws.type_input, self.ws.apply_properties_button,
                       self.ws.resolution_input, self.ws.reload_button):
            self.assertTrue(self.window.rect().contains(widget.mapTo(self.window, widget.rect().bottomRight())))
