"""Quick company UI validation, cancellation and draft preservation."""

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
from f7hub.services.company_service import CompanyCreationError
from f7hub.services.ticket_reference_service import TicketReferenceOption


class QuickCompanyDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = Mock()
        self.service.create_company.return_value = SimpleNamespace(company_id=20, name="Fabrikam Demo Systems")
        self.references = Mock()
        self.references.list_active_companies.return_value = (TicketReferenceOption(10, "Northwind Field Services"),)
        self.references.list_active_ticket_categories.return_value = (TicketReferenceOption(31, "Networking"),)
        self.references.list_active_contacts_for_company.side_effect = lambda company_id: (
            (TicketReferenceOption(11, "Alice Example"),) if company_id == 10 else ()
        )
        self.runner = ServiceTaskRunner()
        self.form = TicketCreateWidget(Mock(), reference_service=self.references,
                                       company_service=self.service, task_runner=self.runner)
        self.form.show()
        self.wait_idle()
        self.form.company_input.setCurrentIndex(1)
        self.wait_idle()
        self.form.contact_input.setCurrentIndex(1)
        self.form.category_input.setCurrentIndex(1)
        self.form.ticket_number_input.setText("SYNTHETIC-008")
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
        if self.form._company_dialog is not None:
            self.form._company_dialog.reject()
        self.form.close()
        self.form.deleteLater()
        self.runner.deleteLater()
        self.app.processEvents()

    def draft(self):
        return (self.form.ticket_number_input.text(), self.form.subject_input.text(),
                self.form.description_input.toPlainText(), self.form.ticket_type_input.currentData(),
                self.form.priority_input.currentData(), self.form.category_input.currentData())

    def open_dialog(self):
        self.assertTrue(self.form.add_company_button.isVisible())
        QTest.mouseClick(self.form.add_company_button, Qt.MouseButton.LeftButton)
        self.app.processEvents()
        dialog = self.form._company_dialog
        self.assertTrue(dialog.isVisible())
        self.assertTrue(dialog.isModal())
        return dialog

    def prepare_success(self):
        self.references.list_active_companies.return_value = (
            TicketReferenceOption(20, "Fabrikam Demo Systems"), TicketReferenceOption(10, "Northwind Field Services"),
        )

    def test_cancel_preserves_draft_and_references_without_creation(self):
        dialog = self.open_dialog()
        dialog.name_input.setText("Contoso Test Support")
        QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
        self.assertIsNone(self.form._company_dialog)
        self.service.create_company.assert_not_called()
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.company_input.currentData(), 10)
        self.assertEqual(self.form.contact_input.currentData(), 11)

    def test_escape_and_titlebar_close_perform_no_write(self):
        for close in (lambda dialog: QTest.keyClick(dialog, Qt.Key.Key_Escape), lambda dialog: dialog.close()):
            dialog = self.open_dialog()
            dialog.name_input.setText("Contoso Test Support")
            close(dialog)
            self.assertIsNone(self.form._company_dialog)
            self.assertEqual(self.draft(), self.original_draft)
        self.service.create_company.assert_not_called()

    def test_enter_requires_nonblank_name(self):
        dialog = self.open_dialog()
        for value in ("", " \t "):
            dialog.name_input.setText(value)
            QTest.keyClick(dialog.name_input, Qt.Key.Key_Return)
            self.assertIn("required", dialog.feedback.text())
            self.assertTrue(dialog.isVisible())
        self.service.create_company.assert_not_called()

    def test_success_selects_company_clears_contact_preserves_every_draft_field(self):
        self.prepare_success()
        categories_before = self.references.list_active_ticket_categories.call_count
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        QTest.keyClick(dialog.name_input, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertIsNone(self.form._company_dialog)
        self.assertEqual(self.form.company_input.currentData(), 20)
        self.assertEqual(self.form.company_input.currentText(), "Fabrikam Demo Systems")
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.form.contact_input.count(), 1)
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.references.list_active_ticket_categories.call_count, categories_before)
        self.references.list_active_contacts_for_company.assert_called_with(20)
        self.assertEqual([self.form.company_input.itemData(i) for i in range(3)], [None, 20, 10])
        self.assertTrue(self.form.add_company_button.isEnabled())

    def test_creation_failure_preserves_input_and_allows_retry(self):
        self.service.create_company.side_effect = CompanyCreationError("Could not create the company.")
        dialog = self.open_dialog()
        dialog.name_input.setText("  Fabrikam Demo Systems  ")
        dialog.create_button.click()
        self.wait_idle()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.name_input.text(), "  Fabrikam Demo Systems  ")
        self.assertTrue(dialog.create_button.isEnabled())
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.contact_input.currentData(), 11)
        self.service.create_company.side_effect = None
        self.prepare_success()
        dialog.create_button.click()
        self.wait_idle()
        self.assertEqual(self.form.company_input.currentData(), 20)

    def test_unexpected_error_is_not_exposed(self):
        self.service.create_company.side_effect = RuntimeError("private database path")
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        dialog.create_button.click()
        self.wait_idle()
        self.assertNotIn("private", dialog.feedback.text())
        self.assertIn("preserved", dialog.feedback.text())

    def test_postcommit_company_refresh_failure_retries_without_recreation(self):
        self.references.list_active_companies.side_effect = RuntimeError("private database path")
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        dialog.create_button.click()
        self.wait_idle()
        self.assertIsNone(self.form._company_dialog)
        self.assertIn("Company created successfully", self.form.reference_feedback.text())
        self.assertNotIn("private", self.form.reference_feedback.text())
        self.assertFalse(self.form.add_company_button.isEnabled())
        self.assertIsNone(self.form.contact_input.currentData())
        self.form.submit()
        self.form._ticket_service.create_ticket.assert_not_called()
        self.assertEqual(self.draft(), self.original_draft)
        self.references.list_active_companies.side_effect = None
        self.prepare_success()
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.assertEqual(self.form.company_input.currentData(), 20)
        self.service.create_company.assert_called_once()
        self.assertEqual(self.draft(), self.original_draft)

    def test_postcommit_contact_failure_keeps_company_selected_and_truthful_success(self):
        self.prepare_success()
        self.references.list_active_contacts_for_company.side_effect = RuntimeError("private")
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        dialog.create_button.click()
        self.wait_idle()
        self.assertEqual(self.form.company_input.currentData(), 20)
        self.assertIn("Company created successfully", self.form.status_label.text())
        self.assertIn("Could not load contacts", self.form.reference_feedback.text())
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.draft(), self.original_draft)
        self.references.list_active_contacts_for_company.side_effect = None
        self.references.list_active_contacts_for_company.return_value = ()
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.service.create_company.assert_called_once()
        self.assertEqual(self.form.company_input.currentData(), 20)
