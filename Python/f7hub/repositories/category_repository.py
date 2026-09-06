"""Read shared category taxonomy through configured SQLite connections."""

from dataclasses import dataclass
from pathlib import Path

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class CategoryRecord:
    """Category identity and ordering facts for reference reads."""

    category_id: int
    scope: str
    name: str
    is_active: int
    sort_order: int


class CategoryRepository:
    """Read categories without choosing a consuming feature's scope or policy."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def list_categories(self, *, scope: str, active_only: bool = False) -> tuple[CategoryRecord, ...]:
        """Return scoped rows ordered by sort order, case-insensitive name and ID."""
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                "SELECT category_id, scope, name, is_active, sort_order FROM categories "
                "WHERE scope = ? AND (? = 0 OR is_active = 1) "
                "ORDER BY sort_order, name, category_id",
                (scope, int(active_only)),
            ).fetchall()
        return tuple(CategoryRecord(**dict(row)) for row in rows)
