"""Individual diagnostic outcomes; execution and collected severity are separate."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PowerShellProcessResult:
    classification: str
    stdout: bytes = b""
    stderr: bytes = b""
    exit_code: int | None = None
    duration_seconds: float = 0.0
    cleanup_verified: bool = True
    process_id: int | None = None


@dataclass(frozen=True)
class DiagnosticResult:
    operation: str
    status: str
    message: str
    data: dict[str, Any]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ScriptDiagnosticRunResult:
    script_code: str
    digest: str | None
    classification: str
    message: str
    diagnostic: DiagnosticResult | None = None
    duration_seconds: float = 0.0
    exit_code: int | None = None
    cleanup_verified: bool = True
