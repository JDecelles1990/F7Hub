"""Saved-ticket list and detail presentation backed by TicketService."""

import logging

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPushButton, QSplitter, QTabWidget,
    QTableView, QTextEdit, QVBoxLayout, QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.ticket_service import TICKET_NOTE_TYPES, TICKET_STATUSES, TicketValidationError


class TicketTableModel(QAbstractTableModel):
    columns = (("Number", "ticket_number"), ("Subject", "subject"),
               ("Status", "status"), ("Priority", "priority"))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tickets = ()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.tickets)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            return str(getattr(self.tickets[index.row()], self.columns[index.column()][1]))
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.columns[section][0]
        return None

    def replace_tickets(self, tickets):
        self.beginResetModel()
        self.tickets = tuple(tickets)
        self.endResetModel()


def _plain_editor(parent, *, read_only=False):
    editor = QTextEdit(parent)
    editor.setAcceptRichText(False)
    editor.setReadOnly(read_only)
    return editor


class TicketWorkspace(QWidget):
    PAGE_SIZE = 100

    def __init__(self, service, runner: ServiceTaskRunner, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self.details = None
        self._offset = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)
        splitter = QSplitter(self)
        layout.addWidget(splitter)
        queue = QWidget(splitter)
        queue_layout = QVBoxLayout(queue)
        filters = QHBoxLayout()
        self.status_filter = QComboBox(queue)
        self.status_filter.setAccessibleName("Filter tickets by status")
        self.status_filter.addItem("All statuses", None)
        for status in sorted(TICKET_STATUSES):
            self.status_filter.addItem(status.replace("_", " ").title(), status)
        self.refresh_button = QPushButton("Refresh", queue)
        self.refresh_button.clicked.connect(lambda: self.refresh_list())
        self.status_filter.currentIndexChanged.connect(lambda: self.refresh_list(offset=0))
        filters.addWidget(self.status_filter)
        filters.addWidget(self.refresh_button)
        queue_layout.addLayout(filters)
        self.model = TicketTableModel(self)
        self.table = QTableView(queue)
        self.table.setAccessibleName("Saved tickets; activate a row to open")
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.activated.connect(self._activate_row)
        queue_layout.addWidget(self.table)
        open_button = QPushButton("Open selected ticket", queue)
        open_button.clicked.connect(lambda: self._activate_row(self.table.currentIndex()))
        queue_layout.addWidget(open_button)
        pages = QHBoxLayout()
        self.previous_button = QPushButton("Previous", queue)
        self.next_button = QPushButton("Next", queue)
        self.page_label = QLabel(queue)
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.previous_button.clicked.connect(lambda: self.refresh_list(offset=self._offset - self.PAGE_SIZE))
        self.next_button.clicked.connect(lambda: self.refresh_list(offset=self._offset + self.PAGE_SIZE))
        for widget in (self.previous_button, self.page_label, self.next_button):
            pages.addWidget(widget)
        queue_layout.addLayout(pages)

        self.detail_panel = QWidget(splitter)
        detail_layout = QVBoxLayout(self.detail_panel)
        self.heading = QLabel("Open a ticket to see its details", self.detail_panel)
        self.heading.setTextFormat(Qt.TextFormat.PlainText)
        self.heading.setWordWrap(True)
        detail_layout.addWidget(self.heading)
        tabs = QTabWidget(self.detail_panel)
        self.summary = _plain_editor(tabs, read_only=True)
        self.notes_history = _plain_editor(tabs, read_only=True)
        self.timeline = _plain_editor(tabs, read_only=True)
        tabs.addTab(self.summary, "Details")
        tabs.addTab(self.notes_history, "Notes")
        tabs.addTab(self.timeline, "History & timeline")
        detail_layout.addWidget(tabs)
        self.author_input = QLineEdit(self.detail_panel)
        self.author_input.setPlaceholderText("Your name (optional)")
        self.author_input.setAccessibleName("Activity author")
        detail_layout.addWidget(self.author_input)
        self.note_type = QComboBox(self.detail_panel)
        for kind in sorted(TICKET_NOTE_TYPES):
            self.note_type.addItem(kind.title(), kind)
        self.note_type.setAccessibleName("Note type")
        self.note_input = _plain_editor(self.detail_panel)
        self.note_input.setPlaceholderText("Add a support note…")
        self.note_input.setAccessibleName("New note")
        self.note_input.setMaximumHeight(85)
        self.add_note_button = QPushButton("Add note", self.detail_panel)
        self.add_note_button.clicked.connect(self.add_note)
        note_actions = QHBoxLayout()
        note_actions.addWidget(self.note_type)
        note_actions.addWidget(self.add_note_button)
        detail_layout.addWidget(self.note_input)
        detail_layout.addLayout(note_actions)
        self.status_input = QComboBox(self.detail_panel)
        self.status_input.setAccessibleName("New ticket status")
        self.reason_input = QLineEdit(self.detail_panel)
        self.reason_input.setAccessibleName("Status change reason")
        self.reason_input.setPlaceholderText("Reason (optional)")
        self.resolution_input = _plain_editor(self.detail_panel)
        self.resolution_input.setAccessibleName("Resolution summary")
        self.resolution_input.setPlaceholderText("Resolution summary (required to resolve)")
        self.resolution_input.setMaximumHeight(75)
        self.resolution_input.setVisible(False)
        self.status_input.currentIndexChanged.connect(
            lambda: self.resolution_input.setVisible(self.status_input.currentData() == "RESOLVED")
        )
        form = QFormLayout()
        form.addRow("Change status", self.status_input)
        form.addRow("Reason", self.reason_input)
        detail_layout.addLayout(form)
        detail_layout.addWidget(self.resolution_input)
        self.change_status_button = QPushButton("Apply status", self.detail_panel)
        self.change_status_button.clicked.connect(self.change_status)
        detail_layout.addWidget(self.change_status_button)
        self.reload_button = QPushButton("Reload ticket", self.detail_panel)
        self.reload_button.clicked.connect(lambda: self.open_ticket(self.details.ticket.ticket_id) if self.details else None)
        detail_layout.addWidget(self.reload_button)
        self.detail_panel.setEnabled(False)
        splitter.setSizes([460, 620])

    def refresh_list(self, *, offset=None, message=None):
        if self._runner.busy:
            return
        target = self._offset if offset is None else max(0, offset)
        status = self.status_filter.currentData()
        self.feedback.setText("Loading tickets…")

        def loaded(tickets):
            self._offset = target
            self.model.replace_tickets(tickets[:self.PAGE_SIZE])
            self.previous_button.setEnabled(target > 0)
            self.next_button.setEnabled(len(tickets) > self.PAGE_SIZE)
            self.page_label.setText(f"Page {target // self.PAGE_SIZE + 1}")
            self.feedback.setText(message or ("No tickets match this filter." if not tickets else "Double-click a ticket or select it and press Open."))

        self._runner.submit(
            lambda: self._service.list_tickets(status=status, limit=self.PAGE_SIZE + 1, offset=target),
            loaded, lambda error: self._show_error(error, (message + " " if message else "") + "Could not refresh tickets. Previous results are still shown."),
        )

    def _activate_row(self, index):
        if index.isValid():
            self.open_ticket(self.model.tickets[index.row()].ticket_id)

    def has_draft(self):
        return bool(self.note_input.toPlainText().strip() or self.reason_input.text().strip()
                    or self.resolution_input.toPlainText().strip() or self.status_input.currentData())

    def confirm_discard(self):
        if not self.has_draft():
            return True
        return QMessageBox.question(
            self, "Unsaved ticket activity", "Discard the unsaved note or status change?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        ) == QMessageBox.StandardButton.Discard

    def open_ticket(self, ticket_id, *, refresh_queue=False):
        if self._runner.busy:
            return
        switching = self.details is not None and self.details.ticket.ticket_id != ticket_id
        if switching and not self.confirm_discard():
            return
        self.feedback.setText("Loading ticket…")

        def loaded(details):
            if switching:
                self._clear_drafts()
            self._display_details(details)
            self.feedback.setText("Ticket loaded.")
            if refresh_queue:
                self.status_filter.blockSignals(True)
                self.status_filter.setCurrentIndex(0)
                self.status_filter.blockSignals(False)
                self.refresh_list(offset=0, message="Ticket created and loaded.")

        def load_failed(error):
            if refresh_queue:
                # Creation already committed; keep that outcome visible and
                # refresh the queue so the new ticket can be opened again.
                logging.getLogger(__name__).error("Created ticket reload failed: %s", type(error).__name__)
                self.status_filter.blockSignals(True)
                self.status_filter.setCurrentIndex(0)
                self.status_filter.blockSignals(False)
                self.refresh_list(offset=0, message=(
                    "Ticket created, but its details could not be loaded. "
                    "Select it from Saved tickets and retry."
                ))
            else:
                self._show_error(error, "Could not load the requested ticket. Existing information and drafts are unchanged.")

        self._runner.submit(
            lambda: self._service.get_ticket_details(ticket_id), loaded, load_failed,
        )

    def _display_details(self, details):
        self.details = details
        ticket = details.ticket
        self.heading.setText(f"{ticket.ticket_number} — {ticket.subject}\n{ticket.status} · {ticket.priority}")
        self.summary.setPlainText(
            f"{ticket.description or '(No description)'}\n\n"
            f"Assigned to: {ticket.assigned_to or 'Unassigned'}\n"
            f"Created: {ticket.created_at}\nUpdated: {ticket.updated_at}\n"
            f"Resolved: {ticket.resolved_at or '—'}\nClosed: {ticket.closed_at or '—'}\n\n"
            f"Resolution: {ticket.resolution or '—'}"
        )
        self.notes_history.setPlainText("\n\n".join(
            f"{n.created_at} · {n.note_type} · {n.author_label or 'Unknown author'}"
            f"{' · AI-generated' if n.is_ai_generated else ''}\n{n.note_text}"
            for n in details.notes
        ) or "No notes yet.")
        history = "\n".join(
            f"{h.changed_at} · {h.previous_status or 'Created'} → {h.new_status}"
            f" · {h.changed_by or 'Unknown actor'}{': ' + h.reason if h.reason else ''}"
            for h in details.status_history
        )
        timeline = "\n".join(f"{e.occurred_at} · {e.title}" for e in details.timeline_events)
        self.timeline.setPlainText(f"STATUS HISTORY\n{history}\n\nTIMELINE\n{timeline}")
        selected = self.status_input.currentData()
        self.status_input.clear()
        self.status_input.addItem("Choose a status…", None)
        for status in self._service.allowed_statuses(ticket.status):
            self.status_input.addItem(status.replace("_", " ").title(), status)
        self.status_input.setCurrentIndex(max(0, self.status_input.findData(selected)))
        self.change_status_button.setEnabled(self.status_input.count() > 1)
        self.detail_panel.setEnabled(True)

    def _clear_drafts(self):
        self.note_input.clear()
        self.reason_input.clear()
        self.resolution_input.clear()
        self.status_input.setCurrentIndex(0)

    def add_note(self):
        if self.details is None or self._runner.busy:
            return
        ticket_id = self.details.ticket.ticket_id
        values = dict(note_text=self.note_input.toPlainText(), note_type=self.note_type.currentData(),
                      author_label=self.author_input.text())

        def saved(note):
            self.note_input.clear()
            self._reload_after_save(ticket_id, "Note saved.")

        self._runner.submit(lambda: self._service.add_note(ticket_id, **values), saved,
                            lambda error: self._show_error(error, "Could not save the note. Your draft is preserved."))

    def change_status(self):
        if self.details is None or self._runner.busy:
            return
        ticket_id = self.details.ticket.ticket_id
        status = self.status_input.currentData()
        values = dict(new_status=status, reason=self.reason_input.text(), changed_by=self.author_input.text())
        if status == "RESOLVED":
            values["resolution"] = self.resolution_input.toPlainText()

        def saved(ticket):
            self.reason_input.clear()
            self.resolution_input.clear()
            self.status_input.setCurrentIndex(0)
            self._reload_after_save(ticket_id, f"Status changed to {ticket.status}.")

        self._runner.submit(lambda: self._service.change_status(ticket_id, **values), saved,
                            lambda error: self._show_error(error, "Could not change status. Your draft is preserved."))

    def _reload_after_save(self, ticket_id, message):
        # A failed reload must not present an already committed write as failed.
        def loaded(details):
            self._display_details(details)
            self.feedback.setText(message)
            self.refresh_list(message=message)

        def reload_failed(error):
            logging.getLogger(__name__).error("Ticket reload after save failed: %s", type(error).__name__)
            self.feedback.setText(message + " Reload failed; use Reload ticket.")

        self._runner.submit(lambda: self._service.get_ticket_details(ticket_id), loaded, reload_failed)

    def _show_error(self, error, fallback):
        logging.getLogger(__name__).error("Ticket operation failed: %s", type(error).__name__)
        self.feedback.setText(str(error) if isinstance(error, TicketValidationError) else fallback)
