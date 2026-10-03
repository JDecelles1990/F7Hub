"""Small Windows API boundary for sealed files and owned diagnostic processes.

Handles are non-inheritable except the explicitly listed child standard streams.
No process-name lookup, shell, elevation, or recursive deletion is used.
"""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ctypes as C
from ctypes import wintypes as W
import hashlib
import os
from pathlib import Path
import uuid


HANDLE = W.HANDLE
SIZE = C.c_size_t
INVALID = C.c_void_p(-1).value


class SecurityAttributes(C.Structure):
    _fields_ = [("length", W.DWORD), ("descriptor", W.LPVOID), ("inherit", W.BOOL)]


class StartupInfo(C.Structure):
    _fields_ = [("cb", W.DWORD), ("reserved", W.LPWSTR), ("desktop", W.LPWSTR),
               ("title", W.LPWSTR), ("x", W.DWORD), ("y", W.DWORD),
               ("xsize", W.DWORD), ("ysize", W.DWORD), ("xchars", W.DWORD),
               ("ychars", W.DWORD), ("fill", W.DWORD), ("flags", W.DWORD),
               ("show", W.WORD), ("reserved2size", W.WORD), ("reserved2", W.LPVOID),
               ("stdin", HANDLE), ("stdout", HANDLE), ("stderr", HANDLE)]


class StartupInfoEx(C.Structure):
    _fields_ = [("startup", StartupInfo), ("attributes", W.LPVOID)]


class ProcessInfo(C.Structure):
    _fields_ = [("process", HANDLE), ("thread", HANDLE), ("pid", W.DWORD), ("tid", W.DWORD)]


class JobLimits(C.Structure):
    _fields_ = [("process_time", C.c_int64), ("job_time", C.c_int64), ("flags", W.DWORD),
               ("min_ws", SIZE), ("max_ws", SIZE), ("active_limit", W.DWORD),
               ("affinity", SIZE), ("priority", W.DWORD), ("scheduling", W.DWORD)]


class JobExtendedLimits(C.Structure):
    _fields_ = [("basic", JobLimits), ("io", C.c_uint64 * 6),
               ("process_memory", SIZE), ("job_memory", SIZE),
               ("peak_process_memory", SIZE), ("peak_job_memory", SIZE)]


class JobAccounting(C.Structure):
    _fields_ = [("times", C.c_int64 * 4), ("page_faults", W.DWORD),
               ("total", W.DWORD), ("active", W.DWORD), ("terminated", W.DWORD)]


class FileTag(C.Structure):
    _fields_ = [("attributes", W.DWORD), ("tag", W.DWORD)]


class WindowsExecution:
    def __init__(self):
        if os.name != "nt" or C.sizeof(W.LPVOID) != 8:
            raise OSError("64-bit Windows is required")
        self.kernel = C.WinDLL("kernel32", use_last_error=True)
        self.advapi = C.WinDLL("advapi32", use_last_error=True)
        self.shell = C.WinDLL("shell32", use_last_error=True)
        self.ole = C.WinDLL("ole32", use_last_error=True)
        definitions = [
            (self.kernel, "CloseHandle", W.BOOL, [HANDLE]),
            (self.kernel, "CreateFileW", HANDLE, [W.LPCWSTR, W.DWORD, W.DWORD, W.LPVOID, W.DWORD, W.DWORD, HANDLE]),
            (self.kernel, "GetFinalPathNameByHandleW", W.DWORD, [HANDLE, W.LPWSTR, W.DWORD, W.DWORD]),
            (self.kernel, "GetFileInformationByHandleEx", W.BOOL, [HANDLE, C.c_int, W.LPVOID, W.DWORD]),
            (self.kernel, "ReadFile", W.BOOL, [HANDLE, W.LPVOID, W.DWORD, C.POINTER(W.DWORD), W.LPVOID]),
            (self.kernel, "CreateDirectoryW", W.BOOL, [W.LPCWSTR, C.POINTER(SecurityAttributes)]),
            (self.kernel, "GetDriveTypeW", W.UINT, [W.LPCWSTR]),
            (self.kernel, "GetWindowsDirectoryW", W.UINT, [W.LPWSTR, W.UINT]),
            (self.kernel, "LocalFree", W.LPVOID, [W.LPVOID]),
            (self.kernel, "GetCurrentProcess", HANDLE, []),
            (self.kernel, "CreateJobObjectW", HANDLE, [W.LPVOID, W.LPCWSTR]),
            (self.kernel, "SetInformationJobObject", W.BOOL, [HANDLE, C.c_int, W.LPVOID, W.DWORD]),
            (self.kernel, "QueryInformationJobObject", W.BOOL, [HANDLE, C.c_int, W.LPVOID, W.DWORD, W.LPVOID]),
            (self.kernel, "AssignProcessToJobObject", W.BOOL, [HANDLE, HANDLE]),
            (self.kernel, "TerminateJobObject", W.BOOL, [HANDLE, W.UINT]),
            (self.kernel, "TerminateProcess", W.BOOL, [HANDLE, W.UINT]),
            (self.kernel, "WaitForSingleObject", W.DWORD, [HANDLE, W.DWORD]),
            (self.kernel, "ResumeThread", W.DWORD, [HANDLE]),
            (self.kernel, "GetExitCodeProcess", W.BOOL, [HANDLE, C.POINTER(W.DWORD)]),
            (self.kernel, "InitializeProcThreadAttributeList", W.BOOL, [W.LPVOID, W.DWORD, W.DWORD, C.POINTER(SIZE)]),
            (self.kernel, "UpdateProcThreadAttribute", W.BOOL, [W.LPVOID, W.DWORD, SIZE, W.LPVOID, SIZE, W.LPVOID, W.LPVOID]),
            (self.kernel, "DeleteProcThreadAttributeList", None, [W.LPVOID]),
            (self.kernel, "CreateProcessW", W.BOOL, [W.LPCWSTR, W.LPWSTR, W.LPVOID, W.LPVOID, W.BOOL, W.DWORD, W.LPVOID, W.LPCWSTR, C.POINTER(StartupInfoEx), C.POINTER(ProcessInfo)]),
            (self.advapi, "OpenProcessToken", W.BOOL, [HANDLE, W.DWORD, C.POINTER(HANDLE)]),
            (self.advapi, "GetTokenInformation", W.BOOL, [HANDLE, C.c_int, W.LPVOID, W.DWORD, C.POINTER(W.DWORD)]),
            (self.advapi, "ConvertSidToStringSidW", W.BOOL, [W.LPVOID, C.POINTER(W.LPWSTR)]),
            (self.advapi, "ConvertStringSecurityDescriptorToSecurityDescriptorW", W.BOOL, [W.LPCWSTR, W.DWORD, C.POINTER(W.LPVOID), W.LPVOID]),
            (self.advapi, "GetSecurityInfo", W.DWORD, [HANDLE, C.c_int, W.DWORD, W.LPVOID, W.LPVOID, C.POINTER(W.LPVOID), W.LPVOID, C.POINTER(W.LPVOID)]),
            (self.advapi, "GetAce", W.BOOL, [W.LPVOID, W.DWORD, C.POINTER(W.LPVOID)]),
            (self.shell, "SHGetKnownFolderPath", C.c_long, [W.LPVOID, W.DWORD, HANDLE, C.POINTER(W.LPWSTR)]),
            (self.ole, "CoTaskMemFree", None, [W.LPVOID]),
        ]
        for library, name, result, args in definitions:
            fn = getattr(library, name)
            fn.restype, fn.argtypes = result, args

    @staticmethod
    def check(value):
        if not value:
            raise C.WinError(C.get_last_error())
        return value

    def close(self, handle):
        self.check(self.kernel.CloseHandle(handle))

    @contextmanager
    def handle(self, value):
        if value in (None, INVALID):
            raise C.WinError(C.get_last_error())
        try:
            yield value
        finally:
            self.close(value)

    def known_folder(self, identifier):
        guid = (C.c_byte * 16).from_buffer_copy(uuid.UUID(identifier).bytes_le)
        result = W.LPWSTR()
        if self.shell.SHGetKnownFolderPath(guid, 0, None, C.byref(result)) != 0:
            raise OSError("Known folder unavailable")
        try:
            return Path(result.value)
        finally:
            self.ole.CoTaskMemFree(result)

    def token(self, process):
        token = HANDLE()
        self.check(self.advapi.OpenProcessToken(process, 8, C.byref(token)))
        return self.handle(token.value)

    def require_standard_user(self, process):
        with self.token(process) as token:
            elevated, size = W.DWORD(), W.DWORD()
            self.check(self.advapi.GetTokenInformation(token, 20, C.byref(elevated), 4, C.byref(size)))
            if elevated.value != 0:
                raise OSError("Elevated execution refused")

    def sid_text(self, sid):
        text = W.LPWSTR()
        self.check(self.advapi.ConvertSidToStringSidW(sid, C.byref(text)))
        try:
            return text.value
        finally:
            self.kernel.LocalFree(text)

    def current_sid(self):
        with self.token(self.kernel.GetCurrentProcess()) as token:
            size = W.DWORD()
            self.advapi.GetTokenInformation(token, 1, None, 0, C.byref(size))
            buffer = C.create_string_buffer(size.value)
            self.check(self.advapi.GetTokenInformation(token, 1, buffer, size.value, C.byref(size)))
            return self.sid_text(C.cast(buffer, C.POINTER(W.LPVOID))[0])

    def trusted_acl(self, handle, *, volume_root=False):
        """Refuse installation objects granting mutation to non-administrator SIDs."""
        acl, descriptor = W.LPVOID(), W.LPVOID()
        if self.advapi.GetSecurityInfo(handle, 1, 4, None, None, C.byref(acl), None, C.byref(descriptor)) != 0:
            raise OSError("Installation ACL unavailable")
        try:
            if not acl.value:
                raise OSError("Unrestricted installation ACL")
            count = C.c_ushort.from_address(acl.value + 4).value
            trusted = {"S-1-5-18", "S-1-5-32-544",
                       "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"}
            for index in range(count):
                ace = W.LPVOID()
                self.check(self.advapi.GetAce(acl, index, C.byref(ace)))
                kind = C.c_ubyte.from_address(ace.value).value
                flags = C.c_ubyte.from_address(ace.value + 1).value
                if flags & 8 or kind == 1:  # inherit-only and denied grants
                    continue
                if kind != 0:
                    raise OSError("Unsupported installation ACL")
                mask = W.DWORD.from_address(ace.value + 4).value
                # Creating a sibling at the volume root cannot replace an already
                # protected Program Files path. Delete-child and ACL mutation can.
                mutation_mask = 0x500D0150 if volume_root else 0x500D0156
                if mask & mutation_mask and self.sid_text(ace.value + 8) not in trusted:
                    raise OSError("Writable installation")
        finally:
            self.kernel.LocalFree(descriptor)

    def open_protected(self, path, *, directory=False, trusted=False):
        path = Path(path).absolute()
        if not path.drive or path.drive.startswith("\\\\") or self.kernel.GetDriveTypeW(path.anchor) != 3:
            raise OSError("A local fixed drive is required")
        access = 0x20080 if directory else 0x80000000
        handle = self.kernel.CreateFileW(str(path), access, 1, None, 3, 0x02200000, None)
        if handle in (None, INVALID):
            raise C.WinError(C.get_last_error())
        try:
            tag = FileTag()
            self.check(self.kernel.GetFileInformationByHandleEx(handle, 9, C.byref(tag), C.sizeof(tag)))
            if tag.attributes & 0x400 or bool(tag.attributes & 0x10) != directory:
                raise OSError("Reparse or unexpected file type")
            final = C.create_unicode_buffer(32768)
            count = self.kernel.GetFinalPathNameByHandleW(handle, final, len(final), 0)
            if count == 0 or count >= len(final) or os.path.normcase(final.value.removeprefix("\\\\?\\")) != os.path.normcase(str(path)):
                raise OSError("Opened path changed")
            if trusted:
                self.trusted_acl(handle, volume_root=directory and path == Path(path.anchor))
            return handle
        except BaseException:
            self.close(handle)
            raise

    def protect_ancestry(self, stack, path, *, trusted=False):
        for directory in reversed(Path(path).absolute().parents):
            stack.enter_context(self.handle(self.open_protected(directory, directory=True, trusted=trusted)))

    def read(self, handle, limit):
        content = bytearray()
        while len(content) <= limit:
            buffer, read = C.create_string_buffer(65536), W.DWORD()
            self.check(self.kernel.ReadFile(handle, buffer, len(buffer), C.byref(read), None))
            if read.value == 0:
                return bytes(content)
            content.extend(buffer.raw[:read.value])
        raise OSError("Script exceeds execution size limit")

    def private_directory(self, parent):
        path = parent / ("F7Hub-run-" + uuid.uuid4().hex)
        descriptor = W.LPVOID()
        self.check(self.advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            f"D:P(A;;FA;;;SY)(A;;FA;;;{self.current_sid()})", 1, C.byref(descriptor), None))
        try:
            attributes = SecurityAttributes(C.sizeof(SecurityAttributes), descriptor, False)
            self.check(self.kernel.CreateDirectoryW(str(path), C.byref(attributes)))
            return path
        finally:
            self.kernel.LocalFree(descriptor)


def protected_read(path, limit):
    api = WindowsExecution()
    with ExitStack() as stack:
        api.protect_ancestry(stack, path)
        handle = stack.enter_context(api.handle(api.open_protected(path)))
        return api.read(handle, limit)


class SealedScript:
    """Exact verified bytes with file and directory guards held through cleanup."""

    def __init__(self, api, content, digest):
        self.api, self.content, self.digest = api, content, digest
        self.path = None
        self.parent_guards = ExitStack()
        self.guards = ExitStack()
        self.cleanup_verified = False

    def __enter__(self):
        try:
            parent = self.api.known_folder("f1b32785-6fba-4fcf-9d55-7b8e7f157091")
            self.api.protect_ancestry(self.parent_guards, parent / "placeholder")
            directory = self.api.private_directory(parent)
            self.path = directory / "diagnostic.ps1"
            self.guards.enter_context(self.api.handle(self.api.open_protected(directory, directory=True)))
            with self.path.open("xb") as file:
                file.write(self.content)
                file.flush()
                os.fsync(file.fileno())
            handle = self.guards.enter_context(self.api.handle(self.api.open_protected(self.path)))
            if hashlib.sha256(self.api.read(handle, 1024 * 1024)).hexdigest() != self.digest:
                raise OSError("Sealed bytes changed")
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_args):
        if self.cleanup_verified:
            return
        try:
            self.guards.close()
            if self.path is not None:
                self.path.unlink(missing_ok=True)
                self.path.parent.rmdir()
            self.cleanup_verified = True
        finally:
            self.parent_guards.close()
