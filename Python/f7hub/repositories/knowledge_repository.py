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


@dataclass(frozen=True)
class KnowledgeArticleSearchResult:
    """Lightweight current-article identity returned by FTS5 search."""

    knowledge_article_id: int
    article_code: str
    title: str
    status: str
    version_number: int
    updated_at: str


@dataclass(frozen=True)
class KnowledgeArticleVersionListRecord:
    """Lightweight immutable revision metadata; intentionally excludes bodies."""

    knowledge_article_version_id: int
    knowledge_article_id: int
    version_number: int
    title: str
    change_summary: str | None
    created_by: str | None
    created_at: str


@dataclass(frozen=True)
class KnowledgeArticleVersionRecord:
    """One exact immutable historical revision snapshot."""

    knowledge_article_version_id: int
    knowledge_article_id: int
    version_number: int
    title: str
    summary: str | None
    body_markdown: str
    change_summary: str | None
    created_by: str | None
    created_at: str


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


class ArticleMissingError(RuntimeError):
    """The article was removed before the revision could be saved."""


class ArticleNotEditableError(RuntimeError):
    """The current article is not a draft."""


class StaleArticleVersionError(RuntimeError):
    """The editor's expected version is no longer current."""


class ArticleUnchangedError(RuntimeError):
    """Validated current content is identical to the proposed revision."""


class ArticleVersionMissingError(RuntimeError):
    """The requested immutable revision does not exist for the article."""


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

    def update_draft_article(
        self,
        *,
        article_id: int,
        expected_version_number: int,
        title: str,
        summary: str | None,
        body_markdown: str,
        updated_at: str,
    ) -> KnowledgeArticleRecord:
        """Save current content and its new snapshot, or roll back both.

        Check stale state before comparing content: even an unchanged stale
        editor must reopen the latest version. Prior snapshots are never edited.
        """
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            current = _get_article(connection, article_id)
            if current is None:
                raise ArticleMissingError()
            if current.status != "DRAFT":
                raise ArticleNotEditableError()
            if current.version_number != expected_version_number:
                raise StaleArticleVersionError()
            if (current.title, current.summary, current.body_markdown) == (
                title, summary, body_markdown
            ):
                raise ArticleUnchangedError()
            next_version = current.version_number + 1
            cursor = connection.execute(
                """
                UPDATE knowledge_articles
                SET title = ?, summary = ?, body_markdown = ?,
                    version_number = ?, updated_at = ?
                WHERE knowledge_article_id = ? AND version_number = ?
                    AND status = 'DRAFT'
                """,
                (title, summary, body_markdown, next_version, updated_at,
                 article_id, expected_version_number),
            )
            if cursor.rowcount != 1:
                raise StaleArticleVersionError()
            connection.execute(
                """
                INSERT INTO knowledge_article_versions (
                    knowledge_article_id, version_number, title, summary,
                    body_markdown, change_summary, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, NULL, NULL, ?)
                """,
                (article_id, next_version, title, summary, body_markdown, updated_at),
            )
            article = _get_article(connection, article_id)
            if article is None:
                raise RuntimeError("Updated knowledge article could not be reloaded.")
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

    def search_articles(
        self, fts_query: str,
    ) -> tuple[KnowledgeArticleSearchResult, ...]:
        """Search the derived current-article index and return lightweight rows."""

        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    ka.knowledge_article_id,
                    ka.article_code,
                    ka.title,
                    ka.status,
                    ka.version_number,
                    ka.updated_at
                FROM knowledge_articles_fts
                JOIN knowledge_articles AS ka
                    ON ka.knowledge_article_id = knowledge_articles_fts.rowid
                WHERE knowledge_articles_fts MATCH ?
                ORDER BY
                    bm25(knowledge_articles_fts),
                    ka.updated_at DESC,
                    ka.knowledge_article_id DESC
                """,
                (fts_query,),
            ).fetchall()
        return tuple(_search_result_from_row(row) for row in rows)

    def list_article_versions(
        self, article_id: int,
    ) -> tuple[KnowledgeArticleVersionListRecord, ...]:
        """Return lightweight immutable revisions newest-first using SELECT only."""

        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN")
            if not _article_exists(connection, article_id):
                raise ArticleMissingError()
            rows = connection.execute(
                """
                SELECT knowledge_article_version_id, knowledge_article_id,
                       version_number, title, change_summary, created_by, created_at
                FROM knowledge_article_versions
                WHERE knowledge_article_id = ?
                ORDER BY version_number DESC
                """,
                (article_id,),
            ).fetchall()
        return tuple(_version_list_from_row(row) for row in rows)

    def get_article_version(
        self, article_id: int, version_number: int,
    ) -> KnowledgeArticleVersionRecord:
        """Return exactly one stored revision snapshot using SELECT only."""

        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN")
            if not _article_exists(connection, article_id):
                raise ArticleMissingError()
            row = connection.execute(
                """
                SELECT knowledge_article_version_id, knowledge_article_id,
                       version_number, title, summary, body_markdown,
                       change_summary, created_by, created_at
                FROM knowledge_article_versions
                WHERE knowledge_article_id = ? AND version_number = ?
                """,
                (article_id, version_number),
            ).fetchone()
        if row is None:
            raise ArticleVersionMissingError()
        return _version_from_row(row)


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


def _article_exists(connection: sqlite3.Connection, article_id: int) -> bool:
    return connection.execute(
        "SELECT 1 FROM knowledge_articles WHERE knowledge_article_id = ?",
        (article_id,),
    ).fetchone() is not None


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


def _search_result_from_row(row: sqlite3.Row) -> KnowledgeArticleSearchResult:
    return KnowledgeArticleSearchResult(
        knowledge_article_id=int(row["knowledge_article_id"]),
        article_code=str(row["article_code"]),
        title=str(row["title"]),
        status=str(row["status"]),
        version_number=int(row["version_number"]),
        updated_at=str(row["updated_at"]),
    )


def _version_list_from_row(row: sqlite3.Row) -> KnowledgeArticleVersionListRecord:
    return KnowledgeArticleVersionListRecord(
        knowledge_article_version_id=int(row["knowledge_article_version_id"]),
        knowledge_article_id=int(row["knowledge_article_id"]),
        version_number=int(row["version_number"]),
        title=str(row["title"]),
        change_summary=row["change_summary"],
        created_by=row["created_by"],
        created_at=str(row["created_at"]),
    )


def _version_from_row(row: sqlite3.Row) -> KnowledgeArticleVersionRecord:
    return KnowledgeArticleVersionRecord(
        knowledge_article_version_id=int(row["knowledge_article_version_id"]),
        knowledge_article_id=int(row["knowledge_article_id"]),
        version_number=int(row["version_number"]),
        title=str(row["title"]),
        summary=row["summary"],
        body_markdown=str(row["body_markdown"]),
        change_summary=row["change_summary"],
        created_by=row["created_by"],
        created_at=str(row["created_at"]),
    )
