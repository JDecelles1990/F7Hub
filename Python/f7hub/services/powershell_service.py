"""Eligibility and strict result validation for the one reviewed Slice 052 diagnostic."""

from __future__ import annotations

from datetime import datetime
import json
import re
import unicodedata

from f7hub.domain.diagnostic_results import DiagnosticResult, ScriptDiagnosticRunResult
from f7hub.services.script_service import ScriptCopyError, ScriptReadError


SYSTEM_SNAPSHOT_CODE = "diagnostic.windows.system_snapshot"
SYSTEM_SNAPSHOT_DIGEST = "7389e1b402050da4811270d71b92b1a1c53fff151e5300c2b2c6bdbc3fcef758"
SYSTEM_SNAPSHOT_PATH = "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
MESSAGES = {
    "NOT_ELIGIBLE": "This registration is not approved for execution. Refresh Scripts and check its metadata.",
    "INTEGRITY_FAILED": "The script could not be verified. Restore the reviewed file before running.",
    "REGISTRATION_CHANGED": "Registration changed during preparation. Refresh Scripts before running again.",
    "PRIVILEGE_BLOCKED": "Run F7Hub as a standard user. Elevated or unverified execution is blocked.",
    "RUNTIME_UNAVAILABLE": "Install the standard 64-bit PowerShell 7 runtime under Program Files with trusted permissions.",
    "PREPARATION_FAILED": "The diagnostic could not be securely prepared. Check local file access before retrying.",
    "LAUNCH_FAILED": "PowerShell could not start safely. Check installation permissions and execution policy.",
    "TIMEOUT": "The diagnostic exceeded its time limit. Owned processes were stopped.",
    "OUTPUT_LIMIT_EXCEEDED": "PowerShell output exceeded the allowed size. Owned processes were stopped.",
    "OUTPUT_CAPTURE_FAILED": "PowerShell output could not be captured safely.",
    "INVALID_OUTPUT": "PowerShell did not return a valid System Snapshot result. Check runtime and execution policy.",
    "CLEANUP_FAILED": "Diagnostic cleanup could not be verified. Further execution is blocked; close F7Hub and reconcile owned resources.",
    "EXECUTION_BUSY": "Another diagnostic is already running.",
}


def eligible(record):
    return (
        record is not None and record.script_code == SYSTEM_SNAPSHOT_CODE
        and record.relative_path == SYSTEM_SNAPSHOT_PATH and record.version == "1.0.0"
        and record.runtime == "POWERSHELL_7" and record.script_type == "DIAGNOSTIC"
        and record.risk_level == "LOW" and record.privilege_level == "STANDARD_USER"
        and type(record.is_enabled) is int and record.is_enabled == 1
        and type(record.requires_structured_output) is int and record.requires_structured_output == 1
        and type(record.timeout_seconds) is int and 0 < record.timeout_seconds <= 60
        and isinstance(record.checksum_sha256, str)
        and record.checksum_sha256.lower() == SYSTEM_SNAPSHOT_DIGEST
    )


class PowerShellService:
    def __init__(self, script_service, gateway):
        self._scripts, self._gateway = script_service, gateway

    def execute_diagnostic(self, script_code):
        def failure(code, process=None):
            return ScriptDiagnosticRunResult(script_code, SYSTEM_SNAPSHOT_DIGEST if script_code == SYSTEM_SNAPSHOT_CODE else None,
                code, MESSAGES[code], duration_seconds=0 if process is None else process.duration_seconds,
                exit_code=None if process is None else process.exit_code,
                cleanup_verified=True if process is None else process.cleanup_verified)

        if not isinstance(script_code, str) or script_code != SYSTEM_SNAPSHOT_CODE:
            return failure("NOT_ELIGIBLE")
        try:
            entry = self._scripts.get_script(script_code)
            if entry is None or not eligible(entry.metadata):
                return failure("NOT_ELIGIBLE")
            candidate = self._scripts.prepare_verified_script(script_code, for_execution=True)
            if not eligible(candidate.metadata) or candidate.metadata != entry.metadata:
                return failure("REGISTRATION_CHANGED")

            def revalidate():
                # No connection/transaction is retained through process execution.
                current = self._scripts.get_script(script_code)
                return current is not None and eligible(current.metadata) and current.metadata == candidate.metadata

            process = self._gateway.execute(candidate, candidate.metadata.timeout_seconds, revalidate)
        except ScriptCopyError:
            return failure("INTEGRITY_FAILED")
        except ScriptReadError:
            return failure("NOT_ELIGIBLE")
        except OSError:
            return failure("PREPARATION_FAILED")
        if not process.cleanup_verified:
            return failure("CLEANUP_FAILED", process)
        if process.classification != "COMPLETED":
            return failure(process.classification if process.classification in MESSAGES else "LAUNCH_FAILED", process)
        try:
            diagnostic = validate_system_snapshot(process.stdout, process.stderr, process.exit_code)
        except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
            return failure("INVALID_OUTPUT", process)
        return ScriptDiagnosticRunResult(script_code, SYSTEM_SNAPSHOT_DIGEST, "COMPLETED", diagnostic.message,
            diagnostic, process.duration_seconds, process.exit_code, process.cleanup_verified)


def _text(value, *, nullable=False, limit=2048):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value or len(value) > limit:
        raise ValueError("Invalid text")
    if any(unicodedata.category(character).startswith("C") and character not in "\n\r\t" for character in value):
        raise ValueError("Invalid Unicode")


def _integer(value, *, nullable=False):
    if value is None and nullable:
        return
    if type(value) is not int or not 0 <= value < 2**63:
        raise ValueError("Invalid measurement")


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected.split()):
        raise ValueError("Invalid object")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate key")
        result[key] = value
    return result


def validate_system_snapshot(stdout, stderr, exit_code):
    if not stdout or len(stdout) > 1024 * 1024 or stderr or type(exit_code) is not int:
        raise ValueError("Invalid process output")
    source = stdout.decode("utf-8", errors="strict")
    # Bound nesting before parsing, ignoring braces within strings and escapes.
    depth, in_string, escape = 0, False, False
    for character in source:
        if in_string:
            if escape:
                escape = False
            elif character == "\\":
                escape = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > 12:
                raise ValueError("Excessive nesting")
        elif character in "]}":
            depth -= 1
    result = json.loads(source, object_pairs_hook=_pairs, parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("Nonfinite value")))
    _keys(result, "schemaVersion operation success status message data warnings errors")
    if type(result["schemaVersion"]) is not int or result["schemaVersion"] != 1 or result["operation"] != "Get-SystemSnapshot":
        raise ValueError("Wrong contract")
    status, success = result["status"], result["success"]
    if status not in ("PASS", "WARNING", "ERROR") or type(success) is not bool:
        raise ValueError("Invalid severity")
    if success != (status != "ERROR") or exit_code != (0 if success else 1):
        raise ValueError("Inconsistent execution outcome")
    _text(result["message"])
    for field in ("warnings", "errors"):
        values = result[field]
        if not isinstance(values, list) or len(values) > 64:
            raise ValueError("Invalid messages")
        for value in values:
            _text(value)
    if ((status == "PASS" and (result["warnings"] or result["errors"]))
            or (status == "WARNING" and (not result["warnings"] or result["errors"]))
            or (status == "ERROR" and (not result["errors"] or result["warnings"]))):
        raise ValueError("Inconsistent messages")
    data = result["data"]
    _keys(data, "computerName windowsCaption windowsVersion windowsBuild osArchitecture lastBootUtc uptimeSeconds powerShellVersion physicalMemoryBytes fixedDrives")
    for field in ("computerName", "windowsCaption", "windowsVersion", "windowsBuild", "osArchitecture", "lastBootUtc"):
        _text(data[field], nullable=not success, limit=1024)
    _text(data["powerShellVersion"], limit=64)
    if re.fullmatch(r"7\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", data["powerShellVersion"]) is None:
        raise ValueError("Unexpected runtime")
    if data["lastBootUtc"] is not None:
        stamp = datetime.fromisoformat(data["lastBootUtc"].replace("Z", "+00:00"))
        if stamp.utcoffset() is None:
            raise ValueError("Unqualified boot time")
    for field in ("uptimeSeconds", "physicalMemoryBytes"):
        _integer(data[field], nullable=not success)
    drives = data["fixedDrives"]
    if not isinstance(drives, list) or len(drives) > 64 or (not success and drives):
        raise ValueError("Invalid drives")
    devices = []
    for drive in drives:
        _keys(drive, "device capacityBytes freeBytes")
        _text(drive["device"], limit=2)
        if re.fullmatch("[A-Z]:", drive["device"]) is None:
            raise ValueError("Invalid device")
        devices.append(drive["device"])
        for field in ("capacityBytes", "freeBytes"):
            _integer(drive[field], nullable=status == "WARNING")
    if devices != sorted(set(devices)):
        raise ValueError("Unordered or repeated drives")
    return DiagnosticResult(result["operation"], status, result["message"], data,
                            tuple(result["warnings"]), tuple(result["errors"]))
