"""Bounded asynchronous form for creating one knowledge article."""

import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.knowledge_service import (
    KnowledgeCreationError,
    KnowledgeService,
    KnowledgeValidationError,
)


class NewArticleDialog(QDialog):
    """Collect the minimum article contract without owning persistence."""

    article_created = Signal(object)

    def __init__(
        self,
        service: KnowledgeService,
        runner: ServiceTaskRunner,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._submitting = False
        self._created = False
        self.setWindowTitle("New Article")
        self.setMinimumSize(560, 480)

        self.code_input = QLineEdit(self)
        self.code_input.setAccessibleName("Article code, required")
        self.code_input.setPlaceholderText("KB0001")
        self.title_input = QLineEdit(self)
        self.title_input.setAccessibleName("Article title, required")
        self.summary_input = QLineEdit(self)
        self.summary_input.setAccessibleName("Article summary, optional")
        self.body_input = QPlainTextEdit(self)
        self.body_input.setAccessibleName("Article body, required, Markdown source")
        self.body_input.setPlaceholderText("Enter article content (Markdown supported as source text).")

        self.feedback = QLabel(self)
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setProperty("validationError", True)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.create_button = QPushButton("Create Article", self)
        self.create_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.submit)

        form = QFormLayout()
        form.addRow("Article &code *", self.code_input)
        form.addRow("&Title *", self.title_input)
        form.addRow("&Summary", self.summary_input)
        form.addRow("&Body *", self.body_input)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.create_button)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)

    def submit(self) -> None:
        if self._submitting or self._created or self._runner.busy:
            return
        values = {
            "article_code": self.code_input.text(),
            "title": self.title_input.text(),
            "summary": self.summary_input.text(),
            "body": self.body_input.toPlainText(),
        }
        for value, message, widget in (
            (values["article_code"], "Article code is required.", self.code_input),
            (values["title"], "Title is required.", self.title_input),
            (values["body"], "Body is required.", self.body_input),
        ):
            if not value.strip():
                self.feedback.setText(message)
                widget.setFocus()
                return
        self._set_submitting(True)
        self.feedback.setText("Creating article…")
        accepted = self._runner.submit(
            lambda: self._service.create_article(**values),
            self._succeeded,
            self._failed,
        )
        if not accepted:
            self._set_submitting(False)

    def _set_submitting(self, submitting: bool) -> None:
        self._submitting = submitting
        for widget in (
            self.code_input,
            self.title_input,
            self.summary_input,
            self.body_input,
            self.cancel_button,
            self.create_button,
        ):
            widget.setEnabled(not submitting)

    def _succeeded(self, article) -> None:
        self._created = True
        self._set_submitting(False)
        self.accept()
        self.article_created.emit(article)

    def _failed(self, error: Exception) -> None:
        self._set_submitting(False)
        if isinstance(error, (KnowledgeValidationError, KnowledgeCreationError)):
            message = str(error)
        else:
            logging.getLogger(__name__).error(
                "Knowledge article creation failed: %s", type(error).__name__
            )
            message = "Could not create the article. Your entered information is preserved."
        self.feedback.setText(message)
        self.code_input.setFocus()

    def reject(self) -> None:
        if not self._submitting:
            super().reject()

    def closeEvent(self, event) -> None:
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
