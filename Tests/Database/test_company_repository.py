from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.company_repository import CompanyRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"
CREATED_AT = "2026-09-03T10:00:00.000Z"
UPDATED_AT = "2026-09-03T11:00:00.000Z"


class CompanyRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = CompanyRepository(self.database_path)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_create_and_get_company_with_optional_fields(self) -> None:
        company = self.repository.create_company(
            name="Northwind",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertGreater(company.company_id, 0)
        self.assertEqual(self.repository.get_company(company.company_id), company)
        self.assertIsNone(self.repository.get_company(999_999))
        self.assertIsNone(company.company_code)
        self.assertIsNone(company.domain)
        self.assertIsNone(company.phone)
        self.assertIsNone(company.website_url)
        self.assertIsNone(company.address_line1)
        self.assertIsNone(company.address_line2)
        self.assertIsNone(company.city)
        self.assertIsNone(company.region)
        self.assertIsNone(company.postal_code)
        self.assertIsNone(company.country_code)
        self.assertEqual(company.is_active, 1)

    def test_company_code_lookup_is_nocase_and_duplicate_names_are_allowed(self) -> None:
        first = self.repository.create_company(
            name="Contoso",
            company_code="ACME",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        second = self.repository.create_company(
            name="Contoso",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertEqual(self.repository.get_company_by_code("acme"), first)
        self.assertNotEqual(first.company_id, second.company_id)
        self.assertIsNone(self.repository.get_company_by_code("missing"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create_company(
                name="Different Name",
                company_code="AcMe",
                created_at=CREATED_AT,
                updated_at=CREATED_AT,
            )

    def test_list_companies_has_stable_order_and_active_filter(self) -> None:
        self.repository.create_company(
            name="Zulu",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.repository.create_company(
            name="alpha",
            is_active=0,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )
        self.repository.create_company(
            name="Bravo",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertEqual(
            tuple(company.name for company in self.repository.list_companies()),
            ("alpha", "Bravo", "Zulu"),
        )
        self.assertEqual(
            tuple(
                company.name
                for company in self.repository.list_companies(active_only=True)
            ),
            ("Bravo", "Zulu"),
        )

    def test_update_and_set_company_active_persist(self) -> None:
        company = self.repository.create_company(
            name="Original",
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        updated = self.repository.update_company(
            company.company_id,
            company_code="UPDATED",
            name="Updated Company",
            domain="updated.example",
            phone="555-0100",
            website_url="https://updated.example",
            address_line1="1 Main Street",
            address_line2="Suite 2",
            city="Toronto",
            region="ON",
            postal_code="A1A 1A1",
            country_code="CA",
            is_active=0,
            updated_at=UPDATED_AT,
        )

        self.assertIsNotNone(updated)
        assert updated is not None
        self.assertEqual(updated.company_id, company.company_id)
        self.assertEqual(updated.created_at, CREATED_AT)
        self.assertEqual(updated.name, "Updated Company")
        self.assertEqual(updated.company_code, "UPDATED")
        self.assertEqual(updated.domain, "updated.example")
        self.assertEqual(updated.is_active, 0)
        reactivated = self.repository.set_company_active(
            company.company_id,
            is_active=1,
            updated_at="2026-09-03T12:00:00.000Z",
        )
        self.assertIsNotNone(reactivated)
        assert reactivated is not None
        self.assertEqual(reactivated.is_active, 1)
        self.assertIsNone(
            self.repository.update_company(
                999_999,
                company_code=None,
                name="Missing",
                domain=None,
                phone=None,
                website_url=None,
                address_line1=None,
                address_line2=None,
                city=None,
                region=None,
                postal_code=None,
                country_code=None,
                is_active=1,
                updated_at=UPDATED_AT,
            )
        )
        self.assertIsNone(
            self.repository.set_company_active(
                999_999,
                is_active=0,
                updated_at=UPDATED_AT,
            )
        )

    def test_sql_looking_company_name_is_stored_as_data(self) -> None:
        hostile_name = "O'Reilly Support; DROP TABLE companies;"

        company = self.repository.create_company(
            name=hostile_name,
            created_at=CREATED_AT,
            updated_at=CREATED_AT,
        )

        self.assertEqual(self.repository.get_company(company.company_id).name, hostile_name)
        with database_connection(self.database_path) as connection:
            companies_table_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                ("companies",),
            ).fetchone()[0]
        self.assertEqual(companies_table_count, 1)


if __name__ == "__main__":
    unittest.main()
