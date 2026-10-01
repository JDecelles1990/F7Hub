"""Collect metadata for one existing local PowerShell reference."""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QVBoxLayout,
)

from f7hub.services.script_service import (
    PRIVILEGE_LEVELS, RISK_LEVELS, SCRIPT_TYPES, ScriptValidationError, ScriptWriteError,
)


class RegisterScriptDialog(QDialog):
    script_registered = Signal(object)

    def __init__(self, service, runner, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._submitting = False
        self._created = False
        self.setWindowTitle("Register script")
        self.setMinimumWidth(540)
        self.code_input = QLineEdit(self)
        self.name_input = QLineEdit(self)
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText("PowerShell/Diagnostics/Example.ps1")
        self.description_input = QPlainTextEdit(self)
        self.description_input.setMaximumHeight(80)
        self.version_input = QLineEdit(self)
        self.type_input = self._choices(SCRIPT_TYPES)
        self.risk_input = self._choices(RISK_LEVELS)
        self.privilege_input = self._choices(PRIVILEGE_LEVELS)
        form = QFormLayout()
        for label, widget, accessible in (
            ("Script &code *", self.code_input, "Script code, required"),
            ("&Name *", self.name_input, "Script name, required"),
            ("Relative &path *", self.path_input, "Relative script path, required"),
            ("&Type *", self.type_input, "Script type, required"),
            ("&Risk *", self.risk_input, "Script risk, required"),
            ("&Privilege *", self.privilege_input, "Script privilege, required"),
            ("&Description", self.description_input, "Description, optional"),
            ("&Version", self.version_input, "Version, optional"),
        ):
            widget.setAccessibleName(accessible)
            form.addRow(label, widget)
        self.note = QLabel(
            "Registers metadata only. The file must already exist under PowerShell/Diagnostics, "
            "Reports or Modules. New registrations are disabled and have no approved checksum.\n"
            "Defaults: PowerShell 7, 120-second timeout, structured output required.", self,
        )
        self.note.setWordWrap(True)
        self.note.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback = QLabel(self)
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setDefault(True)
        self.register_button = QPushButton("Register script", self)
        self.register_button.setAutoDefault(False)
        self.cancel_button.clicked.connect(self.reject)
        self.register_button.clicked.connect(self.submit)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.register_button)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.note)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)

    def _choices(self, values):
        combo = QComboBox(self)
        combo.addItem("Select…", None)
        for value in values:
            combo.addItem(value, value)
        return combo

    def submit(self):
        if self._submitting or self._created or self._runner.busy:
            return False
        values = dict(
            script_code=self.code_input.text(), name=self.name_input.text(),
            relative_path=self.path_input.text(), script_type=self.type_input.currentData(),
            risk_level=self.risk_input.currentData(), privilege_level=self.privilege_input.currentData(),
            description=self.description_input.toPlainText(), version=self.version_input.text(),
        )
        self._set_submitting(True)
        self.feedback.setText("Registering script…")
        if not self._runner.submit(lambda: self._service.register_script(**values), self._succeeded, self._failed):
            self._failed(None)
            return False
        return True

    def _set_submitting(self, submitting):
        self._submitting = submitting
        for widget in (self.code_input, self.name_input, self.path_input, self.description_input,
                       self.version_input, self.type_input, self.risk_input, self.privilege_input,
                       self.cancel_button, self.register_button):
            widget.setEnabled(not submitting)

    def _succeeded(self, record):
        self._created = True
        self._set_submitting(False)
        self.accept()
        self.script_registered.emit(record)

    def _failed(self, error):
        self._set_submitting(False)
        self.feedback.setText(str(error) if isinstance(error, (ScriptValidationError, ScriptWriteError))
                              else "Could not register the script. Your entered information is preserved.")

    def done(self, result):
        if not self._submitting:
            super().done(result)

    def closeEvent(self, event):
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
