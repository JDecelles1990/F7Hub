"""Bounded Windows mechanics with synthetic scripts, separate from real diagnostics."""

import base64
from contextlib import ExitStack
import ctypes as C
from ctypes import wintypes as W
import hashlib
import os
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from f7hub.infrastructure.windows_execution import WindowsExecution, SealedScript, protected_read, HANDLE
from f7hub.infrastructure.powershell_gateway import PowerShellGateway, STDOUT_LIMIT, STDERR_LIMIT


@unittest.skipUnless(os.name == "nt", "Native Windows APIs required")
class WindowsExecutionTests(unittest.TestCase):
    def setUp(self):
        self.api = WindowsExecution()
        self.api.require_standard_user(self.api.kernel.GetCurrentProcess())
        self.gateway = PowerShellGateway()

    def candidate(self, content=b"# synthetic test fixture\r\n"):
        return SimpleNamespace(content=content, metadata=SimpleNamespace(checksum_sha256=hashlib.sha256(content).hexdigest()))

    def run_fixture(self, command, *, timeout=5):
        launcher = base64.b64encode(command.encode("utf-16-le")).decode("ascii")
        with patch("f7hub.infrastructure.powershell_gateway.ENCODED_LAUNCHER", launcher):
            return self.gateway.execute(self.candidate(), timeout, lambda: True)

    def test_exact_crlf_sealed_and_write_delete_rename_denied(self):
        content = b"# exact\r\n# preserved\r\n"
        sealed = SealedScript(self.api, content, hashlib.sha256(content).hexdigest())
        with sealed:
            self.assertEqual(sealed.path.read_bytes(), content)
            for action in (lambda: sealed.path.write_bytes(b"tampered"), sealed.path.unlink,
                           lambda: sealed.path.rename(sealed.path.with_name("replacement.ps1")),
                           lambda: sealed.path.parent.rename(sealed.path.parent.with_name("replacement"))):
                with self.assertRaises(OSError):
                    action()
            path = sealed.path
        self.assertTrue(sealed.cleanup_verified)
        self.assertFalse(path.exists())
        self.assertFalse(path.parent.exists())

    def test_sealed_digest_mismatch_cleans_owned_artifacts(self):
        sealed = SealedScript(self.api, b"x", "0" * 64)
        with self.assertRaises(OSError):
            with sealed:
                self.fail("Must not prepare mismatched bytes")
        self.assertTrue(sealed.cleanup_verified)
        self.assertFalse(sealed.path.parent.exists())

    def test_source_opened_handle_bound_and_size_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.ps1"
            source.write_bytes(b"abc\r\n")
            self.assertEqual(protected_read(source, 20), b"abc\r\n")
            with self.assertRaises(OSError):
                protected_read(source, 2)
            with ExitStack() as stack:
                self.api.protect_ancestry(stack, source)
                stack.enter_context(self.api.handle(self.api.open_protected(source)))
                with self.assertRaises(OSError):
                    source.write_bytes(b"changed")

    def test_private_acl_and_runtime_trust(self):
        sealed = SealedScript(self.api, b"x", hashlib.sha256(b"x").hexdigest())
        with sealed:
            with self.api.handle(self.api.open_protected(sealed.path)) as handle:
                with self.assertRaises(OSError):
                    self.api.trusted_acl(handle)
        with ExitStack() as stack:
            self.assertEqual(self.gateway._runtime(self.api, stack).name, "pwsh.exe")

    def test_fixed_launcher_stdout_stderr_and_exit(self):
        result = self.run_fixture("[Console]::Out.Write('out'); [Console]::Error.Write('err'); exit 1")
        self.assertEqual((result.classification, result.stdout, result.stderr, result.exit_code),
                         ("COMPLETED", b"out", b"err", 1))
        self.assertTrue(result.cleanup_verified)

    def test_timeout_and_next_run_after_cleanup(self):
        result = self.run_fixture("[Threading.Thread]::Sleep(60000)", timeout=0.4)
        self.assertEqual(result.classification, "TIMEOUT")
        self.assertTrue(result.cleanup_verified)
        self.assertLess(result.duration_seconds, 6)
        self.assertEqual(self.run_fixture("exit 0").classification, "COMPLETED")

    def test_concurrent_stream_limits(self):
        result = self.run_fixture("[Console]::Out.Write('x' * 1200000); [Console]::Error.Write('y' * 100000)")
        self.assertEqual(result.classification, "OUTPUT_LIMIT_EXCEEDED")
        self.assertLessEqual(len(result.stdout), STDOUT_LIMIT)
        self.assertLessEqual(len(result.stderr), STDERR_LIMIT)
        self.assertTrue(result.cleanup_verified)

    def test_stderr_limit(self):
        result = self.run_fixture("[Console]::Error.Write('y' * 100000)")
        self.assertEqual(result.classification, "OUTPUT_LIMIT_EXCEEDED")
        self.assertEqual(len(result.stderr), STDERR_LIMIT)
        self.assertTrue(result.cleanup_verified)

    def test_assignment_failure_never_resumes_suspended_child(self):
        with patch("f7hub.infrastructure.powershell_gateway.WindowsExecution", return_value=self.api), \
             patch.object(self.api.kernel, "AssignProcessToJobObject", return_value=0):
            result = self.gateway.execute(self.candidate(), 5, lambda: True)
        self.assertEqual(result.classification, "LAUNCH_FAILED")
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.cleanup_verified)

    def test_registration_recheck_blocks_process_creation(self):
        with patch.object(self.gateway, "_create_process") as create:
            result = self.gateway.execute(self.candidate(), 5, lambda: False)
        self.assertEqual(result.classification, "REGISTRATION_CHANGED")
        create.assert_not_called()

    def test_original_source_edit_cannot_change_prepared_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory)/"original.ps1"
            content = b"[Console]::Out.Write('original'); exit 0\r\n"
            original.write_bytes(content)
            candidate = self.candidate(protected_read(original, 1024))
            def revalidate():
                original.write_bytes(b"[Console]::Out.Write('tampered'); exit 0")
                return True
            result = self.gateway.execute(candidate, 5, revalidate)
            self.assertEqual(result.classification, "COMPLETED")
            self.assertEqual(result.stdout, b"original")
            self.assertTrue(result.cleanup_verified)

    def test_tampering_before_seal_and_lock_failure_fail_closed(self):
        original_open = self.api.open_protected
        def tampered(path, **kwargs):
            if Path(path).name == "diagnostic.ps1":
                Path(path).write_bytes(b"tampered")
            return original_open(path, **kwargs)
        with patch("f7hub.infrastructure.powershell_gateway.WindowsExecution", return_value=self.api), \
             patch.object(self.api, "open_protected", side_effect=tampered):
            result = self.gateway.execute(self.candidate(), 5, lambda: True)
        self.assertEqual(result.classification, "PREPARATION_FAILED")
        self.assertTrue(result.cleanup_verified)
        with patch.object(WindowsExecution, "private_directory", side_effect=OSError("denied")):
            result = self.gateway.execute(self.candidate(), 5, lambda: True)
        self.assertEqual(result.classification, "PREPARATION_FAILED")
        self.assertTrue(result.cleanup_verified)

    def test_source_junction_path_is_rejected(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/"target"
            target.mkdir()
            (target/"source.ps1").write_bytes(b"reviewed")
            alias = root/"alias"
            result = subprocess.run([str(Path(os.environ['SystemRoot'])/'System32/cmd.exe'),
                '/c','mklink','/J',str(alias),str(target)], capture_output=True,timeout=5)
            self.assertEqual(result.returncode, 0)
            try:
                with self.assertRaises(OSError):
                    protected_read(alias/"source.ps1", 1024)
            finally:
                alias.rmdir()

    def test_elevated_or_unknown_token_and_missing_runtime_block(self):
        with patch.object(WindowsExecution, "require_standard_user", side_effect=OSError("unknown")):
            self.assertEqual(self.gateway.execute(self.candidate(), 5, lambda: True).classification, "PRIVILEGE_BLOCKED")
        with patch.object(self.gateway, "_runtime", side_effect=OSError("missing")):
            self.assertEqual(self.gateway.execute(self.candidate(), 5, lambda: True).classification, "RUNTIME_UNAVAILABLE")

    def test_cleanup_failure_blocks_later_runs(self):
        # Synthetic cleanup failure; no surviving real process is created here.
        with patch.object(self.gateway, "_run", return_value=SimpleNamespace(cleanup_verified=False)):
            result = self.gateway.execute(self.candidate(), 5, lambda: True)
        self.assertFalse(result.cleanup_verified)
        self.assertEqual(self.gateway.execute(self.candidate(), 5, lambda: True).classification, "CLEANUP_FAILED")
        resources, sealed = self.gateway._quarantine
        resources.close()
        sealed.__exit__(None, None, None)
        self.gateway._quarantine = None

    def test_no_inherited_application_secret(self):
        with patch.dict(os.environ, {"F7HUB_SYNTHETIC_SECRET": "must-not-be-inherited"}):
            result = self.run_fixture("if ($env:F7HUB_SYNTHETIC_SECRET) { exit 1 }; exit 0")
        self.assertEqual(result.exit_code, 0)

    def test_owned_child_killed_and_unrelated_process_preserved(self):
        import subprocess
        import sys
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"], creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            result = self.run_fixture("$p=[Diagnostics.ProcessStartInfo]::new(); $p.FileName=$PSHOME+'\\pwsh.exe'; $p.Arguments='-NoProfile -NonInteractive -Command [Threading.Thread]::Sleep(60000)'; $p.UseShellExecute=$false; $child=[Diagnostics.Process]::Start($p); [Console]::Out.Write($child.Id); exit 0")
            self.assertEqual(result.classification, "COMPLETED")
            self.assertTrue(result.cleanup_verified)
            child_pid = int(result.stdout)
            self.api.kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
            self.api.kernel.OpenProcess.restype = HANDLE
            handle = self.api.kernel.OpenProcess(0x100000 | 0x1000, False, child_pid)
            if handle:
                with self.api.handle(handle):
                    self.assertEqual(self.api.kernel.WaitForSingleObject(handle, 0), 0)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)
