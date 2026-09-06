"""Minimal contact creation and retry safety against isolated SQLite."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.services.contact_service import ContactService, ContactCreationError, ContactValidationError
from f7hub.repositories.contact_repository import ContactRepository


class ContactServiceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "contact.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.companies = CompanyRepository(self.path)
        self.company = self.companies.create_company(name="Fabrikam Demo Systems", created_at="2026-09-06T00:00:00Z", updated_at="2026-09-06T00:00:00Z")
        self.repository = ContactRepository(self.path)
        self.service = ContactService(self.repository, self.companies)

    def test_creates_trimmed_active_contact_with_matching_utc_timestamps(self):
        before = datetime.now(timezone.utc)
        contact = self.service.create_contact(company_id=self.company.company_id, display_name=" \tAlice Example\n ")
        after = datetime.now(timezone.utc)
        self.assertEqual(contact.display_name, "Alice Example")
        self.assertEqual(contact.is_active, 1)
        self.assertEqual(contact.company_id, self.company.company_id)
        self.assertEqual(contact.created_at, contact.updated_at)
        timestamp = datetime.fromisoformat(contact.created_at.replace("Z", "+00:00"))
        self.assertLessEqual(before.replace(microsecond=before.microsecond // 1000 * 1000), timestamp)
        self.assertLessEqual(timestamp, after)
        self.assertEqual(self.repository.get_contact(contact.contact_id), contact)

    def test_rejects_empty_and_whitespace_names_without_writes(self):
        for name in ("", " ", "\t\r\n", "\u2003"):
            with self.subTest(name=name), self.assertRaises(ContactValidationError):
                self.service.create_contact(company_id=self.company.company_id, display_name=name)
        self.assertEqual(self.repository.list_contacts(), ())

    def test_rejects_nontext_names_without_writes(self):
        for name in (None, 12, True, [], {}, b"Contoso"):
            with self.subTest(name=name), self.assertRaises(ContactValidationError):
                self.service.create_contact(company_id=self.company.company_id, display_name=name)
        self.assertEqual(self.repository.list_contacts(), ())

    def test_duplicate_names_remain_allowed(self):
        first = self.service.create_contact(company_id=self.company.company_id, display_name="Bob Example")
        second = self.service.create_contact(company_id=self.company.company_id, display_name=first.display_name)
        self.assertNotEqual(first.contact_id, second.contact_id)

    def test_sqlite_write_failure_is_safe_and_leaves_no_row(self):
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER test_write_failure BEFORE INSERT ON contacts "
                               "BEGIN SELECT RAISE(ABORT, 'private failure'); END")
        with self.assertRaises(ContactCreationError) as caught:
            self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertNotIn("private failure", str(caught.exception))
        self.assertEqual(self.repository.list_contacts(), ())

    def test_reload_failure_rolls_back_insert_before_retry(self):
        with patch("f7hub.repositories.contact_repository._get_contact", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(ContactCreationError):
                self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertEqual(self.repository.list_contacts(), ())
        self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertEqual(len(self.repository.list_contacts()), 1)

    def test_missing_reload_record_rolls_back_insert(self):
        with patch("f7hub.repositories.contact_repository._get_contact", return_value=None):
            with self.assertRaises(ContactCreationError):
                self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertEqual(self.repository.list_contacts(), ())

    def test_filesystem_failure_is_translated(self):
        with patch.object(self.repository, "create_contact", side_effect=PermissionError("private path")):
            with self.assertRaises(ContactCreationError) as caught:
                self.service.create_contact(company_id=self.company.company_id, display_name="Bob Example")
        self.assertNotIn("private path", str(caught.exception))

    def test_integrity_foreign_keys_and_five_migrations(self):
        self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_invalid_company_ids_rejected_without_writes(self):
        for value in (None, True, False, 0, -1, 2**63, "1", 1.0, [], {}):
            with self.subTest(value=value), self.assertRaises(ContactValidationError):
                self.service.create_contact(company_id=value, display_name="Alice Example")
        self.assertEqual(self.repository.list_contacts(), ())

    def test_missing_and_inactive_company_rejected(self):
        with self.assertRaises(ContactValidationError):
            self.service.create_contact(company_id=999, display_name="Alice Example")
        self.companies.set_company_active(self.company.company_id, is_active=0, updated_at="2026-09-06T00:00:00Z")
        with self.assertRaises(ContactValidationError):
            self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertEqual(self.repository.list_contacts(), ())

    def test_email_trimmed_optional_and_duplicates_allowed(self):
        for value, expected in ((None, None), (" ", None), (" alice@example.invalid ", "alice@example.invalid"), (" alice@example.invalid ", "alice@example.invalid")):
            contact = self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example", email=value)
            self.assertEqual(contact.email, expected)
        self.assertEqual(len(self.repository.list_contacts()), 4)

    def test_email_nontext_rejected(self):
        for email in (1, True, [], b"alice@example.invalid"):
            with self.subTest(email=email), self.assertRaises(ContactValidationError):
                self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example", email=email)
        self.assertEqual(self.repository.list_contacts(), ())

    def test_company_read_failure_translated(self):
        with patch.object(self.companies, "get_company", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(ContactCreationError) as caught:
                self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
        self.assertNotIn("private", str(caught.exception))
        self.assertEqual(self.repository.list_contacts(), ())

    def test_validation_and_write_share_locked_transaction(self):
        original = self.companies.get_company
        def inspect(company_id, *, connection):
            self.assertTrue(connection.in_transaction)
            with database_connection(self.path, busy_timeout_ms=0) as other:
                with self.assertRaises(sqlite3.OperationalError):
                    other.execute("UPDATE companies SET is_active = 0 WHERE company_id = ?", (company_id,))
            return original(company_id, connection=connection)
        with patch.object(self.companies, "get_company", side_effect=inspect):
            self.service.create_contact(company_id=self.company.company_id, display_name="Alice Example")
