"""Immutable local Clipboard projections; no Qt, SQLite or capture authority."""

from dataclasses import dataclass
from datetime import datetime
import re
import unicodedata


RECENT_DEFAULT_LIMIT = 50
RECENT_MAX_LIMIT = 100
PREVIEW_MAX_SCALARS = 240
_UTC_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z")


class ClipboardValidationError(ValueError):
    """A bounded Clipboard query argument is invalid."""


def validate_recent_limit(limit: int) -> None:
    if type(limit) is not int or not 1 <= limit <= RECENT_MAX_LIMIT:
        raise ClipboardValidationError("Recent limit must be an integer from 1 to 100.")


def validate_utc_timestamp(value: str) -> None:
    """Require a real normalized UTC millisecond date, without echoing input."""
    if not isinstance(value, str) or _UTC_PATTERN.fullmatch(value) is None:
        raise ClipboardValidationError("Clipboard timestamp must be UTC milliseconds.")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        raise ClipboardValidationError("Clipboard timestamp must be a valid date.") from None


def normalize_preview(excerpt: str) -> tuple[str, bool]:
    """Normalize a bounded 241-scalar excerpt, retaining a separate truncation flag."""
    if not isinstance(excerpt, str) or len(excerpt) > PREVIEW_MAX_SCALARS + 1:
        raise ClipboardValidationError("Clipboard preview source must be bounded text.")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in excerpt):
        raise ClipboardValidationError("Clipboard preview source must contain Unicode scalars.")
    preview = "".join(
        " " if unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"} else character
        for character in excerpt[:PREVIEW_MAX_SCALARS]
    )
    return preview, len(excerpt) > PREVIEW_MAX_SCALARS


def _validate_identity(value: int) -> None:
    if type(value) is not int or not 1 <= value <= 2**63 - 1:
        raise ClipboardValidationError("Clipboard identity or revision must be a positive SQLite integer.")


@dataclass(frozen=True)
class ClipboardItemRef:
    """Durable Item identity within the composed Clipboard database scope."""

    clipboard_item_id: int

    def __post_init__(self) -> None:
        _validate_identity(self.clipboard_item_id)


@dataclass(frozen=True)
class ClipboardRecentItem:
    """Safe first-page data; full source and unsupported capabilities are absent."""

    item_ref: ClipboardItemRef
    revision: int
    preview: str
    preview_truncated: bool
    last_received_at: str
    retention_intent: str
    is_pinned: bool
    expires_at: str | None
    sensitivity: str
    kind: None = None

    def __post_init__(self) -> None:
        if not isinstance(self.item_ref, ClipboardItemRef):
            raise ClipboardValidationError("Clipboard Item reference is invalid.")
        _validate_identity(self.revision)
        normalized, truncated = normalize_preview(self.preview)
        if normalized != self.preview or truncated:
            raise ClipboardValidationError("Clipboard preview is not presentation safe.")
        validate_utc_timestamp(self.last_received_at)
        if type(self.is_pinned) is not bool or type(self.preview_truncated) is not bool:
            raise ClipboardValidationError("Clipboard projection flags must be booleans.")
        if self.sensitivity != "PERMITTED" or self.kind is not None:
            raise ClipboardValidationError("Clipboard projection is outside D01 scope.")
        if self.retention_intent == "TEMPORARY":
            validate_utc_timestamp(self.expires_at)
            if self.is_pinned or self.expires_at <= self.last_received_at:
                raise ClipboardValidationError("Clipboard temporary retention is invalid.")
        elif self.retention_intent != "SAVED" or self.expires_at is not None:
            raise ClipboardValidationError("Clipboard preservation state is invalid.")


@dataclass(frozen=True)
class ClipboardRecentPage:
    """One bounded page; has_more does not provide cursor navigation."""

    rows: tuple[ClipboardRecentItem, ...]
    has_more: bool
    limit: int
    as_of: str

    def __post_init__(self) -> None:
        validate_recent_limit(self.limit)
        validate_utc_timestamp(self.as_of)
        if (type(self.rows) is not tuple or len(self.rows) > self.limit
                or any(not isinstance(row, ClipboardRecentItem) for row in self.rows)
                or type(self.has_more) is not bool):
            raise ClipboardValidationError("Clipboard page is not an immutable bounded result.")
