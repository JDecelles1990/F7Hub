from datetime import datetime
import sqlite3
import unittest
from unittest.mock import Mock

from f7hub.repositories.ticket_knowledge_repository import (
    TicketKnowledgeRepository, LinkTicketMissingError, LinkArticleMissingError, ArticleAlreadyLinkedError,
    ArticleNotLinkedError,
)
from f7hub.services.ticket_knowledge_service import (
    TicketKnowledgeService, TicketKnowledgeValidationError, TicketKnowledgeTicketMissingError,
    TicketKnowledgeArticleMissingError, TicketKnowledgeAlreadyLinkedError, TicketKnowledgePersistenceError,
    TicketKnowledgeNotLinkedError,
)


class TicketKnowledgeServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock(spec=TicketKnowledgeRepository)
        self.service = TicketKnowledgeService(self.repository)

    def test_valid_link_normalizes_actor_and_generates_utc_timestamp(self):
        result = self.service.link_related_article(1, 2, "  Technician  ")
        self.assertIs(result, self.repository.link_related_article.return_value)
        values = self.repository.link_related_article.call_args.kwargs
        self.assertEqual(set(values), {"ticket_id", "knowledge_article_id", "linked_by", "linked_at"})
        self.assertEqual((values["ticket_id"], values["knowledge_article_id"], values["linked_by"]), (1, 2, "Technician"))
        self.assertTrue(values["linked_at"].endswith("Z"))
        self.assertIsNotNone(datetime.fromisoformat(values["linked_at"]).tzinfo)

    def test_blank_and_absent_actor_are_null(self):
        for actor in (None, "", " \n "):
            self.service.link_related_article(1, 2, actor)
            self.assertIsNone(self.repository.link_related_article.call_args.kwargs["linked_by"])

    def test_actor_must_be_text(self):
        with self.assertRaises(TicketKnowledgeValidationError):
            self.service.link_related_article(1, 2, 123)
        self.repository.link_related_article.assert_not_called()

    def test_ticket_id_validation_for_all_operations(self):
        for value in (True, False, 0, -1, 1.0, "1", None, 2**63):
            for operation in (lambda x: self.service.link_related_article(x, 1),
                              self.service.list_linked_articles, self.service.list_link_candidates):
                with self.subTest(value=value), self.assertRaises(TicketKnowledgeValidationError):
                    operation(value)
        self.assertEqual(self.repository.mock_calls, [])

    def test_article_id_validation(self):
        for value in (True, False, 0, -1, 1.0, "1", None, 2**63):
            with self.subTest(value=value), self.assertRaises(TicketKnowledgeValidationError):
                self.service.link_related_article(1, value)
        self.repository.link_related_article.assert_not_called()

    def test_sqlite_maximum_ids_are_accepted(self):
        self.service.link_related_article(2**63 - 1, 2**63 - 1)
        self.repository.link_related_article.assert_called_once()

    def test_structured_missing_and_duplicate_translation(self):
        for internal, public, message in (
            (LinkTicketMissingError, TicketKnowledgeTicketMissingError, "This ticket no longer exists."),
            (LinkArticleMissingError, TicketKnowledgeArticleMissingError, "This article no longer exists."),
            (ArticleAlreadyLinkedError, TicketKnowledgeAlreadyLinkedError, "This article is already linked to this ticket."),
        ):
            self.repository.link_related_article.side_effect = internal()
            with self.assertRaises(public) as caught:
                self.service.link_related_article(1, 2)
            self.assertEqual(str(caught.exception), message)

    def test_persistence_errors_are_safe_for_all_operations(self):
        for name, args in (("link_related_article", (1, 2)), ("list_linked_articles", (1,)), ("list_link_candidates", (1,))):
            for error in (sqlite3.IntegrityError, sqlite3.OperationalError, OSError, RuntimeError):
                getattr(self.repository, name).side_effect = error("Sensitive database detail")
                with self.assertRaises(TicketKnowledgePersistenceError) as caught:
                    getattr(self.service, name)(*args)
                self.assertNotIn("Sensitive", str(caught.exception))

    def test_lists_delegate_and_translate_missing_ticket(self):
        for name in ("list_linked_articles", "list_link_candidates"):
            self.assertIs(getattr(self.service, name)(1), getattr(self.repository, name).return_value)
            getattr(self.repository, name).side_effect = LinkTicketMissingError()
            with self.assertRaises(TicketKnowledgeTicketMissingError):
                getattr(self.service, name)(1)

    def test_relationship_type_is_not_user_input(self):
        with self.assertRaises(TypeError):
            self.service.link_related_article(1, 2, relationship_type="APPLIED")

    def test_unlink_delegates_exact_ids_and_returns_only_success(self):
        self.assertIsNone(self.service.unlink_related_article(1, 2))
        self.repository.unlink_related_article.assert_called_once_with(ticket_id=1, knowledge_article_id=2)

    def test_unlink_rejects_invalid_ticket_ids(self):
        for value in (True, False, 0, -1, 1.0, "1", None, 2**63):
            with self.subTest(value=value), self.assertRaises(TicketKnowledgeValidationError):
                self.service.unlink_related_article(value, 2)
        self.repository.unlink_related_article.assert_not_called()

    def test_unlink_rejects_invalid_article_ids(self):
        for value in (True, False, 0, -1, 1.0, "1", None, 2**63):
            with self.subTest(value=value), self.assertRaises(TicketKnowledgeValidationError):
                self.service.unlink_related_article(1, value)
        self.repository.unlink_related_article.assert_not_called()

    def test_unlink_accepts_maximum_sqlite_ids(self):
        self.service.unlink_related_article(2**63 - 1, 2**63 - 1)
        self.repository.unlink_related_article.assert_called_once_with(ticket_id=2**63 - 1, knowledge_article_id=2**63 - 1)

    def test_unlink_translates_missing_conditions(self):
        for internal, public, message in (
            (LinkTicketMissingError, TicketKnowledgeTicketMissingError, "This ticket no longer exists."),
            (LinkArticleMissingError, TicketKnowledgeArticleMissingError, "This article no longer exists."),
            (ArticleNotLinkedError, TicketKnowledgeNotLinkedError,
             "This article is no longer linked to this ticket. Refresh the linked articles."),
        ):
            self.repository.unlink_related_article.side_effect = internal()
            with self.subTest(public=public), self.assertRaises(public) as caught:
                self.service.unlink_related_article(1, 2)
            self.assertEqual(str(caught.exception), message)

    def test_unlink_persistence_errors_hide_internal_details(self):
        for error in (sqlite3.IntegrityError, sqlite3.OperationalError, OSError, RuntimeError):
            self.repository.unlink_related_article.side_effect = error("Sensitive SQL or path")
            with self.assertRaises(TicketKnowledgePersistenceError) as caught:
                self.service.unlink_related_article(1, 2)
            self.assertEqual(str(caught.exception), "Could not unlink the article. Your selection is preserved. Try again.")

    def test_unlink_relationship_type_cannot_be_supplied(self):
        for kind in ("RELATED", "APPLIED", "RESOLUTION_SOURCE"):
            with self.assertRaises(TypeError):
                self.service.unlink_related_article(1, 2, relationship_type=kind)
        self.repository.unlink_related_article.assert_not_called()
