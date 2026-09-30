"""Read eligible script metadata and inspect script file references only."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PureWindowsPath
import sqlite3
import stat

from f7hub.repositories.script_repository import ScriptRecord, ScriptRepository


AVAILABLE = "AVAILABLE"
MISSING = "MISSING"
INACCESSIBLE = "INACCESSIBLE"
INVALID_REFERENCE = "INVALID_REFERENCE"
_APPROVED_FOLDERS = {"diagnostics", "reports", "modules"}
_WINDOWS_INVALID = set('<>:"|?*')
_WINDOWS_DEVICES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}


class ScriptReadError(RuntimeError):
    """Registry metadata could not be loaded; safe to show to a user."""


@dataclass(frozen=True)
class ScriptCatalogEntry:
    metadata: ScriptRecord
    file_status: str


class ScriptService:
    def __init__(self, repository: ScriptRepository, project_root: str | Path) -> None:
        self._repository = repository
        self._project_root = Path(project_root)

    def list_scripts(self) -> tuple[ScriptCatalogEntry, ...]:
        try:
            records = self._repository.list_scripts()
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptReadError("Could not load the script catalog.") from error
        return tuple(self._entry(record) for record in records)

    def get_script(self, script_code: str) -> ScriptCatalogEntry | None:
        try:
            record = self._repository.get_script(script_code)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ScriptReadError("Could not load the script metadata.") from error
        return None if record is None else self._entry(record)

    def _entry(self, record: ScriptRecord) -> ScriptCatalogEntry:
        return ScriptCatalogEntry(record, inspect_script_reference(self._project_root, record.relative_path))


def inspect_script_reference(project_root: str | Path, relative_path: str) -> str:
    """Inspect a .ps1 path at this instant without opening or executing it."""
    if not isinstance(relative_path, str) or not relative_path:
        return INVALID_REFERENCE
    windows_path = PureWindowsPath(relative_path)
    if windows_path.drive or windows_path.root or windows_path.is_absolute():
        return INVALID_REFERENCE
    raw_parts = relative_path.replace("/", "\\").split("\\")
    if len(raw_parts) < 3 or raw_parts[0].casefold() != "powershell":
        return INVALID_REFERENCE
    if raw_parts[1].casefold() not in _APPROVED_FOLDERS:
        return INVALID_REFERENCE
    if any(
        not part or part in (".", "..") or part.endswith((" ", "."))
        or any(character in _WINDOWS_INVALID or ord(character) < 32 for character in part)
        or part.split(".", 1)[0].upper() in _WINDOWS_DEVICES
        for part in raw_parts
    ):
        return INVALID_REFERENCE
    if not raw_parts[-1].casefold().endswith(".ps1"):
        return INVALID_REFERENCE

    try:
        root = Path(project_root).resolve(strict=False)
        approved = root / "PowerShell" / raw_parts[1]
        approved_resolved = approved.resolve(strict=False)
        target = (root.joinpath(*raw_parts)).resolve(strict=False)
        if approved_resolved != approved or not target.is_relative_to(approved_resolved):
            return INVALID_REFERENCE
        details = target.stat()
        if not stat.S_ISREG(details.st_mode):
            return INVALID_REFERENCE
        if not os.access(target, os.R_OK):
            return INACCESSIBLE
        return AVAILABLE
    except (FileNotFoundError, NotADirectoryError):
        return MISSING
    except PermissionError:
        return INACCESSIBLE
    except (OSError, RuntimeError, ValueError):
        return INVALID_REFERENCE
