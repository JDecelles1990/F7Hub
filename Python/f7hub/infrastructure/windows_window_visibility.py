"""Read the existing HWND's visibility style; no messages or window commands."""

import ctypes
from ctypes import wintypes
from functools import lru_cache
import sys


@lru_cache(maxsize=1)
def _visibility_query():
    user32 = ctypes.WinDLL('user32.dll', winmode=0x00000800)  # System32 only.
    query = user32.IsWindowVisible
    query.argtypes = [wintypes.HWND]
    query.restype = wintypes.BOOL
    return query


def is_native_window_visible(window_id: int) -> bool:
    """Return WS_VISIBLE for a known HWND, including when it is obscured."""
    if (sys.platform != 'win32' or isinstance(window_id, bool)
            or not isinstance(window_id, int) or window_id <= 0):
        return False
    return bool(_visibility_query()(window_id))
