"""Coherent USER override state and transaction-level optimistic concurrency."""

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from typing import Mapping

from f7hub.domain.settings import validate_revision, validate_setting_key
from f7hub.infrastructure.database import DatabaseError, database_connection


class SettingsPersistenceError(RuntimeError):
    """Storage failure safe for display; raw SQLite messages are not exposed."""


class SettingsContentionError(SettingsPersistenceError):
    """SQLite busy/locked deadline, distinct from a stale revision or other failure."""


def _storage_failure(error: Exception, message: str) -> SettingsPersistenceError:
    code = getattr(error, "sqlite_errorcode", 0)
    if isinstance(error, sqlite3.Error) and code & 0xFF in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
        return SettingsContentionError("Settings storage is busy. Refresh before an explicit retry.")
    return SettingsPersistenceError(message)


class SettingsConflictError(RuntimeError):
    """Expected revision no longer describes this database's Settings state."""


@dataclass(frozen=True)
class StoredSetting:
    key: str = field(repr=False)
    value_type: object = field(repr=False)
    value_text: object = field(repr=False)


@dataclass(frozen=True)
class SettingsState:
    revision: int
    overrides: tuple[StoredSetting, ...] = field(repr=False)


@dataclass(frozen=True)
class SettingsWriteResult:
    state: SettingsState
    changed_keys: tuple[str, ...]


def _read_state(connection: sqlite3.Connection) -> SettingsState:
    rows = connection.execute("SELECT singleton_id, revision FROM settings_state").fetchall()
    if len(rows) != 1 or rows[0]["singleton_id"] != 1:
        raise SettingsPersistenceError("Settings revision is unavailable.")
    revision = rows[0]["revision"]
    validate_revision(revision)
    overrides = tuple(StoredSetting(row["setting_key"], row["value_type"], row["value_text"])
                      for row in connection.execute(
                          "SELECT setting_key, value_type, value_text FROM settings_user_overrides ORDER BY setting_key"))
    return SettingsState(revision, overrides)


class SettingsRepository:
    """Persistence only. All supported writers must use this revision protocol.

    Reads use an explicit read transaction; writes reserve SQLite's writer lock
    before comparing revision, including absent-key inserts and reset deletes.
    No default, definition, capability or consent is stored by this repository.
    """

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def load_state(self) -> SettingsState:
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                connection.execute("BEGIN")
                state = _read_state(connection)
                connection.commit()
            return state
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, UnicodeError) as error:
            raise _storage_failure(error, "Could not load Settings.") from None

    def apply(self, *, changes: Mapping[str, bool], resets: tuple[str, ...],
              expected_revision: int) -> SettingsWriteResult:
        validate_revision(expected_revision)
        # Structural validation only; definition admission/editability is service-owned.
        changes = dict(changes)
        for key, value in changes.items():
            validate_setting_key(key)
            if type(value) is not bool:
                raise ValueError("Persisted Boolean input is invalid.")
        for key in resets:
            validate_setting_key(key)
        if set(changes).intersection(resets):
            raise ValueError("A setting cannot be changed and reset in one group.")
        try:
            if not self._database_path.is_file():
                raise SettingsPersistenceError("Settings storage is unavailable.")
            with database_connection(self._database_path) as connection:
                connection.execute("BEGIN IMMEDIATE")
                before = _read_state(connection)
                if before.revision != expected_revision:
                    raise SettingsConflictError("Settings changed. Reload before applying this draft.")
                stored = {entry.key: entry for entry in before.overrides}
                changed: list[str] = []
                for key, value in sorted(changes.items()):
                    desired = StoredSetting(key, "BOOLEAN", "true" if value else "false")
                    if stored.get(key) == desired:
                        continue
                    connection.execute(
                        "INSERT INTO settings_user_overrides (setting_key, value_type, value_text) VALUES (?, ?, ?) "
                        "ON CONFLICT(setting_key) DO UPDATE SET value_type=excluded.value_type, value_text=excluded.value_text",
                        (key, desired.value_type, desired.value_text))
                    changed.append(key)
                for key in sorted(set(resets)):
                    if key in stored:
                        connection.execute("DELETE FROM settings_user_overrides WHERE setting_key = ?", (key,))
                        changed.append(key)
                if changed:
                    connection.execute("UPDATE settings_state SET revision = revision + 1 WHERE singleton_id = 1")
                state = _read_state(connection)
                connection.commit()
            return SettingsWriteResult(state, tuple(sorted(changed)))
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, UnicodeError) as error:
            raise _storage_failure(error, "Could not save Settings. No changes were committed.") from None
