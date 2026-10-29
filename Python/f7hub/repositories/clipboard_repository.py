"""Clipboard reads and dormant atomic persistence through existing infrastructure."""

from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import sqlite3
from uuid import uuid4

from f7hub.domain.clipboard import (
    ClipboardItemRef, ClipboardRecentItem, ClipboardRecentPage,
    normalize_preview, validate_recent_limit, validate_utc_timestamp,
    ClipboardAdmissionBinding, ClipboardPrivacyPolicy, ClipboardOperation,
    ClipboardCaptureOutcome, ClipboardReceiptResult, ReplayDisposition,
    ClipboardPersistenceCode as Code, ClipboardPersistenceError, RECEIPT_DAYS,
    ClipboardConsentSnapshot,
    ClipboardAppendHead, AdmittedManualText, ClipboardPasteCode as PasteCode,
    ClipboardPasteError, validate_uuid, validate_token,
)
from f7hub.infrastructure.database import DatabaseError, database_connection, open_database
from f7hub.repositories.settings_repository import _eligible_consent, _read_state, SettingsPersistenceError
from f7hub.domain.clipboard_settings import SOURCE_PROCESS_ENABLED


_RECENT_SQL = """
    SELECT clipboard_item_id, revision, substr(raw_text, 1, 241) AS preview_excerpt,
           last_received_at, retention_intent, is_pinned, expires_at, sensitivity,
           (SELECT e.source_process_basename FROM clipboard_capture_events AS e
            WHERE e.clipboard_item_id = clipboard_items.clipboard_item_id
            ORDER BY e.clipboard_capture_event_id DESC LIMIT 1) AS source_process_basename
    FROM clipboard_items
    WHERE sensitivity = 'PERMITTED' AND assessment_complete = 1
      AND (retention_intent = 'SAVED' OR expires_at > ?)
    ORDER BY last_received_at DESC, clipboard_item_id DESC
    LIMIT ?
"""


class ClipboardRepositoryError(RuntimeError):
    """Safe failure of a Clipboard read or persisted projection."""


class ClipboardRepository:
    """Own SQL; the service alone composes and invokes trusted admission."""

    def __init__(self, database_path: str | Path, *, profile_scope: str | None = None) -> None:
        self._database_path = database_path
        self.profile_scope = profile_scope

    def _prepare_consent(self):
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                connection.execute('BEGIN')
                return _eligible_consent(connection, self.database_scope, self.profile_scope)
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, SettingsPersistenceError):
            return None

    @property
    def database_scope(self) -> str:
        # A path identity, never a text-derived content fingerprint. Not persisted raw.
        path = os.path.normcase(str(Path(self._database_path).expanduser().resolve()))
        return hashlib.sha256(path.encode("utf-8")).hexdigest()

    def get_recent(self, *, limit: int, as_of: str) -> ClipboardRecentPage:
        validate_recent_limit(limit)
        validate_utc_timestamp(as_of)
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                records = connection.execute(_RECENT_SQL, (as_of, limit + 1)).fetchall()
            rows = tuple(_recent_from_row(record) for record in records[:limit])
            return ClipboardRecentPage(rows, len(records) > limit, limit, as_of)
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError, UnicodeError):
            raise ClipboardRepositoryError("Could not read Clipboard history.") from None

    def _read_latest_paste_source(self, consent: ClipboardConsentSnapshot,
                                  *, as_of: str) -> ClipboardAppendHead:
        """Service preparation read, fenced before loading any exact source.

        Visibility alone is not authorization: recheck the supplied S05 snapshot
        against current database consent in this same read transaction. Public
        repository projections expose no new exact-source interface.
        """
        validate_utc_timestamp(as_of)
        if type(consent) is not ClipboardConsentSnapshot:
            raise ClipboardPasteError(PasteCode.DENIED)
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                connection.execute("BEGIN")
                current = _eligible_consent(connection, self.database_scope, self.profile_scope)
                if current is None or current != consent:
                    raise ClipboardPasteError(PasteCode.DENIED)
                return _append_head(connection, as_of)
        except ClipboardPasteError:
            raise
        except Exception:
            raise ClipboardPasteError(PasteCode.UNAVAILABLE) from None

    def _read_paste_consent(self) -> ClipboardConsentSnapshot | None:
        """Unlike historical capture preparation, distinguish storage failure."""
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                connection.execute("BEGIN")
                return _eligible_consent(connection, self.database_scope, self.profile_scope)
        except (ValueError, TypeError, SettingsPersistenceError):
            return None
        except Exception:
            raise ClipboardPasteError(PasteCode.UNAVAILABLE) from None

    def _validate_latest_paste(self, expected: ClipboardAppendHead,
                               consent: ClipboardConsentSnapshot, *, as_of: str) -> ClipboardAppendHead:
        """Final authorization snapshot ordered against all supported SQLite writers.

        No detector/caller callback or native effect runs in this reservation.
        The service retires the one-use ticket before entering; every failure burns it.
        """
        validate_utc_timestamp(as_of)
        if type(expected) is not ClipboardAppendHead or type(consent) is not ClipboardConsentSnapshot:
            raise ClipboardPasteError(PasteCode.DENIED)
        try:
            with database_connection(self._database_path) as connection:
                connection.execute("BEGIN IMMEDIATE")
                current = _eligible_consent(connection, self.database_scope, self.profile_scope)
                if current is None or current != consent:
                    raise ClipboardPasteError(PasteCode.DENIED)
                actual = _append_head(connection, as_of)
                if actual.append_token != expected.append_token:
                    raise ClipboardPasteError(PasteCode.STALE_HEAD)
                if actual != expected:
                    raise ClipboardPasteError(PasteCode.STALE_SOURCE)
                connection.commit()
                return actual
        except ClipboardPasteError:
            raise
        except Exception:
            raise ClipboardPasteError(PasteCode.UNAVAILABLE) from None

    def lookup_receipt(self, operation: ClipboardOperation, *, as_of: str) -> ClipboardReceiptResult:
        if type(operation) is not ClipboardOperation:
            raise ValueError("Clipboard lookup requires a typed operation.")
        validate_utc_timestamp(as_of)
        try:
            with database_connection(self._database_path, read_only=True) as connection:
                # Keep receipt and live-reference observation in one read snapshot.
                connection.execute("BEGIN")
                row = _find_receipt(connection, operation)
                if row is None or row["expires_at"] <= as_of or row["database_scope"] != self.database_scope:
                    return ClipboardReceiptResult(ReplayDisposition.UNKNOWN_OR_EXPIRED)
                return _receipt_result(connection, row)
        except (sqlite3.Error, OSError, DatabaseError, ValueError, TypeError):
            raise ClipboardPersistenceError(Code.LOOKUP_UNAVAILABLE) from None

    def _persist_admitted(self, binding: ClipboardAdmissionBinding, policy: ClipboardPrivacyPolicy,
                          *, accepted_at: str, consent: ClipboardConsentSnapshot | None = None) -> ClipboardReceiptResult:
        """Service-only prepared core. No admission callbacks run under the lock."""
        if (type(binding) is not ClipboardAdmissionBinding or type(policy) is not ClipboardPrivacyPolicy
                or not policy.permits_history or binding.database_scope != self.database_scope
                or type(consent) is not ClipboardConsentSnapshot):
            raise ClipboardPersistenceError(Code.ADMISSION_DENIED)
        validate_utc_timestamp(accepted_at)
        instant = datetime.strptime(accepted_at, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        temporary_expiry = _utc(instant + timedelta(days=policy.temporary_days))
        receipt_expiry = _utc(instant + timedelta(days=RECEIPT_DAYS))
        metadata = _request_metadata(binding, policy)
        def persist(connection):
            try:
                current = _eligible_consent(connection, self.database_scope, self.profile_scope)
            except (sqlite3.Error, ValueError, TypeError, SettingsPersistenceError):
                current = None
            if current is None or current != consent:
                raise ClipboardPersistenceError(Code.ADMISSION_DENIED)
            # Resolve this independent false-default field on the same reserved writer.
            state = _read_state(connection)
            process_enabled = any(x.key == SOURCE_PROCESS_ENABLED and x.value_type == "BOOLEAN"
                                  and x.value_text == "true" for x in state.overrides)
            basename = binding.command.source_process_basename if process_enabled else None
            return _capture(connection, binding, metadata, accepted_at, temporary_expiry, receipt_expiry, basename)
        return self._write(persist)

    def _delete_expired_receipts(self, *, as_of: str,
                                 protected_generation: tuple[str, str] | None) -> int:
        """One explicitly requested batch; at most 100, no Item writes."""
        validate_utc_timestamp(as_of)
        def remove(connection):
            sql = "SELECT clipboard_operation_receipt_id FROM clipboard_operation_receipts WHERE expires_at <= ?"
            parameters = [as_of]
            if protected_generation is not None:
                sql += " AND NOT (producer_binding = ? AND ingress_generation = ?)"
                parameters.extend(protected_generation)
            rows = connection.execute(sql + " ORDER BY expires_at, clipboard_operation_receipt_id LIMIT 100", parameters).fetchall()
            connection.executemany("DELETE FROM clipboard_operation_receipts WHERE clipboard_operation_receipt_id=?", rows)
            return len(rows)
        return self._write(remove)

    def _write(self, action):
        """One writer reservation. Distinguish rollback from uncertain commit/cleanup."""
        connection = None
        result = None
        failure = None
        committed = False
        commit_attempted = False
        try:
            connection = open_database(self._database_path)
            connection.execute("BEGIN IMMEDIATE")
            result = action(connection)
            commit_attempted = True
            connection.commit()
            committed = True
        except Exception as error:
            if commit_attempted:
                failure = Code.UNCERTAIN
            elif isinstance(error, ClipboardPersistenceError):
                failure = error.code
            elif connection is not None and connection.in_transaction:
                failure = Code.ROLLED_BACK
            else:
                failure = Code.NOT_STARTED
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.rollback()
                except Exception:
                    failure = Code.UNCERTAIN
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    # Successful commit is authoritative even when cleanup fails.
                    if not committed:
                        failure = Code.UNCERTAIN
        if failure is not None:
            raise ClipboardPersistenceError(failure) from None
        return result


def _utc(instant: datetime) -> str:
    return instant.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _find_receipt(connection, operation):
    return connection.execute("""SELECT * FROM clipboard_operation_receipts
        WHERE producer_binding=? AND ingress_generation=? AND operation_id=?""",
        (operation.producer_binding, operation.ingress_generation, operation.operation_id)).fetchone()


def _request_metadata(binding, policy):
    command = binding.command
    return dict(database_scope=binding.database_scope, request_profile=command.request_profile,
        media_type=command.source.media_type, identity_profile=command.source.identity_profile,
        capture_method=command.capture_method, observed_at=command.observed_at, source_class=command.source_class,
        assessment_method=policy.assessment_method, assessment_version=policy.assessment_version,
        policy_version=policy.policy_version, sensitivity=policy.sensitivity,
        assessment_complete=int(policy.assessment_complete),
        durable_history_authorized=int(policy.durable_history_authorized), temporary_days=policy.temporary_days)


def _receipt_result(connection, row, *, replay_source=None):
    operation = ClipboardOperation(row["producer_binding"], row["ingress_generation"], row["operation_id"])
    outcome = ClipboardCaptureOutcome(operation, row["historical_item_id"], row["historical_event_id"],
        bool(row["was_duplicate"]), row["captured_total"], row["item_revision"], row["retention_intent"],
        bool(row["is_pinned"]), row["item_expires_at"], row["accepted_at"], row["expires_at"])
    live = None
    if row["live_item_id"] is not None:
        live = connection.execute("SELECT raw_text, media_type, identity_profile FROM clipboard_items WHERE clipboard_item_id=?",
                                  (row["live_item_id"],)).fetchone()
    if live is None:
        return ClipboardReceiptResult(ReplayDisposition.KNOWN_COMMITTED_SOURCE_UNAVAILABLE, outcome)
    if replay_source is not None:
        if (live["raw_text"], live["media_type"], live["identity_profile"]) != (
                replay_source.text, replay_source.media_type, replay_source.identity_profile):
            raise ClipboardPersistenceError(Code.OPERATION_CONFLICT)
        return ClipboardReceiptResult(ReplayDisposition.SAME_OPERATION, outcome,
                                      ClipboardItemRef(row["live_item_id"]), True)
    return ClipboardReceiptResult(ReplayDisposition.KNOWN_COMMITTED, outcome, ClipboardItemRef(row["live_item_id"]))


def _capture(connection, binding, metadata, accepted_at, temporary_expiry, receipt_expiry, source_process_basename=None):
    command = binding.command
    operation = command.operation
    receipt = _find_receipt(connection, operation)
    if receipt is not None:
        if receipt["expires_at"] <= accepted_at:
            raise ClipboardPersistenceError(Code.GENERATION_STALE)
        if any(receipt[key] != value for key, value in metadata.items()):
            raise ClipboardPersistenceError(Code.OPERATION_CONFLICT)
        return _receipt_result(connection, receipt, replay_source=command.source)
    matches = connection.execute("""SELECT * FROM clipboard_items
        WHERE media_type=? AND identity_profile=? AND raw_text COLLATE BINARY = ? LIMIT 2""",
        (command.source.media_type, command.source.identity_profile, command.source.text)).fetchall()
    if len(matches) > 1:
        raise ClipboardPersistenceError(Code.AMBIGUOUS_IDENTITY)
    duplicate = bool(matches)
    if matches:
        item = matches[0]
        item_id = item["clipboard_item_id"]
        # min/max preserve lifetime summaries across backward UTC movement.
        first = min(item["first_received_at"], accepted_at)
        last = max(item["last_received_at"], accepted_at)
        expiry = None if item["retention_intent"] == "SAVED" else max(item["expires_at"], temporary_expiry)
        connection.execute("""UPDATE clipboard_items SET first_received_at=?, last_received_at=?, expires_at=?,
            captured_total=captured_total+1, revision=revision+1 WHERE clipboard_item_id=?""",
            (first, last, expiry, item_id))
    else:
        cursor = connection.execute("""INSERT INTO clipboard_items
            (raw_text, media_type, identity_profile, sensitivity, assessment_complete,
             assessment_method, assessment_version, retention_intent, is_pinned, expires_at,
             first_received_at, last_received_at, captured_total, revision)
            VALUES (?, ?, ?, 'PERMITTED', 1, ?, ?, 'TEMPORARY', 0, ?, ?, ?, 1, 1)""",
            (command.source.text, command.source.media_type, command.source.identity_profile,
             metadata["assessment_method"], metadata["assessment_version"], temporary_expiry, accepted_at, accepted_at))
        item_id = cursor.lastrowid
    event_id = connection.execute("""INSERT INTO clipboard_capture_events
        (clipboard_item_id, received_at, observed_at, capture_method, source_class,
         producer_binding, ingress_generation, operation_id, source_process_basename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item_id, accepted_at, command.observed_at, command.capture_method, command.source_class,
         operation.producer_binding, operation.ingress_generation, operation.operation_id, source_process_basename)).lastrowid
    item = connection.execute("SELECT * FROM clipboard_items WHERE clipboard_item_id=?", (item_id,)).fetchone()
    values = dict(producer_binding=operation.producer_binding, ingress_generation=operation.ingress_generation,
        operation_id=operation.operation_id, **metadata, historical_item_id=item_id, historical_event_id=event_id,
        live_item_id=item_id, was_duplicate=int(duplicate), captured_total=item["captured_total"],
        item_revision=item["revision"], retention_intent=item["retention_intent"], is_pinned=item["is_pinned"],
        item_expires_at=item["expires_at"], accepted_at=accepted_at, expires_at=receipt_expiry)
    connection.execute("INSERT INTO clipboard_operation_receipts (" + ",".join(values)
                       + ") VALUES (" + ",".join("?" for _ in values) + ")", tuple(values.values()))
    connection.execute("""INSERT INTO clipboard_append_head
        (singleton_id, append_token, live_item_id, item_revision) VALUES (1, ?, ?, ?)
        ON CONFLICT(singleton_id) DO UPDATE SET append_token=excluded.append_token,
        live_item_id=excluded.live_item_id, item_revision=excluded.item_revision""",
        (str(uuid4()), item_id, item["revision"]))
    outcome = ClipboardCaptureOutcome(operation, item_id, event_id, duplicate, item["captured_total"],
        item["revision"], item["retention_intent"], bool(item["is_pinned"]), item["expires_at"], accepted_at, receipt_expiry)
    return ClipboardReceiptResult(ReplayDisposition.NEW_CAPTURE, outcome, ClipboardItemRef(item_id))


def _append_head(connection, as_of):
    # One join in the caller's coherent snapshot. No historical/recent ordering.
    rows = connection.execute("""SELECT h.singleton_id, h.append_token, h.live_item_id,
        h.item_revision, i.* FROM clipboard_append_head h
        LEFT JOIN clipboard_items i ON i.clipboard_item_id=h.live_item_id""").fetchall()
    if not rows:
        raise ClipboardPasteError(PasteCode.EMPTY)
    if len(rows) != 1 or rows[0]["singleton_id"] != 1:
        raise ClipboardPasteError(PasteCode.STALE_SOURCE)
    row = rows[0]
    try:
        validate_uuid(row["append_token"])
        ClipboardItemRef(row["item_revision"])
        if row["live_item_id"] is None or row["clipboard_item_id"] is None:
            raise ClipboardPasteError(PasteCode.SOURCE_UNAVAILABLE)
        ref = ClipboardItemRef(row["live_item_id"])
        if row["revision"] != row["item_revision"]:
            raise ClipboardPasteError(PasteCode.STALE_SOURCE)
        if row["sensitivity"] != "PERMITTED" or row["assessment_complete"] != 1:
            raise ClipboardPasteError(PasteCode.DENIED)
        source = AdmittedManualText(row["raw_text"], row["media_type"], row["identity_profile"])
        for value in (row["assessment_method"], row["assessment_version"]):
            validate_token(value)
        if row["is_pinned"] not in (0, 1):
            raise ValueError()
        if row["retention_intent"] == "TEMPORARY":
            validate_utc_timestamp(row["expires_at"])
            if row["is_pinned"]:
                raise ValueError()
            if row["expires_at"] <= as_of:
                raise ClipboardPasteError(PasteCode.EXPIRED)
        elif row["retention_intent"] != "SAVED" or row["expires_at"] is not None:
            raise ValueError()
        return ClipboardAppendHead(row["append_token"], ref, row["item_revision"], source,
            row["retention_intent"], row["expires_at"], bool(row["is_pinned"]),
            row["assessment_method"], row["assessment_version"])
    except ClipboardPasteError:
        raise
    except (ValueError, TypeError, UnicodeError):
        raise ClipboardPasteError(PasteCode.STALE_SOURCE) from None


def _recent_from_row(record: sqlite3.Row) -> ClipboardRecentItem:
    preview, truncated = normalize_preview(record["preview_excerpt"])
    pin = record["is_pinned"]
    if type(pin) is not int or pin not in (0, 1):
        raise ValueError("Invalid Clipboard pin state.")
    return ClipboardRecentItem(
        item_ref=ClipboardItemRef(record["clipboard_item_id"]),
        revision=record["revision"], preview=preview, preview_truncated=truncated,
        last_received_at=record["last_received_at"],
        retention_intent=record["retention_intent"], is_pinned=bool(pin),
        expires_at=record["expires_at"], sensitivity=record["sensitivity"],
        source_process_basename=record["source_process_basename"],
    )
