"""Eligibility and untrusted-output regression coverage without launching processes."""

from dataclasses import replace
import json
from types import SimpleNamespace
import unittest

from f7hub.domain.diagnostic_results import PowerShellProcessResult
from f7hub.services.powershell_service import (
    PowerShellService, SYSTEM_SNAPSHOT_CODE, SYSTEM_SNAPSHOT_PATH,
    SYSTEM_SNAPSHOT_DIGEST, validate_system_snapshot,
)
from f7hub.repositories.script_repository import ScriptRecord
from f7hub.services.script_service import ScriptCatalogEntry, VerifiedScriptCandidate, ScriptCopyError


def record():
    return ScriptRecord(1, None, None, SYSTEM_SNAPSHOT_CODE, "Windows System Snapshot", "description",
        SYSTEM_SNAPSHOT_PATH, "DIAGNOSTIC", "POWERSHELL_7", "LOW", "STANDARD_USER", "1.0.0",
        SYSTEM_SNAPSHOT_DIGEST, 60, 1, 1, "created", "updated")


def envelope(status="PASS"):
    success = status != "ERROR"
    return dict(schemaVersion=1, operation="Get-SystemSnapshot", success=success, status=status,
        message="Collected" if success else "Required collection failed",
        warnings=["Optional measurement unavailable"] if status == "WARNING" else [],
        errors=["Required collection unavailable"] if not success else [],
        data=dict(computerName="PC" if success else None, windowsCaption="Windows" if success else None,
                  windowsVersion="10.0" if success else None, windowsBuild="1" if success else None,
                  osArchitecture="64-bit" if success else None,
                  lastBootUtc="2026-10-03T00:00:00.000Z" if success else None,
                  uptimeSeconds=0 if success else None, powerShellVersion="7.6.6",
                  physicalMemoryBytes=0 if success else None, fixedDrives=[]))


class Scripts:
    def __init__(self):
        self.record = record()
        self.prepared = None
        self.error = None

    def get_script(self, code):
        return None if self.record is None else ScriptCatalogEntry(self.record, "AVAILABLE")

    def prepare_verified_script(self, code, *, for_execution):
        assert for_execution
        if self.error:
            raise self.error
        return VerifiedScriptCandidate(self.prepared or self.record, b"reviewed", None)


class Gateway:
    def __init__(self):
        self.calls = 0
        self.on_prepared = None
        self.result = PowerShellProcessResult("COMPLETED", json.dumps(envelope()).encode(), exit_code=0)

    def execute(self, candidate, timeout, revalidate):
        self.calls += 1
        if self.on_prepared:
            self.on_prepared()
        if not revalidate():
            return PowerShellProcessResult("REGISTRATION_CHANGED")
        return self.result


class PowerShellServiceTests(unittest.TestCase):
    def setUp(self):
        self.scripts, self.gateway = Scripts(), Gateway()
        self.service = PowerShellService(self.scripts, self.gateway)

    def test_only_system_snapshot_manifest_code(self):
        for code in ("diagnostic.windows.network_snapshot", "x", "", None, ["x"]):
            with self.subTest(code=code):
                self.assertEqual(self.service.execute_diagnostic(code).classification, "NOT_ELIGIBLE")
        self.assertEqual(self.gateway.calls, 0)

    def test_missing_registration(self):
        self.scripts.record = None
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "NOT_ELIGIBLE")
        self.assertEqual(self.gateway.calls, 0)

    def test_each_security_metadata_requirement(self):
        for field, values in {
            "relative_path": ["PowerShell/Reports/Get-SystemSnapshot.ps1"], "version": [None, "2.0.0"],
            "runtime": ["POWERSHELL_5"], "script_type": ["UTILITY"], "risk_level": ["HIGH"],
            "privilege_level": ["LOCAL_ADMIN"], "is_enabled": [0, True],
            "requires_structured_output": [0, True], "timeout_seconds": [0, -1, 61, True, 1.5],
            "checksum_sha256": [None, "bad", "0" * 64],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.scripts.record = replace(record(), **{field: value})
                    self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "NOT_ELIGIBLE")
        self.assertEqual(self.gateway.calls, 0)

    def test_preparation_metadata_drift(self):
        self.scripts.prepared = replace(record(), updated_at="new")
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "REGISTRATION_CHANGED")
        self.assertEqual(self.gateway.calls, 0)

    def test_immediately_prelaunch_metadata_drift(self):
        self.gateway.on_prepared = lambda: setattr(self.scripts, "record", replace(record(), is_enabled=0))
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "REGISTRATION_CHANGED")

    def test_source_integrity_failure_never_launches(self):
        self.scripts.error = ScriptCopyError("INTEGRITY_MISMATCH")
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "INTEGRITY_FAILED")
        self.assertEqual(self.gateway.calls, 0)

    def test_valid_diagnostic_error_is_completed(self):
        self.gateway.result = PowerShellProcessResult("COMPLETED", json.dumps(envelope("ERROR")).encode(), exit_code=1)
        result = self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE)
        self.assertEqual(result.classification, "COMPLETED")
        self.assertEqual(result.diagnostic.status, "ERROR")

    def test_infrastructure_failures_and_cleanup_independence(self):
        for code in ("TIMEOUT", "LAUNCH_FAILED", "OUTPUT_LIMIT_EXCEEDED", "PRIVILEGE_BLOCKED", "RUNTIME_UNAVAILABLE"):
            self.gateway.result = PowerShellProcessResult(code)
            self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, code)
        self.gateway.result = replace(self.gateway.result, cleanup_verified=False)
        self.assertEqual(self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE).classification, "CLEANUP_FAILED")

    def test_invalid_output_is_safe(self):
        self.gateway.result = PowerShellProcessResult("COMPLETED", b"private arbitrary output", exit_code=0)
        result = self.service.execute_diagnostic(SYSTEM_SNAPSHOT_CODE)
        self.assertEqual(result.classification, "INVALID_OUTPUT")
        self.assertNotIn("private", result.message)


class SystemSnapshotContractTests(unittest.TestCase):
    def validate(self, value, exit_code=0):
        return validate_system_snapshot(json.dumps(value).encode(), b"", exit_code)

    def test_all_supported_severities(self):
        for status in ("PASS", "WARNING", "ERROR"):
            self.assertEqual(self.validate(envelope(status), int(status == "ERROR")).status, status)

    def test_zero_and_null_are_distinct(self):
        value = envelope("WARNING")
        value["data"]["fixedDrives"] = [dict(device="C:", capacityBytes=0, freeBytes=None)]
        self.assertEqual(self.validate(value).data["fixedDrives"][0]["capacityBytes"], 0)
        self.assertIsNone(self.validate(value).data["fixedDrives"][0]["freeBytes"])

    def test_duplicate_keys_extra_output_encoding_and_depth(self):
        for data in (b'{"schemaVersion":1,"schemaVersion":1}', b'{}\n{}', b'\xff',
                     b'[' * 13 + b']' * 13, b'x' * (1024 * 1024 + 1), b'{"x":NaN}'):
            with self.subTest(data=data[:30]), self.assertRaises(ValueError):
                validate_system_snapshot(data, b"", 0)

    def test_wrong_fields_types_status_and_exit(self):
        for field, value in (("schemaVersion", True), ("schemaVersion", 2), ("operation", "wrong"),
                             ("status", "FAIL"), ("success", 1), ("success", False),
                             ("message", "\u202eevil"), ("message", "\ud800"),
                             ("warnings", "text"), ("errors", ["error"])):
            result = envelope()
            result[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.validate(result)
        with self.assertRaises(ValueError):
            self.validate(envelope(), 1)
        with self.assertRaises(ValueError):
            validate_system_snapshot(json.dumps(envelope()).encode(), b"stderr", 0)

    def test_wrong_data_types_bounds_and_missing_keys(self):
        for field, value in (("uptimeSeconds", True), ("physicalMemoryBytes", -1),
                             ("computerName", None), ("powerShellVersion", "5.1.0"),
                             ("lastBootUtc", "2026-10-03"), ("fixedDrives", {})):
            result = envelope()
            result["data"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(result)
        value = envelope()
        value["extra"] = True
        with self.assertRaises(ValueError):
            self.validate(value)

    def test_drive_validation(self):
        for drives in ([dict(device="C:", capacityBytes=None, freeBytes=0)],
                       [dict(device="C:", capacityBytes=True, freeBytes=0)],
                       [dict(device="C:", capacityBytes=0, freeBytes=0)] * 2,
                       [dict(device="<html>", capacityBytes=0, freeBytes=0)]):
            value = envelope()
            value["data"]["fixedDrives"] = drives
            with self.assertRaises(ValueError):
                self.validate(value)
