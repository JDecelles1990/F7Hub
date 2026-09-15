"""Read the global tag taxonomy and current article tag relationships."""

from dataclasses import dataclass
from pathlib import Path

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class TagRecord:
    """A global tag identity suitable for an article selector."""

    tag_id: int
    name: str


class TagRepository:
    """Read existing global tags without assigning a consumer-specific scope."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def list_tags(self) -> tuple[TagRecord, ...]:
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                "SELECT tag_id, name FROM tags ORDER BY name COLLATE NOCASE, tag_id"
            ).fetchall()
        return tuple(TagRecord(int(row["tag_id"]), str(row["name"])) for row in rows)

    def list_article_tags(self, article_id: int) -> tuple[TagRecord, ...]:
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                """
                SELECT t.tag_id, t.name
                FROM knowledge_article_tags AS kat
                JOIN tags AS t ON t.tag_id = kat.tag_id
                WHERE kat.knowledge_article_id = ?
                ORDER BY t.name COLLATE NOCASE, t.tag_id
                """,
                (article_id,),
            ).fetchall()
        return tuple(TagRecord(int(row["tag_id"]), str(row["name"])) for row in rows)
