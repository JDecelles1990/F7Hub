"""A bounded, asynchronous company-creation form."""

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.company_service import CompanyService, CompanyCreationError, CompanyValidationError


class QuickCompanyDialog(QDialog):
    company_created = Signal(object)

    def __init__(self, service: CompanyService, runner: ServiceTaskRunner, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._submitting = False
        self._created = False
        self.setWindowTitle("Quick Add Company")
        self.setMinimumWidth(420)
        self.name_input = QLineEdit(self)
        self.name_input.setAccessibleName("Company name, required")
        self.feedback = QLabel(self)
        self.feedback.setWordWrap(True)
        self.feedback.setProperty("validationError", True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.create_button = QPushButton("Create Company", self)
        self.create_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.submit)
        form = QFormLayout()
        form.addRow("Company &name *", self.name_input)
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
            self.feedback.setText("Company name is required.")
            self.name_input.setFocus()
            return
        self._set_submitting(True)
        self.feedback.setText("Creating company…")
        self._runner.submit(lambda: self._service.create_company(name=name), self._succeeded, self._failed)

    def _set_submitting(self, busy):
        self._submitting = busy
        self.name_input.setEnabled(not busy)
        self.create_button.setEnabled(not busy)
        self.cancel_button.setEnabled(not busy)

    def _succeeded(self, company):
        self._created = True
        self._set_submitting(False)
        self.accept()
        self.company_created.emit(company)

    def _failed(self, error):
        self._set_submitting(False)
        if isinstance(error, (CompanyValidationError, CompanyCreationError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error("Company creation failed: %s", type(error).__name__)
            message = "Could not create the company. Your entered information is preserved."
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
