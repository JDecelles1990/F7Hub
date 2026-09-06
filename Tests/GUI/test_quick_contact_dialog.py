"""Quick contact UI validation, cancellation and draft preservation."""

import os
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.ticket_create_widget import TicketCreateWidget
from f7hub.services.contact_service import ContactCreationError
from f7hub.services.ticket_reference_service import TicketReferenceOption


class QuickContactDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = Mock()
        self.service.create_contact.return_value = SimpleNamespace(company_id=10, contact_id=20, display_name="Bob Example")
        self.references = Mock()
        self.references.list_active_companies.return_value = (TicketReferenceOption(10, "Northwind Field Services"),)
        self.references.list_active_ticket_categories.return_value = (TicketReferenceOption(31, "Networking"),)
        self.references.list_active_contacts_for_company.side_effect = lambda company_id: (
            (TicketReferenceOption(11, "Alice Example"),) if company_id == 10 else ()
        )
        self.runner = ServiceTaskRunner()
        self.form = TicketCreateWidget(Mock(), reference_service=self.references,
                                       contact_service=self.service, task_runner=self.runner)
        self.form.show()
        self.wait_idle()
        self.form.company_input.setCurrentIndex(1)
        self.wait_idle()
        self.form.contact_input.setCurrentIndex(1)
        self.form.category_input.setCurrentIndex(1)
        self.form.ticket_number_input.setText("SYNTHETIC-009")
        self.form.subject_input.setText("Synthetic subject")
        self.form.description_input.setPlainText("Synthetic description")
        self.form.ticket_type_input.setCurrentIndex(1)
        self.form.priority_input.setCurrentIndex(2)
        self.original_draft = self.draft()

    def wait_idle(self):
        self.app.processEvents()
        deadline = time.monotonic() + 5
        while self.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.runner.busy)

    def tearDown(self):
        self.wait_idle()
        if self.form._contact_dialog is not None:
            self.form._contact_dialog.reject()
        self.form.close()
        self.form.deleteLater()
        self.runner.deleteLater()
        self.app.processEvents()

    def draft(self):
        return (self.form.ticket_number_input.text(), self.form.subject_input.text(),
                self.form.description_input.toPlainText(), self.form.ticket_type_input.currentData(),
                self.form.priority_input.currentData(), self.form.category_input.currentData())

    def open_dialog(self):
        self.assertTrue(self.form.add_contact_button.isVisible())
        QTest.mouseClick(self.form.add_contact_button, Qt.MouseButton.LeftButton)
        self.app.processEvents()
        dialog = self.form._contact_dialog
        self.assertTrue(dialog.isVisible())
        self.assertTrue(dialog.isModal())
        return dialog

    def prepare_success(self):
        self.references.list_active_contacts_for_company.side_effect = None
        self.references.list_active_contacts_for_company.return_value = (
            TicketReferenceOption(11, "Alice Example"), TicketReferenceOption(20, "Bob Example"),
        )

    def test_unavailable_without_company_and_available_after_selection(self):
        self.form.company_input.setCurrentIndex(0)
        self.assertFalse(self.form.add_contact_button.isEnabled())
        self.form.open_contact_dialog()
        self.assertIsNone(self.form._contact_dialog)
        self.form.company_input.setCurrentIndex(1)
        self.wait_idle()
        self.assertTrue(self.form.add_contact_button.isEnabled())

    def test_cancel_escape_and_close_preserve_draft_without_write(self):
        for close in (lambda d: d.cancel_button.click(), lambda d: QTest.keyClick(d, Qt.Key.Key_Escape), lambda d: d.close()):
            dialog = self.open_dialog()
            dialog.name_input.setText("Bob Example")
            dialog.email_input.setText("bob@example.invalid")
            close(dialog)
            self.assertIsNone(self.form._contact_dialog)
            self.assertEqual(self.draft(), self.original_draft)
            self.assertEqual(self.form.company_input.currentData(), 10)
            self.assertEqual(self.form.contact_input.currentData(), 11)
        self.service.create_contact.assert_not_called()

    def test_enter_rejects_blank_name(self):
        dialog = self.open_dialog()
        for name in ("", "   "):
            dialog.name_input.setText(name)
            QTest.keyClick(dialog.name_input, Qt.Key.Key_Return)
            self.assertIn("required", dialog.feedback.text())
            self.assertTrue(dialog.isVisible())
        self.service.create_contact.assert_not_called()

    def test_success_selects_contact_preserves_all_draft_fields_and_company(self):
        self.prepare_success()
        category_calls = self.references.list_active_ticket_categories.call_count
        company_calls = self.references.list_active_companies.call_count
        dialog = self.open_dialog()
        dialog.name_input.setText(" Bob Example ")
        dialog.email_input.setText(" bob@example.invalid ")
        dialog.create_button.click()
        self.wait_idle()
        self.assertIsNone(self.form._contact_dialog)
        self.service.create_contact.assert_called_once_with(company_id=10, display_name=" Bob Example ", email=" bob@example.invalid ")
        self.assertEqual(self.form.company_input.currentData(), 10)
        self.assertEqual(self.form.contact_input.currentData(), 20)
        self.assertEqual(self.form.contact_input.currentText(), "Bob Example")
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.references.list_active_ticket_categories.call_count, category_calls)
        self.assertEqual(self.references.list_active_companies.call_count, company_calls)

    def test_failure_preserves_inputs_and_safe_retry(self):
        self.service.create_contact.side_effect = ContactCreationError("Could not create the contact.")
        dialog = self.open_dialog()
        dialog.name_input.setText("Bob Example")
        dialog.email_input.setText("bob@example.invalid")
        dialog.create_button.click()
        self.wait_idle()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.name_input.text(), "Bob Example")
        self.assertEqual(dialog.email_input.text(), "bob@example.invalid")
        self.assertTrue(dialog.create_button.isEnabled())
        self.assertEqual(self.draft(), self.original_draft)
        self.service.create_contact.side_effect = None
        self.prepare_success()
        dialog.create_button.click()
        self.wait_idle()
        self.assertEqual(self.form.contact_input.currentData(), 20)

    def test_unexpected_error_not_exposed(self):
        self.service.create_contact.side_effect = RuntimeError("private path")
        dialog = self.open_dialog()
        dialog.name_input.setText("Bob Example")
        dialog.create_button.click()
        self.wait_idle()
        self.assertNotIn("private", dialog.feedback.text())
        self.assertIn("preserved", dialog.feedback.text())

    def test_postcommit_failure_locks_company_and_retries_only_contacts(self):
        self.references.list_active_contacts_for_company.side_effect = RuntimeError("private")
        company_calls = self.references.list_active_companies.call_count
        category_calls = self.references.list_active_ticket_categories.call_count
        dialog = self.open_dialog()
        dialog.name_input.setText("Bob Example")
        dialog.create_button.click()
        self.wait_idle()
        self.assertIsNone(self.form._contact_dialog)
        self.assertIn("Contact created successfully", self.form.reference_feedback.text())
        self.assertNotIn("private", self.form.reference_feedback.text())
        self.assertEqual(self.form._pending_contact.contact_id, 20)
        self.assertFalse(self.form.company_input.isEnabled())
        self.assertFalse(self.form.add_company_button.isEnabled())
        self.assertFalse(self.form.add_contact_button.isEnabled())
        self.form.company_input.setCurrentIndex(0)
        self.assertEqual(self.form.company_input.currentData(), 10)
        self.form.open_contact_dialog()
        self.assertIsNone(self.form._contact_dialog)
        self.form.submit()
        self.form._ticket_service.create_ticket.assert_not_called()
        self.prepare_success()
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.service.create_contact.assert_called_once()
        self.assertEqual(self.form.contact_input.currentData(), 20)
        self.assertTrue(self.form.company_input.isEnabled())
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.references.list_active_companies.call_count, company_calls)
        self.assertEqual(self.references.list_active_ticket_categories.call_count, category_calls)

    def test_busy_runner_disables_add_contact(self):
        import threading
        gate = threading.Event()
        try:
            self.runner.submit(lambda: gate.wait(3), lambda _: None, lambda _: None)
            self.assertFalse(self.form.add_contact_button.isEnabled())
            self.form.open_contact_dialog()
            self.assertIsNone(self.form._contact_dialog)
        finally:
            gate.set()
            self.wait_idle()
        self.assertTrue(self.form.add_contact_button.isEnabled())

    def test_pending_company_disables_add_contact(self):
        self.form._pending_company_id = 30
        self.form.open_contact_dialog()
        self.assertFalse(self.form.add_contact_button.isEnabled())
        self.assertIsNone(self.form._contact_dialog)

    def test_committed_contact_no_longer_available_releases_recovery(self):
        dialog = self.open_dialog()
        dialog.name_input.setText("Bob Example")
        dialog.create_button.click()
        self.wait_idle()
        self.assertIsNone(self.form._pending_contact)
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertIn("no longer available", self.form.reference_feedback.text())
        self.assertTrue(self.form.company_input.isEnabled())
        self.service.create_contact.assert_called_once()
