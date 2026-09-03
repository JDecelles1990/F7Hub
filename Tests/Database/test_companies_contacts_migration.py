from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import (
    bootstrap_database,
    database_connection,
    run_foreign_key_check,
    run_integrity_check,
)
from f7hub.infrastructure.migrations import (
    MigrationApplicationError,
    discover_migrations,
    list_applied_migrations,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_MIGRATIONS = (
    PROJECT_ROOT / "Database" / "Migrations" / "0001_core.sql",
    PROJECT_ROOT / "Database" / "Migrations" / "0002_taxonomy.sql",
    PROJECT_ROOT / "Database" / "Migrations" / "0003_companies_contacts.sql",
)
TIMESTAMP = "2026-09-03T00:00:00.000Z"


class CompaniesContactsMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_production_migrations(self) -> tuple[Path, ...]:
        self.migrations_dir.mkdir()
        copied_migrations = []
        for production_migration in PRODUCTION_MIGRATIONS:
            copied_migration = self.migrations_dir / production_migration.name
            shutil.copyfile(production_migration, copied_migration)
            copied_migrations.append(copied_migration)
        return tuple(copied_migrations)

    def bootstrap_schema(self) -> None:
        self.copy_production_migrations()
        bootstrap_database(self.database_path, self.migrations_dir)

    def insert_company(
        self,
        connection: sqlite3.Connection,
        *,
        name: str | None,
        company_code: str | None = None,
        domain: str | None = None,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO companies (
                company_code,
                name,
                domain,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (company_code, name, domain, TIMESTAMP, TIMESTAMP),
        )
        return int(cursor.lastrowid)

    def insert_contact(
        self,
        connection: sqlite3.Connection,
        *,
        display_name: str | None,
        company_id: int | None = None,
        email: str | None = None,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO contacts (
                company_id,
                display_name,
                email,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (company_id, display_name, email, TIMESTAMP, TIMESTAMP),
        )
        return int(cursor.lastrowid)

    def index_key_columns(
        self,
        connection: sqlite3.Connection,
        index_name: str,
    ) -> tuple[tuple[str, int, str], ...]:
        rows = connection.execute(
            """
            SELECT name, "desc", coll, key
            FROM pragma_index_xinfo(?)
            ORDER BY seqno
            """,
            (index_name,),
        ).fetchall()
        return tuple(
            (str(row[0]), int(row[1]), str(row[2]))
            for row in rows
            if row[3] == 1
        )

    def test_migration_chain_is_ordered_recorded_and_idempotent(self) -> None:
        copied_migrations = self.copy_production_migrations()

        migrations = discover_migrations(self.migrations_dir)
        first_result = bootstrap_database(self.database_path, self.migrations_dir)
        second_result = bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)

        expected_checksums = tuple(
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in copied_migrations
        )
        self.assertEqual(
            tuple((migration.version, migration.name) for migration in migrations),
            ((1, "core"), (2, "taxonomy"), (3, "companies_contacts")),
        )
        self.assertEqual(first_result.migration_result.discovered_versions, (1, 2, 3))
        self.assertEqual(first_result.migration_result.applied_versions, (1, 2, 3))
        self.assertEqual(second_result.migration_result.applied_versions, ())
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            ((1, "core"), (2, "taxonomy"), (3, "companies_contacts")),
        )
        self.assertEqual(
            tuple(record.checksum_sha256 for record in records),
            expected_checksums,
        )

    def test_tables_foreign_keys_and_indexes_match_canonical_schema(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            foreign_keys_enabled = connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            columns = {
                table_name: tuple(
                    (row[1], row[2], row[3], row[4], row[5])
                    for row in connection.execute(
                        """
                        SELECT cid, name, type, "notnull", dflt_value, pk
                        FROM pragma_table_info(?)
                        ORDER BY cid
                        """,
                        (table_name,),
                    ).fetchall()
                )
                for table_name in (
                    "companies",
                    "company_notes",
                    "company_links",
                    "contacts",
                )
            }
            foreign_keys = {
                table_name: tuple(
                    (row[2], row[3], row[4], row[6])
                    for row in connection.execute(
                        """
                        SELECT id, seq, "table", "from", "to", on_update,
                               on_delete, match
                        FROM pragma_foreign_key_list(?)
                        ORDER BY id, seq
                        """,
                        (table_name,),
                    ).fetchall()
                )
                for table_name in ("company_notes", "company_links", "contacts")
            }
            explicit_indexes = {
                table_name: {
                    row[1]
                    for row in connection.execute(
                        """
                        SELECT seq, name, "unique", origin, partial
                        FROM pragma_index_list(?)
                        ORDER BY seq
                        """,
                        (table_name,),
                    ).fetchall()
                    if row[3] == "c"
                }
                for table_name in (
                    "companies",
                    "company_notes",
                    "company_links",
                    "contacts",
                )
            }
            index_columns = {
                index_name: self.index_key_columns(connection, index_name)
                for index_name in (
                    "idx_companies_name",
                    "idx_companies_domain",
                    "idx_company_notes_company_created",
                    "idx_company_links_company_sort",
                    "idx_contacts_company_name",
                    "idx_contacts_email",
                )
            }

        self.assertEqual(foreign_keys_enabled, 1)
        self.assertEqual(
            tables,
            {
                "schema_migrations",
                "application_metadata",
                "categories",
                "tags",
                "companies",
                "company_notes",
                "company_links",
                "contacts",
            },
        )
        self.assertEqual(
            columns["companies"],
            (
                ("company_id", "INTEGER", 0, None, 1),
                ("company_code", "TEXT", 0, None, 0),
                ("name", "TEXT", 1, None, 0),
                ("domain", "TEXT", 0, None, 0),
                ("phone", "TEXT", 0, None, 0),
                ("website_url", "TEXT", 0, None, 0),
                ("address_line1", "TEXT", 0, None, 0),
                ("address_line2", "TEXT", 0, None, 0),
                ("city", "TEXT", 0, None, 0),
                ("region", "TEXT", 0, None, 0),
                ("postal_code", "TEXT", 0, None, 0),
                ("country_code", "TEXT", 0, None, 0),
                ("is_active", "INTEGER", 1, "1", 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["company_notes"],
            (
                ("company_note_id", "INTEGER", 0, None, 1),
                ("company_id", "INTEGER", 1, None, 0),
                ("note_text", "TEXT", 1, None, 0),
                ("is_pinned", "INTEGER", 1, "0", 0),
                ("created_by", "TEXT", 0, None, 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["company_links"],
            (
                ("company_link_id", "INTEGER", 0, None, 1),
                ("company_id", "INTEGER", 1, None, 0),
                ("link_type", "TEXT", 0, None, 0),
                ("label", "TEXT", 1, None, 0),
                ("url", "TEXT", 1, None, 0),
                ("sort_order", "INTEGER", 1, "0", 0),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["contacts"],
            (
                ("contact_id", "INTEGER", 0, None, 1),
                ("company_id", "INTEGER", 0, None, 0),
                ("display_name", "TEXT", 1, None, 0),
                ("first_name", "TEXT", 0, None, 0),
                ("last_name", "TEXT", 0, None, 0),
                ("job_title", "TEXT", 0, None, 0),
                ("email", "TEXT", 0, None, 0),
                ("phone", "TEXT", 0, None, 0),
                ("mobile_phone", "TEXT", 0, None, 0),
                ("notes", "TEXT", 0, None, 0),
                ("is_active", "INTEGER", 1, "1", 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            foreign_keys,
            {
                "company_notes": (
                    ("companies", "company_id", "company_id", "CASCADE"),
                ),
                "company_links": (
                    ("companies", "company_id", "company_id", "CASCADE"),
                ),
                "contacts": (
                    ("companies", "company_id", "company_id", "SET NULL"),
                ),
            },
        )
        self.assertEqual(
            explicit_indexes,
            {
                "companies": {"idx_companies_name", "idx_companies_domain"},
                "company_notes": {"idx_company_notes_company_created"},
                "company_links": {"idx_company_links_company_sort"},
                "contacts": {"idx_contacts_company_name", "idx_contacts_email"},
            },
        )
        self.assertEqual(
            index_columns,
            {
                "idx_companies_name": (("name", 0, "NOCASE"),),
                "idx_companies_domain": (("domain", 0, "NOCASE"),),
                "idx_company_notes_company_created": (
                    ("company_id", 0, "BINARY"),
                    ("created_at", 1, "BINARY"),
                ),
                "idx_company_links_company_sort": (
                    ("company_id", 0, "BINARY"),
                    ("sort_order", 0, "BINARY"),
                ),
                "idx_contacts_company_name": (
                    ("company_id", 0, "BINARY"),
                    ("display_name", 0, "NOCASE"),
                ),
                "idx_contacts_email": (("email", 0, "NOCASE"),),
            },
        )

    def test_company_name_code_and_domain_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            self.insert_company(
                connection,
                name="Contoso",
                company_code="CONTOSO",
                domain="contoso.example",
            )
            self.insert_company(
                connection,
                name="Contoso",
                domain="contoso.example",
            )
            self.insert_company(connection, name="Fabrikam")
            duplicate_name_count = connection.execute(
                "SELECT COUNT(*) FROM companies WHERE name = ?",
                ("Contoso",),
            ).fetchone()[0]
            duplicate_domain_count = connection.execute(
                "SELECT COUNT(*) FROM companies WHERE domain = ?",
                ("CONTOSO.EXAMPLE",),
            ).fetchone()[0]
            null_code_count = connection.execute(
                "SELECT COUNT(*) FROM companies WHERE company_code IS NULL"
            ).fetchone()[0]

            for index, invalid_name in enumerate((None, "", "   ")):
                with self.subTest(name=invalid_name):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_company(
                            connection,
                            name=invalid_name,
                            company_code=f"INVALID-{index}",
                        )

            for duplicate_code in ("CONTOSO", "contoso"):
                with self.subTest(company_code=duplicate_code):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_company(
                            connection,
                            name=f"Duplicate {duplicate_code}",
                            company_code=duplicate_code,
                        )

        self.assertEqual(duplicate_name_count, 2)
        self.assertEqual(duplicate_domain_count, 2)
        self.assertEqual(null_code_count, 2)

    def test_company_active_flag_defaults_and_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            default_id = self.insert_company(connection, name="Default Active")
            default_value = connection.execute(
                "SELECT is_active FROM companies WHERE company_id = ?",
                (default_id,),
            ).fetchone()[0]

            for index, active_value in enumerate((0, 1)):
                with self.subTest(active=active_value):
                    connection.execute(
                        """
                        INSERT INTO companies (
                            name,
                            is_active,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (f"Active {index}", active_value, TIMESTAMP, TIMESTAMP),
                    )

            for invalid_value in (-1, 2, 99):
                with self.subTest(active=invalid_value):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO companies (
                                name,
                                is_active,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (
                                f"Invalid active {invalid_value}",
                                invalid_value,
                                TIMESTAMP,
                                TIMESTAMP,
                            ),
                        )

        self.assertEqual(default_value, 1)

    def test_company_note_constraints_and_defaults(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            company_id = self.insert_company(connection, name="Notes Company")
            note_id = connection.execute(
                """
                INSERT INTO company_notes (
                    company_id,
                    note_text,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (company_id, "Escalation instructions", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            default_pin = connection.execute(
                "SELECT is_pinned FROM company_notes WHERE company_note_id = ?",
                (note_id,),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO company_notes (
                    company_id,
                    note_text,
                    is_pinned,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (company_id, "Pinned note", 1, TIMESTAMP, TIMESTAMP),
            )

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO company_notes (
                        company_id,
                        note_text,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (999_999, "Missing company", TIMESTAMP, TIMESTAMP),
                )

            for invalid_note in (None, "", "   "):
                with self.subTest(note_text=invalid_note):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO company_notes (
                                company_id,
                                note_text,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (company_id, invalid_note, TIMESTAMP, TIMESTAMP),
                        )

            for invalid_pin in (-1, 2):
                with self.subTest(is_pinned=invalid_pin):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO company_notes (
                                company_id,
                                note_text,
                                is_pinned,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                company_id,
                                f"Invalid pin {invalid_pin}",
                                invalid_pin,
                                TIMESTAMP,
                                TIMESTAMP,
                            ),
                        )

        self.assertEqual(default_pin, 0)

    def test_company_link_constraints_and_defaults(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            company_id = self.insert_company(connection, name="Links Company")
            link_id = connection.execute(
                """
                INSERT INTO company_links (
                    company_id,
                    label,
                    url,
                    created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (company_id, "Portal", "not-a-validated-url", TIMESTAMP),
            ).lastrowid
            default_sort = connection.execute(
                "SELECT sort_order FROM company_links WHERE company_link_id = ?",
                (link_id,),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO company_links (
                    company_id,
                    label,
                    url,
                    sort_order,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (company_id, "Negative sort", "value", -10, TIMESTAMP),
            )

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO company_links (
                        company_id,
                        label,
                        url,
                        created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (999_999, "Missing company", "value", TIMESTAMP),
                )

            for index, invalid_label in enumerate((None, "", "   ")):
                with self.subTest(label=invalid_label):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO company_links (
                                company_id,
                                label,
                                url,
                                created_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (company_id, invalid_label, f"url-{index}", TIMESTAMP),
                        )

            for index, invalid_url in enumerate((None, "", "   ")):
                with self.subTest(url=invalid_url):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO company_links (
                                company_id,
                                label,
                                url,
                                created_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (company_id, f"Invalid URL {index}", invalid_url, TIMESTAMP),
                        )

        self.assertEqual(default_sort, 0)

    def test_company_deletion_cascades_owned_rows_and_preserves_contact(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            company_id = self.insert_company(connection, name="Delete Company")
            connection.execute(
                """
                INSERT INTO company_notes (
                    company_id,
                    note_text,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (company_id, "Owned note", TIMESTAMP, TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO company_links (
                    company_id,
                    label,
                    url,
                    created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (company_id, "Owned link", "value", TIMESTAMP),
            )
            contact_id = self.insert_contact(
                connection,
                company_id=company_id,
                display_name="Preserved Contact",
            )

            connection.execute(
                "DELETE FROM companies WHERE company_id = ?",
                (company_id,),
            )
            note_count = connection.execute(
                "SELECT COUNT(*) FROM company_notes"
            ).fetchone()[0]
            link_count = connection.execute(
                "SELECT COUNT(*) FROM company_links"
            ).fetchone()[0]
            contact_company_id = connection.execute(
                "SELECT company_id FROM contacts WHERE contact_id = ?",
                (contact_id,),
            ).fetchone()[0]

        self.assertEqual(note_count, 0)
        self.assertEqual(link_count, 0)
        self.assertIsNone(contact_company_id)

    def test_contact_name_email_and_company_relationship_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            company_id = self.insert_company(connection, name="Contact Company")
            self.insert_contact(
                connection,
                company_id=company_id,
                display_name="Alex Smith",
                email="alex@example.test",
            )
            self.insert_contact(
                connection,
                display_name="Alex Smith",
                email="ALEX@EXAMPLE.TEST",
            )
            self.insert_contact(connection, display_name="No Email")
            self.insert_contact(connection, display_name="Also No Email")
            duplicate_names = connection.execute(
                "SELECT COUNT(*) FROM contacts WHERE display_name = ?",
                ("Alex Smith",),
            ).fetchone()[0]
            case_insensitive_emails = connection.execute(
                "SELECT COUNT(*) FROM contacts WHERE email = ?",
                ("alex@example.test",),
            ).fetchone()[0]
            null_email_count = connection.execute(
                "SELECT COUNT(*) FROM contacts WHERE email IS NULL"
            ).fetchone()[0]

            with self.assertRaises(sqlite3.IntegrityError):
                self.insert_contact(
                    connection,
                    company_id=999_999,
                    display_name="Missing Company",
                )

            for invalid_name in (None, "", "   "):
                with self.subTest(display_name=invalid_name):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_contact(
                            connection,
                            display_name=invalid_name,
                        )

        self.assertEqual(duplicate_names, 2)
        self.assertEqual(case_insensitive_emails, 2)
        self.assertEqual(null_email_count, 2)

    def test_contact_active_flag_defaults_and_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            default_id = self.insert_contact(
                connection,
                display_name="Default Active",
            )
            default_value = connection.execute(
                "SELECT is_active FROM contacts WHERE contact_id = ?",
                (default_id,),
            ).fetchone()[0]

            for active_value in (0, 1):
                with self.subTest(active=active_value):
                    connection.execute(
                        """
                        INSERT INTO contacts (
                            display_name,
                            is_active,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            f"Active {active_value}",
                            active_value,
                            TIMESTAMP,
                            TIMESTAMP,
                        ),
                    )

            for invalid_value in (-1, 2, 99):
                with self.subTest(active=invalid_value):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO contacts (
                                display_name,
                                is_active,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (
                                f"Invalid active {invalid_value}",
                                invalid_value,
                                TIMESTAMP,
                                TIMESTAMP,
                            ),
                        )

        self.assertEqual(default_value, 1)

    def test_failed_migration_rolls_back_company_contact_schema_only(self) -> None:
        copied_migrations = self.copy_production_migrations()
        copied_company_migration = copied_migrations[-1]
        copied_company_migration.write_text(
            copied_company_migration.read_text(encoding="utf-8")
            + """
            CREATE TABLE partial_company_state (value TEXT NOT NULL);
            INSERT INTO partial_company_state (value) VALUES ('temporary');
            THIS IS NOT VALID SQL;
            """,
            encoding="utf-8",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            records = list_applied_migrations(connection)
            integrity_results = run_integrity_check(connection)
            foreign_key_violations = run_foreign_key_check(connection)

        self.assertEqual(
            tables,
            {"schema_migrations", "application_metadata", "categories", "tags"},
        )
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            ((1, "core"), (2, "taxonomy")),
        )
        self.assertEqual(integrity_results, ("ok",))
        self.assertEqual(foreign_key_violations, ())


if __name__ == "__main__":
    unittest.main()
