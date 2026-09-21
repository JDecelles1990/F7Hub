"""Application rules for the first usable Knowledge Base slice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import sqlite3
import unicodedata

from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.tag_repository import TagRecord, TagRepository

from f7hub.repositories.knowledge_repository import (
    ArticleMissingError,
    ArticleNotEditableError,
    ArticleNotPublishableError,
    ArticleNotArchivableError,
    ArticleUnchangedError,
    ArticleVersionMissingError,
    KnowledgeArticleRecord,
    KnowledgeArticleSearchResult,
    KnowledgeArticleVersionListRecord,
    KnowledgeArticleVersionRecord,
    KnowledgeRepository,
    StaleArticleVersionError,
    StaleArticleMetadataError,
    ArticleCategoryUnavailableError,
    ArticleTagUnavailableError,
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


class KnowledgePublishError(RuntimeError):
    """Publishing failed; its message is safe for presentation."""


class KnowledgeArchiveError(RuntimeError):
    """Archiving failed; its message is safe for presentation."""


class KnowledgeSearchError(RuntimeError):
    """Knowledge search failed; its message is safe for presentation."""


KNOWLEDGE_STATUSES = frozenset({"DRAFT", "PUBLISHED", "ARCHIVED"})


@dataclass(frozen=True)
class KnowledgeCategoryOption:
    """Only the category identity and display name needed by the selector."""

    category_id: int
    name: str


class KnowledgeCategoryError(RuntimeError):
    """Category loading or saving failed; safe to show to a technician."""


class KnowledgeCategoryConflictError(KnowledgeCategoryError):
    """Reopen current article state before trying another category write."""


class KnowledgeTagError(RuntimeError):
    """Tag loading or saving failed; safe to show to a technician."""


class KnowledgeTagConflictError(KnowledgeTagError):
    """Reopen current article state before trying another tag write."""


class KnowledgeService:
    """Validate and coordinate the narrow create/list/read use cases."""

    def __init__(self, repository: KnowledgeRepository, categories: CategoryRepository, tags: TagRepository) -> None:
        self._repository = repository
        self._categories = categories
        self._tags = tags

    def list_available_tags(self) -> tuple[TagRecord, ...]:
        try:
            return self._tags.list_tags()
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeTagError("Could not load existing tags. Refresh tags and try again.") from error

    def list_article_tags(self, article_id: int) -> tuple[TagRecord, ...]:
        article_id = _positive_integer(article_id, "Article ID")
        try:
            return self._tags.list_article_tags(article_id)
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeTagError("Could not load article tags. Refresh tags and try again.") from error

    def set_article_tags(self, article_id: int, expected_version_number: int, expected_updated_at: str, tag_ids) -> KnowledgeArticleRecord:
        article_id = _positive_integer(article_id, "Article ID")
        expected_version_number = _positive_integer(expected_version_number, "Expected version")
        _required_text(expected_updated_at, "Expected update time")
        if not isinstance(tag_ids, (tuple, list)):
            raise KnowledgeValidationError("Tag IDs must be a collection of positive integers.")
        normalized = tuple(_positive_integer(tag_id, "Tag ID") for tag_id in tag_ids)
        if len(set(normalized)) != len(normalized):
            raise KnowledgeValidationError("Tag IDs must not contain duplicates.")
        timestamp = _next_metadata_timestamp(expected_updated_at)
        try:
            return self._repository.set_draft_tags(
                article_id=article_id, expected_version_number=expected_version_number,
                expected_updated_at=expected_updated_at, tag_ids=normalized, updated_at=timestamp,
            )
        except ArticleMissingError as error:
            raise KnowledgeTagConflictError("This article no longer exists.") from error
        except ArticleNotEditableError as error:
            raise KnowledgeTagConflictError("Only draft articles can change tags.") from error
        except (StaleArticleVersionError, StaleArticleMetadataError) as error:
            raise KnowledgeTagConflictError("This article changed after you opened it. Reopen the latest article before changing its tags.") from error
        except ArticleTagUnavailableError as error:
            raise KnowledgeTagError("One selected tag is no longer available. Refresh tags and try again.") from error
        except ArticleUnchangedError as error:
            raise KnowledgeTagError("Tags are already selected.") from error
        except (sqlite3.Error, OSError, RuntimeError, OverflowError) as error:
            raise KnowledgeTagError("Could not update article tags. Try again.") from error

    def list_active_knowledge_categories(self) -> tuple[KnowledgeCategoryOption, ...]:
        try:
            return tuple(KnowledgeCategoryOption(row.category_id, row.name)
                         for row in self._categories.list_categories(scope="KNOWLEDGE", active_only=True))
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeCategoryError("Could not load Knowledge categories. Refresh categories and try again.") from error

    def set_article_category(
        self, article_id: int, expected_version_number: int,
        expected_updated_at: str, category_id: int | None,
    ) -> KnowledgeArticleRecord:
        article_id = _positive_integer(article_id, "Article ID")
        expected_version_number = _positive_integer(expected_version_number, "Expected version")
        _required_text(expected_updated_at, "Expected update time")
        if category_id is not None:
            category_id = _positive_integer(category_id, "Category ID")
        timestamp = _next_metadata_timestamp(expected_updated_at)
        try:
            return self._repository.set_draft_category(
                article_id=article_id, expected_version_number=expected_version_number,
                expected_updated_at=expected_updated_at, category_id=category_id, updated_at=timestamp,
            )
        except ArticleMissingError as error:
            raise KnowledgeCategoryConflictError("This article no longer exists.") from error
        except ArticleNotEditableError as error:
            raise KnowledgeCategoryConflictError("Only draft articles can change category.") from error
        except (StaleArticleVersionError, StaleArticleMetadataError) as error:
            raise KnowledgeCategoryConflictError(
                "This article changed after you opened it. Reopen the latest article before changing its category."
            ) from error
        except ArticleCategoryUnavailableError as error:
            raise KnowledgeCategoryError(
                "The selected Knowledge category is no longer available. Refresh categories and try again."
            ) from error
        except ArticleUnchangedError as error:
            raise KnowledgeCategoryError("Category is already selected.") from error
        except (sqlite3.Error, OSError, RuntimeError, OverflowError) as error:
            raise KnowledgeCategoryError("Could not update the article category. Try again.") from error

    def publish_article(
        self, article_id: int, expected_version_number: int,
    ) -> KnowledgeArticleRecord:
        article_id = _positive_integer(article_id, "Article ID")
        expected_version_number = _positive_integer(expected_version_number, "Expected version")
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        try:
            return self._repository.publish_draft_article(
                article_id=article_id, expected_version_number=expected_version_number,
                published_at=timestamp,
            )
        except ArticleMissingError as error:
            raise KnowledgePublishError("This article no longer exists.") from error
        except ArticleNotPublishableError as error:
            raise KnowledgePublishError("Only draft articles can be published.") from error
        except StaleArticleVersionError as error:
            raise KnowledgePublishError(
                "This article changed after you opened it. Reopen the latest version before publishing."
            ) from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgePublishError("Could not publish the article. Try again.") from error

    def archive_article(
        self, article_id: int, expected_version_number: int,
    ) -> KnowledgeArticleRecord:
        article_id = _positive_integer(article_id, "Article ID")
        expected_version_number = _positive_integer(expected_version_number, "Expected version")
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        try:
            return self._repository.archive_published_article(
                article_id=article_id, expected_version_number=expected_version_number,
                archived_at=timestamp,
            )
        except ArticleMissingError as error:
            raise KnowledgeArchiveError("This article no longer exists.") from error
        except ArticleNotArchivableError as error:
            raise KnowledgeArchiveError("Only published articles can be archived.") from error
        except StaleArticleVersionError as error:
            raise KnowledgeArchiveError(
                "This article changed after you opened it. Reopen the latest version before archiving."
            ) from error
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise KnowledgeArchiveError("Could not archive the article. Try again.") from error

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

    def list_articles(
        self, *, category_id: int | None = None, uncategorized_only: bool = False,
        status: str | None = None, tag_id: int | None = None,
        untagged_only: bool = False,
    ) -> tuple[KnowledgeArticleRecord, ...]:
        _validate_category_filter(category_id, uncategorized_only)
        _validate_status_filter(status)
        _validate_tag_filter(tag_id, untagged_only)
        try:
            arguments = {
                "category_id": category_id,
                "uncategorized_only": uncategorized_only,
            }
            if status is not None:
                arguments["status"] = status
            if tag_id is not None:
                arguments["tag_id"] = tag_id
            if untagged_only:
                arguments["untagged_only"] = True
            return self._repository.list_articles(**arguments)
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
        self, query: str, *, category_id: int | None = None,
        uncategorized_only: bool = False, status: str | None = None,
        tag_id: int | None = None, untagged_only: bool = False,
    ) -> tuple[KnowledgeArticleSearchResult, ...]:
        """Search current articles using a safe literal FTS expression."""

        _validate_category_filter(category_id, uncategorized_only)
        _validate_status_filter(status)
        _validate_tag_filter(tag_id, untagged_only)
        if not isinstance(query, str):
            raise KnowledgeValidationError("Search query must be text.")
        fts_query = _literal_fts_query(query)
        if not fts_query:
            return ()
        try:
            arguments = {
                "category_id": category_id,
                "uncategorized_only": uncategorized_only,
            }
            if status is not None:
                arguments["status"] = status
            if tag_id is not None:
                arguments["tag_id"] = tag_id
            if untagged_only:
                arguments["untagged_only"] = True
            return self._repository.search_articles(fts_query, **arguments)
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


def _validate_category_filter(category_id: int | None, uncategorized_only: bool) -> None:
    if not isinstance(uncategorized_only, bool):
        raise KnowledgeValidationError("Uncategorized filter must be a boolean.")
    if category_id is not None:
        _positive_integer(category_id, "Category ID")
        if uncategorized_only:
            raise KnowledgeValidationError("Choose one category filter mode.")


def _validate_status_filter(status: str | None) -> None:
    if status is not None and (
        not isinstance(status, str) or status not in KNOWLEDGE_STATUSES
    ):
        raise KnowledgeValidationError(
            "Status filter must be DRAFT, PUBLISHED, ARCHIVED, or All statuses."
        )


def _validate_tag_filter(tag_id: int | None, untagged_only: bool) -> None:
    if not isinstance(untagged_only, bool):
        raise KnowledgeValidationError("Untagged filter must be a boolean.")
    if tag_id is not None:
        _positive_integer(tag_id, "Tag ID")
        if untagged_only:
            raise KnowledgeValidationError("Choose one tag filter mode.")


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


def _next_metadata_timestamp(expected_updated_at: str) -> str:
    """Generate one strictly newer UTC metadata token from one clock read."""
    now = datetime.now(timezone.utc)
    try:
        previous = datetime.fromisoformat(expected_updated_at.replace("Z", "+00:00"))
    except ValueError:
        previous = None
    if previous is not None and previous.tzinfo is not None and now <= previous:
        now = previous + timedelta(microseconds=1)
    return now.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


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
