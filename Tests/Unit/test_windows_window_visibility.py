"""Pointer-safe, read-only native visibility boundary checks."""

import unittest
from unittest.mock import Mock, patch

from f7hub.infrastructure import windows_window_visibility as visibility


class WindowVisibilityTests(unittest.TestCase):
    def tearDown(self):
        visibility._visibility_query.cache_clear()

    def test_invalid_handles_never_load_native_library(self):
        with patch.object(visibility.sys, 'platform', 'win32'), patch.object(
                visibility.ctypes, 'WinDLL', create=True) as load:
            for value in (0, -1, True, None, '123'):
                self.assertFalse(visibility.is_native_window_visible(value))
        load.assert_not_called()

    def test_other_platforms_never_load_native_library(self):
        with patch.object(visibility.sys, 'platform', 'linux'), patch.object(
                visibility.ctypes, 'WinDLL', create=True) as load:
            self.assertFalse(visibility.is_native_window_visible(123))
        load.assert_not_called()

    def test_windows_query_uses_pointer_sized_handle_and_system_library(self):
        query = Mock(side_effect=[1, 0])
        library = Mock(IsWindowVisible=query)
        with patch.object(visibility.sys, 'platform', 'win32'), patch.object(
                visibility.ctypes, 'WinDLL', return_value=library, create=True) as load:
            handle = 0x123456789
            self.assertTrue(visibility.is_native_window_visible(handle))
            self.assertFalse(visibility.is_native_window_visible(handle))
        load.assert_called_once_with('user32.dll', winmode=0x00000800)
        self.assertEqual(query.argtypes, [visibility.wintypes.HWND])
        self.assertEqual(query.restype, visibility.wintypes.BOOL)
        self.assertEqual(query.call_args_list[0].args, (handle,))


if __name__ == '__main__':
    unittest.main()
