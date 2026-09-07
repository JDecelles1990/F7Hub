"""RELATED-only ticket/knowledge use cases and safe application errors."""

from datetime import datetime, timezone
import sqlite3

from f7hub.repositories.ticket_knowledge_repository import (
    ArticleAlreadyLinkedError, ArticleNotLinkedError, LinkArticleMissingError, LinkTicketMissingError,
    TicketKnowledgeCandidateRecord, TicketKnowledgeLinkRecord, TicketKnowledgeRepository,
)


class TicketKnowledgeValidationError(ValueError):
    """Invalid link input; safe to present."""


class TicketKnowledgeTicketMissingError(TicketKnowledgeValidationError):
    """The ticket no longer exists."""


class TicketKnowledgeArticleMissingError(TicketKnowledgeValidationError):
    """The article no longer exists."""


class TicketKnowledgeAlreadyLinkedError(TicketKnowledgeValidationError):
    """The exact RELATED link already exists."""


class TicketKnowledgeNotLinkedError(TicketKnowledgeValidationError):
    """The exact RELATED link no longer exists."""


class TicketKnowledgePersistenceError(RuntimeError):
    """Persistence failed; safe to present."""


class TicketKnowledgeService:
    def __init__(self, repository: TicketKnowledgeRepository) -> None:
        self._repository = repository

    def link_related_article(
        self, ticket_id: int, knowledge_article_id: int, linked_by: str | None = None,
    ) -> TicketKnowledgeLinkRecord:
        _positive_id(ticket_id, "Ticket ID")
        _positive_id(knowledge_article_id, "Article ID")
        if linked_by is not None and not isinstance(linked_by, str):
            raise TicketKnowledgeValidationError("Linked by must be text.")
        linked_by = (linked_by.strip() or None) if linked_by is not None else None
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        return _safe_call(
            lambda: self._repository.link_related_article(
                ticket_id=ticket_id, knowledge_article_id=knowledge_article_id,
                linked_by=linked_by, linked_at=timestamp,
            ),
            "Could not link the article. Your selection is preserved. Try again.",
        )

    def unlink_related_article(self, ticket_id: int, knowledge_article_id: int) -> None:
        _positive_id(ticket_id, "Ticket ID")
        _positive_id(knowledge_article_id, "Article ID")
        _safe_call(
            lambda: self._repository.unlink_related_article(
                ticket_id=ticket_id, knowledge_article_id=knowledge_article_id,
            ),
            "Could not unlink the article. Your selection is preserved. Try again.",
        )

    def list_linked_articles(self, ticket_id: int) -> tuple[TicketKnowledgeLinkRecord, ...]:
        _positive_id(ticket_id, "Ticket ID")
        return _safe_call(
            lambda: self._repository.list_linked_articles(ticket_id),
            "Could not load linked articles. Try again.",
        )

    def list_link_candidates(self, ticket_id: int) -> tuple[TicketKnowledgeCandidateRecord, ...]:
        _positive_id(ticket_id, "Ticket ID")
        return _safe_call(
            lambda: self._repository.list_link_candidates(ticket_id),
            "Could not load articles to link. Try again.",
        )


def _positive_id(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 9223372036854775807:
        raise TicketKnowledgeValidationError(f"{label} must be a positive SQLite integer.")


def _safe_call(operation, fallback):
    try:
        return operation()
    except LinkTicketMissingError as error:
        raise TicketKnowledgeTicketMissingError("This ticket no longer exists.") from error
    except LinkArticleMissingError as error:
        raise TicketKnowledgeArticleMissingError("This article no longer exists.") from error
    except ArticleAlreadyLinkedError as error:
        raise TicketKnowledgeAlreadyLinkedError("This article is already linked to this ticket.") from error
    except ArticleNotLinkedError as error:
        raise TicketKnowledgeNotLinkedError(
            "This article is no longer linked to this ticket. Refresh the linked articles."
        ) from error
    except (sqlite3.Error, OSError, RuntimeError) as error:
        raise TicketKnowledgePersistenceError(fallback) from error
