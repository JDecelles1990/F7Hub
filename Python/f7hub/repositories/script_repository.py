"""Read the PowerShell script registry without changing it."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


class ScriptRepository:
    """Provide scoped registry reads through configured SQLite connections."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def list_scripts(self, *, include_disabled: bool = False) -> tuple[ScriptRecord, ...]:
        """List enabled scripts; disabled inspection is explicit and internal only."""
        if not isinstance(include_disabled, bool):
            raise ValueError("include_disabled must be a boolean.")
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                "SELECT " + _COLUMNS + _FROM
                + " AND (? = 1 OR s.is_enabled = 1)"
                + " ORDER BY s.name COLLATE NOCASE, s.script_code COLLATE NOCASE, s.script_id",
                (int(include_disabled),),
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
