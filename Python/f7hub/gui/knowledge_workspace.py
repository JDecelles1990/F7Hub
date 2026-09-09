"""Create, list, and read workspace for knowledge articles."""

import logging

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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
from f7hub.gui.version_history_dialog import VersionHistoryDialog
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
        self._search_active = False
        self.articles = ()
        self.article = None

        heading = QLabel("Knowledge Base", self)
        heading.setObjectName("knowledgeHeading")
        self.new_button = QPushButton("New Article", self)
        self.new_button.clicked.connect(self.open_new_article)
        self.edit_button = QPushButton("Edit Article", self)
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.open_edit_article)
        self.version_history_button = QPushButton("Version History", self)
        self.version_history_button.setEnabled(False)
        self.version_history_button.clicked.connect(self.open_version_history)
        top = QHBoxLayout()
        top.addWidget(heading)
        top.addStretch()
        top.addWidget(self.new_button)
        top.addWidget(self.edit_button)
        top.addWidget(self.version_history_button)

        self.search_input = QLineEdit(self)
        self.search_input.setAccessibleName("Search current knowledge articles")
        self.search_input.setPlaceholderText("Search current articles")
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_articles)
        self.search_input.returnPressed.connect(self.search_articles)
        self.clear_search_button = QPushButton("Clear Search", self)
        self.clear_search_button.clicked.connect(self.clear_search)
        self.search_input.textChanged.connect(self._search_text_changed)
        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(self.search_button)
        search_row.addWidget(self.clear_search_button)

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
        layout.addLayout(search_row)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)
        self._runner.busy_changed.connect(self._update_actions)
        self._update_actions(False)

    def refresh_list(self, *, select_article_id: int | None = None) -> None:
        if self._runner.busy:
            return
        self._search_active = False
        self.search_input.clear()
        self._pending_selection_id = select_article_id
        self._show_article(None)
        self.feedback.setText("Loading articles…")
        self._runner.submit(self._service.list_articles, self._list_loaded, self._load_failed)

    def search_articles(self) -> None:
        if self._runner.busy:
            return
        query = self.search_input.text()
        if not query.strip():
            self.clear_search()
            return
        self._search_active = True
        self._pending_selection_id = None
        self._show_article(None)
        self.articles = ()
        self.model.removeRows(0, self.model.rowCount())
        self.empty_state.setVisible(False)
        self.table.setVisible(True)
        self.feedback.setText("Searching knowledge articles…")
        self._runner.submit(
            lambda: self._service.search_articles(query),
            self._search_loaded,
            self._search_failed,
        )

    def clear_search(self) -> None:
        if self._runner.busy:
            return
        self.refresh_list()

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

    def open_version_history(self) -> VersionHistoryDialog | None:
        if self._service is None or self._runner.busy or self.article is None:
            return None
        # The window owns the viewer outside the page hierarchy disabled by reads.
        dialog = VersionHistoryDialog(self._service, self._runner, self.article, self.window())
        dialog.open()
        dialog.load_history()
        self._version_history_dialog = dialog
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

    def open_article_by_id(self, article_id: int) -> None:
        """Reconcile the list and reuse selection-driven current detail loading."""
        self.refresh_list(select_article_id=article_id)

    def _article_created(self, article) -> None:
        self.refresh_list(select_article_id=article.knowledge_article_id)

    def _list_loaded(self, articles) -> None:
        self.feedback.setText("")
        self._populate_articles(articles, "No knowledge articles yet.")

    def _search_loaded(self, articles) -> None:
        self._search_active = True
        self._populate_articles(articles, "No matching knowledge articles.")
        self._show_search_result_count()

    def _show_search_result_count(self) -> None:
        count = len(self.articles)
        if count:
            suffix = "article" if count == 1 else "articles"
            self.feedback.setText(f"{count} matching {suffix}.")
        else:
            self.feedback.setText("No matching knowledge articles.")

    def _populate_articles(self, articles, empty_text: str) -> None:
        self.articles = tuple(articles)
        self.model.removeRows(0, self.model.rowCount())
        for article in self.articles:
            code = QStandardItem(article.article_code)
            code.setData(article.knowledge_article_id, Qt.ItemDataRole.UserRole)
            self.model.appendRow((code, QStandardItem(article.title), QStandardItem(article.status)))
        # Recalculate identity columns after each result/list replacement so a
        # longer title cannot leave current code or status values elided.
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(2)
        self.empty_state.setText(empty_text)
        self.empty_state.setVisible(not self.articles)
        self.table.setVisible(bool(self.articles))
        target_id = self._pending_selection_id
        self._pending_selection_id = None
        if target_id is not None and not any(
            article.knowledge_article_id == target_id for article in self.articles
        ):
            self._show_article(None)
            self.feedback.setText("The requested article no longer exists. Refresh the list and try again.")
            return
        if not self.articles:
            self._show_article(None)
            return
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
        if self._search_active:
            self._show_search_result_count()
        else:
            self.feedback.setText("")
        self._show_article(article)

    def _show_article(self, article) -> None:
        self.article = article
        self._update_actions(self._runner.busy)
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

    def _update_actions(self, busy: bool) -> None:
        self.new_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.clear_search_button.setEnabled(
            not busy and (self._search_active or bool(self.search_input.text()))
        )
        self.table.setEnabled(not busy)
        self.edit_button.setEnabled(
            not busy and self.article is not None and self.article.status == "DRAFT"
        )
        self.version_history_button.setEnabled(
            self._service is not None and not busy and self.article is not None
        )

    def _load_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge load failed: %s", type(error).__name__)
        self.feedback.setText("Could not load knowledge articles. Try again.")

    def _search_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge search failed: %s", type(error).__name__)
        self.feedback.setText("Could not search knowledge articles. Check the query and try again.")

    def _search_text_changed(self, _text: str) -> None:
        self._update_actions(self._runner.busy)
