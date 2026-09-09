"""Asynchronous, read-only viewer for immutable knowledge revisions."""

import logging

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.knowledge_repository import KnowledgeArticleRecord
from f7hub.services.knowledge_service import (
    KnowledgeHistoryArticleMissingError,
    KnowledgeHistoryError,
    KnowledgeHistoryVersionMissingError,
    KnowledgeService,
)


class VersionHistoryDialog(QDialog):
    """List lightweight revisions and load only the selected snapshot body."""

    def __init__(
        self,
        service: KnowledgeService,
        runner: ServiceTaskRunner,
        article: KnowledgeArticleRecord,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._article_id = article.knowledge_article_id
        self._current_version_number = article.version_number
        self._active = True
        self._request_generation = 0
        self.versions = ()
        self.version = None
        self.setWindowTitle(f"Version History — {article.article_code}")
        self.setMinimumSize(760, 520)
        self.resize(900, 620)

        self.feedback = QLabel("Loading version history…", self)
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)

        self.model = QStandardItemModel(0, 4, self)
        self.model.setHorizontalHeaderLabels(("Version", "Title", "Created", "Created by"))
        self.table = QTableView(self)
        self.table.setAccessibleName("Knowledge article version history")
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.selectionModel().selectionChanged.connect(self._selection_changed)

        self.detail_version = QLabel("Select a revision to read.", self)
        self.detail_title = QLabel("", self)
        self.detail_summary = QLabel("", self)
        self.detail_created_at = QLabel("", self)
        self.detail_created_by = QLabel("", self)
        self.detail_change_summary = QLabel("", self)
        for label in (
            self.detail_version,
            self.detail_title,
            self.detail_summary,
            self.detail_created_at,
            self.detail_created_by,
            self.detail_change_summary,
        ):
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.detail_body = QPlainTextEdit(self)
        self.detail_body.setReadOnly(True)
        self.detail_body.setAccessibleName("Historical knowledge article body, read only")

        list_panel = QWidget(self)
        list_layout = QVBoxLayout(list_panel)
        list_layout.addWidget(self.table)
        detail_panel = QWidget(self)
        detail_layout = QVBoxLayout(detail_panel)
        metadata_panel = QWidget(self)
        metadata_layout = QVBoxLayout(metadata_panel)
        metadata_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        for label in (
            self.detail_version,
            self.detail_title,
            self.detail_summary,
            self.detail_created_at,
            self.detail_created_by,
            self.detail_change_summary,
        ):
            metadata_layout.addWidget(label)
        self.metadata_scroll = QScrollArea(self)
        self.metadata_scroll.setAccessibleName("Historical revision metadata, read only")
        self.metadata_scroll.setWidgetResizable(True)
        self.metadata_scroll.setWidget(metadata_panel)
        self.metadata_scroll.setMinimumHeight(120)
        self.metadata_scroll.setMaximumHeight(230)
        detail_layout.addWidget(self.metadata_scroll)
        self.detail_body.setMinimumHeight(150)
        detail_layout.addWidget(self.detail_body, 1)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(list_panel)
        splitter.addWidget(detail_panel)
        splitter.setSizes((390, 500))

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.reject)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.close_button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)
        layout.addLayout(actions)
        self._runner.busy_changed.connect(self._busy_changed)

    def load_history(self) -> None:
        if not self._active or self._runner.busy:
            return
        self._request_generation += 1
        generation = self._request_generation
        self.feedback.setText("Loading version history…")
        self.table.setEnabled(False)
        accepted = self._runner.submit(
            lambda: self._service.list_article_versions(self._article_id),
            lambda versions: self._history_loaded(generation, versions),
            lambda error: self._history_failed(generation, error),
        )
        if not accepted:
            self.table.setEnabled(True)

    def _history_loaded(self, generation: int, versions) -> None:
        if not self._accepts(generation):
            return
        self.versions = tuple(versions)
        self.model.removeRows(0, self.model.rowCount())
        for version in self.versions:
            values = (
                str(version.version_number),
                version.title,
                version.created_at,
                version.created_by or "Not provided",
            )
            items = [QStandardItem(value) for value in values]
            items[0].setData(version.version_number, Qt.ItemDataRole.UserRole)
            self.model.appendRow(items)
        if not self.versions:
            self.feedback.setText("No version history is available for this article.")
            self._show_version(None)
            return
        self.feedback.setText("")
        row = next(
            (
                index
                for index, version in enumerate(self.versions)
                if version.version_number == self._current_version_number
            ),
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
        if not indexes or not self._active or self._runner.busy:
            return
        version_number = self.model.item(indexes[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        self._load_version(int(version_number))

    def _load_version(self, version_number: int) -> None:
        self._request_generation += 1
        generation = self._request_generation
        self.feedback.setText(f"Loading Version {version_number}…")
        self._show_version(None)
        self._runner.submit(
            lambda: self._service.get_article_version(self._article_id, version_number),
            lambda version: self._version_loaded(generation, version_number, version),
            lambda error: self._version_failed(generation, version_number, error),
        )

    def _version_loaded(self, generation: int, requested_version: int, version) -> None:
        if not self._accepts(generation) or version.version_number != requested_version:
            return
        current = self.table.currentIndex()
        current_version = (
            None
            if not current.isValid()
            else self.model.item(current.row(), 0).data(Qt.ItemDataRole.UserRole)
        )
        if current_version != requested_version:
            return
        self.feedback.setText("")
        self._show_version(version)

    def _history_failed(self, generation: int, error: Exception) -> None:
        if not self._accepts(generation):
            return
        self.model.removeRows(0, self.model.rowCount())
        self.versions = ()
        self._show_version(None)
        self._show_error(error, "Could not load version history. Close and try again.")

    def _version_failed(
        self, generation: int, _requested_version: int, error: Exception,
    ) -> None:
        if not self._accepts(generation):
            return
        self._show_version(None)
        self._show_error(error, "Could not load the selected revision. Close and try again.")

    def _show_error(self, error: Exception, fallback: str) -> None:
        if isinstance(
            error,
            (
                KnowledgeHistoryArticleMissingError,
                KnowledgeHistoryVersionMissingError,
                KnowledgeHistoryError,
            ),
        ):
            self.feedback.setText(str(error))
        else:
            logging.getLogger(__name__).error(
                "Knowledge history load failed: %s", type(error).__name__
            )
            self.feedback.setText(fallback)

    def _show_version(self, version) -> None:
        self.version = version
        if version is None:
            self.detail_version.setText("Select a revision to read.")
            self.detail_title.setText("")
            self.detail_summary.setText("")
            self.detail_created_at.setText("")
            self.detail_created_by.setText("")
            self.detail_change_summary.setText("")
            self.detail_body.clear()
            return
        self.detail_version.setText(f"Version {version.version_number}")
        self.detail_title.setText(version.title)
        self.detail_summary.setText(
            f"Summary: {version.summary}" if version.summary else "Summary: Not provided"
        )
        self.detail_created_at.setText(f"Created at: {version.created_at}")
        self.detail_created_by.setText(f"Created by: {version.created_by or 'Not provided'}")
        self.detail_change_summary.setText(
            f"Change summary: {version.change_summary or 'Not provided'}"
        )
        self.detail_body.setPlainText(version.body_markdown)

    def _busy_changed(self, busy: bool) -> None:
        if self._active:
            self.table.setEnabled(not busy)

    def _accepts(self, generation: int) -> bool:
        return self._active and generation == self._request_generation

    def reject(self) -> None:
        self._active = False
        self._request_generation += 1
        super().reject()

    def closeEvent(self, event) -> None:
        self._active = False
        self._request_generation += 1
        super().closeEvent(event)
