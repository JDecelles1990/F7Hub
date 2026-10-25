"""Process-local volatile history. No acquisition, persistence or consent authority."""

from dataclasses import dataclass, field, replace
from enum import Enum
from datetime import datetime, timedelta, timezone
import math
import sys
import time
import threading
from typing import Callable, Protocol
from uuid import uuid4

from f7hub.domain.clipboard import normalize_preview, PREVIEW_MAX_SCALARS, ClipboardValidationError
from f7hub.domain.clipboard_privacy import (
    ClipboardPrivacyAssessment, ClipboardPrivacyFinding, ClipboardAssessmentReason,
)


MAX_HISTORY_ENTRIES = 100
MAX_HISTORY_BYTES = 256 * 1024 * 1024
MAX_ENTRY_BYTES = 4 * 1024 * 1024
HISTORY_TTL_SECONDS = 12 * 60 * 60
HISTORY_BASE_BYTES = 16_384
ENTRY_OVERHEAD_BYTES = 2_048
MAX_DUPLICATE_COUNT = 2**31 - 1
CLOCK_DIVERGENCE_SECONDS = 1.0


class ClipboardHistoryUnavailable(RuntimeError):
    """Content-free clock/resource failure; an unavailable read is not an empty read."""


@dataclass(frozen=True, slots=True)
class HistoryClockSample:
    utc: datetime
    elapsed: float
    continuous: bool = True


def system_history_clock() -> HistoryClockSample:
    """Dual clock: wall/elapsed disagreement discards history, including resume gaps.

    No platform assumption that monotonic time includes suspend is necessary.
    A future reviewed resume owner can additionally report continuous=False.
    """
    return HistoryClockSample(datetime.now(timezone.utc), time.monotonic())


@dataclass(frozen=True, slots=True, eq=False)
class VolatileEntryRef:
    """Only the exact live object issued by this store resolves; contains no text."""

    identity: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True, slots=True)
class VolatileEntry:
    """Bounded metadata projection. Full text is available only through a live read."""

    ref: VolatileEntryRef
    admitted_at: datetime
    expires_at: datetime
    utf8_bytes: int
    character_count: int
    line_count: int
    preview: str = field(repr=False)
    preview_truncated: bool
    accounted_bytes: int
    duplicate_count: int = 0


@dataclass(frozen=True, slots=True, repr=False)
class _StoredEntry:
    metadata: VolatileEntry
    payload: bytes
    elapsed_deadline: float


def encode_history_text(text: str) -> bytes | None:
    """Strict whole-text profile; the manual 64-KiB profile is deliberately separate."""
    if type(text) is not str or not text or len(text) > MAX_ENTRY_BYTES:
        return None
    try:
        if not text.strip() or "\0" in text:
            return None
        payload = text.encode("utf-8", errors="strict")
        return payload if len(payload) <= MAX_ENTRY_BYTES else None
    except (UnicodeError, MemoryError):
        return None


class _VolatileHistory:
    """Service-owned store; calls are serialized by the admission service.

    Accounted storage = fixed 16 KiB + sum(bytes object size + preview object
    size + 2 KiB per entry). The fixed reserves cover store/list capacity and
    entry metadata/reference/datetimes/indices/scalars. There is no payload
    index, digest cache, retained decoded string or duplicate text buffer.
    This is a history accounting limit, not a whole-process RSS guarantee.
    """

    def __init__(self, *, clock: Callable[[], HistoryClockSample] = system_history_clock,
                 byte_budget: int = MAX_HISTORY_BYTES) -> None:
        if type(byte_budget) is not int or not HISTORY_BASE_BYTES <= byte_budget <= MAX_HISTORY_BYTES:
            raise ClipboardValidationError("Volatile history budget is outside the supported limits.")
        self._clock = clock
        self._budget = byte_budget
        self._entries: list[_StoredEntry] = []
        self._last_sample: HistoryClockSample | None = None
        self.epoch = object()

    def clear(self) -> None:
        self._entries.clear()
        self.epoch = object()

    def _sample_or_none(self) -> HistoryClockSample | None:
        try:
            sample = self._clock()
            if (type(sample) is not HistoryClockSample or type(sample.utc) is not datetime
                    or sample.utc.tzinfo is None or sample.utc.utcoffset() != timedelta(0)
                    or type(sample.elapsed) not in (float, int) or not math.isfinite(sample.elapsed)
                    or type(sample.continuous) is not bool):
                return None
            return sample
        except Exception:
            return None

    def _now(self) -> HistoryClockSample:
        sample = self._sample_or_none()
        if sample is None:
            self.clear()
            self._last_sample = None
            raise ClipboardHistoryUnavailable("Volatile history clock is unavailable.")
        previous = self._last_sample
        self._last_sample = sample
        discontinuity = not sample.continuous
        if previous is not None:
            wall = (sample.utc - previous.utc).total_seconds()
            elapsed = sample.elapsed - previous.elapsed
            discontinuity |= wall < 0 or elapsed < 0 or abs(wall - elapsed) > CLOCK_DIVERGENCE_SECONDS
        if discontinuity:
            self.clear()
        self._entries[:] = [entry for entry in self._entries
                            if sample.utc < entry.metadata.expires_at
                            and sample.elapsed < entry.elapsed_deadline]
        return sample

    @property
    def accounted_bytes(self) -> int:
        self._now()
        return self._accounted_bytes()

    def _accounted_bytes(self) -> int:
        return HISTORY_BASE_BYTES + sum(e.metadata.accounted_bytes for e in self._entries)

    def list_entries(self, limit: int = MAX_HISTORY_ENTRIES) -> tuple[VolatileEntry, ...]:
        if type(limit) is not int or not 1 <= limit <= MAX_HISTORY_ENTRIES:
            raise ClipboardValidationError("Volatile history limit must be an integer from 1 to 100.")
        self._now()
        return tuple(e.metadata for e in reversed(self._entries[-limit:]))

    def _find(self, ref: VolatileEntryRef) -> _StoredEntry | None:
        self._now()
        return next((e for e in self._entries if e.metadata.ref is ref), None)

    def get_entry(self, ref: VolatileEntryRef) -> VolatileEntry | None:
        entry = self._find(ref)
        return entry.metadata if entry else None

    def read_text(self, ref: VolatileEntryRef) -> str | None:
        entry = self._find(ref)
        if entry is None:
            return None
        text = entry.payload.decode("utf-8", errors="strict")
        # Decoding a large payload can cross expiry; revalidate before release.
        return text if self._find(ref) is entry else None

    def _admit(self, payload: bytes, *, epoch: object) -> "HistoryAdmissionResult":
        """Internal owner boundary; assessment/generation validation lives in service."""
        now = self._now()
        if epoch is not self.epoch:
            return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
        if type(payload) is not bytes or not 0 < len(payload) <= MAX_ENTRY_BYTES:
            return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
        if self._entries and self._entries[-1].payload == payload:
            last = self._entries[-1]
            replacement = replace(last, metadata=replace(last.metadata,
                duplicate_count=min(MAX_DUPLICATE_COUNT, last.metadata.duplicate_count + 1)))
            result = HistoryAdmissionResult(HistoryAdmissionCode.DUPLICATE, last.metadata.ref)
            self._now()
            if epoch is not self.epoch or not self._entries or self._entries[-1] is not last:
                return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
            self._entries[-1] = replacement
            return result
        # Decode transiently for scalar/line counts and a bounded safe preview.
        text = payload.decode("utf-8", errors="strict")
        preview, truncated = normalize_preview(text[:PREVIEW_MAX_SCALARS + 1])
        accounted = sys.getsizeof(payload) + sys.getsizeof(preview) + ENTRY_OVERHEAD_BYTES
        if HISTORY_BASE_BYTES + accounted > self._budget:
            return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
        # Line count: empty text is excluded; CRLF is one break, lone CR/LF one each.
        lines = 1 + text.count("\n") + text.count("\r") - text.count("\r\n")
        metadata = VolatileEntry(VolatileEntryRef(), now.utc,
            now.utc + timedelta(seconds=HISTORY_TTL_SECONDS), len(payload), len(text),
            lines, preview, truncated, accounted)
        stored = _StoredEntry(metadata, payload, now.elapsed + HISTORY_TTL_SECONDS)
        result = HistoryAdmissionResult(HistoryAdmissionCode.ADMITTED, metadata.ref)
        del text
        # Recheck after construction; discard on discontinuity before mutating rows.
        final = self._now()
        if (epoch is not self.epoch or final.utc >= metadata.expires_at
                or final.elapsed >= stored.elapsed_deadline):
            return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
        first_kept = 0
        retained_bytes = self._accounted_bytes()
        while first_kept < len(self._entries) and (
                len(self._entries) - first_kept >= MAX_HISTORY_ENTRIES
                or retained_bytes + accounted > self._budget):
            retained_bytes -= self._entries[first_kept].metadata.accounted_bytes
            first_kept += 1
        # Allocate the complete replacement before evicting any live row. The
        # success result is also ready, so publication needs no further allocation.
        entries = self._entries[first_kept:] + [stored]
        if epoch is not self.epoch:
            return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)
        self._entries = entries
        return result


class VolatilePrivacyAssessor(Protocol):
    """Trusted composition only; assess the complete immutable exact UTF-8 payload.

    Future reviewed acquisition/privacy owner must verify stable supported source
    and complete large-text assessment. Neither this protocol nor a DTO certifies
    that work. No production implementation is provided in RAM-01A.
    """

    def assess(self, payload: bytes) -> ClipboardPrivacyAssessment: ...


class _UnavailableAssessment:
    def assess(self, payload: bytes) -> ClipboardPrivacyAssessment:
        return ClipboardPrivacyAssessment(ClipboardPrivacyFinding.INCOMPLETE,
                                          ClipboardAssessmentReason.UNSUPPORTED_SOURCE)


class HistoryAdmissionCode(str, Enum):
    ADMITTED = "ADMITTED"
    DUPLICATE = "DUPLICATE"
    STALE_OR_DISABLED = "STALE_OR_DISABLED"
    INVALID_TEXT = "INVALID_TEXT"
    ASSESSMENT_DENIED = "ASSESSMENT_DENIED"
    ASSESSMENT_UNAVAILABLE = "ASSESSMENT_UNAVAILABLE"
    CAPACITY_OR_CLOCK_CHANGED = "CAPACITY_OR_CLOCK_CHANGED"


@dataclass(frozen=True, slots=True, eq=False)
class VolatileAdmissionContext:
    """Exact service-issued handle, not consent or a caller-mintable permission."""

    epoch: object


@dataclass(frozen=True, slots=True)
class HistoryAdmissionResult:
    code: HistoryAdmissionCode
    entry_ref: VolatileEntryRef | None = None


class VolatileClipboardHistory:
    """Pure domain admission owner for a separately bounded volatile store.

    Starts disabled and empty. Only future trusted application composition may
    open a context after session consent; there is no GUI/Settings enable flag.
    Assessor injection is a composition seam, not an observe-call permission.
    This is not a sandbox against malicious Python executing in this process.
    """

    def __init__(self, *, assessor: VolatilePrivacyAssessor | None = None,
                 clock: Callable[[], HistoryClockSample] = system_history_clock,
                 byte_budget: int = MAX_HISTORY_BYTES) -> None:
        self._history = _VolatileHistory(clock=clock, byte_budget=byte_budget)
        self._assessor = assessor if assessor is not None else _UnavailableAssessment()
        self._context: VolatileAdmissionContext | None = None
        self._lock = threading.RLock()

    def _open_admission_context(self) -> VolatileAdmissionContext:
        """Internal future lifecycle seam; does not implement monitoring/consent."""
        with self._lock:
            self._history.clear()
            self._context = VolatileAdmissionContext(self._history.epoch)
            return self._context

    def _is_current(self, context: VolatileAdmissionContext) -> bool:
        return context is not None and context is self._context and context.epoch is self._history.epoch

    def observe(self, context: VolatileAdmissionContext, text: str) -> HistoryAdmissionResult:
        with self._lock:
            if not self._is_current(context):
                return HistoryAdmissionResult(HistoryAdmissionCode.STALE_OR_DISABLED)
        payload = encode_history_text(text)
        if payload is None:
            return HistoryAdmissionResult(HistoryAdmissionCode.INVALID_TEXT)
        # No store lock spans external assessment. Clear/revoke remains available.
        try:
            assessment = self._assessor.assess(payload)
        except Exception:
            return HistoryAdmissionResult(HistoryAdmissionCode.ASSESSMENT_UNAVAILABLE)
        with self._lock:
            if not self._is_current(context):
                return HistoryAdmissionResult(HistoryAdmissionCode.STALE_OR_DISABLED)
            if (type(assessment) is not ClipboardPrivacyAssessment or not assessment.assessment_complete
                    or assessment.finding is not ClipboardPrivacyFinding.PERMITTED):
                return HistoryAdmissionResult(HistoryAdmissionCode.ASSESSMENT_DENIED)
            try:
                return self._history._admit(payload, epoch=context.epoch)
            except MemoryError:
                return HistoryAdmissionResult(HistoryAdmissionCode.CAPACITY_OR_CLOCK_CHANGED)

    def clear(self) -> VolatileAdmissionContext | None:
        """Invalidate references and pending work; preserve domain enabled/disabled state."""
        with self._lock:
            self._history.clear()
            if self._context is not None:
                self._context = VolatileAdmissionContext(self._history.epoch)
            return self._context

    def disable_and_clear(self) -> None:
        with self._lock:
            self._context = None
            self._history.clear()

    def list_entries(self, limit: int = MAX_HISTORY_ENTRIES) -> tuple[VolatileEntry, ...]:
        with self._lock:
            return self._history.list_entries(limit)

    def get_entry(self, ref: VolatileEntryRef) -> VolatileEntry | None:
        with self._lock:
            return self._history.get_entry(ref)

    def read_text(self, ref: VolatileEntryRef) -> str | None:
        with self._lock:
            return self._history.read_text(ref)

    @property
    def accounted_bytes(self) -> int:
        with self._lock:
            return self._history.accounted_bytes
