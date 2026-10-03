"""Manage script metadata and read eligible, verified PowerShell source."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import sqlite3
import stat

from f7hub.repositories.script_repository import (
    ScriptRecord, ScriptRepository, ScriptRegistrationConflictError, ScriptStateConflictError,
)


AVAILABLE = "AVAILABLE"
MISSING = "MISSING"
INACCESSIBLE = "INACCESSIBLE"
INVALID_REFERENCE = "INVALID_REFERENCE"
_APPROVED_FOLDERS = {"diagnostics", "reports", "modules"}
_WINDOWS_INVALID = set('<>:"|?*')
_WINDOWS_DEVICES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
SCRIPT_TYPES = ("DIAGNOSTIC", "REMEDIATION", "ADMINISTRATIVE", "REPORT", "UTILITY", "INTEGRATION")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
PRIVILEGE_LEVELS = (
    "STANDARD_USER", "LOCAL_ADMIN", "M365_AUTHENTICATED", "M365_PRIVILEGED", "SPECIAL_ROLE",
)


class ScriptValidationError(ValueError):
    """Invalid script input; safe to display."""


class ScriptWriteError(RuntimeError):
    """Safe metadata write failure."""


class ScriptConflictError(ScriptWriteError):
    """Reload the registration before retrying a visibility change."""


class ScriptReadError(RuntimeError):
    """Registry metadata could not be loaded; safe to show to a user."""


class ScriptCopyError(RuntimeError):
    """Safe copy failure with a stable code for GUI feedback."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class ScriptCatalogEntry:
    metadata: ScriptRecord
    file_status: str


@dataclass(frozen=True)
class VerifiedScriptCandidate:
    metadata: ScriptRecord
    content: bytes
    source_path: Path


class ScriptService:
    def __init__(self, repository: ScriptRepository, project_root: str | Path) -> None:
        self._repository = repository
        self._project_root = Path(project_root)

    def list_scripts(self, *, text_query: str | None = None) -> tuple[ScriptCatalogEntry, ...]:
        if text_query is not None and (
                not isinstance(text_query, str) or "\x00" in text_query):
            raise ScriptValidationError("Search text must be text without NUL characters.")
        query = _optional_text(text_query, "Search text")
        try:
            records = self._repository.list_scripts(text_query=query)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptReadError("Could not load the script catalog.") from error
        return tuple(self._entry(record) for record in records)

    def get_script(self, script_code: str) -> ScriptCatalogEntry | None:
        try:
            record = self._repository.get_script(script_code)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptReadError("Could not load the script metadata.") from error
        return None if record is None else self._entry(record)

    def list_registered_scripts(self) -> tuple[ScriptCatalogEntry, ...]:
        """Include disabled rows while retaining the repository's category scope."""
        try:
            records = self._repository.list_scripts(include_disabled=True)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptReadError("Could not load script registrations.") from error
        return tuple(self._entry(record) for record in records)

    def register_script(
        self, *, script_code: str, name: str, relative_path: str,
        script_type: str, risk_level: str, privilege_level: str,
        description: str | None = None, version: str | None = None,
    ) -> ScriptRecord:
        values = {
            "script_code": _required_text(script_code, "Script code"),
            "name": _required_text(name, "Name"),
            "relative_path": _required_text(relative_path, "Relative path").replace("\\", "/"),
            "script_type": _choice(script_type, SCRIPT_TYPES, "Type"),
            "risk_level": _choice(risk_level, RISK_LEVELS, "Risk"),
            "privilege_level": _choice(privilege_level, PRIVILEGE_LEVELS, "Privilege"),
            "description": _optional_text(description, "Description"),
            "version": _optional_text(version, "Version"),
        }
        _require_readable_script(self._project_root, values["relative_path"])
        try:
            return self._repository.register_script(**values, timestamp=_timestamp())
        except ScriptRegistrationConflictError as error:
            raise ScriptWriteError("That script code or file path is already registered.") from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptWriteError("Could not register the script. Your entered information is preserved.") from error

    def set_script_enabled(
        self, script_id: int, *, enabled: bool, expected_updated_at: str,
    ) -> ScriptRecord:
        if isinstance(script_id, bool) or not isinstance(script_id, int) or not 0 < script_id < 2**63:
            raise ScriptValidationError("Select a valid script registration.")
        if not isinstance(enabled, bool):
            raise ScriptValidationError("Enabled state must be a boolean.")
        token = _required_text(expected_updated_at, "Update token")
        try:
            current = next((row for row in self._repository.list_scripts(include_disabled=True)
                            if row.script_id == script_id), None)
            if current is None or current.updated_at != token:
                raise ScriptConflictError("Registration changed. Refresh before trying again.")
            if enabled:
                _require_readable_script(self._project_root, current.relative_path)
            return self._repository.set_script_enabled(
                script_id, enabled=enabled, expected_updated_at=token,
                expected_relative_path=current.relative_path, updated_at=_next_timestamp(token),
            )
        except ScriptStateConflictError as error:
            raise ScriptConflictError("Registration changed. Refresh before trying again.") from error
        except ScriptWriteError:
            raise
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptWriteError("Could not change script visibility. Refresh and try again.") from error

    def read_verified_script(self, script_code: str) -> str:
        """Return source decoded from the same bytes whose approved hash matched."""
        return self.prepare_verified_script(script_code).content.decode("utf-8", errors="strict")

    def prepare_verified_script(self, script_code: str, *, for_execution: bool = False) -> VerifiedScriptCandidate:
        """Share approved-byte verification with copying and controlled execution."""
        try:
            record = self._repository.get_script(script_code)
        except (sqlite3.Error, OSError, RuntimeError, ValueError) as error:
            raise ScriptCopyError("SCRIPT_NOT_ELIGIBLE") from error
        if record is None:
            raise ScriptCopyError("SCRIPT_NOT_ELIGIBLE")

        status, target = _resolve_script_reference(self._project_root, record.relative_path)
        if status == INVALID_REFERENCE:
            raise ScriptCopyError("INVALID_REFERENCE")
        if status != AVAILABLE or target is None:
            raise ScriptCopyError("FILE_UNAVAILABLE")

        try:
            if for_execution:
                # Open and inspect the actual object, retaining protected ancestry
                # until the bounded buffer has been read. Copy semantics stay unchanged.
                from f7hub.infrastructure.windows_execution import protected_read
                content = protected_read(self._project_root / record.relative_path, 1024 * 1024)
            else:
                with target.open("rb") as source:
                    content = source.read()
        except (OSError, ValueError) as error:
            raise ScriptCopyError("READ_FAILED") from error

        approved = record.checksum_sha256
        if not isinstance(approved, str) or _SHA256.fullmatch(approved) is None:
            raise ScriptCopyError("INTEGRITY_NOT_APPROVED")
        if hashlib.sha256(content).hexdigest() != approved.lower():
            raise ScriptCopyError("INTEGRITY_MISMATCH")
        try:
            content.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise ScriptCopyError("READ_FAILED") from error
        return VerifiedScriptCandidate(record, content, target)

    def _entry(self, record: ScriptRecord) -> ScriptCatalogEntry:
        return ScriptCatalogEntry(record, inspect_script_reference(self._project_root, record.relative_path))


def inspect_script_reference(project_root: str | Path, relative_path: str) -> str:
    """Inspect a .ps1 path at this instant without opening or executing it."""
    return _resolve_script_reference(project_root, relative_path)[0]


def _required_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScriptValidationError(f"{label} is required and must be text.")
    return value.strip()


def _optional_text(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ScriptValidationError(f"{label} must be text.")
    return value.strip() or None


def _choice(value: str, choices: tuple[str, ...], label: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ScriptValidationError(f"Select a valid {label.lower()}.")
    return value


def _require_readable_script(root: Path, relative_path: str) -> None:
    """Prove current read access before a metadata write; retain no source."""
    message = "Use an existing readable .ps1 under PowerShell/Diagnostics, Reports or Modules."
    status, target = _resolve_script_reference(root, relative_path)
    if status != AVAILABLE or target is None:
        raise ScriptValidationError(message)
    try:
        with target.open("rb") as source:
            source.read(1)
    except (OSError, ValueError) as error:
        raise ScriptValidationError(message) from error


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _next_timestamp(previous: str) -> str:
    try:
        prior = datetime.fromisoformat(previous.replace("Z", "+00:00"))
        if prior.tzinfo is None or prior.utcoffset() is None:
            raise ValueError("No timezone")
        minimum = (prior.astimezone(timezone.utc) + timedelta(milliseconds=1)).isoformat(
            timespec="milliseconds",
        ).replace("+00:00", "Z")
    except (ValueError, OverflowError) as error:
        raise ScriptWriteError("Could not read the registration update time. Refresh and try again.") from error
    return max(_timestamp(), minimum)


def _resolve_script_reference(project_root: str | Path, relative_path: str) -> tuple[str, Path | None]:
    if not isinstance(relative_path, str) or not relative_path:
        return INVALID_REFERENCE, None
    windows_path = PureWindowsPath(relative_path)
    if windows_path.drive or windows_path.root or windows_path.is_absolute():
        return INVALID_REFERENCE, None
    raw_parts = relative_path.replace("/", "\\").split("\\")
    if len(raw_parts) < 3 or raw_parts[0].casefold() != "powershell":
        return INVALID_REFERENCE, None
    if raw_parts[1].casefold() not in _APPROVED_FOLDERS:
        return INVALID_REFERENCE, None
    if any(
        not part or part in (".", "..") or part.endswith((" ", "."))
        or any(character in _WINDOWS_INVALID or ord(character) < 32 for character in part)
        or part.split(".", 1)[0].upper() in _WINDOWS_DEVICES
        for part in raw_parts
    ):
        return INVALID_REFERENCE, None
    if not raw_parts[-1].casefold().endswith(".ps1"):
        return INVALID_REFERENCE, None

    try:
        root = Path(project_root).resolve(strict=False)
        approved = root / "PowerShell" / raw_parts[1]
        approved_resolved = approved.resolve(strict=False)
        target = (root.joinpath(*raw_parts)).resolve(strict=False)
        if approved_resolved != approved or not target.is_relative_to(approved_resolved):
            return INVALID_REFERENCE, None
        details = target.stat()
        if not stat.S_ISREG(details.st_mode):
            return INVALID_REFERENCE, None
        if not os.access(target, os.R_OK):
            return INACCESSIBLE, None
        return AVAILABLE, target
    except (FileNotFoundError, NotADirectoryError):
        return MISSING, None
    except PermissionError:
        return INACCESSIBLE, None
    except (OSError, RuntimeError, ValueError):
        return INVALID_REFERENCE, None
