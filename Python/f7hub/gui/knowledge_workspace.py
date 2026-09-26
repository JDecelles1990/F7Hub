"""Create, list, and read workspace for knowledge articles."""

import logging
from html import escape

from PySide6.QtCore import QItemSelectionModel, QSignalBlocker, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from f7hub.gui.new_article_dialog import NewArticleDialog
from f7hub.gui.article_category_dialog import ArticleCategoryDialog
from f7hub.gui.article_tags_dialog import ArticleTagsDialog
from f7hub.gui.knowledge_tag_filter_dialog import KnowledgeTagFilterDialog
from f7hub.gui.edit_article_dialog import EditArticleDialog
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.version_history_dialog import VersionHistoryDialog
from f7hub.services.knowledge_service import KnowledgeArchiveError, KnowledgePublishError, KnowledgeService


_TAG_FILTER_ALL = ("all", None)
_TAG_FILTER_UNTAGGED = ("untagged", None)
_TAG_FILTER_CHOOSE = ("choose", None)


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
        self._filter_runner = ServiceTaskRunner(self)
        self._tag_filter_runner = ServiceTaskRunner(self)
        self._filter_options_loaded = False
        self._filter_options_ready = False
        self._tag_filter_options_loaded = False
        self._tag_filter_options_ready = False
        self._manual_filter_refresh_active = False
        self._manual_filter_refresh_pending = set()
        self._manual_filter_refresh_reset = False
        self._manual_category_filter_selection = None
        self._manual_tag_filter_selection = None
        self._pending_selection_id = None
        self._preferred_selection_id = None
        self._search_active = False
        self._search_query = ""
        self._confirming_publish = False
        self._confirming_archive = False
        self._category_dialog = None
        self._tags_dialog = None
        self._tag_filter_dialog = None
        self._available_filter_tags = ()
        self._selected_tag_filter = _TAG_FILTER_ALL
        self.articles = ()
        self.article = None

        heading = QLabel("Knowledge Base", self)
        heading.setObjectName("knowledgeHeading")
        self.new_button = QPushButton("New Article", self)
        self.new_button.clicked.connect(self.open_new_article)
        self.edit_button = QPushButton("Edit Article", self)
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.open_edit_article)
        self.publish_button = QPushButton("Publish", self)
        self.publish_button.clicked.connect(self.publish_article)
        self.archive_button = QPushButton("Archive", self)
        self.archive_button.clicked.connect(self.archive_article)
        self.category_button = QPushButton("Category…", self)
        self.category_button.clicked.connect(self.open_category)
        self.tags_button = QPushButton("Tags…", self)
        self.tags_button.clicked.connect(self.open_tags)
        self.version_history_button = QPushButton("Version History", self)
        self.version_history_button.setEnabled(False)
        self.version_history_button.clicked.connect(self.open_version_history)
        top = QHBoxLayout()
        top.addWidget(heading)
        top.addStretch()
        top.addWidget(self.new_button)
        top.addWidget(self.edit_button)
        top.addWidget(self.publish_button)
        top.addWidget(self.archive_button)
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
        filter_row = QHBoxLayout()
        self.category_filter = QComboBox(self)
        self.category_filter.setAccessibleName("Filter knowledge articles by category")
        self.category_filter.setMinimumContentsLength(10)
        self.category_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.category_filter.addItem("All categories", None)
        self.category_filter.addItem("Not selected", None)
        self.category_filter.currentIndexChanged.connect(self._filter_changed)
        filter_row.addWidget(QLabel("Category:", self))
        filter_row.addWidget(self.category_filter, 1)
        self.status_filter = QComboBox(self)
        self.status_filter.setAccessibleName("Filter knowledge articles by status")
        self.status_filter.addItem("All statuses", None)
        self.status_filter.addItem("Draft", "DRAFT")
        self.status_filter.addItem("Published", "PUBLISHED")
        self.status_filter.addItem("Archived", "ARCHIVED")
        self.status_filter.currentIndexChanged.connect(self._filter_changed)
        filter_row.addWidget(QLabel("Status:", self))
        filter_row.addWidget(self.status_filter, 1)
        self.tag_filter = QComboBox(self)
        self.tag_filter.setAccessibleName("Filter knowledge articles by tag")
        self.tag_filter.setMinimumContentsLength(8)
        self.tag_filter.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.tag_filter.addItem("All tags", _TAG_FILTER_ALL)
        self.tag_filter.addItem("Untagged", _TAG_FILTER_UNTAGGED)
        self.tag_filter.currentIndexChanged.connect(self._tag_filter_changed)
        filter_row.addWidget(QLabel("Tag:", self))
        filter_row.addWidget(self.tag_filter, 1)
        self.refresh_filters_button = QToolButton(self)
        self.refresh_filters_button.setText("Refresh filters")
        self.refresh_filters_button.setAccessibleName("Refresh knowledge filter choices")
        self.refresh_filters_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.refresh_filters_button.clicked.connect(self.refresh_filter_options)
        filter_row.addWidget(self.refresh_filters_button)
        self.filter_feedback = QLabel(self)
        self.filter_feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.filter_feedback.setWordWrap(True)
        self.filter_feedback.hide()
        self.tag_filter_feedback = QLabel(self)
        self.tag_filter_feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.tag_filter_feedback.setWordWrap(True)
        self.tag_filter_feedback.hide()

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
        self.detail_category = QLabel("", self)
        self.detail_category.setWordWrap(True)
        self.detail_tags = QLabel("", self)
        self.detail_tags.setWordWrap(True)
        self.detail_summary = QLabel("", self)
        self.detail_summary.setWordWrap(True)
        self.detail_body = QPlainTextEdit(self)
        self.detail_body.setReadOnly(True)
        self.detail_body.setAccessibleName("Knowledge article body, read only")
        self.detail_body.setPlaceholderText("Select an article to read.")
        detail = QWidget(self)
        detail_layout = QVBoxLayout(detail)
        for widget in (self.detail_code, self.detail_title, self.detail_status, self.detail_version, self.detail_category, self.detail_tags, self.detail_summary):
            widget.setTextFormat(Qt.TextFormat.PlainText)
            if widget is self.detail_category:
                category_row = QHBoxLayout()
                category_row.addWidget(widget, 1)
                category_row.addWidget(self.category_button)
                detail_layout.addLayout(category_row)
            elif widget is self.detail_tags:
                tags_row = QHBoxLayout()
                tags_row.addWidget(widget, 1)
                tags_row.addWidget(self.tags_button)
                detail_layout.addLayout(tags_row)
            else:
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
        layout.addLayout(filter_row)
        layout.addWidget(self.filter_feedback)
        layout.addWidget(self.tag_filter_feedback)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)
        self._runner.busy_changed.connect(self._update_actions)
        self._filter_runner.busy_changed.connect(lambda _busy: self._update_actions(self._runner.busy))
        self._tag_filter_runner.busy_changed.connect(lambda _busy: self._update_actions(self._runner.busy))
        self._update_actions(False)

    @property
    def filter_loading(self) -> bool:
        return self._filter_runner.busy or self._tag_filter_runner.busy

    def _load_filter_options(self) -> None:
        if not self._filter_options_loaded and not self._filter_runner.busy:
            self._filter_options_ready = False
            self._filter_runner.submit(
                self._service.list_active_knowledge_categories,
                self._filter_options_succeeded, self._filter_options_failed,
            )
        if self._tag_filter_options_loaded or self._tag_filter_runner.busy:
            return
        self._tag_filter_options_ready = False
        self._tag_filter_runner.submit(
            self._service.list_available_tags,
            self._tag_filter_options_succeeded, self._tag_filter_options_failed,
        )

    def _category_filter_selection(self) -> tuple[str, int | None]:
        if self.category_filter.currentIndex() == 1:
            return ("uncategorized", None)
        category_id = self.category_filter.currentData()
        if category_id is None:
            return ("all", None)
        return ("category", category_id)

    def refresh_filter_options(self) -> None:
        if (self._runner.busy or self.filter_loading or self._manual_filter_refresh_active
                or self._tag_filter_dialog is not None):
            return
        self._manual_filter_refresh_active = True
        self._manual_filter_refresh_pending = {"category", "tag"}
        self._manual_filter_refresh_reset = False
        self._manual_category_filter_selection = self._category_filter_selection()
        self._manual_tag_filter_selection = self.tag_filter.currentData()
        self._update_actions(self._runner.busy)
        self._filter_runner.submit(
            self._service.list_active_knowledge_categories,
            self._filter_options_succeeded, self._filter_options_failed,
        )
        self._tag_filter_runner.submit(
            self._service.list_available_tags,
            self._tag_filter_options_succeeded, self._tag_filter_options_failed,
        )

    def _filter_options_succeeded(self, categories) -> None:
        manual = (
            self._manual_filter_refresh_active
            and "category" in self._manual_filter_refresh_pending
        )
        selection = (
            self._manual_category_filter_selection
            if manual else self._category_filter_selection()
        )
        with QSignalBlocker(self.category_filter):
            self.category_filter.clear()
            self.category_filter.addItem("All categories", None)
            self.category_filter.addItem("Not selected", None)
            for category in categories:
                self.category_filter.addItem(category.name, category.category_id)
            mode, category_id = selection
            if mode == "uncategorized":
                self.category_filter.setCurrentIndex(1)
            elif mode == "category":
                index = self.category_filter.findData(category_id)
                self.category_filter.setCurrentIndex(index if index >= 0 else 0)
            else:
                self.category_filter.setCurrentIndex(0)
        self._filter_options_loaded = True
        self._filter_options_ready = True
        self.filter_feedback.hide()
        if manual:
            self._manual_filter_source_settled(
                "category", selection_reset=mode == "category" and index < 0
            )
        self._update_actions(self._runner.busy)

    def _filter_options_failed(self, error) -> None:
        logging.getLogger(__name__).error("Knowledge filter options failed: %s", type(error).__name__)
        manual = (
            self._manual_filter_refresh_active
            and "category" in self._manual_filter_refresh_pending
        )
        self.filter_feedback.setText(
            "Could not refresh category filters. Existing choices were retained. Try again."
            if manual else
            "Could not load category filters. All categories remain available. Select Refresh filters to retry."
        )
        self.filter_feedback.show()
        self._filter_options_ready = True
        if manual:
            self._manual_filter_source_settled("category")
        self._update_actions(self._runner.busy)

    def _tag_filter_options_succeeded(self, tags) -> None:
        manual = (
            self._manual_filter_refresh_active
            and "tag" in self._manual_filter_refresh_pending
        )
        selection = (
            self._manual_tag_filter_selection
            if manual else self.tag_filter.currentData()
        )
        self._available_filter_tags = tuple(tags)
        mode, value = selection
        selected_ids = ((value,) if mode == "tag" else value if mode == "any" else ())
        available_ids = {tag.tag_id for tag in tags}
        surviving_ids = tuple(tag_id for tag_id in selected_ids if tag_id in available_ids)
        selection_reset = len(surviving_ids) != len(selected_ids)
        if mode in ("tag", "any"):
            selection = self._selection_for_tag_ids(surviving_ids)
        self._set_tag_filter_selection(selection)
        self._tag_filter_options_loaded = True
        self._tag_filter_options_ready = True
        if selection_reset:
            self.tag_filter_feedback.setText(
                "Unavailable tags were removed from the filter."
                if surviving_ids else "Selected tags are unavailable. Showing All tags."
            )
            self.tag_filter_feedback.show()
        else:
            self.tag_filter_feedback.hide()
        if manual:
            self._manual_filter_source_settled("tag", selection_reset=selection_reset)
        self._update_actions(self._runner.busy)

    @staticmethod
    def _selection_for_tag_ids(tag_ids: tuple[int, ...]) -> tuple:
        tag_ids = tuple(sorted(tag_ids))
        if not tag_ids:
            return _TAG_FILTER_ALL
        if len(tag_ids) == 1:
            return ("tag", tag_ids[0])
        return ("any", tag_ids)

    def _set_tag_filter_selection(self, selection: tuple) -> None:
        """Rebuild cached shortcuts without submitting a result request."""
        with QSignalBlocker(self.tag_filter):
            self.tag_filter.clear()
            self.tag_filter.addItem("All tags", _TAG_FILTER_ALL)
            self.tag_filter.addItem("Untagged", _TAG_FILTER_UNTAGGED)
            for tag in self._available_filter_tags:
                self.tag_filter.addItem(tag.name, ("tag", tag.tag_id))
            mode, value = selection
            if mode == "any":
                self.tag_filter.addItem(f"Any of {len(value)} tags", selection)
            self.tag_filter.addItem("Choose tags…", _TAG_FILTER_CHOOSE)
            index = next(
                (item_index for item_index in range(self.tag_filter.count())
                 if self.tag_filter.itemData(item_index) == selection), -1,
            )
            self.tag_filter.setCurrentIndex(index if index >= 0 else 0)
            self._selected_tag_filter = self.tag_filter.currentData()
        selected_names = (
            [tag.name for tag in self._available_filter_tags if tag.tag_id in value]
            if mode == "any" else []
        )
        self.tag_filter.setToolTip(
            "<qt>" + escape("Match any selected tag: " + ", ".join(selected_names)) + "</qt>"
            if selected_names else ""
        )

    def _tag_filter_changed(self, index: int) -> None:
        selection = self.tag_filter.currentData()
        if selection == _TAG_FILTER_CHOOSE:
            self._set_tag_filter_selection(self._selected_tag_filter)
            self.open_tag_filter()
            return
        self._selected_tag_filter = selection
        self._filter_changed(index)

    def open_tag_filter(self) -> KnowledgeTagFilterDialog | None:
        if (self._runner.busy or self.filter_loading or self._manual_filter_refresh_active
                or self._tag_filter_dialog is not None or self._category_dialog is not None
                or self._tags_dialog is not None or self._confirming_publish
                or self._confirming_archive or not self._tag_filter_options_ready):
            return None
        mode, value = self._selected_tag_filter
        selected_ids = (value,) if mode == "tag" else value if mode == "any" else ()
        dialog = KnowledgeTagFilterDialog(
            self._available_filter_tags, selected_ids, self.window()
        )
        self._tag_filter_dialog = dialog
        dialog.finished.connect(self._tag_filter_closed)
        self._update_actions(self._runner.busy)
        dialog.open()
        return dialog

    def _tag_filter_closed(self, result: int) -> None:
        dialog = self._tag_filter_dialog
        self._tag_filter_dialog = None
        self._update_actions(self._runner.busy)
        if result == KnowledgeTagFilterDialog.DialogCode.Accepted:
            selection = self._selection_for_tag_ids(dialog.selected_ids())
            if selection != self._selected_tag_filter:
                self._set_tag_filter_selection(selection)
                self._reload_results_after_filter_refresh()
        dialog.deleteLater()

    def _tag_filter_options_failed(self, error) -> None:
        logging.getLogger(__name__).error(
            "Knowledge tag filter options failed: %s", type(error).__name__
        )
        manual = (
            self._manual_filter_refresh_active
            and "tag" in self._manual_filter_refresh_pending
        )
        self.tag_filter_feedback.setText(
            "Could not refresh tag filters. Existing choices were retained. Try again."
            if manual else
            "Could not load specific tag filters. All tags and Untagged remain available. "
            "Select Refresh filters to retry."
        )
        self.tag_filter_feedback.show()
        self._tag_filter_options_ready = True
        if manual:
            self._manual_filter_source_settled("tag")
        self._update_actions(self._runner.busy)

    def _manual_filter_source_settled(
        self, source: str, *, selection_reset: bool = False,
    ) -> None:
        self._manual_filter_refresh_reset |= selection_reset
        self._manual_filter_refresh_pending.discard(source)
        if self._manual_filter_refresh_pending:
            return
        reload_results = self._manual_filter_refresh_reset
        self._manual_filter_refresh_active = False
        self._manual_filter_refresh_reset = False
        self._manual_category_filter_selection = None
        self._manual_tag_filter_selection = None
        self._update_actions(self._runner.busy)
        if reload_results:
            self._reload_results_after_filter_refresh()

    def _reload_results_after_filter_refresh(self) -> None:
        selected_id = self.article.knowledge_article_id if self.article else None
        if self._search_active:
            self.search_articles(query=self._search_query)
        else:
            self.refresh_list(load_filter_options=False, preserve_search_input=True)
        self._preferred_selection_id = selected_id

    def _filter_arguments(self) -> dict:
        arguments = {}
        if self.category_filter.currentIndex() == 1:
            arguments["uncategorized_only"] = True
        else:
            category_id = self.category_filter.currentData()
            if category_id is not None:
                arguments["category_id"] = category_id
        status = self.status_filter.currentData()
        if status is not None:
            arguments["status"] = status
        tag_mode, tag_id = self.tag_filter.currentData()
        if tag_mode == "untagged":
            arguments["untagged_only"] = True
        elif tag_mode == "tag":
            arguments["tag_id"] = tag_id
        elif tag_mode == "any":
            arguments["tag_ids"] = tag_id
        return arguments

    def _reset_category_filter(self) -> None:
        with QSignalBlocker(self.category_filter):
            self.category_filter.setCurrentIndex(0)

    def _reset_status_filter(self) -> None:
        with QSignalBlocker(self.status_filter):
            self.status_filter.setCurrentIndex(0)

    def _reset_tag_filter(self) -> None:
        self._set_tag_filter_selection(_TAG_FILTER_ALL)

    def _article_matches_tag_filter(self, article) -> bool:
        tag_mode, selected = self.tag_filter.currentData()
        tag_ids = getattr(article, "tag_ids", ())
        if tag_mode == "untagged":
            return not tag_ids
        if tag_mode == "tag":
            return selected in tag_ids
        if tag_mode == "any":
            return bool(set(selected).intersection(tag_ids))
        return True

    def _filter_changed(self, _index) -> None:
        if self._runner.busy:
            return
        selected_id = self.article.knowledge_article_id if self.article else None
        if self._search_active:
            self.search_articles(query=self._search_query)
        else:
            self.refresh_list()
        # A previous selection is a preference, not an explicit reveal request.
        self._preferred_selection_id = selected_id

    def refresh_list(
        self, *, select_article_id: int | None = None,
        load_filter_options: bool = True, preserve_search_input: bool = False,
    ) -> None:
        if self._runner.busy:
            return
        self._search_active = False
        self._search_query = ""
        if not preserve_search_input:
            self.search_input.clear()
        self._pending_selection_id = select_article_id
        self._show_article(None)
        self.articles = ()
        self.model.removeRows(0, self.model.rowCount())
        self.empty_state.setVisible(False)
        self.table.setVisible(True)
        self.feedback.setText("Loading articles…")
        arguments = self._filter_arguments()
        self._runner.submit(lambda: self._service.list_articles(**arguments), self._list_loaded, self._load_failed)
        if load_filter_options:
            self._load_filter_options()

    def search_articles(self, *, query: str | None = None) -> None:
        if self._runner.busy:
            return
        if query is None:
            query = self.search_input.text()
        if not query.strip():
            self.clear_search()
            return
        self._search_active = True
        self._search_query = query
        self._pending_selection_id = None
        self._show_article(None)
        self.articles = ()
        self.model.removeRows(0, self.model.rowCount())
        self.empty_state.setVisible(False)
        self.table.setVisible(True)
        self.feedback.setText("Searching knowledge articles…")
        arguments = self._filter_arguments()
        self._runner.submit(
            lambda: self._service.search_articles(query, **arguments),
            self._search_loaded,
            self._search_failed,
        )

    def clear_search(self) -> None:
        if self._runner.busy:
            return
        self.refresh_list()

    def open_new_article(self) -> NewArticleDialog | None:
        if self._runner.busy or self._category_dialog is not None or self._tags_dialog is not None:
            return None
        dialog = NewArticleDialog(self._service, self._runner, self)
        dialog.article_created.connect(self._article_created)
        dialog.open()
        self._new_article_dialog = dialog
        return dialog

    def open_edit_article(self) -> EditArticleDialog | None:
        if self._runner.busy or self._category_dialog is not None or self._tags_dialog is not None or self.article is None or self.article.status != "DRAFT":
            return None
        dialog = EditArticleDialog(self._service, self._runner, self.article, self)
        dialog.article_updated.connect(self._article_created)
        dialog.open()
        self._edit_article_dialog = dialog
        return dialog

    def open_category(self) -> ArticleCategoryDialog | None:
        if (self._service is None or self._runner.busy or self._category_dialog is not None or self._tags_dialog is not None
                or self._confirming_publish or self._confirming_archive
                or self.article is None or self.article.status != "DRAFT"):
            return None
        article = self.article
        dialog = ArticleCategoryDialog(
            self._service, self._runner, article,
            context_is_current=lambda: self.article is article,
            parent=self.window(),
        )
        self._category_dialog = dialog
        dialog.finished.connect(self._category_closed)
        dialog.article_updated.connect(self._category_updated)
        self._update_actions(self._runner.busy)
        dialog.open()
        dialog.load_categories()
        return dialog

    def _category_closed(self, _result):
        self._category_dialog = None
        self._update_actions(self._runner.busy)

    def _category_updated(self, article):
        # The repository already reloaded this record before committing.
        if self.category_filter.currentIndex() == 0:
            self._show_article(article)
            self.feedback.setText("Article category saved.")
        else:
            self._filter_changed(self.category_filter.currentIndex())

    def open_tags(self) -> ArticleTagsDialog | None:
        if (self._service is None or self._runner.busy or self._category_dialog is not None or self._tags_dialog is not None
                or self._confirming_publish or self._confirming_archive
                or self.article is None or self.article.status != "DRAFT"):
            return None
        article = self.article
        dialog = ArticleTagsDialog(
            self._service, self._runner, article,
            context_is_current=lambda: self.article is article,
            parent=self.window(),
        )
        self._tags_dialog = dialog
        dialog.finished.connect(self._tags_closed)
        dialog.article_updated.connect(self._tags_updated)
        self._update_actions(self._runner.busy)
        dialog.open()
        dialog.load_tags()
        return dialog

    def _tags_closed(self, _result):
        self._tags_dialog = None
        self._update_actions(self._runner.busy)

    def _tags_updated(self, article):
        # The repository reloaded the current tag set before its transaction committed.
        if self.tag_filter.currentData() == _TAG_FILTER_ALL:
            self._show_article(article)
            self.feedback.setText("Article tags saved.")
        else:
            self._filter_changed(self.tag_filter.currentIndex())

    def _confirm_publish(self, article) -> bool:
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Publish Article")
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setTextFormat(Qt.TextFormat.PlainText)
        confirmation.setText(f"Publish {article.article_code}: {article.title}?")
        confirmation.setInformativeText(
            "The article will become PUBLISHED. Content and version history are preserved. "
            "Published articles are not editable in the current workflow."
        )
        publish = confirmation.addButton("Publish", QMessageBox.ButtonRole.AcceptRole)
        cancel = confirmation.addButton(QMessageBox.StandardButton.Cancel)
        confirmation.setDefaultButton(cancel)
        confirmation.setEscapeButton(cancel)
        confirmation.exec()
        accepted = confirmation.clickedButton() == publish
        confirmation.deleteLater()
        return accepted

    def publish_article(self) -> None:
        if (self._service is None or self._runner.busy or self._confirming_publish or self._confirming_archive
                or self._category_dialog is not None or self._tags_dialog is not None
                or self.article is None or self.article.status != "DRAFT"):
            return
        article = self.article
        self._confirming_publish = True
        self._update_actions(self._runner.busy)
        try:
            confirmed = self._confirm_publish(article)
        finally:
            self._confirming_publish = False
            self._update_actions(self._runner.busy)
        # The modal confirmation runs an event loop; retain the reviewed token.
        if not confirmed or self._runner.busy or self.article is not article:
            return
        self.feedback.setText("Publishing article…")
        self._runner.submit(
            lambda: self._service.publish_article(
                article.knowledge_article_id, article.version_number,
            ),
            self._article_created,
            self._publish_failed,
        )

    def _publish_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge publish failed: %s", type(error).__name__)
        self.feedback.setText(
            str(error) if isinstance(error, KnowledgePublishError)
            else "Could not publish the article. Try again."
        )

    def _confirm_archive(self, article) -> bool:
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Archive Article")
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setTextFormat(Qt.TextFormat.PlainText)
        confirmation.setText(f"Archive {article.article_code}: {article.title}?")
        confirmation.setInformativeText(
            "The article will become ARCHIVED. Content and version history are preserved. "
            "Existing ticket relationships remain. This workflow does not provide Unarchive."
        )
        archive = confirmation.addButton("Archive", QMessageBox.ButtonRole.AcceptRole)
        cancel = confirmation.addButton(QMessageBox.StandardButton.Cancel)
        confirmation.setDefaultButton(cancel)
        confirmation.setEscapeButton(cancel)
        confirmation.exec()
        accepted = confirmation.clickedButton() == archive
        confirmation.deleteLater()
        return accepted

    def archive_article(self) -> None:
        if (self._service is None or self._runner.busy or self._confirming_archive or self._confirming_publish
                or self._category_dialog is not None or self._tags_dialog is not None
                or self.article is None or self.article.status != "PUBLISHED"):
            return
        article = self.article
        self._confirming_archive = True
        self._update_actions(self._runner.busy)
        try:
            confirmed = self._confirm_archive(article)
        finally:
            self._confirming_archive = False
            self._update_actions(self._runner.busy)
        # The modal confirmation runs an event loop; retain the reviewed token.
        if not confirmed or self._runner.busy or self.article is not article:
            return
        self.feedback.setText("Archiving article…")
        self._runner.submit(
            lambda: self._service.archive_article(
                article.knowledge_article_id, article.version_number,
            ),
            self._article_created,
            self._archive_failed,
        )

    def _archive_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge archive failed: %s", type(error).__name__)
        self.feedback.setText(
            str(error) if isinstance(error, KnowledgeArchiveError)
            else "Could not archive the article. Try again."
        )

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
        if self._runner.busy:
            return
        self._reset_category_filter()
        self._reset_status_filter()
        self._reset_tag_filter()
        self.refresh_list(select_article_id=article_id)

    def _article_created(self, article) -> None:
        arguments = self._filter_arguments()
        if ((arguments.get("uncategorized_only") and article.category_id is not None)
                or ("category_id" in arguments and arguments["category_id"] != article.category_id)):
            self._reset_category_filter()
        if arguments.get("status") not in (None, article.status):
            self._reset_status_filter()
        if not self._article_matches_tag_filter(article):
            self._reset_tag_filter()
        self.refresh_list(select_article_id=article.knowledge_article_id)

    def _list_loaded(self, articles) -> None:
        self.feedback.setText("")
        empty_text = "No knowledge articles yet."
        if self.category_filter.currentIndex() == 1:
            empty_text = "No uncategorized knowledge articles."
        elif self.category_filter.currentIndex() > 1:
            empty_text = "No knowledge articles in this category."
        status = self.status_filter.currentData()
        if status is not None:
            lifecycle = status.lower()
            if self.category_filter.currentIndex() == 1:
                empty_text = f"No uncategorized {lifecycle} knowledge articles."
            elif self.category_filter.currentIndex() > 1:
                empty_text = f"No {lifecycle} knowledge articles in this category."
            else:
                empty_text = f"No {lifecycle} knowledge articles."
        tag_mode, _tag_id = self.tag_filter.currentData()
        if tag_mode == "untagged":
            empty_text = "No untagged knowledge articles."
        elif tag_mode == "tag":
            empty_text = "No knowledge articles with this tag."
        elif tag_mode == "any":
            empty_text = "No knowledge articles with any selected tag."
        self._populate_articles(articles, empty_text)

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
        preferred_id = self._preferred_selection_id
        self._preferred_selection_id = None
        if target_id is not None and not any(
            article.knowledge_article_id == target_id for article in self.articles
        ):
            self._show_article(None)
            self.feedback.setText("The requested article no longer exists. Refresh the list and try again.")
            return
        if not self.articles:
            self._show_article(None)
            return
        if target_id is None:
            target_id = preferred_id
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
            self.detail_category.setText("")
            self.detail_tags.setText("")
            self.detail_summary.setText("")
            self.detail_body.clear()
            return
        self.detail_code.setText(article.article_code)
        self.detail_title.setText(article.title)
        self.detail_status.setText(f"Status: {article.status}")
        self.detail_version.setText(f"Version {article.version_number}")
        self.detail_category.setText(f"Category: {article.category_name or 'Not selected'}")
        tag_names = getattr(article, "tag_names", ())
        self.detail_tags.setText(f"Tags: {', '.join(tag_names) if tag_names else 'None'}")
        self.detail_summary.setText(
            f"Summary: {article.summary}" if article.summary else "Summary: Not provided"
        )
        self.detail_body.setPlainText(article.body_markdown)

    def _update_actions(self, busy: bool) -> None:
        busy = (busy or self._tag_filter_dialog is not None
                or self._manual_filter_refresh_active or self._confirming_publish
                or self._confirming_archive or self._category_dialog is not None
                or self._tags_dialog is not None)
        self.new_button.setEnabled(not busy)
        self.search_input.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.category_filter.setEnabled(
            not busy and self._filter_options_ready and not self._filter_runner.busy
        )
        self.status_filter.setEnabled(not busy)
        self.tag_filter.setEnabled(
            not busy and self._tag_filter_options_ready and not self._tag_filter_runner.busy
        )
        self.refresh_filters_button.setEnabled(
            self._service is not None and not busy and not self.filter_loading
        )
        self.clear_search_button.setEnabled(
            not busy and (self._search_active or bool(self.search_input.text()))
        )
        self.table.setEnabled(not busy)
        self.edit_button.setEnabled(
            not busy and self.article is not None and self.article.status == "DRAFT"
        )
        self.category_button.setEnabled(
            self._service is not None and not busy
            and self.article is not None and self.article.status == "DRAFT"
        )
        self.tags_button.setEnabled(
            self._service is not None and not busy
            and self.article is not None and self.article.status == "DRAFT"
        )
        self.version_history_button.setEnabled(
            self._service is not None and not busy and self.article is not None
        )
        self.publish_button.setEnabled(
            self._service is not None and not busy
            and self.article is not None and self.article.status == "DRAFT"
        )

        self.archive_button.setEnabled(
            self._service is not None and not busy
            and self.article is not None and self.article.status == "PUBLISHED"
        )

    def _load_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge load failed: %s", type(error).__name__)
        self.feedback.setText("Could not load knowledge articles. Try again.")

    def _search_failed(self, error: Exception) -> None:
        logging.getLogger(__name__).error("Knowledge search failed: %s", type(error).__name__)
        self.feedback.setText("Could not search knowledge articles. Check the query and try again.")

    def _search_text_changed(self, _text: str) -> None:
        self._update_actions(self._runner.busy)
