"""Asynchronous selector for one draft article's current category."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from f7hub.services.knowledge_service import (
    KnowledgeCategoryConflictError, KnowledgeCategoryError, KnowledgeValidationError,
)


class ArticleCategoryDialog(QDialog):
    """Keep the reviewed tokens; cancellation of reference reads never writes."""

    article_updated = Signal(object)

    def __init__(self, service, runner, article, *, context_is_current, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._article = article
        self._context_is_current = context_is_current
        self._active = True
        self._loaded = False
        self._submitting = False
        self._conflicted = False
        self.setWindowTitle("Article Category")
        self.resize(480, 220)
        self.current_label = QLabel(
            f"{article.article_code}\nCurrent category: {article.category_name or 'Not selected'}", self,
        )
        self.current_label.setTextFormat(Qt.TextFormat.PlainText)
        self.current_label.setWordWrap(True)
        self.category_input = QComboBox(self)
        self.category_input.setAccessibleName("Active Knowledge category")
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.refresh_button = QPushButton("Refresh categories", self)
        self.refresh_button.clicked.connect(self.load_categories)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setDefault(True)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Save", self)
        self.save_button.setAutoDefault(False)
        self.save_button.clicked.connect(self.submit)
        actions = QHBoxLayout()
        actions.addWidget(self.refresh_button)
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.current_label)
        layout.addWidget(self.category_input)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)
        self._runner.busy_changed.connect(self._update_actions)
        self._update_actions()

    def _update_actions(self, _busy=False):
        idle = self._active and not self._runner.busy and not self._submitting
        self.category_input.setEnabled(idle and self._loaded and not self._conflicted)
        self.refresh_button.setEnabled(idle and not self._conflicted)
        self.save_button.setEnabled(idle and self._loaded and not self._conflicted)
        self.cancel_button.setEnabled(not self._submitting)

    def load_categories(self):
        if not self._active or self._runner.busy or self._submitting or self._conflicted:
            return
        self._loaded = False
        self.feedback.setText("Loading Knowledge categories…")
        self._runner.submit(self._service.list_active_knowledge_categories, self._loaded_categories, self._failed)

    def _loaded_categories(self, categories):
        if not self._active:
            return
        self.category_input.clear()
        self.category_input.addItem("Not selected", None)
        for category in categories:
            self.category_input.addItem(category.name, category.category_id)
        index = self.category_input.findData(self._article.category_id)
        self.category_input.setCurrentIndex(max(0, index))
        self.feedback.setText(
            "Current category is no longer selectable. Choose an active category or Not selected to clear it."
            if self._article.category_id is not None and index < 0
            else "Choose a category, or Not selected to remove it."
        )
        self._loaded = True
        self._update_actions()

    def submit(self):
        if (not self._active or not self._loaded or self._conflicted
                or self._submitting or self._runner.busy):
            return
        if not self._context_is_current():
            self._failed(KnowledgeCategoryConflictError("The open article changed. Close and reopen Category."))
            return
        article = self._article
        category_id = self.category_input.currentData()
        self._submitting = True
        self.feedback.setText("Saving category…")
        self._update_actions()
        if not self._runner.submit(
            lambda: self._service.set_article_category(
                article.knowledge_article_id, article.version_number, article.updated_at, category_id,
            ), self._succeeded, self._failed,
        ):
            self._submitting = False
            self._update_actions()

    def _succeeded(self, article):
        self._submitting = False
        self.accept()
        self.article_updated.emit(article)

    def _failed(self, error):
        if not self._active:
            return
        self._submitting = False
        self._conflicted = isinstance(error, KnowledgeCategoryConflictError)
        self.feedback.setText(
            str(error) if isinstance(error, (KnowledgeCategoryError, KnowledgeValidationError))
            else "Could not complete the category operation. Try again."
        )
        self._update_actions()

    def done(self, result):
        if not self._submitting:
            self._active = False
            super().done(result)

    def reject(self):
        if not self._submitting:
            super().reject()

    def closeEvent(self, event):
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
