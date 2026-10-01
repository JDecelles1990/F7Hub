"""Scoped PowerShell registry reads and bounded metadata writes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class ScriptRecord:
    script_id: int
    category_id: int | None
    category_name: str | None
    script_code: str
    name: str
    description: str | None
    relative_path: str
    script_type: str
    runtime: str
    risk_level: str
    privilege_level: str
    version: str | None
    checksum_sha256: str | None
    timeout_seconds: int
    requires_structured_output: int
    is_enabled: int
    created_at: str
    updated_at: str


_COLUMNS = """
    s.script_id, s.category_id, c.name AS category_name,
    s.script_code, s.name, s.description, s.relative_path,
    s.script_type, s.runtime, s.risk_level, s.privilege_level,
    s.version, s.checksum_sha256, s.timeout_seconds,
    s.requires_structured_output, s.is_enabled, s.created_at, s.updated_at
"""

_FROM = """
    FROM scripts AS s
    LEFT JOIN categories AS c
      ON c.category_id = s.category_id AND c.scope = 'SCRIPT'
    WHERE (s.category_id IS NULL OR c.category_id IS NOT NULL)
"""


class ScriptRegistrationConflictError(RuntimeError):
    """A code or normalized path is already registered."""


class ScriptStateConflictError(RuntimeError):
    """The previously read registration is no longer current or in scope."""


def _get_registered_script(connection: sqlite3.Connection, script_id: int) -> ScriptRecord | None:
    row = connection.execute(
        "SELECT " + _COLUMNS + _FROM + " AND s.script_id = ?", (script_id,),
    ).fetchone()
    return None if row is None else ScriptRecord(**dict(row))


class ScriptRepository:
    """Use configured connections and retain the SCRIPT category boundary."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def list_scripts(
        self, *, include_disabled: bool = False, text_query: str | None = None,
    ) -> tuple[ScriptRecord, ...]:
        """List scoped metadata, optionally matching a literal text substring."""
        if not isinstance(include_disabled, bool):
            raise ValueError("include_disabled must be a boolean.")
        if text_query is not None:
            if not isinstance(text_query, str) or "\x00" in text_query:
                raise ValueError("text_query must be text without NUL characters or None.")
            text_query = text_query.strip() or None
        predicate = ""
        parameters: tuple[object, ...] = (int(include_disabled),)
        if text_query is not None:
            literal = text_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{literal}%"
            predicate = (
                " AND (s.name LIKE ? ESCAPE '\\' OR s.script_code LIKE ? ESCAPE '\\'"
                " OR s.description LIKE ? ESCAPE '\\')"
            )
            parameters += (pattern, pattern, pattern)
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                "SELECT " + _COLUMNS + _FROM
                + " AND (? = 1 OR s.is_enabled = 1)"
                + predicate
                + " ORDER BY s.name COLLATE NOCASE, s.script_code COLLATE NOCASE, s.script_id",
                parameters,
            ).fetchall()
        return tuple(ScriptRecord(**dict(row)) for row in rows)

    def get_script(self, script_code: str) -> ScriptRecord | None:
        """Return one enabled script by exact case-insensitive code, or None."""
        if not isinstance(script_code, str) or not script_code.strip():
            raise ValueError("script_code must be nonempty text.")
        with database_connection(self._database_path) as connection:
            row = connection.execute(
                "SELECT " + _COLUMNS + _FROM
                + " AND s.is_enabled = 1 AND s.script_code = ?",
                (script_code,),
            ).fetchone()
        return None if row is None else ScriptRecord(**dict(row))

    def register_script(
        self, *, script_code: str, name: str, relative_path: str,
        script_type: str, risk_level: str, privilege_level: str,
        description: str | None, version: str | None, timestamp: str,
    ) -> ScriptRecord:
        """Insert default-disabled metadata and reload before committing."""
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            duplicate = connection.execute(
                "SELECT 1 FROM scripts WHERE script_code = ? OR "
                "replace(relative_path, char(92), '/') = ? COLLATE NOCASE",
                (script_code, relative_path),
            ).fetchone()
            if duplicate is not None:
                raise ScriptRegistrationConflictError()
            cursor = connection.execute(
                "INSERT INTO scripts (script_code, name, relative_path, script_type, "
                "risk_level, privilege_level, description, version, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (script_code, name, relative_path, script_type, risk_level,
                 privilege_level, description, version, timestamp, timestamp),
            )
            record = _get_registered_script(connection, int(cursor.lastrowid))
            if record is None:
                raise RuntimeError("Inserted registration could not be reloaded.")
            connection.commit()
            return record

    def set_script_enabled(
        self, script_id: int, *, enabled: bool, expected_updated_at: str,
        expected_relative_path: str, updated_at: str,
    ) -> ScriptRecord:
        """Change only visibility and its token, or fail without committing."""
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            current = _get_registered_script(connection, script_id)
            if (current is None or current.updated_at != expected_updated_at
                    or current.relative_path != expected_relative_path):
                raise ScriptStateConflictError()
            if current.is_enabled == int(enabled):
                return current
            cursor = connection.execute(
                "UPDATE scripts SET is_enabled = ?, updated_at = ? "
                "WHERE script_id = ? AND updated_at = ? AND relative_path = ?",
                (int(enabled), updated_at, script_id, expected_updated_at, expected_relative_path),
            )
            if cursor.rowcount != 1:
                raise ScriptStateConflictError()
            record = _get_registered_script(connection, script_id)
            if record is None:
                raise RuntimeError("Updated registration could not be reloaded.")
            connection.commit()
            return record
