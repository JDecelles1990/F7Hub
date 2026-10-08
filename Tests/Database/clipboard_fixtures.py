"""Synthetic D01 database preparation. Never imported by production modules."""

from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import unittest
from uuid import UUID, uuid4

from f7hub.domain.clipboard import validate_utc_timestamp
from f7hub.infrastructure.database import bootstrap_database


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECEIVED = "2026-10-08T10:00:00.000Z"
AS_OF = "2026-10-08T12:00:00.000Z"
EXPIRES = "2026-10-09T10:00:00.000Z"
ITEM_COLUMNS = (
    "clipboard_item_id", "raw_text", "media_type", "identity_profile", "sensitivity",
    "assessment_complete", "assessment_method", "assessment_version", "retention_intent",
    "is_pinned", "expires_at", "first_received_at", "last_received_at", "captured_total", "revision",
)
ITEM_INSERT = "INSERT INTO clipboard_items (" + ", ".join(ITEM_COLUMNS) + ") VALUES (" + ", ".join("?" for _ in ITEM_COLUMNS) + ")"
EVENT_COLUMNS = (
    "clipboard_capture_event_id", "clipboard_item_id", "received_at", "observed_at",
    "capture_method", "source_class", "producer_binding", "ingress_generation", "operation_id",
)
EVENT_INSERT = "INSERT INTO clipboard_capture_events (" + ", ".join(EVENT_COLUMNS) + ") VALUES (" + ", ".join("?" for _ in EVENT_COLUMNS) + ")"


def item_values(**changes):
    """Values for SQL constraint tests; this function does not insert or admit data."""
    values = dict(zip(ITEM_COLUMNS, (
        None, "Synthetic technician note", "text/plain", "clipboard_text_exact_v1", "PERMITTED",
        1, "synthetic_fixture", "1", "TEMPORARY", 0, EXPIRES, RECEIVED, RECEIVED, 1, 1,
    )))
    if set(changes) - set(values):
        raise ValueError("Unknown fixture Item field.")
    values.update(changes)
    return values


def event_values(item_id, **changes):
    values = dict(zip(EVENT_COLUMNS, (
        None, item_id, RECEIVED, None, "F7HUB", None, "synthetic-producer", "synthetic-generation", str(uuid4()),
    )))
    if set(changes) - set(values):
        raise ValueError("Unknown fixture Event field.")
    values.update(changes)
    return values


@dataclass(frozen=True)
class FixtureCapture:
    received_at: str = RECEIVED
    operation_id: str = field(default_factory=lambda: str(uuid4()))
    observed_at: str | None = None
    capture_method: str = "F7HUB"
    source_class: str | None = None
    producer_binding: str = "synthetic-producer"
    ingress_generation: str = "synthetic-generation"


def seed_item(connection, *, raw_text="Synthetic technician note", captures=None,
              item_id=None, retention_intent="TEMPORARY", is_pinned=False,
              expires_at=EXPIRES, revision=1):
    """Atomically prepare one synthetic Item and its genuine fixture occurrences."""
    if not isinstance(raw_text, str) or not raw_text.strip() or "\0" in raw_text:
        raise ValueError("Fixture source must be nonempty scalar text.")
    try:
        size = len(raw_text.encode("utf-8", errors="strict"))
    except UnicodeError:
        raise ValueError("Fixture source must contain Unicode scalars.") from None
    if size > 65536:
        raise ValueError("Fixture source exceeds D01 storage limit.")
    if item_id is not None and (type(item_id) is not int or not 1 <= item_id <= 2**63 - 1):
        raise ValueError("Fixture Item ID is invalid.")
    if type(revision) is not int or not 1 <= revision <= 2**63 - 1:
        raise ValueError("Fixture revision is invalid.")
    if type(is_pinned) is not bool or retention_intent not in ("TEMPORARY", "SAVED"):
        raise ValueError("Fixture preservation is invalid.")
    if is_pinned and retention_intent != "SAVED":
        raise ValueError("Pinned fixture must be saved.")
    captures = (FixtureCapture(),) if captures is None else tuple(captures)
    if not captures or any(not isinstance(capture, FixtureCapture) for capture in captures):
        raise ValueError("Fixture requires actual synthetic capture occurrences.")
    for capture in captures:
        validate_utc_timestamp(capture.received_at)
        if capture.observed_at is not None:
            validate_utc_timestamp(capture.observed_at)
        if not isinstance(capture.operation_id, str) or str(UUID(capture.operation_id)) != capture.operation_id:
            raise ValueError("Fixture operation must be a canonical UUID.")
        if capture.capture_method not in ("F7HUB", "AHK_MANUAL"):
            raise ValueError("Fixture capture method is invalid.")
        if capture.source_class not in (None, "terminal", "browser", "editor", "unknown"):
            raise ValueError("Fixture source class is invalid.")
        for binding in (capture.producer_binding, capture.ingress_generation):
            if not isinstance(binding, str) or not binding.strip() or not 1 <= len(binding) <= 128:
                raise ValueError("Fixture operation binding is invalid.")
    first = min(capture.received_at for capture in captures)
    latest = max(capture.received_at for capture in captures)
    if retention_intent == "TEMPORARY":
        validate_utc_timestamp(expires_at)
        if expires_at <= latest:
            raise ValueError("Fixture expiry must follow receipt.")
    elif expires_at is not None:
        raise ValueError("Saved fixture must not expire.")
    if connection.in_transaction:
        raise ValueError("Fixture owns its transaction.")
    connection.execute("BEGIN")
    try:
        values = item_values(clipboard_item_id=item_id, raw_text=raw_text,
                             retention_intent=retention_intent, is_pinned=int(is_pinned),
                             expires_at=expires_at, first_received_at=first, last_received_at=latest,
                             captured_total=len(captures), revision=revision)
        cursor = connection.execute(ITEM_INSERT, tuple(values[column] for column in ITEM_COLUMNS))
        identity = cursor.lastrowid
        for capture in captures:
            values = event_values(identity, **capture.__dict__)
            connection.execute(EVENT_INSERT, tuple(values[column] for column in EVENT_COLUMNS))
        connection.commit()
        return identity
    except BaseException:
        connection.rollback()
        raise


class ClipboardDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="f7hub-d01-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database_path = self.root / "fixture.db"
        bootstrap_database(self.database_path, PROJECT_ROOT / "Database/Migrations")
