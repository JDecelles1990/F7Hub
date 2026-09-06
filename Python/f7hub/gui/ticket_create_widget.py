"""Minimal ticket-creation form backed by ``TicketService``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import logging

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from f7hub.repositories.ticket_repository import TicketRecord
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.quick_company_dialog import QuickCompanyDialog
from f7hub.services.company_service import CompanyService
from f7hub.services.ticket_reference_service import TicketReferenceOption, TicketReferenceService
from f7hub.services.ticket_service import (
    TicketValidationError,
)


@dataclass(frozen=True)
class TicketReferenceOptions:
    """Reference choices supplied by application composition code."""

    companies: tuple[TicketReferenceOption, ...] = ()
    contacts: tuple[TicketReferenceOption, ...] = ()
    categories: tuple[TicketReferenceOption, ...] = ()


class TicketCreationService(Protocol):
    """The service operation consumed by the ticket form."""

    def create_ticket(self, **values: object) -> TicketRecord:
        """Create and return a ticket."""


class TicketCreateWidget(QWidget):
    """Collect ticket input and delegate creation to a service."""

    ticket_created = Signal(object)
    submission_failed = Signal(str)

    def __init__(
        self,
        ticket_service: TicketCreationService,
        *,
        reference_options: TicketReferenceOptions | None = None,
        reference_service: TicketReferenceService | None = None,
        company_service: CompanyService | None = None,
        task_runner: ServiceTaskRunner | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ticket_service = ticket_service
        self._reference_options = reference_options or TicketReferenceOptions()
        self._task_runner = task_runner
        self._reference_service = reference_service
        self._company_service = company_service
        self._company_dialog = None
        self._pending_company_id = None
        self._references_started = False
        self._reference_timer = QTimer(self)
        self._reference_timer.setSingleShot(True)
        self._reference_timer.timeout.connect(self.refresh_references)
        self._submitting = False
        self._build_ui()
        if reference_service is not None:
            self.contact_input.setEnabled(False)
            self.company_input.currentIndexChanged.connect(self._company_changed)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._reference_service is not None and not self._references_started:
            self._references_started = True
            self._reference_timer.start(0)

    def _reference_task(self, work, success, failure) -> None:
        if self._task_runner is not None:
            self._task_runner.submit(work, success, failure)
        else:
            try:
                result = work()
            except Exception as error:
                failure(error)
            else:
                success(result)

    def refresh_references(self) -> None:
        """Refresh choices without clearing text or valid reference selections."""
        self.refresh_categories(on_finished=self._refresh_companies)

    def refresh_categories(self, *, on_finished=None) -> None:
        """Refresh category choices independently; failure retains prior selections."""
        if self._reference_service is None or (self._task_runner and self._task_runner.busy):
            return
        category_id = self.category_input.currentData()
        self.category_feedback.setText("Loading categories…")

        def loaded(options):
            self.category_input.clear()
            self.category_input.addItem("Not selected", None)
            for option in options:
                self.category_input.addItem(option.label, option.reference_id)
            self.category_input.setCurrentIndex(max(0, self.category_input.findData(category_id)))
            self.category_feedback.setText(
                "Category is optional." if options
                else "No active ticket categories. You can create a ticket without a category."
            )
            if on_finished is not None:
                on_finished()

        def failed(error):
            logging.getLogger(__name__).error("Category load failed: %s", type(error).__name__)
            self.category_feedback.setText(
                "Could not load categories. Your draft is preserved. Use Refresh categories to retry."
            )
            if on_finished is not None:
                on_finished()

        self._reference_task(self._reference_service.list_active_ticket_categories, loaded, failed)

    def _refresh_companies(self) -> None:
        if self._reference_service is None or (self._task_runner and self._task_runner.busy):
            return
        company_id = self._pending_company_id or self.company_input.currentData()
        contact_id = self.contact_input.currentData()
        self.reference_feedback.setText("Loading companies…")

        def loaded(options):
            self.company_input.blockSignals(True)
            self.company_input.clear()
            self.company_input.addItem("Not selected", None)
            for option in options:
                self.company_input.addItem(option.label, option.reference_id)
            self.company_input.setCurrentIndex(max(0, self.company_input.findData(company_id)))
            self.company_input.blockSignals(False)
            self._pending_company_id = None
            self.add_company_button.setEnabled(True)
            self._load_contacts(contact_id=contact_id)
            if not options:
                self.reference_feedback.setText("No active companies. You can create a ticket without references.")

        self._reference_task(self._reference_service.list_active_companies, loaded,
                             lambda error: self._reference_failed(error, "companies"))

    def _company_changed(self) -> None:
        self._pending_company_id = None
        self.add_company_button.setEnabled(True)
        self._load_contacts()

    def open_company_dialog(self) -> None:
        if (self._company_service is None or self._task_runner is None
                or self._task_runner.busy or self._pending_company_id is not None):
            return
        if self._company_dialog is not None:
            self._company_dialog.raise_()
            return
        dialog = QuickCompanyDialog(self._company_service, self._task_runner, self)
        self._company_dialog = dialog
        dialog.company_created.connect(self._company_created)
        dialog.finished.connect(self._company_dialog_finished)
        dialog.open()
        dialog.name_input.setFocus()

    def _company_dialog_finished(self) -> None:
        dialog = self._company_dialog
        self._company_dialog = None
        dialog.deleteLater()

    def _company_created(self, company) -> None:
        # The write has committed. Retain its ID across any failed selector reload.
        self._pending_company_id = company.company_id
        self.status_label.setText("Company created successfully.")
        self.status_label.setVisible(True)
        self.add_company_button.setEnabled(False)
        self.company_input.blockSignals(True)
        self.company_input.setCurrentIndex(0)
        self.company_input.blockSignals(False)
        self.contact_input.clear()
        self.contact_input.addItem("Not selected", None)
        self.contact_input.setEnabled(False)
        self._refresh_companies()

    def _load_contacts(self, *, contact_id=None) -> None:
        company_id = self.company_input.currentData()
        previous_options = tuple(
            (self.contact_input.itemText(index), self.contact_input.itemData(index))
            for index in range(1, self.contact_input.count())
        ) if contact_id is not None else ()
        self.contact_input.clear()
        self.contact_input.addItem("Not selected", None)
        self.contact_input.setEnabled(False)
        if company_id is None:
            self.reference_feedback.setText("Select a company to choose a contact. References are optional.")
            return
        self.reference_feedback.setText("Loading contacts…")

        def loaded(options):
            # Ignore a result if the form was reset or its company changed.
            if self.company_input.currentData() != company_id:
                return
            for option in options:
                self.contact_input.addItem(option.label, option.reference_id)
            self.contact_input.setCurrentIndex(max(0, self.contact_input.findData(contact_id)))
            self.contact_input.setEnabled(bool(options))
            self.reference_feedback.setText(
                "Contact is optional." if options else "No active contacts for this company."
            )

        def failed(error):
            if self.company_input.currentData() != company_id:
                return
            # A refresh failure keeps the prior selection; save revalidates it.
            for label, reference_id in previous_options:
                self.contact_input.addItem(label, reference_id)
            self.contact_input.setCurrentIndex(max(0, self.contact_input.findData(contact_id)))
            self.contact_input.setEnabled(bool(previous_options))
            self._reference_failed(error, "contacts")

        self._reference_task(
            lambda: self._reference_service.list_active_contacts_for_company(company_id),
            loaded, failed,
        )

    def _reference_failed(self, error, kind) -> None:
        logging.getLogger(__name__).error("Reference load failed: %s", type(error).__name__)
        self.reference_feedback.setText(
            ("Company created successfully. " if self._pending_company_id is not None else "")
            + f"Could not load {kind}. Your ticket draft is preserved. Use Refresh references to retry."
        )

    def submit(self) -> None:
        """Validate presentation input and invoke the ticket service once."""

        if self._submitting or (self._task_runner and self._task_runner.busy):
            return
        if self._pending_company_id is not None:
            self.reference_feedback.setText(
                "Company created successfully. Use Refresh references before saving this ticket."
            )
            return
        self._clear_feedback()
        subject = self.subject_input.text()
        if not subject.strip():
            self._show_field_error(
                self.subject_error,
                self.subject_input,
                "Subject is required.",
            )
            return

        values = dict(
            ticket_number=self.ticket_number_input.text().strip() or None,
            subject=subject,
            ticket_type=str(self.ticket_type_input.currentData()),
            priority=str(self.priority_input.currentData()),
            company_id=self.company_input.currentData(),
            contact_id=self.contact_input.currentData(),
            category_id=self.category_input.currentData(),
            description=self.description_input.toPlainText(),
        )
        self.save_button.setEnabled(False)
        self._submitting = True
        if self._task_runner is not None:
            self._task_runner.submit(
                lambda: self._ticket_service.create_ticket(**values),
                self._submit_succeeded, self._submit_failed,
            )
        else:
            try:
                ticket = self._ticket_service.create_ticket(**values)
            except Exception as error:
                self._submit_failed(error)
            else:
                self._submit_succeeded(ticket)

    def _submit_failed(self, error: Exception) -> None:
        self._submitting = False
        self.save_button.setEnabled(True)
        if isinstance(error, TicketValidationError):
            self._show_validation_error(str(error))
            self.submission_failed.emit(str(error))
        else:
            logging.getLogger(__name__).error("Ticket save failed: %s", type(error).__name__)
            message = (
                "F7Hub could not save the ticket. "
                "Your entered information has been preserved."
            )
            self.form_error.setText(message)
            self.form_error.setVisible(True)
            self.submission_failed.emit(message)

    def _submit_succeeded(self, ticket: TicketRecord) -> None:
        self._submitting = False
        self.save_button.setEnabled(True)
        self.status_label.setText(
            f"Created ticket {ticket.ticket_number} successfully."
        )
        self.status_label.setVisible(True)
        self.ticket_created.emit(ticket)

    def has_draft(self) -> bool:
        return bool(
            self.ticket_number_input.text() or self.subject_input.text()
            or self.description_input.toPlainText()
            or self.ticket_type_input.currentIndex() != 0
            or self.priority_input.currentIndex() != 1
            or any(combo.currentIndex() > 0 for combo in (
                self.company_input, self.contact_input, self.category_input,
            ))
        )

    def reset_form(self) -> None:
        """Clear a successfully saved form before the next ticket."""
        self._pending_company_id = None
        self.add_company_button.setEnabled(True)
        self.ticket_number_input.clear()
        self.subject_input.clear()
        self.description_input.clear()
        self.ticket_type_input.setCurrentIndex(0)
        self.priority_input.setCurrentIndex(1)
        for combo in (self.company_input, self.contact_input, self.category_input):
            combo.setCurrentIndex(0)
        self._clear_feedback()

    def _build_ui(self) -> None:
        self.setObjectName("ticketCreateWidget")
        self.setWindowTitle("New Ticket")
        self.setFont(QFont("Segoe UI", 10))

        heading = QLabel("New Ticket", self)
        heading.setObjectName("ticketCreateHeading")
        heading_font = QFont(self.font())
        heading_font.setPointSize(18)
        heading_font.setBold(True)
        heading.setFont(heading_font)

        self.ticket_number_input = QLineEdit(self)
        self.ticket_number_input.setObjectName("ticketNumberInput")
        self.ticket_number_input.setPlaceholderText("Generated automatically if blank")
        self.ticket_number_input.setAccessibleName("Ticket number")

        self.ticket_number_error = self._new_error_label("ticketNumberError")

        self.subject_input = QLineEdit(self)
        self.subject_input.setObjectName("ticketSubjectInput")
        self.subject_input.setAccessibleName("Subject, required")
        self.subject_error = self._new_error_label("ticketSubjectError")

        self.ticket_type_input = QComboBox(self)
        self.ticket_type_input.setObjectName("ticketTypeInput")
        self.ticket_type_input.setAccessibleName("Ticket type")
        for label, value in (
            ("Incident", "INCIDENT"),
            ("Service request", "SERVICE_REQUEST"),
            ("Problem", "PROBLEM"),
            ("Task", "TASK"),
        ):
            self.ticket_type_input.addItem(label, value)

        self.priority_input = QComboBox(self)
        self.priority_input.setObjectName("ticketPriorityInput")
        self.priority_input.setAccessibleName("Priority")
        for label, value in (
            ("Low", "LOW"),
            ("Medium", "MEDIUM"),
            ("High", "HIGH"),
            ("Critical", "CRITICAL"),
        ):
            self.priority_input.addItem(label, value)
        self.priority_input.setCurrentIndex(1)

        self.company_input = self._new_reference_combo(
            "ticketCompanyInput",
            "Company",
            self._reference_options.companies,
        )
        self.contact_input = self._new_reference_combo(
            "ticketContactInput",
            "Contact",
            self._reference_options.contacts,
        )
        self.category_input = self._new_reference_combo(
            "ticketCategoryInput",
            "Category",
            self._reference_options.categories,
        )
        self.reference_feedback = QLabel(self)
        self.reference_feedback.setWordWrap(True)
        self.refresh_references_button = QPushButton("Refresh references", self)
        self.refresh_references_button.clicked.connect(self.refresh_references)
        self.refresh_references_button.setVisible(self._reference_service is not None)
        self.category_feedback = QLabel(self)
        self.category_feedback.setWordWrap(True)
        self.refresh_categories_button = QPushButton("Refresh categories", self)
        self.refresh_categories_button.clicked.connect(self.refresh_categories)
        self.refresh_categories_button.setVisible(self._reference_service is not None)

        self.description_input = QTextEdit(self)
        self.description_input.setObjectName("ticketDescriptionInput")
        self.description_input.setAccessibleName("Description")
        self.description_input.setAcceptRichText(False)
        self.description_input.setMinimumHeight(100)
        self.description_input.setMaximumHeight(220)

        form = QFormLayout()
        form.addRow("Ticket number", self.ticket_number_input)
        form.addRow("", self.ticket_number_error)
        form.addRow("Subject *", self.subject_input)
        form.addRow("", self.subject_error)
        form.addRow("Type", self.ticket_type_input)
        form.addRow("Priority", self.priority_input)
        company_row = QHBoxLayout()
        company_row.addWidget(self.company_input, 1)
        self.add_company_button = QPushButton("Add Company", self)
        self.add_company_button.setObjectName("addCompanyButton")
        self.add_company_button.setAutoDefault(False)
        self.add_company_button.clicked.connect(self.open_company_dialog)
        self.add_company_button.setVisible(
            self._company_service is not None and self._reference_service is not None
            and self._task_runner is not None
        )
        company_row.addWidget(self.add_company_button)
        form.addRow("Company", company_row)
        form.addRow("Contact", self.contact_input)
        if self._reference_service is not None:
            form.addRow("", self.reference_feedback)
            form.addRow("", self.refresh_references_button)
        form.addRow("Category", self.category_input)
        if self._reference_service is not None:
            category_state = QHBoxLayout()
            category_state.addWidget(self.category_feedback, 1)
            category_state.addWidget(self.refresh_categories_button)
            form.addRow("", category_state)
        form.addRow("Description", self.description_input)

        self.form_error = self._new_error_label("ticketFormError")
        self.status_label = QLabel(self)
        self.status_label.setObjectName("ticketStatusLabel")
        self.status_label.setProperty("successMessage", True)
        self.status_label.setVisible(False)

        self.save_button = QPushButton("Create Ticket", self)
        self.save_button.setObjectName("createTicketButton")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.submit)

        actions = QHBoxLayout()
        actions.addWidget(self.status_label, 1)
        actions.addStretch()
        actions.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(heading)
        layout.addLayout(form)
        layout.addWidget(self.form_error)
        layout.addLayout(actions)
        layout.addStretch()

        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.submit)
        self._save_shortcut = save_shortcut

    def _new_reference_combo(
        self,
        object_name: str,
        accessible_name: str,
        options: tuple[TicketReferenceOption, ...],
    ) -> QComboBox:
        combo = QComboBox(self)
        combo.setObjectName(object_name)
        combo.setAccessibleName(accessible_name)
        combo.addItem("Not selected", None)
        for option in options:
            combo.addItem(option.label, option.reference_id)
        return combo

    def _new_error_label(self, object_name: str) -> QLabel:
        label = QLabel(self)
        label.setObjectName(object_name)
        label.setProperty("validationError", True)
        label.setWordWrap(True)
        label.setVisible(False)
        return label

    def _clear_feedback(self) -> None:
        for label in (
            self.ticket_number_error,
            self.subject_error,
            self.form_error,
            self.status_label,
        ):
            label.clear()
            label.setVisible(False)

    def _show_validation_error(self, message: str) -> None:
        if message.startswith("subject "):
            self._show_field_error(self.subject_error, self.subject_input, message)
        elif message.startswith("ticket_number "):
            self._show_field_error(
                self.ticket_number_error,
                self.ticket_number_input,
                message,
            )
        else:
            self.form_error.setText(message)
            self.form_error.setVisible(True)

    @staticmethod
    def _show_field_error(
        label: QLabel,
        field: QLineEdit,
        message: str,
    ) -> None:
        label.setText(message)
        label.setVisible(True)
        field.setFocus()
