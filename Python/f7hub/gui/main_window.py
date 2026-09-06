"""Minimal F7Hub application shell for the ticket-creation workflow."""

from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QMessageBox
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.ticket_workspace import TicketWorkspace
from f7hub.services.ticket_reference_service import TicketReferenceService
from f7hub.services.company_service import CompanyService
from f7hub.services.contact_service import ContactService

from f7hub.gui.ticket_create_widget import (
    TicketCreateWidget,
    TicketCreationService,
)


class MainWindow(QMainWindow):
    """Host the current workflow behind a stable application shell."""

    def __init__(
        self,
        ticket_service: TicketCreationService,
        *,
        reference_service: TicketReferenceService | None = None,
        company_service: CompanyService | None = None,
        contact_service: ContactService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setWindowTitle("F7Hub")
        available = self.screen().availableGeometry()
        self.resize(min(1180, available.width() - 40), min(850, available.height() - 60))

        self.runner = ServiceTaskRunner(self)
        self.pages = QStackedWidget(self)
        self.ticket_create_widget = TicketCreateWidget(
            ticket_service, reference_service=reference_service, company_service=company_service,
            contact_service=contact_service,
            task_runner=self.runner, parent=self,
        )
        self.workspace = TicketWorkspace(ticket_service, self.runner, self)
        self.pages.addWidget(self.ticket_create_widget)
        self.pages.addWidget(self.workspace)
        self.setCentralWidget(self.pages)
        self.ticket_create_widget.ticket_created.connect(self._ticket_created)

        file_menu = self.menuBar().addMenu("&File")
        toolbar = self.addToolBar("Tickets")
        self.new_ticket_action = QAction("New ticket", self)
        self.new_ticket_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_ticket_action.triggered.connect(self.show_new_ticket)
        self.tickets_action = QAction("Saved tickets", self)
        self.tickets_action.triggered.connect(self.show_tickets)
        for action in (self.new_ticket_action, self.tickets_action):
            file_menu.addAction(action)
            toolbar.addAction(action)
        exit_action = QAction("E&xit", self)
        exit_action.setObjectName("exitAction")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.exit_action = exit_action
        self.runner.busy_changed.connect(self._set_busy)

        self.statusBar().showMessage("Ready")

    def _ticket_created(self, ticket: object) -> None:
        ticket_number = getattr(ticket, "ticket_number", "")
        self.statusBar().showMessage(f"Created ticket {ticket_number}.", 5_000)
        self.ticket_create_widget.reset_form()
        self.pages.setCurrentWidget(self.workspace)
        self.workspace.open_ticket(ticket.ticket_id, refresh_queue=True)

    def _set_busy(self, busy):
        self.pages.setEnabled(not busy)
        self.new_ticket_action.setEnabled(not busy)
        self.tickets_action.setEnabled(not busy)
        self.statusBar().showMessage("Working…" if busy else "Ready")

    def show_new_ticket(self):
        if not self.runner.busy:
            if not self.workspace.confirm_discard():
                return
            self.workspace._clear_drafts()
            self.pages.setCurrentWidget(self.ticket_create_widget)

    def show_tickets(self):
        if not self.runner.busy:
            self.pages.setCurrentWidget(self.workspace)
            self.workspace.refresh_list()

    def closeEvent(self, event):
        if self.runner.busy:
            self.statusBar().showMessage("An operation is finishing. Please close again when it completes.")
            event.ignore()
            return
        if not self.workspace.confirm_discard():
            event.ignore()
            return
        if self.ticket_create_widget.has_draft():
            answer = QMessageBox.question(
                self, "Unsaved new ticket", "Discard the unsaved new ticket?",
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Discard:
                event.ignore()
                return
        super().closeEvent(event)
