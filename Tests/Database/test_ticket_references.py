"""Reference reads, creation validation and historical detail snapshots."""

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRepository
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_reference_service import (
    CompanyReferenceUnavailableError, TicketReferenceService, TicketReferenceError,
)
from f7hub.services.ticket_service import TicketService, TicketValidationError


def seed_references(path):
    """Synthetic companies with distinct, inactive and empty contact sets."""
    companies, contacts = CompanyRepository(path), ContactRepository(path)
    timestamps = dict(created_at="2026-09-05T12:00:00Z", updated_at="2026-09-05T12:00:00Z")
    a = companies.create_company(name="Northwind Support Labs", **timestamps)
    b = companies.create_company(name="Contoso Test Services", **timestamps)
    empty = companies.create_company(name="Empty Test Company", **timestamps)
    inactive = companies.create_company(name="Inactive Test Company", is_active=0, **timestamps)
    alice = contacts.create_contact(display_name="Alice Example", company_id=a.company_id, **timestamps)
    bob = contacts.create_contact(display_name="Bob Example", company_id=a.company_id, is_active=0, **timestamps)
    charlie = contacts.create_contact(display_name="Charlie Example", company_id=b.company_id, **timestamps)
    return a, b, empty, inactive, alice, bob, charlie


class TicketReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "references.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.companies, self.contacts = CompanyRepository(self.path), ContactRepository(self.path)
        self.references = TicketReferenceService(self.companies, self.contacts, CategoryRepository(self.path))
        self.repository = TicketRepository(self.path)
        self.service = TicketService(self.repository)

    def test_empty_companies(self):
        self.assertEqual(self.references.list_active_companies(), ())

    def test_active_choices_are_ordered_and_filtered_by_company(self):
        a, b, empty, inactive, alice, bob, charlie = seed_references(self.path)
        self.assertEqual([o.reference_id for o in self.references.list_active_companies()],
                         [b.company_id, empty.company_id, a.company_id])
        self.assertEqual([(o.reference_id, o.label) for o in self.references.list_active_contacts_for_company(a.company_id)],
                         [(alice.contact_id, "Alice Example")])
        self.assertEqual([o.reference_id for o in self.references.list_active_contacts_for_company(b.company_id)],
                         [charlie.contact_id])
        self.assertEqual(self.references.list_active_contacts_for_company(empty.company_id), ())

    def test_invalid_and_inactive_company_reads(self):
        inactive = seed_references(self.path)[3]
        for value in (None, True, 0, -1, "1", 2**64, 999999, inactive.company_id):
            with self.subTest(value=value), self.assertRaises(TicketReferenceError):
                self.references.list_active_contacts_for_company(value)

    def test_query_errors_are_translated(self):
        a = seed_references(self.path)[0]
        for repository, method, operation in (
            (self.companies, "list_companies", self.references.list_active_companies),
            (self.contacts, "list_contacts_for_company",
             lambda: self.references.list_active_contacts_for_company(a.company_id)),
        ):
            with patch.object(repository, method, side_effect=sqlite3.OperationalError("private detail")):
                with self.assertRaises(TicketReferenceError) as caught:
                    operation()
                self.assertNotIn("private detail", str(caught.exception))
                self.assertNotIsInstance(caught.exception, CompanyReferenceUnavailableError)

    def test_unavailable_company_has_typed_error_but_read_failure_does_not(self):
        a, _, _, inactive, *_ = seed_references(self.path)
        for company_id in (inactive.company_id, 999999):
            with self.subTest(company_id=company_id), self.assertRaises(CompanyReferenceUnavailableError):
                self.references.list_active_contacts_for_company(company_id)
        with patch.object(self.companies, "get_company", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketReferenceError) as caught:
                self.references.list_active_contacts_for_company(a.company_id)
            self.assertNotIsInstance(caught.exception, CompanyReferenceUnavailableError)
            self.assertNotIn("private", str(caught.exception))

    def test_invalid_inactive_and_mismatched_references_write_nothing(self):
        a, b, empty, inactive, alice, bob, charlie = seed_references(self.path)
        for values in (
            dict(company_id=999999), dict(contact_id=999999), dict(company_id=2**64),
            dict(company_id=inactive.company_id), dict(company_id=a.company_id, contact_id=bob.contact_id),
            dict(company_id=a.company_id, contact_id=charlie.contact_id),
        ):
            with self.subTest(values=values), self.assertRaises(TicketValidationError):
                self.service.create_ticket(subject="Rejected draft", **values)
        with database_connection(self.path) as connection:
            for table in ("tickets", "ticket_status_history", "ticket_timeline_events"):
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_contact_detached_after_selection_is_rejected(self):
        a, _, _, _, alice, _, _ = seed_references(self.path)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE contacts SET company_id = NULL WHERE contact_id = ?", (alice.contact_id,))
        with self.assertRaises(TicketValidationError):
            self.service.create_ticket(subject="Detached", company_id=a.company_id, contact_id=alice.contact_id)

    def test_deleted_and_deactivated_selections_are_rechecked_on_save(self):
        a, _, _, _, alice, _, _ = seed_references(self.path)
        self.references.list_active_contacts_for_company(a.company_id)
        self.contacts.set_contact_active(alice.contact_id, is_active=0, updated_at="later")
        with self.assertRaises(TicketValidationError):
            self.service.create_ticket(subject="Stale", company_id=a.company_id, contact_id=alice.contact_id)
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM contacts WHERE contact_id = ?", (alice.contact_id,))
            connection.execute("DELETE FROM companies WHERE company_id = ?", (a.company_id,))
        for values in (dict(company_id=a.company_id), dict(contact_id=alice.contact_id)):
            with self.assertRaises(TicketValidationError):
                self.service.create_ticket(subject="Deleted", **values)

    def test_historical_names_survive_inactivation_and_deletion_is_safe(self):
        a, _, _, _, alice, _, _ = seed_references(self.path)
        ticket = self.service.create_ticket(subject="History", company_id=a.company_id, contact_id=alice.contact_id)
        self.companies.set_company_active(a.company_id, is_active=0, updated_at="later")
        self.contacts.set_contact_active(alice.contact_id, is_active=0, updated_at="later")
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertEqual((details.company_name, details.contact_name), (a.name, alice.display_name))
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM contacts WHERE contact_id = ?", (alice.contact_id,))
            connection.execute("DELETE FROM companies WHERE company_id = ?", (a.company_id,))
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertIsNone(details.company_name)
        self.assertIsNone(details.contact_name)
        self.assertIsNone(details.ticket.company_id)
        self.assertIsNone(details.ticket.contact_id)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_optional_references_remain_supported(self):
        a = seed_references(self.path)[0]
        for values in ({}, dict(company_id=a.company_id)):
            ticket = self.service.create_ticket(subject="Optional", **values)
            self.assertIsNone(ticket.contact_id)
