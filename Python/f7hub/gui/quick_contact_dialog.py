"""A bounded, asynchronous contact-creation form."""

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.contact_service import ContactService, ContactCreationError, ContactValidationError


class QuickContactDialog(QDialog):
    contact_created = Signal(object)

    def __init__(self, service: ContactService, runner: ServiceTaskRunner, company_id: int, parent=None):
        super().__init__(parent)
        self._service = service
        self._company_id = company_id
        self._runner = runner
        self._submitting = False
        self._created = False
        self.setWindowTitle("Quick Add Contact")
        self.setMinimumWidth(420)
        self.name_input = QLineEdit(self)
        self.name_input.setAccessibleName("Contact name, required")
        self.email_input = QLineEdit(self)
        self.email_input.setAccessibleName("Email, optional")
        self.feedback = QLabel(self)
        self.feedback.setWordWrap(True)
        self.feedback.setProperty("validationError", True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.create_button = QPushButton("Create Contact", self)
        self.create_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.submit)
        form = QFormLayout()
        form.addRow("Contact &name *", self.name_input)
        form.addRow("&Email", self.email_input)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.create_button)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)

    def submit(self):
        if self._submitting or self._created or self._runner.busy:
            return
        name = self.name_input.text()
        if not name.strip():
            self.feedback.setText("Contact name is required.")
            self.name_input.setFocus()
            return
        email = self.email_input.text()
        self._set_submitting(True)
        self.feedback.setText("Creating contact…")
        self._runner.submit(lambda: self._service.create_contact(company_id=self._company_id, display_name=name, email=email), self._succeeded, self._failed)

    def _set_submitting(self, busy):
        self._submitting = busy
        self.name_input.setEnabled(not busy)
        self.email_input.setEnabled(not busy)
        self.create_button.setEnabled(not busy)
        self.cancel_button.setEnabled(not busy)

    def _succeeded(self, contact):
        self._created = True
        self._set_submitting(False)
        self.accept()
        self.contact_created.emit(contact)

    def _failed(self, error):
        self._set_submitting(False)
        if isinstance(error, (ContactValidationError, ContactCreationError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error("Contact creation failed: %s", type(error).__name__)
            message = "Could not create the contact. Your entered information is preserved."
        self.feedback.setText(message)
        self.name_input.setFocus()

    def reject(self):
        if not self._submitting:
            super().reject()

    def closeEvent(self, event):
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
