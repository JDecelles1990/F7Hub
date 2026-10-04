"""Atomic built-in registration, checkout integrity and existing copy boundary."""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import MigrationApplicationError
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.script_service import ScriptService, ScriptCopyError

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Database/Migrations'
PATH = 'PowerShell/Diagnostics/Get-ServicesSnapshot.ps1'
CODE = 'diagnostic.windows.services_snapshot'
APPROVED = '8a48321800e4d8147f2dd94a9d83eebedace6ac4e45b3e38c00f74d280abc347'
MIGRATION = '0011_services_snapshot_script.sql'

class ServicesSnapshotMigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / 'catalog.db'
        self.migrations = self.root / 'migrations'
        self.migrations.mkdir()
        for source in SOURCE.glob('*.sql'):
            if int(source.name[:4]) <= 10:
                shutil.copyfile(source, self.migrations / source.name)

    def install(self):
        shutil.copyfile(SOURCE / MIGRATION, self.migrations / MIGRATION)
        return bootstrap_database(self.database, self.migrations)

    def state(self):
        with database_connection(self.database) as connection:
            return (tuple(tuple(r) for r in connection.execute('SELECT * FROM scripts ORDER BY script_id')),
                    tuple(tuple(r) for r in connection.execute('SELECT * FROM schema_migrations ORDER BY version')))

    def assert_integrity(self):
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(connection.execute('PRAGMA foreign_keys').fetchone()[0], 1)

    def test_fresh_registration_metadata_checksum_and_idempotence(self):
        self.assertEqual(self.install().migration_result.applied_versions, tuple(range(1, 12)))
        before = self.state()
        self.assertEqual(self.install().migration_result.applied_versions, ())
        self.assertEqual(self.state(), before)
        row = ScriptRepository(self.database).get_script(CODE)
        self.assertEqual((row.name, row.description, row.relative_path), (
            'Windows Services Snapshot', 'Collects a local read-only Windows services snapshot.', PATH))
        self.assertEqual((row.script_type, row.runtime, row.risk_level, row.privilege_level, row.version,
                          row.timeout_seconds, row.requires_structured_output, row.is_enabled),
                         ('DIAGNOSTIC', 'POWERSHELL_7', 'LOW', 'STANDARD_USER', '1.0.0', 60, 1, 1))
        self.assertIsNone(row.category_id)
        self.assertEqual(row.checksum_sha256, APPROVED)
        self.assertEqual(row.created_at, '2026-10-03T00:00:00.000Z')
        self.assertEqual(row.updated_at, row.created_at)
        content = (ROOT / PATH).read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(), APPROVED)
        self.assertFalse(content.startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\n', content.replace(b'\r\n', b''))
        self.assert_integrity()

    def test_incremental_preserves_existing_rows_defaults_and_history(self):
        bootstrap_database(self.database, self.migrations)
        with database_connection(self.database) as connection:
            connection.execute("INSERT INTO scripts (script_code,name,relative_path,script_type,created_at,updated_at) "
                               "VALUES ('user.script','User','PowerShell/Reports/User.ps1','REPORT','a','a')")
        rows, history = self.state()
        self.assertEqual(self.install().migration_result.applied_versions, (11,))
        after_rows, after_history = self.state()
        self.assertEqual(after_rows[:len(rows)], rows)
        self.assertEqual(after_history[:len(history)], history)
        self.assertEqual(len(after_rows), len(rows) + 1)
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT is_enabled,checksum_sha256 FROM scripts WHERE script_code='user.script'").fetchone()[:], (0, None))
            self.assertEqual(connection.execute("SELECT count(*) FROM categories WHERE scope='SCRIPT'").fetchone()[0], 0)
        self.assert_integrity()

    def test_conflicts_case_and_separator_variants_rollback_without_adoption(self):
        cases = [(CODE, 'PowerShell/Reports/User.ps1'), (CODE.upper(), 'PowerShell/Reports/User.ps1'),
                 ('user.script', PATH), ('user.script', PATH.upper()),
                 ('user.script', PATH.replace('/', '\\')), ('user.script', PATH.upper().replace('/', '\\'))]
        for index, (code, path) in enumerate(cases):
            with self.subTest(code=code, path=path):
                self.database = self.root / f'conflict{index}.db'
                (self.migrations / MIGRATION).unlink(missing_ok=True)
                bootstrap_database(self.database, self.migrations)
                with database_connection(self.database) as connection:
                    connection.execute("INSERT INTO scripts (script_code,name,relative_path,script_type,checksum_sha256,created_at,updated_at) "
                                       "VALUES (?, 'User', ?, 'REPORT', ?, 'a','a')", (code, path, APPROVED))
                before = self.state()
                with self.assertRaises(MigrationApplicationError):
                    self.install()
                self.assertEqual(self.state(), before)
                self.assert_integrity()

    def test_exact_copy_changed_bytes_and_lf_only_fail_closed(self):
        self.install()
        target = self.root / PATH
        target.parent.mkdir(parents=True)
        content = (ROOT / PATH).read_bytes()
        target.write_bytes(content)
        service = ScriptService(ScriptRepository(self.database), self.root)
        self.assertEqual(service.read_verified_script(CODE), content.decode('utf-8'))
        before = self.state()
        for changed in (content + b'# changed\r\n', content.replace(b'\r\n', b'\n')):
            target.write_bytes(changed)
            with self.assertRaises(ScriptCopyError) as caught:
                service.read_verified_script(CODE)
            self.assertEqual(caught.exception.code, 'INTEGRITY_MISMATCH')
            self.assertEqual(self.state(), before)
        target.write_bytes(content)
        self.assertEqual(service.read_verified_script(CODE), content.decode('utf-8'))

    def test_attribute_checkout_forces_crlf_without_autocrlf(self):
        checkout = self.root / 'checkout'
        checkout.mkdir()
        subprocess.run(['git', 'init', '--quiet', str(checkout)], check=True)
        target = checkout / PATH
        target.parent.mkdir(parents=True)
        content = (ROOT / PATH).read_bytes()
        normalized = content.replace(b'\r\n', b'\n')
        target.write_bytes(normalized)
        (checkout / '.gitattributes').write_bytes((ROOT / '.gitattributes').read_bytes())
        subprocess.run(['git', '-c', 'core.autocrlf=false', 'add', '--', '.gitattributes', PATH],
                       cwd=checkout, check=True, capture_output=True)
        blob = subprocess.check_output(['git', 'show', ':' + PATH], cwd=checkout)
        self.assertEqual(blob, normalized)
        target.unlink()
        subprocess.run(['git', '-c', 'core.autocrlf=false', 'checkout-index', '-f', '--', PATH],
                       cwd=checkout, check=True, capture_output=True)
        self.assertEqual(target.read_bytes(), content)
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), APPROVED)

if __name__ == '__main__':
    unittest.main()
