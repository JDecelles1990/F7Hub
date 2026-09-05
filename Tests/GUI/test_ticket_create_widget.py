from __future__ import annotations

import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from f7hub.gui.ticket_create_widget import (
    TicketCreateWidget,
    TicketReferenceOption,
    TicketReferenceOptions,
)
from f7hub.services.ticket_service import (
    TicketCreationError,
    TicketValidationError,
)


class RecordingTicketService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.error: Exception | None = None

    def create_ticket(self, **values: object) -> object:
        self.calls.append(values)
        if self.error is not None:
            raise self.error
        return SimpleNamespace(ticket_id=1, ticket_number="TKT-1001")


class TicketCreateWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.service = RecordingTicketService()
        options = TicketReferenceOptions(
            companies=(TicketReferenceOption(10, "Contoso"),),
            contacts=(TicketReferenceOption(20, "Casey Contact"),),
            categories=(TicketReferenceOption(30, "Printing"),),
        )
        self.widget = TicketCreateWidget(
            self.service,
            reference_options=options,
        )
        self.widget.show()
        self.application.processEvents()

    def tearDown(self) -> None:
        self.widget.close()
        self.widget.deleteLater()
        self.application.processEvents()

    def test_form_defaults_and_reference_options(self) -> None:
        self.assertEqual(self.widget.ticket_type_input.currentData(), "INCIDENT")
        self.assertEqual(self.widget.priority_input.currentData(), "MEDIUM")
        self.assertEqual(self.widget.company_input.count(), 2)
        self.assertEqual(self.widget.contact_input.count(), 2)
        self.assertEqual(self.widget.category_input.count(), 2)
        self.assertTrue(self.widget.save_button.isDefault())

    def test_blank_subject_is_inline_and_does_not_call_service(self) -> None:
        self.widget.subject_input.setText("   ")

        self.widget.submit()

        self.assertEqual(self.service.calls, [])
        self.assertTrue(self.widget.subject_error.isVisible())
        self.assertEqual(self.widget.subject_error.text(), "Subject is required.")
        self.assertEqual(self.widget.subject_input.text(), "   ")

    def test_submit_delegates_all_values_and_emits_created_ticket(self) -> None:
        created: list[object] = []
        self.widget.ticket_created.connect(created.append)
        self.widget.ticket_number_input.setText(" INC-4001 ")
        self.widget.subject_input.setText(" Printer offline ")
        self.widget.ticket_type_input.setCurrentIndex(1)
        self.widget.priority_input.setCurrentIndex(2)
        self.widget.company_input.setCurrentIndex(1)
        self.widget.contact_input.setCurrentIndex(1)
        self.widget.category_input.setCurrentIndex(1)
        self.widget.description_input.setPlainText("Cannot print")

        self.widget.submit()

        self.assertEqual(
            self.service.calls,
            [
                {
                    "ticket_number": "INC-4001",
                    "subject": " Printer offline ",
                    "ticket_type": "SERVICE_REQUEST",
                    "priority": "HIGH",
                    "company_id": 10,
                    "contact_id": 20,
                    "category_id": 30,
                    "description": "Cannot print",
                }
            ],
        )
        self.assertEqual(len(created), 1)
        self.assertTrue(self.widget.status_label.isVisible())
        self.assertIn("TKT-1001", self.widget.status_label.text())
        self.assertTrue(self.widget.save_button.isEnabled())

    def test_service_validation_is_visible_and_input_is_preserved(self) -> None:
        self.service.error = TicketValidationError(
            "contact_id does not belong to the selected company."
        )
        failed: list[str] = []
        self.widget.submission_failed.connect(failed.append)
        self.widget.subject_input.setText("Keep this subject")

        self.widget.submit()

        self.assertTrue(self.widget.form_error.isVisible())
        self.assertIn("selected company", self.widget.form_error.text())
        self.assertEqual(self.widget.subject_input.text(), "Keep this subject")
        self.assertEqual(len(failed), 1)

    def test_persistence_failure_uses_safe_message_and_preserves_input(self) -> None:
        self.service.error = TicketCreationError("internal database detail")
        self.widget.subject_input.setText("Keep this too")

        self.widget.submit()

        self.assertTrue(self.widget.form_error.isVisible())
        self.assertNotIn("database detail", self.widget.form_error.text())
        self.assertIn("preserved", self.widget.form_error.text())
        self.assertEqual(self.widget.subject_input.text(), "Keep this too")
        self.assertTrue(self.widget.save_button.isEnabled())


if __name__ == "__main__":
    unittest.main()
