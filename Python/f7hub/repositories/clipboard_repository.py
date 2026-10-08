"""Bounded read-only Clipboard queries through existing SQLite infrastructure."""

from pathlib import Path
import sqlite3

from f7hub.domain.clipboard import (
    ClipboardItemRef, ClipboardRecentItem, ClipboardRecentPage,
    normalize_preview, validate_recent_limit, validate_utc_timestamp,
)
from f7hub.infrastructure.database import DatabaseError, database_connection


_RECENT_SQL = """
    SELECT clipboard_item_id, revision, substr(raw_text, 1, 241) AS preview_excerpt,
           last_received_at, retention_intent, is_pinned, expires_at, sensitivity
    FROM clipboard_items
    WHERE sensitivity = 'PERMITTED' AND assessment_complete = 1
      AND (retention_intent = 'SAVED' OR expires_at > ?)
    ORDER BY last_received_at DESC, clipboard_item_id DESC
    LIMIT ?
"""


class ClipboardRepositoryError(RuntimeError):
    """Safe failure of a Clipboard read or persisted projection."""


class ClipboardRepository:
    """Own Recent mechanics without a production writer or raw-content API."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

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
    )
