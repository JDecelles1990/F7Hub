"""Compatibility launcher: python Mochi/src/main.py, from any directory."""

from mochi.app import main


if __name__ == "__main__":
    raise SystemExit(main())
