"""Coherent USER override state and transaction-level optimistic concurrency."""

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from typing import Mapping

from f7hub.domain.settings import validate_revision, validate_setting_key
from f7hub.infrastructure.database import DatabaseError, database_connection
from f7hub.domain.clipboard import (ClipboardConsentSnapshot, CONSENT_DISCLOSURE, CONSENT_POLICY,
                                   REQUEST_PROFILE, validate_utc_timestamp)
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED


class SettingsPersistenceError(RuntimeError):
    """Storage failure safe for display; raw SQLite messages are not exposed."""


class SettingsContentionError(SettingsPersistenceError):
    """SQLite busy/locked deadline, distinct from a stale revision or other failure."""


class SettingsUncertainError(SettingsPersistenceError):
    """A save may have committed. Reload/reconcile; never automatically replay."""

    def __init__(self, action_id: str | None = None):
        super().__init__("Settings save outcome is uncertain. Reload before any new explicit save.")
        self.action_id = action_id


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


def _eligible_consent(connection, database_scope, profile_scope, state=None):
    """Bounded SQL/read validation shared by preparation and final writer fence."""
    state = state if state is not None else _read_state(connection)
    rows = connection.execute("SELECT * FROM clipboard_history_consent").fetchall()
    enabled = any(x.key == WORKFLOW_ENABLED and x.value_type == "BOOLEAN" and x.value_text == "true"
                  for x in state.overrides)
    if not enabled or len(rows) != 1:
        return None
    row = rows[0]
    if (row['singleton_id'] != 1 or row['state'] != 'GRANTED' or row['revoked_at'] is not None
            or row['database_scope'] != database_scope or row['profile_scope'] != profile_scope
            or row['purpose'] != REQUEST_PROFILE or row['disclosure_version'] != CONSENT_DISCLOSURE
            or row['policy_version'] != CONSENT_POLICY):
        return None
    for key in ('grant_settings_revision', 'transition_settings_revision'):
        if type(row[key]) is not int or not 0 <= row[key] <= state.revision:
            return None
    if row['transition_settings_revision'] != row['grant_settings_revision']:
        return None
    if type(row['consent_epoch']) is not int or not 1 <= row['consent_epoch'] < 2**63 - 1:
        return None  # An exhausted epoch cannot safely support another revoke.
    validate_utc_timestamp(row['granted_at'])
    if type(row['last_action_id']) is not str or len(row['last_action_id']) != 32 or any(c not in '0123456789abcdef' for c in row['last_action_id']):
        return None
    return ClipboardConsentSnapshot(row['database_instance_id'], database_scope, profile_scope,
                                    row['consent_epoch'], state.revision)


class SettingsRepository:
    """Persistence only. All supported writers must use this revision protocol.

    Reads use an explicit read transaction; writes reserve SQLite's writer lock
    before comparing revision, including absent-key inserts and reset deletes.
    Definitions/defaults stay in Python. Explicit Clipboard owner transactions
    persist content-free consent; the general Apply API can only revoke it.
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
        return self._apply(changes=changes, resets=resets, expected_revision=expected_revision)

    def _load_clipboard_setup(self, database_scope, profile_scope):
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                connection.execute('BEGIN')
                state = _read_state(connection)
                row = connection.execute('SELECT consent_epoch FROM clipboard_history_consent WHERE singleton_id=1').fetchone()
                epoch = row[0] if row else None
                if epoch is not None and (type(epoch) is not int or not 1 <= epoch <= 2**63-1):
                    raise SettingsPersistenceError('Clipboard consent is unavailable.')
                consent = _eligible_consent(connection, database_scope, profile_scope, state)
                return state, epoch, consent
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, UnicodeError):
            raise SettingsPersistenceError('Clipboard consent is unavailable.') from None

    def _apply_clipboard_setup(self, *, changes, expected_revision, expected_epoch,
                               database_scope, profile_scope):
        return self._apply(changes=changes, resets=(), expected_revision=expected_revision,
                           setup=(database_scope, profile_scope, expected_epoch))

    def _apply(self, *, changes, resets, expected_revision, setup=None):
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
        commit_attempted = False
        committed = False
        action_id = uuid4().hex
        try:
            if not self._database_path.is_file():
                raise SettingsPersistenceError("Settings storage is unavailable.")
            with database_connection(self._database_path) as connection:
                connection.execute("BEGIN IMMEDIATE")
                before = _read_state(connection)
                if before.revision != expected_revision:
                    raise SettingsConflictError("Settings changed. Reload before applying this draft.")
                evidence = connection.execute('SELECT * FROM clipboard_history_consent WHERE singleton_id=1').fetchone()
                if setup is not None and (evidence['consent_epoch'] if evidence else None) != setup[2]:
                    raise SettingsConflictError('Clipboard consent changed. Reload before applying this draft.')
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
                now = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                if setup is not None:
                    scope, profile, _ = setup
                    instance = evidence['database_instance_id'] if evidence else uuid4().hex
                    epoch = evidence['consent_epoch'] + 1 if evidence else 1
                    ClipboardConsentSnapshot(instance, scope, profile, epoch, state.revision)
                    # SQL constraints enforce overflow/shape; the owner supplies versions.
                    connection.execute('''INSERT INTO clipboard_history_consent VALUES
                        (1, ?, ?, ?, ?, ?, ?, ?, 'GRANTED', ?, ?, ?, ?, NULL)
                        ON CONFLICT(singleton_id) DO UPDATE SET
                        database_scope=excluded.database_scope, profile_scope=excluded.profile_scope,
                        purpose=excluded.purpose, disclosure_version=excluded.disclosure_version,
                        policy_version=excluded.policy_version, consent_epoch=excluded.consent_epoch,
                        state='GRANTED', grant_settings_revision=excluded.grant_settings_revision,
                        transition_settings_revision=excluded.transition_settings_revision,
                        last_action_id=excluded.last_action_id, granted_at=excluded.granted_at, revoked_at=NULL''',
                        (instance, scope, profile, REQUEST_PROFILE, CONSENT_DISCLOSURE, CONSENT_POLICY,
                         epoch, state.revision, state.revision, action_id, now))
                elif WORKFLOW_ENABLED in changed and evidence is not None:
                    connection.execute('''UPDATE clipboard_history_consent SET state='REVOKED',
                        consent_epoch=consent_epoch+1, transition_settings_revision=?,
                        last_action_id=?, revoked_at=? WHERE singleton_id=1''', (state.revision, action_id, now))
                result = SettingsWriteResult(state, tuple(sorted(changed)))
                commit_attempted = True
                connection.commit()
                committed = True
            return result
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, UnicodeError) as error:
            if committed:
                return result  # Commit remains authoritative after close failure.
            if commit_attempted:
                raise SettingsUncertainError(action_id if setup is not None else None) from None
            raise _storage_failure(error, "Could not save Settings. Reload to verify saved state.") from None
