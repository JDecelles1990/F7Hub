from __future__ import annotations

from pathlib import Path
import hashlib
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import (
    DuplicateMigrationVersionError,
    InvalidMigrationFilenameError,
    MigrationApplicationError,
    MigrationChecksumError,
    MigrationDiscoveryError,
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


class MigrationPortabilityTests(unittest.TestCase):
    LF = b"-- immutable fixture\n\nCREATE TABLE sample (value TEXT);\nINSERT INTO sample VALUES ('caf\xc3\xa9\nnext');\n"

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.sources = self.root / "migrations"
        self.sources.mkdir()
        self.path = self.sources / "0001_sample.sql"
        self.database = self.root / "test.db"

    def seed_history(self, sources: tuple[bytes, ...]) -> None:
        # Model the old raw-byte runner without using production hash helpers.
        with database_connection(self.database) as connection:
            initialize_migration_table(connection)
            for version, source in enumerate(sources, 1):
                connection.execute(
                    "INSERT INTO schema_migrations VALUES (?, ?, ?, ?, ?)",
                    (version, "sample", hashlib.sha256(source).hexdigest(),
                     "2026-09-01T00:00:00.000Z", 17 + version),
                )

    def history(self) -> tuple:
        with database_connection(self.database) as connection:
            return tuple(tuple(row) for row in connection.execute(
                "SELECT * FROM schema_migrations ORDER BY version"
            ))

    def test_legacy_matrix_is_read_only_and_idempotent(self) -> None:
        crlf = self.LF.replace(b"\n", b"\r\n")
        for stored in (self.LF, crlf):
            for current in (self.LF, crlf):
                with self.subTest(stored_crlf=stored == crlf, current_crlf=current == crlf):
                    self.database = self.root / f"{stored == crlf}-{current == crlf}.db"
                    self.path.write_bytes(current)
                    self.seed_history((stored,))
                    before = self.history()
                    with database_connection(self.database) as connection:
                        connection.execute("PRAGMA query_only=ON")
                        for _ in range(2):
                            result = run_migrations(connection, discover_migrations(self.sources))
                            self.assertEqual(result.applied_versions, ())
                        self.assertEqual(connection.total_changes, 0)
                    self.assertEqual(self.history(), before)

    def test_fresh_checksum_and_execution_are_canonical(self) -> None:
        for index, source in enumerate((self.LF, self.LF.replace(b"\n", b"\r\n"))):
            with self.subTest(index=index):
                self.database = self.root / f"fresh-{index}.db"
                self.path.write_bytes(source)
                result = bootstrap_database(self.database, self.sources)
                self.assertEqual(result.integrity_results, ("ok",))
                self.assertEqual(result.foreign_key_violations, ())
                self.assertEqual(self.history()[0][2], hashlib.sha256(self.LF).hexdigest())
                with database_connection(self.database) as connection:
                    self.assertEqual(connection.execute("SELECT value FROM sample").fetchone()[0], "caf\u00e9\nnext")
                self.assertEqual(bootstrap_database(self.database, self.sources).migration_result.applied_versions, ())

    def test_mixed_history_preserved_before_canonical_increment(self) -> None:
        for crlf in (False, True):
            with self.subTest(crlf=crlf):
                self.database = self.root / f"mixed-{crlf}.db"
                for version in range(1, 7):
                    source = f"SELECT {version};\n".encode()
                    (self.sources / f"{version:04d}_sample.sql").write_bytes(
                        source.replace(b"\n", b"\r\n") if crlf else source
                    )
                legacy = tuple(
                    f"SELECT {version};".encode() + (b"\n" if version <= 4 else b"\r\n")
                    for version in range(1, 7)
                )
                self.seed_history(legacy)
                before = self.history()
                pending = self.sources / "0007_pending.sql"
                pending.write_bytes(b"CREATE TABLE pending (id INTEGER);\r\n")
                result = bootstrap_database(self.database, self.sources)
                self.assertEqual(result.migration_result.applied_versions, (7,))
                self.assertEqual(self.history()[:6], before)
                self.assertEqual(self.history()[6][2], hashlib.sha256(b"CREATE TABLE pending (id INTEGER);\n").hexdigest())
                self.assertEqual(result.integrity_results, ("ok",))
                self.assertEqual(result.foreign_key_violations, ())

    def test_non_newline_changes_rejected_before_pending_execution(self) -> None:
        bom = b"\xef\xbb\xbf"
        cases = {
            "SQL token": (self.LF, self.LF.replace(b"TEXT", b"BLOB")),
            "comment": (self.LF, self.LF.replace(b"fixture", b"changed")),
            "space": (self.LF, self.LF.replace(b"CREATE TABLE", b"CREATE  TABLE")),
            "tab": (self.LF, self.LF.replace(b"CREATE TABLE", b"CREATE\tTABLE")),
            "added blank": (self.LF, self.LF + b"\n"),
            "removed blank": (self.LF, self.LF.replace(b"\n\n", b"\n")),
            "added final newline": (self.LF[:-1], self.LF),
            "removed final newline": (self.LF, self.LF[:-1]),
            "added BOM": (self.LF, bom + self.LF),
            "removed BOM": (bom + self.LF, self.LF),
            "Unicode normalization": (self.LF, self.LF.replace(b"\xc3\xa9", b"e\xcc\x81")),
            "lone CR": (self.LF, self.LF.replace(b"\n", b"\r")),
        }
        pending = self.sources / "0002_pending.sql"
        pending.write_bytes(b"CREATE TABLE must_not_exist (id INTEGER);\n")
        for index, (label, (original, changed)) in enumerate(cases.items()):
            for legacy_crlf in (False, True):
                with self.subTest(change=label, legacy_crlf=legacy_crlf):
                    self.database = self.root / f"tamper-{index}-{legacy_crlf}.db"
                    self.seed_history((original.replace(b"\n", b"\r\n") if legacy_crlf else original,))
                    before = self.history()
                    self.path.write_bytes(changed)
                    with self.assertRaises(MigrationChecksumError):
                        bootstrap_database(self.database, self.sources)
                    self.assertEqual(self.history(), before)
                    with database_connection(self.database) as connection:
                        self.assertIsNone(connection.execute("SELECT name FROM sqlite_master WHERE name='must_not_exist'").fetchone())

    def test_unknown_digest_and_unavailable_mixed_raw_history_rejected(self) -> None:
        for index, checksum in enumerate(("0" * 64, hashlib.sha256(self.LF.replace(b"\n", b"\r\n", 1)).hexdigest())):
            with self.subTest(index=index):
                self.database = self.root / f"unknown-{index}.db"
                self.seed_history((self.LF,))
                with database_connection(self.database) as connection:
                    connection.execute("UPDATE schema_migrations SET checksum_sha256=?", (checksum,))
                before = self.history()
                self.path.write_bytes(self.LF)
                (self.sources / "0002_pending.sql").write_bytes(b"CREATE TABLE pending (id INTEGER);\n")
                with self.assertRaises(MigrationChecksumError):
                    bootstrap_database(self.database, self.sources)
                self.assertEqual(self.history(), before)
                with database_connection(self.database) as connection:
                    self.assertIsNone(connection.execute("SELECT name FROM sqlite_master WHERE name='pending'").fetchone())

    def test_exact_raw_mixed_and_lone_cr_history_remains_accepted(self) -> None:
        for index, raw in enumerate((self.LF.replace(b"\n", b"\r\n", 1), b"SELECT 'a\rb';\n")):
            with self.subTest(index=index):
                self.database = self.root / f"raw-{index}.db"
                self.path.write_bytes(raw)
                self.seed_history((raw,))
                before = self.history()
                bootstrap_database(self.database, self.sources)
                self.assertEqual(self.history(), before)
                if index == 1:
                    self.path.write_bytes(b"SELECT 'a\nb';\n")
                    with self.assertRaises(MigrationChecksumError):
                        bootstrap_database(self.database, self.sources)

    def test_bom_is_hashed_but_not_executed(self) -> None:
        canonical = b"\xef\xbb\xbf" + self.LF
        self.path.write_bytes(canonical.replace(b"\n", b"\r\n"))
        bootstrap_database(self.database, self.sources)
        self.assertEqual(self.history()[0][2], hashlib.sha256(canonical).hexdigest())

    def test_invalid_utf8_fails_before_database_creation(self) -> None:
        self.path.write_bytes(b"SELECT '\xff';\r\n")
        with self.assertRaises(MigrationDiscoveryError):
            bootstrap_database(self.database, self.sources)
        self.assertFalse(self.database.exists())


if __name__ == "__main__":
    unittest.main()
