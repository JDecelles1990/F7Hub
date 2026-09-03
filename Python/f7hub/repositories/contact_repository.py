"""SQLite persistence for contacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class ContactRecord:
    """One contact row returned by the repository."""

    contact_id: int
    company_id: int | None
    display_name: str
    first_name: str | None
    last_name: str | None
    job_title: str | None
    email: str | None
    phone: str | None
    mobile_phone: str | None
    notes: str | None
    is_active: int
    created_at: str
    updated_at: str


_CONTACT_COLUMNS = """
    contact_id,
    company_id,
    display_name,
    first_name,
    last_name,
    job_title,
    email,
    phone,
    mobile_phone,
    notes,
    is_active,
    created_at,
    updated_at
"""


class ContactRepository:
    """Persist and retrieve contacts through configured SQLite connections."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def create_contact(
        self,
        *,
        display_name: str,
        created_at: str,
        updated_at: str,
        company_id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        job_title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        mobile_phone: str | None = None,
        notes: str | None = None,
        is_active: int = 1,
    ) -> ContactRecord:
        """Insert a contact and return its database-generated identity and values."""

        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO contacts (
                    company_id,
                    display_name,
                    first_name,
                    last_name,
                    job_title,
                    email,
                    phone,
                    mobile_phone,
                    notes,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    display_name,
                    first_name,
                    last_name,
                    job_title,
                    email,
                    phone,
                    mobile_phone,
                    notes,
                    is_active,
                    created_at,
                    updated_at,
                ),
            )
            contact = _get_contact(connection, int(cursor.lastrowid))

        if contact is None:
            raise RuntimeError("Inserted contact could not be reloaded.")
        return contact

    def get_contact(self, contact_id: int) -> ContactRecord | None:
        """Return a contact by internal ID, or ``None`` when it is absent."""

        with database_connection(self._database_path) as connection:
            return _get_contact(connection, contact_id)

    def list_contacts(
        self,
        *,
        active_only: bool = False,
    ) -> tuple[ContactRecord, ...]:
        """Return contacts in stable case-insensitive name and ID order."""

        if active_only:
            sql = f"""
                SELECT {_CONTACT_COLUMNS}
                FROM contacts
                WHERE is_active = 1
                ORDER BY display_name COLLATE NOCASE, contact_id
            """
        else:
            sql = f"""
                SELECT {_CONTACT_COLUMNS}
                FROM contacts
                ORDER BY display_name COLLATE NOCASE, contact_id
            """

        with database_connection(self._database_path) as connection:
            rows = connection.execute(sql).fetchall()
        return tuple(_contact_from_row(row) for row in rows)

    def list_contacts_for_company(
        self,
        company_id: int,
    ) -> tuple[ContactRecord, ...]:
        """Return one company's contacts in stable name and ID order."""

        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT {_CONTACT_COLUMNS}
                FROM contacts
                WHERE company_id = ?
                ORDER BY display_name COLLATE NOCASE, contact_id
                """,
                (company_id,),
            ).fetchall()
        return tuple(_contact_from_row(row) for row in rows)

    def update_contact(
        self,
        contact_id: int,
        *,
        company_id: int | None,
        display_name: str,
        first_name: str | None,
        last_name: str | None,
        job_title: str | None,
        email: str | None,
        phone: str | None,
        mobile_phone: str | None,
        notes: str | None,
        is_active: int,
        updated_at: str,
    ) -> ContactRecord | None:
        """Replace mutable contact fields and return the updated row, or ``None``."""

        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE contacts
                SET company_id = ?,
                    display_name = ?,
                    first_name = ?,
                    last_name = ?,
                    job_title = ?,
                    email = ?,
                    phone = ?,
                    mobile_phone = ?,
                    notes = ?,
                    is_active = ?,
                    updated_at = ?
                WHERE contact_id = ?
                """,
                (
                    company_id,
                    display_name,
                    first_name,
                    last_name,
                    job_title,
                    email,
                    phone,
                    mobile_phone,
                    notes,
                    is_active,
                    updated_at,
                    contact_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            return _get_contact(connection, contact_id)

    def set_contact_active(
        self,
        contact_id: int,
        *,
        is_active: int,
        updated_at: str,
    ) -> ContactRecord | None:
        """Set active state and return the updated contact, or ``None``."""

        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE contacts
                SET is_active = ?, updated_at = ?
                WHERE contact_id = ?
                """,
                (is_active, updated_at, contact_id),
            )
            if cursor.rowcount == 0:
                return None
            return _get_contact(connection, contact_id)


def _get_contact(
    connection: sqlite3.Connection,
    contact_id: int,
) -> ContactRecord | None:
    row = connection.execute(
        f"""
        SELECT {_CONTACT_COLUMNS}
        FROM contacts
        WHERE contact_id = ?
        """,
        (contact_id,),
    ).fetchone()
    return _contact_from_row(row) if row is not None else None


def _contact_from_row(row: sqlite3.Row) -> ContactRecord:
    return ContactRecord(
        contact_id=int(row["contact_id"]),
        company_id=None if row["company_id"] is None else int(row["company_id"]),
        display_name=str(row["display_name"]),
        first_name=row["first_name"],
        last_name=row["last_name"],
        job_title=row["job_title"],
        email=row["email"],
        phone=row["phone"],
        mobile_phone=row["mobile_phone"],
        notes=row["notes"],
        is_active=int(row["is_active"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )
