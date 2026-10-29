"""One explicit Python paste effect; reuse the selection adapter's target policy."""

import ctypes as C
from ctypes import wintypes as W
from datetime import datetime, timezone
import os
import time
from uuid import uuid4

from f7hub.domain.clipboard import ClipboardPasteError, ClipboardPasteCode
from f7hub.infrastructure.windows_selection_copy import (
    WindowsSelectionAPI, SelectionCopyError, INPUT, RELEASE_KEYS, HOTKEY_MODIFIERS, decode_unicode,
)

PASTE_HOTKEY_ID = 0xF7D
PASTE_EXCLUSIONS = frozenset({'winword.exe', 'excel.exe', 'outlook.exe', 'olk.exe', 'powerpnt.exe'})


class PasteEffectError(RuntimeError):
    """Fixed code and separate effect outcomes; never retains source text."""
    def __init__(self, code, clipboard='UNCHANGED', dispatch='NOT_SENT', *, guard=None):
        super().__init__(code)
        self.clipboard, self.dispatch = clipboard, dispatch
        self.guard = guard


_SEQUENCE_CODES = frozenset({
    'GUARDS_PASSED_NO_DISPATCH', 'INITIAL_BINDING_FAILED', 'INITIAL_OWNER_FAILED',
    'WORKER_START_FAILED', 'AUTHORIZATION_OR_SERVICE_UNAVAILABLE', 'UNCLASSIFIED',
    'CLIPBOARD_CHANGED', 'SEQUENCE_UNAVAILABLE', 'CLIPBOARD_WRITE_FAILED',
    'CLIPBOARD_LOCKED', 'ALLOCATION_FAILED', 'CLEANUP_FAILED', 'CANCELLED',
    'CLIPBOARD_VERIFY_LOCKED', 'CLIPBOARD_VERIFY_FAILED', 'CLIPBOARD_CONTENT_MISMATCH',
    'TARGET_CHANGED', 'TARGET_UNAVAILABLE', 'UNSUPPORTED_TARGET', 'RELEASE_TIMEOUT',
    'EXPIRED', 'MODIFIERS_CHANGED', 'AUTHORIZATION_MISMATCH',
    'AUTHORIZATION_OR_NATIVE_UNAVAILABLE',
}) | frozenset(code.value for code in ClipboardPasteCode)


class PasteSequenceDiagnostic:
    """Three bounded RAM samples; only comparisons and fixed codes leave this object."""
    def __init__(self):
        self.samples = {}
        self.close = 'NA'
        self.predicate = 'NONE'

    def observe(self, point, api, owner_hwnd, *, value=None, failed=False):
        # Additional observations never turn an original refusal into permission.
        sequence_ok = not failed
        if value is None and not failed:
            try:
                value = api.sequence()
            except Exception:
                sequence_ok = False
        sequence_ok = sequence_ok and type(value) is int and 0 <= value <= 0xFFFFFFFF
        owner_ok, owner_match = True, None
        try:
            hwnd = api.user.GetClipboardOwner()
            owner_match = bool(hwnd == owner_hwnd and api._pid(hwnd) == os.getpid())
        except Exception:
            owner_ok = False
        self.samples[point] = (value if sequence_ok else None, sequence_ok, owner_match, owner_ok)

    def guard(self, api, expected, owner_hwnd):
        # Same original operands/short-circuit decision, with S3 using the actual
        # sequence operand. Extra owner observations are explicitly separate samples.
        try:
            actual = api.sequence()
        except Exception:
            self.observe(3, api, owner_hwnd, failed=True)
            self.predicate = 'SEQUENCE_API_FAILED'
            raise
        self.observe(3, api, owner_hwnd, value=actual)
        if not expected:
            self.predicate = 'EXPECTED_ZERO'
            return False
        if actual != expected:
            self.predicate = 'ACTUAL_ZERO' if not actual else 'SEQUENCE_MISMATCH'
            return False
        try:
            owner = api.owner_pid()
        except Exception:
            self.predicate = 'OWNER_API_FAILED'
            raise
        if owner != os.getpid():
            self.predicate = 'OWNER_MISMATCH'
            return False
        self.predicate = 'PASS'
        return True

    def comparison(self, first, second):
        a, b = self.samples.get(first), self.samples.get(second)
        if a is None or b is None or not (a[1] and b[1]):
            return 'UNKNOWN'
        return 'SAME' if a[0] == b[0] else 'CHANGED'

    def summary(self, code, clipboard='UNCHANGED'):
        code = code if code in _SEQUENCE_CODES else 'UNCLASSIFIED'
        clipboard = clipboard if clipboard in ('UNCHANGED', 'MAY_HAVE_CHANGED', 'WRITTEN') else 'UNKNOWN'
        comparisons = [self.comparison(a, b) for a, b in ((1, 2), (2, 3), (1, 3))]
        owner_changed = any(sample[3] and sample[2] is False for sample in self.samples.values())
        changed = 'CHANGED' in comparisons
        complete = len(self.samples) == 3 and all(q and a and value for value, q, _, a in self.samples.values())
        if not complete:
            category = 'INCOMPLETE'
        elif changed and owner_changed:
            category = 'D'
        elif complete and comparisons[0] == 'CHANGED':
            category = 'A'
        elif complete and comparisons[0] == 'SAME' and comparisons[1] == 'CHANGED':
            category = 'B'
        elif complete and not changed and owner_changed:
            category = 'C'
        elif (complete and not owner_changed and code == 'GUARDS_PASSED_NO_DISPATCH'
              and self.predicate == 'PASS' and self.close == 'OK'):
            category = 'F'
        else:
            category = 'E'
        owners_complete = len(self.samples) == 3 and all(sample[3] for sample in self.samples.values())
        update = ('OWNER_DIFFERENCE_OBSERVED' if owner_changed else
                  ('AMBIGUOUS_SAME_OWNER' if owners_complete else 'AMBIGUOUS_OWNER_UNKNOWN')
                  if changed else 'NOT_OBSERVED')
        parts = []
        for point in (1, 2, 3):
            sample = self.samples.get(point)
            if sample is None:
                flags = 'Q=NA,Z=?,O=UNKNOWN,A=NA'
            else:
                value, q, match, a = sample
                flags = ('Q=' + ('OK' if q else 'FAIL') + ',Z=' + (str(int(value == 0)) if q else '?')
                         + ',O=' + ('MATCH' if a and match else 'DIFF' if a else 'UNKNOWN')
                         + ',A=' + ('OK' if a else 'FAIL'))
            parts.append('S%d[' % point + flags + ']')
        # predicate/close are assigned only fixed internal literals, never exception data.
        return ('SEQ_DIAG ' + ' '.join(parts) + ' D12=' + comparisons[0] + ' D23=' + comparisons[1]
                + ' D13=' + comparisons[2] + ' CLOSE=' + self.close + ' P=' + self.predicate
                + ' CLASS=' + category + ' UPDATE=' + update + ' RESULT=' + code
                + ' CLIPBOARD=' + clipboard + ' CTRLV=NOT_SENT')


class WindowsPasteAPI(WindowsSelectionAPI):
    """Extends the existing native gateway; owns no repository or authorization."""
    def __init__(self):
        super().__init__()
        for lib, name, result, args in (
            (self.user, 'EmptyClipboard', W.BOOL, []),
            (self.user, 'SetClipboardData', W.HANDLE, [W.UINT, W.HANDLE]),
            (self.kernel, 'GlobalAlloc', W.HANDLE, [W.UINT, C.c_size_t]),
            (self.kernel, 'GlobalFree', W.HANDLE, [W.HANDLE]),
        ):
            fn = getattr(lib, name)
            fn.restype, fn.argtypes = result, args

    def register_paste(self):
        return bool(self.user.RegisterHotKey(None, PASTE_HOTKEY_ID, HOTKEY_MODIFIERS, 0x56))

    def unregister_paste(self):
        return bool(self.user.UnregisterHotKey(None, PASTE_HOTKEY_ID))

    def paste_keys_down(self):
        return any(self.user.GetAsyncKeyState(key) & 0x8000 for key in (*RELEASE_KEYS, 0x56))

    def pin_paste(self, target):
        handle = self.pin(target)  # Reuse terminal, elevation, identity and handle safety.
        try:
            image = C.create_unicode_buffer(32768)
            length = W.DWORD(len(image))
            if not self.kernel.QueryFullProcessImageNameW(handle, 0, image, C.byref(length)):
                raise SelectionCopyError('TARGET_UNAVAILABLE', guard='PASTE_IMAGE_QUERY_FAILED')
            if image.value.rsplit('\\', 1)[-1].lower() in PASTE_EXCLUSIONS:
                raise SelectionCopyError('UNSUPPORTED_TARGET', guard='OFFICE_POLICY')
            return handle
        except BaseException:
            self.unpin(handle)
            raise

    def write_text(self, text, owner_hwnd, before_write, *, sequence_diagnostic=None):
        # Allocate every movable buffer before changing the user's Clipboard.
        buffers = []
        opened = False
        state = 'UNCHANGED'
        try:
            entries = [(fmt, b'\0' * 4) for fmt in self.permissions]
            entries += [(fmt, b'\1') for fmt in self.exclusions]
            entries.append((13, (text + '\0').encode('utf-16-le', errors='strict')))
            for fmt, raw in entries:
                handle = self.kernel.GlobalAlloc(0x0002, len(raw))
                if not handle:
                    raise PasteEffectError('ALLOCATION_FAILED')
                buffers.append([fmt, handle])
                ptr = self.kernel.GlobalLock(handle)
                if not ptr:
                    raise PasteEffectError('ALLOCATION_FAILED')
                try:
                    C.memmove(ptr, raw, len(raw))
                finally:
                    C.set_last_error(0)
                    if not self.kernel.GlobalUnlock(handle) and C.get_last_error():
                        raise PasteEffectError('CLEANUP_FAILED')
            if not owner_hwnd or not self.user.OpenClipboard(owner_hwnd):
                raise PasteEffectError('CLIPBOARD_LOCKED')
            opened = True
            before_write()  # Final target/cancellation/time check after native waits.
            state = 'MAY_HAVE_CHANGED'
            if not self.user.EmptyClipboard():
                raise PasteEffectError('CLIPBOARD_WRITE_FAILED', state)
            for entry in buffers:
                if not self.user.SetClipboardData(entry[0], entry[1]):
                    raise PasteEffectError('CLIPBOARD_WRITE_FAILED', state)
                entry[1] = None  # Windows owns successfully transferred handles.
            state = 'WRITTEN'
            try:
                sequence = self.sequence()
            except Exception:
                if sequence_diagnostic is not None:
                    sequence_diagnostic.observe(1, self, owner_hwnd, failed=True)
                raise
            if sequence_diagnostic is not None:
                sequence_diagnostic.observe(1, self, owner_hwnd, value=sequence)
            if not sequence:
                raise PasteEffectError('SEQUENCE_UNAVAILABLE', state)
        except PasteEffectError:
            raise
        except Exception:
            raise PasteEffectError('CLIPBOARD_WRITE_FAILED', state) from None
        finally:
            failed = False
            cleanup_error = None
            if opened:
                try:
                    failed = not self.user.CloseClipboard()
                except Exception as error:
                    failed = True
                    cleanup_error = error
            if opened and sequence_diagnostic is not None:
                sequence_diagnostic.close = 'FAIL' if failed else 'OK'
                if not failed:
                    sequence_diagnostic.observe(2, self, owner_hwnd)
            for _, handle in buffers:
                if handle:  # Successfully transferred handles already belong to Windows.
                    try:
                        if self.kernel.GlobalFree(handle):
                            failed = True
                    except Exception as error:
                        failed = True
                        if cleanup_error is None:
                            cleanup_error = error
            if failed:
                raise PasteEffectError('CLEANUP_FAILED', state) from cleanup_error

        # A pre-close sample is diagnostic evidence, not a dispatch baseline.
        # Verify exact authorized state after successful close before returning one.
        return self._verify_written_text(text, owner_hwnd, before_write)

    def _verify_written_text(self, text, owner_hwnd, before_read):
        """One bounded readback; no retries, provenance claim, or source substitution."""
        opened = False
        try:
            before_read()
            expected = (text + '\0').encode('utf-16-le', errors='strict')
            if decode_unicode(expected) != text:
                raise PasteEffectError('CLIPBOARD_CONTENT_MISMATCH', 'WRITTEN')
            sequence = self.sequence()
            if type(sequence) is not int or not 1 <= sequence <= 0xFFFFFFFF:
                raise PasteEffectError('CLIPBOARD_CHANGED', 'WRITTEN')

            def unchanged():
                if self.sequence() != sequence:
                    raise PasteEffectError('CLIPBOARD_CHANGED', 'WRITTEN')
                hwnd = self.user.GetClipboardOwner()
                if hwnd != owner_hwnd or self._pid(hwnd) != os.getpid():
                    raise PasteEffectError('CLIPBOARD_CHANGED', 'WRITTEN')

            unchanged()
            if not self.user.OpenClipboard(owner_hwnd):
                raise PasteEffectError('CLIPBOARD_VERIFY_LOCKED', 'WRITTEN')
            opened = True
            before_read()
            unchanged()
            # These existing markers are privacy controls, NOT per-operation IDs.
            # GlobalSize can exceed requested size; ignore bounded allocator padding.
            markers = [(fmt, b'\0' * 4) for fmt in self.permissions]
            markers += [(fmt, b'\1') for fmt in self.exclusions]
            for fmt, value in markers:
                if (not self.user.IsClipboardFormatAvailable(fmt)
                        or self._bytes(fmt, 64)[:len(value)] != value):
                    raise PasteEffectError('CLIPBOARD_VERIFY_FAILED', 'WRITTEN')
            if not self.user.IsClipboardFormatAvailable(13):
                raise PasteEffectError('CLIPBOARD_VERIFY_FAILED', 'WRITTEN')
            # 65536 UTF-8 bytes permit at most 131074 UTF-16 bytes with terminator.
            # Bound allocation reads, then decode only the exact expected extent.
            raw = self._bytes(13, 131200)[:len(expected)]
            if raw != expected or decode_unicode(raw) != text:
                raise PasteEffectError('CLIPBOARD_CONTENT_MISMATCH', 'WRITTEN')
            before_read()
            unchanged()
            return sequence
        except PasteEffectError as error:
            # The original effect closure still says UNCHANGED until write_text
            # returns. A post-write cancellation/expiry must truthfully say WRITTEN.
            raise PasteEffectError(str(error), 'WRITTEN', error.dispatch, guard=error.guard) from None
        except SelectionCopyError as error:
            code = 'CLEANUP_FAILED' if str(error) == 'CLEANUP_FAILED' else 'CLIPBOARD_VERIFY_FAILED'
            raise PasteEffectError(code, 'WRITTEN') from None
        except Exception:
            raise PasteEffectError('CLIPBOARD_VERIFY_FAILED', 'WRITTEN') from None
        finally:
            if opened:
                try:
                    closed = self.user.CloseClipboard()
                except Exception as error:
                    # Cleanup takes priority; the completed write and cause survive.
                    raise PasteEffectError('CLEANUP_FAILED', 'WRITTEN') from error
                if not closed:
                    raise PasteEffectError('CLEANUP_FAILED', 'WRITTEN')

    def send_paste(self):
        events = (INPUT * 4)(self._key(0x11), self._key(0x56), self._key(0x56, True), self._key(0x11, True))
        sent = self.user.SendInput(4, events, C.sizeof(INPUT))
        if sent != 4:
            releases = (INPUT * 2)(self._key(0x56, True), self._key(0x11, True))
            if self.user.SendInput(2, releases, C.sizeof(INPUT)) != 2:
                raise PasteEffectError('CLEANUP_FAILED', 'WRITTEN', 'UNCERTAIN')
            raise PasteEffectError('INPUT_DENIED', 'WRITTEN', 'UNCERTAIN' if sent else 'NOT_SENT')


def paste_latest(api, target, owner_hwnd, cancelled, prepare, consume, *, clock=time.monotonic,
                 sleep=time.sleep, utc=lambda: datetime.now(timezone.utc), diagnostic=False, on_release=None, sequence_diagnostic=None):
    """Prepare once, release, consume once, write once, dispatch once; no retry."""
    handle = None
    clipboard, dispatch = 'UNCHANGED', 'NOT_SENT'
    pending_effect_error = None
    stage = 'PIN'
    try:
        handle = api.pin_paste(target)
        def check():
            if cancelled.is_set():
                raise PasteEffectError('CANCELLED', clipboard, dispatch, guard=stage + '_CANCELLED')
            if not api.live(handle):
                raise PasteEffectError('TARGET_CHANGED', clipboard, dispatch, guard=stage + '_PROCESS_NOT_LIVE')
            if api.foreground() != target:
                raise PasteEffectError('TARGET_CHANGED', clipboard, dispatch, guard=stage + '_FOREGROUND_MISMATCH')
        stage = 'WORKER'
        check()
        if not diagnostic:
            target_token = str(uuid4())
            authorization = prepare(target_token)
        stage = 'RELEASE'
        deadline = clock() + 1.5
        while api.paste_keys_down():
            check()
            if clock() >= deadline:
                raise PasteEffectError('RELEASE_TIMEOUT', guard='RELEASE_TIMEOUT')
            sleep(.015)
        if on_release is not None:
            on_release()  # Share an actual all-up sample, never operation completion.
        stage = 'POST_RELEASE'
        check()
        if diagnostic:
            # Same target pin/release checks; no source, authorization or native effect.
            return 'TARGET_VALIDATED_AFTER_RELEASE'
        stage = 'EFFECT'
        started = clock()
        source = consume(authorization)
        if source.authorization != authorization or authorization.target_token != target_token:
            raise PasteEffectError('AUTHORIZATION_MISMATCH')
        expires = datetime.fromisoformat(source.effect_lease_expires_at.replace('Z', '+00:00'))
        def before_write():
            check()
            if not 0 <= clock() - started < 1 or utc() >= expires:
                raise PasteEffectError('EXPIRED', clipboard, dispatch)
            if api.paste_keys_down():
                raise PasteEffectError('MODIFIERS_CHANGED', clipboard, dispatch)
        before_write()
        if sequence_diagnostic is None:
            sequence = api.write_text(source.source.text, owner_hwnd, before_write)
        else:
            sequence = api.write_text(source.source.text, owner_hwnd, before_write,
                                      sequence_diagnostic=sequence_diagnostic)
        clipboard = 'WRITTEN'
        before_write()
        if sequence_diagnostic is None:
            if not sequence or api.sequence() != sequence or api.owner_pid() != os.getpid():
                raise PasteEffectError('CLIPBOARD_CHANGED', clipboard, dispatch)
        elif not sequence_diagnostic.guard(api, sequence, owner_hwnd):
            raise PasteEffectError('CLIPBOARD_CHANGED', clipboard, dispatch)
        # Recheck after observing Clipboard state, immediately before SendInput.
        before_write()
        if sequence_diagnostic is not None:
            return clipboard, 'NOT_SENT'  # Diagnostic never injects Ctrl+V, even on PASS.
        dispatch = 'UNCERTAIN'
        api.send_paste()
        dispatch = 'DISPATCHED'
        return clipboard, dispatch
    except PasteEffectError as error:
        clipboard, dispatch = error.clipboard, error.dispatch
        pending_effect_error = error
        raise
    except ClipboardPasteError as error:
        raise PasteEffectError(error.code.value, clipboard, dispatch) from None
    except SelectionCopyError as error:
        raise PasteEffectError(str(error), clipboard, dispatch, guard=stage + '_' + (error.guard or 'UNCLASSIFIED')) from None
    except Exception:
        raise PasteEffectError('AUTHORIZATION_OR_NATIVE_UNAVAILABLE', clipboard, dispatch, guard=stage + '_NATIVE_EXCEPTION') from None
    finally:
        if handle is not None:
            try:
                api.unpin(handle)
            except Exception:
                raise PasteEffectError('CLEANUP_FAILED', clipboard, dispatch, guard='CLEANUP_HANDLE_CLOSE_FAILED') from pending_effect_error


# Fixed development-only output vocabulary. No exception text or target metadata is displayed.
_BIND_GUARDS = ('NO_WINDOW', 'WINDOW_QUERY_FAILED', 'WINDOW_PROCESS_MISSING')
_PIN_GUARDS = ('SELF_TARGET', 'PROCESS_OPEN_FAILED', 'IMAGE_QUERY_FAILED', 'TERMINAL_POLICY',
               'PROCESS_TIMES_FAILED', 'TOKEN_OPEN_FAILED', 'TOKEN_QUERY_FAILED', 'TOKEN_SIZE_INVALID',
               'ELEVATED_POLICY', 'TOKEN_CLOSE_FAILED', 'REJECTED_HANDLE_CLOSE_FAILED',
               'PASTE_IMAGE_QUERY_FAILED', 'OFFICE_POLICY', 'HANDLE_CLOSE_FAILED')
TARGET_DIAGNOSTIC_CODES = frozenset({
    'TARGET_VALIDATED_AFTER_RELEASE', 'INITIAL_OWNER_WINDOW_FAILED', 'WORKER_START_FAILED',
    'RELEASE_TIMEOUT', 'CLEANUP_HANDLE_CLOSE_FAILED', 'UNCLASSIFIED_GUARD',
    'ADMISSION_CLOSED', 'ADMISSION_CLEANUP_DISABLED', 'ADMISSION_UNREGISTERED',
    'ADMISSION_BUSY', 'ADMISSION_RELEASE_REQUIRED', 'ADMISSION_OTHER_OPERATION_PENDING',
    'ADMISSION_WORKER_COMPLETE_PENDING_DRAIN', 'ADMISSION_RELEASE_EVENT_SIGNALED_NOT_RECONCILED',
    'ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN', 'ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_UP',
    *('INITIAL_' + code for code in _BIND_GUARDS),
    *('PIN_' + code for code in _PIN_GUARDS),
    *(stage + '_' + code for stage in ('WORKER', 'RELEASE', 'POST_RELEASE')
      for code in (*_BIND_GUARDS, 'CANCELLED', 'PROCESS_NOT_LIVE', 'FOREGROUND_MISMATCH')),
    *(stage + '_NATIVE_EXCEPTION' for stage in ('INITIAL', 'PIN', 'WORKER', 'RELEASE', 'POST_RELEASE')),
})


def target_diagnostic_code(code):
    return code if code in TARGET_DIAGNOSTIC_CODES else 'UNCLASSIFIED_GUARD'
