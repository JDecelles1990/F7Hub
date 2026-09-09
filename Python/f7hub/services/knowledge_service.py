"""Application rules for the first usable Knowledge Base slice."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
import unicodedata

from f7hub.repositories.knowledge_repository import (
    ArticleMissingError,
    ArticleNotEditableError,
    ArticleUnchangedError,
    ArticleVersionMissingError,
    KnowledgeArticleRecord,
    KnowledgeArticleSearchResult,
    KnowledgeArticleVersionListRecord,
    KnowledgeArticleVersionRecord,
    KnowledgeRepository,
    StaleArticleVersionError,
)


class KnowledgeValidationError(ValueError):
    """Knowledge article input is invalid."""


class KnowledgeCreationError(RuntimeError):
    """Knowledge article persistence failed; safe to show to a technician."""


class KnowledgeUpdateError(RuntimeError):
    """A revision failed; its message is safe for presentation."""


class KnowledgeEditConflictError(KnowledgeUpdateError):
    """The editor must reopen the article before saving again."""


class KnowledgeNoChangesError(KnowledgeUpdateError):
    """No revision was needed after checking authoritative current state."""


class KnowledgeHistoryError(RuntimeError):
    """Version-history loading failed; its message is safe for presentation."""


class KnowledgeHistoryArticleMissingError(KnowledgeHistoryError):
    """The current article disappeared before history could be read."""


class KnowledgeHistoryVersionMissingError(KnowledgeHistoryError):
    """The selected historical revision is no longer available."""


class KnowledgeSearchError(RuntimeError):
    """Knowledge search failed; its message is safe for presentation."""


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

    def update_article(
        self,
        *,
        article_id: int,
        expected_version_number: int,
        title: str,
        summary: str | None,
        body: str,
    ) -> KnowledgeArticleRecord:
        for value, label in (
            (article_id, "Article ID"),
            (expected_version_number, "Expected version"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise KnowledgeValidationError(f"{label} must be a positive integer.")
        title = _required_text(title, "Title")
        body = _required_body(body)
        if summary is not None and not isinstance(summary, str):
            raise KnowledgeValidationError("Summary must be text.")
        summary = (summary.strip() or None) if summary is not None else None
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        try:
            return self._repository.update_draft_article(
                article_id=article_id, expected_version_number=expected_version_number,
                title=title, summary=summary, body_markdown=body, updated_at=timestamp,
            )
        except StaleArticleVersionError as error:
            raise KnowledgeEditConflictError(
                "This article changed after you opened it. Reopen the latest version "
                "before saving your changes. Your entered information is preserved."
            ) from error
        except ArticleNotEditableError as error:
            raise KnowledgeEditConflictError("Only draft articles can be edited.") from error
        except ArticleMissingError as error:
            raise KnowledgeEditConflictError("This article no longer exists.") from error
        except ArticleUnchangedError as error:
            raise KnowledgeNoChangesError("No changes to save.") from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeUpdateError(
                "Could not save the revision. Your entered information is preserved."
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

    def search_articles(
        self, query: str,
    ) -> tuple[KnowledgeArticleSearchResult, ...]:
        """Search current articles using a safe literal FTS expression."""

        if not isinstance(query, str):
            raise KnowledgeValidationError("Search query must be text.")
        fts_query = _literal_fts_query(query)
        if not fts_query:
            return ()
        try:
            return self._repository.search_articles(fts_query)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeSearchError(
                "Could not search knowledge articles. Check the query and try again."
            ) from error

    def list_article_versions(
        self, article_id: int,
    ) -> tuple[KnowledgeArticleVersionListRecord, ...]:
        _positive_integer(article_id, "Article ID")
        try:
            return self._repository.list_article_versions(article_id)
        except ArticleMissingError as error:
            raise KnowledgeHistoryArticleMissingError(
                "This article no longer exists. Close Version History and refresh the Knowledge Base."
            ) from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeHistoryError(
                "Could not load version history. Close and try again."
            ) from error

    def get_article_version(
        self, article_id: int, version_number: int,
    ) -> KnowledgeArticleVersionRecord:
        _positive_integer(article_id, "Article ID")
        _positive_integer(version_number, "Version number")
        try:
            return self._repository.get_article_version(article_id, version_number)
        except ArticleMissingError as error:
            raise KnowledgeHistoryArticleMissingError(
                "This article no longer exists. Close Version History and refresh the Knowledge Base."
            ) from error
        except ArticleVersionMissingError as error:
            raise KnowledgeHistoryVersionMissingError(
                "This revision is no longer available. Close Version History and reopen it."
            ) from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeHistoryError(
                "Could not load the selected revision. Close and try again."
            ) from error


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


def _positive_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise KnowledgeValidationError(f"{label} must be a positive integer.")
    return value


def _literal_fts_query(query: str) -> str:
    """Turn plain text into implicitly-ANDed quoted unicode61 tokens."""

    tokens: list[str] = []
    token_characters: list[str] = []
    for character in query:
        category = unicodedata.category(character)
        if category[0] in {"L", "N"} or category == "Co":
            token_characters.append(character)
        elif token_characters:
            tokens.append("".join(token_characters))
            token_characters.clear()
    if token_characters:
        tokens.append("".join(token_characters))
    return " ".join(f'"{token}"' for token in tokens)
