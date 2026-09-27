"""Asynchronous editor for one loaded ticket subject."""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.ticket_repository import TicketRecord
from f7hub.services.ticket_service import (
    TicketEditConflictError, TicketService, TicketUpdateError, TicketValidationError,
)


class EditTicketSubjectDialog(QDialog):
    """Keep the loaded-state guard and entered subject until save or cancel."""

    subject_updated = Signal(object)

    def __init__(
        self, service: TicketService, runner: ServiceTaskRunner,
        ticket: TicketRecord, parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._ticket_id = ticket.ticket_id
        self._expected_subject = ticket.subject
        self._expected_updated_at = ticket.updated_at
        self._submitting = False
        self._saved = False
        self._conflicted = False
        self.setWindowTitle("Edit ticket subject")
        self.setMinimumWidth(420)

        number = QLabel(ticket.ticket_number, self)
        number.setTextFormat(Qt.TextFormat.PlainText)
        self.subject_input = QLineEdit(ticket.subject, self)
        self.subject_input.setAccessibleName("Ticket subject, required")
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.feedback.setProperty("validationError", True)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.save_button = QPushButton("Save subject", self)
        self.save_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.submit)

        form = QFormLayout()
        form.addRow("Ticket number", number)
        form.addRow("&Subject *", self.subject_input)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)

    def submit(self) -> None:
        if self._submitting or self._saved or self._conflicted or self._runner.busy:
            return
        subject = self.subject_input.text()
        self._set_submitting(True)
        self.feedback.setText("Saving subject…")
        if not self._runner.submit(
            lambda: self._service.update_ticket_subject(
                self._ticket_id,
                expected_subject=self._expected_subject,
                expected_updated_at=self._expected_updated_at,
                subject=subject,
            ),
            self._succeeded, self._failed,
        ):
            self._set_submitting(False)

    def _set_submitting(self, submitting: bool) -> None:
        self._submitting = submitting
        self.subject_input.setEnabled(not submitting)
        self.cancel_button.setEnabled(not submitting)
        self.save_button.setEnabled(not submitting and not self._conflicted and not self._saved)

    def _succeeded(self, ticket: TicketRecord) -> None:
        self._saved = True
        self._set_submitting(False)
        self.accept()
        self.subject_updated.emit(ticket)

    def _failed(self, error: Exception) -> None:
        self._conflicted = isinstance(error, TicketEditConflictError)
        self._set_submitting(False)
        if isinstance(error, (TicketValidationError, TicketUpdateError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error("Ticket subject edit failed: %s", type(error).__name__)
            message = "Could not save the subject. Your entry is preserved."
        self.feedback.setText(message)
        self.subject_input.setFocus()

    def reject(self) -> None:
        if not self._submitting:
            super().reject()

    def closeEvent(self, event) -> None:
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
