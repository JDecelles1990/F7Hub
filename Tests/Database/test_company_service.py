"""Minimal company creation and retry safety against isolated SQLite."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.services.company_service import CompanyService, CompanyCreationError, CompanyValidationError


class CompanyServiceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "company.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repository = CompanyRepository(self.path)
        self.service = CompanyService(self.repository)

    def test_creates_trimmed_active_company_with_matching_utc_timestamps(self):
        before = datetime.now(timezone.utc)
        company = self.service.create_company(name=" \tNorthwind Field Services\n ")
        after = datetime.now(timezone.utc)
        self.assertEqual(company.name, "Northwind Field Services")
        self.assertEqual(company.is_active, 1)
        self.assertIsNone(company.company_code)
        self.assertEqual(company.created_at, company.updated_at)
        timestamp = datetime.fromisoformat(company.created_at.replace("Z", "+00:00"))
        self.assertLessEqual(before.replace(microsecond=before.microsecond // 1000 * 1000), timestamp)
        self.assertLessEqual(timestamp, after)
        self.assertEqual(self.repository.get_company(company.company_id), company)

    def test_rejects_empty_and_whitespace_names_without_writes(self):
        for name in ("", " ", "\t\r\n", "\u2003"):
            with self.subTest(name=name), self.assertRaises(CompanyValidationError):
                self.service.create_company(name=name)
        self.assertEqual(self.repository.list_companies(), ())

    def test_rejects_nontext_names_without_writes(self):
        for name in (None, 12, True, [], {}, b"Contoso"):
            with self.subTest(name=name), self.assertRaises(CompanyValidationError):
                self.service.create_company(name=name)
        self.assertEqual(self.repository.list_companies(), ())

    def test_duplicate_names_remain_allowed(self):
        first = self.service.create_company(name="Contoso Test Support")
        second = self.service.create_company(name=first.name)
        self.assertNotEqual(first.company_id, second.company_id)

    def test_sqlite_write_failure_is_safe_and_leaves_no_row(self):
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER test_write_failure BEFORE INSERT ON companies "
                               "BEGIN SELECT RAISE(ABORT, 'private failure'); END")
        with self.assertRaises(CompanyCreationError) as caught:
            self.service.create_company(name="Fabrikam Demo Systems")
        self.assertNotIn("private failure", str(caught.exception))
        self.assertEqual(self.repository.list_companies(), ())

    def test_reload_failure_rolls_back_insert_before_retry(self):
        with patch("f7hub.repositories.company_repository._get_company", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(CompanyCreationError):
                self.service.create_company(name="Fabrikam Demo Systems")
        self.assertEqual(self.repository.list_companies(), ())
        self.service.create_company(name="Fabrikam Demo Systems")
        self.assertEqual(len(self.repository.list_companies()), 1)

    def test_missing_reload_record_rolls_back_insert(self):
        with patch("f7hub.repositories.company_repository._get_company", return_value=None):
            with self.assertRaises(CompanyCreationError):
                self.service.create_company(name="Fabrikam Demo Systems")
        self.assertEqual(self.repository.list_companies(), ())

    def test_filesystem_failure_is_translated(self):
        with patch.object(self.repository, "create_company", side_effect=PermissionError("private path")):
            with self.assertRaises(CompanyCreationError) as caught:
                self.service.create_company(name="Contoso Test Support")
        self.assertNotIn("private path", str(caught.exception))

    def test_integrity_foreign_keys_and_six_migrations(self):
        self.service.create_company(name="Fabrikam Demo Systems")
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
