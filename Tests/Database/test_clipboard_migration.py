import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationApplicationError, MigrationChecksumError
from Tests.Database.clipboard_fixtures import (
    PROJECT_ROOT, ClipboardDatabaseTestCase, ITEM_COLUMNS, ITEM_INSERT, EVENT_COLUMNS, EVENT_INSERT,
    FixtureCapture, item_values, event_values, seed_item,
)


class ClipboardMigrationTests(ClipboardDatabaseTestCase):
    def test_fresh_install_exact_objects_and_integrity(self):
        with database_connection(self.database_path) as connection:
            versions = tuple(row[0] for row in connection.execute("SELECT version FROM schema_migrations ORDER BY version"))
            objects = tuple((row[0], row[1]) for row in connection.execute(
                "SELECT type, name FROM sqlite_master WHERE name LIKE 'clipboard_%' OR name LIKE 'idx_clipboard_%' ORDER BY name"))
            self.assertEqual(versions, tuple(range(1, 14)))
            self.assertEqual(set(objects), {("table", "clipboard_items"), ("table", "clipboard_capture_events"),
                ("index", "idx_clipboard_items_recent"), ("index", "idx_clipboard_capture_events_item")})
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            for table in ("clipboard_items", "clipboard_capture_events"):
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
            for table, expected in (("clipboard_items", ITEM_COLUMNS), ("clipboard_capture_events", EVENT_COLUMNS)):
                self.assertEqual(tuple(row[1] for row in connection.execute(f"PRAGMA table_info({table})")), expected)

    def test_repeat_bootstrap_preserves_history_and_rows(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection)
            history = tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations ORDER BY version"))
        result = bootstrap_database(self.database_path, PROJECT_ROOT / "Database/Migrations")
        self.assertEqual(result.migration_result.applied_versions, ())
        with database_connection(self.database_path) as connection:
            self.assertEqual(history, tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations ORDER BY version")))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clipboard_items").fetchone()[0], 1)

    def test_upgrade_from_12_preserves_existing_records(self):
        directory = self.root / "prior-migrations"
        directory.mkdir()
        for migration in (PROJECT_ROOT / "Database/Migrations").glob("*.sql"):
            if int(migration.name[:4]) <= 12:
                shutil.copyfile(migration, directory / migration.name)
        path = self.root / "upgrade.db"
        bootstrap_database(path, directory)
        with database_connection(path) as connection:
            connection.execute("INSERT INTO application_metadata VALUES (?, ?, ?)",
                               ("synthetic_upgrade", "preserve", "2026-10-08T00:00:00.000Z"))
            prior = tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations ORDER BY version"))
            scripts = tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts ORDER BY script_id"))
        result = bootstrap_database(path, PROJECT_ROOT / "Database/Migrations")
        self.assertEqual(result.migration_result.applied_versions, (13,))
        with database_connection(path) as connection:
            self.assertEqual(prior, tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations WHERE version <= 12 ORDER BY version")))
            self.assertEqual(scripts, tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts ORDER BY script_id")))
            self.assertEqual(connection.execute("SELECT metadata_value FROM application_metadata WHERE metadata_key=?", ("synthetic_upgrade",)).fetchone()[0], "preserve")
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_checksum_enforcement(self):
        directory = self.root / "changed-migrations"
        shutil.copytree(PROJECT_ROOT / "Database/Migrations", directory)
        migration = directory / "0013_clipboard_items_capture_events.sql"
        with database_connection(self.database_path) as connection:
            checksum = connection.execute("SELECT checksum_sha256 FROM schema_migrations WHERE version=13").fetchone()[0]
        self.assertEqual(checksum, hashlib.sha256(migration.read_bytes().replace(b"\r\n", b"\n")).hexdigest())
        with migration.open("ab") as stream:
            stream.write(b"\n-- synthetic checksum alteration\n")
        with self.assertRaises(MigrationChecksumError):
            bootstrap_database(self.database_path, directory)

    def test_failed_migration_rolls_back_schema_and_history(self):
        directory = self.root / "failed-migrations"
        shutil.copytree(PROJECT_ROOT / "Database/Migrations", directory)
        migration = directory / "0013_clipboard_items_capture_events.sql"
        with migration.open("ab") as stream:
            stream.write(b"\nTHIS IS INVALID SQL;\n")
        path = self.root / "failure.db"
        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(path, directory)
        with database_connection(path) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=13").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE name LIKE '%clipboard%'").fetchone()[0], 0)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_item_constraints(self):
        invalid = (
            {"clipboard_item_id": 0}, {"clipboard_item_id": -1}, {"raw_text": None}, {"raw_text": ""},
            {"raw_text": "text\0tail"}, {"raw_text": "é" * 32769}, {"media_type": "html"},
            {"identity_profile": "other"}, {"sensitivity": "NEEDS_REVIEW"}, {"sensitivity": "POSSIBLE_SECRET"},
            {"assessment_complete": 0}, {"assessment_complete": None}, {"assessment_method": " "},
            {"assessment_version": None}, {"retention_intent": "RECENT"}, {"is_pinned": 2},
            {"is_pinned": 1}, {"expires_at": None}, {"expires_at": "2026-10-08T10:00:00.000Z"},
            {"retention_intent": "SAVED"}, {"first_received_at": "2026-10-09T10:00:00.000Z"},
            {"last_received_at": "bad"}, {"captured_total": 0}, {"captured_total": 1.5},
            {"revision": -1}, {"revision": 1.5},
        )
        with database_connection(self.database_path) as connection:
            for changes in invalid:
                with self.subTest(fields=tuple(changes)):
                    values = item_values(**changes)
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(ITEM_INSERT, tuple(values[column] for column in ITEM_COLUMNS))
            # Every mandatory column rejects NULL; the PK legitimately allocates its ID.
            for column in set(ITEM_COLUMNS) - {"clipboard_item_id", "expires_at"}:
                with self.subTest(null_column=column):
                    values = item_values(**{column: None})
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(ITEM_INSERT, tuple(values[name] for name in ITEM_COLUMNS))

    def test_event_constraints_and_operation_uniqueness(self):
        with database_connection(self.database_path) as connection:
            identity = seed_item(connection)
            invalid = ({"clipboard_capture_event_id": 0}, {"clipboard_item_id": 999},
                       {"received_at": "bad"}, {"observed_at": "bad"}, {"capture_method": "AUTO"},
                       {"source_class": "private-title"}, {"producer_binding": ""},
                       {"producer_binding": "x" * 129}, {"ingress_generation": " "}, {"operation_id": "bad"})
            for changes in invalid:
                with self.subTest(fields=tuple(changes)):
                    values = event_values(identity, **changes)
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(EVENT_INSERT, tuple(values[column] for column in EVENT_COLUMNS))
            for column in set(EVENT_COLUMNS) - {"clipboard_capture_event_id", "observed_at", "source_class"}:
                with self.subTest(null_column=column):
                    values = event_values(identity, **{column: None})
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(EVENT_INSERT, tuple(values[name] for name in EVENT_COLUMNS))
            original = connection.execute("SELECT * FROM clipboard_capture_events").fetchone()
            values = dict(original)
            values["clipboard_capture_event_id"] = None
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(EVENT_INSERT, tuple(values[column] for column in EVENT_COLUMNS))
            values["ingress_generation"] = "different-generation"
            connection.execute(EVENT_INSERT, tuple(values[column] for column in EVENT_COLUMNS))

    def test_item_owned_events_cascade(self):
        with database_connection(self.database_path) as connection:
            identity = seed_item(connection, captures=(FixtureCapture(), FixtureCapture()))
            connection.execute("DELETE FROM clipboard_items WHERE clipboard_item_id=?", (identity,))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clipboard_capture_events").fetchone()[0], 0)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_fixture_atomic_failure_and_input_validation(self):
        with database_connection(self.database_path) as connection:
            capture = FixtureCapture()
            with self.assertRaises(sqlite3.IntegrityError):
                seed_item(connection, captures=(capture, capture))
            self.assertFalse(connection.in_transaction)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clipboard_items").fetchone()[0], 0)
            invalid = ({"raw_text": " \t\n"}, {"raw_text": "\ud800"}, {"raw_text": "x" * 65537},
                       {"captures": ()}, {"captures": (FixtureCapture(operation_id="bad"),)},
                       {"captures": (FixtureCapture(received_at="2026-99-08T10:00:00.000Z"),)},
                       {"captures": (FixtureCapture(source_class="title"),)}, {"item_id": True}, {"is_pinned": 1})
            for arguments in invalid:
                with self.subTest(fields=tuple(arguments)), self.assertRaises(ValueError):
                    seed_item(connection, **arguments)
