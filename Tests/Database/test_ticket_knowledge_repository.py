from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.repositories.ticket_knowledge_repository import (
    TicketKnowledgeRepository, LinkTicketMissingError, LinkArticleMissingError,
    ArticleAlreadyLinkedError,
)
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_service import TicketService


class TicketKnowledgeRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "links.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.tickets = TicketService(TicketRepository(self.path))
        self.knowledge = KnowledgeService(KnowledgeRepository(self.path))
        self.ticket = self.tickets.create_ticket(subject="Synthetic ticket")
        self.article = self.create_article("KB0001")
        self.repository = TicketKnowledgeRepository(self.path)

    def create_article(self, code):
        return self.knowledge.create_article(article_code=code, title="Article " + code, summary=None, body="# Synthetic")

    def link(self, ticket_id=None, article_id=None):
        return self.repository.link_related_article(
            ticket_id=self.ticket.ticket_id if ticket_id is None else ticket_id,
            knowledge_article_id=self.article.knowledge_article_id if article_id is None else article_id,
            linked_by=None, linked_at="2026-09-06T18:00:00.000Z",
        )

    def count(self):
        with database_connection(self.path) as connection:
            return connection.execute("SELECT count(*) FROM ticket_knowledge_articles").fetchone()[0]

    def test_link_reload_and_immutable_lightweight_identity(self):
        link = self.link()
        self.assertEqual(link.relationship_type, "RELATED")
        self.assertEqual(link.linked_at, "2026-09-06T18:00:00.000Z")
        self.assertIsNone(link.linked_by)
        self.assertEqual((link.article_code, link.article_title, link.article_status, link.article_version_number),
                         ("KB0001", "Article KB0001", "DRAFT", 1))
        self.assertFalse(hasattr(link, "body_markdown"))
        with self.assertRaises(FrozenInstanceError):
            link.article_title = "Other"
        self.assertEqual(TicketKnowledgeRepository(self.path).list_linked_articles(self.ticket.ticket_id), (link,))

    def test_order_and_ticket_isolation(self):
        second = self.create_article("KB0002")
        self.link(article_id=second.knowledge_article_id)
        self.link()
        other = self.tickets.create_ticket(subject="Other")
        self.assertEqual(self.repository.list_linked_articles(other.ticket_id), ())
        self.assertEqual([x.article_code for x in self.repository.list_linked_articles(self.ticket.ticket_id)], ["KB0001", "KB0002"])

    def test_missing_ticket(self):
        with self.assertRaises(LinkTicketMissingError):
            self.link(ticket_id=999)
        self.assertEqual(self.count(), 0)

    def test_missing_article(self):
        with self.assertRaises(LinkArticleMissingError):
            self.link(article_id=999)
        self.assertEqual(self.count(), 0)

    def test_duplicate_rejected_without_mutating_first_link(self):
        link = self.link()
        with self.assertRaises(ArticleAlreadyLinkedError):
            self.link()
        self.assertEqual(self.repository.list_linked_articles(self.ticket.ticket_id), (link,))

    def test_concurrent_duplicate_has_one_winner(self):
        def attempt():
            try:
                self.link()
                return "linked"
            except ArticleAlreadyLinkedError:
                return "duplicate"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertCountEqual(results, ["linked", "duplicate"])
        self.assertEqual(self.count(), 1)

    def test_insert_failure_rolls_back_and_retry_succeeds(self):
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_link BEFORE INSERT ON ticket_knowledge_articles BEGIN SELECT RAISE(ABORT, 'synthetic'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.link()
        self.assertEqual(self.count(), 0)
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_link")
        self.link()
        self.assertEqual(self.count(), 1)

    def test_reload_failure_rolls_back_and_retry_succeeds(self):
        with patch("f7hub.repositories.ticket_knowledge_repository._get_link", return_value=None):
            with self.assertRaises(RuntimeError):
                self.link()
        self.assertEqual(self.count(), 0)
        self.link()
        self.assertEqual(self.count(), 1)

    def test_ticket_delete_cascades(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM tickets WHERE ticket_id = ?", (self.ticket.ticket_id,))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.count(), 0)

    def test_article_delete_cascades(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (self.article.knowledge_article_id,))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.count(), 0)

    def test_join_reflects_current_title_status_and_version(self):
        self.link()
        self.knowledge.update_article(article_id=self.article.knowledge_article_id, expected_version_number=1,
                                      title="Revised", summary=None, body="Revised body")
        for status in ("PUBLISHED", "ARCHIVED"):
            with database_connection(self.path) as connection:
                connection.execute("UPDATE knowledge_articles SET status = ? WHERE knowledge_article_id = ?", (status, self.article.knowledge_article_id))
            link = self.repository.list_linked_articles(self.ticket.ticket_id)[0]
            self.assertEqual((link.article_title, link.article_status, link.article_version_number), ("Revised", status, 2))

    def test_candidates_all_statuses_lightweight_sorted_exclude_related(self):
        for code, status in (("KB0003", "ARCHIVED"), ("KB0002", "PUBLISHED")):
            article = self.create_article(code)
            with database_connection(self.path) as connection:
                connection.execute("UPDATE knowledge_articles SET status = ? WHERE knowledge_article_id = ?", (status, article.knowledge_article_id))
        candidates = self.repository.list_link_candidates(self.ticket.ticket_id)
        self.assertEqual([x.article_status for x in candidates], ["DRAFT", "PUBLISHED", "ARCHIVED"])
        self.assertTrue(all(not hasattr(x, "body_markdown") for x in candidates))
        for candidate in candidates:
            self.link(article_id=candidate.knowledge_article_id)
        self.assertEqual(self.repository.list_link_candidates(self.ticket.ticket_id), ())

    def test_reads_distinguish_missing_ticket(self):
        for operation in (self.repository.list_linked_articles, self.repository.list_link_candidates):
            with self.assertRaises(LinkTicketMissingError):
                operation(999)

    def test_only_relationship_changes_and_database_integrity(self):
        before = self.tickets.get_ticket_details(self.ticket.ticket_id)
        self.link()
        self.assertEqual(self.tickets.get_ticket_details(self.ticket.ticket_id), before)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)
            row = connection.execute("SELECT ticket_id, knowledge_article_id, relationship_type, linked_at FROM ticket_knowledge_articles").fetchone()
            self.assertEqual(tuple(row), (self.ticket.ticket_id, self.article.knowledge_article_id, "RELATED", "2026-09-06T18:00:00.000Z"))
