"""Minimal F7Hub application shell for current technician workflows."""

from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QMessageBox
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.ticket_workspace import TicketWorkspace
from f7hub.gui.script_workspace import ScriptWorkspace
from f7hub.services.ticket_reference_service import TicketReferenceService
from f7hub.services.company_service import CompanyService
from f7hub.services.contact_service import ContactService
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_knowledge_service import TicketKnowledgeService
from f7hub.services.database_backup_service import DatabaseBackupService
from f7hub.services.script_service import ScriptService
from f7hub.gui.mochi_settings_dialog import MochiSettingsDialog
from f7hub.services.altf7hub_service import AltF7HubService, AltF7HubOpenError

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
        knowledge_service: KnowledgeService | None = None,
        knowledge_link_service: TicketKnowledgeService | None = None,
        backup_service: DatabaseBackupService | None = None,
        script_service: ScriptService | None = None,
        mochi_service=None,
        altf7hub_service: AltF7HubService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.setWindowTitle("F7Hub")
        available = self.screen().availableGeometry()
        self.resize(min(1180, available.width() - 40), min(850, available.height() - 60))

        self.runner = ServiceTaskRunner(self)
        self.backup_service = backup_service
        self.mochi_service = mochi_service
        self._mochi_dialog = None
        self._tickets_started = False
        self.altf7hub_service = altf7hub_service
        self.pages = QStackedWidget(self)
        self.ticket_create_widget = TicketCreateWidget(
            ticket_service, reference_service=reference_service, company_service=company_service,
            contact_service=contact_service,
            task_runner=self.runner, parent=self,
        )
        self.workspace = TicketWorkspace(
            ticket_service, self.runner, self, knowledge_link_service=knowledge_link_service,
            create_widget=self.ticket_create_widget,
        )
        self.workspace.knowledge_article_requested.connect(self.open_knowledge_article)
        self.knowledge_workspace = (
            KnowledgeWorkspace(knowledge_service, self.runner, self)
            if knowledge_service is not None
            else None
        )
        self.script_workspace = (
            ScriptWorkspace(script_service, self.runner, self)
            if script_service is not None
            else None
        )
        self.pages.addWidget(self.workspace)
        if self.knowledge_workspace is not None:
            self.pages.addWidget(self.knowledge_workspace)
        if self.script_workspace is not None:
            self.pages.addWidget(self.script_workspace)
        self.setCentralWidget(self.pages)
        self.ticket_create_widget.ticket_created.connect(self._ticket_created)

        file_menu = self.menuBar().addMenu("&File")
        settings_menu = self.menuBar().addMenu('&Settings')
        self.mochi_action = QAction('Mochi…', self)
        self.mochi_action.setObjectName('mochiSettingsAction')
        self.mochi_action.setEnabled(mochi_service is not None)
        self.mochi_action.triggered.connect(self.show_mochi_settings)
        settings_menu.addAction(self.mochi_action)
        toolbar = self.addToolBar("Tickets")
        self.tickets_action = QAction("Tickets", self)
        self.tickets_action.triggered.connect(self.show_tickets)
        self.knowledge_action = QAction("Knowledge Base", self)
        self.knowledge_action.setEnabled(self.knowledge_workspace is not None)
        self.knowledge_action.triggered.connect(self.show_knowledge)
        self.scripts_action = QAction("Scripts", self)
        self.scripts_action.setEnabled(self.script_workspace is not None)
        self.scripts_action.triggered.connect(self.show_scripts)
        for action in (self.tickets_action, self.knowledge_action, self.scripts_action):
            file_menu.addAction(action)
            toolbar.addAction(action)
        self.backup_action = QAction("Back up database", self)
        self.altf7hub_action = QAction("AltF7Hub Guide", self)
        self.altf7hub_action.setObjectName("altF7HubGuideAction")
        self.altf7hub_action.setEnabled(self.altf7hub_service is not None)
        self.altf7hub_action.triggered.connect(self.show_altf7hub)
        file_menu.addAction(self.altf7hub_action)
        toolbar.addAction(self.altf7hub_action)
        self.backup_action.setObjectName("backupDatabaseAction")
        self.backup_action.setEnabled(self.backup_service is not None)
        self.backup_action.triggered.connect(self.back_up_database)
        file_menu.addAction(self.backup_action)
        exit_action = QAction("E&xit", self)
        exit_action.setObjectName("exitAction")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.exit_action = exit_action
        self.runner.busy_changed.connect(self._set_busy)
        self.workspace.note_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.creation_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.status_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.workspace.classification_pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))
        self.ticket_create_widget.pending_changed.connect(lambda _pending: self._set_busy(self.runner.busy))

        self.statusBar().showMessage("Ready")

    def showEvent(self, event):
        super().showEvent(event)
        if not self._tickets_started:
            self._tickets_started = True
            QTimer.singleShot(0, self, self._load_initial_tickets)
        if self.mochi_service is not None:
            self.mochi_service.automatic_start(lambda callback: QTimer.singleShot(0, self, callback))

    def show_mochi_settings(self):
        if self.mochi_service is None:
            return
        if self._mochi_dialog is None:
            self._mochi_dialog = MochiSettingsDialog(self.mochi_service, self)
            self._mochi_dialog.finished.connect(self._mochi_dialog_closed)
        self._mochi_dialog.show()
        self._mochi_dialog.raise_()
        self._mochi_dialog.activateWindow()

    def _load_initial_tickets(self):
        if (self.pages.currentWidget() is self.workspace and not self.runner.busy
                and not self.workspace.creating and self.workspace.details is None):
            self.workspace.refresh_list()

    def _mochi_dialog_closed(self, _result):
        self._mochi_dialog = None

    def _ticket_created(self, ticket: object) -> None:
        ticket_number = getattr(ticket, "ticket_number", "")
        self.statusBar().showMessage(f"Created ticket {ticket_number}.", 5_000)

    def _set_busy(self, busy):
        busy = busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending
        self.pages.setEnabled(not busy)
        self.tickets_action.setEnabled(not busy)
        self.knowledge_action.setEnabled(not busy and self.knowledge_workspace is not None)
        self.scripts_action.setEnabled(not busy and self.script_workspace is not None)
        self.backup_action.setEnabled(not busy and self.backup_service is not None)
        self.altf7hub_action.setEnabled(not busy and self.altf7hub_service is not None)
        self.statusBar().showMessage("Working…" if busy else "Ready")

    def show_new_ticket(self):
        if (not self.runner.busy and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending
                and not self.workspace.note_pending and self.workspace.creating):
            self.pages.setCurrentWidget(self.workspace)
            self.ticket_create_widget.subject_input.setFocus()
        elif self.workspace.begin_creation():
            self.pages.setCurrentWidget(self.workspace)

    def show_altf7hub(self):
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.altf7hub_service is None:
            return

        def completed(outcome):
            self.statusBar().showMessage(
                "AltF7Hub editor focused." if outcome == "FOCUSED_EDITOR" else "AltF7Hub Guide opened.",
                5_000,
            )

        def failed(error):
            message = (str(error) if isinstance(error, AltF7HubOpenError) else
                       "The guide open request was not confirmed. Retry or use Alt+F7.")
            self.statusBar().showMessage("AltF7Hub open request not confirmed.", 5_000)
            QMessageBox.warning(self, "AltF7Hub could not open", message)

        self.runner.submit(self.altf7hub_service.show_guide, completed, failed)

    def back_up_database(self):
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.backup_service is None:
            return

        def completed(path):
            self.statusBar().showMessage("Database backup completed.", 5_000)
            QMessageBox.information(
                self, "Database backup completed",
                f"Backup saved to:\n{path}\n\n"
                "This contains local SQLite data only. Copy it to another location "
                "to protect against loss of this drive.",
            )

        def failed(_error):
            self.statusBar().showMessage("Database backup failed.", 5_000)
            QMessageBox.warning(
                self, "Database backup failed",
                "The database backup could not be completed. No completed backup was published.",
            )

        self.runner.submit(self.backup_service.create_backup, completed, failed)

    def show_tickets(self):
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending:
            self.pages.setCurrentWidget(self.workspace)
            self.workspace.refresh_list()

    def show_knowledge(self):
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending and self.knowledge_workspace is not None:
            if not self.workspace.confirm_discard():
                return
            self.workspace._clear_drafts()
            self.pages.setCurrentWidget(self.knowledge_workspace)
            self.knowledge_workspace.refresh_list()

    def show_scripts(self):
        if not self.runner.busy and not self.workspace.note_pending and not self.workspace.creation_pending and not self.workspace.status_pending and not self.workspace.classification_pending and self.script_workspace is not None:
            if not self.workspace.confirm_discard():
                return
            self.workspace._clear_drafts()
            self.pages.setCurrentWidget(self.script_workspace)
            self.script_workspace.refresh_list()

    def open_knowledge_article(self, article_id):
        if self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending or self.knowledge_workspace is None:
            return
        if not self.workspace.confirm_discard():
            return
        self.workspace._clear_drafts()
        self.pages.setCurrentWidget(self.knowledge_workspace)
        self.knowledge_workspace.open_article_by_id(article_id)

    def closeEvent(self, event):
        if (self.runner.busy or self.workspace.note_pending or self.workspace.creation_pending or self.workspace.status_pending or self.workspace.classification_pending
                or (self.knowledge_workspace is not None and self.knowledge_workspace.filter_loading)):
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
        if self.mochi_service is not None:
            if self._mochi_dialog is not None:
                self._mochi_dialog.close()
            self.mochi_service.close()
        super().closeEvent(event)
