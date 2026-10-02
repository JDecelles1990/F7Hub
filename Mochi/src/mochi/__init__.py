"""Mochi's local desktop-pet runtime. No F7Hub or provider integration."""
"""Standalone renderer using F7Hub's shared, data-free IPC contract."""

from pathlib import Path
import sys

# Script/module routes share checkout-relative imports; no F7Hub bootstrap.
_python = str(Path(__file__).resolve().parents[3] / 'Python')
if _python not in sys.path:
    sys.path.insert(0, _python)
