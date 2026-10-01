"""Read-only technician view of enabled PowerShell registry metadata."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSplitter, QTableView, QVBoxLayout, QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.script_management_dialog import ScriptManagementDialog
from f7hub.services.script_service import (
    AVAILABLE, INACCESSIBLE, INVALID_REFERENCE, MISSING,
    ScriptCatalogEntry, ScriptService,
    ScriptCopyError, ScriptValidationError,
)


_FILE_STATUSES = {AVAILABLE, MISSING, INACCESSIBLE, INVALID_REFERENCE}
_COPY_FEEDBACK = {
    "SCRIPT_NOT_ELIGIBLE": "Script is no longer eligible to copy.",
    "INVALID_REFERENCE": "Script reference is invalid. Copy blocked.",
    "FILE_UNAVAILABLE": "Script file is no longer available.",
    "READ_FAILED": "Script could not be read.",
    "INTEGRITY_NOT_APPROVED": "Script integrity has not been approved.",
    "INTEGRITY_MISMATCH": "Script changed since approval. Copy blocked.",
}


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
        self._copying = False
        self._text_query: str | None = None
        self._selection_generation = 0
        self._preferred_code: str | None = None
        self._management_dialog = None
        self._management_refresh_pending = False

        self.heading = QLabel("Scripts", self)
        self.heading.setObjectName("scriptsHeading")
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_list)
        self.copy_button = QPushButton("Copy Script", self)
        self.copy_button.setAccessibleName("Copy Script")
        self.copy_button.clicked.connect(self.copy_script)
        self.manage_button = QPushButton("Manage scripts…", self)
        self.manage_button.clicked.connect(self.open_management)
        heading_row = QHBoxLayout()
        heading_row.addWidget(self.heading)
        heading_row.addStretch()
        heading_row.addWidget(self.copy_button)
        heading_row.addWidget(self.manage_button)
        heading_row.addWidget(self.refresh_button)

        self.search_input = QLineEdit(self)
        self.search_input.setAccessibleName("Search script names, codes and descriptions")
        self.search_input.setPlaceholderText("Search names, codes and descriptions")
        self.search_input.returnPressed.connect(self.search_scripts)
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_scripts)
        self.clear_search_button = QPushButton("Clear", self)
        self.clear_search_button.clicked.connect(self.clear_search)
        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(self.search_button)
        search_row.addWidget(self.clear_search_button)

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
        layout.addLayout(search_row)
        layout.addWidget(self.feedback)
        layout.addWidget(splitter, 1)
        self._runner.busy_changed.connect(self._update_actions)
        self._runner.busy_changed.connect(self._finish_management_refresh)
        self._update_actions(self._runner.busy)

    def _update_actions(self, busy: bool) -> None:
        idle = not busy and not self._loading and not self._copying
        self.manage_button.setEnabled(idle and self._management_dialog is None)
        self.refresh_button.setEnabled(idle)
        for control in (self.search_input, self.search_button, self.clear_search_button):
            control.setEnabled(idle)
        row = self.table.currentIndex().row()
        available = 0 <= row < len(self._entries) and self._entries[row].file_status == AVAILABLE
        self.copy_button.setEnabled(available and not busy and not self._loading and not self._copying)

    def open_management(self):
        if self._runner.busy or self._loading or self._copying or self._management_dialog is not None:
            return None
        # Parent outside MainWindow.pages, which is disabled during worker calls.
        dialog = ScriptManagementDialog(self._service, self._runner, self.window())
        self._management_dialog = dialog
        dialog.finished.connect(self._management_closed)
        dialog.open()
        dialog.refresh_list()
        self._update_actions(self._runner.busy)
        return dialog

    def _management_closed(self, _result):
        dialog = self._management_dialog
        self._management_dialog = None
        self._management_refresh_pending = dialog.changed
        dialog.deleteLater()
        self._update_actions(self._runner.busy)
        self._finish_management_refresh(self._runner.busy)

    def _finish_management_refresh(self, busy):
        if not busy and self._management_refresh_pending:
            self._management_refresh_pending = False
            self.refresh_list()

    def copy_script(self) -> bool:
        """Verify source off-thread, then copy only a still-selected result."""
        row = self.table.currentIndex().row()
        if (self._runner.busy or self._loading or self._copying or
                not 0 <= row < len(self._entries) or self._entries[row].file_status != AVAILABLE):
            return False
        code = self._entries[row].metadata.script_code
        generation = self._selection_generation
        self._copying = True
        self.feedback.setText("Verifying script…")
        self._update_actions(True)

        def current() -> bool:
            selected = self.table.currentIndex().row()
            return (generation == self._selection_generation and self.isVisible() and
                    0 <= selected < len(self._entries) and
                    self._entries[selected].metadata.script_code == code)

        def succeeded(source: str) -> None:
            self._copying = False
            if current():
                QApplication.clipboard().setText(source)
                self.feedback.setText("PowerShell script copied to clipboard.")
            self._update_actions(self._runner.busy)

        def failed(error: object) -> None:
            self._copying = False
            if current():
                key = error.code if isinstance(error, ScriptCopyError) else "READ_FAILED"
                self.feedback.setText(_COPY_FEEDBACK.get(key, _COPY_FEEDBACK["READ_FAILED"]))
            self._update_actions(self._runner.busy)

        if not self._runner.submit(lambda: self._service.read_verified_script(code), succeeded, failed):
            self._copying = False
            self.feedback.setText("Script could not be read.")
            self._update_actions(self._runner.busy)
            return False
        return True

    def search_scripts(self) -> bool:
        if self._runner.busy or self._loading or self._copying:
            return False
        self._text_query = self.search_input.text().strip() or None
        return self.refresh_list()

    def clear_search(self) -> bool:
        if self._runner.busy or self._loading or self._copying:
            return False
        self.search_input.clear()
        self._text_query = None
        return self.refresh_list()

    def refresh_list(self) -> bool:
        """Read once on the shared runner; preserve selection only after success."""
        if self._runner.busy or self._loading or self._copying:
            return False
        query = self._text_query
        self._selection_generation += 1
        current = self.table.currentIndex()
        if current.isValid() and current.row() < len(self._entries):
            self._preferred_code = self._entries[current.row()].metadata.script_code
        self._loading = True
        self._entries = ()
        self.model.removeRows(0, self.model.rowCount())
        self.details.clear()
        self.empty_state.hide()
        self.feedback.setText("Loading scripts…")
        self._update_actions(True)
        if not self._runner.submit(lambda: self._service.list_scripts(text_query=query),
                                   lambda entries: self._loaded(entries, query), self._failed):
            self._failed(None)
            return False
        return True

    def _loaded(self, entries: tuple[ScriptCatalogEntry, ...], query: str | None) -> None:
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
        self.empty_state.setText("No scripts match your search." if query is not None
                                 else "No scripts available.")
        self.empty_state.setVisible(not self._entries)
        if self._entries:
            row = next((index for index, entry in enumerate(self._entries)
                        if entry.metadata.script_code == self._preferred_code), 0)
            self.table.selectRow(row)
            self.table.setCurrentIndex(self.model.index(row, 0))
            self._show_entry(self._entries[row])
        self._preferred_code = None
        self._update_actions(self._runner.busy)

    def _failed(self, error: object) -> None:
        self._loading = False
        self._preferred_code = None
        if isinstance(error, ScriptValidationError):
            self.feedback.setText("Search text is invalid. Edit it and select Search, or select Clear.")
        else:
            self.feedback.setText("Could not load scripts. Select Refresh to try again.")
        self.empty_state.hide()
        self._update_actions(self._runner.busy)

    def _selection_changed(self, *_args: object) -> None:
        self._selection_generation += 1
        row = self.table.currentIndex().row()
        if 0 <= row < len(self._entries):
            self._show_entry(self._entries[row])
        else:
            self.details.clear()
        if self._copying:
            self.feedback.clear()
        self._update_actions(self._runner.busy)

    def hideEvent(self, event) -> None:
        self._selection_generation += 1
        super().hideEvent(event)

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
