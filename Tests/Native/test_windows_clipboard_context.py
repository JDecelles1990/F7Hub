"""WINDOWS_NATIVE process/token API checks only; no IPC/enrollment/Clipboard."""
import ctypes as C
from ctypes import wintypes as W
import os
import struct
import subprocess
import sys
import unittest

from f7hub.infrastructure import windows_clipboard_context as m


@unittest.skipUnless(os.name == 'nt' and C.sizeof(C.c_void_p) == 8, '64-bit Windows required')
class WindowsContextTests(unittest.TestCase):
    def setUp(self):
        self.kernel = C.WinDLL('kernel32', use_last_error=True)
        self.kernel.OpenProcess.restype = W.HANDLE
        self.kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
        self.kernel.CloseHandle.argtypes = [W.HANDLE]
        self.kernel.CloseHandle.restype = W.BOOL
        # Opening our OWN process is fixture setup, never production peer discovery.
        self.server = self.kernel.OpenProcess(0x00100000 | 0x1000, False, os.getpid())
        self.assertTrue(self.server)
        self.addCleanup(self.close_server)
        # Finite child watchdog bounds survival if the outer harness is interrupted.
        script = ('import sys,os,threading; '
                  't=threading.Timer(10,lambda:os._exit(9)); t.start(); '
                  'sys.stdout.buffer.write(b"R"); sys.stdout.buffer.flush(); '
                  'sys.stdin.buffer.read(1); t.cancel()')
        self.child = subprocess.Popen([sys.executable, '-B', '-c', script],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        self.addCleanup(self.finish_child)
        self.assertEqual(self.child.stdout.read(1), b'R')
        self.api = m._WindowsAPI()
        self.args = dict(server_handle=self.server, child_handle=int(self.child._handle),
                         server_pin=self.api.pin(self.server),
                         child_pin=self.api.pin(int(self.child._handle)))

    def close_server(self):
        self.assertTrue(self.kernel.CloseHandle(self.server))

    def finish_child(self):
        if self.child.poll() is None:
            self.child.stdin.write(b'X')
            self.child.stdin.flush()
        try:
            result = self.child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.child.terminate()  # Exact test-owned child only; cleanup failure stays FAIL.
            self.child.wait(timeout=3)
            self.fail('test-owned child failed natural bounded exit')
        finally:
            self.child.stdin.close()
            self.child.stdout.close()
            self.child._handle.Close()
        self.assertEqual(result, 0)

    def test_native_exact_context_and_borrowed_handles_remain_live(self):
        raw = m.read_pinned_context(b'G' * 16, **self.args)
        self.assertEqual(len(raw), 112)
        self.assertEqual(struct.unpack_from('<IQIQ', raw, 16),
                         (*self.args['server_pin'], *self.args['child_pin']))
        self.assertEqual(raw[108:], struct.pack('<I', 8192))
        self.api.live(self.server)
        self.api.live(int(self.child._handle))

    def test_native_wrong_creation_rejected(self):
        pin = self.args['child_pin']
        self.args['child_pin'] = (pin[0], pin[1] + 1)
        with self.assertRaisesRegex(m.NativeContextError, '^NATIVE_CONTEXT_REJECTED$'):
            m.read_pinned_context(b'G' * 16, **self.args)
        self.api.live(int(self.child._handle))

    def test_native_exited_original_child_rejected(self):
        self.child.stdin.write(b'X')
        self.child.stdin.flush()
        self.assertEqual(self.child.wait(timeout=3), 0)
        with self.assertRaisesRegex(m.NativeContextError, '^NATIVE_CONTEXT_REJECTED$'):
            m.read_pinned_context(b'G' * 16, **self.args)


if __name__ == '__main__':
    unittest.main()
