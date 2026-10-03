"""Atomic classification updates using real SQLite transactions and failure points."""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.ticket_repository import TicketRepository, TicketRepositoryTransaction
from f7hub.services.ticket_service import (
    TicketService, TicketValidationError, TicketNotFoundError,
    TicketEditConflictError, TicketUpdateError, TICKET_PRIORITIES, TICKET_TYPES,
)


class TicketClassificationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "classification.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repo = TicketRepository(self.path)
        self.service = TicketService(self.repo, clock=lambda: datetime(2026, 10, 3, tzinfo=timezone.utc))
        self.ticket = self.service.create_ticket(subject="Synthetic ticket", priority="HIGH")
        self.events = self.repo.list_timeline_events(self.ticket.ticket_id)

    def values(self, **overrides):
        values = dict(expected_priority=self.ticket.priority,
                      expected_ticket_type=self.ticket.ticket_type,
                      expected_updated_at=self.ticket.updated_at,
                      priority="MEDIUM", ticket_type="TASK")
        values.update(overrides)
        return values

    def apply(self, **overrides):
        return self.service.update_ticket_classification(self.ticket.ticket_id, **self.values(**overrides))

    def unchanged(self):
        self.assertEqual(self.repo.get_ticket(self.ticket.ticket_id), self.ticket)
        self.assertEqual(self.repo.list_timeline_events(self.ticket.ticket_id), self.events)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_invalid_ids_and_choices_are_rejected_before_repository_access(self):
        with patch.object(self.repo, "transaction", side_effect=AssertionError("Must validate first")):
            for ticket_id in (None, True, 0, -1, "1", 1.5):
                with self.subTest(ticket_id=ticket_id), self.assertRaises(TicketValidationError):
                    self.service.update_ticket_classification(ticket_id, **self.values())
            for field in ("priority", "ticket_type", "expected_priority", "expected_ticket_type", "expected_updated_at"):
                for value in (None, True, "", " ", "INVALID"):
                    if field == "expected_updated_at" and value == "INVALID":
                        continue  # Existing timestamp input contract requires nonempty text.
                    with self.subTest(field=field, value=value), self.assertRaises(TicketValidationError):
                        self.apply(**{field: value})
        self.unchanged()

    def test_missing_ticket(self):
        with self.assertRaises(TicketNotFoundError):
            self.service.update_ticket_classification(999999, **self.values())
        self.unchanged()

    def test_each_stale_guard_precedes_noop(self):
        for field, value in (("expected_priority", "LOW"), ("expected_ticket_type", "PROBLEM"),
                             ("expected_updated_at", "2026-10-02T00:00:00.000Z")):
            with self.subTest(field=field), self.assertRaises(TicketEditConflictError):
                self.apply(priority=self.ticket.priority, ticket_type=self.ticket.ticket_type, **{field: value})
            self.unchanged()

    def test_noop_performs_zero_writes_and_events(self):
        statements = []
        original = TicketRepositoryTransaction.get_ticket

        def traced(transaction, ticket_id):
            transaction._connection.set_trace_callback(statements.append)
            return original(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", traced):
            result = self.apply(priority=self.ticket.priority, ticket_type=self.ticket.ticket_type)
        self.assertEqual(result, self.ticket)
        self.assertFalse(any(s.lstrip().upper().startswith(("UPDATE", "INSERT", "DELETE")) for s in statements))
        self.unchanged()

    def test_priority_only_type_only_and_both_change_with_exact_events(self):
        for priority, ticket_type, kinds in (("MEDIUM", "INCIDENT", ["PRIORITY_CHANGED"]),
                                           ("MEDIUM", "TASK", ["TYPE_CHANGED"]),
                                           ("LOW", "PROBLEM", ["PRIORITY_CHANGED", "TYPE_CHANGED"])):
            with self.subTest(priority=priority, ticket_type=ticket_type):
                current = self.repo.get_ticket(self.ticket.ticket_id)
                before = len(self.repo.list_timeline_events(current.ticket_id))
                result = self.apply(expected_priority=current.priority, expected_ticket_type=current.ticket_type,
                                    expected_updated_at=current.updated_at, priority=priority, ticket_type=ticket_type)
                self.assertGreater(result.updated_at, current.updated_at)
                self.assertEqual(result, replace(current, priority=priority, ticket_type=ticket_type,
                                                 updated_at=result.updated_at))
                events = self.repo.list_timeline_events(current.ticket_id)[before:]
                self.assertEqual([e.event_type for e in events], kinds)
                self.assertTrue(all(e.occurred_at == result.updated_at and e.details is None and e.metadata_json is None for e in events))
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_all_authoritative_values_supported(self):
        for priority in sorted(TICKET_PRIORITIES):
            for ticket_type in TICKET_TYPES:
                current = self.repo.get_ticket(self.ticket.ticket_id)
                result = self.apply(expected_priority=current.priority, expected_ticket_type=current.ticket_type,
                                    expected_updated_at=current.updated_at, priority=priority, ticket_type=ticket_type)
                self.assertEqual((result.priority, result.ticket_type), (priority, ticket_type))

    def test_guarded_update_failure_rolls_back_even_after_write(self):
        original = TicketRepositoryTransaction.update_ticket_classification

        def failed(transaction, *args, **kwargs):
            self.assertTrue(original(transaction, *args, **kwargs))
            return False

        with patch.object(TicketRepositoryTransaction, "update_ticket_classification", failed):
            with self.assertRaises(TicketEditConflictError):
                self.apply()
        self.unchanged()

    def test_first_and_second_event_failure_roll_back_both_fields(self):
        for kind in ("PRIORITY_CHANGED", "TYPE_CHANGED"):
            with self.subTest(event=kind):
                with database_connection(self.path) as connection:
                    connection.execute(
                        "CREATE TRIGGER reject_event BEFORE INSERT ON ticket_timeline_events "
                        f"WHEN NEW.event_type = '{kind}' BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END"
                    )
                with self.assertRaises(TicketUpdateError):
                    self.apply()
                self.unchanged()
                with database_connection(self.path) as connection:
                    connection.execute("DROP TRIGGER reject_event")

    def test_failed_authoritative_reload_rolls_back_update_and_events(self):
        original = TicketRepositoryTransaction.get_ticket
        for failure in (None, sqlite3.OperationalError("synthetic read failure")):
            count = 0

            def failed(transaction, ticket_id):
                nonlocal count
                count += 1
                if count == 2:
                    if isinstance(failure, Exception):
                        raise failure
                    return None
                return original(transaction, ticket_id)

            with self.subTest(failure=failure), patch.object(TicketRepositoryTransaction, "get_ticket", failed):
                with self.assertRaises(TicketUpdateError):
                    self.apply()
            self.unchanged()

    def test_repository_guards_each_expected_value_and_changes_only_requested_columns(self):
        for field, value in (("expected_priority", "LOW"), ("expected_ticket_type", "TASK"),
                             ("expected_updated_at", "stale")):
            with self.subTest(field=field), self.repo.transaction() as transaction:
                self.assertFalse(transaction.update_ticket_classification(
                    self.ticket.ticket_id, **self.values(**{field: value}), updated_at="new time"))
            self.unchanged()
        # Updating unchanged type would fire this trigger; priority-only must avoid it.
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_type_column BEFORE UPDATE OF ticket_type ON tickets "
                               "BEGIN SELECT RAISE(ABORT, 'type must be untouched'); END")
        self.apply(ticket_type=self.ticket.ticket_type)
