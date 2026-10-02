from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from f7hub.infrastructure.altf7hub_gateway import AltF7HubOpenError, WindowsAltF7HubGateway
from f7hub.services.altf7hub_service import AltF7HubService


class AltF7HubLaunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="F7Hub guide launch ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.program_files = self.root / "Program Files"
        self.exe = self.program_files / "AutoHotkey/v2/AutoHotkey64.exe"
        self.guide = self.root / "AutoHotkey/Troubleshooting_Sections"
        for path in (self.exe, self.root / "AutoHotkey/F7Hub.ahk", *(self.guide / name for name in
                     ("GuideCore.ahk", "GuideHost.ahk", "GuideRequest.ahk", "Troubleshooting_Quick_Guide.ahk"))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        self.env = patch.dict(os.environ, {"ProgramFiles": str(self.program_files)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.platform = patch("f7hub.infrastructure.altf7hub_gateway.sys.platform", "win32")
        self.platform.start()
        self.addCleanup(self.platform.stop)
        self.gateway = WindowsAltF7HubGateway(self.root)
        self.service = AltF7HubService(self.gateway)

    def test_fixed_argument_array_handles_spaces_without_shell(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run",
                   return_value=SimpleNamespace(returncode=0, stdout="SHOWN\n")) as run:
            self.assertEqual(self.service.show_guide(), "SHOWN")
        args, values = run.call_args
        self.assertEqual(args[0], [str(self.exe), "/ErrorStdOut=UTF-8",
                                 str(self.guide / "Troubleshooting_Quick_Guide.ahk"), "--show"])
        self.assertFalse(values["shell"])
        self.assertEqual(values["timeout"], 16)
        self.assertEqual(values["cwd"], str(self.root))

    def test_existing_editor_result_is_preserved(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run",
                   return_value=SimpleNamespace(returncode=0, stdout="FOCUSED_EDITOR\n")):
            self.assertEqual(self.service.show_guide(), "FOCUSED_EDITOR")

    def test_missing_files_and_interpreter_reject_before_launch(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run") as run:
            self.exe.unlink()
            with self.assertRaisesRegex(AltF7HubOpenError, "Install AutoHotkey v2"):
                self.service.show_guide()
            self.exe.touch()
            (self.guide / "GuideHost.ahk").unlink()
            with self.assertRaisesRegex(AltF7HubOpenError, "files are missing"):
                self.service.show_guide()
            run.assert_not_called()

    def test_unconfirmed_outputs_and_errors_do_not_leak_diagnostics(self):
        for code, output in ((0, "STARTED"), (0, ""), (1, "SHOWN"), (1, "private diagnostics")):
            with self.subTest(code=code, output=output), patch(
                "f7hub.infrastructure.altf7hub_gateway.subprocess.run",
                return_value=SimpleNamespace(returncode=code, stdout=output),
            ), self.assertRaises(AltF7HubOpenError) as caught:
                self.service.show_guide()
            self.assertNotIn("private", str(caught.exception))

    def test_timeout_is_uncertain_and_does_not_retry(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("client", 16)) as run:
            with self.assertRaisesRegex(AltF7HubOpenError, "host may still be running"):
                self.service.show_guide()
            self.assertEqual(run.call_count, 1)

    def test_os_failure_is_actionable(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run", side_effect=OSError("private")):
            with self.assertRaisesRegex(AltF7HubOpenError, "Check its installation") as caught:
                self.service.show_guide()
            self.assertNotIn("private", str(caught.exception))

    def test_non_windows_and_invalid_program_files_reject_before_launch(self):
        with patch("f7hub.infrastructure.altf7hub_gateway.subprocess.run") as run:
            with patch("f7hub.infrastructure.altf7hub_gateway.sys.platform", "linux"):
                with self.assertRaisesRegex(AltF7HubOpenError, "requires Windows"):
                    self.service.show_guide()
            with patch.dict(os.environ, {"ProgramFiles": "relative"}):
                with self.assertRaisesRegex(AltF7HubOpenError, "Program Files"):
                    self.service.show_guide()
            run.assert_not_called()
