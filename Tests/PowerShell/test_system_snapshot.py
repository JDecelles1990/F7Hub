"""Standalone validation only; F7Hub has no PowerShell execution path."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
SCRIPT_QUOTED = str(SCRIPT).replace("'", "''")
PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell 7 is required for standalone validation")
class SystemSnapshotTests(unittest.TestCase):
    def run_script(self, command: str | None = None):
        with tempfile.TemporaryDirectory() as temporary:
            cwd = Path(temporary)
            before = tuple(cwd.iterdir())
            args = [PWSH, "-NoProfile", "-NonInteractive"]
            args += ["-File", str(SCRIPT)] if command is None else ["-Command", command]
            process = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=70)
            self.assertEqual(tuple(cwd.iterdir()), before, "Diagnostic created a file in its working directory")
        decoder = json.JSONDecoder()
        result, end = decoder.raw_decode(process.stdout.strip())
        self.assertEqual(process.stdout.strip()[end:], "", "Extra stdout after JSON")
        self.assertEqual(process.stderr, "")
        self.assertEqual(result["schemaVersion"], 1)
        self.assertEqual(result["operation"], "Get-SystemSnapshot")
        self.assertIsInstance(result["warnings"], list)
        self.assertIsInstance(result["errors"], list)
        self.assertIsInstance(result["data"], dict)
        return process, result

    def test_parser_has_no_errors(self):
        command = (
            "$tokens=$null; $errors=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{SCRIPT_QUOTED}',"
            "[ref]$tokens,[ref]$errors) > $null; "
            "if ($errors.Count -ne 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        process = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-Command", command],
                                 capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, "")

    def test_success_on_local_windows(self):
        process, result = self.run_script()
        self.assertEqual(process.returncode, 0)
        self.assertTrue(result["success"])
        self.assertIn(result["status"], ("PASS", "WARNING"))
        data = result["data"]
        for key in ("computerName", "windowsCaption", "windowsVersion", "windowsBuild",
                    "osArchitecture", "lastBootUtc", "powerShellVersion"):
            self.assertIsInstance(data[key], str)
        self.assertGreaterEqual(data["uptimeSeconds"], 0)
        self.assertGreaterEqual(data["physicalMemoryBytes"], 0)
        drives = data["fixedDrives"]
        self.assertIsInstance(drives, list)
        self.assertLessEqual(len(drives), 64)
        self.assertEqual([d["device"] for d in drives], sorted(d["device"] for d in drives))
        for drive in drives:
            self.assertIsInstance(drive["device"], str)
            for field in ("capacityBytes", "freeBytes"):
                value = drive[field]
                if value is None:
                    self.assertEqual(result["status"], "WARNING")
                    self.assertTrue(result["warnings"])
                else:
                    self.assertIsInstance(value, int)
                    self.assertGreaterEqual(value, 0)

    def test_required_os_query_failure(self):
        command = (
            "function Get-CimInstance { throw 'synthetic private failure' }; "
            f". '{SCRIPT_QUOTED}'"
        )
        process, result = self.run_script(command)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["data"]["fixedDrives"], [])
        self.assertNotIn("synthetic private failure", str(result))

    def test_required_os_query_returns_no_result(self):
        process, result = self.run_script(
            "function Get-CimInstance { return }; " + f". '{SCRIPT_QUOTED}'"
        )
        self.assertEqual(process.returncode, 1)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(set(result["data"]), {
            "computerName", "windowsCaption", "windowsVersion", "windowsBuild",
            "osArchitecture", "lastBootUtc", "uptimeSeconds", "powerShellVersion",
            "physicalMemoryBytes", "fixedDrives",
        })

    def test_fixed_drive_query_failure(self):
        command = (
            "function Get-CimInstance { param($ClassName) "
            "if ($ClassName -eq 'Win32_LogicalDisk') { throw 'synthetic private drive failure' }; "
            "[pscustomobject]@{CSName='TEST'; Caption='Windows'; Version='1'; BuildNumber='1'; "
            "OSArchitecture='64-bit'; LastBootUpTime=[datetime]::UtcNow.AddHours(-1); "
            "TotalVisibleMemorySize=1024} }; "
            f". '{SCRIPT_QUOTED}'"
        )
        process, result = self.run_script(command)
        self.assertEqual(process.returncode, 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(result["data"]["fixedDrives"], [])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertNotIn("synthetic private drive failure", str(result))

    def test_partial_fixed_drive_measurements_preserve_null_and_zero(self):
        command = (
            "function Get-CimInstance { param($ClassName) "
            "if ($ClassName -eq 'Win32_LogicalDisk') { "
            "[pscustomobject]@{DeviceID='E:'; Size=0; FreeSpace=0}; "
            "[pscustomobject]@{DeviceID='C:'; Size=$null; FreeSpace=$null}; "
            "[pscustomobject]@{DeviceID='D:'; Size=4096; FreeSpace=$null}; return }; "
            "[pscustomobject]@{CSName='TEST'; Caption='Windows'; Version='1'; BuildNumber='1'; "
            "OSArchitecture='64-bit'; LastBootUpTime=[datetime]::UtcNow.AddHours(-1); "
            "TotalVisibleMemorySize=1024} }; "
            f". '{SCRIPT_QUOTED}'"
        )
        process, result = self.run_script(command)
        self.assertEqual(process.returncode, 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(result["warnings"], ["One or more fixed-drive measurements are unavailable."])
        self.assertEqual(result["errors"], [])
        drives = result["data"]["fixedDrives"]
        self.assertEqual([drive["device"] for drive in drives], ["C:", "D:", "E:"])
        self.assertIsNone(drives[0]["capacityBytes"])
        self.assertIsNone(drives[0]["freeBytes"])
        self.assertEqual(drives[1]["capacityBytes"], 4096)
        self.assertIsNone(drives[1]["freeBytes"])
        self.assertIsInstance(drives[2]["capacityBytes"], int)
        self.assertIsInstance(drives[2]["freeBytes"], int)
        self.assertEqual((drives[2]["capacityBytes"], drives[2]["freeBytes"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
