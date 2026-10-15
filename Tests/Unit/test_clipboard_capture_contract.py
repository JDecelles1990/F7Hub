"""D02 synthetic authority and immutable-contract/fencing checks."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from f7hub.domain.clipboard import (
    AdmittedManualText, ClipboardOperation, ClipboardCaptureCommand, ClipboardPrivacyPolicy,
    ClipboardAdmissionBinding, ClipboardAdmissionDecision, ClipboardPersistenceError,
    ClipboardPersistenceCode as Code, ClipboardValidationError, ClipboardReceiptResult,
    ReplayDisposition,
)
from f7hub.services.clipboard_service import ClipboardService, ClipboardAdmissionContext


class SyntheticAuthority:
    """Test-only precompleted assessment. Production never imports this module."""
    def __init__(self):
        self.policy = ClipboardPrivacyPolicy("synthetic_assessment", "1", "1", "PERMITTED", True, True)
        self.calls = []

    def authorize(self, binding):
        self.calls.append(binding)
        return ClipboardAdmissionDecision(binding, self.policy)


class SyntheticClock:
    def __init__(self):
        self.instant = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
        self.elapsed = 100.0

    def utc(self):
        return self.instant

    def monotonic(self):
        return self.elapsed

    def advance(self, seconds):
        self.instant += timedelta(seconds=seconds)
        self.elapsed += seconds


class ClipboardCaptureContractTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock(database_scope="a" * 64)
        self.authority = SyntheticAuthority()
        self.clock = SyntheticClock()
        self.service = ClipboardService(self.repository, admission=self.authority,
            clock=self.clock.utc, monotonic=self.clock.monotonic)
        self.context = self.service.open_admission_context("synthetic")

    def command(self, text="Synthetic manual note"):
        return ClipboardCaptureCommand(self.service.new_operation(self.context), AdmittedManualText(text))

    def assert_code(self, code, function, *args):
        with self.assertRaises(ClipboardPersistenceError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_exact_source_immutable_and_redacted_in_nested_representations(self):
        text = "Synthetic secret sentinel\r\n e\u0301 😀 "
        command = self.command(text)
        binding = ClipboardAdmissionBinding(command, "a" * 64)
        decision = self.authority.authorize(binding)
        self.assertEqual(command.source.text, text)
        for value in (command.source, command, binding, decision):
            self.assertNotIn(text, repr(value))
        with self.assertRaises(FrozenInstanceError):
            command.source.text = "replacement"

    def test_invalid_source_rejects_without_echo(self):
        for value in (None, 1, "", " \n\t", "synthetic\0tail", "\ud800", "é" * 32769):
            with self.subTest(kind=type(value).__name__), self.assertRaises(ClipboardValidationError) as caught:
                AdmittedManualText(value)
            self.assertNotIn("synthetic", str(caught.exception))
        self.assertEqual(len(AdmittedManualText("é" * 32768).text.encode("utf-8")), 65536)

    def test_invalid_command_identity_metadata_and_calendar(self):
        command = self.command()
        for changes in ({"source": "untyped"}, {"capture_method": "AUTO"}, {"source_class": "private title"},
                        {"observed_at": "2026-02-30T12:00:00.000Z"}, {"request_profile": "other"}):
            with self.subTest(fields=tuple(changes)), self.assertRaises(ClipboardValidationError):
                replace(command, **changes)
        for operation in (lambda: ClipboardOperation("bad title", str(uuid4()), str(uuid4())),
                          lambda: ClipboardOperation("synthetic", "untrusted", str(uuid4()))):
            with self.assertRaises(ClipboardValidationError):
                operation()

    def test_default_authority_unavailable_even_with_constructible_permitted_dto(self):
        service = ClipboardService(self.repository, clock=self.clock.utc, monotonic=self.clock.monotonic)
        context = service.open_admission_context("synthetic")
        command = ClipboardCaptureCommand(service.new_operation(context), AdmittedManualText("Synthetic note"))
        self.authority.authorize(ClipboardAdmissionBinding(command, "a" * 64))
        self.assert_code(Code.ADMISSION_UNAVAILABLE, service.capture_manual_text, context, command)
        self.repository._persist_admitted.assert_not_called()

    def test_incomplete_denied_unavailable_and_history_disabled_fail_before_repository(self):
        for changes in ({"assessment_complete": False}, {"sensitivity": "DENIED"},
                        {"sensitivity": "UNAVAILABLE"}, {"durable_history_authorized": False}):
            self.authority.policy = replace(SyntheticAuthority().policy, **changes)
            self.assert_code(Code.ADMISSION_DENIED, self.service.capture_manual_text, self.context, self.command())
        self.repository._persist_admitted.assert_not_called()

    def test_binding_mismatch_exact_source_operation_scope_and_profile_fails_closed(self):
        for change in ("source", "operation", "scope"):
            command = self.command()
            def bad_authorize(binding):
                changed = replace(binding.command, source=AdmittedManualText("Different synthetic text")) if change == "source" else replace(
                    binding.command, operation=replace(command.operation, operation_id=str(uuid4())))
                wrong = replace(binding, database_scope="b" * 64) if change == "scope" else replace(binding, command=changed)
                return ClipboardAdmissionDecision(wrong, self.authority.policy)
            with patch.object(self.authority, "authorize", side_effect=bad_authorize):
                self.assert_code(Code.ADMISSION_DENIED, self.service.capture_manual_text, self.context, command)
        self.repository._persist_admitted.assert_not_called()

    def test_authority_exception_is_safe_and_rejection_cannot_later_be_retried(self):
        command = self.command()
        with patch.object(self.authority, "authorize", side_effect=RuntimeError("synthetic sensitive internals")):
            error = self.assert_code(Code.ADMISSION_UNAVAILABLE, self.service.capture_manual_text, self.context, command)
        self.assertNotIn("sensitive", str(error))
        self.assert_code(Code.OPERATION_REJECTED, self.service.capture_manual_text, self.context, command)
        self.repository._persist_admitted.assert_not_called()

    def test_caller_context_uuid_cannot_activate_generation(self):
        command = self.command()
        forged = ClipboardAdmissionContext(self.context.producer_binding, self.context.ingress_generation)
        self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, forged, command)
        self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, str(uuid4()), command)
        self.repository._persist_admitted.assert_not_called()

    def test_unknown_operation_is_rejected_and_remembered(self):
        command = self.command()
        command = replace(command, operation=replace(command.operation, operation_id=str(uuid4())))
        self.assert_code(Code.OPERATION_REJECTED, self.service.capture_manual_text, self.context, command)
        self.assert_code(Code.OPERATION_REJECTED, self.service.capture_manual_text, self.context, command)
        self.assertEqual(self.authority.calls, [])

    def test_expired_context_and_restart_remain_query_only(self):
        command = self.command()
        self.clock.advance(300)
        self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, command)
        restarted = ClipboardService(self.repository, admission=self.authority, clock=self.clock.utc, monotonic=self.clock.monotonic)
        self.assert_code(Code.GENERATION_STALE, restarted.capture_manual_text, self.context, command)
        self.repository.lookup_receipt.return_value = ClipboardReceiptResult(ReplayDisposition.UNKNOWN_OR_EXPIRED)
        self.assertEqual(restarted.lookup_receipt(command.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)
        self.repository._persist_admitted.assert_not_called()

    def test_rekey_closes_old_generation(self):
        command = self.command()
        later = self.service.open_admission_context("synthetic")
        self.assertNotEqual(later.ingress_generation, self.context.ingress_generation)
        self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, command)

    def test_lease_rechecked_after_slow_assessment(self):
        command = self.command()
        def slow(binding):
            self.clock.advance(300)
            return ClipboardAdmissionDecision(binding, self.authority.policy)
        with patch.object(self.authority, "authorize", side_effect=slow):
            self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, command)
        self.repository._persist_admitted.assert_not_called()

    def test_bounded_capacity_fails_closed_without_eviction_in_live_generation(self):
        with patch("f7hub.services.clipboard_service.MAX_GENERATION_OPERATIONS", 2):
            first = self.command()
            second = self.command()
            self.assert_code(Code.CAPACITY_EXHAUSTED, self.service.new_operation, self.context)
            self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, first)
            self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, second)

    def test_rejected_unknown_operations_consume_bounded_capacity(self):
        with patch("f7hub.services.clipboard_service.MAX_GENERATION_OPERATIONS", 2):
            for _ in range(2):
                operation = ClipboardOperation("synthetic", self.context.ingress_generation, str(uuid4()))
                self.assert_code(Code.OPERATION_REJECTED, self.service.capture_manual_text, self.context,
                                 ClipboardCaptureCommand(operation, AdmittedManualText("Synthetic")))
            self.assert_code(Code.CAPACITY_EXHAUSTED, self.service.new_operation, self.context)

    def test_clock_invalid_or_monotonic_reversal_retires_admission(self):
        command = self.command()
        self.clock.elapsed -= 1
        self.assert_code(Code.CLOCK_ANOMALY, self.service.capture_manual_text, self.context, command)
        self.repository._persist_admitted.assert_not_called()

    def test_wall_clock_changes_never_extend_monotonic_lease_and_pause_cleanup(self):
        command = self.command()
        self.clock.instant -= timedelta(days=1)
        self.assert_code(Code.CLOCK_ANOMALY, self.service.maintain_receipts)
        self.clock.elapsed += 300
        self.assert_code(Code.GENERATION_STALE, self.service.capture_manual_text, self.context, command)
        self.repository._delete_expired_receipts.assert_not_called()

    def test_invalid_receipt_observations_reject_false_equality_and_fabricated_outcomes(self):
        for arguments in (
            (ReplayDisposition.SAME_OPERATION,),
            (ReplayDisposition.UNKNOWN_OR_EXPIRED, None, None, True),
            (ReplayDisposition.KNOWN_COMMITTED_SOURCE_UNAVAILABLE, None, None, False),
        ):
            with self.assertRaises(ClipboardValidationError):
                ClipboardReceiptResult(*arguments)
