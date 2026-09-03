"""Discover, validate, and atomically apply SQLite migrations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import sqlite3
import time
from typing import Iterator, Sequence


MIGRATION_FILENAME_PATTERN = re.compile(
    r"^(?P<version>\d{4})_(?P<name>[a-z0-9]+(?:_[a-z0-9]+)*)\.sql$"
)

SCHEMA_MIGRATIONS_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    execution_ms INTEGER NOT NULL CHECK (execution_ms >= 0)
)
"""


class MigrationError(RuntimeError):
    """Base class for migration failures."""


class MigrationDiscoveryError(MigrationError):
    """Raised when the migration source directory cannot be read."""


class InvalidMigrationFilenameError(MigrationDiscoveryError):
    """Raised when a migration filename does not follow the canonical format."""


class DuplicateMigrationVersionError(MigrationDiscoveryError):
    """Raised when multiple files declare the same migration version."""


class MigrationHistoryError(MigrationError):
    """Raised when recorded migration history does not match migration files."""


class MigrationChecksumError(MigrationHistoryError):
    """Raised when an applied migration's SHA-256 checksum has changed."""


class MigrationApplicationError(MigrationError):
    """Raised when a pending migration cannot be applied atomically."""


class MigrationRollbackError(MigrationApplicationError):
    """Raised when migration failure is followed by rollback failure."""


@dataclass(frozen=True)
class Migration:
    """A validated migration loaded from disk."""

    version: int
    name: str
    path: Path
    checksum_sha256: str
    sql: str


@dataclass(frozen=True)
class AppliedMigration:
    """An immutable migration-history record."""

    version: int
    name: str
    checksum_sha256: str
    applied_at: str
    execution_ms: int


@dataclass(frozen=True)
class MigrationRunResult:
    """Summary of one migration-runner invocation."""

    discovered_versions: tuple[int, ...]
    applied_versions: tuple[int, ...]


def discover_migrations(migrations_dir: str | Path) -> tuple[Migration, ...]:
    """Load canonical migration files and return them in numeric order.

    Every regular file in the migration directory is required to follow
    ``NNNN_description.sql``. Subdirectories are ignored.
    """

    directory_path = Path(migrations_dir)
    if not directory_path.exists():
        raise MigrationDiscoveryError(
            f"Migration directory does not exist: {directory_path}"
        )
    if not directory_path.is_dir():
        raise MigrationDiscoveryError(
            f"Migration path is not a directory: {directory_path}"
        )

    migrations_by_version: dict[int, Migration] = {}
    for migration_path in sorted(directory_path.iterdir(), key=lambda path: path.name):
        if not migration_path.is_file():
            continue

        filename_match = MIGRATION_FILENAME_PATTERN.fullmatch(migration_path.name)
        if filename_match is None:
            raise InvalidMigrationFilenameError(
                "Migration filename must use NNNN_description.sql with a "
                f"lowercase snake_case description: {migration_path.name}"
            )

        version = int(filename_match.group("version"))
        if version < 1:
            raise InvalidMigrationFilenameError(
                f"Migration version must be at least 0001: {migration_path.name}"
            )
        if version in migrations_by_version:
            other_path = migrations_by_version[version].path
            raise DuplicateMigrationVersionError(
                f"Duplicate migration version {version:04d}: "
                f"{other_path.name}, {migration_path.name}"
            )

        try:
            migration_bytes = migration_path.read_bytes()
            migration_sql = migration_bytes.decode("utf-8-sig")
        except (OSError, UnicodeError) as error:
            raise MigrationDiscoveryError(
                f"Could not read UTF-8 migration file: {migration_path}"
            ) from error

        migrations_by_version[version] = Migration(
            version=version,
            name=filename_match.group("name"),
            path=migration_path,
            checksum_sha256=hashlib.sha256(migration_bytes).hexdigest(),
            sql=migration_sql,
        )

    return tuple(
        migrations_by_version[version]
        for version in sorted(migrations_by_version)
    )


def initialize_migration_table(connection: sqlite3.Connection) -> None:
    """Create the canonical migration-history table when it is absent."""

    connection.execute(SCHEMA_MIGRATIONS_DDL)


def list_applied_migrations(
    connection: sqlite3.Connection,
) -> tuple[AppliedMigration, ...]:
    """Return applied migrations ordered by numeric version."""

    rows = connection.execute(
        """
        SELECT version, name, checksum_sha256, applied_at, execution_ms
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()
    return tuple(
        AppliedMigration(
            version=int(row[0]),
            name=str(row[1]),
            checksum_sha256=str(row[2]),
            applied_at=str(row[3]),
            execution_ms=int(row[4]),
        )
        for row in rows
    )


def run_migrations(
    connection: sqlite3.Connection,
    migrations: Sequence[Migration],
) -> MigrationRunResult:
    """Validate migration history and apply pending migrations in order."""

    applied_migrations = list_applied_migrations(connection)
    _validate_migration_history(migrations, applied_migrations)

    applied_versions = {migration.version for migration in applied_migrations}
    if applied_versions:
        highest_applied_version = max(applied_versions)
        out_of_order_versions = tuple(
            migration.version
            for migration in migrations
            if migration.version < highest_applied_version
            and migration.version not in applied_versions
        )
        if out_of_order_versions:
            formatted_versions = ", ".join(
                f"{version:04d}" for version in out_of_order_versions
            )
            raise MigrationHistoryError(
                "Pending migration versions precede the current migration history: "
                f"{formatted_versions}."
            )

    newly_applied_versions: list[int] = []
    for migration in migrations:
        if migration.version in applied_versions:
            continue
        _apply_migration(connection, migration)
        newly_applied_versions.append(migration.version)

    return MigrationRunResult(
        discovered_versions=tuple(migration.version for migration in migrations),
        applied_versions=tuple(newly_applied_versions),
    )


def _validate_migration_history(
    migrations: Sequence[Migration],
    applied_migrations: Sequence[AppliedMigration],
) -> None:
    migrations_by_version = {migration.version: migration for migration in migrations}

    for applied_migration in applied_migrations:
        migration = migrations_by_version.get(applied_migration.version)
        if migration is None:
            raise MigrationHistoryError(
                "Applied migration file is missing for version "
                f"{applied_migration.version:04d}."
            )
        if migration.name != applied_migration.name:
            raise MigrationHistoryError(
                "Applied migration name changed for version "
                f"{applied_migration.version:04d}."
            )
        if migration.checksum_sha256 != applied_migration.checksum_sha256:
            raise MigrationChecksumError(
                "Applied migration checksum changed for version "
                f"{applied_migration.version:04d}."
            )


def _apply_migration(connection: sqlite3.Connection, migration: Migration) -> None:
    if connection.in_transaction:
        raise MigrationApplicationError(
            "Cannot apply a migration while another transaction is active."
        )

    started_ns = time.perf_counter_ns()
    try:
        connection.execute("BEGIN IMMEDIATE")
        try:
            connection.set_authorizer(_migration_authorizer)
            for statement in _iter_sql_statements(migration.sql):
                connection.execute(statement)
        finally:
            connection.set_authorizer(None)

        execution_ms = max(0, (time.perf_counter_ns() - started_ns) // 1_000_000)
        connection.execute(
            """
            INSERT INTO schema_migrations (
                version,
                name,
                checksum_sha256,
                applied_at,
                execution_ms
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                migration.version,
                migration.name,
                migration.checksum_sha256,
                _utc_now_text(),
                execution_ms,
            ),
        )
        connection.commit()
    except Exception as error:
        try:
            if connection.in_transaction:
                connection.rollback()
        except sqlite3.Error as rollback_error:
            raise MigrationRollbackError(
                f"Migration {migration.path.name} failed and rollback also failed."
            ) from rollback_error
        raise MigrationApplicationError(
            f"Migration {migration.path.name} failed and was rolled back."
        ) from error


def _migration_authorizer(
    action_code: int,
    _argument_one: str | None,
    _argument_two: str | None,
    _database_name: str | None,
    _trigger_or_view: str | None,
) -> int:
    blocked_action_codes = {
        sqlite3.SQLITE_TRANSACTION,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
    }
    savepoint_action_code = getattr(sqlite3, "SQLITE_SAVEPOINT", None)
    if savepoint_action_code is not None:
        blocked_action_codes.add(savepoint_action_code)

    if action_code in blocked_action_codes:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _iter_sql_statements(sql_script: str) -> Iterator[str]:
    """Yield complete SQLite statements without using ``executescript``.

    ``executescript`` can implicitly commit a pending transaction. Splitting on
    SQLite-recognized statement boundaries lets the caller retain one explicit
    transaction around the migration and its history record.
    """

    statement_characters: list[str] = []
    for character in sql_script:
        statement_characters.append(character)
        if character != ";":
            continue

        candidate = "".join(statement_characters)
        if sqlite3.complete_statement(candidate):
            if candidate.strip():
                yield candidate
            statement_characters.clear()

    trailing_statement = "".join(statement_characters)
    if trailing_statement.strip():
        yield trailing_statement


def _utc_now_text() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
