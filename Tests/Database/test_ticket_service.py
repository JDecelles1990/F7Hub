from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import (
    TicketCreationError,
    TicketService,
    TicketValidationError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"
FIXED_TIME = datetime(2026, 9, 4, 10, 30, tzinfo=timezone(timedelta(hours=-4)))
EXPECTED_TIMESTAMP = "2026-09-04T14:30:00.000Z"


class TicketServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = TicketRepository(self.database_path)
        self.service = TicketService(
            self.repository,
            clock=lambda: FIXED_TIME,
            ticket_number_factory=lambda: "TKT-GENERATED",
        )

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_create_ticket_is_validated_normalized_and_atomic(self) -> None:
        company_id, contact_id, category_id = self._create_references()

        ticket = self.service.create_ticket(
            subject="  Cannot print  ",
            ticket_type="INCIDENT",
            priority="HIGH",
            company_id=company_id,
            contact_id=contact_id,
            category_id=category_id,
            description="  Printer reports offline.  ",
            assigned_to="  Technician One  ",
            source="  MANUAL  ",
            created_by="  Jo  ",
        )

        self.assertEqual(ticket.ticket_number, "TKT-GENERATED")
        self.assertEqual(ticket.subject, "Cannot print")
        self.assertEqual(ticket.status, "NEW")
        self.assertEqual(ticket.created_at, EXPECTED_TIMESTAMP)
        self.assertEqual(ticket.updated_at, EXPECTED_TIMESTAMP)
        self.assertEqual(ticket.description, "Printer reports offline.")
        self.assertEqual(ticket.assigned_to, "Technician One")
        self.assertEqual(ticket.source, "MANUAL")
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)

        history = self.repository.list_status_history(ticket.ticket_id)
        timeline = self.repository.list_timeline_events(ticket.ticket_id)
        self.assertEqual(len(history), 1)
        self.assertIsNone(history[0].previous_status)
        self.assertEqual(history[0].new_status, "NEW")
        self.assertEqual(history[0].reason, "Ticket created")
        self.assertEqual(history[0].changed_by, "Jo")
        self.assertEqual(history[0].changed_at, EXPECTED_TIMESTAMP)
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0].event_type, "TICKET_CREATED")
        self.assertEqual(timeline[0].title, "Ticket created")
        self.assertEqual(timeline[0].actor_label, "Jo")
        self.assertEqual(timeline[0].occurred_at, EXPECTED_TIMESTAMP)

    def test_explicit_ticket_number_is_supported(self) -> None:
        ticket = self.service.create_ticket(
            ticket_number="  INC-3001  ",
            subject="Explicit reference",
        )

        self.assertEqual(ticket.ticket_number, "INC-3001")
        self.assertEqual(self.repository.get_ticket_by_number("inc-3001"), ticket)

    def test_invalid_fields_are_rejected_before_persistence(self) -> None:
        invalid_calls = (
            {"subject": ""},
            {"subject": "   "},
            {"subject": "Valid", "ticket_number": "  "},
            {"subject": "Valid", "ticket_type": "CHANGE"},
            {"subject": "Valid", "priority": "URGENT"},
            {"subject": "Valid", "company_id": 0},
            {"subject": "Valid", "contact_id": True},
            {"subject": "Valid", "description": 42},
        )

        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(TicketValidationError):
                    self.service.create_ticket(**arguments)

        self.assertEqual(self._ticket_activity_counts(), (0, 0, 0))

    def test_invalid_and_inconsistent_references_are_rejected(self) -> None:
        company_id, contact_id, category_id = self._create_references()
        with database_connection(self.database_path) as connection:
            other_company_id = int(
                connection.execute(
                    """
                    INSERT INTO companies (name, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    ("Other", EXPECTED_TIMESTAMP, EXPECTED_TIMESTAMP),
                ).lastrowid
            )
            general_category_id = int(
                connection.execute(
                    """
                    INSERT INTO categories (
                        scope, name, slug, created_at, updated_at
                    ) VALUES ('GENERAL', ?, ?, ?, ?)
                    """,
                    ("General", "general", EXPECTED_TIMESTAMP, EXPECTED_TIMESTAMP),
                ).lastrowid
            )

        invalid_references = (
            {"company_id": 999_999},
            {"contact_id": 999_999},
            {"category_id": 999_999},
            {"company_id": other_company_id, "contact_id": contact_id},
            {"category_id": general_category_id},
        )
        for references in invalid_references:
            with self.subTest(references=references):
                with self.assertRaises(TicketValidationError):
                    self.service.create_ticket(subject="Invalid reference", **references)

        valid = self.service.create_ticket(
            subject="Valid references",
            company_id=company_id,
            contact_id=contact_id,
            category_id=category_id,
        )
        self.assertEqual(valid.company_id, company_id)

    def test_timeline_failure_rolls_back_ticket_and_status_history(self) -> None:
        with database_connection(self.database_path) as connection:
            connection.execute(
                """
                CREATE TRIGGER reject_ticket_timeline
                BEFORE INSERT ON ticket_timeline_events
                BEGIN
                    SELECT RAISE(ABORT, 'simulated timeline failure');
                END
                """
            )

        with self.assertRaisesRegex(TicketCreationError, "could not create") as caught:
            self.service.create_ticket(
                ticket_number="INC-ROLLBACK",
                subject="Must be fully rolled back",
            )

        self.assertIsInstance(caught.exception.__cause__, sqlite3.IntegrityError)
        self.assertEqual(self._ticket_activity_counts(), (0, 0, 0))
        self.assertIsNone(self.repository.get_ticket_by_number("INC-ROLLBACK"))

    def _create_references(self) -> tuple[int, int, int]:
        with database_connection(self.database_path) as connection:
            company_id = int(
                connection.execute(
                    """
                    INSERT INTO companies (name, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    ("Contoso", EXPECTED_TIMESTAMP, EXPECTED_TIMESTAMP),
                ).lastrowid
            )
            contact_id = int(
                connection.execute(
                    """
                    INSERT INTO contacts (
                        company_id, display_name, created_at, updated_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (company_id, "Casey Contact", EXPECTED_TIMESTAMP, EXPECTED_TIMESTAMP),
                ).lastrowid
            )
            category_id = int(
                connection.execute(
                    """
                    INSERT INTO categories (
                        scope, name, slug, created_at, updated_at
                    ) VALUES ('TICKET', ?, ?, ?, ?)
                    """,
                    ("Printing", "printing", EXPECTED_TIMESTAMP, EXPECTED_TIMESTAMP),
                ).lastrowid
            )
        return company_id, contact_id, category_id

    def _ticket_activity_counts(self) -> tuple[int, int, int]:
        with database_connection(self.database_path) as connection:
            return tuple(
                connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in (
                    "tickets",
                    "ticket_status_history",
                    "ticket_timeline_events",
                )
            )


if __name__ == "__main__":
    unittest.main()
