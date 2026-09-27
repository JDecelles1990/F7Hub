"""Asynchronous editor for one loaded ticket priority."""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.ticket_repository import TicketRecord
from f7hub.services.ticket_service import (
    TICKET_PRIORITIES, TicketEditConflictError, TicketService,
    TicketUpdateError, TicketValidationError,
)


class EditTicketPriorityDialog(QDialog):
    """Keep the loaded-state guard and selected priority until save or cancel."""

    priority_updated = Signal(object)

    def __init__(
        self, service: TicketService, runner: ServiceTaskRunner,
        ticket: TicketRecord, parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._ticket_id = ticket.ticket_id
        self._expected_priority = ticket.priority
        self._expected_updated_at = ticket.updated_at
        self._submitting = False
        self._saved = False
        self._conflicted = False
        self.setWindowTitle("Edit ticket priority")
        self.setMinimumWidth(420)

        number = QLabel(ticket.ticket_number, self)
        number.setTextFormat(Qt.TextFormat.PlainText)
        self.priority_input = QComboBox(self)
        self.priority_input.setAccessibleName("Ticket priority")
        for priority in sorted(TICKET_PRIORITIES):
            self.priority_input.addItem(priority.title(), priority)
        self.priority_input.setCurrentIndex(self.priority_input.findData(ticket.priority))
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.feedback.setProperty("validationError", True)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.save_button = QPushButton("Save priority", self)
        self.save_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.submit)

        form = QFormLayout()
        form.addRow("Ticket number", number)
        form.addRow("&Priority", self.priority_input)
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
        priority = self.priority_input.currentData()
        self._set_submitting(True)
        self.feedback.setText("Saving priority…")
        if not self._runner.submit(
            lambda: self._service.update_ticket_priority(
                self._ticket_id,
                expected_priority=self._expected_priority,
                expected_updated_at=self._expected_updated_at,
                priority=priority,
            ),
            self._succeeded, self._failed,
        ):
            self._set_submitting(False)

    def _set_submitting(self, submitting: bool) -> None:
        self._submitting = submitting
        self.priority_input.setEnabled(not submitting)
        self.cancel_button.setEnabled(not submitting)
        self.save_button.setEnabled(not submitting and not self._conflicted and not self._saved)

    def _succeeded(self, ticket: TicketRecord) -> None:
        self._saved = True
        self._set_submitting(False)
        self.accept()
        self.priority_updated.emit(ticket)

    def _failed(self, error: Exception) -> None:
        self._conflicted = isinstance(error, TicketEditConflictError)
        self._set_submitting(False)
        if isinstance(error, (TicketValidationError, TicketUpdateError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error("Ticket priority edit failed: %s", type(error).__name__)
            message = "Could not save the priority. Your selection is preserved."
        self.feedback.setText(message)
        self.priority_input.setFocus()

    def reject(self) -> None:
        if not self._submitting:
            super().reject()

    def closeEvent(self, event) -> None:
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
