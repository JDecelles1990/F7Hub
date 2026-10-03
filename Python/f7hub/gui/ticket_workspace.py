"""Saved-ticket list and detail presentation backed by TicketService."""

import logging

from PySide6.QtCore import QAbstractTableModel, QEvent, QModelIndex, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPushButton, QSplitter, QTabWidget,
    QTableView, QTextEdit, QVBoxLayout, QWidget, QStackedWidget, QScrollArea,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.edit_ticket_subject_dialog import EditTicketSubjectDialog
from f7hub.gui.edit_ticket_priority_dialog import EditTicketPriorityDialog
from f7hub.gui.edit_ticket_description_dialog import EditTicketDescriptionDialog
from f7hub.gui.edit_ticket_type_dialog import EditTicketTypeDialog
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
    note_pending_changed = Signal(bool)
    creation_pending_changed = Signal(bool)
    status_pending_changed = Signal(bool)

    def __init__(self, service, runner: ServiceTaskRunner, parent=None, *, knowledge_link_service=None,
                 create_widget=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self.details = None
        self._offset = 0
        self._retry_offset = None
        self._subject_query = None
        self._company_context = None
        self._company_context_generation = 0
        self._knowledge_link_service = knowledge_link_service
        self._edit_subject_dialog = None
        self._edit_priority_dialog = None
        self._edit_description_dialog = None
        self._edit_type_dialog = None
        self._note_pending = False
        self.status_pending = False
        self._note_focus_ticket_id = None
        self.create_widget = create_widget
        self.creating = False
        self._previous_details = None
        self._creation_pending = False
        self._created_ticket_id = None
        self._creation_generation = 0
        self._creation_focus_pending = False
        self._build_ui()
        self._runner.busy_changed.connect(self._update_note_controls)
        self.note_pending_changed.connect(self._update_note_controls)
        self._update_note_controls()
        self._runner.busy_changed.connect(self._update_creation_controls)
        self.note_pending_changed.connect(self._update_creation_controls)
        self.creation_pending_changed.connect(self._update_creation_controls)
        self.creation_pending_changed.connect(self._update_note_controls)
        self.status_pending_changed.connect(self._update_creation_controls)
        self.status_pending_changed.connect(self._update_note_controls)
        if self.create_widget is not None:
            self.create_widget.ticket_created.connect(self._ticket_created)
            self.create_widget.pending_changed.connect(lambda _pending: self._update_creation_controls())

    @property
    def creation_pending(self):
        return self._creation_pending or bool(self.create_widget and self.create_widget._submitting)

    def _update_creation_controls(self, *_):
        idle = not self._runner.busy and not self.note_pending and not self.creation_pending and not self.status_pending
        self.new_ticket_button.setEnabled(idle and not self.creating and self.create_widget is not None)
        self.cancel_create_button.setEnabled(idle)
        self.retry_created_button.setEnabled(idle and not self.creating)
        if idle and self.creating and self._creation_focus_pending:
            QTimer.singleShot(0, self, self._focus_creation)

    def _focus_creation(self):
        if (self.creating and self._creation_focus_pending and not self._runner.busy
                and self.create_widget.isVisible()):
            self._creation_focus_pending = False
            self.create_widget.subject_input.setFocus()

    def begin_creation(self):
        if (self.create_widget is None or self.creating or self._runner.busy
                or self.note_pending or self.creation_pending or self.status_pending or not self.confirm_discard()):
            return False
        self._clear_drafts()
        self._creation_generation += 1
        self._previous_details = self.details
        self.details = None
        self.heading.setText("Open a ticket to see its details")
        self.summary.clear()
        self.notes_history.clear()
        self.timeline.clear()
        self.knowledge_tab.set_ticket(None)
        self.detail_panel.setEnabled(False)
        self.creating = True
        self._creation_focus_pending = True
        self.detail_stack.setCurrentWidget(self.creation_panel)
        self.feedback.setText("New ticket — the queue and its filters are retained.")
        self._update_note_controls()
        self._update_creation_controls()
        self.create_widget.subject_input.setFocus()
        return True

    def cancel_creation(self):
        if not self.creating or self._runner.busy or self.creation_pending:
            return False
        if self.create_widget.has_draft() and QMessageBox.question(
            self, "Unsaved new ticket", "Discard the unsaved new ticket?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        ) != QMessageBox.StandardButton.Discard:
            return False
        self.create_widget.reset_form()
        self._creation_generation += 1
        self.creating = False
        self.detail_stack.setCurrentWidget(self.detail_panel)
        if self._previous_details is not None:
            self._display_details(self._previous_details)
        self._previous_details = None
        self.feedback.setText("New ticket cancelled. No ticket was created.")
        self._update_creation_controls()
        return True

    def _ticket_created(self, ticket):
        self._created_ticket_id = ticket.ticket_id
        self.create_widget.reset_form()
        self.creating = False
        self._previous_details = None
        self.detail_stack.setCurrentWidget(self.detail_panel)
        self.retry_created_button.show()
        self._open_created_ticket()

    def _open_created_ticket(self):
        if self.creating or self.status_pending or self.note_pending or self._runner.busy or self._creation_pending or self._created_ticket_id is None:
            return
        self._creation_pending = True
        self.creation_pending_changed.emit(True)
        generation = self._creation_generation

        def finished():
            if generation == self._creation_generation:
                self._creation_pending = False
                self.creation_pending_changed.emit(False)

        self.open_ticket(self._created_ticket_id, refresh_queue=True, on_finished=finished)

    @property
    def note_pending(self):
        return self._note_pending

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        header = QHBoxLayout()
        self.workspace_heading = QLabel("Tickets", self)
        heading_font = self.workspace_heading.font()
        heading_font.setBold(True)
        heading_font.setPointSize(14)
        self.workspace_heading.setFont(heading_font)
        self.workspace_heading.setAccessibleName("Tickets")
        header.addWidget(self.workspace_heading, 1)
        self.retry_created_button = QPushButton("Open created ticket", self)
        self.retry_created_button.clicked.connect(self._open_created_ticket)
        self.retry_created_button.hide()
        header.addWidget(self.retry_created_button)
        self.new_ticket_button = QPushButton("+ New Ticket", self)
        self.new_ticket_button.setObjectName("newTicketButton")
        self.new_ticket_button.setAccessibleName("New Ticket")
        self.new_ticket_button.clicked.connect(self.begin_creation)
        header.addWidget(self.new_ticket_button)
        layout.addLayout(header)
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
        search_row = QHBoxLayout()
        self.subject_search_input = QLineEdit(queue)
        self.subject_search_input.setAccessibleName("Search subjects, descriptions and notes")
        self.subject_search_input.setPlaceholderText("Search subjects, descriptions and notes")
        self.subject_search_input.returnPressed.connect(self.search_subjects)
        self.search_subjects_button = QPushButton("Search", queue)
        self.search_subjects_button.clicked.connect(self.search_subjects)
        self.clear_subject_search_button = QPushButton("Clear", queue)
        self.clear_subject_search_button.clicked.connect(self.clear_subject_search)
        search_row.addWidget(self.subject_search_input, 1)
        search_row.addWidget(self.search_subjects_button)
        search_row.addWidget(self.clear_subject_search_button)
        queue_layout.addLayout(search_row)
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
        self.table.setAccessibleName("Tickets; activate a row to open")
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

        self.detail_stack = QStackedWidget(splitter)
        self.detail_panel = QWidget(self.detail_stack)
        self.detail_stack.addWidget(self.detail_panel)
        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setSpacing(4)
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
        company_tab = QWidget(tabs)
        company_layout = QVBoxLayout(company_tab)
        self.company_heading = QLabel("No company is linked to this ticket.", company_tab)
        self.company_heading.setTextFormat(Qt.TextFormat.PlainText)
        self.company_heading.setWordWrap(True)
        company_layout.addWidget(self.company_heading)
        self.company_feedback = QLabel(company_tab)
        self.company_feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.company_feedback.setWordWrap(True)
        company_layout.addWidget(self.company_feedback)
        self.company_load_button = QPushButton("Load recent tickets", company_tab)
        self.company_load_button.clicked.connect(self.load_company_tickets)
        self.company_load_button.setEnabled(False)
        company_layout.addWidget(self.company_load_button)
        self.company_model = TicketTableModel(self)
        self.company_table = QTableView(company_tab)
        self.company_table.setAccessibleName("Recent tickets for this company")
        self.company_table.setModel(self.company_model)
        self.company_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.company_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.company_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.company_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.company_table.activated.connect(self._activate_company_row)
        company_layout.addWidget(self.company_table)
        self.company_open_button = QPushButton("Open selected ticket", company_tab)
        self.company_open_button.clicked.connect(
            lambda: self._activate_company_row(self.company_table.currentIndex())
        )
        self.company_open_button.setEnabled(False)
        company_layout.addWidget(self.company_open_button)
        self.company_table.selectionModel().currentChanged.connect(
            lambda: self._set_company_controls_idle(self._runner.busy)
        )
        self._runner.busy_changed.connect(self._set_company_controls_idle)
        tabs.addTab(company_tab, "Company")
        self.detail_tabs = tabs
        detail_layout.addWidget(tabs)
        self.author_input = QLineEdit(self.detail_panel)
        self.author_input.setPlaceholderText("Your name (optional)")
        self.author_input.setAccessibleName("Activity author")
        detail_layout.addWidget(self.author_input)
        self.note_type = QComboBox(self.detail_panel)
        for kind in sorted(TICKET_NOTE_TYPES):
            self.note_type.addItem(kind.title(), kind)
        self.note_type.setCurrentIndex(self.note_type.findData("INTERNAL"))
        self.note_type.setAccessibleName("Note type")
        self.note_input = _plain_editor(self.detail_panel)
        self.note_input.setPlaceholderText("Add a support note…")
        self.note_input.setAccessibleName("New note")
        self.note_input.setMaximumHeight(85)
        self.note_input.installEventFilter(self)
        self.note_input.textChanged.connect(self._update_note_controls)
        self.add_note_button = QPushButton("Add note", self.detail_panel)
        self.add_note_button.setToolTip("Save this note (Ctrl+Enter in the note editor)")
        self.add_note_button.clicked.connect(self.add_note)
        note_actions = QHBoxLayout()
        note_actions.addWidget(QLabel("Quick Note", self.detail_panel))
        note_actions.addWidget(self.note_type)
        note_actions.addStretch()
        note_actions.addWidget(self.add_note_button)
        detail_layout.addLayout(note_actions)
        detail_layout.addWidget(self.note_input)
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
        self.edit_description_button = QPushButton("Edit description", self.detail_panel)
        self.edit_description_button.clicked.connect(self.open_edit_description)
        self.edit_type_button = QPushButton("Edit type", self.detail_panel)
        self.edit_type_button.clicked.connect(self.open_edit_type)
        detail_actions = QGridLayout()
        detail_actions.addWidget(self.edit_subject_button, 0, 0)
        detail_actions.addWidget(self.edit_priority_button, 0, 1)
        detail_actions.addWidget(self.edit_type_button, 0, 2)
        detail_actions.addWidget(self.edit_description_button, 1, 0)
        detail_actions.addWidget(self.reload_button, 1, 1)
        detail_layout.addLayout(detail_actions)
        self.detail_panel.setEnabled(False)
        self.creation_panel = QWidget(self.detail_stack)
        creation_layout = QVBoxLayout(self.creation_panel)
        creation_layout.setContentsMargins(0, 0, 0, 0)
        self.creation_scroll = QScrollArea(self.creation_panel)
        self.creation_scroll.setWidgetResizable(True)
        if self.create_widget is not None:
            self.create_widget.layout().setContentsMargins(12, 12, 12, 12)
            self.create_widget.layout().setSpacing(8)
            self.creation_scroll.setWidget(self.create_widget)
        creation_layout.addWidget(self.creation_scroll)
        self.cancel_create_button = QPushButton("Cancel", self.creation_panel)
        self.cancel_create_button.setAccessibleName("Cancel New Ticket")
        self.cancel_create_button.clicked.connect(self.cancel_creation)
        creation_layout.addWidget(self.cancel_create_button)
        self.detail_stack.addWidget(self.creation_panel)
        splitter.setSizes([460, 620])
        self._update_creation_controls()

    def refresh_list(self, *, offset=None, message=None, on_finished=None):
        # Only the note's own refresh may enter while its write is pending.
        if self._runner.busy or ((self.note_pending or self.creation_pending or self.status_pending) and on_finished is None):
            return False
        if offset is None:
            target = self._offset if self._retry_offset is None else self._retry_offset
        else:
            target = max(0, offset)
        status = self.status_filter.currentData()
        priority = self.priority_filter.currentData()
        ticket_type = self.type_filter.currentData()
        subject_query = self._subject_query
        generation = self._creation_generation
        self.feedback.setText("Loading tickets…")

        def loaded(tickets):
            if generation != self._creation_generation:
                return
            self._offset = target
            self._retry_offset = None
            self.model.replace_tickets(tickets[:self.PAGE_SIZE])
            if self.details is not None:
                for row, ticket in enumerate(self.model.tickets):
                    if ticket.ticket_id == self.details.ticket.ticket_id:
                        self.table.selectRow(row)
                        break
            self.previous_button.setEnabled(target > 0)
            self.next_button.setEnabled(len(tickets) > self.PAGE_SIZE)
            self.page_label.setText(f"Page {target // self.PAGE_SIZE + 1}")
            self.feedback.setText(message or ("No tickets match this filter." if not tickets else "Double-click a ticket or select it and press Open."))
            self.knowledge_tab.refresh_links()
            if on_finished is not None:
                on_finished()

        def failed(error):
            if generation != self._creation_generation:
                return
            self._retry_offset = target
            retry = "Could not refresh tickets. Previous results are still shown. Use Refresh to retry."
            if message:
                logging.getLogger(__name__).error("Ticket refresh after save failed: %s", type(error).__name__)
                detail = f" {error}" if isinstance(error, TicketValidationError) and str(error) else ""
                self.feedback.setText(f"{message} {retry}{detail}")
            else:
                self._show_error(error, retry)
            if on_finished is not None:
                on_finished()

        return self._runner.submit(
            lambda: self._service.list_tickets(
                status=status, priority=priority, ticket_type=ticket_type,
                subject_query=subject_query, include_description=True, include_notes=True,
                limit=self.PAGE_SIZE + 1, offset=target,
            ),
            loaded, failed,
        )

    def search_subjects(self):
        if self._runner.busy or self.note_pending or self.creation_pending or self.status_pending:
            return
        self._subject_query = self.subject_search_input.text().strip() or None
        self.refresh_list(offset=0)

    def clear_subject_search(self):
        if self._runner.busy or self.note_pending or self.creation_pending or self.status_pending:
            return
        self.subject_search_input.clear()
        self._subject_query = None
        self.refresh_list(offset=0)

    def _activate_row(self, index):
        if index.isValid():
            self.open_ticket(self.model.tickets[index.row()].ticket_id)

    def _set_filter_controls_idle(self, busy):
        self.status_filter.setEnabled(not busy)
        self.priority_filter.setEnabled(not busy)
        self.type_filter.setEnabled(not busy)
        self.subject_search_input.setEnabled(not busy)
        self.search_subjects_button.setEnabled(not busy)
        self.clear_subject_search_button.setEnabled(not busy)

    def _set_number_lookup_idle(self, busy):
        self.ticket_number_input.setEnabled(not busy)
        self.open_number_button.setEnabled(not busy)

    def _set_company_controls_idle(self, busy):
        self.company_load_button.setEnabled(
            not busy and self._company_context is not None
            and self._company_context[1] is not None
        )
        self.company_open_button.setEnabled(
            not busy and self.company_table.currentIndex().isValid()
        )

    def load_company_tickets(self):
        if (self.creating or self.creation_pending or self._runner.busy
                or self.note_pending or self._company_context is None):
            return
        context = self._company_context
        if context[1] is None:
            return
        generation = self._company_context_generation
        self.company_feedback.setText("Loading recent company tickets…")

        def still_current():
            return (self._company_context_generation == generation
                    and self._company_context == context)

        def loaded(tickets):
            if not still_current():
                return
            self.company_model.replace_tickets(tickets)
            if tickets:
                self.company_table.selectRow(0)
                self.company_feedback.setText("Up to 20 most recently updated tickets for this company.")
            else:
                self.company_feedback.setText("No recent tickets for this company.")
            self._set_company_controls_idle(False)

        def failed(error):
            if not still_current():
                return
            logging.getLogger(__name__).error("Company ticket load failed: %s", type(error).__name__)
            self.company_feedback.setText(
                "Could not load recent company tickets. Previous results for this company remain. "
                "Use Load recent tickets to retry."
                if self.company_model.tickets else
                "Could not load recent company tickets. Use Load recent tickets to retry."
            )

        self._runner.submit(
            lambda: self._service.list_tickets(company_id=context[1], limit=20, offset=0),
            loaded, failed,
        )

    def _activate_company_row(self, index):
        if not self._runner.busy and index.isValid() and index.row() < len(self.company_model.tickets):
            self.open_ticket(self.company_model.tickets[index.row()].ticket_id)

    def open_ticket_by_number(self):
        if self._runner.busy or self.note_pending or self.creation_pending or self.status_pending:
            return
        if self.creating and not self.cancel_creation():
            return
        ticket_number = self.ticket_number_input.text()
        if not ticket_number.strip():
            self.feedback.setText("Enter a ticket number.")
            return
        self.feedback.setText("Opening ticket…")
        generation = self._creation_generation

        def loaded(details):
            if generation != self._creation_generation:
                return
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
            ) if generation == self._creation_generation else None,
        )

    def has_draft(self):
        return bool(self.note_input.toPlainText().strip() or self.reason_input.text().strip()
                    or self.resolution_input.toPlainText().strip() or self.status_input.currentData())

    def confirm_discard(self):
        if self.note_pending:
            return False
        if not self.has_draft():
            return True
        return QMessageBox.question(
            self, "Unsaved ticket activity", "Discard the unsaved note or status change?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        ) == QMessageBox.StandardButton.Discard

    def open_ticket(self, ticket_id, *, refresh_queue=False, on_finished=None):
        if self._runner.busy or self.note_pending or ((self.creation_pending or self.status_pending) and on_finished is None):
            if on_finished is not None:
                on_finished()
            return
        if self.creating and not self.cancel_creation():
            if on_finished is not None:
                on_finished()
            return
        switching = self.details is not None and self.details.ticket.ticket_id != ticket_id
        if switching and not self.confirm_discard():
            # No read was submitted; release the retry's transition ownership.
            if on_finished is not None:
                on_finished()
            return
        self.feedback.setText("Loading ticket…")
        generation = self._creation_generation

        def refresh_created(message):
            if not self.refresh_list(message=message, on_finished=on_finished) and on_finished is not None:
                self.feedback.setText(message + " Refresh could not start; use Refresh.")
                on_finished()

        def loaded(details):
            if generation != self._creation_generation:
                return
            if switching:
                self._clear_drafts()
            self._display_details(details)
            self.feedback.setText("Ticket loaded.")
            if refresh_queue:
                self._created_ticket_id = None
                self.retry_created_button.hide()
                refresh_created("Ticket created successfully and loaded. Current queue filters and page are retained.")
            else:
                self.knowledge_tab.refresh_links()

        def load_failed(error):
            if generation != self._creation_generation:
                return
            if refresh_queue:
                # Creation already committed; keep that outcome visible and
                # refresh the queue so the new ticket can be opened again.
                logging.getLogger(__name__).error("Created ticket reload failed: %s", type(error).__name__)
                refresh_created("Ticket created successfully, but its details could not be loaded. "
                                "Use Open created ticket to retry without creating another ticket.")
            else:
                self._show_error(error, "Could not load the requested ticket. Existing information and drafts are unchanged.")

        if not self._runner.submit(
            lambda: self._service.get_ticket_details(ticket_id), loaded, load_failed,
        ) and on_finished is not None:
            load_failed(RuntimeError("Dispatch rejected"))

    def _display_details(self, details):
        self.details = details
        ticket = details.ticket
        context = (ticket.ticket_id, ticket.company_id)
        if context != self._company_context:
            self._company_context = context
            self._company_context_generation += 1
            self.company_model.replace_tickets(())
            self.company_feedback.setText(
                "Select Load recent tickets to see up to 20 tickets for this company."
                if ticket.company_id is not None else ""
            )
        self.company_heading.setText(
            f"Company: {details.company_name or 'Unavailable'}"
            if ticket.company_id is not None else "No company is linked to this ticket."
        )
        self._set_company_controls_idle(self._runner.busy)
        self.knowledge_tab.set_ticket(ticket.ticket_id)
        self.heading.setText(f"{ticket.ticket_number} — {ticket.subject}\n{ticket.status} · {ticket.priority}")
        self.summary.setPlainText(
            f"{ticket.description or '(No description)'}\n\n"
            f"Type: {ticket.ticket_type.replace('_', ' ').capitalize()}\n"
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
        self._update_note_controls()

    def _clear_drafts(self):
        self.note_input.clear()
        self.reason_input.clear()
        self.resolution_input.clear()
        self.status_input.setCurrentIndex(0)

    def open_edit_subject(self):
        if (self.details is None or self._runner.busy or self.note_pending or self.creation_pending or self.status_pending
                or self._edit_subject_dialog is not None
                or self._edit_priority_dialog is not None
                or self._edit_description_dialog is not None
                or self._edit_type_dialog is not None):
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
        if (self.details is None or self._runner.busy or self.note_pending or self.creation_pending or self.status_pending
                or self._edit_priority_dialog is not None
                or self._edit_subject_dialog is not None
                or self._edit_description_dialog is not None
                or self._edit_type_dialog is not None):
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

    def open_edit_description(self):
        if (self.details is None or self._runner.busy or self.note_pending or self.creation_pending or self.status_pending
                or self._edit_description_dialog is not None
                or self._edit_subject_dialog is not None
                or self._edit_priority_dialog is not None
                or self._edit_type_dialog is not None):
            return None
        ticket = self.details.ticket
        dialog = EditTicketDescriptionDialog(self._service, self._runner, ticket, self)
        self._edit_description_dialog = dialog
        dialog.finished.connect(lambda _result: setattr(self, "_edit_description_dialog", None))
        dialog.description_updated.connect(
            lambda updated: self._description_updated(ticket, updated)
        )
        dialog.open()
        return dialog

    def _description_updated(self, previous, updated):
        if (updated.description == previous.description
                and updated.updated_at == previous.updated_at):
            self.feedback.setText("Description unchanged.")
            return
        self._reload_after_save(updated.ticket_id, "Description saved.")

    def open_edit_type(self):
        if (self.details is None or self._runner.busy or self.note_pending or self.creation_pending or self.status_pending
                or self._edit_type_dialog is not None
                or self._edit_subject_dialog is not None
                or self._edit_priority_dialog is not None
                or self._edit_description_dialog is not None):
            return None
        ticket = self.details.ticket
        dialog = EditTicketTypeDialog(self._service, self._runner, ticket, self)
        self._edit_type_dialog = dialog
        dialog.finished.connect(lambda _result: setattr(self, "_edit_type_dialog", None))
        dialog.type_updated.connect(lambda updated: self._type_updated(ticket, updated))
        dialog.open()
        return dialog

    def _type_updated(self, previous, updated):
        if (updated.ticket_type == previous.ticket_type
                and updated.updated_at == previous.updated_at):
            self.feedback.setText("Type unchanged.")
            return
        self._reload_after_save(updated.ticket_id, "Type saved.")

    def eventFilter(self, watched, event):
        if watched is self.note_input and self.note_input.hasFocus():
            submit_key = (
                event.type() in (QEvent.Type.KeyPress, QEvent.Type.ShortcutOverride)
                and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                and (event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier)
                == Qt.KeyboardModifier.ControlModifier
            )
            if submit_key:
                if event.type() == QEvent.Type.KeyPress and not event.isAutoRepeat():
                    self.add_note()
                event.accept()
                return True
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def _update_note_controls(self, *_):
        if not hasattr(self, "add_note_button"):
            return
        enabled = (self.details is not None and not self.creating and not self.creation_pending and not self.status_pending
                   and not self._runner.busy and not self.note_pending)
        for widget in (self.note_input, self.note_type, self.author_input):
            widget.setEnabled(enabled)
        self.add_note_button.setEnabled(enabled and bool(self.note_input.toPlainText().strip()))
        if self._note_focus_ticket_id is not None:
            QTimer.singleShot(0, self, self._restore_note_focus)

    def _restore_note_focus(self):
        if self._runner.busy or self.note_pending or self.creation_pending or self.status_pending:
            return
        ticket_id = self._note_focus_ticket_id
        self._note_focus_ticket_id = None
        if (self.details is not None and self.details.ticket.ticket_id == ticket_id
                and self.note_input.isVisible() and self.note_input.isEnabled()):
            self.note_input.setFocus()

    def _finish_note(self, ticket_id):
        self._note_focus_ticket_id = ticket_id
        self._note_pending = False
        self.note_pending_changed.emit(False)

    def add_note(self):
        if (self.creating or self.details is None or self._runner.busy or self.note_pending or self.creation_pending or self.status_pending
                or not self.note_input.toPlainText().strip()):
            return
        ticket_id = self.details.ticket.ticket_id
        values = dict(note_text=self.note_input.toPlainText(), note_type=self.note_type.currentData(),
                      author_label=self.author_input.text())
        self._note_pending = True
        self.note_pending_changed.emit(True)
        self.feedback.setText("Saving note…")

        def saved(note):
            self.note_input.clear()
            self._reload_after_save(ticket_id, "Note saved.",
                                    on_finished=lambda: self._finish_note(ticket_id))

        def failed(error):
            self._show_error(error, "Could not save the note. Your draft is preserved.")
            self._finish_note(ticket_id)

        if not self._runner.submit(lambda: self._service.add_note(ticket_id, **values), saved, failed):
            self.feedback.setText("Could not start saving the note. Your draft is preserved.")
            self._finish_note(ticket_id)

    def change_status(self):
        if (self.creating or self.details is None or self._runner.busy
                or self.note_pending or self.creation_pending or self.status_pending):
            return
        ticket_id = self.details.ticket.ticket_id
        status = self.status_input.currentData()
        values = dict(new_status=status, reason=self.reason_input.text(), changed_by=self.author_input.text())
        if status == "RESOLVED":
            values["resolution"] = self.resolution_input.toPlainText()
        self.status_pending = True
        self.status_pending_changed.emit(True)

        def finished():
            self.status_pending = False
            self.status_pending_changed.emit(False)

        def saved(ticket):
            self.reason_input.clear()
            self.resolution_input.clear()
            self.status_input.setCurrentIndex(0)
            self._reload_after_save(ticket_id, f"Status changed to {ticket.status}.", on_finished=finished)

        def failed(error):
            self._show_error(error, "Could not change status. Your draft is preserved.")
            finished()

        if not self._runner.submit(lambda: self._service.change_status(ticket_id, **values), saved, failed):
            failed(RuntimeError("Dispatch rejected"))

    def _reload_after_save(self, ticket_id, message, *, on_finished=None):
        # A failed reload must not present an already committed write as failed.
        def loaded(details):
            self._display_details(details)
            self.feedback.setText(message)
            if not self.refresh_list(message=message, on_finished=on_finished):
                self.feedback.setText(message + " Refresh could not start; use Refresh.")
                if on_finished is not None:
                    on_finished()

        def reload_failed(error):
            logging.getLogger(__name__).error("Ticket reload after save failed: %s", type(error).__name__)
            self.feedback.setText(message + " Reload failed; use Reload ticket.")
            if on_finished is not None:
                on_finished()

        if not self._runner.submit(lambda: self._service.get_ticket_details(ticket_id), loaded, reload_failed):
            self.feedback.setText(message + " Reload could not start; use Reload ticket.")
            if on_finished is not None:
                on_finished()

    def _show_error(self, error, fallback):
        logging.getLogger(__name__).error("Ticket operation failed: %s", type(error).__name__)
        self.feedback.setText(str(error) if isinstance(error, TicketValidationError) else fallback)
