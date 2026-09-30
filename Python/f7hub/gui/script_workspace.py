"""Read-only technician view of enabled PowerShell registry metadata."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QPlainTextEdit,
    QPushButton, QSplitter, QTableView, QVBoxLayout, QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.script_service import (
    AVAILABLE, INACCESSIBLE, INVALID_REFERENCE, MISSING,
    ScriptCatalogEntry, ScriptService,
)


_FILE_STATUSES = {AVAILABLE, MISSING, INACCESSIBLE, INVALID_REFERENCE}


def _status_text(status: str) -> str:
    return status if status in _FILE_STATUSES else "Unknown"


class ScriptWorkspace(QWidget):
    """Display service-returned catalog entries without inspecting script files."""

    def __init__(self, service: ScriptService, runner: ServiceTaskRunner, parent=None) -> None:
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._entries: tuple[ScriptCatalogEntry, ...] = ()
        self._loading = False
        self._preferred_code: str | None = None

        self.heading = QLabel("Scripts", self)
        self.heading.setObjectName("scriptsHeading")
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_list)
        heading_row = QHBoxLayout()
        heading_row.addWidget(self.heading)
        heading_row.addStretch()
        heading_row.addWidget(self.refresh_button)

        self.feedback = QLabel("", self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.empty_state = QLabel("No scripts available.", self)
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.hide()

        self.model = QStandardItemModel(0, 4, self)
        self.model.setHorizontalHeaderLabels(("Name", "Code", "Category", "File status"))
        self.table = QTableView(self)
        self.table.setAccessibleName("Enabled scripts; select a row to read metadata")
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.table.selectionModel().selectionChanged.connect(self._selection_changed)

        self.details = QPlainTextEdit(self)
        self.details.setReadOnly(True)
        self.details.setAccessibleName("Script metadata, read only")
        self.details.setPlaceholderText("Select a script to read its metadata.")

        list_panel = QWidget(self)
        list_layout = QVBoxLayout(list_panel)
        list_layout.addWidget(self.table, 1)
        list_layout.addWidget(self.empty_state)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(list_panel)
        splitter.addWidget(self.details)
        splitter.setSizes((560, 440))

        layout = QVBoxLayout(self)
        layout.addLayout(heading_row)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)
        self._runner.busy_changed.connect(self._update_refresh)
        self._update_refresh(self._runner.busy)

    def _update_refresh(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy and not self._loading)

    def refresh_list(self) -> bool:
        """Read once on the shared runner; preserve selection only after success."""
        if self._runner.busy or self._loading:
            return False
        current = self.table.currentIndex()
        if current.isValid() and current.row() < len(self._entries):
            self._preferred_code = self._entries[current.row()].metadata.script_code
        self._loading = True
        self._entries = ()
        self.model.removeRows(0, self.model.rowCount())
        self.details.clear()
        self.empty_state.hide()
        self.feedback.setText("Loading scripts…")
        self._update_refresh(True)
        if not self._runner.submit(self._service.list_scripts, self._loaded, self._failed):
            self._failed(None)
            return False
        return True

    def _loaded(self, entries: tuple[ScriptCatalogEntry, ...]) -> None:
        self._loading = False
        self._entries = tuple(entries)
        with QSignalBlocker(self.table.selectionModel()):
            for entry in self._entries:
                record = entry.metadata
                self.model.appendRow([
                    QStandardItem(record.name), QStandardItem(record.script_code),
                    QStandardItem(record.category_name or "Not selected"),
                    QStandardItem(_status_text(entry.file_status)),
                ])
        self.feedback.clear()
        self.empty_state.setVisible(not self._entries)
        if self._entries:
            row = next((index for index, entry in enumerate(self._entries)
                        if entry.metadata.script_code == self._preferred_code), 0)
            self.table.selectRow(row)
            self.table.setCurrentIndex(self.model.index(row, 0))
            self._show_entry(self._entries[row])
        self._preferred_code = None
        self._update_refresh(self._runner.busy)

    def _failed(self, _error: object) -> None:
        self._loading = False
        self._preferred_code = None
        self.feedback.setText("Could not load scripts. Select Refresh to try again.")
        self.empty_state.hide()
        self._update_refresh(self._runner.busy)

    def _selection_changed(self, *_args: object) -> None:
        row = self.table.currentIndex().row()
        if 0 <= row < len(self._entries):
            self._show_entry(self._entries[row])
        else:
            self.details.clear()

    def _show_entry(self, entry: ScriptCatalogEntry) -> None:
        record = entry.metadata
        status = _status_text(entry.file_status)
        status_note = " (File found at last refresh.)" if status == AVAILABLE else ""
        self.details.setPlainText("\n".join((
            f"Name: {record.name}",
            f"Code: {record.script_code}",
            f"Category: {record.category_name or 'Not selected'}",
            f"Description: {record.description or 'Not provided'}",
            f"Type: {record.script_type}",
            f"Runtime: {record.runtime}",
            f"Risk: {record.risk_level}",
            f"Privilege: {record.privilege_level}",
            f"PowerShell reference: {record.relative_path}",
            f"File status: {status}{status_note}",
        )))
