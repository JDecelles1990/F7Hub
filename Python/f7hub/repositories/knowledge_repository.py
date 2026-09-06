"""SQLite persistence for the first usable Knowledge Base slice."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class KnowledgeArticleRecord:
    """One current knowledge article returned by the repository."""

    knowledge_article_id: int
    article_code: str
    category_id: int | None
    title: str
    summary: str | None
    body_markdown: str
    status: str
    version_number: int
    created_by: str | None
    updated_by: str | None
    created_at: str
    updated_at: str
    published_at: str | None


_ARTICLE_COLUMNS = """
    knowledge_article_id,
    article_code,
    category_id,
    title,
    summary,
    body_markdown,
    status,
    version_number,
    created_by,
    updated_by,
    created_at,
    updated_at,
    published_at
"""


class KnowledgeRepository:
    """Persist and retrieve knowledge articles through configured SQLite connections."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def create_article(
        self,
        *,
        article_code: str,
        title: str,
        summary: str | None,
        body_markdown: str,
        created_at: str,
        updated_at: str,
    ) -> KnowledgeArticleRecord:
        """Create a draft article and its initial snapshot atomically."""

        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                INSERT INTO knowledge_articles (
                    article_code, category_id, title, summary, body_markdown,
                    status, version_number, created_by, updated_by,
                    created_at, updated_at, published_at
                ) VALUES (?, NULL, ?, ?, ?, 'DRAFT', 1, NULL, NULL, ?, ?, NULL)
                """,
                (article_code, title, summary, body_markdown, created_at, updated_at),
            )
            article_id = int(cursor.lastrowid)
            connection.execute(
                """
                INSERT INTO knowledge_article_versions (
                    knowledge_article_id, version_number, title, summary,
                    body_markdown, change_summary, created_by, created_at
                ) VALUES (?, 1, ?, ?, ?, NULL, NULL, ?)
                """,
                (article_id, title, summary, body_markdown, created_at),
            )
            article = _get_article(connection, article_id)
            if article is None:
                raise RuntimeError("Inserted knowledge article could not be reloaded.")
            connection.commit()
        return article

    def get_article(self, article_id: int) -> KnowledgeArticleRecord | None:
        """Return an article by internal ID, or ``None`` when absent."""

        with database_connection(self._database_path) as connection:
            return _get_article(connection, article_id)

    def list_articles(self) -> tuple[KnowledgeArticleRecord, ...]:
        """Return all statuses, newest update first with a stable ID tie-breaker."""

        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT {_ARTICLE_COLUMNS}
                FROM knowledge_articles
                ORDER BY updated_at DESC, knowledge_article_id DESC
                """
            ).fetchall()
        return tuple(_article_from_row(row) for row in rows)


def _get_article(
    connection: sqlite3.Connection,
    article_id: int,
) -> KnowledgeArticleRecord | None:
    row = connection.execute(
        f"""
        SELECT {_ARTICLE_COLUMNS}
        FROM knowledge_articles
        WHERE knowledge_article_id = ?
        """,
        (article_id,),
    ).fetchone()
    return _article_from_row(row) if row is not None else None


def _article_from_row(row: sqlite3.Row) -> KnowledgeArticleRecord:
    return KnowledgeArticleRecord(
        knowledge_article_id=int(row["knowledge_article_id"]),
        article_code=str(row["article_code"]),
        category_id=row["category_id"],
        title=str(row["title"]),
        summary=row["summary"],
        body_markdown=str(row["body_markdown"]),
        status=str(row["status"]),
        version_number=int(row["version_number"]),
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        published_at=row["published_at"],
    )
