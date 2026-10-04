"""Guarded approval of the exact production script checkout bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import MigrationApplicationError


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Database/Migrations"
SCRIPT = ROOT / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
CODE = "diagnostic.windows.system_snapshot"
APPROVED = "7389e1b402050da4811270d71b92b1a1c53fff151e5300c2b2c6bdbc3fcef758"


class SystemSnapshotChecksumTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / "catalog.db"
        self.migrations = self.root / "migrations"
        self.migrations.mkdir()
        for source in SOURCE.glob("*.sql"):
            if int(source.name[:4]) <= 8:
                shutil.copyfile(source, self.migrations / source.name)

    def approve(self):
        shutil.copyfile(SOURCE / "0009_system_snapshot_checksum.sql",
                        self.migrations / "0009_system_snapshot_checksum.sql")
        return bootstrap_database(self.database, self.migrations)

    def test_fresh_bootstrap_exact_bytes_and_repeat(self):
        result = self.approve()
        self.assertEqual(result.migration_result.applied_versions, tuple(range(1, 10)))
        self.assertEqual(bootstrap_database(self.database, self.migrations).migration_result.applied_versions, ())
        content = SCRIPT.read_bytes()
        self.assertFalse(content.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(content.count(b"\r\n"), content.count(b"\n"))
        self.assertNotEqual(hashlib.sha256(content).hexdigest(), APPROVED)  # 0012 approves current bytes.
        with database_connection(self.database) as connection:
            row = connection.execute("SELECT * FROM scripts WHERE script_code=?", (CODE,)).fetchone()
            self.assertEqual(row["checksum_sha256"], APPROVED)
            self.assertEqual(tuple(row[key] for key in (
                "name", "description", "relative_path", "script_type", "runtime", "risk_level",
                "privilege_level", "version", "timeout_seconds", "requires_structured_output",
                "is_enabled", "category_id", "created_at", "updated_at",
            )), (
                "Windows System Snapshot", "Collects a local read-only Windows system snapshot.",
                "PowerShell/Diagnostics/Get-SystemSnapshot.ps1", "DIAGNOSTIC", "POWERSHELL_7",
                "LOW", "STANDARD_USER", "1.0.0", 60, 1, 1, None,
                "2026-09-30T00:00:00.000Z", "2026-09-30T00:00:00.000Z",
            ))
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations WHERE version=9").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_incremental_preserves_unrelated_default_disabled_row(self):
        bootstrap_database(self.database, self.migrations)
        with database_connection(self.database) as connection:
            connection.execute("INSERT INTO scripts (script_code,name,relative_path,script_type,created_at,updated_at) "
                               "VALUES ('user.script','User','PowerShell/Reports/User.ps1','REPORT','a','a')")
            before = tuple(connection.execute("SELECT * FROM scripts WHERE script_code='user.script'").fetchone())
        self.assertEqual(self.approve().migration_result.applied_versions, (9,))
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(connection.execute("SELECT * FROM scripts WHERE script_code='user.script'").fetchone()), before)
            self.assertEqual(connection.execute("SELECT is_enabled FROM scripts WHERE script_code='user.script'").fetchone()[0], 0)

    def test_missing_drifted_and_preapproved_rows_fail_and_rollback(self):
        for mutation in (
            "DELETE FROM scripts WHERE script_code='diagnostic.windows.system_snapshot'",
            "UPDATE scripts SET version='2.0' WHERE script_code='diagnostic.windows.system_snapshot'",
            "UPDATE scripts SET checksum_sha256='unexpected' WHERE script_code='diagnostic.windows.system_snapshot'",
        ):
            with self.subTest(mutation=mutation):
                database = self.root / f"drift{len(list(self.root.glob('drift*.db')))}.db"
                bootstrap_database(database, self.migrations)
                with database_connection(database) as connection:
                    connection.execute(mutation)
                    before = tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts"))
                shutil.copyfile(SOURCE / "0009_system_snapshot_checksum.sql",
                                self.migrations / "0009_system_snapshot_checksum.sql")
                with self.assertRaises(MigrationApplicationError):
                    bootstrap_database(database, self.migrations)
                with database_connection(database) as connection:
                    self.assertEqual(tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts")), before)
                    self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations WHERE version=9").fetchone()[0], 0)
                    self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                    self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                (self.migrations / "0009_system_snapshot_checksum.sql").unlink()

    def test_isolated_checkout_uses_crlf_with_autocrlf_disabled(self):
        checkout = self.root / "checkout"
        checkout.mkdir()
        subprocess.run(("git", "init", "--quiet", str(checkout)), check=True)
        relative = Path("PowerShell/Diagnostics/Get-SystemSnapshot.ps1")
        target = checkout / relative
        target.parent.mkdir(parents=True)
        blob = subprocess.run(("git", "show", "HEAD:PowerShell/Diagnostics/Get-SystemSnapshot.ps1"),
                              cwd=ROOT, capture_output=True, check=True).stdout
        target.write_bytes(blob)
        (checkout / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
        subprocess.run(("git", "-c", "core.autocrlf=false", "add", "--", ".gitattributes", relative.as_posix()),
                       cwd=checkout, check=True, capture_output=True)
        target.unlink()
        subprocess.run(("git", "-c", "core.autocrlf=false", "checkout-index", "-f", "--", relative.as_posix()),
                       cwd=checkout, check=True, capture_output=True)
        checked_out = target.read_bytes()
        self.assertEqual(hashlib.sha256(checked_out).hexdigest(), APPROVED)
        self.assertFalse(checked_out.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(checked_out.count(b"\r\n"), 85)
        self.assertEqual(checked_out.replace(b"\r\n", b"\n"), blob)


if __name__ == "__main__":
    unittest.main()
