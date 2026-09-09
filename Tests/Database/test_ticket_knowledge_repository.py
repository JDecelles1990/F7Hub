from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import FrozenInstanceError
from pathlib import Path
import sqlite3
import tempfile
from threading import Barrier
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.repositories.ticket_knowledge_repository import (
    TicketKnowledgeRepository, LinkTicketMissingError, LinkArticleMissingError,
    ArticleAlreadyLinkedError, ArticleNotLinkedError,
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

    def unlink(self):
        return self.repository.unlink_related_article(
            ticket_id=self.ticket.ticket_id, knowledge_article_id=self.article.knowledge_article_id,
        )

    def database_rows(self):
        with database_connection(self.path) as connection:
            tables = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' "
                    "AND name NOT LIKE 'knowledge_articles_fts%'"
                )
            ]
            return {table: tuple(tuple(row) for row in connection.execute(f'SELECT * FROM "{table}" ORDER BY rowid'))
                    for table in tables}

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
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)
            row = connection.execute("SELECT ticket_id, knowledge_article_id, relationship_type, linked_at FROM ticket_knowledge_articles").fetchone()
            self.assertEqual(tuple(row), (self.ticket.ticket_id, self.article.knowledge_article_id, "RELATED", "2026-09-06T18:00:00.000Z"))

    def test_unlink_removes_only_exact_related_row_and_preserves_all_other_data(self):
        self.link()
        second = self.create_article("KB0002")
        self.link(article_id=second.knowledge_article_id)
        other_ticket = self.tickets.create_ticket(subject="Another synthetic ticket")
        self.link(ticket_id=other_ticket.ticket_id)
        with database_connection(self.path) as connection:
            for relationship_type in ("APPLIED", "RESOLUTION_SOURCE"):
                connection.execute(
                    "INSERT INTO ticket_knowledge_articles VALUES (?, ?, ?, ?, ?)",
                    (self.ticket.ticket_id, self.article.knowledge_article_id, relationship_type, None, "2026-09-07T00:00:00Z"),
                )
        before = self.database_rows()
        self.assertIsNone(self.unlink())
        after = self.database_rows()
        expected_links = tuple(row for row in before["ticket_knowledge_articles"]
                               if row[:3] != (self.ticket.ticket_id, self.article.knowledge_article_id, "RELATED"))
        before["ticket_knowledge_articles"] = expected_links
        self.assertEqual(after, before)
        self.assertEqual(self.count(), 4)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)

    def test_unlink_ticket_deleted_distinguishes_missing_ticket(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM tickets WHERE ticket_id = ?", (self.ticket.ticket_id,))
        before = self.database_rows()
        with self.assertRaises(LinkTicketMissingError):
            self.unlink()
        self.assertEqual(self.database_rows(), before)
        self.assertIsNotNone(self.knowledge.get_article(self.article.knowledge_article_id))

    def test_unlink_article_deleted_distinguishes_missing_article(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (self.article.knowledge_article_id,))
        before = self.database_rows()
        with self.assertRaises(LinkArticleMissingError):
            self.unlink()
        self.assertEqual(self.database_rows(), before)
        self.assertIsNotNone(self.tickets.get_ticket_details(self.ticket.ticket_id))

    def test_unlink_missing_related_does_not_remove_other_type(self):
        with database_connection(self.path) as connection:
            connection.execute("INSERT INTO ticket_knowledge_articles VALUES (?, ?, 'APPLIED', NULL, ?)",
                               (self.ticket.ticket_id, self.article.knowledge_article_id, "2026-09-07T00:00:00Z"))
        before = self.database_rows()
        with self.assertRaises(ArticleNotLinkedError):
            self.unlink()
        self.assertEqual(self.database_rows(), before)

    def test_unlink_zero_rowcount_is_not_reported_as_success(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER ignore_unlink BEFORE DELETE ON ticket_knowledge_articles BEGIN SELECT RAISE(IGNORE); END")
        before = self.database_rows()
        with self.assertRaises(ArticleNotLinkedError):
            self.unlink()
        self.assertEqual(self.database_rows(), before)

    def test_unlink_excessive_rowcount_rolls_back(self):
        self.link()
        before = self.database_rows()

        @contextmanager
        def unexpected_rowcount(path):
            with database_connection(path) as connection:
                proxy = Mock(wraps=connection)
                def execute(sql, parameters=()):
                    cursor = connection.execute(sql, parameters)
                    return SimpleNamespace(rowcount=2) if sql.startswith("DELETE") else cursor
                proxy.execute.side_effect = execute
                yield proxy

        with patch("f7hub.repositories.ticket_knowledge_repository.database_connection", unexpected_rowcount):
            with self.assertRaises(RuntimeError):
                self.unlink()
        self.assertEqual(self.database_rows(), before)

    def test_unlink_failure_after_delete_rolls_back_and_retry_succeeds(self):
        self.link()
        before = self.database_rows()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_unlink AFTER DELETE ON ticket_knowledge_articles BEGIN SELECT RAISE(FAIL, 'synthetic'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.unlink()
        self.assertEqual(self.database_rows(), before)
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_unlink")
        self.unlink()
        self.assertEqual(self.count(), 0)

    def test_unlink_commit_failure_rolls_back(self):
        self.link()
        before = self.database_rows()

        @contextmanager
        def failed_commit(path):
            with database_connection(path) as connection:
                proxy = Mock(wraps=connection)
                proxy.commit.side_effect = sqlite3.OperationalError("synthetic commit failure")
                yield proxy

        with patch("f7hub.repositories.ticket_knowledge_repository.database_connection", failed_commit):
            with self.assertRaises(sqlite3.OperationalError):
                self.unlink()
        self.assertEqual(self.database_rows(), before)

    def test_concurrent_unlink_has_one_winner_and_one_not_linked(self):
        self.link()
        gate = Barrier(2)
        def attempt(_):
            repository = TicketKnowledgeRepository(self.path)
            gate.wait(timeout=5)
            try:
                repository.unlink_related_article(ticket_id=self.ticket.ticket_id,
                                                  knowledge_article_id=self.article.knowledge_article_id)
                return "unlinked"
            except ArticleNotLinkedError:
                return "not linked"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, range(2)))
        self.assertCountEqual(results, ["unlinked", "not linked"])
        self.assertEqual(self.count(), 0)
        self.assertIsNotNone(self.knowledge.get_article(self.article.knowledge_article_id))
        self.assertIsNotNone(self.tickets.get_ticket_details(self.ticket.ticket_id))

    def test_unlink_reappears_in_candidates_and_can_be_relinked(self):
        self.link()
        self.assertEqual(self.repository.list_link_candidates(self.ticket.ticket_id), ())
        self.unlink()
        candidates = self.repository.list_link_candidates(self.ticket.ticket_id)
        self.assertEqual([item.knowledge_article_id for item in candidates], [self.article.knowledge_article_id])
        self.link()
        self.assertEqual(self.count(), 1)

    def test_unlink_transaction_reserves_writer_before_checks_and_commits_once(self):
        self.link()
        statements = []
        connections = []

        @contextmanager
        def traced(path):
            with database_connection(path) as connection:
                connections.append(connection)
                connection.set_trace_callback(lambda sql: statements.append(" ".join(sql.split())))
                yield connection

        with patch("f7hub.repositories.ticket_knowledge_repository.database_connection", traced):
            self.unlink()
        self.assertEqual(len(connections), 1)
        self.assertEqual(statements[0], "BEGIN IMMEDIATE")
        self.assertTrue(statements[1].startswith("SELECT 1 FROM tickets"))
        self.assertTrue(statements[2].startswith("SELECT 1 FROM knowledge_articles"))
        self.assertIn("JOIN knowledge_articles", statements[3])
        self.assertTrue(statements[4].startswith("DELETE FROM ticket_knowledge_articles"))
        self.assertEqual(statements[5:], ["COMMIT"])
