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
    MigrationChecksumError,
    discover_migrations,
    list_applied_migrations,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_CORE_MIGRATION = (
    PROJECT_ROOT / "Database" / "Migrations" / "0001_core.sql"
)


class CoreMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_production_core_migration(self) -> Path:
        self.migrations_dir.mkdir()
        copied_migration = self.migrations_dir / PRODUCTION_CORE_MIGRATION.name
        shutil.copyfile(PRODUCTION_CORE_MIGRATION, copied_migration)
        return copied_migration

    def test_fresh_database_applies_and_records_core_migration(self) -> None:
        copied_migration = self.copy_production_core_migration()

        migrations = discover_migrations(self.migrations_dir)
        result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(len(migrations), 1)
        self.assertEqual(migrations[0].version, 1)
        self.assertEqual(migrations[0].name, "core")
        self.assertEqual(result.migration_result.discovered_versions, (1,))
        self.assertEqual(result.migration_result.applied_versions, (1,))
        self.assertEqual(result.integrity_results, ("ok",))
        self.assertEqual(result.foreign_key_violations, ())

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

        expected_checksum = hashlib.sha256(copied_migration.read_bytes()).hexdigest()
        self.assertEqual(tables, {"schema_migrations", "application_metadata"})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].version, 1)
        self.assertEqual(records[0].name, "core")
        self.assertEqual(records[0].checksum_sha256, expected_checksum)

    def test_second_bootstrap_is_idempotent_for_core_migration(self) -> None:
        self.copy_production_core_migration()

        first_result = bootstrap_database(self.database_path, self.migrations_dir)
        second_result = bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
                (1,),
            ).fetchone()[0]
            metadata_table_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                ("application_metadata",),
            ).fetchone()[0]

        self.assertEqual(first_result.migration_result.applied_versions, (1,))
        self.assertEqual(second_result.migration_result.applied_versions, ())
        self.assertEqual(migration_count, 1)
        self.assertEqual(metadata_table_count, 1)

    def test_modified_copied_core_migration_fails_checksum_validation(self) -> None:
        copied_migration = self.copy_production_core_migration()
        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            original_record = list_applied_migrations(connection)[0]

        copied_migration.write_text(
            copied_migration.read_text(encoding="utf-8")
            + "\n-- Isolated checksum-change fixture.\n",
            encoding="utf-8",
        )

        with self.assertRaises(MigrationChecksumError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)
            connection_is_usable = connection.execute("SELECT 1").fetchone()[0]

        self.assertEqual(records, (original_record,))
        self.assertEqual(connection_is_usable, 1)

    def test_core_tables_match_approved_structure_and_constraints(self) -> None:
        self.copy_production_core_migration()
        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            migration_columns = tuple(
                (row[1], row[2], row[3], row[5])
                for row in connection.execute(
                    "PRAGMA table_info(schema_migrations)"
                ).fetchall()
            )
            metadata_columns = tuple(
                (row[1], row[2], row[3], row[5])
                for row in connection.execute(
                    "PRAGMA table_info(application_metadata)"
                ).fetchall()
            )
            metadata_ddl = connection.execute(
                """
                SELECT sql
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                ("application_metadata",),
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO application_metadata (
                    metadata_key,
                    metadata_value,
                    updated_at
                ) VALUES (?, ?, ?)
                """,
                ("database_uuid", "example", "2026-09-03T00:00:00.000Z"),
            )
            invalid_rows = (
                (None, "test", "2026-01-01T00:00:00Z"),
                ("database_uuid", "duplicate", "2026-09-03T00:00:01.000Z"),
                ("missing_value", None, "2026-09-03T00:00:02.000Z"),
                ("missing_time", "example", None),
            )
            for invalid_row in invalid_rows:
                with self.subTest(row=invalid_row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO application_metadata (
                                metadata_key,
                                metadata_value,
                                updated_at
                            ) VALUES (?, ?, ?)
                            """,
                            invalid_row,
                        )

        self.assertEqual(
            migration_columns,
            (
                ("version", "INTEGER", 0, 1),
                ("name", "TEXT", 1, 0),
                ("checksum_sha256", "TEXT", 1, 0),
                ("applied_at", "TEXT", 1, 0),
                ("execution_ms", "INTEGER", 1, 0),
            ),
        )
        self.assertEqual(
            metadata_columns,
            (
                ("metadata_key", "TEXT", 1, 1),
                ("metadata_value", "TEXT", 1, 0),
                ("updated_at", "TEXT", 1, 0),
            ),
        )
        self.assertEqual(
            " ".join(metadata_ddl.split()),
            "CREATE TABLE application_metadata ( metadata_key TEXT NOT NULL "
            "PRIMARY KEY, metadata_value TEXT NOT NULL, updated_at TEXT NOT NULL )",
        )

    def test_failed_copied_core_migration_rolls_back_application_schema(self) -> None:
        copied_migration = self.copy_production_core_migration()
        copied_migration.write_text(
            copied_migration.read_text(encoding="utf-8")
            + """
            CREATE TABLE partial_core_state (value TEXT NOT NULL);
            INSERT INTO partial_core_state (value) VALUES ('temporary');
            THIS IS NOT VALID SQL;
            """,
            encoding="utf-8",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            application_table_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE name IN (?, ?)
                """,
                ("application_metadata", "partial_core_state"),
            ).fetchone()[0]
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            integrity_results = run_integrity_check(connection)
            foreign_key_violations = run_foreign_key_check(connection)
            connection_is_usable = connection.execute("SELECT 1").fetchone()[0]

        self.assertEqual(application_table_count, 0)
        self.assertEqual(migration_count, 0)
        self.assertEqual(integrity_results, ("ok",))
        self.assertEqual(foreign_key_violations, ())
        self.assertEqual(connection_is_usable, 1)


if __name__ == "__main__":
    unittest.main()
