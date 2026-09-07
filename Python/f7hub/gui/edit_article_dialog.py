"""Asynchronous draft revision editor with a fixed optimistic version token."""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QVBoxLayout,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.knowledge_repository import KnowledgeArticleRecord
from f7hub.services.knowledge_service import (
    KnowledgeEditConflictError, KnowledgeService,
    KnowledgeUpdateError, KnowledgeValidationError,
)


class EditArticleDialog(QDialog):
    """Retain the originally opened version and preserve input on failure."""

    article_updated = Signal(object)

    def __init__(
        self, service: KnowledgeService, runner: ServiceTaskRunner,
        article: KnowledgeArticleRecord, parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._article_id = article.knowledge_article_id
        self._expected_version_number = article.version_number
        self._submitting = False
        self._saved = False
        self._conflicted = False
        self.setWindowTitle("Edit Article")
        self.setMinimumSize(560, 480)

        self.code_label = QLabel(article.article_code, self)
        self.version_label = QLabel(f"Version {article.version_number}", self)
        for label in (self.code_label, self.version_label):
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.title_input = QLineEdit(article.title, self)
        self.title_input.setAccessibleName("Article title, required")
        self.summary_input = QLineEdit(article.summary or "", self)
        self.summary_input.setAccessibleName("Article summary, optional")
        self.body_input = QPlainTextEdit(self)
        self.body_input.setAccessibleName("Article body, required, Markdown source")
        self.body_input.setPlainText(article.body_markdown)
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.feedback.setProperty("validationError", True)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.save_button = QPushButton("Save Revision", self)
        self.save_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.submit)

        form = QFormLayout()
        form.addRow("Article code", self.code_label)
        form.addRow("Current version", self.version_label)
        form.addRow("&Title *", self.title_input)
        form.addRow("&Summary", self.summary_input)
        form.addRow("&Body *", self.body_input)
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
        values = dict(
            article_id=self._article_id,
            expected_version_number=self._expected_version_number,
            title=self.title_input.text(), summary=self.summary_input.text(),
            body=self.body_input.toPlainText(),
        )
        self._set_submitting(True)
        self.feedback.setText("Saving revision…")
        if not self._runner.submit(
            lambda: self._service.update_article(**values), self._succeeded, self._failed
        ):
            self._set_submitting(False)

    def _set_submitting(self, submitting: bool) -> None:
        self._submitting = submitting
        for widget in (
            self.title_input, self.summary_input, self.body_input, self.cancel_button,
        ):
            widget.setEnabled(not submitting)
        self.save_button.setEnabled(not submitting and not self._conflicted and not self._saved)

    def _succeeded(self, article) -> None:
        self._saved = True
        self._set_submitting(False)
        self.accept()
        self.article_updated.emit(article)

    def _failed(self, error: Exception) -> None:
        self._conflicted = isinstance(error, KnowledgeEditConflictError)
        self._set_submitting(False)
        if isinstance(error, (KnowledgeValidationError, KnowledgeUpdateError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error("Knowledge revision failed: %s", type(error).__name__)
            message = "Could not save the revision. Your entered information is preserved."
        self.feedback.setText(message)
        self.title_input.setFocus()

    def reject(self) -> None:
        if not self._submitting:
            super().reject()

    def closeEvent(self, event) -> None:
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
