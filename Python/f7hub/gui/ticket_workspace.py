"""Saved-ticket list and detail presentation backed by TicketService."""

import logging

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPushButton, QSplitter, QTabWidget,
    QTableView, QTextEdit, QVBoxLayout, QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.edit_ticket_subject_dialog import EditTicketSubjectDialog
from f7hub.gui.edit_ticket_priority_dialog import EditTicketPriorityDialog
from f7hub.gui.ticket_knowledge_widget import TicketKnowledgeWidget
from f7hub.services.ticket_service import (
    TICKET_NOTE_TYPES, TICKET_PRIORITIES, TICKET_STATUSES, TICKET_TYPES,
    TicketValidationError,
)


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
    knowledge_article_requested = Signal(object)

    def __init__(self, service, runner: ServiceTaskRunner, parent=None, *, knowledge_link_service=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self.details = None
        self._offset = 0
        self._retry_offset = None
        self._knowledge_link_service = knowledge_link_service
        self._edit_subject_dialog = None
        self._edit_priority_dialog = None
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
        self.priority_filter = QComboBox(queue)
        self.priority_filter.setAccessibleName("Filter tickets by priority")
        self.priority_filter.addItem("All priorities", None)
        for priority in sorted(TICKET_PRIORITIES, key=("CRITICAL", "HIGH", "MEDIUM", "LOW").index):
            self.priority_filter.addItem(priority.title(), priority)
        self.type_filter = QComboBox(queue)
        self.type_filter.setAccessibleName("Filter tickets by type")
        self.type_filter.addItem("All types", None)
        for ticket_type in TICKET_TYPES:
            self.type_filter.addItem(ticket_type.replace("_", " ").capitalize(), ticket_type)
        self.refresh_button = QPushButton("Refresh", queue)
        self.refresh_button.clicked.connect(lambda: self.refresh_list())
        self.status_filter.currentIndexChanged.connect(lambda: self.refresh_list(offset=0))
        self.priority_filter.currentIndexChanged.connect(lambda: self.refresh_list(offset=0))
        self.type_filter.currentIndexChanged.connect(lambda: self.refresh_list(offset=0))
        filters.addWidget(self.status_filter)
        filters.addWidget(self.refresh_button)
        queue_layout.addLayout(filters)
        queue_layout.addWidget(self.priority_filter)
        queue_layout.addWidget(self.type_filter)
        self._runner.busy_changed.connect(self._set_filter_controls_idle)
        number_row = QHBoxLayout()
        self.ticket_number_input = QLineEdit(queue)
        self.ticket_number_input.setAccessibleName("Open saved ticket by number")
        self.ticket_number_input.setPlaceholderText("Ticket number")
        self.ticket_number_input.returnPressed.connect(self.open_ticket_by_number)
        self.open_number_button = QPushButton("Open number", queue)
        self.open_number_button.clicked.connect(self.open_ticket_by_number)
        number_row.addWidget(self.ticket_number_input, 1)
        number_row.addWidget(self.open_number_button)
        queue_layout.addLayout(number_row)
        self._runner.busy_changed.connect(self._set_number_lookup_idle)
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
        self.knowledge_tab = TicketKnowledgeWidget(self._knowledge_link_service, self._runner, tabs)
        self.knowledge_tab.knowledge_article_requested.connect(self.knowledge_article_requested.emit)
        tabs.addTab(self.knowledge_tab, "Knowledge")
        self.detail_tabs = tabs
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
        self.edit_subject_button = QPushButton("Edit subject", self.detail_panel)
        self.edit_subject_button.clicked.connect(self.open_edit_subject)
        self.edit_priority_button = QPushButton("Edit priority", self.detail_panel)
        self.edit_priority_button.clicked.connect(self.open_edit_priority)
        detail_actions = QHBoxLayout()
        detail_actions.addWidget(self.edit_subject_button)
        detail_actions.addWidget(self.edit_priority_button)
        detail_actions.addWidget(self.reload_button)
        detail_layout.addLayout(detail_actions)
        self.detail_panel.setEnabled(False)
        splitter.setSizes([460, 620])

    def refresh_list(self, *, offset=None, message=None):
        if self._runner.busy:
            return
        if offset is None:
            target = self._offset if self._retry_offset is None else self._retry_offset
        else:
            target = max(0, offset)
        status = self.status_filter.currentData()
        priority = self.priority_filter.currentData()
        ticket_type = self.type_filter.currentData()
        self.feedback.setText("Loading tickets…")

        def loaded(tickets):
            self._offset = target
            self._retry_offset = None
            self.model.replace_tickets(tickets[:self.PAGE_SIZE])
            self.previous_button.setEnabled(target > 0)
            self.next_button.setEnabled(len(tickets) > self.PAGE_SIZE)
            self.page_label.setText(f"Page {target // self.PAGE_SIZE + 1}")
            self.feedback.setText(message or ("No tickets match this filter." if not tickets else "Double-click a ticket or select it and press Open."))
            self.knowledge_tab.refresh_links()

        def failed(error):
            self._retry_offset = target
            retry = "Could not refresh tickets. Previous results are still shown. Use Refresh to retry."
            if message:
                logging.getLogger(__name__).error("Ticket refresh after save failed: %s", type(error).__name__)
                detail = f" {error}" if isinstance(error, TicketValidationError) and str(error) else ""
                self.feedback.setText(f"{message} {retry}{detail}")
            else:
                self._show_error(error, retry)

        self._runner.submit(
            lambda: self._service.list_tickets(
                status=status, priority=priority, ticket_type=ticket_type,
                limit=self.PAGE_SIZE + 1, offset=target,
            ),
            loaded, failed,
        )

    def _activate_row(self, index):
        if index.isValid():
            self.open_ticket(self.model.tickets[index.row()].ticket_id)

    def _set_filter_controls_idle(self, busy):
        self.status_filter.setEnabled(not busy)
        self.priority_filter.setEnabled(not busy)
        self.type_filter.setEnabled(not busy)

    def _set_number_lookup_idle(self, busy):
        self.ticket_number_input.setEnabled(not busy)
        self.open_number_button.setEnabled(not busy)

    def open_ticket_by_number(self):
        if self._runner.busy:
            return
        ticket_number = self.ticket_number_input.text()
        if not ticket_number.strip():
            self.feedback.setText("Enter a ticket number.")
            return
        self.feedback.setText("Opening ticket…")

        def loaded(details):
            switching = self.details is not None and self.details.ticket.ticket_id != details.ticket.ticket_id
            if switching and not self.confirm_discard():
                self.feedback.setText("Ticket opening cancelled.")
                return
            if switching:
                self._clear_drafts()
            self._display_details(details)
            self.feedback.setText("Ticket loaded.")
            self.knowledge_tab.refresh_links()

        self._runner.submit(
            lambda: self._service.get_ticket_details_by_number(ticket_number),
            loaded,
            lambda error: self._show_error(
                error, "Could not load the requested ticket. Existing information and drafts are unchanged."
            ),
        )

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
            else:
                self.knowledge_tab.refresh_links()

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
        self.knowledge_tab.set_ticket(ticket.ticket_id)
        self.heading.setText(f"{ticket.ticket_number} — {ticket.subject}\n{ticket.status} · {ticket.priority}")
        self.summary.setPlainText(
            f"{ticket.description or '(No description)'}\n\n"
            f"Company: {details.company_name or ('Unavailable' if ticket.company_id else 'Not selected')}\n"
            f"Contact: {details.contact_name or ('Unavailable' if ticket.contact_id else 'Not selected')}\n"
            f"Category: {details.category_name or ('Unavailable' if ticket.category_id else 'Not selected')}\n\n"
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

    def open_edit_subject(self):
        if (self.details is None or self._runner.busy
                or self._edit_subject_dialog is not None
                or self._edit_priority_dialog is not None):
            return None
        ticket = self.details.ticket
        dialog = EditTicketSubjectDialog(self._service, self._runner, ticket, self)
        self._edit_subject_dialog = dialog
        dialog.finished.connect(lambda _result: setattr(self, "_edit_subject_dialog", None))
        dialog.subject_updated.connect(lambda updated: self._subject_updated(ticket, updated))
        dialog.open()
        return dialog

    def _subject_updated(self, previous, updated):
        if (updated.subject == previous.subject
                and updated.updated_at == previous.updated_at):
            self.feedback.setText("Subject unchanged.")
            return
        self._reload_after_save(updated.ticket_id, "Subject saved.")

    def open_edit_priority(self):
        if (self.details is None or self._runner.busy
                or self._edit_priority_dialog is not None
                or self._edit_subject_dialog is not None):
            return None
        ticket = self.details.ticket
        dialog = EditTicketPriorityDialog(self._service, self._runner, ticket, self)
        self._edit_priority_dialog = dialog
        dialog.finished.connect(lambda _result: setattr(self, "_edit_priority_dialog", None))
        dialog.priority_updated.connect(lambda updated: self._priority_updated(ticket, updated))
        dialog.open()
        return dialog

    def _priority_updated(self, previous, updated):
        if (updated.priority == previous.priority
                and updated.updated_at == previous.updated_at):
            self.feedback.setText("Priority unchanged.")
            return
        self._reload_after_save(updated.ticket_id, "Priority saved.")

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
