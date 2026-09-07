"""Persistence and lightweight current metadata for RELATED ticket/article links."""

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from f7hub.infrastructure.database import database_connection


@dataclass(frozen=True)
class TicketKnowledgeCandidateRecord:
    knowledge_article_id: int
    article_code: str
    article_title: str
    article_status: str
    article_version_number: int


@dataclass(frozen=True)
class TicketKnowledgeLinkRecord(TicketKnowledgeCandidateRecord):
    ticket_id: int
    relationship_type: str
    linked_by: str | None
    linked_at: str


class LinkTicketMissingError(RuntimeError):
    """The relationship's ticket does not exist."""


class LinkArticleMissingError(RuntimeError):
    """The relationship's article does not exist."""


class ArticleAlreadyLinkedError(RuntimeError):
    """An exact RELATED relationship already exists."""


_IDENTITY_COLUMNS = """
    a.knowledge_article_id, a.article_code, a.title AS article_title,
    a.status AS article_status, a.version_number AS article_version_number
"""
_LINK_SELECT = f"""
    SELECT {_IDENTITY_COLUMNS}, l.ticket_id, l.relationship_type,
           l.linked_by, l.linked_at
    FROM ticket_knowledge_articles AS l
    JOIN knowledge_articles AS a USING (knowledge_article_id)
    WHERE l.ticket_id = ? AND l.relationship_type = 'RELATED'
"""


class TicketKnowledgeRepository:
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = database_path

    def link_related_article(
        self, *, ticket_id: int, knowledge_article_id: int,
        linked_by: str | None, linked_at: str,
    ) -> TicketKnowledgeLinkRecord:
        """Validate existence, insert and reload under one writer reservation."""
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            _require_ticket(connection, ticket_id)
            if connection.execute(
                "SELECT 1 FROM knowledge_articles WHERE knowledge_article_id = ?",
                (knowledge_article_id,),
            ).fetchone() is None:
                raise LinkArticleMissingError()
            if _get_link(connection, ticket_id, knowledge_article_id) is not None:
                raise ArticleAlreadyLinkedError()
            connection.execute(
                """INSERT INTO ticket_knowledge_articles
                   (ticket_id, knowledge_article_id, relationship_type, linked_by, linked_at)
                   VALUES (?, ?, 'RELATED', ?, ?)""",
                (ticket_id, knowledge_article_id, linked_by, linked_at),
            )
            link = _get_link(connection, ticket_id, knowledge_article_id)
            if link is None:
                raise RuntimeError("Inserted ticket/article link could not be reloaded.")
            connection.commit()
        return link

    def list_linked_articles(self, ticket_id: int) -> tuple[TicketKnowledgeLinkRecord, ...]:
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN")
            _require_ticket(connection, ticket_id)
            rows = connection.execute(
                _LINK_SELECT + " ORDER BY a.article_code COLLATE NOCASE, a.knowledge_article_id",
                (ticket_id,),
            ).fetchall()
        return tuple(TicketKnowledgeLinkRecord(**dict(row)) for row in rows)

    def list_link_candidates(self, ticket_id: int) -> tuple[TicketKnowledgeCandidateRecord, ...]:
        """All statuses, without bodies or already RELATED articles."""
        with database_connection(self._database_path) as connection:
            connection.execute("BEGIN")
            _require_ticket(connection, ticket_id)
            rows = connection.execute(
                f"""SELECT {_IDENTITY_COLUMNS} FROM knowledge_articles AS a
                    WHERE NOT EXISTS (
                        SELECT 1 FROM ticket_knowledge_articles AS l
                        WHERE l.ticket_id = ?
                          AND l.knowledge_article_id = a.knowledge_article_id
                          AND l.relationship_type = 'RELATED'
                    )
                    ORDER BY a.article_code COLLATE NOCASE, a.knowledge_article_id""",
                (ticket_id,),
            ).fetchall()
        return tuple(TicketKnowledgeCandidateRecord(**dict(row)) for row in rows)


def _require_ticket(connection: sqlite3.Connection, ticket_id: int) -> None:
    if connection.execute("SELECT 1 FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone() is None:
        raise LinkTicketMissingError()


def _get_link(connection, ticket_id, article_id):
    row = connection.execute(
        _LINK_SELECT + " AND l.knowledge_article_id = ?", (ticket_id, article_id),
    ).fetchone()
    return TicketKnowledgeLinkRecord(**dict(row)) if row is not None else None
