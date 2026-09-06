"""Reference selection and retry behavior without persistence."""

import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QEvent
from f7hub.gui.ticket_create_widget import TicketCreateWidget
from f7hub.services.ticket_reference_service import TicketReferenceOption


class TicketReferenceWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.references = Mock()
        self.references.list_active_ticket_categories.return_value = ()
        self.references.list_active_companies.return_value = (
            TicketReferenceOption(10, "Northwind Support Labs"),
            TicketReferenceOption(20, "Contoso Test Services"),
            TicketReferenceOption(30, "Empty Test Company"),
        )
        self.references.list_active_contacts_for_company.side_effect = lambda company_id: {
            10: (TicketReferenceOption(11, "Alice Example"),),
            20: (TicketReferenceOption(21, "Charlie Example"),), 30: (),
        }[company_id]
        self.service = Mock()
        self.service.create_ticket.return_value = SimpleNamespace(ticket_id=1, ticket_number="TKT-TEST")
        self.widget = TicketCreateWidget(self.service, reference_service=self.references)
        self.widget.show()
        self.app.processEvents()

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def test_initial_load_and_unselected_state(self):
        self.assertEqual(self.widget.company_input.count(), 4)
        self.assertEqual(self.widget.company_input.currentText(), "Not selected")
        self.assertIsNone(self.widget.contact_input.currentData())
        self.assertFalse(self.widget.contact_input.isEnabled())

    def test_category_population_and_id_submission(self):
        self.references.list_active_ticket_categories.return_value = (
            TicketReferenceOption(23, "Hardware"), TicketReferenceOption(31, "Networking"),
        )
        self.widget.refresh_categories_button.click()
        self.assertEqual(self.widget.category_input.count(), 3)
        self.assertEqual(self.widget.category_input.currentText(), "Not selected")
        self.assertIsNone(self.widget.category_input.currentData())
        self.widget.category_input.setCurrentIndex(2)
        self.widget.subject_input.setText("Synthetic ticket")
        self.widget.save_button.click()
        self.assertEqual(self.service.create_ticket.call_args.kwargs["category_id"], 31)

    def test_empty_categories_allow_optional_ticket(self):
        self.assertEqual(self.widget.category_input.count(), 1)
        self.assertIn("No active ticket categories", self.widget.category_feedback.text())
        self.widget.subject_input.setText("Without category")
        self.widget.save_button.click()
        self.assertIsNone(self.service.create_ticket.call_args.kwargs["category_id"])

    def test_category_failure_and_retry_preserve_draft_and_unrelated_choices(self):
        self.references.list_active_ticket_categories.return_value = (TicketReferenceOption(31, "Networking"),)
        self.widget.refresh_categories_button.click()
        self.widget.category_input.setCurrentIndex(1)
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.widget.subject_input.setText("Draft subject")
        self.widget.description_input.setPlainText("Draft description")
        self.references.list_active_companies.reset_mock()
        self.references.list_active_contacts_for_company.reset_mock()
        self.references.list_active_ticket_categories.side_effect = RuntimeError("private detail")
        self.widget.refresh_categories_button.click()
        self.assertIn("Refresh categories", self.widget.category_feedback.text())
        self.assertNotIn("private detail", self.widget.category_feedback.text())
        self.assertEqual(self.widget.category_input.currentData(), 31)
        self.assertEqual(self.widget.company_input.currentData(), 10)
        self.assertEqual(self.widget.contact_input.currentData(), 11)
        self.assertEqual(self.widget.subject_input.text(), "Draft subject")
        self.assertEqual(self.widget.description_input.toPlainText(), "Draft description")
        self.references.list_active_ticket_categories.side_effect = None
        self.widget.refresh_categories_button.click()
        self.assertEqual(self.widget.category_input.currentData(), 31)
        self.assertEqual(self.widget.category_feedback.text(), "Category is optional.")
        self.references.list_active_companies.assert_not_called()
        self.references.list_active_contacts_for_company.assert_not_called()

    def test_category_selection_survives_company_switch_and_full_refresh(self):
        self.references.list_active_ticket_categories.return_value = (TicketReferenceOption(31, "Networking"),)
        self.widget.refresh_categories_button.click()
        self.widget.category_input.setCurrentIndex(1)
        category_calls = self.references.list_active_ticket_categories.call_count
        self.widget.company_input.setCurrentIndex(1)
        self.widget.company_input.setCurrentIndex(2)
        self.assertEqual(self.references.list_active_ticket_categories.call_count, category_calls)
        self.widget.refresh_references_button.click()
        self.assertEqual(self.widget.category_input.currentData(), 31)

    def test_full_refresh_category_failure_still_loads_companies_and_contacts(self):
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.references.list_active_ticket_categories.side_effect = RuntimeError("private detail")
        self.widget.refresh_references_button.click()
        self.assertEqual(self.widget.company_input.currentData(), 10)
        self.assertEqual(self.widget.contact_input.currentData(), 11)
        self.assertIn("Could not load categories", self.widget.category_feedback.text())

    def test_refresh_removes_unavailable_category_selection(self):
        self.references.list_active_ticket_categories.return_value = (TicketReferenceOption(31, "Networking"),)
        self.widget.refresh_categories_button.click()
        self.widget.category_input.setCurrentIndex(1)
        self.references.list_active_ticket_categories.return_value = ()
        self.widget.refresh_categories_button.click()
        self.assertIsNone(self.widget.category_input.currentData())

    def test_destroy_before_deferred_initial_load_cancels_callback(self):
        references = Mock()
        widget = TicketCreateWidget(self.service, reference_service=references)
        widget.show()
        widget.deleteLater()
        QCoreApplication.sendPostedEvents(widget, QEvent.Type.DeferredDelete)
        self.app.processEvents()
        references.list_active_companies.assert_not_called()

    def test_company_switch_clears_old_contact_and_filters_choices(self):
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.assertEqual(self.widget.contact_input.currentData(), 11)
        self.widget.company_input.setCurrentIndex(2)
        self.assertIsNone(self.widget.contact_input.currentData())
        self.assertEqual(self.widget.contact_input.findData(11), -1)
        self.assertEqual(self.widget.contact_input.itemText(1), "Charlie Example")
        self.widget.company_input.setCurrentIndex(0)
        self.assertEqual(self.widget.contact_input.count(), 1)
        self.assertFalse(self.widget.contact_input.isEnabled())

    def test_empty_company_and_contact_states(self):
        self.widget.company_input.setCurrentIndex(3)
        self.assertIn("No active contacts", self.widget.reference_feedback.text())
        self.assertFalse(self.widget.contact_input.isEnabled())
        self.references.list_active_companies.return_value = ()
        self.widget.refresh_references_button.click()
        self.assertEqual(self.widget.company_input.count(), 1)
        self.assertIn("No active companies", self.widget.reference_feedback.text())
        self.widget.subject_input.setText("No references")
        self.widget.save_button.click()
        self.assertIsNone(self.service.create_ticket.call_args.kwargs["company_id"])

    def test_refresh_failures_preserve_text_and_selected_references(self):
        self.widget.subject_input.setText("Draft subject")
        self.widget.description_input.setPlainText("Draft description")
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.references.list_active_contacts_for_company.side_effect = RuntimeError("private detail")
        self.widget.refresh_references_button.click()
        self.assertEqual(self.widget.contact_input.currentData(), 11)
        self.references.list_active_companies.side_effect = RuntimeError("private detail")
        self.widget.refresh_references_button.click()
        self.assertEqual(self.widget.company_input.currentData(), 10)
        self.assertEqual(self.widget.contact_input.currentData(), 11)
        self.assertEqual(self.widget.subject_input.text(), "Draft subject")
        self.assertEqual(self.widget.description_input.toPlainText(), "Draft description")
        self.assertIn("preserved", self.widget.reference_feedback.text())
        self.assertNotIn("private detail", self.widget.reference_feedback.text())
        self.assertTrue(self.widget.save_button.isEnabled())

    def test_contact_load_failure_after_switch_clears_incompatible_choice_and_retries(self):
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.references.list_active_contacts_for_company.side_effect = RuntimeError("private detail")
        self.widget.company_input.setCurrentIndex(2)
        self.assertIsNone(self.widget.contact_input.currentData())
        self.assertFalse(self.widget.contact_input.isEnabled())
        self.references.list_active_contacts_for_company.side_effect = None
        self.references.list_active_contacts_for_company.return_value = (TicketReferenceOption(21, "Charlie Example"),)
        self.widget.refresh_references_button.click()
        self.assertTrue(self.widget.contact_input.isEnabled())
        self.assertEqual(self.widget.contact_input.itemData(1), 21)
