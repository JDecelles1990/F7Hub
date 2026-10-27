"""Dormant H01-C retained-process context observation, without enrollment.

The future trusted enrollment owner lends ORIGINAL real process handles and
their launch/inherited-parent PID/creation pins, serializes use, retains them,
and prevents concurrent closure. No OpenProcess-by-PID discovery occurs here.
This observation is neither executable/script provenance, pipe-peer checking,
trusted launch, authentication nor permission to construct an active session.
Revalidate at the required native use boundary; liveness is only a snapshot.
Only temporary TOKEN_QUERY handles opened here are closed here, once.
No application wiring, keys, IPC, Clipboard, logs or persistence.
"""

import ctypes as C
from ctypes import wintypes as W
import hashlib
import os
import struct


class NativeContextError(ValueError):
    """Content-free rejection; never include native identity or API diagnostics."""


def _deny():
    raise NativeContextError('NATIVE_CONTEXT_REJECTED')


class _SidAttributes(C.Structure):
    _fields_ = [('sid', C.c_void_p), ('attributes', W.DWORD)]


class _Groups(C.Structure):
    _fields_ = [('count', W.DWORD), ('groups', _SidAttributes * 1)]


def _sid(buffer, length, pointer, minimum):
    """Copy only an entire SID inside the returned token buffer, after headers."""
    offset = (pointer or 0) - C.addressof(buffer)
    if offset < minimum or offset + 8 > length:
        _deny()
    header = bytes(buffer)[offset:offset + 8]
    size = 8 + 4 * header[1]
    if header[0] != 1 or not 1 <= header[1] <= 15 or offset + size > length:
        _deny()
    return bytes(buffer)[offset:offset + size]


class _WindowsAPI:
    def __init__(self):
        if os.name != 'nt' or C.sizeof(C.c_void_p) != 8:
            _deny()
        self.kernel = C.WinDLL('kernel32', use_last_error=True)
        self.advapi = C.WinDLL('advapi32', use_last_error=True)
        for lib, name, result, args in (
            (self.kernel, 'GetProcessId', W.DWORD, [W.HANDLE]),
            (self.kernel, 'GetProcessTimes', W.BOOL,
             [W.HANDLE] + [C.POINTER(W.FILETIME)] * 4),
            (self.kernel, 'WaitForSingleObject', W.DWORD, [W.HANDLE, W.DWORD]),
            (self.kernel, 'CloseHandle', W.BOOL, [W.HANDLE]),
            (self.advapi, 'OpenProcessToken', W.BOOL,
             [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]),
            (self.advapi, 'GetTokenInformation', W.BOOL,
             [W.HANDLE, C.c_int, W.LPVOID, W.DWORD, C.POINTER(W.DWORD)]),
        ):
            fn = getattr(lib, name)
            fn.restype, fn.argtypes = result, args

    def live(self, handle):
        # Exact WAIT_TIMEOUT is the only positive evidence of a live process.
        if self.kernel.WaitForSingleObject(handle, 0) != 258:
            _deny()

    def pin(self, handle):
        pid = self.kernel.GetProcessId(handle)
        times = [W.FILETIME() for _ in range(4)]
        if not pid or not self.kernel.GetProcessTimes(
                handle, *(C.byref(t) for t in times)):
            _deny()
        creation = times[0].dwLowDateTime | (times[0].dwHighDateTime << 32)
        if not creation:
            _deny()
        return pid, creation

    def _token_buffer(self, token, kind):
        size = W.DWORD()
        if self.advapi.GetTokenInformation(token, kind, None, 0, C.byref(size)) \
                or C.get_last_error() != 122 or not 1 <= size.value <= 65_536:
            _deny()
        buffer = C.create_string_buffer(size.value)
        used = W.DWORD()
        if not self.advapi.GetTokenInformation(
                token, kind, buffer, size.value, C.byref(used)) \
                or not 1 <= used.value <= size.value:
            _deny()  # Changing/oversized results get no allocation retry.
        return buffer, used.value

    def _single_sid(self, token, kind):
        buffer, length = self._token_buffer(token, kind)
        if length < C.sizeof(_SidAttributes):
            _deny()
        entry = _SidAttributes.from_buffer(buffer)
        return _sid(buffer, length, entry.sid, C.sizeof(_SidAttributes))

    def _logon_sid(self, token):
        # TokenLogonSid returns TOKEN_GROUPS. Require one unambiguous logon SID.
        buffer, length = self._token_buffer(token, 28)
        minimum = _Groups.groups.offset + C.sizeof(_SidAttributes)
        if length < minimum or W.DWORD.from_buffer(buffer).value != 1:
            _deny()
        entry = _SidAttributes.from_buffer(buffer, _Groups.groups.offset)
        if entry.attributes & 0xC0000000 != 0xC0000000:
            _deny()
        sid = _sid(buffer, length, entry.sid, minimum)
        # SECURITY_NT_AUTHORITY, SECURITY_LOGON_IDS_RID: S-1-5-5-X-Y.
        if len(sid) != 20 or sid[:8] != b'\x01\x03\x00\x00\x00\x00\x00\x05' \
                or struct.unpack_from('<I', sid, 8)[0] != 5:
            _deny()
        return sid

    def security(self, handle):
        token = W.HANDLE()
        if not self.advapi.OpenProcessToken(handle, 0x0008, C.byref(token)):
            _deny()
        try:
            user = self._single_sid(token, 1)
            logon = self._logon_sid(token)
            buffer, length = self._token_buffer(token, 12)
            if length != 4:
                _deny()
            session = struct.unpack('<I', bytes(buffer)[:4])[0]
            integrity = self._single_sid(token, 25)
            # Exact medium mandatory label S-1-16-8192, not medium-plus/high.
            if integrity != b'\x01\x01\x00\x00\x00\x00\x00\x10\x00\x20\x00\x00':
                _deny()
            return session, user, logon
        finally:
            # Own only this temporary handle. Unknown close is a denial, no retry.
            if not self.kernel.CloseHandle(token):
                _deny()


def read_pinned_context(generation, *, server_handle, child_handle,
                        server_pin, child_pin):
    """Observe H01-C's exact 112 bytes; caller still owns all enrollment gates.

    Handles are borrowed positive native integers. Pins are exact (PID, creation
    FILETIME) tuples from the original retained launch/parent identity, never a
    substitute for trusted launch or the separate pipe self-client PID gate.
    Same-user/session is necessary but cannot establish peer authentication.
    The 64-bit Windows adapter deliberately fails closed on other platforms.
    """
    if type(generation) is not bytes or len(generation) != 16 or not any(generation):
        _deny()
    for handle in (server_handle, child_handle):
        # Reject pseudo handles (-1 through -6), including unsigned encodings.
        if type(handle) is not int or not 0 < handle < 2**64 - 6:
            _deny()
    for pin in (server_pin, child_pin):
        if type(pin) is not tuple or len(pin) != 2 \
                or type(pin[0]) is not int or not 0 < pin[0] < 2**32 \
                or type(pin[1]) is not int or not 0 < pin[1] < 2**64:
            _deny()
    if server_handle == child_handle or server_pin[0] == child_pin[0]:
        _deny()
    try:
        api = _WindowsAPI()
        for handle, pin in ((server_handle, server_pin), (child_handle, child_pin)):
            api.live(handle)
            if api.pin(handle) != pin:
                _deny()
        server = api.security(server_handle)
        child = api.security(child_handle)
        if server != child:
            _deny()
        # No context is published if either process exits during observation.
        api.live(server_handle)
        api.live(child_handle)
        session, user, logon = server
        return generation + struct.pack('<IQIQI', *server_pin, *child_pin, session) \
            + hashlib.sha256(user).digest() + hashlib.sha256(logon).digest() \
            + struct.pack('<I', 0x2000)
    except (OSError, ValueError, OverflowError, C.ArgumentError):
        raise NativeContextError('NATIVE_CONTEXT_REJECTED') from None
