"""Saved-ticket Knowledge tab and its small asynchronous link selector."""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox,
    QPushButton, QTableView, QVBoxLayout, QWidget,
)

from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.ticket_knowledge_service import (
    TicketKnowledgeService, TicketKnowledgeValidationError, TicketKnowledgePersistenceError,
)


class _ArticleIdentityTable(QTableView):
    """The same lightweight article identity in the tab and selector."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = ()
        self.identity_model = QStandardItemModel(0, 4, self)
        self.identity_model.setHorizontalHeaderLabels(("Code", "Title", "Status", "Version"))
        self.setModel(self.identity_model)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def replace_records(self, records, select_article_id=None):
        self.records = tuple(records)
        self.identity_model.removeRows(0, self.identity_model.rowCount())
        for article in self.records:
            self.identity_model.appendRow([
                QStandardItem(str(value)) for value in (
                    article.article_code, article.article_title,
                    article.article_status, article.article_version_number,
                )
            ])
        # Size identity columns now; a deferred header resize can leave the
        # first loaded code clipped until another layout event occurs.
        for column in (0, 2, 3):
            self.resizeColumnToContents(column)
        if self.records:
            row = next((i for i, item in enumerate(self.records)
                        if item.knowledge_article_id == select_article_id), 0)
            self.selectRow(row)

    def selected_article_id(self):
        rows = self.selectionModel().selectedRows()
        return self.records[rows[0].row()].knowledge_article_id if rows else None


def _safe_message(error, fallback):
    if isinstance(error, (TicketKnowledgeValidationError, TicketKnowledgePersistenceError)):
        return str(error)
    logging.getLogger(__name__).error("Ticket knowledge operation failed: %s", type(error).__name__)
    return fallback


class LinkArticleDialog(QDialog):
    article_linked = Signal(object)

    def __init__(self, service, runner, ticket_id, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._ticket_id = ticket_id
        self._submitting = False
        self._completed = False
        self._dismissed = False
        self.setWindowTitle("Link Knowledge Article")
        self.resize(600, 380)
        self.table = _ArticleIdentityTable(self)
        self.table.setAccessibleName("Existing knowledge articles available to link")
        self.feedback = QLabel(self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.retry_button = QPushButton("Retry loading articles", self)
        self.retry_button.hide()
        self.retry_button.clicked.connect(self.load_candidates)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.clicked.connect(self.reject)
        self.link_button = QPushButton("Link Article", self)
        self.link_button.setEnabled(False)
        self.link_button.clicked.connect(self.submit)
        self.table.selectionModel().selectionChanged.connect(self._update_link_button)
        actions = QHBoxLayout()
        actions.addWidget(self.retry_button)
        actions.addStretch()
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.link_button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)

    def load_candidates(self):
        if self._runner.busy or self._dismissed or self._completed:
            return
        self.retry_button.hide()
        self.feedback.setText("Loading articles…")
        self.link_button.setEnabled(False)
        self._runner.submit(
            lambda: self._service.list_link_candidates(self._ticket_id),
            self._candidates_loaded, self._candidates_failed,
        )

    def _candidates_loaded(self, candidates):
        if self._dismissed:
            return
        self.table.replace_records(candidates)
        self.feedback.setText("" if candidates else "No articles available to link.")
        self._update_link_button()

    def _candidates_failed(self, error):
        if self._dismissed:
            return
        self.feedback.setText(_safe_message(error, "Could not load articles to link. Try again."))
        self.retry_button.show()

    def _update_link_button(self, *_):
        self.link_button.setEnabled(
            not self._submitting and not self._completed and not self._runner.busy
            and self.table.selected_article_id() is not None
        )

    def submit(self):
        article_id = self.table.selected_article_id()
        if self._submitting or self._completed or self._dismissed or self._runner.busy or article_id is None:
            return
        self._set_submitting(True)
        self.feedback.setText("Linking article…")
        self._runner.submit(
            lambda: self._service.link_related_article(self._ticket_id, article_id),
            self._succeeded, self._failed,
        )

    def _set_submitting(self, submitting):
        self._submitting = submitting
        self.table.setEnabled(not submitting)
        self.cancel_button.setEnabled(not submitting)
        self._update_link_button()

    def _succeeded(self, link):
        self._completed = True
        self._set_submitting(False)
        self.accept()
        self.article_linked.emit(link)

    def _failed(self, error):
        self._set_submitting(False)
        self.feedback.setText(_safe_message(error, "Could not link the article. Your selection is preserved. Try again."))

    def reject(self):
        if not self._submitting:
            self._dismissed = True
            super().reject()

    def closeEvent(self, event):
        if self._submitting:
            event.ignore()
        else:
            self._dismissed = True
            super().closeEvent(event)


class TicketKnowledgeWidget(QWidget):
    knowledge_article_requested = Signal(object)

    def __init__(self, service: TicketKnowledgeService | None, runner: ServiceTaskRunner, parent=None):
        super().__init__(parent)
        self._service = service
        self._runner = runner
        self._ticket_id = None
        self._dialog = None
        self._confirming_unlink = False
        self.table = _ArticleIdentityTable(self)
        self.table.setAccessibleName("Linked knowledge articles")
        self.feedback = QLabel("Open a ticket to see linked articles.", self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.link_button = QPushButton("Link Article", self)
        self.link_button.clicked.connect(self.open_link_dialog)
        self.open_button = QPushButton("Open Article", self)
        self.open_button.clicked.connect(self.open_selected_article)
        self.unlink_button = QPushButton("Unlink Article", self)
        self.unlink_button.clicked.connect(self.unlink_selected_article)
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(lambda: self.refresh_links())
        self.table.selectionModel().selectionChanged.connect(self._update_controls)
        actions = QHBoxLayout()
        actions.addWidget(self.link_button)
        actions.addWidget(self.open_button)
        actions.addWidget(self.unlink_button)
        actions.addStretch()
        actions.addWidget(self.refresh_button)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Linked articles", self))
        layout.addWidget(self.table, 1)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)
        self._runner.busy_changed.connect(self._update_controls)
        self._update_controls()

    def set_ticket(self, ticket_id):
        self._ticket_id = ticket_id
        self.table.replace_records(())
        self.feedback.setText("" if ticket_id is not None else "Open a ticket to see linked articles.")
        self._update_controls()

    def _update_controls(self, *_):
        enabled = (self._ticket_id is not None and self._service is not None
                   and not self._runner.busy and not self._confirming_unlink)
        self.link_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        self.open_button.setEnabled(enabled and self.table.selected_article_id() is not None)
        self.unlink_button.setEnabled(enabled and self.table.selected_article_id() is not None)

    def refresh_links(self, *, select_article_id=None, message=None):
        if self._ticket_id is None or self._service is None or self._runner.busy:
            return
        ticket_id = self._ticket_id
        if select_article_id is None:
            select_article_id = self.table.selected_article_id()
        self.feedback.setText(message or "Loading linked articles…")

        def loaded(links):
            if self._ticket_id != ticket_id:
                return
            self.table.replace_records(links, select_article_id)
            self.feedback.setText(message or ("" if links else "No knowledge articles linked."))
            self._update_controls()

        def failed(error):
            if self._ticket_id != ticket_id:
                return
            self.table.replace_records(())
            self.feedback.setText((message + " " if message else "") + _safe_message(error, "Could not load linked articles. Try again."))
            self._update_controls()

        self._runner.submit(lambda: self._service.list_linked_articles(ticket_id), loaded, failed)

    def open_link_dialog(self):
        if self._ticket_id is None or self._service is None or self._runner.busy:
            return None
        if self._dialog is not None and self._dialog.isVisible():
            return self._dialog
        dialog = LinkArticleDialog(self._service, self._runner, self._ticket_id, self)
        dialog.article_linked.connect(self._article_linked)
        self._dialog = dialog
        dialog.open()
        dialog.load_candidates()
        return dialog

    def _article_linked(self, link):
        if link.ticket_id == self._ticket_id:
            self.refresh_links(select_article_id=link.knowledge_article_id, message="Article linked.")

    def _confirm_unlink(self, article):
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Unlink Article")
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setTextFormat(Qt.TextFormat.PlainText)
        confirmation.setText(f"Remove {article.article_code} from this ticket?")
        confirmation.setInformativeText(
            "This removes only the relationship. The ticket and knowledge article will remain."
        )
        unlink = confirmation.addButton("Unlink", QMessageBox.ButtonRole.DestructiveRole)
        cancel = confirmation.addButton(QMessageBox.StandardButton.Cancel)
        confirmation.setDefaultButton(cancel)
        confirmation.setEscapeButton(cancel)
        confirmation.exec()
        accepted = confirmation.clickedButton() == unlink
        confirmation.deleteLater()
        return accepted

    def unlink_selected_article(self):
        article_id = self.table.selected_article_id()
        if (self._ticket_id is None or self._service is None or self._runner.busy
                or self._confirming_unlink or article_id is None):
            return
        ticket_id = self._ticket_id
        article = next(item for item in self.table.records if item.knowledge_article_id == article_id)
        self._confirming_unlink = True
        self._update_controls()
        try:
            confirmed = self._confirm_unlink(article)
        finally:
            self._confirming_unlink = False
            self._update_controls()
        # Confirmation runs an event loop. Do not act on a changed context.
        if (not confirmed or self._ticket_id != ticket_id or self._runner.busy
                or self.table.selected_article_id() != article_id):
            return
        self.feedback.setText("Unlinking article…")

        def unlinked(_result):
            if self._ticket_id == ticket_id:
                self.refresh_links(message="Article unlinked.")

        def failed(error):
            if self._ticket_id == ticket_id:
                self.feedback.setText(_safe_message(
                    error, "Could not unlink the article. Your selection is preserved. Try again.",
                ))

        self._runner.submit(
            lambda: self._service.unlink_related_article(ticket_id, article_id), unlinked, failed,
        )

    def open_selected_article(self):
        article_id = self.table.selected_article_id()
        if self._ticket_id is not None and article_id is not None and not self._runner.busy:
            self.knowledge_article_requested.emit(article_id)
