"""Bounded read-only Recent presentation using Clipboard owner projections."""

from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex, QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QHeaderView, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QTableView, QVBoxLayout, QWidget,
)

from f7hub.domain.clipboard import (ClipboardRecentItem, ClipboardRecentPage,
    ClipboardCopyItem, ClipboardCopyError, COPY_MAX_ITEMS)
from f7hub.infrastructure.windows_selected_copy import write_selected_text
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.clipboard_service import ClipboardService
from f7hub.gui.clipboard_setup import ClipboardSetup
from f7hub.services.settings_service import SettingsService


class ClipboardRecentTableModel(QAbstractTableModel):
    """Safe immutable rows plus transient check state; no full text or SQL."""

    selection_changed = Signal()

    HEADERS = ("Time", "Preview", "Source App", "Retention", "Pinned", "Select")
    CHECK_COLUMN = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: tuple[ClipboardRecentItem, ...] = ()
        self._checked: set[ClipboardCopyItem] = set()
        self._checking_enabled = True

    def replace_rows(self, rows: tuple[ClipboardRecentItem, ...]) -> None:
        self.beginResetModel()
        self._rows = rows
        self._checked.clear()
        self.endResetModel()
        self.selection_changed.emit()

    def selected_items(self):
        return tuple(ClipboardCopyItem(row.item_ref, row.revision) for row in self._rows
                     if ClipboardCopyItem(row.item_ref, row.revision) in self._checked)

    def clear_checks(self):
        if self._checked:
            self._checked.clear()
            self._checks_changed()

    def select_all_visible(self):
        if not self._checking_enabled or len(self._rows) > COPY_MAX_ITEMS:
            return
        self._checked = {ClipboardCopyItem(row.item_ref, row.revision) for row in self._rows}
        self._checks_changed()

    def set_checking_enabled(self, enabled):
        if self._checking_enabled != enabled:
            self._checking_enabled = enabled
            self._checks_changed()

    def _checks_changed(self):
        if self._rows:
            self.dataChanged.emit(self.index(0, self.CHECK_COLUMN),
                                  self.index(len(self._rows) - 1, self.CHECK_COLUMN),
                                  [Qt.ItemDataRole.CheckStateRole, Qt.ItemDataRole.AccessibleTextRole])
        self.selection_changed.emit()

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid() and index.column() == self.CHECK_COLUMN:
            flags = Qt.ItemFlag.ItemIsUserCheckable
            if self._checking_enabled:
                flags |= Qt.ItemFlag.ItemIsEnabled
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (not self._checking_enabled or not index.isValid()
                or index.column() != self.CHECK_COLUMN or not 0 <= index.row() < len(self._rows)
                or role != Qt.ItemDataRole.CheckStateRole
                or value not in (Qt.CheckState.Checked, Qt.CheckState.Unchecked,
                                 Qt.CheckState.Checked.value, Qt.CheckState.Unchecked.value)):
            return False
        row = self._rows[index.row()]
        item = ClipboardCopyItem(row.item_ref, row.revision)
        if value in (Qt.CheckState.Checked, Qt.CheckState.Checked.value):
            if item not in self._checked and len(self._checked) >= COPY_MAX_ITEMS:
                return False
            self._checked.add(item)
        else:
            self._checked.discard(item)
        self._checks_changed()
        return True

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
        if index.isValid() and 0 <= index.row() < len(self._rows) and index.column() == self.CHECK_COLUMN:
            row = self._rows[index.row()]
            checked = ClipboardCopyItem(row.item_ref, row.revision) in self._checked
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            if role == Qt.ItemDataRole.AccessibleTextRole:
                return f"Select item {index.row() + 1}: {'checked' if checked else 'unchecked'}"
            return None
        if (not index.isValid() or not 0 <= index.row() < len(self._rows)
                or not 0 <= index.column() < len(self.HEADERS)
                or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.AccessibleTextRole)):
            return None
        row = self._rows[index.row()]
        # D01 validates UTC milliseconds; keep UTC explicit and locale independent.
        values = (
            row.last_received_at.replace("T", " ").replace("Z", " UTC"),
            row.preview + (" … [truncated]" if row.preview_truncated else ""),
            row.source_process_basename or "Not recorded",
            "Temporary" if row.retention_intent == "TEMPORARY" else "Saved",
            "Yes" if row.is_pinned else "No",
        )
        return values[index.column()]


class ClipboardWorkspace(QWidget):
    """Retain two source surfaces; only F7Hub has a delivered read use case."""

    def __init__(self, parent=None, *, clipboard_service: ClipboardService | None = None,
                 settings_service: SettingsService | None = None,
                 capture_scroll=None, restore_scroll=None, copy_delivery=None) -> None:
        super().__init__(parent)
        self._service = clipboard_service
        self._copy_delivery = copy_delivery or write_selected_text
        self._copy_pending = False
        self.runner = ServiceTaskRunner(self)
        self.runner.completion_finished.connect(self._update_selection_controls)
        self._loading = False
        self._started = False
        self._recent_generation = 0
        self._source_key = "f7hub"
        self._capture_scroll = capture_scroll or (lambda: (0, 0))
        self._restore_scroll = restore_scroll or (lambda _position: None)
        self._source_scroll = {"f7hub": (0, 0), "windows": (0, 0)}
        self._source_focus = {"f7hub": None, "windows": None}
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
        outer = QVBoxLayout(self)
        outer.addWidget(self.heading)
        source_row = QHBoxLayout()
        self.source_label = QLabel("Source:", self)
        self.source_selector = QComboBox(self)
        self.source_selector.setObjectName("clipboardSourceSelector")
        self.source_selector.setAccessibleName("Clipboard source")
        self.source_selector.setAccessibleDescription(
            "Choose F7Hub Clipboard history or the current Windows Clipboard view.")
        self.source_selector.addItem("F7Hub Clipboard", "f7hub")
        self.source_selector.addItem("Windows Clipboard", "windows")
        self.source_label.setBuddy(self.source_selector)
        source_row.addWidget(self.source_label)
        source_row.addWidget(self.source_selector)
        source_row.addStretch()
        outer.addLayout(source_row)
        self.source_message = QLabel(self)
        self.source_message.setTextFormat(Qt.TextFormat.PlainText)
        self.source_message.setWordWrap(True)
        self.source_message.hide()
        outer.addWidget(self.source_message)
        self.source_pages = QStackedWidget(self)
        self.source_pages.setObjectName("clipboardSourcePages")
        self.f7hub_page = QWidget(self.source_pages)
        self.f7hub_page.setObjectName("f7hubClipboardSourcePage")
        self.source_pages.addWidget(self.f7hub_page)
        f7hub_layout = QVBoxLayout(self.f7hub_page)
        f7hub_layout.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.source_pages, 1)
        self.setup = None
        self.sections = None
        if settings_service is not None:
            navigation = QHBoxLayout()
            self.recent_button = QPushButton("Recent", self)
            self.setup_button = QPushButton("Clipboard Setup", self)
            self.recent_button.setAccessibleName("Recent Clipboard history")
            self.setup_button.setAccessibleName("Clipboard Setup")
            self.recent_button.clicked.connect(self.show_recent)
            self.setup_button.clicked.connect(self.show_setup)
            navigation.addWidget(self.recent_button)
            navigation.addWidget(self.setup_button)
            navigation.addStretch()
            f7hub_layout.addLayout(navigation)
            self.sections = QStackedWidget(self)
            self.recent_page = QWidget(self)
            self.sections.addWidget(self.recent_page)
            self.setup = ClipboardSetup(settings_service, self, clipboard_service=(clipboard_service
                if getattr(clipboard_service, 'supports_setup', False) else None))
            self.sections.addWidget(self.setup)
            f7hub_layout.addWidget(self.sections, 1)
            layout = QVBoxLayout(self.recent_page)
        else:
            layout = f7hub_layout
        layout.addWidget(self.status_message)
        self.refresh_button = None
        self.table = None
        self.model = None
        self.page_message = None
        self.select_all_button = self.clear_selection_button = self.copy_selected_button = None
        self.selected_count = None
        if self._service is not None:
            self.refresh_button = QPushButton("Refresh", self)
            self.refresh_button.setObjectName("clipboardRefreshButton")
            self.refresh_button.setAccessibleName("Refresh")
            self.refresh_button.clicked.connect(self.refresh)
            layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
            controls = QHBoxLayout()
            self.select_all_button = QPushButton("Select All Visible", self)
            self.clear_selection_button = QPushButton("Clear Selection", self)
            self.copy_selected_button = QPushButton("Copy Selected (0)", self)
            self.selected_count = QLabel("0 selected", self)
            self.selected_count.setTextFormat(Qt.TextFormat.PlainText)
            for button, name in ((self.select_all_button, "clipboardSelectAllVisibleButton"),
                                 (self.clear_selection_button, "clipboardClearSelectionButton"),
                                 (self.copy_selected_button, "clipboardCopySelectedButton")):
                button.setObjectName(name)
                button.setAccessibleName(button.text())
                controls.addWidget(button)
            self.selected_count.setObjectName("clipboardSelectedCount")
            controls.addWidget(self.selected_count)
            controls.addStretch()
            layout.addLayout(controls)
            self.copy_selected_button.setAccessibleDescription(
                "Copy complete selected F7Hub items in displayed order. Maximum 100 items and 65536 UTF-8 bytes. No automatic paste.")
            self.model = ClipboardRecentTableModel(self)
            self.model.selection_changed.connect(self._update_selection_controls)
            self.select_all_button.clicked.connect(self.model.select_all_visible)
            self.clear_selection_button.clicked.connect(self.model.clear_checks)
            self.copy_selected_button.clicked.connect(self.copy_selected)
            self.table = QTableView(self)
            self.table.setObjectName("clipboardRecentTable")
            self.table.setAccessibleName("Recent Clipboard history")
            self.table.setAccessibleDescription("Use arrow keys to move. Space toggles the current row checkbox; Tab leaves the table.")
            self.table.setModel(self.model)
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.table.setTabKeyNavigation(False)
            self.table.setSortingEnabled(False)
            self.table.setWordWrap(False)
            self.table.verticalHeader().hide()
            header = self.table.horizontalHeader()
            header.setSectionsClickable(False)
            header.moveSection(self.model.CHECK_COLUMN, 0)  # Keep checkboxes reachable at compact widths.
            header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(0, 230)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.setColumnWidth(2, 170)
            self.table.setColumnWidth(3, 105)
            self.table.setColumnWidth(4, 70)
            self.table.setColumnWidth(self.model.CHECK_COLUMN, 70)
            layout.addWidget(self.table, 1)
            self.page_message = QLabel(self)
            self.page_message.setTextFormat(Qt.TextFormat.PlainText)
            self.page_message.setWordWrap(True)
            layout.addWidget(self.page_message)
            self._set_status("Clipboard history has not been loaded.")
        if self._service is None:
            layout.addStretch()

        self.windows_page = QWidget(self.source_pages)
        self.windows_page.setObjectName("windowsClipboardSourcePage")
        self.windows_page.setAccessibleName("Windows Clipboard")
        windows_layout = QVBoxLayout(self.windows_page)
        windows_layout.setContentsMargins(0, 0, 0, 0)
        self.windows_heading = QLabel("Windows Clipboard", self.windows_page)
        self.windows_unavailable_message = QLabel(
            "Windows Clipboard snapshot is not available yet.", self.windows_page)
        self.windows_unavailable_message.setObjectName("windowsClipboardUnavailableMessage")
        self.windows_help = QLabel(
            "You can continue to use F7Hub Clipboard history and Clipboard Setup.", self.windows_page)
        for label in (self.windows_heading, self.windows_unavailable_message, self.windows_help):
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            label.setAccessibleName(label.text())
            windows_layout.addWidget(label)
        self.windows_refresh_button = QPushButton("Refresh", self.windows_page)
        self.windows_refresh_button.setObjectName("windowsClipboardRefreshButton")
        self.windows_refresh_button.setAccessibleName("Refresh Windows Clipboard")
        self.windows_refresh_button.setAccessibleDescription(
            "Windows Clipboard refresh is not available yet.")
        self.windows_refresh_button.setEnabled(False)
        windows_layout.addWidget(self.windows_refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
        windows_layout.addStretch()
        self.source_pages.addWidget(self.windows_page)
        self.source_selector.activated.connect(self._source_activated)
        for child in self.f7hub_page.findChildren(QWidget):
            child.installEventFilter(self)
        if self.sections is not None:
            QWidget.setTabOrder(self.source_selector, self.recent_button)
            QWidget.setTabOrder(self.recent_button, self.setup_button)
            if self.refresh_button is not None:
                QWidget.setTabOrder(self.setup_button, self.refresh_button)
        elif self.refresh_button is not None:
            QWidget.setTabOrder(self.source_selector, self.refresh_button)
        if self.refresh_button is not None:
            QWidget.setTabOrder(self.refresh_button, self.select_all_button)
            QWidget.setTabOrder(self.select_all_button, self.clear_selection_button)
            QWidget.setTabOrder(self.clear_selection_button, self.copy_selected_button)
            QWidget.setTabOrder(self.copy_selected_button, self.table)
        self._update_selection_controls()

    @property
    def source_key(self) -> str:
        return self._source_key

    def eventFilter(self, watched, event):
        if (watched is self.table and event.type() == QEvent.Type.KeyPress
                and event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.NoModifier):
            if not event.isAutoRepeat() and self.model is not None and self.model.rowCount():
                current = self.table.currentIndex()
                index = self.model.index(current.row() if current.isValid() else 0, self.model.CHECK_COLUMN)
                checked = self.model.data(index, Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
                self.model.setData(index, Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked,
                                   Qt.ItemDataRole.CheckStateRole)
            return True
        if event.type() == QEvent.Type.FocusIn and isinstance(watched, QWidget):
            if self.f7hub_page.isAncestorOf(watched):
                self._source_focus["f7hub"] = watched
        return super().eventFilter(watched, event)

    def _source_activated(self, index):
        self.select_source(self.source_selector.itemData(index))

    def _sync_source_selector(self):
        with QSignalBlocker(self.source_selector):
            self.source_selector.setCurrentIndex(self.source_selector.findData(self._source_key))

    def _source_feedback(self, text):
        self.source_message.setText(text)
        self.source_message.setAccessibleName(text)
        self.source_message.setVisible(bool(text))

    def select_source(self, key: str) -> bool:
        """Guard one presentation transition; never dispatch a service operation."""
        # activated arrives after Qt changed its candidate index. Restore the
        # committed value before a modal guard can expose inconsistent state.
        self._sync_source_selector()
        if key not in self._source_scroll:
            return False
        if key == self._source_key:
            return True
        previous_focus = self._source_focus[self._source_key]
        if self.loading or self.settings_pending:
            self._source_feedback("An operation is finishing. Change source when it completes.")
            return False
        if not self.confirm_leave():
            if self._usable_focus(previous_focus):
                previous_focus.setFocus(Qt.FocusReason.OtherFocusReason)
            return False
        self._source_scroll[self._source_key] = self._capture_scroll()
        if self._source_key == "f7hub":
            self.leave()
        self._source_key = key
        self._update_selection_controls()
        self.source_pages.setCurrentWidget(self.f7hub_page if key == "f7hub" else self.windows_page)
        self._sync_source_selector()
        self._source_feedback("")
        self.source_selector.setFocus(Qt.FocusReason.OtherFocusReason)
        # Synchronous restoration has no delayed callback that can overwrite a
        # newer source/module choice or later intentional scrolling.
        self.source_pages.layout().activate()
        self.layout().activate()
        self._restore_scroll(self._source_scroll[key])
        return True

    @staticmethod
    def _usable_focus(widget):
        try:
            return (widget is not None and widget.isVisible() and widget.isEnabled()
                    and widget.focusPolicy() != Qt.FocusPolicy.NoFocus)
        except RuntimeError:
            return False

    def activation_focus_target(self) -> QWidget | None:
        """Choose a usable control in the displayed section, if one exists."""
        if self._source_key == "windows":
            candidates = (self.source_selector,)
        elif self.setup is not None and self.sections.currentWidget() is self.setup:
            if self.setup.pending:
                candidates = (self.setup_button,)
            else:
                candidates = (*self.setup.checkboxes.values(), self.setup.reload_button,
                              self.setup.cancel_button, self.setup_button)
        else:
            candidates = (self.refresh_button,)
            if self.sections is not None:
                candidates += (self.recent_button,)
        for widget in (*candidates, self.source_selector):
            if widget is not None:
                try:
                    if (widget.isVisible() and widget.isEnabled()
                            and widget.focusPolicy() != Qt.FocusPolicy.NoFocus):
                        return widget
                except RuntimeError:
                    pass  # Qt may have destroyed a previously retained control.
        return None

    @property
    def loading(self) -> bool:
        # Covers the runner's idle-before-callback interval too.
        return self._copy_pending or self._loading or self.runner.busy or self.runner.completing

    @property
    def settings_pending(self) -> bool:
        return self.setup is not None and (self.setup.pending or self.setup.runner.completing)

    def confirm_leave(self) -> bool:
        if self._copy_pending or self.settings_pending:
            return False
        if self.setup is None:
            return True
        return self.setup.confirm_discard()

    def leave(self) -> None:
        if self._copy_pending:
            return
        if self.model is not None:
            self.model.clear_checks()
        if self.setup is not None:
            self.setup.end_session()
            self.sections.setCurrentWidget(self.recent_page)
            self._source_focus["f7hub"] = None

    def show_setup(self) -> bool:
        if self._source_key != "f7hub" or self._copy_pending or self.setup is None or not self.setup.reload():
            return False
        if self.model is not None:
            self.model.clear_checks()
        self.sections.setCurrentWidget(self.setup)
        self.setup.reload_button.setFocus()
        return True

    def show_recent(self) -> bool:
        if self._source_key != "f7hub" or not self.confirm_leave():
            return False
        self.leave()
        if self.refresh_button is not None:
            self.refresh_button.setFocus()
        return True

    def activate(self) -> bool:
        """Load once on accepted navigation; reuse pending/completed presentation."""
        return self.refresh() if self._source_key == "f7hub" and not self._started else False

    def refresh(self) -> bool:
        if self._source_key != "f7hub" or self._service is None or self.loading:
            return False
        self._loading = True
        self._update_selection_controls()
        self.model.replace_rows(())
        self.page_message.clear()
        self.page_message.setAccessibleName("")
        self._set_status("Loading Clipboard history…")
        self.refresh_button.setEnabled(False)
        self._recent_generation += 1
        generation = self._recent_generation
        accepted = self.runner.submit(
            self._service.get_recent,
            lambda page: self._recent_completed(generation, page),
            lambda error: self._recent_completed(generation, error, failed=True),
        )
        if accepted:
            self._started = True
        else:
            self._failed(None)
        return accepted

    def _update_selection_controls(self):
        if self.model is None:
            return
        count = len(self.model.selected_items())
        ready = not self.loading and self._source_key == "f7hub"
        self.model.set_checking_enabled(ready)
        self.selected_count.setText(f"{count} selected")
        self.selected_count.setAccessibleName(self.selected_count.text())
        self.copy_selected_button.setText(f"Copy Selected ({count})")
        self.copy_selected_button.setAccessibleName(self.copy_selected_button.text())
        self.copy_selected_button.setEnabled(ready and count > 0 and callable(getattr(self._service, "copy_selected", None)))
        self.select_all_button.setEnabled(ready and count < self.model.rowCount())
        self.clear_selection_button.setEnabled(ready and count > 0)
        self.refresh_button.setEnabled(ready)

    def copy_selected(self) -> bool:
        if (self._source_key != "f7hub" or self.loading or self.model is None
                or not callable(getattr(self._service, "copy_selected", None))):
            return False
        selection = self.model.selected_items()
        if not selection:
            return False
        owner_hwnd = int(self.window().winId())  # Qt access stays on the GUI thread.
        self._copy_pending = True
        self._set_status("Copying selected items…")
        self._update_selection_controls()
        generation = self._recent_generation
        delivery = self._copy_delivery
        accepted = self.runner.submit(
            lambda: self._service.copy_selected(selection, lambda text, guard: delivery(text, owner_hwnd, guard)),
            lambda outcome: self._copy_completed(generation, outcome),
            lambda error: self._copy_completed(generation, error, failed=True))
        if not accepted:
            self._copy_completed(generation, ClipboardCopyError("BUSY"), failed=True)
        return accepted

    def _copy_completed(self, generation, value, *, failed=False):
        self._copy_pending = False
        if generation != self._recent_generation:
            return
        if not failed and value == "WRITTEN":
            self._set_status("Selected items copied. Use Ctrl+V to paste.")
        else:
            error = value if isinstance(value, ClipboardCopyError) else ClipboardCopyError("UNAVAILABLE", "MAY_HAVE_CHANGED")
            if error.clipboard == "UNCHANGED":
                feedback = ("Selection is no longer eligible. Refresh and select again."
                            if error.code in {"DENIED", "STALE_SELECTION", "EXPIRED"} else
                            "Selection exceeds 100 items or 65536 UTF-8 bytes. Select fewer items."
                            if error.code == "TOO_LARGE" else "Selected items could not be copied. Clipboard was unchanged.")
            else:
                feedback = "Copy could not be verified. Clipboard may have changed. No automatic retry was made."
            if error.code in {"DENIED", "STALE_SELECTION", "EXPIRED"}:
                self.model.clear_checks()
            self._set_status(feedback)
        self._update_selection_controls()

    def _recent_completed(self, generation, value, *, failed=False):
        if generation != self._recent_generation:
            return
        if failed:
            self._failed(value)
        else:
            self._loaded(value)

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

    def closeEvent(self, event):
        if self.loading or not self.confirm_leave():
            event.ignore()
            return
        self.leave()
        self._recent_generation += 1
        super().closeEvent(event)
