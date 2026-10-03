"""Controlled, finite PowerShell 7 execution for service-prepared diagnostics."""

from __future__ import annotations

import base64
from contextlib import ExitStack
import ctypes as C
from ctypes import wintypes as W
from dataclasses import replace
import os
from pathlib import Path
import subprocess
import threading
import time

from f7hub.domain.diagnostic_results import PowerShellProcessResult
from f7hub.infrastructure.windows_execution import (
    WindowsExecution, SealedScript, JobExtendedLimits, JobAccounting,
    StartupInfoEx, ProcessInfo, SIZE, HANDLE,
)


LAUNCHER = """$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$PSModuleAutoLoadingPreference = 'None'
try {
    if ($PSVersionTable.PSVersion.Major -ne 7 -or [IntPtr]::Size -ne 8) { throw 'Runtime' }
    Import-Module -Name ([IO.Path]::Combine($env:F7HUB_MODULE_ROOT, 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
    Import-Module -Name ([IO.Path]::Combine($env:F7HUB_MODULE_ROOT, 'CimCmdlets', 'CimCmdlets.psd1')) -ErrorAction Stop
    $global:LASTEXITCODE = 0
    & $env:F7HUB_DIAGNOSTIC_PATH
    exit $LASTEXITCODE
} catch {
    [Console]::Error.WriteLine('F7HUB_LAUNCHER_ERROR')
    exit 125
}
"""
ENCODED_LAUNCHER = base64.b64encode(LAUNCHER.encode("utf-16-le")).decode("ascii")
STDOUT_LIMIT = 1024 * 1024
STDERR_LIMIT = 64 * 1024


class _PreparationBlocked(Exception):
    def __init__(self, classification):
        self.classification = classification


class PowerShellGateway:
    def __init__(self):
        self._lock = threading.Lock()
        self._quarantine = None

    def execute(self, candidate, timeout_seconds, revalidate):
        """No caller-provided commands, runtime location, flags or environment."""
        if not self._lock.acquire(blocking=False):
            return PowerShellProcessResult("EXECUTION_BUSY")
        started = time.monotonic()
        resources = ExitStack()
        sealed = None
        outcome = PowerShellProcessResult("PREPARATION_FAILED")
        try:
            if self._quarantine is not None:
                return PowerShellProcessResult("CLEANUP_FAILED", cleanup_verified=False)
            api = WindowsExecution()
            try:
                api.require_standard_user(api.kernel.GetCurrentProcess())
            except OSError:
                raise _PreparationBlocked("PRIVILEGE_BLOCKED") from None
            try:
                executable = self._runtime(api, resources)
            except OSError:
                raise _PreparationBlocked("RUNTIME_UNAVAILABLE") from None
            sealed = SealedScript(api, candidate.content, candidate.metadata.checksum_sha256.lower())
            sealed.__enter__()
            # Held sealed-file and ancestry handles close the interpreter-open race.
            if not revalidate():
                outcome = PowerShellProcessResult("REGISTRATION_CHANGED")
            else:
                outcome = self._run(api, resources, executable, sealed.path, timeout_seconds)
            if not outcome.cleanup_verified:
                # Preserve protections and kill-on-close job ownership; never free
                # an execution file still potentially in use. Further runs fail closed.
                self._quarantine = (resources, sealed)
                return outcome
        except _PreparationBlocked as error:
            outcome = PowerShellProcessResult(error.classification)
        except (OSError, ValueError):
            outcome = PowerShellProcessResult("PREPARATION_FAILED")
        finally:
            if self._quarantine is None:
                try:
                    resources.close()
                    if sealed is not None:
                        sealed.__exit__(None, None, None)
                except OSError:
                    outcome = replace(outcome, classification="CLEANUP_FAILED", cleanup_verified=False)
                    self._quarantine = (resources, sealed)
            self._lock.release()
        return replace(outcome, duration_seconds=time.monotonic() - started)

    def _runtime(self, api, resources):
        program_files = api.known_folder("905e63b6-c1bf-494e-b29c-65b732d3d21a")
        executable = program_files / "PowerShell" / "7" / "pwsh.exe"
        api.protect_ancestry(resources, executable, trusted=True)
        resources.enter_context(api.handle(api.open_protected(executable, trusted=True)))
        # Root ACLs prevent additions; check and hold existing runtime dependencies
        # too, since a child can have a non-inherited permissive ACL.
        for path in executable.parent.rglob("*"):
            resources.enter_context(api.handle(api.open_protected(path, directory=path.is_dir(), trusted=True)))
        for name in ("Microsoft.PowerShell.Utility", "CimCmdlets"):
            if not (executable.parent / "Modules" / name / f"{name}.psd1").is_file():
                raise OSError("Required module unavailable")
        return executable

    @staticmethod
    def _environment(api, executable, script):
        windows = C.create_unicode_buffer(32768)
        count = api.kernel.GetWindowsDirectoryW(windows, len(windows))
        if not count or count >= len(windows):
            raise OSError("Windows directory unavailable")
        return {
            "SystemRoot": windows.value, "WINDIR": windows.value,
            "SystemDrive": Path(windows.value).drive,
            "TEMP": str(script.parent), "TMP": str(script.parent),
            "PSModulePath": "", "POWERSHELL_TELEMETRY_OPTOUT": "1",
            "POWERSHELL_UPDATECHECK": "Off",
            "F7HUB_MODULE_ROOT": str(executable.parent / "Modules"),
            "F7HUB_DIAGNOSTIC_PATH": str(script),
        }

    def _create_process(self, api, executable, script, handles):
        startup = StartupInfoEx()
        startup.startup.cb = C.sizeof(startup)
        startup.startup.flags = 0x100  # STARTF_USESTDHANDLES
        startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = handles
        size = SIZE()
        api.kernel.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
        buffer = C.create_string_buffer(size.value)
        startup.attributes = C.cast(buffer, W.LPVOID)
        api.check(api.kernel.InitializeProcThreadAttributeList(startup.attributes, 1, 0, C.byref(size)))
        try:
            allowed = (HANDLE * 3)(*handles)
            api.check(api.kernel.UpdateProcThreadAttribute(startup.attributes, 0, 0x20002,
                      allowed, C.sizeof(allowed), None, None))
            args = [str(executable), "-NoLogo", "-NoProfile", "-NonInteractive",
                    "-OutputFormat", "Text", "-EncodedCommand", ENCODED_LAUNCHER]
            command = C.create_unicode_buffer(subprocess.list2cmdline(args))
            environment = self._environment(api, executable, script)
            block = C.create_unicode_buffer("\0".join(f"{key}={environment[key]}" for key in sorted(environment)) + "\0\0")
            info = ProcessInfo()
            api.check(api.kernel.CreateProcessW(str(executable), command, None, None, True,
                      0x08080404, block, str(script.parent), C.byref(startup), C.byref(info)))
            return info
        finally:
            api.kernel.DeleteProcThreadAttributeList(startup.attributes)

    def _run(self, api, resources, executable, script, timeout):
        import msvcrt

        job = resources.enter_context(api.handle(api.kernel.CreateJobObjectW(None, None)))
        limits = JobExtendedLimits()
        limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE; no breakaway permission
        api.check(api.kernel.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)))
        reads, writes = [], []
        threads, buffers = [], [bytearray(), bytearray()]
        failure = threading.Event()
        io_error = threading.Event()
        info = None
        assigned = False
        classification = "LAUNCH_FAILED"
        exit_code = None
        cleanup_verified = True
        try:
            for _ in range(2):
                read, write = os.pipe()
                reads.append(read)
                writes.append(write)
                os.set_inheritable(write, True)
            stdin = os.open(os.devnull, os.O_RDONLY)
            writes.append(stdin)
            os.set_inheritable(stdin, True)
            info = self._create_process(api, executable, script,
                     [msvcrt.get_osfhandle(fd) for fd in (stdin, writes[0], writes[1])])
            resources.callback(api.close, info.process)
            resources.callback(api.close, info.thread)
            for fd in writes:
                os.close(fd)
            writes.clear()
            # An assignment failure leaves a suspended process: it must never run.
            api.check(api.kernel.AssignProcessToJobObject(job, info.process))
            assigned = True
            api.require_standard_user(info.process)

            def drain(index, fd, cap):
                try:
                    while True:
                        chunk = os.read(fd, 16384)
                        if not chunk:
                            break
                        remaining = cap - len(buffers[index])
                        buffers[index].extend(chunk[:max(0, remaining)])
                        if len(chunk) > remaining:
                            failure.set()
                            break
                except OSError:
                    io_error.set()
                    failure.set()

            for index, (fd, cap) in enumerate(zip(reads, (STDOUT_LIMIT, STDERR_LIMIT))):
                thread = threading.Thread(target=drain, args=(index, fd, cap), daemon=True)
                thread.start()
                threads.append(thread)
            deadline = time.monotonic() + timeout
            if api.kernel.ResumeThread(info.thread) == 0xFFFFFFFF:
                raise OSError("Could not resume diagnostic")
            while True:
                if failure.is_set():
                    classification = "OUTPUT_CAPTURE_FAILED" if io_error.is_set() else "OUTPUT_LIMIT_EXCEEDED"
                    break
                if time.monotonic() >= deadline:
                    classification = "TIMEOUT"
                    break
                wait = api.kernel.WaitForSingleObject(info.process, 20)
                if wait == 0:
                    code = W.DWORD()
                    api.check(api.kernel.GetExitCodeProcess(info.process, C.byref(code)))
                    exit_code = code.value
                    classification = "COMPLETED"
                    break
                if wait != 258:
                    raise OSError("Process wait failed")
        except OSError:
            classification = "LAUNCH_FAILED"
        finally:
            cleanup_deadline = time.monotonic() + 5
            if info is not None:
                try:
                    if assigned:
                        api.check(api.kernel.TerminateJobObject(job, 124))
                        while True:
                            accounting = JobAccounting()
                            api.check(api.kernel.QueryInformationJobObject(job, 1, C.byref(accounting), C.sizeof(accounting), None))
                            if accounting.active == 0:
                                break
                            if time.monotonic() >= cleanup_deadline:
                                raise OSError("Job cleanup incomplete")
                            time.sleep(0.01)
                    else:
                        api.check(api.kernel.TerminateProcess(info.process, 124))
                    if api.kernel.WaitForSingleObject(info.process, max(0, int((cleanup_deadline - time.monotonic()) * 1000))) != 0:
                        raise OSError("Process cleanup incomplete")
                except OSError:
                    cleanup_verified = False
            for fd in writes:
                os.close(fd)
            for thread in threads:
                thread.join(max(0, cleanup_deadline - time.monotonic()))
            if any(thread.is_alive() for thread in threads):
                cleanup_verified = False
            if cleanup_verified:
                for fd in reads:
                    os.close(fd)
            else:
                # Retained resource stack owns these descriptors until reconciliation.
                for fd in reads:
                    resources.callback(os.close, fd)
        if failure.is_set() and classification == "COMPLETED":
            classification = "OUTPUT_CAPTURE_FAILED" if io_error.is_set() else "OUTPUT_LIMIT_EXCEEDED"
        if not cleanup_verified:
            classification = "CLEANUP_FAILED"
        return PowerShellProcessResult(classification, bytes(buffers[0]), bytes(buffers[1]),
                                       exit_code, cleanup_verified=cleanup_verified,
                                       process_id=None if info is None else info.pid)
