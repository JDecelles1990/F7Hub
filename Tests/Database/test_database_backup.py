from __future__ import annotations

import os
from contextlib import closing, contextmanager
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import (
    DatabaseIntegrityError, create_database_snapshot, validate_database_integrity,
)
from f7hub.services.database_backup_service import DatabaseBackupError, DatabaseBackupService


@contextmanager
def connected(path, **kwargs):
    with closing(sqlite3.connect(path, **kwargs)) as connection:
        with connection:
            yield connection


class DatabaseBackupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "active.db"
        self.backups = self.root / "local" / "F7Hub" / "Backups"
        self.environment = patch.dict(os.environ, {"LOCALAPPDATA": str(self.root / "local")})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        with connected(self.source) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript("""
                CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY);
                CREATE TABLE tickets(id INTEGER PRIMARY KEY, subject TEXT NOT NULL);
                CREATE TABLE notes(id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL
                    REFERENCES tickets(id), body TEXT NOT NULL);
                INSERT INTO schema_migrations VALUES (6);
                INSERT INTO tickets VALUES (1, 'Printer offline');
                INSERT INTO notes VALUES (1, 1, 'Investigate cable');
            """)

    def source_dump(self):
        with connected(self.source) as connection:
            return tuple(connection.iterdump())

    def temp_files(self):
        return tuple(self.backups.glob(".f7hub-backup-*.tmp")) if self.backups.exists() else ()

    def test_populated_snapshot_reopens_validates_and_does_not_change_source(self):
        before = self.source_dump()
        result = DatabaseBackupService(self.source).create_backup()
        self.assertEqual(result.parent, self.backups)
        self.assertTrue(result.name.startswith("F7Hub-Database-"))
        self.assertEqual(result.suffix, ".db")
        self.assertFalse(self.temp_files())
        with connected(result) as snapshot:
            self.assertEqual(validate_database_integrity(snapshot), (("ok",), ()))
            self.assertEqual(snapshot.execute("SELECT subject FROM tickets").fetchone()[0],
                             "Printer offline")
            self.assertEqual(snapshot.execute("SELECT body FROM notes").fetchone()[0],
                             "Investigate cable")
            self.assertEqual(snapshot.execute("SELECT version FROM schema_migrations").fetchone()[0], 6)
        self.assertEqual(self.source_dump(), before)
        second = DatabaseBackupService(self.source).create_backup()
        self.assertNotEqual(second, result)
        self.assertTrue(result.exists())

    def test_backup_connections_enable_foreign_keys(self):
        original_connect = sqlite3.connect
        observed = []

        class ObservedConnection(sqlite3.Connection):
            def close(self):
                try:
                    observed.append((self.backup_role,
                                     self.execute("PRAGMA foreign_keys").fetchone()[0]))
                finally:
                    super().close()

        def observing_connect(path, *args, **kwargs):
            if path == self.source.resolve().as_uri() + "?mode=ro":
                role = "source"
            elif isinstance(path, Path) and path.suffix == ".tmp":
                role = "destination"
            elif str(path).endswith(".tmp?mode=ro"):
                role = "validation"
            else:
                raise AssertionError(f"Unexpected backup connection target: {path}")
            connection = original_connect(path, *args, factory=ObservedConnection, **kwargs)
            connection.backup_role = role
            return connection

        with patch("f7hub.infrastructure.database.sqlite3.connect",
                   side_effect=observing_connect):
            result = DatabaseBackupService(self.source).create_backup()

        self.assertTrue(result.is_file())
        self.assertEqual(observed, [
            ("destination", 1), ("source", 1), ("validation", 1),
        ])

    def test_missing_source_does_not_create_database_or_publish(self):
        missing = self.root / "missing.db"
        with self.assertRaisesRegex(DatabaseBackupError, "could not be completed"):
            DatabaseBackupService(missing).create_backup()
        self.assertFalse(missing.exists())
        self.assertFalse(self.backups.exists())

    def test_missing_local_app_data_fails_before_destination_creation(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": ""}):
            with self.assertRaises(DatabaseBackupError):
                DatabaseBackupService(self.source).create_backup()
        self.assertFalse(self.backups.exists())

    def test_relative_local_app_data_cannot_redirect_backup_to_working_directory(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": "relative-backups"}):
            with self.assertRaises(DatabaseBackupError):
                DatabaseBackupService(self.source).create_backup()
        self.assertFalse(self.backups.exists())

    def test_directory_creation_failure_is_safe(self):
        self.backups.parent.mkdir(parents=True)
        self.backups.write_text("not a directory", encoding="utf-8")
        before = self.source_dump()
        with self.assertRaises(DatabaseBackupError):
            DatabaseBackupService(self.source).create_backup()
        self.assertEqual(self.source_dump(), before)
        self.assertEqual(self.backups.read_text(encoding="utf-8"), "not a directory")

    def test_destination_open_failure_removes_temporary_file(self):
        original_connect = sqlite3.connect

        def failing_destination(path, *args, **kwargs):
            if str(path).endswith(".tmp"):
                raise OSError("PRIVATE_DESTINATION_ERROR")
            return original_connect(path, *args, **kwargs)

        before = self.source_dump()
        with patch("f7hub.infrastructure.database.sqlite3.connect", side_effect=failing_destination):
            with self.assertRaisesRegex(DatabaseBackupError, "could not be completed") as caught:
                DatabaseBackupService(self.source).create_backup()
        self.assertNotIn("PRIVATE_DESTINATION_ERROR", str(caught.exception))
        self.assertEqual(self.source_dump(), before)
        self.assertFalse(self.temp_files())
        self.assertEqual(tuple(self.backups.glob("*.db")), ())

    def test_integrity_failure_does_not_publish_and_preserves_existing_backup(self):
        self.backups.mkdir(parents=True)
        existing = self.backups / "existing.db"
        existing.write_bytes(b"EXISTING_BACKUP")
        before = self.source_dump()
        with patch("f7hub.infrastructure.database.validate_database_integrity",
                   side_effect=DatabaseIntegrityError("PRIVATE_INTEGRITY_ERROR")):
            with self.assertRaises(DatabaseBackupError):
                DatabaseBackupService(self.source).create_backup()
        self.assertEqual(existing.read_bytes(), b"EXISTING_BACKUP")
        self.assertEqual(self.source_dump(), before)
        self.assertFalse(self.temp_files())
        self.assertEqual(tuple(self.backups.glob("F7Hub-Database-*.db")), ())

    def test_collision_does_not_overwrite_final_or_leave_temporary_file(self):
        self.backups.mkdir(parents=True)
        final = self.backups / "F7Hub-Database-fixed.db"
        final.write_bytes(b"EXISTING_BACKUP")
        before = self.source_dump()
        with patch("f7hub.services.database_backup_service._backup_filename", return_value=final.name):
            with self.assertRaisesRegex(DatabaseBackupError, "could not be completed") as caught:
                DatabaseBackupService(self.source).create_backup()
        self.assertNotIn("EXISTING_BACKUP", str(caught.exception))
        self.assertEqual(final.read_bytes(), b"EXISTING_BACKUP")
        self.assertEqual(self.source_dump(), before)
        self.assertFalse(self.temp_files())

    def test_failed_backup_step_cleans_temporary_file(self):
        def abort(_status, _remaining, _total):
            raise OSError("PRIVATE_STEP_FAILURE")

        self.assertEqual(tuple(self.backups.glob("*.db")) if self.backups.exists() else (), ())
        with self.assertRaises(OSError):
            create_database_snapshot(self.source, self.backups, "F7Hub-Database-abort.db",
                                     progress=abort)
        self.assertFalse(self.temp_files())
        self.assertEqual(tuple(self.backups.glob("*.db")), ())

    def test_foreign_key_violation_rejects_backup(self):
        with connected(self.source) as connection:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("INSERT INTO notes VALUES (2, 999, 'orphan')")
        before = self.source_dump()
        with self.assertRaises(DatabaseBackupError):
            DatabaseBackupService(self.source).create_backup()
        self.assertEqual(self.source_dump(), before)
        self.assertFalse(self.temp_files())
        self.assertEqual(tuple(self.backups.glob("*.db")), ())

    def test_wal_source_and_concurrent_writer_yield_valid_snapshot(self):
        with connected(self.source) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("INSERT INTO tickets VALUES (2, 'Before backup')")
            connection.execute("CREATE TABLE padding(value BLOB)")
            connection.executemany("INSERT INTO padding VALUES (?)", [(bytes(8192),)] * 256)
        started = threading.Event()
        writer_done = threading.Event()
        writer_error = []

        def writer():
            if not started.wait(5):
                writer_error.append("backup never started")
                return
            try:
                with connected(self.source, timeout=5) as connection:
                    connection.execute("INSERT INTO tickets VALUES (3, 'Concurrent write')")
                    connection.execute("INSERT INTO notes VALUES (3, 3, 'Concurrent note')")
            except Exception as error:
                writer_error.append(str(error))
            finally:
                writer_done.set()

        thread = threading.Thread(target=writer)
        thread.start()
        first_progress = True
        progress_remaining = []
        writer_finished_during_backup = []

        def progress(_status, _remaining, _total):
            nonlocal first_progress
            if first_progress:
                first_progress = False
                progress_remaining.append(_remaining)
                started.set()
                writer_finished_during_backup.append(writer_done.wait(4))

        try:
            result = create_database_snapshot(
                self.source, self.backups, "F7Hub-Database-concurrent.db",
                progress=progress,
            )
        finally:
            thread.join(6)
        self.assertFalse(thread.is_alive())
        self.assertFalse(writer_error, writer_error)
        self.assertTrue(writer_done.is_set())
        self.assertEqual(len(progress_remaining), 1)
        self.assertGreater(progress_remaining[0], 0)
        self.assertEqual(writer_finished_during_backup, [True])
        with connected(self.source) as connection:
            source_tickets = dict(connection.execute("SELECT id, subject FROM tickets"))
            source_notes = {
                row[0]: (row[1], row[2])
                for row in connection.execute("SELECT id, ticket_id, body FROM notes")
            }
        self.assertEqual(source_tickets[3], "Concurrent write")
        self.assertEqual(source_notes[3], (3, "Concurrent note"))
        with connected(result) as snapshot:
            self.assertEqual(validate_database_integrity(snapshot), (("ok",), ()))
            snapshot_tickets = dict(snapshot.execute("SELECT id, subject FROM tickets"))
            snapshot_notes = {
                row[0]: (row[1], row[2])
                for row in snapshot.execute("SELECT id, ticket_id, body FROM notes")
            }
        self.assertEqual(snapshot_tickets[1], "Printer offline")
        self.assertEqual(snapshot_tickets[2], "Before backup")
        self.assertEqual(snapshot_notes[1], (1, "Investigate cable"))
        self.assertIn(set(snapshot_tickets), ({1, 2}, {1, 2, 3}))
        self.assertEqual(set(snapshot_notes), {1} | ({3} if 3 in snapshot_tickets else set()))
        if 3 in snapshot_tickets:
            self.assertEqual(snapshot_tickets[3], "Concurrent write")
            self.assertEqual(snapshot_notes[3], (3, "Concurrent note"))
        self.assertFalse(self.temp_files())


if __name__ == "__main__":
    unittest.main()
