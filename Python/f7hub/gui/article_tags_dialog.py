"""Modal selection of existing global tags for one current draft article."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.knowledge_service import KnowledgeTagConflictError, KnowledgeTagError, KnowledgeValidationError


class ArticleTagsDialog(QDialog):
    """Load existing tags asynchronously and save an authoritative complete set."""

    article_updated = Signal(object)

    def __init__(self, service, runner: ServiceTaskRunner, article, *, context_is_current, parent=None) -> None:
        super().__init__(parent)
        self._service, self._runner, self._article = service, runner, article
        self._context_is_current = context_is_current
        self._active = True
        self._loaded = self._submitting = self._conflicted = False
        self.setWindowTitle("Article Tags")
        self.resize(480, 340)
        self.current_label = QLabel(f"{article.article_code}\n{article.title}", self)
        self.current_label.setTextFormat(Qt.TextFormat.PlainText)
        self.current_label.setWordWrap(True)
        self.tag_list = QListWidget(self)
        self.tag_list.setAccessibleName("Existing global tags")
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.refresh_button = QPushButton("Refresh tags", self)
        self.refresh_button.clicked.connect(self.load_tags)
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
        layout.addWidget(QLabel("Select zero or more existing tags:", self))
        layout.addWidget(self.tag_list, 1)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)
        self._runner.busy_changed.connect(self._update_actions)
        self._update_actions()

    def _update_actions(self, _busy=False) -> None:
        idle = self._active and not self._runner.busy and not self._submitting
        self.tag_list.setEnabled(idle and self._loaded and not self._conflicted)
        self.refresh_button.setEnabled(idle and not self._conflicted)
        self.save_button.setEnabled(idle and self._loaded and not self._conflicted)
        self.cancel_button.setEnabled(not self._submitting)

    def load_tags(self) -> None:
        if not self._active or self._runner.busy or self._submitting or self._conflicted:
            return
        self._loaded = False
        self.feedback.setText("Loading existing tags…")
        self._runner.submit(
            lambda: (self._service.list_available_tags(), self._service.list_article_tags(self._article.knowledge_article_id)),
            self._loaded_tags, self._failed,
        )

    def _loaded_tags(self, result) -> None:
        if not self._active:
            return
        available, current = result
        current_ids = {tag.tag_id for tag in current}
        self.tag_list.clear()
        for tag in available:
            item = QListWidgetItem(tag.name, self.tag_list)
            item.setData(Qt.ItemDataRole.UserRole, tag.tag_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if tag.tag_id in current_ids else Qt.CheckState.Unchecked)
        self._loaded = True
        self.feedback.setText("Select existing tags, or clear all selections to remove every tag.")
        self._update_actions()

    def submit(self) -> None:
        if not self._active or not self._loaded or self._conflicted or self._submitting or self._runner.busy:
            return
        if not self._context_is_current():
            self._failed(KnowledgeTagConflictError("The open article changed. Close and reopen Tags."))
            return
        tag_ids = tuple(self.tag_list.item(index).data(Qt.ItemDataRole.UserRole)
                        for index in range(self.tag_list.count())
                        if self.tag_list.item(index).checkState() == Qt.CheckState.Checked)
        article = self._article
        self._submitting = True
        self.feedback.setText("Saving tags…")
        self._update_actions()
        if not self._runner.submit(
            lambda: self._service.set_article_tags(article.knowledge_article_id, article.version_number, article.updated_at, tag_ids),
            self._succeeded, self._failed,
        ):
            self._submitting = False
            self._update_actions()

    def _succeeded(self, article) -> None:
        self._submitting = False
        self.accept()
        self.article_updated.emit(article)

    def _failed(self, error) -> None:
        if not self._active:
            return
        self._submitting = False
        self._conflicted = isinstance(error, KnowledgeTagConflictError)
        self.feedback.setText(str(error) if isinstance(error, (KnowledgeTagError, KnowledgeValidationError)) else "Could not complete the tag operation. Try again.")
        self._update_actions()

    def done(self, result) -> None:
        if not self._submitting:
            self._active = False
            super().done(result)

    def reject(self) -> None:
        if not self._submitting:
            super().reject()

    def closeEvent(self, event) -> None:
        if self._submitting:
            event.ignore()
        else:
            super().closeEvent(event)
