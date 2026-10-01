"""Production reference-data migration 0008 and conflict rollback."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import MigrationApplicationError


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Database/Migrations"
CODE = "diagnostic.windows.system_snapshot"
PATH = "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
STAMP = "2026-09-30T00:00:00.000Z"


class SystemSnapshotMigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / "catalog.db"
        self.migrations = self.root / "migrations"
        self.migrations.mkdir()
        for source in SOURCE.glob("*.sql"):
            if int(source.name[:4]) <= 7:
                shutil.copyfile(source, self.migrations / source.name)

    def add_0008(self):
        name = "0008_system_snapshot_script.sql"
        shutil.copyfile(SOURCE / name, self.migrations / name)

    def versions(self):
        with database_connection(self.database) as connection:
            return tuple(row[0] for row in connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version"))

    def insert_user_script(self, code="user.script", path="PowerShell/Reports/User.ps1"):
        with database_connection(self.database) as connection:
            connection.execute(
                "INSERT INTO scripts (script_code, name, relative_path, script_type, created_at, updated_at) "
                "VALUES (?, 'User Script', ?, 'REPORT', ?, ?)",
                (code, path, STAMP, STAMP),
            )

    def assert_catalog(self, expected_count=1):
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM scripts").fetchone()[0], expected_count)
            self.assertEqual(connection.execute("SELECT count(*) FROM categories WHERE scope='SCRIPT'").fetchone()[0], 0)
            rows = connection.execute("SELECT * FROM scripts WHERE script_code=?", (CODE,)).fetchall()
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["name"], "Windows System Snapshot")
            self.assertEqual(row["relative_path"], PATH)
            self.assertEqual(row["description"], "Collects a local read-only Windows system snapshot.")
            self.assertEqual(tuple(row[key] for key in (
                "script_type", "runtime", "risk_level", "privilege_level", "version",
                "timeout_seconds", "requires_structured_output", "is_enabled",
            )), ("DIAGNOSTIC", "POWERSHELL_7", "LOW", "STANDARD_USER", "1.0.0", 60, 1, 1))
            self.assertIsNone(row["category_id"])
            self.assertIsNone(row["checksum_sha256"])
            self.assertEqual(row["created_at"], STAMP)
            self.assertEqual(row["updated_at"], STAMP)
            columns = {column[1]: column for column in connection.execute("PRAGMA table_info(scripts)")}
            self.assertEqual(columns["is_enabled"][4], "0")
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_fresh_bootstrap_and_idempotence(self):
        self.add_0008()
        first = bootstrap_database(self.database, self.migrations)
        second = bootstrap_database(self.database, self.migrations)
        self.assertEqual(first.migration_result.applied_versions, tuple(range(1, 9)))
        self.assertEqual(second.migration_result.applied_versions, ())
        self.assertEqual(self.versions(), tuple(range(1, 9)))
        self.assert_catalog()
        self.insert_user_script()
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT is_enabled FROM scripts WHERE script_code='user.script'").fetchone()[0], 0)

    def test_incremental_preserves_user_data(self):
        bootstrap_database(self.database, self.migrations)
        self.insert_user_script()
        self.add_0008()
        result = bootstrap_database(self.database, self.migrations)
        self.assertEqual(result.migration_result.applied_versions, (8,))
        self.assertEqual(self.versions(), tuple(range(1, 9)))
        self.assert_catalog(expected_count=2)
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(connection.execute("SELECT name, is_enabled FROM scripts WHERE script_code='user.script'").fetchone()),
                             ("User Script", 0))

    def test_conflicts_rollback_without_overwriting(self):
        for code, path in ((CODE, "PowerShell/Reports/User.ps1"), ("user.script", PATH)):
            with self.subTest(code=code, path=path):
                (self.migrations / "0008_system_snapshot_script.sql").unlink(missing_ok=True)
                database = self.root / ("code.db" if code == CODE else "path.db")
                bootstrap_database(database, self.migrations)
                with database_connection(database) as connection:
                    connection.execute(
                        "INSERT INTO scripts (script_code, name, relative_path, script_type, created_at, updated_at) "
                        "VALUES (?, 'User Script', ?, 'REPORT', ?, ?)", (code, path, STAMP, STAMP))
                    before = tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts"))
                self.add_0008()
                with self.assertRaises(MigrationApplicationError):
                    bootstrap_database(database, self.migrations)
                with database_connection(database) as connection:
                    self.assertEqual(tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts")), before)
                    self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations WHERE version=8").fetchone()[0], 0)
                    self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                    self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
