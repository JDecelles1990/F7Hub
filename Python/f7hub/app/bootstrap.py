"""Construct the current F7Hub application dependencies in one place."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from f7hub.gui.main_window import MainWindow
from f7hub.infrastructure.database import BootstrapResult, bootstrap_database
from f7hub.infrastructure.database_paths import resolve_development_database_path
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import TicketService


DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class ApplicationContext:
    """Stable objects constructed for the current application process."""

    database_path: Path
    bootstrap_result: BootstrapResult
    ticket_repository: TicketRepository
    ticket_service: TicketService
    main_window: MainWindow


def bootstrap_application(
    *,
    project_root: str | Path = DEFAULT_PROJECT_ROOT,
    database_path: str | Path | None = None,
) -> ApplicationContext:
    """Initialize persistence, services, and the main application window."""

    resolved_project_root = Path(project_root).expanduser().resolve(strict=False)
    resolved_database_path = (
        resolve_development_database_path(resolved_project_root)
        if database_path is None
        else Path(database_path).expanduser().resolve(strict=False)
    )
    migrations_dir = resolved_project_root / "Database" / "Migrations"

    bootstrap_result = bootstrap_database(
        resolved_database_path,
        migrations_dir,
    )
    ticket_repository = TicketRepository(resolved_database_path)
    ticket_service = TicketService(ticket_repository)
    main_window = MainWindow(ticket_service)

    return ApplicationContext(
        database_path=resolved_database_path,
        bootstrap_result=bootstrap_result,
        ticket_repository=ticket_repository,
        ticket_service=ticket_service,
        main_window=main_window,
    )
