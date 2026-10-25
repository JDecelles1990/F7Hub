"""Deterministic synthetic RAM-01A contracts; no native Clipboard or physical input."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from f7hub.domain import clipboard_history as history
from f7hub.domain.clipboard import ClipboardValidationError, PREVIEW_MAX_SCALARS
from f7hub.domain.clipboard_history import (
    HistoryClockSample, ClipboardHistoryUnavailable, VolatileEntryRef,
    HISTORY_BASE_BYTES, ENTRY_OVERHEAD_BYTES, MAX_HISTORY_BYTES, MAX_ENTRY_BYTES,
    HISTORY_TTL_SECONDS, MAX_DUPLICATE_COUNT,
)
from f7hub.domain.clipboard_privacy import (
    ClipboardPrivacyAssessment, ClipboardPrivacyFinding as F, ClipboardAssessmentReason as R,
)
from f7hub.domain.clipboard_history import (
    VolatileClipboardHistory, HistoryAdmissionCode as Code, VolatileAdmissionContext,
)


class SyntheticClock:
    def __init__(self):
        self.utc = datetime(2026, 10, 25, 12, tzinfo=timezone.utc)
        self.elapsed = 100.0
        self.continuous = True

    def __call__(self):
        return HistoryClockSample(self.utc, self.elapsed, self.continuous)

    def advance(self, seconds):
        self.utc += timedelta(seconds=seconds)
        self.elapsed += seconds


class SyntheticAssessor:
    """Only synthetic fixture authority; never imported by production."""

    def __init__(self):
        self.result = ClipboardPrivacyAssessment(F.PERMITTED, R.NO_RECOGNIZED_RISK)
        self.calls = 0
        self.hook = lambda: None

    def assess(self, payload):
        assert type(payload) is bytes
        self.calls += 1
        self.hook()
        return self.result


class ClipboardHistoryTests(unittest.TestCase):
    def setUp(self):
        self.clock = SyntheticClock()
        self.assessor = SyntheticAssessor()
        self.service = VolatileClipboardHistory(clock=self.clock, assessor=self.assessor)
        self.context = self.service._open_admission_context()

    def admit(self, text, service=None, context=None):
        result = (service or self.service).observe(context or self.context, text)
        self.assertEqual(result.code, Code.ADMITTED)
        return result.entry_ref

    def test_empty_history_and_disabled_start(self):
        service = VolatileClipboardHistory(clock=self.clock)
        self.assertEqual(service.list_entries(), ())
        self.assertEqual(service.accounted_bytes, HISTORY_BASE_BYTES)
        self.assertIsNone(service.clear())
        self.assertEqual(service.observe(None, 'synthetic').code, Code.STALE_OR_DISABLED)

    def test_first_entry_metadata_and_immutable_reference(self):
        ref = self.admit('Synthetic text')
        entry = self.service.get_entry(ref)
        self.assertIs(entry.ref, ref)
        self.assertEqual(entry.admitted_at, self.clock.utc)
        self.assertEqual((entry.expires_at - entry.admitted_at).total_seconds(), HISTORY_TTL_SECONDS)
        self.assertEqual((entry.utf8_bytes, entry.character_count, entry.line_count), (14, 14, 1))
        self.assertTrue(self.service.read_text(ref) == 'Synthetic text')
        with self.assertRaises(FrozenInstanceError):
            entry.duplicate_count = 10
        self.assertIsNone(self.service.get_entry(VolatileEntryRef(ref.identity)))

    def test_exactly_100_entries_and_entry_101_evicts_oldest(self):
        refs = [self.admit(f'Synthetic entry {i}') for i in range(100)]
        self.assertEqual(len(self.service.list_entries()), 100)
        self.assertIs(self.service.list_entries()[0].ref, refs[-1])
        self.admit('Synthetic entry 101')
        self.assertEqual(len(self.service.list_entries()), 100)
        self.assertIsNone(self.service.get_entry(refs[0]))
        self.assertIsNotNone(self.service.get_entry(refs[1]))

    def test_exact_12_hour_expiration_on_each_read_surface(self):
        for surface in ('list_entries', 'get_entry', 'read_text', 'accounted_bytes'):
            with self.subTest(surface=surface):
                service = VolatileClipboardHistory(clock=self.clock, assessor=self.assessor)
                context = service._open_admission_context()
                ref = self.admit('Synthetic expiry', service, context)
                self.clock.advance(HISTORY_TTL_SECONDS - 0.001)
                self.assertIsNotNone(service.get_entry(ref))
                self.clock.advance(0.001)
                value = (getattr(service, surface)(ref) if surface in ('get_entry', 'read_text')
                         else service.list_entries() if surface == 'list_entries' else service.accounted_bytes)
                self.assertEqual(value, () if surface == 'list_entries' else
                                 HISTORY_BASE_BYTES if surface == 'accounted_bytes' else None)

    def test_consecutive_duplicate_preserves_expiry_identity_and_order(self):
        ref = self.admit('Synthetic repeat')
        before = self.service.get_entry(ref)
        self.clock.advance(60)
        result = self.service.observe(self.context, 'Synthetic repeat')
        after = self.service.get_entry(ref)
        self.assertEqual(result.code, Code.DUPLICATE)
        self.assertIs(result.entry_ref, ref)
        self.assertEqual(after, replace(before, duplicate_count=1))
        self.clock.advance(HISTORY_TTL_SECONDS - 60)
        self.assertIsNone(self.service.get_entry(ref))
        self.assertEqual(len(self.service.list_entries()), 0)

    def test_duplicate_count_is_saturated(self):
        ref = self.admit('Synthetic repeat')
        store = self.service._history
        stored = store._entries[-1]
        store._entries[-1] = replace(stored, metadata=replace(stored.metadata,
                                                    duplicate_count=MAX_DUPLICATE_COUNT))
        self.assertEqual(self.service.observe(self.context, 'Synthetic repeat').code, Code.DUPLICATE)
        self.assertEqual(self.service.get_entry(ref).duplicate_count, MAX_DUPLICATE_COUNT)

    def test_only_consecutive_exact_bytes_are_duplicates(self):
        texts = ('é', 'e\u0301', 'é', 'É', 'é ', 'é\n', 'é\r\n')
        for text in texts:
            self.admit(text)
        self.assertEqual(len(self.service.list_entries()), len(texts))

    def test_original_unicode_newlines_and_safe_bounded_preview(self):
        text = 'Résumé 😀\r\nDeuxième\rTroisième\n\u202e' + 'é' * 300
        ref = self.admit(text)
        entry = self.service.get_entry(ref)
        self.assertTrue(self.service.read_text(ref) == text)
        self.assertEqual(entry.utf8_bytes, len(text.encode('utf-8')))
        self.assertEqual(entry.character_count, len(text))
        self.assertEqual(entry.line_count, 4)
        self.assertEqual(len(entry.preview), PREVIEW_MAX_SCALARS)
        self.assertTrue(entry.preview_truncated)
        self.assertFalse(any(c in entry.preview for c in '\r\n\u202e'))

    def test_invalid_and_malformed_unicode_is_rejected_before_assessment(self):
        for index, text in enumerate(('', ' \r\n', '\0', 'synthetic\0text', '\ud800', '\udfff', 12, b'text')):
            with self.subTest(profile=index):
                self.assertEqual(self.service.observe(self.context, text).code, Code.INVALID_TEXT)
        self.assertEqual(self.assessor.calls, 0)

    def test_exact_per_item_utf8_boundary_and_reject_without_truncation(self):
        text = '😀' * (MAX_ENTRY_BYTES // 4)
        ref = self.admit(text)
        self.assertEqual(self.service.get_entry(ref).utf8_bytes, MAX_ENTRY_BYTES)
        self.assertTrue(self.service.read_text(ref) == text)
        before = self.service.accounted_bytes
        self.assertEqual(self.service.observe(self.context, text + 'a').code, Code.INVALID_TEXT)
        self.assertEqual(self.service.observe(self.context, 'a' * (MAX_ENTRY_BYTES + 1)).code, Code.INVALID_TEXT)
        self.assertEqual(self.service.accounted_bytes, before)
        self.assertEqual(self.assessor.calls, 1)

    def test_accounting_includes_payload_preview_and_overhead(self):
        ref = self.admit('Synthetic accounting 😀')
        entry = self.service.get_entry(ref)
        stored = self.service._history._entries[0]
        self.assertEqual(entry.accounted_bytes, sys.getsizeof(stored.payload)
                         + sys.getsizeof(entry.preview) + ENTRY_OVERHEAD_BYTES)
        metadata_size = (sys.getsizeof(stored) + sys.getsizeof(entry) + sys.getsizeof(ref)
                         + sys.getsizeof(ref.identity) + sys.getsizeof(entry.admitted_at)
                         + sys.getsizeof(entry.expires_at) + sum(sys.getsizeof(v) for v in
                         (stored.elapsed_deadline, entry.utf8_bytes, entry.character_count,
                          entry.line_count, entry.duplicate_count, entry.accounted_bytes)))
        self.assertLess(metadata_size, ENTRY_OVERHEAD_BYTES)
        self.assertEqual(self.service.accounted_bytes, HISTORY_BASE_BYTES + entry.accounted_bytes)

    def test_exact_budget_then_oldest_eviction_and_unfit_entry_keeps_history(self):
        payload = 'x' * 1000
        cost = sys.getsizeof(payload.encode()) + sys.getsizeof('x' * PREVIEW_MAX_SCALARS) + ENTRY_OVERHEAD_BYTES
        service = VolatileClipboardHistory(clock=self.clock, assessor=self.assessor,
                                          byte_budget=HISTORY_BASE_BYTES + 2 * cost)
        context = service._open_admission_context()
        a = self.admit('a' * 1000, service, context)
        b = self.admit('b' * 1000, service, context)
        self.assertEqual(service.accounted_bytes, HISTORY_BASE_BYTES + 2 * cost)
        self.admit('c' * 1000, service, context)
        self.assertIsNone(service.get_entry(a))
        self.assertIsNotNone(service.get_entry(b))
        before = service.list_entries()
        self.assertEqual(service.observe(context, 'd' * 10000).code, Code.CAPACITY_OR_CLOCK_CHANGED)
        self.assertEqual(service.list_entries(), before)

    def test_expired_entries_removed_before_live_capacity_eviction(self):
        old = self.admit('Synthetic old')
        self.clock.advance(HISTORY_TTL_SECONDS - 1)
        young = self.admit('Synthetic young')
        self.clock.advance(1)
        new = self.admit('Synthetic new')
        self.assertIsNone(self.service.get_entry(old))
        self.assertEqual([e.ref for e in self.service.list_entries()], [new, young])

    def test_full_aggregate_budget_exhaustion_before_100_entries(self):
        first = None
        for i in range(70):
            # One retained UTF-8 payload per entry, distinct at a bounded prefix.
            ref = self.admit(f'{i:04}' + 'x' * (MAX_ENTRY_BYTES - 4))
            first = first or ref
        self.assertLess(self.service.accounted_bytes, MAX_HISTORY_BYTES)
        self.assertEqual(len(self.service.list_entries()), 63)
        self.assertIsNone(self.service.get_entry(first))

    def test_100_entry_large_markdown_load_within_limits(self):
        markdown = '# Synthetic report\n\n' + '| étape 😀 | résumé |\n' * 20000
        for i in range(100):
            self.admit(f'{i}\n' + markdown)
        self.assertEqual(len(self.service.list_entries()), 100)
        self.assertLessEqual(self.service.accounted_bytes, MAX_HISTORY_BYTES)
        newest = self.service.list_entries(1)[0]
        self.assertTrue(self.service.read_text(newest.ref) == '99\n' + markdown)
        self.assertGreater(newest.line_count, 20000)

    def test_clear_invalidates_refs_context_and_preserves_enabled_state(self):
        ref = self.admit('Synthetic clear')
        old = self.context
        self.context = self.service.clear()
        self.assertIsNone(self.service.get_entry(ref))
        self.assertIsNone(self.service.read_text(ref))
        self.assertEqual(self.service.observe(old, 'Late synthetic').code, Code.STALE_OR_DISABLED)
        self.admit('Synthetic after clear')

    def test_disable_revoke_and_reenable_cannot_reuse_context(self):
        ref = self.admit('Synthetic revoke')
        self.service.disable_and_clear()
        self.assertEqual(self.service.observe(self.context, 'Late').code, Code.STALE_OR_DISABLED)
        self.assertIsNone(self.service.get_entry(ref))
        self.assertIsNone(self.service.clear())
        self.service._open_admission_context()
        self.assertEqual(self.service.observe(self.context, 'Late').code, Code.STALE_OR_DISABLED)

    def test_late_assessment_after_concurrent_revocation(self):
        started, release = threading.Event(), threading.Event()
        results = []
        def wait_for_revocation():
            started.set()
            if not release.wait(5):
                raise RuntimeError('Synthetic synchronization deadline')
        self.assessor.hook = wait_for_revocation
        thread = threading.Thread(target=lambda: results.append(
            self.service.observe(self.context, 'Synthetic pending')), daemon=True)
        thread.start()
        try:
            self.assertTrue(started.wait(5))
            self.service.disable_and_clear()
        finally:
            release.set()
            thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(results[0].code, Code.STALE_OR_DISABLED)
        self.assertEqual(self.service.list_entries(), ())

    def test_late_assessment_after_clear_or_rekey(self):
        for action in (self.service.clear, self.service._open_admission_context):
            with self.subTest(action=action.__name__):
                self.context = self.service._open_admission_context()
                self.assessor.hook = action
                self.assertEqual(self.service.observe(self.context, 'Late synthetic').code, Code.STALE_OR_DISABLED)
                self.assertEqual(self.service.list_entries(), ())

    def test_context_cannot_be_forged_or_used_in_another_process_store(self):
        forged = VolatileAdmissionContext(self.context.epoch)
        other = VolatileClipboardHistory(clock=self.clock, assessor=self.assessor)
        self.assertEqual(self.service.observe(forged, 'Synthetic').code, Code.STALE_OR_DISABLED)
        self.assertEqual(other.observe(self.context, 'Synthetic').code, Code.STALE_OR_DISABLED)
        ref = self.admit('Synthetic identity')
        self.assertIsNone(other.get_entry(ref))

    def test_default_assessment_unavailable_and_no_permitted_call_flag(self):
        service = VolatileClipboardHistory(clock=self.clock)
        context = service._open_admission_context()
        self.assertEqual(service.observe(context, 'Synthetic').code, Code.ASSESSMENT_DENIED)
        with self.assertRaises(TypeError):
            service.observe(context, 'Synthetic', permitted=True)
        self.assertEqual(service.list_entries(), ())

    def test_complete_nonpermitted_incomplete_and_invalid_assessments_deny(self):
        for finding, reason in ((F.NEEDS_REVIEW, R.AMBIGUOUS_OR_SENSITIVE),
                                (F.POSSIBLE_SECRET, R.CREDENTIAL_SHAPE),
                                (F.INCOMPLETE, R.RESOURCE_LIMIT),
                                (F.ASSESSMENT_FAILED, R.DETECTOR_ERROR)):
            self.assessor.result = ClipboardPrivacyAssessment(finding, reason)
            self.assertEqual(self.service.observe(self.context, 'Synthetic').code, Code.ASSESSMENT_DENIED)
        self.assessor.result = 'PERMITTED'
        self.assertEqual(self.service.observe(self.context, 'Synthetic').code, Code.ASSESSMENT_DENIED)
        self.assertEqual(self.service.list_entries(), ())

    def test_failures_and_representations_are_content_free(self):
        marker = 'SyntheticPrivateMarker'
        def fail():
            raise RuntimeError(marker)
        self.assessor.hook = fail
        result = self.service.observe(self.context, marker)
        self.assertEqual(result.code, Code.ASSESSMENT_UNAVAILABLE)
        self.assertNotIn(marker, repr(result))
        self.assessor.hook = lambda: None
        ref = self.admit(marker)
        self.assertNotIn(marker, repr(self.service.get_entry(ref)))
        self.assertNotIn(marker, repr(self.service._history._entries[0]))
        with patch.object(self.service._history, '_clock', side_effect=RuntimeError(marker)):
            with self.assertRaises(ClipboardHistoryUnavailable) as caught:
                self.service.list_entries()
        self.assertNotIn(marker, str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def _assert_construction_failure_preserves_history(self, target):
        refs = [self.admit(f'Synthetic retained {i}') for i in range(100)]
        before = self.service.list_entries()
        accounted = self.service.accounted_bytes
        original = getattr(history, target)
        calls = 0
        def fail_once(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise MemoryError('SyntheticAllocationDiagnostic')
            return original(*args, **kwargs)
        with self.assertNoLogs(level='DEBUG'):
            with patch.object(history, target, side_effect=fail_once):
                result = self.service.observe(self.context, 'SyntheticIncomingPrivateMarker')
        self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
        self.assertIsNone(result.entry_ref)
        self.assertNotIn('SyntheticIncomingPrivateMarker', repr(result))
        self.assertNotIn('SyntheticAllocationDiagnostic', repr(result))
        self.assertEqual(self.service.list_entries(), before)
        self.assertEqual(self.service.accounted_bytes, accounted)
        self.assertTrue(self.service.read_text(refs[0]) == 'Synthetic retained 0')
        new = self.admit('Synthetic recovery')
        self.assertIsNone(self.service.get_entry(refs[0]))
        self.assertIs(self.service.list_entries()[0].ref, new)
        self.assertEqual(len(self.service.list_entries()), 100)

    def test_preview_memory_failure_preserves_history_and_recovers(self):
        self._assert_construction_failure_preserves_history('normalize_preview')

    def test_reference_memory_failure_preserves_history_and_recovers(self):
        self._assert_construction_failure_preserves_history('VolatileEntryRef')

    def test_metadata_stored_entry_and_result_memory_failures_are_atomic(self):
        for target in ('VolatileEntry', '_StoredEntry', 'HistoryAdmissionResult'):
            with self.subTest(target=target):
                self.context = self.service.clear()
                self._assert_construction_failure_preserves_history(target)

    def test_constructed_reference_cannot_resolve_after_failed_admission(self):
        old = self.admit('Synthetic retained')
        before = self.service.list_entries(), self.service.accounted_bytes
        pending_refs = []
        def fail(metadata, *args):
            pending_refs.append(metadata.ref)
            raise MemoryError('SyntheticPrivateDiagnostic')
        with patch.object(history, '_StoredEntry', side_effect=fail):
            result = self.service.observe(self.context, 'Synthetic unpublishable')
        self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
        self.assertIsNone(result.entry_ref)
        self.assertEqual(len(pending_refs), 1)
        self.assertIsNone(self.service.get_entry(pending_refs[0]))
        self.assertIsNone(self.service.read_text(pending_refs[0]))
        self.assertEqual((self.service.list_entries(), self.service.accounted_bytes), before)
        self.assertTrue(self.service.read_text(old) == 'Synthetic retained')
        self.admit('Synthetic recovery')

    def test_publication_list_memory_failure_never_evicts_live_history(self):
        class FailedSlice(list):
            def __getitem__(self, key):
                if isinstance(key, slice):
                    raise MemoryError('SyntheticPublicationDiagnostic')
                return super().__getitem__(key)
        cost = (sys.getsizeof(b'x' * 1000) + sys.getsizeof('x' * PREVIEW_MAX_SCALARS)
                + ENTRY_OVERHEAD_BYTES)
        for mode in ('count', 'bytes'):
            with self.subTest(mode=mode):
                budget = MAX_HISTORY_BYTES if mode == 'count' else HISTORY_BASE_BYTES + 2 * cost
                service = VolatileClipboardHistory(clock=self.clock, assessor=self.assessor,
                                                  byte_budget=budget)
                context = service._open_admission_context()
                size = 100 if mode == 'count' else 2
                refs = [self.admit(f'{i:04}' + 'x' * 996, service, context) for i in range(size)]
                before = service.list_entries(), service.accounted_bytes
                store = service._history
                with patch.object(store, '_entries', FailedSlice(store._entries)):
                    result = service.observe(context, 'y' * 1000)
                    # Inspect while the injected container is still installed.
                    self.assertEqual(tuple(e.metadata for e in reversed(store._entries)), before[0])
                    self.assertEqual(store._accounted_bytes(), before[1])
                self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
                self.assertIsNone(result.entry_ref)
                self.assertEqual((service.list_entries(), service.accounted_bytes), before)
                self.admit('y' * 1000, service, context)
                self.assertIsNone(service.get_entry(refs[0]))
                self.assertEqual(len(service.list_entries()), size)

    def test_duplicate_memory_failures_preserve_metadata_accounting_and_expiry(self):
        for target in ('replace', 'HistoryAdmissionResult'):
            with self.subTest(target=target):
                self.context = self.service.clear()
                ref = self.admit('Synthetic duplicate')
                before = self.service.get_entry(ref), self.service.accounted_bytes
                original = getattr(history, target)
                def fail(*args, **kwargs):
                    if target == 'replace' or args[0] is Code.DUPLICATE:
                        raise MemoryError('SyntheticDuplicateDiagnostic')
                    return original(*args, **kwargs)
                with patch.object(history, target, side_effect=fail):
                    result = self.service.observe(self.context, 'Synthetic duplicate')
                self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
                self.assertEqual((self.service.get_entry(ref), self.service.accounted_bytes), before)
                self.assertEqual(self.service.observe(self.context, 'Synthetic duplicate').code, Code.DUPLICATE)
                self.assertEqual(self.service.get_entry(ref), replace(before[0], duplicate_count=1))

    def test_clear_disable_and_rekey_during_construction_fence_publication(self):
        for action in (self.service.clear, self.service.disable_and_clear,
                       self.service._open_admission_context):
            for memory_failure in (False, True):
                with self.subTest(action=action.__name__, memory_failure=memory_failure):
                    self.context = self.service._open_admission_context()
                    ref = self.admit('Synthetic before invalidation')
                    original = history.normalize_preview
                    def invalidate(excerpt):
                        action()
                        if memory_failure:
                            raise MemoryError('SyntheticInvalidationDiagnostic')
                        return original(excerpt)
                    with patch.object(history, 'normalize_preview', side_effect=invalidate):
                        result = self.service.observe(self.context, 'Synthetic pending construction')
                    self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
                    self.assertIsNone(result.entry_ref)
                    self.assertEqual(self.service.list_entries(), ())
                    self.assertIsNone(self.service.read_text(ref))
                    self.assertEqual(self.service.observe(self.context, 'Late').code, Code.STALE_OR_DISABLED)

    def test_duplicate_construction_cannot_republish_after_invalidation(self):
        for action in (self.service.clear, self.service.disable_and_clear,
                       self.service._open_admission_context):
            with self.subTest(action=action.__name__):
                self.context = self.service._open_admission_context()
                ref = self.admit('Synthetic duplicate invalidation')
                original = history.replace
                invalidated = False
                def invalidate(*args, **kwargs):
                    nonlocal invalidated
                    if not invalidated:
                        invalidated = True
                        action()
                    return original(*args, **kwargs)
                with patch.object(history, 'replace', side_effect=invalidate):
                    result = self.service.observe(self.context, 'Synthetic duplicate invalidation')
                self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
                self.assertEqual(self.service.list_entries(), ())
                self.assertIsNone(self.service.read_text(ref))

    def test_construction_cancellation_propagates_without_publication(self):
        ref = self.admit('Synthetic before cancellation')
        before = self.service.list_entries(), self.service.accounted_bytes
        for target in ('normalize_preview', 'VolatileEntryRef', 'HistoryAdmissionResult'):
            with self.subTest(target=target):
                with patch.object(history, target, side_effect=KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        self.service.observe(self.context, 'Synthetic cancelled construction')
                self.assertEqual((self.service.list_entries(), self.service.accounted_bytes), before)
                self.assertIsNotNone(self.service.read_text(ref))
        self.admit('Synthetic after cancellation')

    def test_nonmemory_construction_errors_propagate_without_publication(self):
        self.admit('Synthetic before programming error')
        before = self.service.list_entries(), self.service.accounted_bytes
        for target in ('normalize_preview', 'VolatileEntryRef', 'HistoryAdmissionResult'):
            with self.subTest(target=target):
                with patch.object(history, target, side_effect=RuntimeError('Synthetic programming defect')):
                    with self.assertRaisesRegex(RuntimeError, 'Synthetic programming defect'):
                        self.service.observe(self.context, 'Synthetic programming error')
                self.assertEqual((self.service.list_entries(), self.service.accounted_bytes), before)
        self.admit('Synthetic after programming error')

    def test_memory_failure_does_not_restore_independently_expired_rows(self):
        ref = self.admit('Synthetic expiring history')
        self.clock.advance(HISTORY_TTL_SECONDS - 1)
        def expire_and_fail(excerpt):
            self.clock.advance(1)
            raise MemoryError('SyntheticExpiryDiagnostic')
        with patch.object(history, 'normalize_preview', side_effect=expire_and_fail):
            result = self.service.observe(self.context, 'Synthetic failed admission')
        self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
        self.assertEqual(self.service.list_entries(), ())
        self.assertEqual(self.service.accounted_bytes, HISTORY_BASE_BYTES)
        self.assertIsNone(self.service.read_text(ref))
        self.admit('Synthetic after expiry and failure')

    def test_clock_rollback_suspend_gap_and_continuity_loss_discard(self):
        for change in ('wall_back', 'elapsed_back', 'suspend', 'lost', 'forward_adjust'):
            with self.subTest(change=change):
                self.context = self.service._open_admission_context()
                self.clock.continuous = True
                ref = self.admit('Synthetic clock')
                if change == 'wall_back': self.clock.utc -= timedelta(seconds=1)
                if change == 'elapsed_back': self.clock.elapsed -= 1
                if change == 'suspend': self.clock.utc += timedelta(hours=13)
                if change == 'lost': self.clock.continuous = False
                if change == 'forward_adjust': self.clock.utc += timedelta(seconds=5)
                self.assertIsNone(self.service.read_text(ref))
                self.assertEqual(self.service.observe(self.context, 'Late').code, Code.STALE_OR_DISABLED)

    def test_suspend_with_both_clocks_advancing_expires_normally(self):
        ref = self.admit('Synthetic suspended')
        self.clock.advance(HISTORY_TTL_SECONDS)
        self.assertIsNone(self.service.read_text(ref))
        self.admit('Synthetic after expiry')

    def test_expiry_during_assessment_starts_new_admission_at_completion(self):
        old = self.admit('Synthetic before assessment')
        self.assessor.hook = lambda: self.clock.advance(HISTORY_TTL_SECONDS)
        ref = self.admit('Synthetic after assessment')
        self.assertIsNone(self.service.get_entry(old))
        self.assertEqual(self.service.get_entry(ref).admitted_at, self.clock.utc)

    def test_clock_failure_clears_and_fences_pending_context(self):
        ref = self.admit('Synthetic clock error')
        with patch.object(self.service._history, '_clock', return_value=HistoryClockSample(self.clock.utc, float('nan'))):
            with self.assertRaises(ClipboardHistoryUnavailable):
                self.service.list_entries()
        self.assertIsNone(self.service.get_entry(ref))
        self.assertEqual(self.service.observe(self.context, 'Late').code, Code.STALE_OR_DISABLED)

    def test_expiry_during_metadata_construction_never_publishes_entry(self):
        from f7hub.domain.clipboard import normalize_preview
        def delayed_preview(excerpt):
            self.clock.advance(HISTORY_TTL_SECONDS)
            return normalize_preview(excerpt)
        with patch('f7hub.domain.clipboard_history.normalize_preview', side_effect=delayed_preview):
            result = self.service.observe(self.context, 'Synthetic delayed construction')
        self.assertEqual(result.code, Code.CAPACITY_OR_CLOCK_CHANGED)
        self.assertEqual(self.service.list_entries(), ())

    def test_expiry_during_detail_decode_never_releases_text(self):
        ref = self.admit('Synthetic delayed read')
        original = self.service._history._find
        calls = 0
        def delayed_find(entry_ref):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.clock.advance(HISTORY_TTL_SECONDS)
            return original(entry_ref)
        with patch.object(self.service._history, '_find', side_effect=delayed_find):
            self.assertIsNone(self.service.read_text(ref))

    def test_assessment_cancellation_propagates_without_admission(self):
        def cancel():
            raise KeyboardInterrupt()
        self.assessor.hook = cancel
        with self.assertRaises(KeyboardInterrupt):
            self.service.observe(self.context, 'Synthetic cancelled')
        self.assertEqual(self.service.list_entries(), ())

    def test_invalid_limits_are_content_free(self):
        for limit in (0, 101, True, 'SyntheticPrivateMarker'):
            with self.assertRaises(ClipboardValidationError) as caught:
                self.service.list_entries(limit)
            self.assertNotIn('SyntheticPrivateMarker', str(caught.exception))
        for budget in (True, HISTORY_BASE_BYTES - 1, MAX_HISTORY_BYTES + 1):
            with self.assertRaises(ClipboardValidationError):
                VolatileClipboardHistory(byte_budget=budget)

    def test_no_file_logging_repository_or_native_dependency_and_restart_empty(self):
        source = str(Path(__file__).resolve().parents[2] / 'Python')
        program = '''
import sys, logging
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
from f7hub.domain.clipboard_history import VolatileClipboardHistory
from f7hub.domain.clipboard_privacy import ClipboardPrivacyAssessment, ClipboardPrivacyFinding as F, ClipboardAssessmentReason as R
assert not any(n.startswith(('sqlite3', 'PySide6', 'f7hub.repositories', 'ctypes')) for n in sys.modules)
class SyntheticAssessor:
    def assess(self, payload): return ClipboardPrivacyAssessment(F.PERMITTED, R.NO_RECOGNIZED_RISK)
def forbid(event, args):
    if event == 'open' and (isinstance(args[1], str) and any(c in args[1] for c in 'wax+') or isinstance(args[2], int) and args[2] & 3):
        raise AssertionError('Unexpected file write')
    if event in ('sqlite3.connect', 'subprocess.Popen', 'socket.connect'):
        raise AssertionError('Unexpected external effect')
sys.addaudithook(forbid)
with patch.object(logging.Logger, '_log', side_effect=AssertionError('Unexpected logging')):
    service = VolatileClipboardHistory(assessor=SyntheticAssessor())
    context = service._open_admission_context()
    result = service.observe(context, 'Synthetic no persistence')
    assert result.code.value == 'ADMITTED'
    assert service.read_text(result.entry_ref) == 'Synthetic no persistence'
    service.list_entries()
    service.clear()
    service.disable_and_clear()
    assert VolatileClipboardHistory().list_entries() == ()
'''
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run([sys.executable, '-B', '-c', program, source],
                                       cwd=directory, capture_output=True, text=True, timeout=20)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])
            # A separate interpreter/process also starts without entries.
            fresh = subprocess.run([sys.executable, '-B', '-c',
                "import sys; sys.path.insert(0, sys.argv[1]); from f7hub.domain.clipboard_history import VolatileClipboardHistory; assert VolatileClipboardHistory().list_entries() == ()",
                source], cwd=directory, capture_output=True, text=True, timeout=20)
            self.assertEqual(fresh.returncode, 0, fresh.stderr)


if __name__ == '__main__':
    unittest.main()
