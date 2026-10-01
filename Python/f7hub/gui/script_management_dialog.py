"""Local management of scoped script metadata and catalog visibility."""

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QHeaderView, QLabel,
    QMessageBox, QPlainTextEdit, QPushButton, QTableView, QVBoxLayout,
)

from f7hub.gui.register_script_dialog import RegisterScriptDialog
from f7hub.services.script_service import ScriptConflictError, ScriptValidationError, ScriptWriteError


class ScriptManagementDialog(QDialog):
    def __init__(self, service, runner, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._entries = ()
        self._loading = False
        self._writing = False
        self._closed = False
        self._confirming = False
        self._registration_dialog = None
        self._preferred_id = None
        self._committed_notice = ""
        self.changed = False
        self.setWindowTitle("Manage scripts")
        self.resize(840, 540)
        self.setMinimumSize(620, 440)
        note = QLabel("Enabled means visible in the catalog. It does not approve copying or execution.", self)
        note.setWordWrap(True)
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.model = QStandardItemModel(0, 4, self)
        self.model.setHorizontalHeaderLabels(("Name", "Code", "Enabled", "File status"))
        self.table = QTableView(self)
        self.table.setAccessibleName("Script registrations, including disabled")
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
        self.details.setMaximumHeight(150)
        self.details.setAccessibleName("Registration metadata, read only")
        self.register_button = QPushButton("Register script…", self)
        self.refresh_button = QPushButton("Refresh", self)
        self.toggle_button = QPushButton("Enable", self)
        self.close_button = QPushButton("Close", self)
        self.close_button.setDefault(True)
        for button in (self.register_button, self.refresh_button, self.toggle_button):
            button.setAutoDefault(False)
        self.register_button.clicked.connect(self.open_registration)
        self.refresh_button.clicked.connect(self.refresh_list)
        self.toggle_button.clicked.connect(self.toggle_selected)
        self.close_button.clicked.connect(self.reject)
        actions = QHBoxLayout()
        for button in (self.register_button, self.refresh_button, self.toggle_button):
            actions.addWidget(button)
        actions.addStretch()
        actions.addWidget(self.close_button)
        layout = QVBoxLayout(self)
        layout.addWidget(note)
        layout.addWidget(self.feedback)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.details)
        layout.addLayout(actions)
        self._runner.busy_changed.connect(self._update_actions)
        self._update_actions(self._runner.busy)

    def _selected(self):
        row = self.table.currentIndex().row()
        return self._entries[row].metadata if 0 <= row < len(self._entries) else None

    def _update_actions(self, busy):
        idle = not (busy or self._loading or self._writing or self._confirming
                    or self._registration_dialog is not None or self._closed)
        record = self._selected()
        self.register_button.setEnabled(idle)
        self.refresh_button.setEnabled(idle)
        self.toggle_button.setEnabled(idle and record is not None)
        self.toggle_button.setText("Disable" if record is not None and record.is_enabled else "Enable")
        self.table.setEnabled(idle)
        self.close_button.setEnabled(not self._writing and self._registration_dialog is None)

    def _selection_changed(self, *_args):
        record = self._selected()
        self.details.setPlainText("" if record is None else "\n".join((
            f"Name: {record.name}", f"Code: {record.script_code}",
            f"Reference: {record.relative_path}",
            f"Type: {record.script_type} | Runtime: {record.runtime}",
            f"Risk: {record.risk_level} | Privilege: {record.privilege_level}",
            f"Version: {record.version or 'Not specified'} | Category: {record.category_name or 'Not selected'}",
            f"Timeout: {record.timeout_seconds} seconds | Structured output: {'Yes' if record.requires_structured_output else 'No'}",
            f"Stored checksum: {record.checksum_sha256 or 'None'}",
            f"Description: {record.description or 'Not specified'}",
        )))
        self._update_actions(self._runner.busy)

    def refresh_list(self):
        if self._closed or self._runner.busy or self._writing or self._registration_dialog is not None:
            return False
        current = self._selected()
        if self._preferred_id is None and current is not None:
            self._preferred_id = current.script_id
        self._loading = True
        self._entries = ()
        self.model.removeRows(0, self.model.rowCount())
        self.details.clear()
        self.feedback.setText(self._committed_notice + " Loading registrations…")
        self._update_actions(True)
        if not self._runner.submit(self._service.list_registered_scripts, self._loaded, self._load_failed):
            self._load_failed(None)
            return False
        return True

    def _loaded(self, entries):
        self._loading = False
        if self._closed:
            return
        self._entries = tuple(entries)
        with QSignalBlocker(self.table.selectionModel()):
            for entry in self._entries:
                record = entry.metadata
                self.model.appendRow([QStandardItem(record.name), QStandardItem(record.script_code),
                                      QStandardItem("Yes" if record.is_enabled else "No"),
                                      QStandardItem(entry.file_status)])
        if self._entries:
            row = next((i for i, entry in enumerate(self._entries)
                        if entry.metadata.script_id == self._preferred_id), 0)
            self.table.selectRow(row)
            self.table.setCurrentIndex(self.model.index(row, 0))
        self._preferred_id = None
        self.feedback.setText(self._committed_notice or ("" if self._entries else "No registrations."))
        self._committed_notice = ""
        self._selection_changed()

    def _load_failed(self, _error):
        self._loading = False
        if self._closed:
            return
        self.feedback.setText((self._committed_notice + " Could not refresh registrations. Select Refresh to try again.").strip())
        self._update_actions(self._runner.busy)

    def open_registration(self):
        if self._closed or self._runner.busy or self._registration_dialog is not None:
            return None
        dialog = RegisterScriptDialog(self._service, self._runner, self)
        self._registration_dialog = dialog
        dialog.finished.connect(self._registration_closed)
        dialog.script_registered.connect(self._registered)
        self._update_actions(self._runner.busy)
        dialog.open()
        return dialog

    def _registration_closed(self, _result):
        dialog = self._registration_dialog
        self._registration_dialog = None
        self._update_actions(self._runner.busy)
        dialog.deleteLater()

    def _registered(self, record):
        self._committed(record, "Script registered disabled.")

    def toggle_selected(self):
        record = self._selected()
        if (record is None or self._closed or self._runner.busy or self._loading or self._writing
                or self._confirming or self._registration_dialog is not None):
            return False
        enabled = not bool(record.is_enabled)
        if enabled:
            self._confirming = True
            self._update_actions(False)
            box = QMessageBox(self)
            box.setWindowTitle("Enable script")
            box.setTextFormat(Qt.TextFormat.PlainText)
            box.setText(f"Make {record.name} visible in the catalog?\n{record.relative_path}\n\n"
                        "This does not approve script contents, copying or execution.")
            box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
            box.setDefaultButton(QMessageBox.StandardButton.Cancel)
            answer = box.exec()
            self._confirming = False
            self._update_actions(self._runner.busy)
            if answer != QMessageBox.StandardButton.Yes or self._selected() is not record or self._closed:
                return False
        self._writing = True
        self.feedback.setText("Changing catalog visibility…")
        self._update_actions(True)
        if not self._runner.submit(
            lambda: self._service.set_script_enabled(record.script_id, enabled=enabled,
                                                     expected_updated_at=record.updated_at),
            lambda saved: self._committed(saved, "Script enabled." if enabled else "Script disabled."),
            self._write_failed,
        ):
            self._write_failed(None)
            return False
        return True

    def _committed(self, record, notice):
        self._writing = False
        self.changed = True
        self._preferred_id = record.script_id
        self._committed_notice = notice
        self.refresh_list()

    def _write_failed(self, error):
        self._writing = False
        self.feedback.setText(str(error) if isinstance(error, (ScriptValidationError, ScriptWriteError))
                              else "Could not change script visibility. Refresh and try again.")
        if isinstance(error, ScriptConflictError):
            self._entries = ()
            self.model.removeRows(0, self.model.rowCount())
            self.details.clear()
        self._update_actions(self._runner.busy)

    def done(self, result):
        if not self._writing and not self._confirming and self._registration_dialog is None:
            self._closed = True
            super().done(result)

    def closeEvent(self, event):
        if self._writing or self._confirming or self._registration_dialog is not None:
            event.ignore()
        else:
            super().closeEvent(event)
