"""Create, list, and read workspace for knowledge articles."""

import logging

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from f7hub.gui.new_article_dialog import NewArticleDialog
from f7hub.gui.edit_article_dialog import EditArticleDialog
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.knowledge_service import KnowledgeService


class KnowledgeWorkspace(QWidget):
    """A deliberately small Knowledge Base list/detail workspace."""

    def __init__(
        self,
        service: KnowledgeService,
        runner: ServiceTaskRunner,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._pending_selection_id = None
        self.articles = ()
        self.article = None

        heading = QLabel("Knowledge Base", self)
        heading.setObjectName("knowledgeHeading")
        self.new_button = QPushButton("New Article", self)
        self.new_button.clicked.connect(self.open_new_article)
        self.edit_button = QPushButton("Edit Article", self)
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.open_edit_article)
        top = QHBoxLayout()
        top.addWidget(heading)
        top.addStretch()
        top.addWidget(self.new_button)
        top.addWidget(self.edit_button)

        self.model = QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels(("Article code", "Title", "Status"))
        self.table = QTableView(self)
        self.table.setAccessibleName("Knowledge articles; select a row to read")
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.selectionModel().selectionChanged.connect(self._selection_changed)

        self.empty_state = QLabel("No knowledge articles yet.", self)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback = QLabel(self)
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)

        self.detail_code = QLabel("Select an article to read.", self)
        self.detail_code.setObjectName("articleCode")
        self.detail_title = QLabel("", self)
        self.detail_title.setWordWrap(True)
        self.detail_status = QLabel("", self)
        self.detail_version = QLabel("", self)
        self.detail_summary = QLabel("", self)
        self.detail_summary.setWordWrap(True)
        self.detail_body = QPlainTextEdit(self)
        self.detail_body.setReadOnly(True)
        self.detail_body.setAccessibleName("Knowledge article body, read only")
        self.detail_body.setPlaceholderText("Select an article to read.")
        detail = QWidget(self)
        detail_layout = QVBoxLayout(detail)
        for widget in (self.detail_code, self.detail_title, self.detail_status, self.detail_version, self.detail_summary):
            widget.setTextFormat(Qt.TextFormat.PlainText)
            detail_layout.addWidget(widget)
        detail_layout.addWidget(self.detail_body, 1)

        list_panel = QWidget(self)
        list_layout = QVBoxLayout(list_panel)
        list_layout.addWidget(self.table, 1)
        list_layout.addWidget(self.empty_state)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(list_panel)
        splitter.addWidget(detail)
        splitter.setSizes((420, 620))

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)

    def refresh_list(self, *, select_article_id: int | None = None) -> None:
        if self._runner.busy:
            return
        self._pending_selection_id = select_article_id
        self._show_article(None)
        self.feedback.setText("Loading articles…")
        self._runner.submit(self._service.list_articles, self._list_loaded, self._load_failed)

    def open_new_article(self) -> NewArticleDialog | None:
        if self._runner.busy:
            return None
        dialog = NewArticleDialog(self._service, self._runner, self)
        dialog.article_created.connect(self._article_created)
        dialog.open()
        self._new_article_dialog = dialog
        return dialog

    def open_edit_article(self) -> EditArticleDialog | None:
        if self._runner.busy or self.article is None or self.article.status != "DRAFT":
            return None
        dialog = EditArticleDialog(self._service, self._runner, self.article, self)
        dialog.article_updated.connect(self._article_created)
        dialog.open()
        self._edit_article_dialog = dialog
        return dialog

    def open_article(self, article_id: int) -> None:
        if self._runner.busy:
            return
        self._show_article(None)
        self.feedback.setText("Loading article…")
        self._runner.submit(
            lambda: self._service.get_article(article_id),
            lambda article: self._article_loaded(article_id, article),
            self._load_failed,
        )

    def _article_created(self, article) -> None:
        self.refresh_list(select_article_id=article.knowledge_article_id)

    def _list_loaded(self, articles) -> None:
        self.articles = tuple(articles)
        self.model.removeRows(0, self.model.rowCount())
        for article in self.articles:
            code = QStandardItem(article.article_code)
            code.setData(article.knowledge_article_id, Qt.ItemDataRole.UserRole)
            self.model.appendRow((code, QStandardItem(article.title), QStandardItem(article.status)))
        self.empty_state.setVisible(not self.articles)
        self.table.setVisible(bool(self.articles))
        self.feedback.setText("")
        if not self.articles:
            self._show_article(None)
            return
        target_id = self._pending_selection_id
        self._pending_selection_id = None
        row = next(
            (index for index, article in enumerate(self.articles)
             if article.knowledge_article_id == target_id),
            0,
        )
        index = self.model.index(row, 0)
        self.table.selectionModel().setCurrentIndex(
            index,
            QItemSelectionModel.SelectionFlag.ClearAndSelect
            | QItemSelectionModel.SelectionFlag.Rows,
        )

    def _selection_changed(self, selected, _deselected) -> None:
        indexes = selected.indexes()
        if not indexes or self._runner.busy:
            return
        article_id = self.model.item(indexes[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        self.open_article(int(article_id))

    def _article_loaded(self, requested_id: int, article) -> None:
        current = self.table.currentIndex()
        current_id = None if not current.isValid() else self.model.item(current.row(), 0).data(Qt.ItemDataRole.UserRole)
        if current_id != requested_id:
            return
        if article is None:
            self.feedback.setText("The selected article no longer exists. Refresh the list and try again.")
            self._show_article(None)
            return
        self.feedback.setText("")
        self._show_article(article)

    def _show_article(self, article) -> None:
        self.article = article
        self.edit_button.setEnabled(article is not None and article.status == "DRAFT")
        if article is None:
            self.detail_code.setText("Select an article to read.")
            self.detail_title.setText("")
            self.detail_status.setText("")
            self.detail_version.setText("")
            self.detail_summary.setText("")
            self.detail_body.clear()
            return
        self.detail_code.setText(article.article_code)
        self.detail_title.setText(article.title)
        self.detail_status.setText(f"Status: {article.status}")
        self.detail_version.setText(f"Version {article.version_number}")
        self.detail_summary.setText(
            f"Summary: {article.summary}" if article.summary else "Summary: Not provided"
        )
        self.detail_body.setPlainText(article.body_markdown)

    def _load_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge load failed: %s", type(error).__name__)
        self.feedback.setText("Could not load knowledge articles. Try again.")
