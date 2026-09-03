from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"
CREATED_AT = "2026-09-03T10:00:00.000Z"
UPDATED_AT = "2026-09-03T11:00:00.000Z"


class ContactRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.company_repository = CompanyRepository(self.database_path)
        self.repository = ContactRepository(self.database_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def create_company(self, name: str = "Contoso") -> int:
        return self.company_repository.create_company(
            name=name,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        ).company_id

    def test_create_and_get_standalone_and_company_contacts(self) -> None:
        standalone = self.repository.create_contact(
            display_name="Standalone Contact",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        company_id = self.create_company()
        linked = self.repository.create_contact(
            company_id=company_id,
            display_name="Linked Contact",
            first_name="Linked",
            last_name="Contact",
            job_title="Technician",
            email="linked@example.test",
            phone="555-0101",
            mobile_phone="555-0102",
            notes="Primary contact",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertGreater(standalone.contact_id, 0)
        self.assertIsNone(standalone.company_id)
        self.assertEqual(self.repository.get_contact(standalone.contact_id), standalone)
        self.assertEqual(self.repository.get_contact(linked.contact_id), linked)
        self.assertEqual(linked.company_id, company_id)
        self.assertIsNone(self.repository.get_contact(999_999))

    def test_missing_company_fails_and_duplicate_emails_are_allowed(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create_contact(
                company_id=999_999,
                display_name="Missing Company",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )

        first = self.repository.create_contact(
            display_name="First",
            email="shared@example.test",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        second = self.repository.create_contact(
            display_name="Second",
            email="SHARED@EXAMPLE.TEST",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.assertNotEqual(first.contact_id, second.contact_id)

    def test_contact_lists_have_stable_order_and_company_filter(self) -> None:
        first_company_id = self.create_company("First Company")
        second_company_id = self.create_company("Second Company")
        self.repository.create_contact(
            company_id=first_company_id,
            display_name="Zulu",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.repository.create_contact(
            company_id=first_company_id,
            display_name="alpha",
            is_active=0,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.repository.create_contact(
            company_id=second_company_id,
            display_name="Bravo",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertEqual(
            tuple(contact.display_name for contact in self.repository.list_contacts()),
            ("alpha", "Bravo", "Zulu"),
        )
        self.assertEqual(
            tuple(
                contact.display_name
                for contact in self.repository.list_contacts(active_only=True)
            ),
            ("Bravo", "Zulu"),
        )
        self.assertEqual(
            tuple(
                contact.display_name
                for contact in self.repository.list_contacts_for_company(
                    first_company_id
                )
            ),
            ("alpha", "Zulu"),
        )

    def test_update_and_set_contact_active_persist(self) -> None:
        contact = self.repository.create_contact(
            display_name="Original Contact",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        company_id = self.create_company()

        updated = self.repository.update_contact(
            contact.contact_id,
            company_id=company_id,
            display_name="Updated Contact",
            first_name="Updated",
            last_name="Contact",
            job_title="Manager",
            email="updated@example.test",
            phone="555-0201",
            mobile_phone="555-0202",
            notes="Updated notes",
            is_active=0,
            updated_at=UPDATED_AT,
        )

        self.assertIsNotNone(updated)
        assert updated is not None
        self.assertEqual(updated.contact_id, contact.contact_id)
        self.assertEqual(updated.created_at, CREATED_AT)
        self.assertEqual(updated.company_id, company_id)
        self.assertEqual(updated.display_name, "Updated Contact")
        self.assertEqual(updated.is_active, 0)
        reactivated = self.repository.set_contact_active(
            contact.contact_id,
            is_active=1,
            updated_at="2026-09-03T12:00:00.000Z",
        )
        self.assertIsNotNone(reactivated)
        assert reactivated is not None
        self.assertEqual(reactivated.is_active, 1)
        self.assertIsNone(
            self.repository.update_contact(
                999_999,
                company_id=None,
                display_name="Missing",
                first_name=None,
                last_name=None,
                job_title=None,
                email=None,
                phone=None,
                mobile_phone=None,
                notes=None,
                is_active=1,
                updated_at=UPDATED_AT,
            )
        )
        self.assertIsNone(
            self.repository.set_contact_active(
                999_999,
                is_active=0,
                updated_at=UPDATED_AT,
            )
        )

    def test_sql_looking_contact_is_data_and_company_deletion_sets_null(self) -> None:
        company_id = self.create_company()
        hostile_name = "Robert'); DROP TABLE contacts;--"
        contact = self.repository.create_contact(
            company_id=company_id,
            display_name=hostile_name,
            notes="'; DELETE FROM companies;--",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        with database_connection(self.database_path) as connection:
            connection.execute(
                "DELETE FROM companies WHERE company_id = ?",
                (company_id,),
            )
            contacts_table_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                ("contacts",),
            ).fetchone()[0]

        preserved = self.repository.get_contact(contact.contact_id)
        self.assertIsNotNone(preserved)
        assert preserved is not None
        self.assertEqual(preserved.display_name, hostile_name)
        self.assertIsNone(preserved.company_id)
        self.assertEqual(contacts_table_count, 1)


if __name__ == "__main__":
    unittest.main()
