from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import (
    DuplicateMigrationVersionError,
    InvalidMigrationFilenameError,
    MigrationApplicationError,
    MigrationChecksumError,
    MigrationHistoryError,
    discover_migrations,
    initialize_migration_table,
    list_applied_migrations,
    run_migrations,
)


class MigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"
        self.migrations_dir.mkdir()

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def write_migration(self, filename: str, sql: str) -> Path:
        migration_path = self.migrations_dir / filename
        migration_path.write_text(sql, encoding="utf-8")
        return migration_path

    def assert_rejected_migration_rolls_back(
        self,
        *,
        database_path: Path,
        migrations_dir: Path,
        sql: str,
    ) -> None:
        migrations_dir.mkdir(parents=True)
        (migrations_dir / "0001_rejected.sql").write_text(sql, encoding="utf-8")

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(database_path, migrations_dir)

        with database_connection(database_path) as connection:
            partial_table_count = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name = ?",
                ("partial_items",),
            ).fetchone()[0]
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            connection_is_usable = connection.execute("SELECT 1").fetchone()[0]

        self.assertEqual(partial_table_count, 0)
        self.assertEqual(migration_count, 0)
        self.assertEqual(connection_is_usable, 1)

    def test_empty_migration_directory_initializes_schema_migrations(self) -> None:
        result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(result.migration_result.discovered_versions, ())
        self.assertEqual(result.migration_result.applied_versions, ())
        self.assertEqual(result.integrity_results, ("ok",))
        self.assertEqual(result.foreign_key_violations, ())
        with database_connection(self.database_path) as connection:
            table_name = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'schema_migrations'
                """
            ).fetchone()[0]
        self.assertEqual(table_name, "schema_migrations")

    def test_discovers_valid_migrations_in_numeric_order(self) -> None:
        self.write_migration("0010_tenth.sql", "SELECT 10;")
        self.write_migration("0002_second.sql", "SELECT 2;")

        migrations = discover_migrations(self.migrations_dir)

        self.assertEqual([migration.version for migration in migrations], [2, 10])
        self.assertEqual([migration.name for migration in migrations], ["second", "tenth"])

    def test_rejects_malformed_migration_filenames(self) -> None:
        malformed_filenames = (
            "1_short.sql",
            "0001_.sql",
            "0001_bad-name.sql",
            "0001_UPPER.sql",
            "0001_missing_extension",
            "notes.txt",
        )

        for index, malformed_filename in enumerate(malformed_filenames):
            with self.subTest(filename=malformed_filename):
                case_dir = self.temporary_path / f"malformed_{index}"
                case_dir.mkdir()
                (case_dir / malformed_filename).write_text("SELECT 1;", encoding="utf-8")
                with self.assertRaises(InvalidMigrationFilenameError):
                    discover_migrations(case_dir)

    def test_rejects_duplicate_migration_versions(self) -> None:
        self.write_migration("0001_core.sql", "SELECT 1;")
        self.write_migration("0001_other.sql", "SELECT 2;")

        with self.assertRaises(DuplicateMigrationVersionError):
            discover_migrations(self.migrations_dir)

    def test_applies_one_migration_and_records_it(self) -> None:
        self.write_migration(
            "0001_core.sql",
            "CREATE TABLE sample_items (item_id INTEGER PRIMARY KEY);",
        )

        result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(result.migration_result.applied_versions, (1,))
        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)
            table_name = connection.execute(
                "SELECT name FROM sqlite_master WHERE name = ?",
                ("sample_items",),
            ).fetchone()[0]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].version, 1)
        self.assertEqual(records[0].name, "core")
        self.assertEqual(len(records[0].checksum_sha256), 64)
        self.assertEqual(table_name, "sample_items")

    def test_applies_multiple_migrations_in_order(self) -> None:
        self.write_migration(
            "0002_add_name.sql",
            "ALTER TABLE ordered_items ADD COLUMN name TEXT;",
        )
        self.write_migration(
            "0001_create_items.sql",
            "CREATE TABLE ordered_items (item_id INTEGER PRIMARY KEY);",
        )

        result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(result.migration_result.applied_versions, (1, 2))
        with database_connection(self.database_path) as connection:
            columns = connection.execute(
                "PRAGMA table_info(ordered_items)"
            ).fetchall()
            versions = [
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
            ]
        self.assertEqual([column[1] for column in columns], ["item_id", "name"])
        self.assertEqual(versions, [1, 2])

    def test_second_bootstrap_is_idempotent_and_accepts_unchanged_checksum(self) -> None:
        self.write_migration(
            "0001_core.sql",
            "CREATE TABLE stable_items (item_id INTEGER PRIMARY KEY);",
        )

        first_result = bootstrap_database(self.database_path, self.migrations_dir)
        second_result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(first_result.migration_result.applied_versions, (1,))
        self.assertEqual(second_result.migration_result.applied_versions, ())
        with database_connection(self.database_path) as connection:
            record_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
        self.assertEqual(record_count, 1)

    def test_incremental_bootstrap_applies_only_newer_pending_migration(self) -> None:
        self.write_migration(
            "0001_core.sql",
            "CREATE TABLE incremental_items (item_id INTEGER PRIMARY KEY);",
        )
        bootstrap_database(self.database_path, self.migrations_dir)
        self.write_migration(
            "0002_add_name.sql",
            "ALTER TABLE incremental_items ADD COLUMN name TEXT;",
        )

        result = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(result.migration_result.applied_versions, (2,))
        with database_connection(self.database_path) as connection:
            versions = [
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
            ]
        self.assertEqual(versions, [1, 2])

    def test_rejects_modified_applied_migration(self) -> None:
        migration_path = self.write_migration(
            "0001_core.sql",
            "CREATE TABLE immutable_items (item_id INTEGER PRIMARY KEY);",
        )
        bootstrap_database(self.database_path, self.migrations_dir)
        migration_path.write_text(
            "CREATE TABLE immutable_items (item_id INTEGER PRIMARY KEY, name TEXT);",
            encoding="utf-8",
        )

        with self.assertRaises(MigrationChecksumError):
            bootstrap_database(self.database_path, self.migrations_dir)

    def test_rejects_renamed_applied_migration(self) -> None:
        migration_path = self.write_migration("0001_core.sql", "SELECT 1;")
        bootstrap_database(self.database_path, self.migrations_dir)
        migration_path.rename(self.migrations_dir / "0001_renamed.sql")

        with self.assertRaises(MigrationHistoryError):
            bootstrap_database(self.database_path, self.migrations_dir)

    def test_rejects_missing_applied_migration_file(self) -> None:
        migration_path = self.write_migration("0001_core.sql", "SELECT 1;")
        bootstrap_database(self.database_path, self.migrations_dir)
        migration_path.unlink()

        with self.assertRaises(MigrationHistoryError):
            bootstrap_database(self.database_path, self.migrations_dir)

    def test_rejects_pending_migration_older_than_applied_history(self) -> None:
        self.write_migration("0002_existing.sql", "SELECT 2;")
        bootstrap_database(self.database_path, self.migrations_dir)
        self.write_migration("0001_late.sql", "SELECT 1;")

        with self.assertRaises(MigrationHistoryError):
            bootstrap_database(self.database_path, self.migrations_dir)

    def test_invalid_migration_is_not_recorded(self) -> None:
        self.write_migration(
            "0001_invalid.sql",
            "CREATE TABLE invalid_items (item_id INTEGER PRIMARY KEY); NOT VALID SQL;",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            record_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            table_exists = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name = ?",
                ("invalid_items",),
            ).fetchone()[0]
        self.assertEqual(record_count, 0)
        self.assertEqual(table_exists, 0)

    def test_partial_migration_changes_are_rolled_back(self) -> None:
        self.write_migration(
            "0001_partial_failure.sql",
            """
            CREATE TABLE partial_items (item_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            INSERT INTO partial_items (name) VALUES ('temporary');
            INSERT INTO missing_table (name) VALUES ('failure');
            """,
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            table_exists = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name = ?",
                ("partial_items",),
            ).fetchone()[0]
        self.assertEqual(table_exists, 0)

    def test_migration_cannot_commit_its_own_partial_changes(self) -> None:
        self.write_migration(
            "0001_forbidden_commit.sql",
            """
            CREATE TABLE escaped_items (item_id INTEGER PRIMARY KEY);
            COMMIT;
            CREATE TABLE never_created (item_id INTEGER PRIMARY KEY);
            """,
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            escaped_table_count = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name IN (?, ?)",
                ("escaped_items", "never_created"),
            ).fetchone()[0]
        self.assertEqual(escaped_table_count, 0)

    def test_rejects_migration_authored_transaction_control(self) -> None:
        transaction_statements = (
            "BEGIN;",
            "COMMIT;",
            "ROLLBACK;",
            "SAVEPOINT migration_scope;",
        )

        for index, transaction_statement in enumerate(transaction_statements):
            with self.subTest(statement=transaction_statement):
                case_path = self.temporary_path / f"transaction_control_{index}"
                self.assert_rejected_migration_rolls_back(
                    database_path=case_path / "database.db",
                    migrations_dir=case_path / "migrations",
                    sql=f"""
                    CREATE TABLE partial_items (
                        item_id INTEGER PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    INSERT INTO partial_items (value) VALUES ('temporary');
                    {transaction_statement}
                    CREATE TABLE unreachable_items (item_id INTEGER PRIMARY KEY);
                    """,
                )

    def test_rejects_migration_authored_attach(self) -> None:
        case_path = self.temporary_path / "attach"
        self.assert_rejected_migration_rolls_back(
            database_path=case_path / "database.db",
            migrations_dir=case_path / "migrations",
            sql="""
            CREATE TABLE partial_items (
                item_id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            );
            INSERT INTO partial_items (value) VALUES ('temporary');
            ATTACH DATABASE ':memory:' AS external_database;
            """,
        )

    def test_rejects_migration_authored_detach(self) -> None:
        self.write_migration(
            "0001_detach.sql",
            """
            CREATE TABLE partial_items (
                item_id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            );
            INSERT INTO partial_items (value) VALUES ('temporary');
            DETACH DATABASE external_database;
            """,
        )

        with database_connection(self.database_path) as connection:
            initialize_migration_table(connection)
            connection.execute("ATTACH DATABASE ':memory:' AS external_database")

            with self.assertRaises(MigrationApplicationError):
                run_migrations(connection, discover_migrations(self.migrations_dir))

            partial_table_count = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name = ?",
                ("partial_items",),
            ).fetchone()[0]
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            connection_is_usable = connection.execute("SELECT 1").fetchone()[0]

        self.assertEqual(partial_table_count, 0)
        self.assertEqual(migration_count, 0)
        self.assertEqual(connection_is_usable, 1)

    def test_parses_semicolons_inside_quoted_values_and_comments(self) -> None:
        self.write_migration(
            "0001_semicolons.sql",
            """
            CREATE TABLE parsed_values (value TEXT NOT NULL);
            -- A line-comment semicolon ; must not split the statement.
            INSERT INTO parsed_values (value) VALUES ('alpha;beta');
            /* A block-comment semicolon ; must not split the statement. */
            INSERT INTO parsed_values (value) VALUES ('gamma;delta');
            """,
        )

        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            values = tuple(
                row[0]
                for row in connection.execute(
                    "SELECT value FROM parsed_values ORDER BY rowid"
                ).fetchall()
            )

        self.assertEqual(values, ("alpha;beta", "gamma;delta"))

    def test_schema_migrations_has_approved_structure_and_constraints(self) -> None:
        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            columns = tuple(
                (row[1], row[2], row[3], row[5])
                for row in connection.execute(
                    "PRAGMA table_info(schema_migrations)"
                ).fetchall()
            )
            table_ddl = connection.execute(
                """
                SELECT sql
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                ("schema_migrations",),
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO schema_migrations (
                    version,
                    name,
                    checksum_sha256,
                    applied_at,
                    execution_ms
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (1, "core", "a" * 64, "2026-09-03T00:00:00.000Z", 0),
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO schema_migrations (
                        version,
                        name,
                        checksum_sha256,
                        applied_at,
                        execution_ms
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (1, "duplicate", "b" * 64, "2026-09-03T00:00:01.000Z", 1),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO schema_migrations (
                        version,
                        name,
                        checksum_sha256,
                        applied_at,
                        execution_ms
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (2, None, "c" * 64, "2026-09-03T00:00:02.000Z", 1),
                )

        self.assertEqual(
            columns,
            (
                ("version", "INTEGER", 0, 1),
                ("name", "TEXT", 1, 0),
                ("checksum_sha256", "TEXT", 1, 0),
                ("applied_at", "TEXT", 1, 0),
                ("execution_ms", "INTEGER", 1, 0),
            ),
        )
        self.assertIn("CHECK (execution_ms >= 0)", table_ddl)

    def test_schema_migrations_rejects_negative_execution_time(self) -> None:
        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO schema_migrations (
                        version,
                        name,
                        checksum_sha256,
                        applied_at,
                        execution_ms
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (1, "invalid", "a" * 64, "2026-09-03T00:00:00.000Z", -1),
                )
            migration_count = connection.execute(
                "SELECT COUNT(*) FROM schema_migrations"
            ).fetchone()[0]
            connection_is_usable = connection.execute("SELECT 1").fetchone()[0]

        self.assertEqual(migration_count, 0)
        self.assertEqual(connection_is_usable, 1)

    def test_trigger_body_is_parsed_as_one_complete_statement(self) -> None:
        self.write_migration(
            "0001_trigger.sql",
            """
            CREATE TABLE source_items (item_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE item_audit (name TEXT NOT NULL);
            CREATE TRIGGER source_items_ai
            AFTER INSERT ON source_items
            BEGIN
                INSERT INTO item_audit (name) VALUES (NEW.name);
            END;
            INSERT INTO source_items (name) VALUES ('created');
            """,
        )

        bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            audit_name = connection.execute(
                "SELECT name FROM item_audit"
            ).fetchone()[0]
        self.assertEqual(audit_name, "created")


if __name__ == "__main__":
    unittest.main()
