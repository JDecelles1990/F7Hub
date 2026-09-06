"""Application rules for the first usable Knowledge Base slice."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from f7hub.repositories.knowledge_repository import (
    KnowledgeArticleRecord,
    KnowledgeRepository,
)


class KnowledgeValidationError(ValueError):
    """Knowledge article input is invalid."""


class KnowledgeCreationError(RuntimeError):
    """Knowledge article persistence failed; safe to show to a technician."""


class KnowledgeService:
    """Validate and coordinate the narrow create/list/read use cases."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self._repository = repository

    def create_article(
        self,
        *,
        article_code: str,
        title: str,
        summary: str | None,
        body: str,
    ) -> KnowledgeArticleRecord:
        article_code = _required_text(article_code, "Article code")
        title = _required_text(title, "Title")
        body = _required_body(body)
        if summary is not None and not isinstance(summary, str):
            raise KnowledgeValidationError("Summary must be text.")
        normalized_summary = summary.strip() if summary is not None else None
        if not normalized_summary:
            normalized_summary = None
        timestamp = (
            datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
        try:
            return self._repository.create_article(
                article_code=article_code,
                title=title,
                summary=normalized_summary,
                body_markdown=body,
                created_at=timestamp,
                updated_at=timestamp,
            )
        except sqlite3.IntegrityError as error:
            if "knowledge_articles.article_code" in str(error):
                raise KnowledgeValidationError(
                    "Article code is already in use. Choose a different code."
                ) from error
            raise KnowledgeCreationError(
                "Could not create the article. Your entered information is preserved."
            ) from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeCreationError(
                "Could not create the article. Your entered information is preserved."
            ) from error

    def list_articles(self) -> tuple[KnowledgeArticleRecord, ...]:
        try:
            return self._repository.list_articles()
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeCreationError("Could not load knowledge articles.") from error

    def get_article(self, article_id: int) -> KnowledgeArticleRecord | None:
        if isinstance(article_id, bool) or not isinstance(article_id, int):
            raise KnowledgeValidationError("Article ID must be an integer.")
        try:
            return self._repository.get_article(article_id)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeCreationError("Could not load the knowledge article.") from error


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise KnowledgeValidationError(f"{label} must be text.")
    value = value.strip()
    if not value:
        raise KnowledgeValidationError(f"{label} is required.")
    return value


def _required_body(value: object) -> str:
    if not isinstance(value, str):
        raise KnowledgeValidationError("Body must be text.")
    if not value.strip():
        raise KnowledgeValidationError("Body is required.")
    return value
