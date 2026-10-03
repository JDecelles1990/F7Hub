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


@dataclass(frozen=True)
class DiagnosticPackDefinition:
    code: str
    name: str
    description: str
    diagnostic_codes: tuple[str, ...]


LOCAL_BASELINE_PACK = DiagnosticPackDefinition(
    "diagnostic.pack.local_baseline", "Local Baseline Diagnostics",
    "System → Network configuration → Services. Local, read only, Standard User.",
    ("diagnostic.windows.system_snapshot", "diagnostic.windows.network_snapshot",
     "diagnostic.windows.services_snapshot"),
)


@dataclass(frozen=True)
class DiagnosticPackResult:
    pack_code: str
    classification: str
    collection_status: str | None
    message: str
    diagnostics: tuple[ScriptDiagnosticRunResult, ...] = ()
    duration_seconds: float = 0.0
    aborted_at: str | None = None
    failure_classification: str | None = None
    skipped_codes: tuple[str, ...] = ()
    cleanup_verified: bool = True
