"""Atomic D02 persistence/replay/failure/concurrency tests with synthetic text."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
import sqlite3
import threading
from unittest.mock import patch
from uuid import uuid4

from f7hub.domain.clipboard import (
    AdmittedManualText, ClipboardCaptureCommand, ClipboardAdmissionBinding, ClipboardPersistenceError,
    ClipboardPersistenceCode as Code, ReplayDisposition,
)
from f7hub.infrastructure.database import database_connection, open_database, validate_database_integrity
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.services.clipboard_service import ClipboardService
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, seed_item
from Tests.Database.test_clipboard_receipts_migration import insert_receipt
from Tests.Unit.test_clipboard_capture_contract import SyntheticAuthority, SyntheticClock
from Tests.Database.test_clipboard_consent import grant_synthetic_consent


class FaultConnection:
    """Test-owned SQLite proxy: no production fault-injection backdoor."""
    def __init__(self, connection, *, fail_table=None, commit_mode=None, rollback_failure=False, close_failure=False):
        self.connection = connection
        self.fail_table = fail_table
        self.commit_mode = commit_mode
        self.rollback_failure = rollback_failure
        self.close_failure = close_failure

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def execute(self, sql, parameters=()):
        if self.fail_table and ("INSERT INTO " + self.fail_table in sql or "UPDATE " + self.fail_table + " SET" in sql):
            raise sqlite3.OperationalError("Synthetic private SQL/source internals")
        return self.connection.execute(sql, parameters)

    def commit(self):
        if self.commit_mode == "before":
            raise sqlite3.OperationalError("Synthetic uncertain commit")
        self.connection.commit()
        if self.commit_mode == "after":
            raise sqlite3.OperationalError("Synthetic lost commit acknowledgement")

    def rollback(self):
        if self.rollback_failure:
            raise sqlite3.OperationalError("Synthetic rollback failure")
        self.connection.rollback()

    def close(self):
        self.connection.close()
        if self.close_failure:
            raise sqlite3.OperationalError("Synthetic close failure")


class ClipboardPersistenceTests(ClipboardDatabaseTestCase):
    def setUp(self):
        super().setUp()
        grant_synthetic_consent(self.database_path)
        self.clock = SyntheticClock()
        self.authority = SyntheticAuthority()
        self.repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
        self.service = ClipboardService(self.repository, admission=self.authority,
            clock=self.clock.utc, monotonic=self.clock.monotonic)
        self.context = self.service.open_admission_context("synthetic")

    def command(self, text="Synthetic exact technician note"):
        return ClipboardCaptureCommand(self.service.new_operation(self.context), AdmittedManualText(text))

    def capture(self, command=None):
        return self.service.capture_manual_text(self.context, command or self.command())

    def counts(self):
        with database_connection(self.database_path, read_only=True) as connection:
            return tuple(connection.execute("SELECT count(*) FROM " + table).fetchone()[0] for table in (
                "clipboard_items", "clipboard_capture_events", "clipboard_operation_receipts"))

    def assert_code(self, code, function, *args):
        with self.assertRaises(ClipboardPersistenceError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)
        self.assertNotIn("private", str(caught.exception))
        return caught.exception

    def test_first_capture_has_exact_item_event_receipt_and_original_policy(self):
        command = self.command("Synthetic note\r\n e\u0301 😀\n")
        result = self.capture(command)
        self.assertEqual(result.disposition, ReplayDisposition.NEW_CAPTURE)
        self.assertEqual(self.counts(), (1, 1, 1))
        outcome = result.outcome
        self.assertEqual((outcome.was_duplicate, outcome.captured_total, outcome.item_revision), (False, 1, 1))
        self.assertEqual(outcome.item_expires_at, "2026-10-22T12:00:00.000Z")
        self.assertEqual(outcome.receipt_expires_at, "2026-10-29T12:00:00.000Z")
        with database_connection(self.database_path) as connection:
            self.assertEqual(connection.execute("SELECT raw_text FROM clipboard_items").fetchone()[0], command.source.text)
            receipt = connection.execute("SELECT * FROM clipboard_operation_receipts").fetchone()
            self.assertEqual(receipt["assessment_method"], "synthetic_assessment")
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_new_genuine_operation_reuses_exact_item_increments_once_and_refreshes_temporary(self):
        first = self.capture()
        self.clock.advance(10)
        second = self.capture()
        self.assertEqual(self.counts(), (1, 2, 2))
        self.assertEqual(first.live_item_ref, second.live_item_ref)
        self.assertNotEqual(first.outcome.historical_event_id, second.outcome.historical_event_id)
        self.assertEqual((second.outcome.was_duplicate, second.outcome.captured_total, second.outcome.item_revision), (True, 2, 2))
        self.assertGreater(second.outcome.item_expires_at, first.outcome.item_expires_at)

    def test_same_operation_replay_returns_original_outcome_without_writes_or_ttl_refresh(self):
        command = self.command()
        first = self.capture(command)
        self.capture()  # Later genuine capture changes the current summary.
        self.clock.advance(20)
        before = self.database_path.read_bytes()
        replay = self.capture(command)
        self.assertEqual(replay.disposition, ReplayDisposition.SAME_OPERATION)
        self.assertEqual(replay.outcome, first.outcome)
        self.assertTrue(replay.payload_equality_verified)
        self.assertEqual(self.database_path.read_bytes(), before)
        self.assertEqual(self.counts(), (1, 2, 2))

    def test_changed_semantic_payload_is_safe_conflict_with_no_new_effects(self):
        command = self.command()
        self.capture(command)
        for changes in ({"source": AdmittedManualText("Different synthetic source")}, {"capture_method": "AHK_MANUAL"},
                        {"observed_at": "2026-10-15T11:00:00.000Z"}, {"source_class": "editor"}):
            before = self.database_path.read_bytes()
            self.assert_code(Code.OPERATION_CONFLICT, self.capture, replace(command, **changes))
            self.assertEqual(self.database_path.read_bytes(), before)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_policy_change_is_replay_conflict(self):
        command = self.command()
        self.capture(command)
        self.authority.policy = replace(self.authority.policy, policy_version="2")
        self.assert_code(Code.OPERATION_CONFLICT, self.capture, command)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_deleted_source_receipt_never_recreates_or_verifies_payload_even_after_numeric_id_reuse(self):
        command = self.command()
        first = self.capture(command)
        item_id = first.outcome.historical_item_id
        with database_connection(self.database_path) as connection:
            connection.execute("DELETE FROM clipboard_items WHERE clipboard_item_id=?", (item_id,))
            seed_item(connection, item_id=item_id, raw_text="Unrelated synthetic replacement")
        before = self.database_path.read_bytes()
        result = self.capture(replace(command, source=AdmittedManualText("Unverifiable different payload")))
        self.assertEqual(result.disposition, ReplayDisposition.KNOWN_COMMITTED_SOURCE_UNAVAILABLE)
        self.assertEqual(result.outcome, first.outcome)
        self.assertIsNone(result.live_item_ref)
        self.assertFalse(result.payload_equality_verified)
        self.assertEqual(self.database_path.read_bytes(), before)

    def test_restart_lookup_is_content_free_and_does_not_activate_old_generation(self):
        command = self.command()
        first = self.capture(command)
        restarted = ClipboardService(ClipboardRepository(self.database_path, profile_scope='b'*64), clock=self.clock.utc)
        result = restarted.lookup_receipt(command.operation)
        self.assertEqual(result.disposition, ReplayDisposition.KNOWN_COMMITTED)
        self.assertFalse(result.payload_equality_verified)
        self.assertEqual(result.outcome, first.outcome)
        self.assert_code(Code.GENERATION_STALE, restarted.capture_manual_text, self.context, command)

    def test_unknown_or_expired_lookup_never_captures_or_cleans(self):
        command = self.command()
        before = self.database_path.read_bytes()
        self.assertEqual(self.service.lookup_receipt(command.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)
        self.assertEqual(self.database_path.read_bytes(), before)
        self.capture(command)
        self.clock.advance(14 * 86400)
        before = self.database_path.read_bytes()
        self.assertEqual(self.service.lookup_receipt(command.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)
        self.assertEqual(self.database_path.read_bytes(), before)
        self.assert_code(Code.GENERATION_STALE, self.capture, command)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_forward_clock_jump_cannot_readmit_consumed_operation_even_with_live_monotonic_lease(self):
        command = self.command()
        self.capture(command)
        self.clock.instant += timedelta(days=15)
        self.assert_code(Code.GENERATION_STALE, self.capture, command)
        self.assert_code(Code.CLOCK_ANOMALY, self.service.maintain_receipts)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_backward_clock_does_not_shorten_expiry_or_last_receipt(self):
        first = self.capture()
        self.clock.instant -= timedelta(hours=1)
        second = self.capture()
        self.assertEqual(first.outcome.item_expires_at, second.outcome.item_expires_at)
        self.assertEqual(second.outcome.captured_total, 2)
        with database_connection(self.database_path) as connection:
            row = connection.execute("SELECT first_received_at, last_received_at FROM clipboard_items").fetchone()
            self.assertLess(row[0], row[1])
            self.assertEqual(row[1], first.outcome.accepted_at)
        self.assert_code(Code.CLOCK_ANOMALY, self.service.maintain_receipts)

    def test_saved_pin_and_expiry_preserved_on_genuine_capture(self):
        with database_connection(self.database_path) as connection:
            item_id = seed_item(connection, raw_text="Synthetic exact technician note", retention_intent="SAVED", expires_at=None, is_pinned=True)
        result = self.capture()
        self.assertEqual(result.outcome.historical_item_id, item_id)
        self.assertEqual((result.outcome.retention_intent, result.outcome.is_pinned, result.outcome.item_expires_at), ("SAVED", True, None))

    def test_case_space_line_endings_accents_and_trailing_newlines_remain_distinct(self):
        variants = ("Synthetic", "synthetic", " Synthetic", "Synthetic ", "Synthetic\n", "Synthetic\r\n",
                    "Synthétique", "Synthe\u0301tique", "Synthetic\ttext", "Synthetic text")
        for text in variants:
            self.assertFalse(self.capture(self.command(text)).outcome.was_duplicate)
        self.assertEqual(self.counts(), (len(variants), len(variants), len(variants)))

    def test_parameterized_text_is_data_and_same_text_in_other_database_is_independent(self):
        command = self.command("Synthetic '; DROP TABLE clipboard_items; --")
        first = self.capture(command)
        from f7hub.infrastructure.database import bootstrap_database
        from Tests.Database.clipboard_fixtures import PROJECT_ROOT
        other = self.root / "other.db"
        bootstrap_database(other, PROJECT_ROOT / "Database/Migrations")
        grant_synthetic_consent(other)
        repository = ClipboardRepository(other, profile_scope='b'*64)
        service = ClipboardService(repository, admission=self.authority, clock=self.clock.utc)
        context = service.open_admission_context("synthetic")
        result = service.capture_manual_text(context, replace(command, operation=service.new_operation(context)))
        self.assertFalse(result.outcome.was_duplicate)
        self.assertNotEqual(repository.database_scope, self.repository.database_scope)
        self.assertEqual(service.lookup_receipt(first.outcome.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)

    def test_preexisting_ambiguous_exact_items_fail_without_arbitrary_resolution(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection)
            seed_item(connection)
        before = self.counts()
        self.assert_code(Code.AMBIGUOUS_IDENTITY, self.capture, self.command("Synthetic technician note"))
        self.assertEqual(self.counts(), before)

    def test_item_event_and_receipt_write_failures_confirm_full_rollback(self):
        for table in ("clipboard_items", "clipboard_capture_events", "clipboard_operation_receipts"):
            command = self.command()
            with self.subTest(table=table), patch("f7hub.repositories.clipboard_repository.open_database",
                    side_effect=lambda path: FaultConnection(open_database(path), fail_table=table)):
                error = self.assert_code(Code.ROLLED_BACK, self.capture, command)
                self.assertTrue(error.__suppress_context__)
            self.assertEqual(self.counts(), (0, 0, 0))
        with database_connection(self.database_path) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_duplicate_update_then_event_failure_preserves_original_summary(self):
        original = self.capture()
        command = self.command()
        before = self.database_path.read_bytes()
        with patch("f7hub.repositories.clipboard_repository.open_database",
                   side_effect=lambda path: FaultConnection(open_database(path), fail_table="clipboard_capture_events")):
            self.assert_code(Code.ROLLED_BACK, self.capture, command)
        self.assertEqual(self.database_path.read_bytes(), before)
        result = self.capture(command)
        self.assertEqual(result.outcome.captured_total, original.outcome.captured_total + 1)

    def test_uncertain_commit_before_or_after_effects_requires_query_only_reconciliation(self):
        for mode in ("before", "after"):
            command = self.command("Synthetic commit " + mode)
            with self.subTest(mode=mode), patch("f7hub.repositories.clipboard_repository.open_database",
                       side_effect=lambda path: FaultConnection(open_database(path), commit_mode=mode)):
                self.assert_code(Code.UNCERTAIN, self.capture, command)
            before = self.counts()
            self.assert_code(Code.UNCERTAIN, self.capture, command)
            self.assertEqual(self.counts(), before)
            lookup = self.service.lookup_receipt(command.operation)
            self.assertEqual(lookup.disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED if mode == "before" else ReplayDisposition.KNOWN_COMMITTED)

    def test_rollback_failure_is_uncertain_and_close_releases_test_connection(self):
        command = self.command()
        with patch("f7hub.repositories.clipboard_repository.open_database", side_effect=lambda path:
                FaultConnection(open_database(path), fail_table="clipboard_capture_events", rollback_failure=True)):
            self.assert_code(Code.UNCERTAIN, self.capture, command)
        self.assertEqual(self.counts(), (0, 0, 0))
        self.assert_code(Code.UNCERTAIN, self.capture, command)
        self.assertEqual(self.service.lookup_receipt(command.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)

    def test_post_commit_cleanup_or_presentation_failure_never_claims_rollback(self):
        command = self.command()
        with patch("f7hub.repositories.clipboard_repository.open_database", side_effect=lambda path:
                   FaultConnection(open_database(path), close_failure=True)):
            committed = self.capture(command)
        def present(result):
            raise RuntimeError("Synthetic presentation failure after commit")
        with self.assertRaises(RuntimeError):
            present(committed)
        self.assertEqual(self.counts(), (1, 1, 1))
        self.assertEqual(self.service.lookup_receipt(command.operation).outcome, committed.outcome)

    def test_two_workers_same_operation_reserve_writer_and_create_once(self):
        command = self.command()
        binding = ClipboardAdmissionBinding(command, self.repository.database_scope)
        barrier = threading.Barrier(2)
        def worker():
            repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
            barrier.wait(timeout=5)
            return repository._persist_admitted(binding, self.authority.policy, accepted_at="2026-10-15T12:00:00.000Z", consent=repository._prepare_consent())
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(worker) for _ in range(2)]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual({r.disposition for r in results}, {ReplayDisposition.NEW_CAPTURE, ReplayDisposition.SAME_OPERATION})
        self.assertEqual(results[0].outcome, results[1].outcome)
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_two_genuine_concurrent_operations_same_text_create_two_events_one_item(self):
        commands = (self.command(), self.command())
        barrier = threading.Barrier(2)
        def worker(command):
            repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
            binding = ClipboardAdmissionBinding(command, repository.database_scope)
            barrier.wait(timeout=5)
            return repository._persist_admitted(binding, self.authority.policy, accepted_at="2026-10-15T12:00:00.000Z", consent=repository._prepare_consent())
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(worker, command) for command in commands]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual({r.outcome.captured_total for r in results}, {1, 2})
        self.assertEqual(self.counts(), (1, 2, 2))

    def test_concurrent_operation_conflict_has_one_winner(self):
        command = self.command()
        commands = (command, replace(command, source=AdmittedManualText("Conflicting synthetic text")))
        barrier = threading.Barrier(2)
        def worker(command):
            repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
            binding = ClipboardAdmissionBinding(command, repository.database_scope)
            barrier.wait(timeout=5)
            try:
                return repository._persist_admitted(binding, self.authority.policy, accepted_at="2026-10-15T12:00:00.000Z", consent=repository._prepare_consent()).disposition
            except ClipboardPersistenceError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(worker, command) for command in commands]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual(set(results), {ReplayDisposition.NEW_CAPTURE, Code.OPERATION_CONFLICT})
        self.assertEqual(self.counts(), (1, 1, 1))

    def test_sqlite_lock_contention_has_no_effects_and_safe_confirmed_retry(self):
        command = self.command()
        with database_connection(self.database_path) as blocker:
            self.assertEqual(blocker.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(blocker.execute("PRAGMA busy_timeout").fetchone()[0], 5000)
            blocker.execute("BEGIN IMMEDIATE")
            self.assert_code(Code.NOT_STARTED, self.capture, command)
        self.assertEqual(self.counts(), (0, 0, 0))
        self.assertEqual(self.capture(command).disposition, ReplayDisposition.NEW_CAPTURE)

    def test_explicit_cleanup_is_100_per_transaction_500_per_invocation_and_item_preserving(self):
        with database_connection(self.database_path) as connection:
            item_id = seed_item(connection)
            connection.execute("BEGIN IMMEDIATE")
            for _ in range(550):
                insert_receipt(connection, item_id)
            for _ in range(50):
                insert_receipt(connection, item_id, producer_binding=self.context.producer_binding,
                               ingress_generation=self.context.ingress_generation)
            connection.commit()
            original = tuple(connection.execute("SELECT * FROM clipboard_items").fetchone())
        # New service sampled at this date, with an active generation protected by exact binding.
        self.clock.instant += timedelta(days=20)
        service = ClipboardService(self.repository, clock=self.clock.utc, monotonic=self.clock.monotonic)
        context = service.open_admission_context("synthetic")
        with database_connection(self.database_path) as connection:
            connection.execute("UPDATE clipboard_operation_receipts SET ingress_generation=? WHERE ingress_generation=?",
                               (context.ingress_generation, self.context.ingress_generation))
        with patch.object(self.repository, "_delete_expired_receipts", wraps=self.repository._delete_expired_receipts) as batches:
            self.assertEqual(service.maintain_receipts(), 500)
            self.assertEqual(batches.call_count, 5)
        self.assertEqual(service.maintain_receipts(), 50)
        self.assertEqual(self.counts(), (1, 1, 50))
        self.clock.advance(300)
        self.assertEqual(service.maintain_receipts(), 50)
        with database_connection(self.database_path) as connection:
            self.assertEqual(tuple(connection.execute("SELECT * FROM clipboard_items").fetchone()), original)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_receipt_cleanup_does_not_prune_events_or_enable_old_capture(self):
        command = self.command()
        self.capture(command)
        self.clock.advance(14 * 86400)
        self.assertEqual(self.service.maintain_receipts(), 1)
        self.assertEqual(self.counts(), (1, 1, 0))
        self.assert_code(Code.GENERATION_STALE, self.capture, command)
        self.assertEqual(self.service.lookup_receipt(command.operation).disposition, ReplayDisposition.UNKNOWN_OR_EXPIRED)

    def test_lookup_failure_is_safe_and_does_not_create_database(self):
        command = self.command()
        absent = ClipboardRepository(self.root / "absent" / "missing.db")
        self.assert_code(Code.LOOKUP_UNAVAILABLE, lambda: absent.lookup_receipt(command.operation, as_of="2026-10-15T12:00:00.000Z"))
        self.assertFalse((self.root / "absent").exists())
