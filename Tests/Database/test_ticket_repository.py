from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.ticket_repository import TicketRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"
CREATED_AT = "2026-09-04T14:30:00.000Z"


class TicketRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = TicketRepository(self.database_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_create_and_reload_ticket_preserves_all_values(self) -> None:
        company_id, contact_id, category_id = self._create_references()

        ticket = self.repository.create_ticket(
            ticket_number="INC-2001",
            ticket_type="SERVICE_REQUEST",
            status="IN_PROGRESS",
            priority="HIGH",
            company_id=company_id,
            contact_id=contact_id,
            category_id=category_id,
            subject="Cannot access shared drive",
            description="Access stopped after a password reset.",
            resolution=None,
            assigned_to="Technician One",
            source="MANUAL",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertGreater(ticket.ticket_id, 0)
        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        self.assertEqual(self.repository.get_ticket_by_number("inc-2001"), ticket)
        self.assertEqual(ticket.company_id, company_id)
        self.assertEqual(ticket.contact_id, contact_id)
        self.assertEqual(ticket.category_id, category_id)
        self.assertEqual(ticket.ticket_type, "SERVICE_REQUEST")
        self.assertEqual(ticket.status, "IN_PROGRESS")
        self.assertEqual(ticket.priority, "HIGH")
        self.assertEqual(ticket.description, "Access stopped after a password reset.")
        self.assertEqual(ticket.assigned_to, "Technician One")
        self.assertEqual(ticket.source, "MANUAL")

    def test_missing_ticket_lookups_return_none(self) -> None:
        self.assertIsNone(self.repository.get_ticket(999_999))
        self.assertIsNone(self.repository.get_ticket_by_number("INC-MISSING"))

    def test_repository_leaves_workflow_related_records_to_service(self) -> None:
        ticket = self.repository.create_ticket(
            ticket_number="INC-2002",
            subject="Repository-only ticket",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertEqual(self.repository.list_status_history(ticket.ticket_id), ())
        self.assertEqual(self.repository.list_timeline_events(ticket.ticket_id), ())

    def test_transaction_commits_ticket_history_and_timeline_together(self) -> None:
        with self.repository.transaction() as transaction:
            ticket = transaction.create_ticket(
                ticket_number="INC-2003",
                subject="Atomic ticket",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
            history = transaction.create_status_history(
                ticket_id=ticket.ticket_id,
                previous_status=None,
                new_status="NEW",
                changed_at=CREATED_AT,
            )
            event = transaction.create_timeline_event(
                ticket_id=ticket.ticket_id,
                event_type="TICKET_CREATED",
                title="Ticket created",
                occurred_at=CREATED_AT,
            )

        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
        self.assertEqual(self.repository.list_status_history(ticket.ticket_id), (history,))
        self.assertEqual(self.repository.list_timeline_events(ticket.ticket_id), (event,))

    def test_transaction_rolls_back_every_insert_on_failure(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "simulated failure"):
            with self.repository.transaction() as transaction:
                ticket = transaction.create_ticket(
                    ticket_number="INC-ROLLBACK",
                    subject="Must roll back",
                    created_at=CREATED_AT,
                    updated_at=CREATED_AT,
                )
                transaction.create_status_history(
                    ticket_id=ticket.ticket_id,
                    previous_status=None,
                    new_status="NEW",
                    changed_at=CREATED_AT,
                )
                raise RuntimeError("simulated failure")

        self.assertIsNone(self.repository.get_ticket_by_number("INC-ROLLBACK"))
        with database_connection(self.database_path) as connection:
            counts = tuple(
                connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in (
                    "tickets",
                    "ticket_status_history",
                    "ticket_timeline_events",
                )
            )
        self.assertEqual(counts, (0, 0, 0))

    def test_constraints_and_parameter_binding_are_preserved(self) -> None:
        hostile_subject = "O'Reilly'); DROP TABLE tickets;--"
        ticket = self.repository.create_ticket(
            ticket_number="INC-2004",
            subject=hostile_subject,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.assertEqual(ticket.subject, hostile_subject)

        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create_ticket(
                ticket_number="inc-2004",
                subject="Duplicate",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create_ticket(
                ticket_number="INC-INVALID",
                subject="Invalid relationship",
                company_id=999_999,
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )

        self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)

    def _create_references(self) -> tuple[int, int, int]:
        with database_connection(self.database_path) as connection:
            company_id = int(
                connection.execute(
                    """
                    INSERT INTO companies (name, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    ("Contoso", CREATED_AT, CREATED_AT),
                ).lastrowid
            )
            contact_id = int(
                connection.execute(
                    """
                    INSERT INTO contacts (
                        company_id, display_name, created_at, updated_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (company_id, "Casey Contact", CREATED_AT, CREATED_AT),
                ).lastrowid
            )
            category_id = int(
                connection.execute(
                    """
                    INSERT INTO categories (
                        scope, name, slug, created_at, updated_at
                    ) VALUES ('TICKET', ?, ?, ?, ?)
                    """,
                    ("Access", "access", CREATED_AT, CREATED_AT),
                ).lastrowid
            )
        return company_id, contact_id, category_id


if __name__ == "__main__":
    unittest.main()
