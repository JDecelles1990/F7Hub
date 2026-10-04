"""Isolated registry-to-process diagnostic workflow and SQLite read-only evidence."""

import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, validate_database_integrity, database_connection
from f7hub.infrastructure.powershell_gateway import PowerShellGateway
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.script_service import ScriptService
from f7hub.services.powershell_service import PowerShellService, SYSTEM_SNAPSHOT_CODE
from f7hub.domain.diagnostic_results import LOCAL_BASELINE_PACK


ROOT = Path(__file__).resolve().parents[2]


class ScriptExecutionWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name)/"isolated.db"
        bootstrap_database(self.database, ROOT/"Database/Migrations")
        self.scripts = ScriptService(ScriptRepository(self.database), ROOT)
        self.service = PowerShellService(self.scripts, PowerShellGateway())

    def snapshot(self):
        with database_connection(self.database) as connection:
            return tuple(connection.iterdump())

    def test_real_standard_user_execution_does_not_write_database(self):
        before = self.snapshot()
        result = self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE)
        self.assertEqual(result.classification, "COMPLETED", result.message)
        self.assertIsNotNone(result.diagnostic)
        self.assertIn(result.diagnostic.status, ("PASS", "WARNING"))
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.cleanup_verified)
        self.assertEqual(self.snapshot(), before)
        with database_connection(self.database) as connection:
            validate_database_integrity(connection)

    def test_disabled_and_wrong_scope_registrations_never_execute(self):
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET is_enabled=0 WHERE script_code=?",(SYSTEM_SNAPSHOT_CODE,))
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "NOT_ELIGIBLE")

    def test_tampered_source_fails_closed_and_copy_boundary_still_applies(self):
        fixture = Path(self.temp.name)/"checkout"
        source = fixture/"PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
        source.parent.mkdir(parents=True)
        source.write_bytes((ROOT/"PowerShell/Diagnostics/Get-SystemSnapshot.ps1").read_bytes()+b"\r\n# tamper")
        service = PowerShellService(ScriptService(ScriptRepository(self.database),fixture), PowerShellGateway())
        self.assertEqual(service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "INTEGRITY_FAILED")

    def test_shared_copy_preserves_exact_crlf_bytes(self):
        source = self.scripts.read_verified_script(SYSTEM_SNAPSHOT_CODE).encode("utf-8")
        self.assertEqual(source, (ROOT/"PowerShell/Diagnostics/Get-SystemSnapshot.ps1").read_bytes())
        self.assertIn(b"\r\n", source)

    def test_real_three_member_pack_then_individuals_leave_logical_database_unchanged(self):
        before = self.snapshot()
        pack = self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
        self.assertEqual(pack.classification, "COMPLETED", pack.message)
        self.assertEqual(tuple(item.script_code for item in pack.diagnostics), LOCAL_BASELINE_PACK.diagnostic_codes)
        self.assertTrue(pack.cleanup_verified)
        self.assertEqual(pack.skipped_codes, ())
        self.assertIn(pack.collection_status, ("PASS", "WARNING", "ERROR"))
        for code in LOCAL_BASELINE_PACK.diagnostic_codes:
            run = self.service.execute_diagnostic(code)
            self.assertEqual(run.classification, "COMPLETED", run.message)
            self.assertTrue(run.cleanup_verified)
        self.assertEqual(self.snapshot(), before)
        with database_connection(self.database) as connection:
            validate_database_integrity(connection)

    def test_pack_rechecks_registry_after_readiness(self):
        self.assertTrue(self.service.pack_readiness()[0])
        middle = LOCAL_BASELINE_PACK.diagnostic_codes[1]
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET is_enabled=0 WHERE script_code=?", (middle,))
        before = self.snapshot()
        result = self.service.execute_diagnostic_pack(LOCAL_BASELINE_PACK.code)
        self.assertEqual(result.classification, "ABORTED")
        self.assertIsNone(result.collection_status)
        self.assertEqual(result.failure_classification, "NOT_ELIGIBLE")
        self.assertEqual(result.aborted_at, middle)
        self.assertEqual(result.skipped_codes, LOCAL_BASELINE_PACK.diagnostic_codes[2:])
        self.assertEqual(self.snapshot(), before)
