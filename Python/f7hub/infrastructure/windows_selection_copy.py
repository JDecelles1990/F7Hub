"""One explicit Python-owned selection copy; no monitoring, logging or storage."""

from __future__ import annotations

import ctypes as C
from ctypes import wintypes as W
from dataclasses import dataclass
import os
import time

from f7hub.domain.clipboard import ClipboardSelectionAcquisition, normalize_source_process_basename


class SelectionCopyError(RuntimeError):
    """Fixed content-free failure; optional guard is used only by target diagnosis."""
    def __init__(self, code, *, guard=None):
        super().__init__(code)
        self.guard = guard


@dataclass(frozen=True)
class Target:
    hwnd: int
    pid: int


class KEYBDINPUT(C.Structure):
    _fields_ = [('vk', W.WORD), ('scan', W.WORD), ('flags', W.DWORD),
                ('time', W.DWORD), ('extra', C.c_size_t)]


class MOUSEINPUT(C.Structure):
    _fields_ = [('dx', W.LONG), ('dy', W.LONG), ('data', W.DWORD),
                ('flags', W.DWORD), ('time', W.DWORD), ('extra', C.c_size_t)]


class HARDWAREINPUT(C.Structure):
    _fields_ = [('message', W.DWORD), ('low', W.WORD), ('high', W.WORD)]


class INPUTUNION(C.Union):
    _fields_ = [('keyboard', KEYBDINPUT), ('mouse', MOUSEINPUT), ('hardware', HARDWAREINPUT)]


class INPUT(C.Structure):
    _fields_ = [('kind', W.DWORD), ('value', INPUTUNION)]


class MSG(C.Structure):
    _fields_ = [('hwnd', W.HWND), ('message', W.UINT), ('wParam', W.WPARAM),
                ('lParam', W.LPARAM), ('time', W.DWORD), ('point', W.POINT),
                ('private', W.DWORD)]


RELEASE_KEYS = (0x5B, 0x5C, 0xA4, 0xA5, 0x43, 0xA2, 0xA3, 0xA0, 0xA1)
HOTKEY_ID = 0xF7C
HOTKEY_MODIFIERS = 0x4009  # MOD_NOREPEAT | MOD_WIN | MOD_ALT


def decode_unicode(raw: bytes) -> str:
    if not 2 <= len(raw) <= 131074 or len(raw) % 2:
        raise SelectionCopyError('UNSUPPORTED_TEXT')
    end = next((i for i in range(0, len(raw), 2) if raw[i:i + 2] == b'\0\0'), None)
    if end is None:
        raise SelectionCopyError('UNSUPPORTED_TEXT')
    # A terminator is mandatory; allocation padding after it is not content.
    try:
        text = raw[:end].decode('utf-16-le', errors='strict')
        valid = bool(text.strip()) and len(text.encode('utf-8')) <= 65536
    except UnicodeError:
        valid = False
    if not valid:
        raise SelectionCopyError('UNSUPPORTED_TEXT')
    return text


class WindowsSelectionAPI:
    """ctypes ABI is explicit; each read owns and releases its native handles."""

    def __init__(self):
        if os.name != 'nt':
            raise SelectionCopyError('WINDOWS_REQUIRED')
        self.user = C.WinDLL('user32', use_last_error=True)
        self.kernel = C.WinDLL('kernel32', use_last_error=True)
        self.advapi = C.WinDLL('advapi32', use_last_error=True)
        for lib, name, result, args in (
            (self.user, 'RegisterHotKey', W.BOOL, [W.HWND, C.c_int, W.UINT, W.UINT]),
            (self.user, 'UnregisterHotKey', W.BOOL, [W.HWND, C.c_int]),
            (self.user, 'GetForegroundWindow', W.HWND, []),
            (self.user, 'GetWindowThreadProcessId', W.DWORD, [W.HWND, C.POINTER(W.DWORD)]),
            (self.user, 'GetAsyncKeyState', C.c_short, [C.c_int]),
            (self.user, 'GetClipboardSequenceNumber', W.DWORD, []),
            (self.user, 'GetClipboardOwner', W.HWND, []),
            (self.user, 'SendInput', W.UINT, [W.UINT, C.POINTER(INPUT), C.c_int]),
            (self.user, 'OpenClipboard', W.BOOL, [W.HWND]),
            (self.user, 'CloseClipboard', W.BOOL, []),
            (self.user, 'IsClipboardFormatAvailable', W.BOOL, [W.UINT]),
            (self.user, 'GetClipboardData', W.HANDLE, [W.UINT]),
            (self.user, 'RegisterClipboardFormatW', W.UINT, [W.LPCWSTR]),
            (self.kernel, 'OpenProcess', W.HANDLE, [W.DWORD, W.BOOL, W.DWORD]),
            (self.kernel, 'QueryFullProcessImageNameW', W.BOOL, [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]),
            (self.kernel, 'GetProcessTimes', W.BOOL, [W.HANDLE] + [C.POINTER(W.FILETIME)] * 4),
            (self.kernel, 'WaitForSingleObject', W.DWORD, [W.HANDLE, W.DWORD]),
            (self.kernel, 'CloseHandle', W.BOOL, [W.HANDLE]),
            (self.kernel, 'GlobalSize', C.c_size_t, [W.HANDLE]),
            (self.kernel, 'GlobalLock', C.c_void_p, [W.HANDLE]),
            (self.kernel, 'GlobalUnlock', W.BOOL, [W.HANDLE]),
            (self.advapi, 'OpenProcessToken', W.BOOL, [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]),
            (self.advapi, 'GetTokenInformation', W.BOOL,
             [W.HANDLE, C.c_int, W.LPVOID, W.DWORD, C.POINTER(W.DWORD)]),
        ):
            fn = getattr(lib, name)
            fn.restype, fn.argtypes = result, args
        self.exclusions = tuple(self.user.RegisterClipboardFormatW(name) for name in (
            'ExcludeClipboardContentFromMonitorProcessing', 'Clipboard Viewer Ignore'))
        self.permissions = tuple(self.user.RegisterClipboardFormatW(name) for name in (
            'CanIncludeInClipboardHistory', 'CanUploadToCloudClipboard'))
        if not all(self.exclusions + self.permissions):
            raise SelectionCopyError('NATIVE_UNAVAILABLE')

    def register(self):
        return bool(self.user.RegisterHotKey(None, HOTKEY_ID, HOTKEY_MODIFIERS, 0x43))

    def unregister(self):
        return bool(self.user.UnregisterHotKey(None, HOTKEY_ID))

    def _pid(self, hwnd):
        pid = W.DWORD()
        if not hwnd:
            raise SelectionCopyError('TARGET_UNAVAILABLE', guard='NO_WINDOW')
        if not self.user.GetWindowThreadProcessId(hwnd, C.byref(pid)):
            raise SelectionCopyError('TARGET_UNAVAILABLE', guard='WINDOW_QUERY_FAILED')
        if not pid.value:
            raise SelectionCopyError('TARGET_UNAVAILABLE', guard='WINDOW_PROCESS_MISSING')
        return pid.value

    def foreground(self):
        hwnd = self.user.GetForegroundWindow()
        return Target(int(hwnd or 0), self._pid(hwnd))

    def keys_down(self):
        return any(self.user.GetAsyncKeyState(key) & 0x8000 for key in RELEASE_KEYS)

    def sequence(self):
        return int(self.user.GetClipboardSequenceNumber())

    def owner_pid(self):
        return self._pid(self.user.GetClipboardOwner())

    def pin(self, target, *, on_source_process=None):
        if target.pid == os.getpid():
            raise SelectionCopyError('TARGET_UNAVAILABLE', guard='SELF_TARGET')
        handle = self.kernel.OpenProcess(0x101000, False, target.pid)
        if not handle:
            raise SelectionCopyError('TARGET_UNAVAILABLE', guard='PROCESS_OPEN_FAILED')
        try:
            # Ctrl+C may interrupt commands instead of copying in these hosts.
            image = C.create_unicode_buffer(32768)
            length = W.DWORD(len(image))
            if not self.kernel.QueryFullProcessImageNameW(handle, 0, image, C.byref(length)):
                raise SelectionCopyError('TARGET_UNAVAILABLE', guard='IMAGE_QUERY_FAILED')
            basename = image.value.rsplit('\\', 1)[-1].lower()
            if basename in {'windowsterminal.exe', 'openconsole.exe', 'conhost.exe',
                            'cmd.exe', 'powershell.exe', 'pwsh.exe'}:
                raise SelectionCopyError('UNSUPPORTED_TARGET', guard='TERMINAL_POLICY')
            times = [W.FILETIME() for _ in range(4)]
            if not self.kernel.GetProcessTimes(handle, *(C.byref(t) for t in times)):
                raise SelectionCopyError('TARGET_UNAVAILABLE', guard='PROCESS_TIMES_FAILED')
            token = W.HANDLE()
            if not self.advapi.OpenProcessToken(handle, 8, C.byref(token)):
                raise SelectionCopyError('TARGET_UNAVAILABLE', guard='TOKEN_OPEN_FAILED')
            try:
                elevated, used = W.DWORD(), W.DWORD()
                if not self.advapi.GetTokenInformation(token, 20, C.byref(elevated), 4, C.byref(used)):
                    raise SelectionCopyError('TARGET_UNAVAILABLE', guard='TOKEN_QUERY_FAILED')
                if used.value != 4:
                    raise SelectionCopyError('TARGET_UNAVAILABLE', guard='TOKEN_SIZE_INVALID')
                if elevated.value:
                    raise SelectionCopyError('TARGET_UNAVAILABLE', guard='ELEVATED_POLICY')
            finally:
                if not self.kernel.CloseHandle(token):
                    raise SelectionCopyError('CLEANUP_FAILED', guard='TOKEN_CLOSE_FAILED')
            if on_source_process is not None:
                on_source_process(normalize_source_process_basename(basename))
            return handle
        except BaseException:
            if not self.kernel.CloseHandle(handle):
                raise SelectionCopyError('CLEANUP_FAILED', guard='REJECTED_HANDLE_CLOSE_FAILED') from None
            raise

    def live(self, handle):
        return self.kernel.WaitForSingleObject(handle, 0) == 258

    def unpin(self, handle):
        if not self.kernel.CloseHandle(handle):
            raise SelectionCopyError('CLEANUP_FAILED', guard='HANDLE_CLOSE_FAILED')

    @staticmethod
    def _key(vk, up=False):
        item = INPUT()
        item.kind = 1
        item.value.keyboard = KEYBDINPUT(vk, 0, 2 if up else 0, 0, 0)
        return item

    def send_copy(self):
        events = (INPUT * 4)(self._key(0x11), self._key(0x43), self._key(0x43, True), self._key(0x11, True))
        if self.user.SendInput(4, events, C.sizeof(INPUT)) != 4:
            releases = (INPUT * 2)(self._key(0x43, True), self._key(0x11, True))
            if self.user.SendInput(2, releases, C.sizeof(INPUT)) != 2:
                raise SelectionCopyError('CLEANUP_FAILED')
            raise SelectionCopyError('INPUT_DENIED')

    def _bytes(self, fmt, maximum):
        handle = self.user.GetClipboardData(fmt)  # May block for delayed rendering.
        if not handle:
            raise SelectionCopyError('UNSUPPORTED_TEXT')
        size = self.kernel.GlobalSize(handle)
        if not 1 <= size <= maximum:
            raise SelectionCopyError('UNSUPPORTED_TEXT')
        ptr = self.kernel.GlobalLock(handle)
        if not ptr:
            raise SelectionCopyError('UNSUPPORTED_TEXT')
        try:
            return C.string_at(ptr, size)
        finally:
            C.set_last_error(0)
            if not self.kernel.GlobalUnlock(handle) and C.get_last_error():
                raise SelectionCopyError('CLEANUP_FAILED')

    def read_text(self, target, expected_sequence):
        if not self.user.OpenClipboard(None):
            raise SelectionCopyError('CLIPBOARD_LOCKED')
        try:
            if self.sequence() != expected_sequence or self.owner_pid() != target.pid:
                raise SelectionCopyError('AMBIGUOUS_UPDATE')
            if any(self.user.IsClipboardFormatAvailable(fmt) for fmt in self.exclusions):
                raise SelectionCopyError('PRIVACY_DENIED')
            for fmt in self.permissions:
                if self.user.IsClipboardFormatAvailable(fmt):
                    marker = self._bytes(fmt, 4)
                    if len(marker) != 4 or int.from_bytes(marker, 'little') != 1:
                        raise SelectionCopyError('PRIVACY_DENIED')
            if not self.user.IsClipboardFormatAvailable(13):
                raise SelectionCopyError('UNSUPPORTED_TEXT')
            text = decode_unicode(self._bytes(13, 131074))
            if self.sequence() != expected_sequence or self.owner_pid() != target.pid:
                raise SelectionCopyError('AMBIGUOUS_UPDATE')
            return text
        finally:
            if not self.user.CloseClipboard():
                raise SelectionCopyError('CLEANUP_FAILED')


def copy_selection(api, target, cancelled, *, clock=time.monotonic, sleep=time.sleep, on_release=None, on_release_wait=None, with_metadata=False):
    """One copy only; sequence change plus target/owner checks, never old text."""
    source_process = []
    handle = (api.pin(target, on_source_process=source_process.append) if with_metadata else api.pin(target))
    try:
        def check():
            if cancelled.is_set():
                raise SelectionCopyError('CANCELLED')
            if not api.live(handle) or api.foreground() != target:
                raise SelectionCopyError('TARGET_CHANGED')
        release_deadline = clock() + 1.5
        if on_release_wait is not None:
            on_release_wait()  # Diagnostic observation only; no admission decision.
        while api.keys_down():
            check()
            if clock() >= release_deadline:
                raise SelectionCopyError('RELEASE_TIMEOUT')
            sleep(.015)
        if on_release is not None:
            on_release()  # Preserve this press's observed release for the coordinator.
        check()
        before = api.sequence()
        if not before:
            raise SelectionCopyError('SEQUENCE_UNAVAILABLE')
        api.send_copy()
        deadline = clock() + 1.5
        while clock() < deadline:
            check()
            after = api.sequence()
            if after and after != before:
                if api.owner_pid() != target.pid:
                    raise SelectionCopyError('AMBIGUOUS_UPDATE')
                text = api.read_text(target, after)
                check()
                if clock() >= deadline or api.sequence() != after:
                    raise SelectionCopyError('LATE_OR_UNSTABLE')
                return (ClipboardSelectionAcquisition(text, source_process[0] if source_process else None)
                        if with_metadata else text)
            sleep(.02)
        raise SelectionCopyError('NO_FRESH_COPY')
    finally:
        api.unpin(handle)
