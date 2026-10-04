"""Literal diagnostic policy, strict output contracts and fixed sequential pack."""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from collections.abc import Callable
import ipaddress
import json
import re
import threading
import time
from types import MappingProxyType
import unicodedata

from f7hub.domain.diagnostic_results import (
    DiagnosticResult, ScriptDiagnosticRunResult, DiagnosticPackResult, LOCAL_BASELINE_PACK,
)
from f7hub.services.script_service import ScriptCopyError, ScriptReadError


SYSTEM_SNAPSHOT_CODE = "diagnostic.windows.system_snapshot"
SYSTEM_SNAPSHOT_DIGEST = "c2b3931341a0a6d7e858f8a728e50c9cdc1bfbb41dd5545588c24a11e5103e19"
SYSTEM_SNAPSHOT_PATH = "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
NETWORK_SNAPSHOT_CODE = "diagnostic.windows.network_snapshot"
SERVICES_SNAPSHOT_CODE = "diagnostic.windows.services_snapshot"
SERVICES_SNAPSHOT_DIGEST = "c747c65992518551c72e168e55ffc61bd1829572f804e318528d73fe53981a18"
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
    "INVALID_OUTPUT": "PowerShell did not return a valid diagnostic result. Check runtime and execution policy.",
    "CLEANUP_FAILED": "Diagnostic cleanup could not be verified. Further execution is blocked; close F7Hub and reconcile owned resources.",
    "EXECUTION_BUSY": "Another diagnostic is already running.",
}


@dataclass(frozen=True)
class _ApprovedDiagnosticSpec:
    script_code: str
    relative_path: str
    digest: str
    operation: str
    validator: Callable
    purpose: str
    version: str = "1.0.0"
    maximum_timeout: int = 60


def eligible(record):
    spec = APPROVED_DIAGNOSTICS.get(record.script_code) if record is not None and isinstance(record.script_code, str) else None
    return (
        spec is not None
        and record.relative_path == spec.relative_path and record.version == spec.version
        and record.runtime == "POWERSHELL_7" and record.script_type == "DIAGNOSTIC"
        and record.risk_level == "LOW" and record.privilege_level == "STANDARD_USER"
        and type(record.is_enabled) is int and record.is_enabled == 1
        and type(record.requires_structured_output) is int and record.requires_structured_output == 1
        and type(record.timeout_seconds) is int and 0 < record.timeout_seconds <= spec.maximum_timeout
        and isinstance(record.checksum_sha256, str)
        and record.checksum_sha256.lower() == spec.digest
    )


class PowerShellService:
    def __init__(self, script_service, gateway):
        self._scripts, self._gateway = script_service, gateway
        self._reservation = threading.Lock()
        self._cleanup_blocked = False

    @property
    def execution_blocked(self):
        return self._cleanup_blocked

    @staticmethod
    def execution_approved(record):
        """Advisory metadata policy; execution always checks current bytes/runtime."""
        return eligible(record)

    def pack_readiness(self):
        """Refresh-only member observations, independent of catalog search."""
        if self._cleanup_blocked:
            return False, MESSAGES["CLEANUP_FAILED"]
        for code in LOCAL_BASELINE_PACK.diagnostic_codes:
            entry = self._scripts.get_script(code)
            name = APPROVED_DIAGNOSTICS[code].operation.removeprefix("Get-")
            if entry is None:
                return False, f"{name} is missing or disabled. Refresh or check Manage scripts."
            if not eligible(entry.metadata):
                return False, f"{name} is not execution approved. Check its registration."
            if entry.file_status != "AVAILABLE":
                return False, f"{name} file is unavailable. Restore its reviewed source and refresh."
        return True, "Ready: 3 of 3 approved and available. Running rechecks source bytes and runtime."

    def _failure(self, script_code, code, process=None):
        spec = APPROVED_DIAGNOSTICS.get(script_code) if isinstance(script_code, str) else None
        return ScriptDiagnosticRunResult(script_code, None if spec is None else spec.digest,
            code, MESSAGES[code], duration_seconds=0 if process is None else process.duration_seconds,
            exit_code=None if process is None else process.exit_code,
            cleanup_verified=(not self._cleanup_blocked) if process is None else process.cleanup_verified)

    def execute_diagnostic(self, script_code):
        if not self._reservation.acquire(blocking=False):
            return self._failure(script_code, "EXECUTION_BUSY")
        try:
            return self._execute_member(script_code)
        finally:
            self._reservation.release()

    def execute_diagnostic_pack(self, pack_code):
        started = time.monotonic()
        codes = LOCAL_BASELINE_PACK.diagnostic_codes
        attempted = []

        def aborted(classification, at=None):
            return DiagnosticPackResult(pack_code, "ABORTED", None, MESSAGES[classification],
                tuple(attempted), time.monotonic() - started, at, classification,
                codes[len(attempted):], not self._cleanup_blocked and all(r.cleanup_verified for r in attempted))

        if not isinstance(pack_code, str) or pack_code != LOCAL_BASELINE_PACK.code:
            return aborted("NOT_ELIGIBLE")
        if not self._reservation.acquire(blocking=False):
            return aborted("EXECUTION_BUSY")
        try:
            if self._cleanup_blocked:
                return aborted("CLEANUP_FAILED")
            for code in codes:
                result = self._execute_member(code)
                attempted.append(result)
                if result.classification != "COMPLETED":
                    return aborted(result.classification, code)
            severity = max((r.diagnostic.status for r in attempted), key=("PASS", "WARNING", "ERROR").index)
            return DiagnosticPackResult(pack_code, "COMPLETED", severity,
                "Local Baseline Diagnostics completed. Results are kept in memory only.",
                tuple(attempted), time.monotonic() - started)
        finally:
            self._reservation.release()

    def _execute_member(self, script_code):
        def failure(code, process=None):
            return self._failure(script_code, code, process)

        if self._cleanup_blocked:
            return failure("CLEANUP_FAILED")
        spec = APPROVED_DIAGNOSTICS.get(script_code) if isinstance(script_code, str) else None
        if spec is None:
            return failure("NOT_ELIGIBLE")
        try:
            entry = self._scripts.get_script(script_code)
            if entry is None or entry.metadata.script_code != script_code or not eligible(entry.metadata):
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
            self._cleanup_blocked = True
            return failure("CLEANUP_FAILED", process)
        if process.classification != "COMPLETED":
            return failure(process.classification if process.classification in MESSAGES else "LAUNCH_FAILED", process)
        try:
            diagnostic = spec.validator(process.stdout, process.stderr, process.exit_code)
            if diagnostic.operation != spec.operation:
                raise ValueError("Wrong policy operation")
        except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
            return failure("INVALID_OUTPUT", process)
        return ScriptDiagnosticRunResult(script_code, spec.digest, "COMPLETED", diagnostic.message,
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


def _decode_output(stdout, stderr, exit_code, limit=1024 * 1024):
    if not stdout or len(stdout) > limit or stderr or type(exit_code) is not int:
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
    return json.loads(source, object_pairs_hook=_pairs, parse_constant=lambda _value: (_ for _ in ()).throw(ValueError("Nonfinite value")))


def validate_system_snapshot(stdout, stderr, exit_code):
    result = _decode_output(stdout, stderr, exit_code)
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


NETWORK_WARNINGS = (
    "One or more network metadata values are unavailable.",
    "One or more interface address collections are unavailable.",
    "One or more default gateway collections are unavailable.",
    "One or more DNS server collections are unavailable.",
    "Network snapshot output was limited to documented bounds.",
)
SERVICES_WARNINGS = (
    "One or more services metadata values are unavailable.",
    "Services snapshot output was limited to documented bounds.",
)


def _bounded_text(value, limit, *, nullable=True):
    if value is None and nullable:
        return
    _text(value, limit=limit)
    if not value.strip() or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("Unsafe text")
    if len(value.encode("utf-16-le", errors="strict")) > limit * 2:
        raise ValueError("Text exceeds UTF-16 bound")


def _snapshot_envelope(stdout, stderr, exit_code, operation, summaries, warnings, errors):
    # PowerShell emits one terminal line ending outside the document byte cap.
    document = stdout[:-2] if stdout.endswith(b"\r\n") else stdout[:-1] if stdout.endswith(b"\n") else stdout
    if len(stdout) > 524290 or len(document) > 524288:
        raise ValueError("Output too large")
    result = _decode_output(document, stderr, exit_code, 524288)
    _keys(result, "schemaVersion operation success status message data warnings errors")
    if type(result["schemaVersion"]) is not int or result["schemaVersion"] != 1 or result["operation"] != operation:
        raise ValueError("Wrong contract")
    status = result["status"]
    if status not in ("PASS", "WARNING", "ERROR") or type(result["success"]) is not bool:
        raise ValueError("Invalid status")
    if result["success"] != (status != "ERROR") or exit_code != int(status == "ERROR"):
        raise ValueError("Inconsistent outcome")
    if result["message"] != summaries[("PASS", "WARNING", "ERROR").index(status)]:
        raise ValueError("Invalid summary")
    for field in ("warnings", "errors"):
        if not isinstance(result[field], list) or not all(isinstance(v, str) for v in result[field]):
            raise ValueError("Invalid messages")
    observed = result["warnings"]
    if len(observed) > len(warnings) or any(v not in warnings for v in observed):
        raise ValueError("Unknown warning")
    if observed != [v for v in warnings if v in observed]:
        raise ValueError("Repeated/unordered warning")
    if ((status == "PASS" and (observed or result["errors"]))
            or (status == "WARNING" and (not observed or result["errors"]))
            or (status == "ERROR" and (observed or len(result["errors"]) != 1 or result["errors"][0] not in errors))):
        raise ValueError("Inconsistent messages")
    return result


def _require_warning(result, unavailable, warning):
    if result["success"] and unavailable and warning not in result["warnings"]:
        raise ValueError("Missing metadata warning")


def _diagnostic(result):
    return DiagnosticResult(result["operation"], result["status"], result["message"], result["data"],
                            tuple(result["warnings"]), tuple(result["errors"]))


def _addresses(value, family, limit, *, ordered=True):
    if value is None:
        return
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError("Invalid addresses")
    identities = []
    for text in value:
        _bounded_text(text, 64, nullable=False)
        if "%" in text:
            scope = text.rsplit("%", 1)[1]
            if not scope.isascii() or not scope.isdecimal() or int(scope) > 2**32 - 1:
                raise ValueError("Invalid scope")
        address = ipaddress.ip_address(text)
        if family is not None and address.version != family:
            raise ValueError("Wrong address family")
        identities.append((address.version, int(address), getattr(address, "scope_id", None)))
    if len(set(identities)) != len(identities) or (ordered and value != sorted(value)):
        raise ValueError("Repeated/unordered addresses")


def validate_network_snapshot(stdout, stderr, exit_code):
    result = _snapshot_envelope(stdout, stderr, exit_code, "Get-NetworkSnapshot", (
        "Local Windows network configuration snapshot collected.",
        "Network configuration collected with incomplete or bounded data.",
        "Unable to collect required local Windows network configuration.",
    ), NETWORK_WARNINGS, ("Required local network configuration is unavailable.",
                         "Network snapshot exceeded its output size limit."))
    data = result["data"]
    _keys(data, "computerName interfaces")
    _bounded_text(data["computerName"], 128)
    rows = data["interfaces"]
    if not isinstance(rows, list) or len(rows) > 64 or (not result["success"] and rows):
        raise ValueError("Invalid inventory")
    _require_warning(result, data["computerName"] is None, NETWORK_WARNINGS[0])
    indices = []
    for row in rows:
        _keys(row, "interfaceIndex interfaceDescription ipv4Addresses ipv6Addresses ipv4DefaultGateways ipv6DefaultGateways dnsServerAddresses dhcpEnabled")
        index = row["interfaceIndex"]
        if type(index) is not int or not 0 <= index <= 2**32 - 1:
            raise ValueError("Invalid interface identity")
        indices.append(index)
        _bounded_text(row["interfaceDescription"], 256)
        if row["dhcpEnabled"] is not None and type(row["dhcpEnabled"]) is not bool:
            raise ValueError("Invalid DHCP flag")
        _require_warning(result, row["interfaceDescription"] is None or row["dhcpEnabled"] is None, NETWORK_WARNINGS[0])
        for fields, cap, warning in ((('ipv4Addresses', 'ipv6Addresses'), 16, NETWORK_WARNINGS[1]),
                                     (('ipv4DefaultGateways', 'ipv6DefaultGateways'), 8, NETWORK_WARNINGS[2])):
            first, second = (row[field] for field in fields)
            if (first is None) != (second is None):
                raise ValueError("Inconsistent address collections")
            _addresses(first, 4, cap)
            _addresses(second, 6, cap)
            _require_warning(result, first is None, warning)
        _addresses(row["dnsServerAddresses"], None, 16, ordered=False)
        _require_warning(result, row["dnsServerAddresses"] is None, NETWORK_WARNINGS[3])
    if indices != sorted(set(indices)):
        raise ValueError("Repeated/unordered interfaces")
    return _diagnostic(result)


def validate_services_snapshot(stdout, stderr, exit_code):
    result = _snapshot_envelope(stdout, stderr, exit_code, "Get-ServicesSnapshot", (
        "Local Windows services snapshot collected.",
        "Services snapshot collected with incomplete or bounded data.",
        "Unable to collect required local Windows services information.",
    ), SERVICES_WARNINGS, ("Required local services information is unavailable.",
                          "Services snapshot exceeded its output size limit."))
    data = result["data"]
    _keys(data, "computerName services")
    _bounded_text(data["computerName"], 128)
    rows = data["services"]
    if not isinstance(rows, list) or len(rows) > 512 or (not result["success"] and rows):
        raise ValueError("Invalid service inventory")
    unavailable = data["computerName"] is None
    names = []
    for row in rows:
        _keys(row, "name displayName state startupMode")
        _bounded_text(row["name"], 256, nullable=False)
        _bounded_text(row["displayName"], 256)
        if row["state"] is not None and row["state"] not in (
                "Running", "Stopped", "Start Pending", "Stop Pending", "Continue Pending", "Pause Pending", "Paused"):
            raise ValueError("Invalid service state")
        if row["startupMode"] is not None and row["startupMode"] not in ("Auto", "Manual", "Disabled", "Boot", "System"):
            raise ValueError("Invalid startup mode")
        unavailable |= any(row[key] is None for key in ("displayName", "state", "startupMode"))
        names.append(row["name"])
    if (names != sorted(names, key=lambda v: v.encode("utf-16-be"))
            or len({v.casefold() for v in names}) != len(names)):
        raise ValueError("Repeated/unordered services")
    _require_warning(result, unavailable, SERVICES_WARNINGS[0])
    return _diagnostic(result)


APPROVED_DIAGNOSTICS = MappingProxyType({
    SYSTEM_SNAPSHOT_CODE: _ApprovedDiagnosticSpec(SYSTEM_SNAPSHOT_CODE, SYSTEM_SNAPSHOT_PATH,
        SYSTEM_SNAPSHOT_DIGEST, "Get-SystemSnapshot", validate_system_snapshot,
        "Collects OS, uptime, memory and fixed drives on this PC."),
    NETWORK_SNAPSHOT_CODE: _ApprovedDiagnosticSpec(NETWORK_SNAPSHOT_CODE,
        "PowerShell/Diagnostics/Get-NetworkSnapshot.ps1",
        "f0b81a4a73c0db35333245be2ea4d0de76dbbd85d24b97a8ed39f2c74155400c",
        "Get-NetworkSnapshot", validate_network_snapshot,
        "Collects local TCP/IP-enabled interface configuration; does not test connectivity."),
    SERVICES_SNAPSHOT_CODE: _ApprovedDiagnosticSpec(SERVICES_SNAPSHOT_CODE,
        "PowerShell/Diagnostics/Get-ServicesSnapshot.ps1", SERVICES_SNAPSHOT_DIGEST,
        "Get-ServicesSnapshot", validate_services_snapshot,
        "Collects local service names, states and startup modes; stopped does not imply a fault."),
})
