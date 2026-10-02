"""Launch the fixed local AHK v2 guide client without a shell."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


class AltF7HubOpenError(RuntimeError):
    """A safe, actionable guide-open failure for presentation."""


class WindowsAltF7HubGateway:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()

    def show_guide(self) -> str:
        if sys.platform != "win32":
            raise AltF7HubOpenError("AltF7Hub requires Windows and AutoHotkey v2.")
        program_files = os.environ.get("ProgramFiles")
        if not program_files or not Path(program_files).is_absolute():
            raise AltF7HubOpenError("Install AutoHotkey v2 in its standard Program Files location.")
        interpreter = Path(program_files) / "AutoHotkey" / "v2" / "AutoHotkey64.exe"
        guide_root = self.project_root / "AutoHotkey" / "Troubleshooting_Sections"
        client = guide_root / "Troubleshooting_Quick_Guide.ahk"
        if not interpreter.is_file():
            raise AltF7HubOpenError("Install AutoHotkey v2 (64-bit), then retry opening AltF7Hub.")
        required = (client, guide_root / "GuideRequest.ahk", guide_root / "GuideHost.ahk",
                    guide_root / "GuideCore.ahk", self.project_root / "AutoHotkey" / "F7Hub.ahk")
        if not all(path.is_file() for path in required):
            raise AltF7HubOpenError("AltF7Hub files are missing. Restore this checkout's guide files and retry.")
        try:
            result = subprocess.run(
                [str(interpreter), "/ErrorStdOut=UTF-8", str(client), "--show"],
                cwd=str(self.project_root), shell=False, capture_output=True,
                encoding="utf-8-sig", errors="replace", timeout=16,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except subprocess.TimeoutExpired as error:
            raise AltF7HubOpenError(
                "The guide open request was not confirmed. The host may still be running; retry or use Alt+F7."
            ) from error
        except OSError as error:
            raise AltF7HubOpenError("AutoHotkey v2 could not start. Check its installation and retry.") from error
        outcome = result.stdout.strip()
        if result.returncode != 0 or outcome not in {"SHOWN", "FOCUSED_EDITOR"}:
            raise AltF7HubOpenError(
                "The guide open request was not confirmed. Check AutoHotkey v2, then retry or use Alt+F7."
            )
        return outcome
