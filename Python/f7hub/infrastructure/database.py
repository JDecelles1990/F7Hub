"""Controlled SQLite connection, integrity, and bootstrap operations."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3
from typing import Iterator

from f7hub.infrastructure.migrations import (
    MigrationRunResult,
    discover_migrations,
    initialize_migration_table,
    run_migrations,
)


DEFAULT_BUSY_TIMEOUT_MS = 5_000


class DatabaseError(RuntimeError):
    """Base class for F7Hub database-infrastructure failures."""


class DatabaseConfigurationError(DatabaseError):
    """Raised when a database connection cannot meet required settings."""


class DatabaseIntegrityError(DatabaseError):
    """Raised when SQLite integrity validation reports a problem."""


@dataclass(frozen=True)
class ForeignKeyViolation:
    """One row reported by ``PRAGMA foreign_key_check``."""

    table: str
    row_id: int | None
    parent_table: str
    foreign_key_index: int


@dataclass(frozen=True)
class BootstrapResult:
    """Summary of one successful database bootstrap."""

    migration_result: MigrationRunResult
    integrity_results: tuple[str, ...]
    foreign_key_violations: tuple[ForeignKeyViolation, ...]


def open_database(
    database_path: str | Path,
    *,
    busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
) -> sqlite3.Connection:
    """Create or open a configured SQLite connection.

    File-backed database parent directories are created when needed. The caller
    owns the returned connection and must close it.
    """

    if isinstance(busy_timeout_ms, bool) or not isinstance(busy_timeout_ms, int):
        raise DatabaseConfigurationError("busy_timeout_ms must be an integer.")
    if busy_timeout_ms < 0:
        raise DatabaseConfigurationError("busy_timeout_ms must not be negative.")

    raw_database_path = os.fspath(database_path)
    if not raw_database_path.strip():
        raise DatabaseConfigurationError("database_path must not be empty.")

    connection_target = raw_database_path
    if raw_database_path != ":memory:":
        expanded_database_path = Path(raw_database_path).expanduser()
        expanded_database_path.parent.mkdir(parents=True, exist_ok=True)
        connection_target = os.fspath(expanded_database_path)

    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(
            connection_target,
            timeout=busy_timeout_ms / 1_000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {busy_timeout_ms:d}")
        _verify_connection_configuration(connection, busy_timeout_ms)
        return connection
    except Exception:
        if connection is not None:
            connection.close()
        raise


@contextmanager
def database_connection(
    database_path: str | Path,
    *,
    busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
) -> Iterator[sqlite3.Connection]:
    """Yield a configured connection and always close it cleanly."""

    connection = open_database(database_path, busy_timeout_ms=busy_timeout_ms)
    try:
        yield connection
    finally:
        try:
            if connection.in_transaction:
                connection.rollback()
        finally:
            connection.close()


def run_integrity_check(connection: sqlite3.Connection) -> tuple[str, ...]:
    """Return every result emitted by ``PRAGMA integrity_check``."""

    rows = connection.execute("PRAGMA integrity_check").fetchall()
    return tuple(str(row[0]) for row in rows)


def run_foreign_key_check(
    connection: sqlite3.Connection,
) -> tuple[ForeignKeyViolation, ...]:
    """Return all current foreign-key violations."""

    rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    return tuple(
        ForeignKeyViolation(
            table=str(row[0]),
            row_id=None if row[1] is None else int(row[1]),
            parent_table=str(row[2]),
            foreign_key_index=int(row[3]),
        )
        for row in rows
    )


def validate_database_integrity(
    connection: sqlite3.Connection,
) -> tuple[tuple[str, ...], tuple[ForeignKeyViolation, ...]]:
    """Run required integrity checks and fail visibly on any problem."""

    integrity_results = run_integrity_check(connection)
    foreign_key_violations = run_foreign_key_check(connection)

    if integrity_results != ("ok",):
        raise DatabaseIntegrityError("PRAGMA integrity_check did not return ok.")
    if foreign_key_violations:
        raise DatabaseIntegrityError(
            "PRAGMA foreign_key_check reported one or more violations."
        )

    return integrity_results, foreign_key_violations


def bootstrap_database(
    database_path: str | Path,
    migrations_dir: str | Path,
    *,
    busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
) -> BootstrapResult:
    """Create/open, migrate, validate, and close an F7Hub SQLite database."""

    migrations = discover_migrations(migrations_dir)
    with database_connection(
        database_path,
        busy_timeout_ms=busy_timeout_ms,
    ) as connection:
        initialize_migration_table(connection)
        migration_result = run_migrations(connection, migrations)
        integrity_results, foreign_key_violations = validate_database_integrity(
            connection
        )

    return BootstrapResult(
        migration_result=migration_result,
        integrity_results=integrity_results,
        foreign_key_violations=foreign_key_violations,
    )


def _verify_connection_configuration(
    connection: sqlite3.Connection,
    expected_busy_timeout_ms: int,
) -> None:
    foreign_keys_enabled = int(
        connection.execute("PRAGMA foreign_keys").fetchone()[0]
    )
    actual_busy_timeout_ms = int(
        connection.execute("PRAGMA busy_timeout").fetchone()[0]
    )
    if foreign_keys_enabled != 1:
        raise DatabaseConfigurationError(
            "SQLite foreign-key enforcement could not be enabled."
        )
    if actual_busy_timeout_ms != expected_busy_timeout_ms:
        raise DatabaseConfigurationError(
            "SQLite busy timeout does not match the requested value."
        )
