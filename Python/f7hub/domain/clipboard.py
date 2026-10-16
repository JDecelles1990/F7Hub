"""Immutable local Clipboard projections; no Qt, SQLite or capture authority."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import unicodedata
from uuid import UUID


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


# D02 in-process values. These carry assertions, never admission authority.
IDENTITY_PROFILE = "clipboard_text_exact_v1"
REQUEST_PROFILE = "clipboard_manual_durable_v1"
TEMPORARY_DAYS = 7
RECEIPT_DAYS = 14
MAX_TEXT_BYTES = 65_536
CONSENT_DISCLOSURE = "clipboard_setup_manual_history_v1"
CONSENT_POLICY = "clipboard_history_consent_v1"
_TOKEN = re.compile(r"[A-Za-z0-9_.:-]+")


def validate_token(value: str, maximum: int = 64) -> None:
    if type(value) is not str or not 1 <= len(value) <= maximum or _TOKEN.fullmatch(value) is None:
        raise ClipboardValidationError("Clipboard metadata must be a bounded identifier.")


def validate_uuid(value: str) -> None:
    valid = False
    if type(value) is str:
        try:
            valid = str(UUID(value)) == value
        except ValueError:
            pass
    if not valid:
        raise ClipboardValidationError("Clipboard operation identity must be a canonical UUID.")


@dataclass(frozen=True, slots=True)
class AdmittedManualText:
    """Exact bounded source candidate; construction does not authorize storage."""

    text: str = field(repr=False)
    media_type: str = "text/plain"
    identity_profile: str = IDENTITY_PROFILE

    def __post_init__(self) -> None:
        valid = type(self.text) is str and bool(self.text.strip()) and "\0" not in self.text
        if valid:
            try:
                valid = len(self.text.encode("utf-8", errors="strict")) <= MAX_TEXT_BYTES
            except UnicodeError:
                valid = False
        if not valid or self.media_type != "text/plain" or self.identity_profile != IDENTITY_PROFILE:
            raise ClipboardValidationError("Clipboard source is outside the manual exact-text profile.")


@dataclass(frozen=True, slots=True)
class ClipboardOperation:
    producer_binding: str
    ingress_generation: str
    operation_id: str

    def __post_init__(self) -> None:
        validate_token(self.producer_binding, 128)
        validate_uuid(self.ingress_generation)
        validate_uuid(self.operation_id)


@dataclass(frozen=True, slots=True)
class ClipboardCaptureCommand:
    operation: ClipboardOperation
    source: AdmittedManualText = field(repr=False)
    capture_method: str = "F7HUB"
    observed_at: str | None = None
    source_class: str | None = None
    request_profile: str = REQUEST_PROFILE

    def __post_init__(self) -> None:
        if type(self.operation) is not ClipboardOperation or type(self.source) is not AdmittedManualText:
            raise ClipboardValidationError("Clipboard command requires immutable typed values.")
        if self.capture_method not in ("F7HUB", "AHK_MANUAL") or self.request_profile != REQUEST_PROFILE:
            raise ClipboardValidationError("Clipboard capture profile is unsupported.")
        if self.observed_at is not None:
            validate_utc_timestamp(self.observed_at)
        if self.source_class not in (None, "terminal", "browser", "editor", "unknown"):
            raise ClipboardValidationError("Clipboard coarse source class is invalid.")


@dataclass(frozen=True, slots=True)
class ClipboardPrivacyPolicy:
    """Completed assessment assertions returned only by the composed authority."""

    assessment_method: str
    assessment_version: str
    policy_version: str
    sensitivity: str
    assessment_complete: bool
    durable_history_authorized: bool
    temporary_days: int = TEMPORARY_DAYS

    def __post_init__(self) -> None:
        for value in (self.assessment_method, self.assessment_version, self.policy_version):
            validate_token(value)
        if self.sensitivity not in ("PERMITTED", "DENIED", "UNAVAILABLE"):
            raise ClipboardValidationError("Clipboard privacy disposition is invalid.")
        if (type(self.assessment_complete) is not bool or type(self.durable_history_authorized) is not bool
                or type(self.temporary_days) is not int or self.temporary_days != TEMPORARY_DAYS):
            raise ClipboardValidationError("Clipboard privacy policy is invalid.")

    @property
    def permits_history(self) -> bool:
        return self.sensitivity == "PERMITTED" and self.assessment_complete and self.durable_history_authorized


@dataclass(frozen=True, slots=True)
class ClipboardAdmissionBinding:
    command: ClipboardCaptureCommand = field(repr=False)
    database_scope: str

    def __post_init__(self) -> None:
        if type(self.command) is not ClipboardCaptureCommand:
            raise ClipboardValidationError("Clipboard admission binding requires a command.")
        if type(self.database_scope) is not str or re.fullmatch(r"[0-9a-f]{64}", self.database_scope) is None:
            raise ClipboardValidationError("Clipboard database scope is invalid.")


@dataclass(frozen=True, slots=True)
class ClipboardAdmissionDecision:
    binding: ClipboardAdmissionBinding = field(repr=False)
    policy: ClipboardPrivacyPolicy

    def __post_init__(self) -> None:
        if type(self.binding) is not ClipboardAdmissionBinding or type(self.policy) is not ClipboardPrivacyPolicy:
            raise ClipboardValidationError("Clipboard admission decision is invalid.")


@dataclass(frozen=True, slots=True)
class ClipboardConsentSnapshot:
    """Prepared local evidence, never a capability or caller authority."""

    database_instance_id: str
    database_scope: str
    profile_scope: str
    consent_epoch: int
    settings_revision: int

    def __post_init__(self) -> None:
        for value, size in ((self.database_instance_id, 32), (self.database_scope, 64), (self.profile_scope, 64)):
            if type(value) is not str or re.fullmatch(r"[0-9a-f]{%d}" % size, value) is None:
                raise ClipboardValidationError("Clipboard consent scope is invalid.")
        for value, minimum in ((self.consent_epoch, 1), (self.settings_revision, 0)):
            if type(value) is not int or not minimum <= value <= 2**63 - 1:
                raise ClipboardValidationError("Clipboard consent ordering is invalid.")

class ReplayDisposition(str, Enum):
    NEW_CAPTURE = "NEW_CAPTURE"
    SAME_OPERATION = "SAME_OPERATION"
    KNOWN_COMMITTED_SOURCE_UNAVAILABLE = "KNOWN_COMMITTED_SOURCE_UNAVAILABLE"
    KNOWN_COMMITTED = "KNOWN_COMMITTED"
    UNKNOWN_OR_EXPIRED = "UNKNOWN_OR_EXPIRED"


@dataclass(frozen=True, slots=True)
class ClipboardCaptureOutcome:
    """Original committed snapshot, independent of later Item state/deletion."""

    operation: ClipboardOperation
    historical_item_id: int
    historical_event_id: int
    was_duplicate: bool
    captured_total: int
    item_revision: int
    retention_intent: str
    is_pinned: bool
    item_expires_at: str | None
    accepted_at: str
    receipt_expires_at: str

    def __post_init__(self) -> None:
        if type(self.operation) is not ClipboardOperation:
            raise ClipboardValidationError("Clipboard outcome operation is invalid.")
        for value in (self.historical_item_id, self.historical_event_id, self.captured_total, self.item_revision):
            _validate_identity(value)
        if type(self.was_duplicate) is not bool or type(self.is_pinned) is not bool:
            raise ClipboardValidationError("Clipboard outcome flags are invalid.")
        validate_utc_timestamp(self.accepted_at)
        validate_utc_timestamp(self.receipt_expires_at)
        if self.receipt_expires_at <= self.accepted_at:
            raise ClipboardValidationError("Clipboard receipt lifetime is invalid.")
        if self.retention_intent == "TEMPORARY":
            validate_utc_timestamp(self.item_expires_at)
            if self.is_pinned or self.item_expires_at <= self.accepted_at:
                raise ClipboardValidationError("Clipboard outcome retention is invalid.")
        elif self.retention_intent != "SAVED" or self.item_expires_at is not None:
            raise ClipboardValidationError("Clipboard outcome preservation is invalid.")


@dataclass(frozen=True, slots=True)
class ClipboardReceiptResult:
    disposition: ReplayDisposition
    outcome: ClipboardCaptureOutcome | None = None
    live_item_ref: ClipboardItemRef | None = None
    payload_equality_verified: bool = False

    def __post_init__(self) -> None:
        if type(self.disposition) is not ReplayDisposition or type(self.payload_equality_verified) is not bool:
            raise ClipboardValidationError("Clipboard receipt result is invalid.")
        if self.disposition == ReplayDisposition.UNKNOWN_OR_EXPIRED:
            valid = self.outcome is None and self.live_item_ref is None and not self.payload_equality_verified
        else:
            valid = type(self.outcome) is ClipboardCaptureOutcome
            if self.disposition == ReplayDisposition.KNOWN_COMMITTED_SOURCE_UNAVAILABLE:
                valid = valid and self.live_item_ref is None and not self.payload_equality_verified
            else:
                valid = valid and type(self.live_item_ref) is ClipboardItemRef
                if valid:
                    valid = self.live_item_ref.clipboard_item_id == self.outcome.historical_item_id
                valid = valid and (self.payload_equality_verified == (self.disposition == ReplayDisposition.SAME_OPERATION))
        if not valid:
            raise ClipboardValidationError("Clipboard receipt observation is inconsistent.")


class ClipboardPersistenceCode(str, Enum):
    ADMISSION_DENIED = "ADMISSION_DENIED"
    ADMISSION_UNAVAILABLE = "ADMISSION_UNAVAILABLE"
    GENERATION_STALE = "GENERATION_STALE"
    CAPACITY_EXHAUSTED = "CAPACITY_EXHAUSTED"
    OPERATION_REJECTED = "OPERATION_REJECTED"
    OPERATION_CONFLICT = "OPERATION_CONFLICT"
    AMBIGUOUS_IDENTITY = "AMBIGUOUS_IDENTITY"
    ROLLED_BACK = "ROLLED_BACK"
    NOT_STARTED = "NOT_STARTED"
    UNCERTAIN = "UNCERTAIN"
    CLOCK_ANOMALY = "CLOCK_ANOMALY"
    LOOKUP_UNAVAILABLE = "LOOKUP_UNAVAILABLE"


class ClipboardPersistenceError(RuntimeError):
    """Fixed safe code only; UNCERTAIN requires receipt reconciliation."""

    def __init__(self, code: ClipboardPersistenceCode) -> None:
        if type(code) is not ClipboardPersistenceCode:
            raise ClipboardValidationError("Clipboard persistence error code is invalid.")
        self.code = code
        super().__init__("Clipboard persistence: " + code.value + ".")


class ClipboardPasteCode(str, Enum):
    EMPTY = "EMPTY"
    EXPIRED = "EXPIRED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    STALE_SOURCE = "STALE_SOURCE"
    STALE_HEAD = "STALE_HEAD"
    DENIED = "DENIED"
    UNAVAILABLE = "UNAVAILABLE"
    BUSY = "BUSY"
    REPLAYED = "REPLAYED"


class ClipboardPasteError(RuntimeError):
    """Fixed content-free denial; no native effect has been authorized."""

    def __init__(self, code: ClipboardPasteCode) -> None:
        if type(code) is not ClipboardPasteCode:
            raise ClipboardValidationError("Clipboard paste failure is invalid.")
        self.code = code
        super().__init__("Clipboard paste: " + code.value + ".")


@dataclass(frozen=True, slots=True)
class ClipboardAppendHead:
    """Repository-to-service exact source snapshot; never a transport projection."""

    append_token: str
    item_ref: ClipboardItemRef
    item_revision: int
    source: AdmittedManualText = field(repr=False)
    retention_intent: str
    expires_at: str | None
    is_pinned: bool
    assessment_method: str
    assessment_version: str


@dataclass(frozen=True, slots=True)
class ClipboardPasteAuthorization:
    """Content-free binding. Values alone confer no service authority."""

    prepared_id: str = field(repr=False)
    head_token: str
    item_ref: ClipboardItemRef
    revision: int
    target_token: str = field(repr=False)

    def __post_init__(self) -> None:
        for value in (self.prepared_id, self.head_token, self.target_token):
            validate_uuid(value)
        if type(self.item_ref) is not ClipboardItemRef:
            raise ClipboardValidationError("Clipboard paste source reference is invalid.")
        _validate_identity(self.revision)


@dataclass(frozen=True, slots=True)
class ClipboardPasteSource:
    """One internal delivery only; authorizes no OS effect by itself."""

    authorization: ClipboardPasteAuthorization = field(repr=False)
    source: AdmittedManualText = field(repr=False)
    effect_lease_expires_at: str
