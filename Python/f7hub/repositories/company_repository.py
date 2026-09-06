"""SQLite persistence for companies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class CompanyRecord:
    """One company row returned by the repository."""

    company_id: int
    company_code: str | None
    name: str
    domain: str | None
    phone: str | None
    website_url: str | None
    address_line1: str | None
    address_line2: str | None
    city: str | None
    region: str | None
    postal_code: str | None
    country_code: str | None
    is_active: int
    created_at: str
    updated_at: str


_COMPANY_COLUMNS = """
    company_id,
    company_code,
    name,
    domain,
    phone,
    website_url,
    address_line1,
    address_line2,
    city,
    region,
    postal_code,
    country_code,
    is_active,
    created_at,
    updated_at
"""


class CompanyRepository:
    """Persist and retrieve companies through configured SQLite connections."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def create_company(
        self,
        *,
        name: str,
        created_at: str,
        updated_at: str,
        company_code: str | None = None,
        domain: str | None = None,
        phone: str | None = None,
        website_url: str | None = None,
        address_line1: str | None = None,
        address_line2: str | None = None,
        city: str | None = None,
        region: str | None = None,
        postal_code: str | None = None,
        country_code: str | None = None,
        is_active: int = 1,
    ) -> CompanyRecord:
        """Insert a company and return its database-generated identity and values."""

        with database_connection(self._database_path) as connection:
            # Return a reloadable record or roll back the insertion as one unit.
            connection.execute("BEGIN")
            cursor = connection.execute(
                """
                INSERT INTO companies (
                    company_code,
                    name,
                    domain,
                    phone,
                    website_url,
                    address_line1,
                    address_line2,
                    city,
                    region,
                    postal_code,
                    country_code,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_code,
                    name,
                    domain,
                    phone,
                    website_url,
                    address_line1,
                    address_line2,
                    city,
                    region,
                    postal_code,
                    country_code,
                    is_active,
                    created_at,
                    updated_at,
                ),
            )
            company = _get_company(connection, int(cursor.lastrowid))
            if company is None:
                raise RuntimeError("Inserted company could not be reloaded.")
            connection.commit()
        return company

    def get_company(self, company_id: int, *, connection: sqlite3.Connection | None = None) -> CompanyRecord | None:
        """Return a company by internal ID, or ``None`` when it is absent."""

        if connection is not None:
            return _get_company(connection, company_id)
        with database_connection(self._database_path) as connection:
            return _get_company(connection, company_id)

    def get_company_by_code(self, company_code: str) -> CompanyRecord | None:
        """Return a company by its case-insensitive code, or ``None``."""

        with database_connection(self._database_path) as connection:
            row = connection.execute(
                f"""
                SELECT {_COMPANY_COLUMNS}
                FROM companies
                WHERE company_code = ?
                """,
                (company_code,),
            ).fetchone()
        return _company_from_row(row) if row is not None else None

    def list_companies(
        self,
        *,
        active_only: bool = False,
    ) -> tuple[CompanyRecord, ...]:
        """Return companies in stable case-insensitive name and ID order."""

        if active_only:
            sql = f"""
                SELECT {_COMPANY_COLUMNS}
                FROM companies
                WHERE is_active = 1
                ORDER BY name COLLATE NOCASE, company_id
            """
        else:
            sql = f"""
                SELECT {_COMPANY_COLUMNS}
                FROM companies
                ORDER BY name COLLATE NOCASE, company_id
            """

        with database_connection(self._database_path) as connection:
            rows = connection.execute(sql).fetchall()
        return tuple(_company_from_row(row) for row in rows)

    def update_company(
        self,
        company_id: int,
        *,
        company_code: str | None,
        name: str,
        domain: str | None,
        phone: str | None,
        website_url: str | None,
        address_line1: str | None,
        address_line2: str | None,
        city: str | None,
        region: str | None,
        postal_code: str | None,
        country_code: str | None,
        is_active: int,
        updated_at: str,
    ) -> CompanyRecord | None:
        """Replace mutable company fields and return the updated row, or ``None``."""

        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE companies
                SET company_code = ?,
                    name = ?,
                    domain = ?,
                    phone = ?,
                    website_url = ?,
                    address_line1 = ?,
                    address_line2 = ?,
                    city = ?,
                    region = ?,
                    postal_code = ?,
                    country_code = ?,
                    is_active = ?,
                    updated_at = ?
                WHERE company_id = ?
                """,
                (
                    company_code,
                    name,
                    domain,
                    phone,
                    website_url,
                    address_line1,
                    address_line2,
                    city,
                    region,
                    postal_code,
                    country_code,
                    is_active,
                    updated_at,
                    company_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            return _get_company(connection, company_id)

    def set_company_active(
        self,
        company_id: int,
        *,
        is_active: int,
        updated_at: str,
    ) -> CompanyRecord | None:
        """Set active state and return the updated company, or ``None``."""

        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE companies
                SET is_active = ?, updated_at = ?
                WHERE company_id = ?
                """,
                (is_active, updated_at, company_id),
            )
            if cursor.rowcount == 0:
                return None
            return _get_company(connection, company_id)


def _get_company(
    connection: sqlite3.Connection,
    company_id: int,
) -> CompanyRecord | None:
    row = connection.execute(
        f"""
        SELECT {_COMPANY_COLUMNS}
        FROM companies
        WHERE company_id = ?
        """,
        (company_id,),
    ).fetchone()
    return _company_from_row(row) if row is not None else None


def _company_from_row(row: sqlite3.Row) -> CompanyRecord:
    return CompanyRecord(
        company_id=int(row["company_id"]),
        company_code=row["company_code"],
        name=str(row["name"]),
        domain=row["domain"],
        phone=row["phone"],
        website_url=row["website_url"],
        address_line1=row["address_line1"],
        address_line2=row["address_line2"],
        city=row["city"],
        region=row["region"],
        postal_code=row["postal_code"],
        country_code=row["country_code"],
        is_active=int(row["is_active"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )
