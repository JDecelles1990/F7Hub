from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import (
    bootstrap_database,
    database_connection,
    validate_database_integrity,
)
from f7hub.repositories import TicketNoteRecord, TicketRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"
CREATED_AT = "2026-09-04T14:30:00.000Z"
UPDATED_AT = "2026-09-04T15:30:00.000Z"


class TicketActivityRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.database_path = Path(temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = TicketRepository(self.database_path)
        self.ticket = self.repository.create_ticket(
            ticket_number="INC-ACTIVITY-1",
            ticket_type="SERVICE_REQUEST",
            subject="Cannot connect to shared drive",
            description="Access stopped after a password reset.",
            priority="HIGH",
            assigned_to="Technician One",
            source="MANUAL",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

    def tearDown(self) -> None:
        with database_connection(self.database_path) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_note_roundtrip_preserves_all_metadata_and_parameter_values(self) -> None:
        text = "O'Reilly'); DROP TABLE tickets;--\nReconnected the shared drive."
        with self.repository.transaction() as transaction:
            note = transaction.create_note(
                ticket_id=self.ticket.ticket_id,
                note_type="WORKLOG",
                note_text=text,
                author_label="Technician O'Reilly",
                source="MANUAL'); DELETE FROM ticket_notes;--",
                is_ai_generated=True,
                created_at=CREATED_AT,
                updated_at=UPDATED_AT,
            )

        expected = TicketNoteRecord(
            ticket_note_id=note.ticket_note_id,
            ticket_id=self.ticket.ticket_id,
            note_type="WORKLOG",
            note_text=text,
            author_label="Technician O'Reilly",
            source="MANUAL'); DELETE FROM ticket_notes;--",
            is_ai_generated=True,
            created_at=CREATED_AT,
            updated_at=UPDATED_AT,
        )
        self.assertGreater(note.ticket_note_id, 0)
        self.assertEqual(note, expected)
        reloaded = self.repository.get_note(note.ticket_note_id)
        self.assertEqual(reloaded, expected)
        self.assertIs(reloaded.is_ai_generated, True)
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), self.ticket)
        self.assertEqual(self.repository.list_status_history(self.ticket.ticket_id), ())
        self.assertEqual(self.repository.list_timeline_events(self.ticket.ticket_id), ())

    def test_note_defaults_are_persisted(self) -> None:
        with self.repository.transaction() as transaction:
            note = transaction.create_note(
                ticket_id=self.ticket.ticket_id,
                note_text="Technician note",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
        self.assertEqual(self.repository.get_note(note.ticket_note_id), note)
        self.assertEqual(note.note_type, "INTERNAL")
        self.assertIsNone(note.author_label)
        self.assertIsNone(note.source)
        self.assertIs(note.is_ai_generated, False)

    def test_note_list_filters_ticket_and_has_stable_chronological_order(self) -> None:
        other_ticket = self.repository.create_ticket(
            ticket_number="INC-ACTIVITY-2",
            subject="Other ticket",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        with self.repository.transaction() as transaction:
            later = transaction.create_note(
                ticket_id=self.ticket.ticket_id,
                note_text="Later timestamp, inserted first",
                created_at=UPDATED_AT,
                updated_at=UPDATED_AT,
            )
            earlier = transaction.create_note(
                ticket_id=self.ticket.ticket_id,
                note_text="Earlier timestamp",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
            same_time = transaction.create_note(
                ticket_id=self.ticket.ticket_id,
                note_text="Same timestamp, higher note ID",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
            unrelated = transaction.create_note(
                ticket_id=other_ticket.ticket_id,
                note_text="Other ticket's note",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
        self.assertEqual(
            self.repository.list_notes(self.ticket.ticket_id),
            (earlier, same_time, later),
        )
        self.assertEqual(self.repository.list_notes(other_ticket.ticket_id), (unrelated,))

    def test_missing_note_ticket_and_updates_return_empty_results(self) -> None:
        self.assertIsNone(self.repository.get_note(999_999))
        self.assertEqual(self.repository.list_notes(999_999), ())
        with self.repository.transaction() as transaction:
            self.assertIsNone(transaction.get_ticket(999_999))
            self.assertIsNone(
                transaction.update_ticket_activity(999_999, updated_at=UPDATED_AT)
            )
            self.assertIsNone(
                transaction.update_ticket_status(
                    999_999,
                    status="OPEN",
                    resolution=None,
                    resolved_at=None,
                    closed_at=None,
                    updated_at=UPDATED_AT,
                )
            )

    def test_transaction_get_ticket_reads_its_own_uncommitted_insert(self) -> None:
        with self.repository.transaction() as transaction:
            ticket = transaction.create_ticket(
                ticket_number="INC-TRANSACTION-READ",
                subject="Uncommitted ticket",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
            self.assertEqual(transaction.get_ticket(ticket.ticket_id), ticket)
            self.assertIsNone(self.repository.get_ticket(ticket.ticket_id))
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)

    def test_activity_timestamp_update_preserves_other_ticket_fields(self) -> None:
        with self.repository.transaction() as transaction:
            result = transaction.update_ticket_activity(
                self.ticket.ticket_id,
                updated_at=UPDATED_AT,
            )
        expected = replace(self.ticket, updated_at=UPDATED_AT)
        self.assertEqual(result, expected)
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), expected)

    def test_status_update_reloads_lifecycle_fields_and_preserves_other_fields(self) -> None:
        resolution = "Replaced O'Reilly's cable'); DROP TABLE tickets;--"
        with self.repository.transaction() as transaction:
            result = transaction.update_ticket_status(
                self.ticket.ticket_id,
                status="CLOSED",
                resolution=resolution,
                resolved_at=CREATED_AT,
                closed_at=UPDATED_AT,
                updated_at=UPDATED_AT,
            )
            self.assertEqual(transaction.get_ticket(self.ticket.ticket_id), result)
        expected = replace(
            self.ticket,
            status="CLOSED",
            resolution=resolution,
            resolved_at=CREATED_AT,
            closed_at=UPDATED_AT,
            updated_at=UPDATED_AT,
        )
        self.assertEqual(result, expected)
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), expected)
        self.assertEqual(self.repository.list_status_history(self.ticket.ticket_id), ())
        self.assertEqual(self.repository.list_timeline_events(self.ticket.ticket_id), ())

        with self.repository.transaction() as transaction:
            reopened = transaction.update_ticket_status(
                self.ticket.ticket_id,
                status="OPEN",
                resolution=None,
                resolved_at=None,
                closed_at=None,
                updated_at=UPDATED_AT,
            )
        self.assertEqual(reopened, replace(self.ticket, status="OPEN", updated_at=UPDATED_AT))
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), reopened)

    def test_note_and_ticket_status_roll_back_together_on_failure(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "simulated activity failure"):
            with self.repository.transaction() as transaction:
                note = transaction.create_note(
                    ticket_id=self.ticket.ticket_id,
                    note_text="Must be rolled back",
                    created_at=UPDATED_AT,
                    updated_at=UPDATED_AT,
                )
                transaction.update_ticket_status(
                    self.ticket.ticket_id,
                    status="RESOLVED",
                    resolution="Reconnected",
                    resolved_at=UPDATED_AT,
                    closed_at=None,
                    updated_at=UPDATED_AT,
                )
                raise RuntimeError("simulated activity failure")
        self.assertIsNone(self.repository.get_note(note.ticket_note_id))
        self.assertEqual(self.repository.list_notes(self.ticket.ticket_id), ())
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), self.ticket)

    def test_note_constraints_and_foreign_keys_are_enforced(self) -> None:
        invalid_values = (
            {"note_text": "   "},
            {"note_type": "INVALID"},
            {"ticket_id": 999_999},
            {"is_ai_generated": 2},
        )
        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                parameters = {
                    "ticket_id": self.ticket.ticket_id,
                    "note_text": "Valid note",
                    "created_at": CREATED_AT,
                    "updated_at": CREATED_AT,
                }
                parameters.update(invalid_value)
                with self.assertRaises(sqlite3.IntegrityError):
                    with self.repository.transaction() as transaction:
                        transaction.update_ticket_activity(
                            self.ticket.ticket_id,
                            updated_at=UPDATED_AT,
                        )
                        transaction.create_note(**parameters)
                self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), self.ticket)
        self.assertEqual(self.repository.list_notes(self.ticket.ticket_id), ())

    def test_status_and_lifecycle_constraints_reject_invalid_updates(self) -> None:
        invalid_values = (
            {"status": "INVALID"},
            {"status": "OPEN", "resolved_at": UPDATED_AT},
            {"status": "RESOLVED", "closed_at": UPDATED_AT},
        )
        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                parameters = {
                    "status": "OPEN",
                    "resolution": None,
                    "resolved_at": None,
                    "closed_at": None,
                    "updated_at": UPDATED_AT,
                }
                parameters.update(invalid_value)
                with self.assertRaises(sqlite3.IntegrityError):
                    with self.repository.transaction() as transaction:
                        transaction.update_ticket_status(self.ticket.ticket_id, **parameters)
                self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id), self.ticket)

    def test_transaction_reserves_writer_before_reading_current_state(self) -> None:
        with self.repository.transaction() as transaction:
            with database_connection(self.database_path, busy_timeout_ms=0) as competing:
                with self.assertRaises(sqlite3.OperationalError) as raised:
                    competing.execute("BEGIN IMMEDIATE")
                self.assertEqual(raised.exception.sqlite_errorcode, sqlite3.SQLITE_BUSY)
            self.assertEqual(transaction.get_ticket(self.ticket.ticket_id), self.ticket)
        with database_connection(self.database_path, busy_timeout_ms=0) as competing:
            competing.execute("BEGIN IMMEDIATE")
            competing.rollback()


if __name__ == "__main__":
    unittest.main()
