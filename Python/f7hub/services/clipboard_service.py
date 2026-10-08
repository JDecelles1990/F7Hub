"""Read-only Clipboard use case; capture and production writes remain deferred."""

from datetime import datetime, timezone
import sqlite3
from typing import Callable

from f7hub.domain.clipboard import (
    ClipboardRecentPage, ClipboardValidationError, RECENT_DEFAULT_LIMIT,
    validate_recent_limit, validate_utc_timestamp,
)
from f7hub.repositories.clipboard_repository import ClipboardRepository


class ClipboardQueryError(RuntimeError):
    """Safe application failure; history unavailability is not an empty result."""


class ClipboardService:
    """Validate one first-page intent and delegate to the Clipboard owner."""

    def __init__(self, repository: ClipboardRepository, *,
                 clock: Callable[[], datetime] | None = None) -> None:
        self._repository = repository
        self._clock = clock if clock is not None else lambda: datetime.now(timezone.utc)

    def get_recent(self, *, limit: int = RECENT_DEFAULT_LIMIT) -> ClipboardRecentPage:
        validate_recent_limit(limit)
        try:
            instant = self._clock()
            if not isinstance(instant, datetime) or instant.utcoffset() is None:
                raise ValueError("Clipboard clock must provide an aware instant.")
            as_of = instant.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            validate_utc_timestamp(as_of)
            page = self._repository.get_recent(limit=limit, as_of=as_of)
            if not isinstance(page, ClipboardRecentPage) or page.limit != limit or page.as_of != as_of:
                raise ValueError("Clipboard repository returned an incompatible page.")
            return page
        except (sqlite3.Error, OSError, RuntimeError, ValueError, TypeError):
            raise ClipboardQueryError("Clipboard history is unavailable. Retry the read when ready.") from None
