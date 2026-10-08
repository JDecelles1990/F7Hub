"""Bounded read-only Recent presentation using Clipboard owner projections."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QHeaderView, QLabel, QPushButton, QTableView, QVBoxLayout, QWidget,
)

from f7hub.domain.clipboard import ClipboardRecentItem, ClipboardRecentPage
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.clipboard_service import ClipboardService


class ClipboardRecentTableModel(QAbstractTableModel):
    """Present immutable safe rows; no owner reads, edits or selection contract."""

    HEADERS = ("Time", "Preview", "Retention", "Pinned")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: tuple[ClipboardRecentItem, ...] = ()

    def replace_rows(self, rows: tuple[ClipboardRecentItem, ...]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal
                and 0 <= section < len(self.HEADERS)):
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if (not index.isValid() or not 0 <= index.row() < len(self._rows)
                or not 0 <= index.column() < len(self.HEADERS)
                or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.AccessibleTextRole)):
            return None
        row = self._rows[index.row()]
        # D01 validates UTC milliseconds; keep UTC explicit and locale independent.
        values = (
            row.last_received_at.replace("T", " ").replace("Z", " UTC"),
            row.preview + (" … [truncated]" if row.preview_truncated else ""),
            "Temporary" if row.retention_intent == "TEMPORARY" else "Saved",
            "Yes" if row.is_pinned else "No",
        )
        return values[index.column()]


class ClipboardWorkspace(QWidget):
    """Own one independent asynchronous first-page read and its presentation."""

    tickets_requested = Signal()

    def __init__(self, parent=None, *, clipboard_service: ClipboardService | None = None) -> None:
        super().__init__(parent)
        self._service = clipboard_service
        self.runner = ServiceTaskRunner(self)
        self._loading = False
        self._started = False
        self.setObjectName("clipboardWorkspace")
        self.setAccessibleName("Clipboard Center")
        self.setProperty("moduleKey", "clipboard")

        self.heading = QLabel("Clipboard Center", self)
        self.heading.setObjectName("clipboardHeading")
        self.heading.setTextFormat(Qt.TextFormat.PlainText)
        self.heading.setAccessibleName("Clipboard Center")
        self.unavailable_message = QLabel("Clipboard history is not available yet.", self)
        self.unavailable_message.setObjectName("clipboardUnavailableMessage")
        self.unavailable_message.setTextFormat(Qt.TextFormat.PlainText)
        self.unavailable_message.setWordWrap(True)
        self.unavailable_message.setAccessibleName(self.unavailable_message.text())
        self.status_message = self.unavailable_message
        self.back_button = QPushButton("Back to Tickets", self)
        self.back_button.setObjectName("clipboardBackToTicketsButton")
        self.back_button.setAccessibleName("Back to Tickets")
        self.back_button.clicked.connect(self.tickets_requested.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.status_message)
        self.refresh_button = None
        self.table = None
        self.model = None
        self.page_message = None
        if self._service is not None:
            self.refresh_button = QPushButton("Refresh", self)
            self.refresh_button.setObjectName("clipboardRefreshButton")
            self.refresh_button.setAccessibleName("Refresh")
            self.refresh_button.clicked.connect(self.refresh)
            layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
            self.model = ClipboardRecentTableModel(self)
            self.table = QTableView(self)
            self.table.setObjectName("clipboardRecentTable")
            self.table.setAccessibleName("Recent Clipboard history")
            self.table.setModel(self.model)
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.table.setSortingEnabled(False)
            self.table.setWordWrap(False)
            self.table.verticalHeader().hide()
            header = self.table.horizontalHeader()
            header.setSectionsClickable(False)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 230)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.setColumnWidth(2, 105)
            self.table.setColumnWidth(3, 70)
            layout.addWidget(self.table, 1)
            self.page_message = QLabel(self)
            self.page_message.setTextFormat(Qt.TextFormat.PlainText)
            self.page_message.setWordWrap(True)
            layout.addWidget(self.page_message)
            self._set_status("Clipboard history has not been loaded.")
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        if self._service is None:
            layout.addStretch()

    @property
    def loading(self) -> bool:
        # Covers the runner's idle-before-callback interval too.
        return self._loading or self.runner.busy

    def activate(self) -> bool:
        """Load once on accepted navigation; reuse pending/completed presentation."""
        return self.refresh() if not self._started else False

    def refresh(self) -> bool:
        if self._service is None or self.loading:
            return False
        self._loading = True
        self.model.replace_rows(())
        self.page_message.clear()
        self.page_message.setAccessibleName("")
        self._set_status("Loading Clipboard history…")
        self.refresh_button.setEnabled(False)
        accepted = self.runner.submit(self._service.get_recent, self._loaded, self._failed)
        if accepted:
            self._started = True
        else:
            self._failed(None)
        return accepted

    def _set_status(self, text: str) -> None:
        self.status_message.setText(text)
        self.status_message.setAccessibleName(text)

    def _loaded(self, page: ClipboardRecentPage) -> None:
        self.model.replace_rows(page.rows)
        count = len(page.rows)
        self._set_status("" if count else "No recent Clipboard history is available.")
        summary = f"Showing {count} recent items."
        if page.has_more:
            summary += " More items are available."
        self.page_message.setText(summary)
        self.page_message.setAccessibleName(summary)
        self._finish("Refresh")

    def _failed(self, _error) -> None:
        # Exception details and previews must never enter feedback or logs.
        self._set_status("Clipboard history could not be loaded.")
        self._finish("Retry")

    def _finish(self, action: str) -> None:
        self._loading = False
        self.refresh_button.setText(action)
        self.refresh_button.setAccessibleName(action)
        self.refresh_button.setEnabled(True)
