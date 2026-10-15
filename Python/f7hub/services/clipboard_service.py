"""Clipboard use cases; dormant persistence defaults to unavailable admission."""

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import sqlite3
import threading
import time
from typing import Callable, Protocol
from uuid import uuid4
from pathlib import Path

from f7hub.domain.clipboard import (
    ClipboardRecentPage, ClipboardValidationError, RECENT_DEFAULT_LIMIT,
    validate_recent_limit, validate_utc_timestamp,
    ClipboardAdmissionBinding, ClipboardAdmissionDecision, ClipboardCaptureCommand,
    ClipboardOperation, ClipboardReceiptResult, ClipboardPersistenceCode as Code,
    ClipboardPersistenceError, ReplayDisposition, validate_token,
    ClipboardPrivacyPolicy, CONSENT_POLICY,
)
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.domain.clipboard_privacy import assess_manual_text, ClipboardPrivacyFinding
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED, CLIPBOARD_SETTING_DEFINITIONS
from f7hub.repositories.settings_repository import SettingsPersistenceError


class ClipboardQueryError(RuntimeError):
    """Safe application failure; history unavailability is not an empty result."""


class ClipboardAdmissionAuthority(Protocol):
    """Trusted composition dependency, never a caller-supplied decision parameter.

    Assessments must already be complete. This interface performs no detection.
    Only an explicitly reviewed future composition may provide a real authority.
    """

    def authorize(self, binding: ClipboardAdmissionBinding) -> ClipboardAdmissionDecision | None: ...


class _UnavailableAdmission:
    def authorize(self, binding: ClipboardAdmissionBinding) -> None:
        return None


@dataclass(frozen=True, slots=True, eq=False)
class ClipboardAdmissionContext:
    """Process-local handle. Only the issuing service's exact live object is valid."""

    producer_binding: str
    ingress_generation: str


MAX_GENERATION_SECONDS = 300
MAX_GENERATION_OPERATIONS = 1024
CLOCK_DRIFT_TOLERANCE_SECONDS = 60


class ClipboardService:
    """Validate one first-page intent and delegate to the Clipboard owner."""

    def __init__(self, repository: ClipboardRepository, *,
                 clock: Callable[[], datetime] | None = None,
                 admission: ClipboardAdmissionAuthority | None = None,
                 monotonic: Callable[[], float] | None = None,
                 settings=None) -> None:
        self._repository = repository
        self._clock = clock if clock is not None else lambda: datetime.now(timezone.utc)
        self._admission = admission if admission is not None else _UnavailableAdmission()
        self._settings = settings
        self._real_assessment = settings is not None and admission is None
        if settings is not None and Path(settings._repository._database_path).resolve() != Path(repository._database_path).resolve():
            raise ValueError('Clipboard and Settings must use the same database.')
        self._monotonic = monotonic if monotonic is not None else time.monotonic
        self._lock = threading.RLock()
        self._context = None
        self._deadline = 0.0
        self._operations: dict[str, str] = {}
        self._last_sample = None
        self._clock_anomaly = False

    def refresh_setup(self):
        """Coherent preference/consent projection; reading never grants consent."""
        if self._settings is None or self._repository.profile_scope is None:
            raise SettingsPersistenceError('Clipboard Setup authority is unavailable.')
        return self._settings._load_clipboard_setup(self._repository.database_scope, self._repository.profile_scope)

    @property
    def supports_setup(self):
        return self._settings is not None

    def enable_history_from_setup(self, changes, *, expected_revision, expected_epoch):
        """Explicit affirmative Setup use case in trusted local composition.

        General Settings Apply has no route/flag to this action. This does not
        authenticate a human against malicious code executing in this process.
        """
        if self._settings is None or self._repository.profile_scope is None:
            raise SettingsPersistenceError('Clipboard Setup authority is unavailable.')
        if (not isinstance(changes, dict) or changes.get(WORKFLOW_ENABLED) is not True
                or set(changes) - {d.key for d in CLIPBOARD_SETTING_DEFINITIONS}
                or (expected_epoch is not None and (type(expected_epoch) is not int or not 1 <= expected_epoch < 2**63))):
            raise ClipboardValidationError('Clipboard Setup action is invalid.')
        return self._settings._apply_clipboard_setup(changes, expected_revision=expected_revision,
            expected_epoch=expected_epoch, database_scope=self._repository.database_scope,
            profile_scope=self._repository.profile_scope)

    def open_admission_context(self, producer_binding: str) -> ClipboardAdmissionContext:
        """Issue a fresh generation; issuance alone grants no storage permission."""
        validate_token(producer_binding, 128)
        with self._lock:
            _, monotonic = self._sample()
            self._context = ClipboardAdmissionContext(producer_binding, str(uuid4()))
            self._deadline = monotonic + MAX_GENERATION_SECONDS
            self._operations = {}
            return self._context

    def new_operation(self, context: ClipboardAdmissionContext) -> ClipboardOperation:
        """Issue a fresh identity; caller UUIDs cannot mint genuine operations."""
        with self._lock:
            _, monotonic = self._sample()
            self._require_context(context, monotonic)
            self._require_capacity()
            operation = ClipboardOperation(context.producer_binding, context.ingress_generation, str(uuid4()))
            self._operations[operation.operation_id] = "issued"
            return operation

    def capture_manual_text(self, context: ClipboardAdmissionContext,
                            command: ClipboardCaptureCommand) -> ClipboardReceiptResult:
        if type(command) is not ClipboardCaptureCommand:
            raise ClipboardValidationError("Clipboard capture requires an immutable command.")
        # Serializes local fencing/assessment; separate repository connections still
        # reserve the SQLite writer across services/workers/processes.
        with self._lock:
            _, monotonic = self._sample()
            self._require_context(context, monotonic)
            operation = command.operation
            if (operation.producer_binding, operation.ingress_generation) != (
                    context.producer_binding, context.ingress_generation):
                raise ClipboardPersistenceError(Code.GENERATION_STALE)
            state = self._operations.get(operation.operation_id)
            if state is None:
                self._require_capacity()
                self._operations[operation.operation_id] = "rejected"
                raise ClipboardPersistenceError(Code.OPERATION_REJECTED)
            if state == "rejected":
                raise ClipboardPersistenceError(Code.OPERATION_REJECTED)
            if state == "uncertain":
                raise ClipboardPersistenceError(Code.UNCERTAIN)
            try:
                binding = ClipboardAdmissionBinding(command, self._repository.database_scope)
                # Bind the epoch/revision before expensive assessment; a later
                # grant or settings change must not retarget this preparation.
                consent = self._repository._prepare_consent() if (
                    self._real_assessment or not isinstance(self._admission, _UnavailableAdmission)) else None
                if self._real_assessment:
                    assessment = assess_manual_text(command.source)
                    if assessment.finding != ClipboardPrivacyFinding.PERMITTED or not assessment.assessment_complete:
                        raise ClipboardPersistenceError(Code.ADMISSION_DENIED)
                    decision = ClipboardAdmissionDecision(binding, ClipboardPrivacyPolicy(
                        assessment.assessment_method, assessment.assessment_version, CONSENT_POLICY,
                        'PERMITTED', True, True))
                else:
                    decision = self._admission.authorize(binding)
            except Exception:
                self._operations[operation.operation_id] = "rejected"
                raise ClipboardPersistenceError(Code.ADMISSION_UNAVAILABLE) from None
            if decision is None:
                self._operations[operation.operation_id] = "rejected"
                raise ClipboardPersistenceError(Code.ADMISSION_UNAVAILABLE)
            if (type(decision) is not ClipboardAdmissionDecision or decision.binding != binding
                    or not decision.policy.permits_history):
                self._operations[operation.operation_id] = "rejected"
                raise ClipboardPersistenceError(Code.ADMISSION_DENIED)
            # Assessment and preparation precede writer opening; recheck the lease.
            accepted_at, monotonic = self._sample()
            self._require_context(context, monotonic)
            if state == "done":
                # Receipt loss/expiry is never permission to execute a consumed ID.
                known = self._repository.lookup_receipt(operation, as_of=accepted_at)
                if known.disposition == ReplayDisposition.UNKNOWN_OR_EXPIRED:
                    raise ClipboardPersistenceError(Code.GENERATION_STALE)
            try:
                result = self._repository._persist_admitted(binding, decision.policy, accepted_at=accepted_at,
                                                            consent=consent)
            except ClipboardPersistenceError as error:
                if error.code == Code.UNCERTAIN:
                    self._operations[operation.operation_id] = "uncertain"
                elif error.code not in (Code.NOT_STARTED, Code.ROLLED_BACK, Code.OPERATION_CONFLICT):
                    self._operations[operation.operation_id] = "rejected"
                raise
            self._operations[operation.operation_id] = "done"
            return result

    def lookup_receipt(self, operation: ClipboardOperation) -> ClipboardReceiptResult:
        """Query-only recovery, including after restart/lease expiry/source deletion."""
        if type(operation) is not ClipboardOperation:
            raise ClipboardValidationError("Clipboard receipt lookup requires a typed operation.")
        with self._lock:
            as_of, _ = self._sample()
            return self._repository.lookup_receipt(operation, as_of=as_of)

    def maintain_receipts(self) -> int:
        """Explicit bounded cleanup: at most five transactions of 100 receipts."""
        with self._lock:
            total = 0
            for _ in range(5):
                as_of, monotonic = self._sample()
                if self._clock_anomaly:
                    raise ClipboardPersistenceError(Code.CLOCK_ANOMALY)
                protected = None
                if self._context is not None and monotonic < self._deadline:
                    protected = (self._context.producer_binding, self._context.ingress_generation)
                removed = self._repository._delete_expired_receipts(as_of=as_of, protected_generation=protected)
                total += removed
                if removed < 100:
                    break
            return total

    def _require_context(self, context, monotonic):
        if (type(context) is not ClipboardAdmissionContext or context is not self._context
                or monotonic >= self._deadline):
            raise ClipboardPersistenceError(Code.GENERATION_STALE)

    def _require_capacity(self):
        if len(self._operations) >= MAX_GENERATION_OPERATIONS:
            self._context = None
            self._operations = {}
            raise ClipboardPersistenceError(Code.CAPACITY_EXHAUSTED)

    def _sample(self):
        try:
            instant = self._clock()
            monotonic = self._monotonic()
            if (type(instant) is not datetime or instant.utcoffset() is None
                    or type(monotonic) not in (int, float) or not math.isfinite(monotonic)):
                raise ValueError()
            instant = instant.astimezone(timezone.utc)
            as_of = instant.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            validate_utc_timestamp(as_of)
            if self._last_sample is not None:
                old_instant, old_monotonic = self._last_sample
                wall_elapsed = (instant - old_instant).total_seconds()
                elapsed = monotonic - old_monotonic
                if elapsed < 0:
                    self._context = None
                    raise ValueError()
                if wall_elapsed < 0 or abs(wall_elapsed - elapsed) > CLOCK_DRIFT_TOLERANCE_SECONDS:
                    self._clock_anomaly = True
            self._last_sample = (instant, monotonic)
            return as_of, monotonic
        except Exception:
            self._clock_anomaly = True
            self._context = None
            raise ClipboardPersistenceError(Code.CLOCK_ANOMALY) from None

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
