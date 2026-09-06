"""SQLite persistence for tickets, notes, and activity records."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Iterator

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class TicketRecord:
    """One ticket row returned by the repository."""

    ticket_id: int
    ticket_number: str
    ticket_type: str
    status: str
    priority: str
    company_id: int | None
    contact_id: int | None
    category_id: int | None
    subject: str
    description: str | None
    resolution: str | None
    assigned_to: str | None
    source: str | None
    created_at: str
    updated_at: str
    resolved_at: str | None
    closed_at: str | None


@dataclass(frozen=True)
class TicketNoteRecord:
    """One persisted ticket note with its authorship and origin metadata."""

    ticket_note_id: int
    ticket_id: int
    note_type: str
    note_text: str
    author_label: str | None
    source: str | None
    is_ai_generated: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class TicketStatusHistoryRecord:
    """One persisted ticket status-history row."""

    ticket_status_history_id: int
    ticket_id: int
    previous_status: str | None
    new_status: str
    reason: str | None
    changed_by: str | None
    changed_at: str


@dataclass(frozen=True)
class TicketTimelineEventRecord:
    """One persisted ticket timeline event."""

    ticket_timeline_event_id: int
    ticket_id: int
    event_type: str
    title: str
    details: str | None
    metadata_json: str | None
    actor_label: str | None
    occurred_at: str


@dataclass(frozen=True)
class TicketDetailsRecord:
    """A ticket and its activity read from one SQLite snapshot."""

    ticket: TicketRecord
    notes: tuple[TicketNoteRecord, ...]
    status_history: tuple[TicketStatusHistoryRecord, ...]
    timeline_events: tuple[TicketTimelineEventRecord, ...]
    company_name: str | None = None
    contact_name: str | None = None
    category_name: str | None = None


_TICKET_COLUMNS = """
    ticket_id,
    ticket_number,
    ticket_type,
    status,
    priority,
    company_id,
    contact_id,
    category_id,
    subject,
    description,
    resolution,
    assigned_to,
    source,
    created_at,
    updated_at,
    resolved_at,
    closed_at
"""

_NOTE_COLUMNS = """
    ticket_note_id,
    ticket_id,
    note_type,
    note_text,
    author_label,
    source,
    is_ai_generated,
    created_at,
    updated_at
"""

_STATUS_HISTORY_COLUMNS = """
    ticket_status_history_id,
    ticket_id,
    previous_status,
    new_status,
    reason,
    changed_by,
    changed_at
"""

_TIMELINE_EVENT_COLUMNS = """
    ticket_timeline_event_id,
    ticket_id,
    event_type,
    title,
    details,
    metadata_json,
    actor_label,
    occurred_at
"""


class TicketRepository:
    """Persist tickets through configured SQLite connections."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def create_ticket(
        self,
        *,
        ticket_number: str,
        subject: str,
        created_at: str,
        updated_at: str,
        ticket_type: str = "INCIDENT",
        status: str = "NEW",
        priority: str = "MEDIUM",
        company_id: int | None = None,
        contact_id: int | None = None,
        category_id: int | None = None,
        description: str | None = None,
        resolution: str | None = None,
        assigned_to: str | None = None,
        source: str | None = None,
        resolved_at: str | None = None,
        closed_at: str | None = None,
    ) -> TicketRecord:
        """Insert and reload one ticket in its own transaction.

        Workflow-level validation and related-record coordination belong to
        ``TicketService``. This method intentionally persists only the ticket.
        """

        with self.transaction() as transaction:
            return transaction.create_ticket(
                ticket_number=ticket_number,
                subject=subject,
                created_at=created_at,
                updated_at=updated_at,
                ticket_type=ticket_type,
                status=status,
                priority=priority,
                company_id=company_id,
                contact_id=contact_id,
                category_id=category_id,
                description=description,
                resolution=resolution,
                assigned_to=assigned_to,
                source=source,
                resolved_at=resolved_at,
                closed_at=closed_at,
            )

    def get_ticket(self, ticket_id: int) -> TicketRecord | None:
        """Return a ticket by internal ID, or ``None`` when absent."""

        with database_connection(self._database_path) as connection:
            return _get_ticket(connection, ticket_id)

    def list_tickets(
        self, *, status: str | None = None, limit: int = 100, offset: int = 0,
    ) -> tuple[TicketRecord, ...]:
        """Return a bounded page, most recently updated first, with ID ties."""

        predicate = "" if status is None else "WHERE status = ?"
        parameters = (limit, offset) if status is None else (status, limit, offset)
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                f"SELECT {_TICKET_COLUMNS} FROM tickets {predicate} "
                "ORDER BY updated_at DESC, ticket_id DESC LIMIT ? OFFSET ?",
                parameters,
            ).fetchall()
        return tuple(_ticket_from_row(row) for row in rows)

    def get_ticket_details(self, ticket_id: int) -> TicketDetailsRecord | None:
        """Read ticket and activity consistently without reserving the writer."""

        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN")
            ticket = _get_ticket(connection, ticket_id)
            if ticket is None:
                return None
            references = connection.execute(
                "SELECT c.name AS company_name, p.display_name AS contact_name, k.name AS category_name "
                "FROM tickets t LEFT JOIN companies c ON c.company_id = t.company_id "
                "LEFT JOIN contacts p ON p.contact_id = t.contact_id "
                "LEFT JOIN categories k ON k.category_id = t.category_id WHERE t.ticket_id = ?",
                (ticket_id,),
            ).fetchone()
            return TicketDetailsRecord(
                ticket, _list_notes(connection, ticket_id),
                _list_status_history(connection, ticket_id),
                _list_timeline_events(connection, ticket_id),
                references["company_name"], references["contact_name"],
                references["category_name"],
            )

    def get_ticket_by_number(self, ticket_number: str) -> TicketRecord | None:
        """Return a ticket by its case-insensitive technician reference."""

        with database_connection(self._database_path) as connection:
            row = connection.execute(
                f"""
                SELECT {_TICKET_COLUMNS}
                FROM tickets
                WHERE ticket_number = ?
                """,
                (ticket_number,),
            ).fetchone()
        return _ticket_from_row(row) if row is not None else None

    def get_note(self, ticket_note_id: int) -> TicketNoteRecord | None:
        """Return a note by internal ID, or ``None`` when absent."""

        with database_connection(self._database_path) as connection:
            return _get_note(connection, ticket_note_id)

    def list_notes(self, ticket_id: int) -> tuple[TicketNoteRecord, ...]:
        """Return a ticket's notes in stable chronological order."""

        with database_connection(self._database_path) as connection:
            return _list_notes(connection, ticket_id)

    def list_status_history(
        self,
        ticket_id: int,
    ) -> tuple[TicketStatusHistoryRecord, ...]:
        """Return a ticket's status history in stable chronological order."""

        with database_connection(self._database_path) as connection:
            return _list_status_history(connection, ticket_id)

    def list_timeline_events(
        self,
        ticket_id: int,
    ) -> tuple[TicketTimelineEventRecord, ...]:
        """Return a ticket's timeline in stable chronological order."""

        with database_connection(self._database_path) as connection:
            return _list_timeline_events(connection, ticket_id)

    @contextmanager
    def transaction(self) -> Iterator[TicketRepositoryTransaction]:
        """Yield one atomic writer transaction, reserving writes before reads."""

        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            transaction = TicketRepositoryTransaction(connection)
            try:
                yield transaction
            except BaseException:
                connection.rollback()
                raise
            else:
                connection.commit()


class TicketRepositoryTransaction:
    """Ticket repository operations bound to one private SQLite transaction."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_notes(self, ticket_id: int) -> tuple[TicketNoteRecord, ...]:
        """Read notes within the same transaction as a lifecycle update."""

        return _list_notes(self._connection, ticket_id)

    def get_ticket(self, ticket_id: int) -> TicketRecord | None:
        """Read the current ticket using this transaction's connection."""

        return _get_ticket(self._connection, ticket_id)

    def create_ticket(
        self,
        *,
        ticket_number: str,
        subject: str,
        created_at: str,
        updated_at: str,
        ticket_type: str = "INCIDENT",
        status: str = "NEW",
        priority: str = "MEDIUM",
        company_id: int | None = None,
        contact_id: int | None = None,
        category_id: int | None = None,
        description: str | None = None,
        resolution: str | None = None,
        assigned_to: str | None = None,
        source: str | None = None,
        resolved_at: str | None = None,
        closed_at: str | None = None,
    ) -> TicketRecord:
        """Insert and reload one ticket using this transaction."""

        cursor = self._connection.execute(
            """
            INSERT INTO tickets (
                ticket_number,
                ticket_type,
                status,
                priority,
                company_id,
                contact_id,
                category_id,
                subject,
                description,
                resolution,
                assigned_to,
                source,
                created_at,
                updated_at,
                resolved_at,
                closed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_number,
                ticket_type,
                status,
                priority,
                company_id,
                contact_id,
                category_id,
                subject,
                description,
                resolution,
                assigned_to,
                source,
                created_at,
                updated_at,
                resolved_at,
                closed_at,
            ),
        )
        ticket = _get_ticket(self._connection, int(cursor.lastrowid))
        if ticket is None:
            raise RuntimeError("Inserted ticket could not be reloaded.")
        return ticket

    def create_note(
        self,
        *,
        ticket_id: int,
        note_text: str,
        created_at: str,
        updated_at: str,
        note_type: str = "INTERNAL",
        author_label: str | None = None,
        source: str | None = None,
        is_ai_generated: bool = False,
    ) -> TicketNoteRecord:
        """Insert and reload a note; related activity is service-coordinated."""

        cursor = self._connection.execute(
            """
            INSERT INTO ticket_notes (
                ticket_id,
                note_type,
                note_text,
                author_label,
                source,
                is_ai_generated,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                note_type,
                note_text,
                author_label,
                source,
                is_ai_generated,
                created_at,
                updated_at,
            ),
        )
        note = _get_note(self._connection, int(cursor.lastrowid))
        if note is None:
            raise RuntimeError("Inserted ticket note could not be reloaded.")
        return note

    def update_ticket_activity(
        self,
        ticket_id: int,
        *,
        updated_at: str,
    ) -> TicketRecord | None:
        """Update only the ticket activity timestamp and reload the row."""

        self._connection.execute(
            "UPDATE tickets SET updated_at = ? WHERE ticket_id = ?",
            (updated_at, ticket_id),
        )
        return _get_ticket(self._connection, ticket_id)

    def update_ticket_status(
        self,
        ticket_id: int,
        *,
        status: str,
        resolution: str | None,
        resolved_at: str | None,
        closed_at: str | None,
        updated_at: str,
    ) -> TicketRecord | None:
        """Persist service-selected lifecycle values and reload the ticket."""

        self._connection.execute(
            """
            UPDATE tickets
            SET status = ?, resolution = ?, resolved_at = ?, closed_at = ?,
                updated_at = ?
            WHERE ticket_id = ?
            """,
            (status, resolution, resolved_at, closed_at, updated_at, ticket_id),
        )
        return _get_ticket(self._connection, ticket_id)

    def create_status_history(
        self,
        *,
        ticket_id: int,
        previous_status: str | None,
        new_status: str,
        changed_at: str,
        reason: str | None = None,
        changed_by: str | None = None,
    ) -> TicketStatusHistoryRecord:
        """Insert one ticket status-history record."""

        cursor = self._connection.execute(
            """
            INSERT INTO ticket_status_history (
                ticket_id,
                previous_status,
                new_status,
                reason,
                changed_by,
                changed_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                previous_status,
                new_status,
                reason,
                changed_by,
                changed_at,
            ),
        )
        row = self._connection.execute(
            f"""
            SELECT {_STATUS_HISTORY_COLUMNS}
            FROM ticket_status_history
            WHERE ticket_status_history_id = ?
            """,
            (int(cursor.lastrowid),),
        ).fetchone()
        if row is None:
            raise RuntimeError("Inserted ticket status history could not be reloaded.")
        return _status_history_from_row(row)

    def create_timeline_event(
        self,
        *,
        ticket_id: int,
        event_type: str,
        title: str,
        occurred_at: str,
        details: str | None = None,
        metadata_json: str | None = None,
        actor_label: str | None = None,
    ) -> TicketTimelineEventRecord:
        """Insert one ticket timeline event."""

        cursor = self._connection.execute(
            """
            INSERT INTO ticket_timeline_events (
                ticket_id,
                event_type,
                title,
                details,
                metadata_json,
                actor_label,
                occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                event_type,
                title,
                details,
                metadata_json,
                actor_label,
                occurred_at,
            ),
        )
        row = self._connection.execute(
            f"""
            SELECT {_TIMELINE_EVENT_COLUMNS}
            FROM ticket_timeline_events
            WHERE ticket_timeline_event_id = ?
            """,
            (int(cursor.lastrowid),),
        ).fetchone()
        if row is None:
            raise RuntimeError("Inserted ticket timeline event could not be reloaded.")
        return _timeline_event_from_row(row)

    def company_exists(self, company_id: int, *, active_only: bool = False) -> bool:
        """Return whether a company reference exists."""

        row = self._connection.execute(
            "SELECT 1 FROM companies WHERE company_id = ? AND (? = 0 OR is_active = 1)",
            (company_id, active_only),
        ).fetchone()
        return row is not None

    def get_contact_reference(self, contact_id: int, *, active_only: bool = False) -> tuple[bool, int | None]:
        """Return whether a contact exists and its optional company ID."""

        row = self._connection.execute(
            "SELECT company_id FROM contacts WHERE contact_id = ? AND (? = 0 OR is_active = 1)",
            (contact_id, active_only),
        ).fetchone()
        if row is None:
            return False, None
        company_id = (
            None if row["company_id"] is None else int(row["company_id"])
        )
        return True, company_id

    def ticket_category_exists(self, category_id: int) -> bool:
        """Return whether an active ticket-scoped category exists."""

        row = self._connection.execute(
            """
            SELECT 1
            FROM categories
            WHERE category_id = ? AND scope = 'TICKET' AND is_active = 1
            """,
            (category_id,),
        ).fetchone()
        return row is not None


def _list_status_history(connection, ticket_id):
    rows = connection.execute(
        f"SELECT {_STATUS_HISTORY_COLUMNS} FROM ticket_status_history "
        "WHERE ticket_id = ? ORDER BY changed_at, ticket_status_history_id",
        (ticket_id,),
    ).fetchall()
    return tuple(_status_history_from_row(row) for row in rows)


def _list_timeline_events(connection, ticket_id):
    rows = connection.execute(
        f"SELECT {_TIMELINE_EVENT_COLUMNS} FROM ticket_timeline_events "
        "WHERE ticket_id = ? ORDER BY occurred_at, ticket_timeline_event_id",
        (ticket_id,),
    ).fetchall()
    return tuple(_timeline_event_from_row(row) for row in rows)


def _list_notes(
    connection: sqlite3.Connection,
    ticket_id: int,
) -> tuple[TicketNoteRecord, ...]:
    rows = connection.execute(
        f"""
        SELECT {_NOTE_COLUMNS}
        FROM ticket_notes
        WHERE ticket_id = ?
        ORDER BY created_at, ticket_note_id
        """,
        (ticket_id,),
    ).fetchall()
    return tuple(_note_from_row(row) for row in rows)


def _get_ticket(
    connection: sqlite3.Connection,
    ticket_id: int,
) -> TicketRecord | None:
    row = connection.execute(
        f"""
        SELECT {_TICKET_COLUMNS}
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    ).fetchone()
    return _ticket_from_row(row) if row is not None else None


def _get_note(
    connection: sqlite3.Connection,
    ticket_note_id: int,
) -> TicketNoteRecord | None:
    row = connection.execute(
        f"""
        SELECT {_NOTE_COLUMNS}
        FROM ticket_notes
        WHERE ticket_note_id = ?
        """,
        (ticket_note_id,),
    ).fetchone()
    return _note_from_row(row) if row is not None else None


def _ticket_from_row(row: sqlite3.Row) -> TicketRecord:
    return TicketRecord(
        ticket_id=int(row["ticket_id"]),
        ticket_number=str(row["ticket_number"]),
        ticket_type=str(row["ticket_type"]),
        status=str(row["status"]),
        priority=str(row["priority"]),
        company_id=None if row["company_id"] is None else int(row["company_id"]),
        contact_id=None if row["contact_id"] is None else int(row["contact_id"]),
        category_id=None if row["category_id"] is None else int(row["category_id"]),
        subject=str(row["subject"]),
        description=row["description"],
        resolution=row["resolution"],
        assigned_to=row["assigned_to"],
        source=row["source"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        resolved_at=row["resolved_at"],
        closed_at=row["closed_at"],
    )


def _note_from_row(row: sqlite3.Row) -> TicketNoteRecord:
    return TicketNoteRecord(
        ticket_note_id=int(row["ticket_note_id"]),
        ticket_id=int(row["ticket_id"]),
        note_type=str(row["note_type"]),
        note_text=str(row["note_text"]),
        author_label=row["author_label"],
        source=row["source"],
        is_ai_generated=bool(row["is_ai_generated"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _status_history_from_row(row: sqlite3.Row) -> TicketStatusHistoryRecord:
    return TicketStatusHistoryRecord(
        ticket_status_history_id=int(row["ticket_status_history_id"]),
        ticket_id=int(row["ticket_id"]),
        previous_status=row["previous_status"],
        new_status=str(row["new_status"]),
        reason=row["reason"],
        changed_by=row["changed_by"],
        changed_at=str(row["changed_at"]),
    )


def _timeline_event_from_row(row: sqlite3.Row) -> TicketTimelineEventRecord:
    return TicketTimelineEventRecord(
        ticket_timeline_event_id=int(row["ticket_timeline_event_id"]),
        ticket_id=int(row["ticket_id"]),
        event_type=str(row["event_type"]),
        title=str(row["title"]),
        details=row["details"],
        metadata_json=row["metadata_json"],
        actor_label=row["actor_label"],
        occurred_at=str(row["occurred_at"]),
    )
