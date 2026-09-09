"""Synthetic category reads, validation, history and database integrity."""

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_reference_service import TicketReferenceService, TicketReferenceError
from f7hub.services.ticket_service import TicketService, TicketValidationError


def seed_categories(path):
    """IDs intentionally differ from display order; all records are synthetic."""
    rows = (
        (31, "TICKET", "Networking", 1, 20),
        (12, "TICKET", "Microsoft 365", 1, 10),
        (23, "TICKET", "Hardware", 1, 10),
        (44, "TICKET", "Legacy Test Category", 0, 0),
        (55, "KNOWLEDGE", "Outlook KB", 1, 0),
        (66, "SCRIPT", "PowerShell Test", 1, 0),
        (77, "DIAGNOSTIC", "Diagnostic Test", 1, 0),
    )
    with database_connection(path) as connection:
        connection.executemany(
            "INSERT INTO categories (category_id, scope, name, is_active, sort_order, slug, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*row, f"synthetic-{row[0]}", "2026-09-05T12:00:00Z", "2026-09-05T12:00:00Z") for row in rows],
        )


class CategoryReferenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "categories.db"
        self.migrations = Path(__file__).resolve().parents[2] / "Database/Migrations"
        bootstrap_database(self.path, self.migrations)
        self.categories = CategoryRepository(self.path)
        self.references = TicketReferenceService(CompanyRepository(self.path), ContactRepository(self.path), self.categories)
        self.tickets = TicketRepository(self.path)
        self.service = TicketService(self.tickets)

    def test_empty_categories(self):
        self.assertEqual(self.categories.list_categories(scope="TICKET", active_only=True), ())
        self.assertEqual(self.references.list_active_ticket_categories(), ())

    def test_scope_active_filter_and_sort_order(self):
        seed_categories(self.path)
        self.assertEqual([r.category_id for r in self.categories.list_categories(scope="TICKET", active_only=True)], [23, 12, 31])
        self.assertEqual([r.category_id for r in self.categories.list_categories(scope="TICKET")], [44, 23, 12, 31])
        self.assertEqual([r.category_id for r in self.categories.list_categories(scope="KNOWLEDGE", active_only=True)], [55])

    def test_name_ties_are_case_insensitive_and_ordered_by_id(self):
        seed_categories(self.path)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE categories SET name = ?, sort_order = ? WHERE category_id IN (?, ?)",
                               ("hardware", 10, 12, 31))
        self.assertEqual([r.category_id for r in self.categories.list_categories(scope="TICKET", active_only=True)], [12, 23, 31])

    def test_sql_looking_scope_is_data(self):
        seed_categories(self.path)
        self.assertEqual(self.categories.list_categories(scope="TICKET' OR 1=1 --", active_only=True), ())
        self.assertEqual(len(self.categories.list_categories(scope="TICKET", active_only=True)), 3)

    def test_reference_options_enforce_ticket_scope_and_keep_ids_separate(self):
        seed_categories(self.path)
        with patch.object(self.categories, "list_categories", wraps=self.categories.list_categories) as query:
            options = self.references.list_active_ticket_categories()
        query.assert_called_once_with(scope="TICKET", active_only=True)
        self.assertEqual([(o.reference_id, o.label) for o in options], [(23, "Hardware"), (12, "Microsoft 365"), (31, "Networking")])

    def test_reference_errors_are_safe(self):
        with patch.object(self.categories, "list_categories", side_effect=sqlite3.OperationalError("private database path")):
            with self.assertRaisesRegex(TicketReferenceError, "^Could not load ticket categories.$"):
                self.references.list_active_ticket_categories()

    def test_active_and_null_categories_commit_ticket_history_and_timeline(self):
        seed_categories(self.path)
        for category_id in (23, 12, 31, None):
            ticket = self.service.create_ticket(subject="Synthetic category ticket", category_id=category_id)
            details = self.tickets.get_ticket_details(ticket.ticket_id)
            self.assertEqual(details.ticket.category_id, category_id)
            self.assertEqual(len(details.status_history), 1)
            self.assertEqual(len(details.timeline_events), 1)

    def test_invalid_categories_leave_no_partial_rows(self):
        seed_categories(self.path)
        for category_id in (44, 55, 66, 77, 999):
            with self.subTest(category_id=category_id):
                with self.assertRaises(TicketValidationError):
                    self.service.create_ticket(subject="Invalid reference", category_id=category_id)
                with database_connection(self.path) as connection:
                    for table in ("tickets", "ticket_status_history", "ticket_timeline_events"):
                        self.assertEqual(connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0], 0)

    def test_current_inactive_and_deleted_category_labels(self):
        seed_categories(self.path)
        ticket = self.service.create_ticket(subject="Historical category", category_id=31)
        self.assertEqual(self.tickets.get_ticket_details(ticket.ticket_id).category_name, "Networking")
        with database_connection(self.path) as connection:
            connection.execute("UPDATE categories SET is_active = 0, name = ? WHERE category_id = ?", ("Networking Test Renamed", 31))
        self.assertEqual(self.tickets.get_ticket_details(ticket.ticket_id).category_name, "Networking Test Renamed")
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM categories WHERE category_id = ?", (31,))
        details = self.tickets.get_ticket_details(ticket.ticket_id)
        self.assertIsNone(details.category_name)
        self.assertIsNone(details.ticket.category_id)

    def test_fresh_bootstrap_integrity_and_unchanged_migration_count(self):
        seed_categories(self.path)
        self.service.create_ticket(subject="Integrity test", category_id=31)
        bootstrap_database(self.path, self.migrations)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)
