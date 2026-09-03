"""Resolve development and installed-runtime SQLite database paths."""

from __future__ import annotations

import os
from pathlib import Path


DEVELOPMENT_DATABASE_RELATIVE_PATH = Path("Database", "Dev", "f7hub_dev.db")
RUNTIME_DATABASE_RELATIVE_PATH = Path("F7Hub", "Data", "f7hub.db")


class DatabasePathError(ValueError):
    """Raised when a database path cannot be resolved safely."""


def resolve_development_database_path(project_root: str | Path) -> Path:
    """Return the development database path for an explicit project root."""

    root_path = _require_non_empty_path(project_root, "project_root")
    return root_path.resolve(strict=False) / DEVELOPMENT_DATABASE_RELATIVE_PATH


def resolve_runtime_database_path(
    local_app_data: str | Path | None = None,
) -> Path:
    """Return the installed-runtime database path below LocalAppData.

    ``local_app_data`` is injectable so callers and tests do not need to mutate
    process environment variables.
    """

    base_path_value = local_app_data
    if base_path_value is None:
        base_path_value = os.environ.get("LOCALAPPDATA")

    if base_path_value is None:
        raise DatabasePathError(
            "LOCALAPPDATA is not set; the runtime database path cannot be resolved."
        )

    base_path = _require_non_empty_path(base_path_value, "local_app_data")
    return base_path.resolve(strict=False) / RUNTIME_DATABASE_RELATIVE_PATH


def _require_non_empty_path(path_value: str | Path, parameter_name: str) -> Path:
    raw_path = os.fspath(path_value)
    if not raw_path.strip():
        raise DatabasePathError(f"{parameter_name} must not be empty.")
    return Path(raw_path).expanduser()

