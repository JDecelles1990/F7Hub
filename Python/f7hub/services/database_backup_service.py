"""Explicit local backup of the active F7Hub SQLite database."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from uuid import uuid4

from f7hub.infrastructure.database import create_database_snapshot


class DatabaseBackupError(RuntimeError):
    """A database backup could not be completed."""


class DatabaseBackupService:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).expanduser().resolve(strict=False)

    def create_backup(self) -> Path:
        """Return the final published path of a validated manual backup."""
        try:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if not local_app_data:
                raise ValueError("LOCALAPPDATA is unavailable")
            if not Path(local_app_data).expanduser().is_absolute():
                raise ValueError("LOCALAPPDATA must be absolute")
            backup_directory = (
                Path(local_app_data).expanduser().resolve(strict=False)
                / "F7Hub" / "Backups"
            )
            final_name = _backup_filename()
            return create_database_snapshot(self.database_path, backup_directory, final_name)
        except Exception as error:
            raise DatabaseBackupError("The database backup could not be completed.") from error


def _backup_filename() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"F7Hub-Database-{timestamp}-{uuid4().hex}.db"
