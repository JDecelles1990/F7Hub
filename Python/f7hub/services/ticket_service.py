"""Ticket creation, notes, and lifecycle workflow coordination."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import json
import sqlite3
from uuid import uuid4

from f7hub.repositories.ticket_repository import (
    TicketDetailsRecord,
    TicketNoteRecord,
    TicketRecord,
    TicketRepository,
    TicketRepositoryTransaction,
)


TICKET_TYPES = frozenset({"INCIDENT", "SERVICE_REQUEST", "PROBLEM", "TASK"})
TICKET_PRIORITIES = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
INITIAL_TICKET_STATUS = "NEW"
TICKET_CREATED_EVENT_TYPE = "TICKET_CREATED"
TICKET_CREATED_EVENT_TITLE = "Ticket created"
TICKET_NOTE_TYPES = frozenset({"INTERNAL", "PUBLIC", "WORKLOG", "RESOLUTION"})
TICKET_STATUS_TRANSITIONS = {
    "NEW": frozenset({"OPEN", "IN_PROGRESS", "WAITING", "RESOLVED", "CANCELLED"}),
    "OPEN": frozenset({"IN_PROGRESS", "WAITING", "RESOLVED", "CANCELLED"}),
    "IN_PROGRESS": frozenset({"OPEN", "WAITING", "RESOLVED", "CANCELLED"}),
    "WAITING": frozenset({"OPEN", "IN_PROGRESS", "RESOLVED", "CANCELLED"}),
    "RESOLVED": frozenset({"OPEN", "CLOSED"}),
    "CLOSED": frozenset({"OPEN"}),
    "CANCELLED": frozenset(),
}
TICKET_STATUSES = frozenset(TICKET_STATUS_TRANSITIONS)


class TicketValidationError(ValueError):
    """Raised when ticket input violates a workflow requirement."""


class TicketNotFoundError(TicketValidationError):
    """Raised when a workflow targets a ticket that no longer exists."""


class TicketCreationError(RuntimeError):
    """Raised when persistence prevents completion of ticket creation."""


class TicketUpdateError(RuntimeError):
    """Raised when persistence prevents a note or status change."""


class TicketReadError(RuntimeError):
    """Raised when ticket data cannot be loaded."""


class TicketService:
    """Validate and atomically coordinate ticket workflows."""

    def __init__(
        self,
        ticket_repository: TicketRepository,
        *,
        clock: Callable[[], datetime] | None = None,
        ticket_number_factory: Callable[[], str] | None = None,
    ) -> None:
        self._ticket_repository = ticket_repository
        self._clock = clock or _utc_now
        self._ticket_number_factory = ticket_number_factory or _new_ticket_number

    def create_ticket(
        self,
        *,
        subject: str,
        ticket_number: str | None = None,
        ticket_type: str = "INCIDENT",
        priority: str = "MEDIUM",
        company_id: int | None = None,
        contact_id: int | None = None,
        category_id: int | None = None,
        description: str | None = None,
        assigned_to: str | None = None,
        source: str | None = None,
        created_by: str | None = None,
    ) -> TicketRecord:
        """Create a ticket, initial status history, and timeline event atomically."""

        clean_subject = _required_text(subject, "subject")
        candidate_ticket_number = (
            ticket_number
            if ticket_number is not None
            else self._ticket_number_factory()
        )
        clean_ticket_number = _required_text(
            candidate_ticket_number,
            "ticket_number",
        )
        clean_ticket_type = _choice(ticket_type, "ticket_type", TICKET_TYPES)
        clean_priority = _choice(priority, "priority", TICKET_PRIORITIES)
        clean_description = _optional_text(description, "description")
        clean_assigned_to = _optional_text(assigned_to, "assigned_to")
        clean_source = _optional_text(source, "source")
        clean_created_by = _optional_text(created_by, "created_by")
        _validate_optional_id(company_id, "company_id")
        _validate_optional_id(contact_id, "contact_id")
        _validate_optional_id(category_id, "category_id")

        timestamp = _format_utc_timestamp(self._clock())
        try:
            with self._ticket_repository.transaction() as transaction:
                self._validate_references(
                    transaction,
                    company_id=company_id,
                    contact_id=contact_id,
                    category_id=category_id,
                )
                ticket = transaction.create_ticket(
                    ticket_number=clean_ticket_number,
                    ticket_type=clean_ticket_type,
                    status=INITIAL_TICKET_STATUS,
                    priority=clean_priority,
                    company_id=company_id,
                    contact_id=contact_id,
                    category_id=category_id,
                    subject=clean_subject,
                    description=clean_description,
                    assigned_to=clean_assigned_to,
                    source=clean_source,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
                transaction.create_status_history(
                    ticket_id=ticket.ticket_id,
                    previous_status=None,
                    new_status=INITIAL_TICKET_STATUS,
                    reason="Ticket created",
                    changed_by=clean_created_by,
                    changed_at=timestamp,
                )
                transaction.create_timeline_event(
                    ticket_id=ticket.ticket_id,
                    event_type=TICKET_CREATED_EVENT_TYPE,
                    title=TICKET_CREATED_EVENT_TITLE,
                    actor_label=clean_created_by,
                    occurred_at=timestamp,
                )
                return ticket
        except sqlite3.Error as error:
            raise TicketCreationError("F7Hub could not create the ticket.") from error

    def list_tickets(
        self, *, status: str | None = None, limit: int = 100, offset: int = 0,
    ) -> tuple[TicketRecord, ...]:
        if status is not None:
            _choice(status, "status", TICKET_STATUSES)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
            raise TicketValidationError("limit must be an integer from 1 to 200.")
        if isinstance(offset, bool) or not isinstance(offset, int) or not 0 <= offset <= 2**63 - 1:
            raise TicketValidationError("offset must be a non-negative SQLite integer.")
        try:
            return self._ticket_repository.list_tickets(status=status, limit=limit, offset=offset)
        except sqlite3.Error as error:
            raise TicketReadError("F7Hub could not load the ticket list.") from error

    def get_ticket_details(self, ticket_id: int) -> TicketDetailsRecord:
        _validate_ticket_id(ticket_id)
        try:
            details = self._ticket_repository.get_ticket_details(ticket_id)
            if details is None:
                raise TicketNotFoundError("The ticket does not exist.")
            return details
        except sqlite3.Error as error:
            raise TicketReadError("F7Hub could not load the ticket.") from error

    @staticmethod
    def allowed_statuses(status: str) -> tuple[str, ...]:
        """Expose workflow choices to presentation without duplicating rules."""

        _choice(status, "status", TICKET_STATUSES)
        return tuple(sorted(TICKET_STATUS_TRANSITIONS[status]))

    def add_note(
        self,
        ticket_id: int,
        *,
        note_text: str,
        note_type: str = "INTERNAL",
        author_label: str | None = None,
        source: str | None = None,
        is_ai_generated: bool = False,
    ) -> TicketNoteRecord:
        """Save a note, its timeline reference, and ticket activity atomically.

        A RESOLUTION-typed note alone does not change ticket status.
        """

        _validate_ticket_id(ticket_id)
        clean_text = _required_text(note_text, "note_text")
        clean_type = _choice(note_type, "note_type", TICKET_NOTE_TYPES)
        clean_author = _optional_text(author_label, "author_label")
        clean_source = _optional_text(source, "source")
        if not isinstance(is_ai_generated, bool):
            raise TicketValidationError("is_ai_generated must be a boolean.")

        try:
            with self._ticket_repository.transaction() as transaction:
                _require_ticket(transaction.get_ticket(ticket_id))
                timestamp = _format_utc_timestamp(self._clock())
                note = self._append_note(
                    transaction,
                    ticket_id=ticket_id,
                    note_text=clean_text,
                    note_type=clean_type,
                    author_label=clean_author,
                    source=clean_source,
                    is_ai_generated=is_ai_generated,
                    timestamp=timestamp,
                )
                _require_ticket(transaction.update_ticket_activity(
                    ticket_id, updated_at=timestamp
                ))
                return note
        except sqlite3.Error as error:
            raise TicketUpdateError("F7Hub could not save the ticket note.") from error

    def change_status(
        self,
        ticket_id: int,
        *,
        new_status: str,
        resolution: str | None = None,
        reason: str | None = None,
        changed_by: str | None = None,
    ) -> TicketRecord:
        """Change status with history, timeline, and any resolution note.

        Resolved and closed tickets can reopen to OPEN. Prior resolutions
        remain in notes; current resolution/lifecycle fields clear on reopen.
        """

        _validate_ticket_id(ticket_id)
        clean_status = _choice(new_status, "new_status", TICKET_STATUSES)
        clean_reason = _optional_text(reason, "reason")
        clean_actor = _optional_text(changed_by, "changed_by")
        clean_resolution = _optional_text(resolution, "resolution")
        if clean_status == "RESOLVED":
            clean_resolution = _required_text(resolution, "resolution")
        elif resolution is not None:
            raise TicketValidationError(
                "resolution may only be supplied when changing status to RESOLVED."
            )

        try:
            with self._ticket_repository.transaction() as transaction:
                current = _require_ticket(transaction.get_ticket(ticket_id))
                if clean_status not in TICKET_STATUS_TRANSITIONS[current.status]:
                    raise TicketValidationError(
                        f"Cannot change ticket status from {current.status} "
                        f"to {clean_status}."
                    )
                timestamp = _format_utc_timestamp(self._clock())
                resolved_at = None
                closed_at = None
                if clean_status == "RESOLVED":
                    resolved_at = timestamp
                    self._append_note(
                        transaction,
                        ticket_id=ticket_id,
                        note_text=clean_resolution,
                        note_type="RESOLUTION",
                        author_label=clean_actor,
                        source=None,
                        is_ai_generated=False,
                        timestamp=timestamp,
                    )
                elif clean_status == "CLOSED":
                    clean_resolution = current.resolution
                    resolved_at = current.resolved_at
                    closed_at = timestamp
                elif (
                    current.status in {"RESOLVED", "CLOSED"}
                    and current.resolution
                    and current.resolution.strip()
                    and not any(
                        note.note_type == "RESOLUTION"
                        and note.note_text == current.resolution
                        for note in transaction.list_notes(ticket_id)
                    )
                ):
                    # Older or imported rows may predate automatic resolution
                    # notes. Preserve their only resolution copy before reopen.
                    self._append_note(
                        transaction,
                        ticket_id=ticket_id,
                        note_text=current.resolution,
                        note_type="RESOLUTION",
                        author_label=None,
                        source="REOPEN_SNAPSHOT",
                        is_ai_generated=False,
                        timestamp=timestamp,
                    )

                ticket = _require_ticket(transaction.update_ticket_status(
                    ticket_id,
                    status=clean_status,
                    resolution=clean_resolution,
                    resolved_at=resolved_at,
                    closed_at=closed_at,
                    updated_at=timestamp,
                ))
                transaction.create_status_history(
                    ticket_id=ticket_id,
                    previous_status=current.status,
                    new_status=clean_status,
                    reason=clean_reason,
                    changed_by=clean_actor,
                    changed_at=timestamp,
                )
                transaction.create_timeline_event(
                    ticket_id=ticket_id,
                    event_type="STATUS_CHANGED",
                    title=f"Status changed from {current.status} to {clean_status}",
                    details=clean_reason,
                    metadata_json=json.dumps({
                        "previous_status": current.status,
                        "new_status": clean_status,
                    }),
                    actor_label=clean_actor,
                    occurred_at=timestamp,
                )
                return ticket
        except sqlite3.Error as error:
            raise TicketUpdateError("F7Hub could not change the ticket status.") from error

    @staticmethod
    def _append_note(
        transaction: TicketRepositoryTransaction,
        *,
        ticket_id: int,
        note_text: str,
        note_type: str,
        author_label: str | None,
        source: str | None,
        is_ai_generated: bool,
        timestamp: str,
    ) -> TicketNoteRecord:
        note = transaction.create_note(
            ticket_id=ticket_id,
            note_text=note_text,
            note_type=note_type,
            author_label=author_label,
            source=source,
            is_ai_generated=is_ai_generated,
            created_at=timestamp,
            updated_at=timestamp,
        )
        transaction.create_timeline_event(
            ticket_id=ticket_id,
            event_type="NOTE_ADDED",
            title="Ticket note added",
            metadata_json=json.dumps({"ticket_note_id": note.ticket_note_id}),
            actor_label=author_label,
            occurred_at=timestamp,
        )
        return note

    @staticmethod
    def _validate_references(
        transaction: TicketRepositoryTransaction,
        *,
        company_id: int | None,
        contact_id: int | None,
        category_id: int | None,
    ) -> None:
        if company_id is not None and not transaction.company_exists(company_id):
            raise TicketValidationError("company_id does not reference a company.")

        if contact_id is not None:
            contact_exists, contact_company_id = transaction.get_contact_reference(
                contact_id
            )
            if not contact_exists:
                raise TicketValidationError("contact_id does not reference a contact.")
            if (
                company_id is not None
                and contact_company_id is not None
                and contact_company_id != company_id
            ):
                raise TicketValidationError(
                    "contact_id does not belong to the selected company."
                )

        if (
            category_id is not None
            and not transaction.ticket_category_exists(category_id)
        ):
            raise TicketValidationError(
                "category_id must reference an active TICKET category."
            )


def _validate_ticket_id(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TicketValidationError("ticket_id must be a positive integer.")


def _require_ticket(ticket: TicketRecord | None) -> TicketRecord:
    if ticket is None:
        raise TicketNotFoundError("The ticket does not exist.")
    return ticket


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TicketValidationError(f"{field_name} must be non-blank text.")
    return value.strip()


def _optional_text(value: object | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TicketValidationError(f"{field_name} must be text or None.")
    clean_value = value.strip()
    return clean_value or None


def _choice(value: object, field_name: str, choices: frozenset[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        allowed = ", ".join(sorted(choices))
        raise TicketValidationError(f"{field_name} must be one of: {allowed}.")
    return value


def _validate_optional_id(value: object | None, field_name: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TicketValidationError(f"{field_name} must be a positive integer or None.")


def _format_utc_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise TypeError("clock must return a datetime.")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime.")
    utc_value = value.astimezone(timezone.utc)
    return utc_value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_ticket_number() -> str:
    return f"TKT-{uuid4().hex.upper()}"
