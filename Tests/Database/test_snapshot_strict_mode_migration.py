"""Forward-only approval of the three strict-mode diagnostic source identities."""
from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import MigrationApplicationError
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.powershell_service import APPROVED_DIAGNOSTICS, eligible
from f7hub.services.script_service import ScriptCopyError, ScriptService


ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / 'Database/Migrations'
OLD = {
    'diagnostic.windows.system_snapshot': '7389e1b402050da4811270d71b92b1a1c53fff151e5300c2b2c6bdbc3fcef758',
    'diagnostic.windows.network_snapshot': 'aa126985b01c840b588ee3769d4c0a4a43e57ae5415f422cc8c9db1bafcb02b7',
    'diagnostic.windows.services_snapshot': '8a48321800e4d8147f2dd94a9d83eebedace6ac4e45b3e38c00f74d280abc347',
}


class SnapshotStrictModeMigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / 'catalog.db'
        self.migrations = self.root / 'migrations'
        self.migrations.mkdir()
        for source in MIGRATIONS.glob('*.sql'):
            if int(source.name[:4]) <= 11:
                shutil.copyfile(source, self.migrations / source.name)

    def install(self):
        shutil.copyfile(MIGRATIONS / '0012_snapshot_strict_mode_digests.sql',
                        self.migrations / '0012_snapshot_strict_mode_digests.sql')
        return bootstrap_database(self.database, self.migrations)

    def state(self):
        with database_connection(self.database) as connection:
            return (
                tuple(tuple(row) for row in connection.execute('SELECT * FROM scripts ORDER BY script_id')),
                tuple(tuple(row) for row in connection.execute('SELECT * FROM schema_migrations ORDER BY version')),
            )

    def assert_integrity(self):
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_fresh_and_incremental_are_exact_and_idempotent(self):
        self.assertEqual(self.install().migration_result.applied_versions, tuple(range(1, 13)))
        current = self.state()
        self.assertEqual(self.install().migration_result.applied_versions, ())
        self.assertEqual(self.state(), current)
        self.assertEqual(set(APPROVED_DIAGNOSTICS), set(OLD))
        repository = ScriptRepository(self.database)
        for code, spec in APPROVED_DIAGNOSTICS.items():
            with self.subTest(code=code):
                content = (ROOT / spec.relative_path).read_bytes()
                self.assertIn(b'Set-StrictMode -Version Latest', content)
                self.assertEqual(hashlib.sha256(content).hexdigest(), spec.digest)
                self.assertNotEqual(spec.digest, OLD[code])
                record = repository.get_script(code)
                self.assertEqual(record.checksum_sha256, spec.digest)
                self.assertTrue(eligible(record))
                self.assertFalse(eligible(replace(record, checksum_sha256=OLD[code])))
                self.assertEqual((record.script_type, record.runtime, record.risk_level, record.privilege_level),
                                 ('DIAGNOSTIC', 'POWERSHELL_7', 'LOW', 'STANDARD_USER'))
                target = self.root / spec.relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                self.assertEqual(ScriptService(repository, self.root).read_verified_script(code), content.decode())
                target.write_bytes(content + b'# changed\r\n')
                with self.assertRaises(ScriptCopyError):
                    ScriptService(repository, self.root).read_verified_script(code)
        self.assert_integrity()

        self.database = self.root / 'incremental.db'
        (self.migrations / '0012_snapshot_strict_mode_digests.sql').unlink()
        bootstrap_database(self.database, self.migrations)
        with database_connection(self.database) as connection:
            connection.execute("INSERT INTO scripts (script_code,name,relative_path,script_type,created_at,updated_at) "
                               "VALUES ('user.script','User','PowerShell/Reports/User.ps1','REPORT','a','a')")
        before, history = self.state()
        self.assertEqual(self.install().migration_result.applied_versions, (12,))
        after, new_history = self.state()
        self.assertEqual(len(after), len(before))
        self.assertEqual(new_history[:len(history)], history)
        self.assertEqual(tuple(row for row in after if row[3] == 'user.script'),
                         tuple(row for row in before if row[3] == 'user.script'))
        self.assert_integrity()

    def test_conflict_rolls_back_all_digest_updates(self):
        for code in OLD:
            with self.subTest(code=code):
                self.database = self.root / (code.rsplit('.', 1)[-1] + '.db')
                (self.migrations / '0012_snapshot_strict_mode_digests.sql').unlink(missing_ok=True)
                bootstrap_database(self.database, self.migrations)
                with database_connection(self.database) as connection:
                    connection.execute('UPDATE scripts SET checksum_sha256=? WHERE script_code=?', ('0' * 64, code))
                before = self.state()
                with self.assertRaises(MigrationApplicationError):
                    self.install()
                self.assertEqual(self.state(), before)
                self.assert_integrity()


if __name__ == '__main__':
    unittest.main()
