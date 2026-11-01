"""Focused synthetic checks for non-creating taxonomy reference reads."""

from dataclasses import fields
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.category_repository import CategoryRecord, CategoryRepository
from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRepository
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.tag_repository import TagRecord, TagRepository
from f7hub.services.knowledge_service import (
    KnowledgeCategoryError, KnowledgeService, KnowledgeTagError, KnowledgeValidationError,
)
from f7hub.services.ticket_reference_service import TicketReferenceError, TicketReferenceService


class TaxonomyReferenceReadSafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "taxonomy.db"
        self.categories = CategoryRepository(self.path)
        self.tags = TagRepository(self.path)
        self.knowledge = KnowledgeService(
            KnowledgeRepository(self.path), self.categories, self.tags,
        )
        self.ticket = TicketReferenceService(
            CompanyRepository(self.path), ContactRepository(self.path), self.categories,
        )

    def bootstrap(self):
        migrations = Path(__file__).resolve().parents[2] / "Database" / "Migrations"
        bootstrap_database(self.path, migrations)

    def repository_calls(self):
        return (
            lambda: self.categories.list_categories(scope="TICKET", active_only=True),
            self.tags.list_tags,
            lambda: self.tags.list_article_tags(1),
        )

    def consumer_calls(self):
        return (
            (self.ticket.list_active_ticket_categories, TicketReferenceError),
            (self.knowledge.list_active_knowledge_categories, KnowledgeCategoryError),
            (self.knowledge.list_available_tags, KnowledgeTagError),
            (lambda: self.knowledge.list_article_tags(1), KnowledgeTagError),
        )

    def assert_no_storage(self, path):
        self.assertFalse(path.exists())
        for suffix in ("-wal", "-shm", "-journal"):
            self.assertFalse(Path(str(path) + suffix).exists())

    def test_existing_empty_and_populated_database_contracts(self):
        self.bootstrap()
        for read in self.repository_calls():
            self.assertEqual(read(), ())
        for read, _error in self.consumer_calls():
            self.assertEqual(read(), ())

        with database_connection(self.path) as connection:
            connection.executemany(
                "INSERT INTO categories "
                "(category_id, scope, name, slug, is_active, sort_order, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, '2026-01-01', '2026-01-01')",
                (
                    (3, "TICKET", "Zulu", "ticket-zulu", 1, 20),
                    (4, "TICKET", "Alpha", "ticket-alpha", 1, 10),
                    (5, "TICKET", "Inactive", "ticket-inactive", 0, 0),
                    (6, "KNOWLEDGE", "Knowledge", "knowledge", 1, 0),
                    (7, "GENERAL", "General", "general", 1, 0),
                ),
            )
            connection.executemany(
                "INSERT INTO tags (tag_id, name, slug, created_at) VALUES (?, ?, ?, '2026-01-01')",
                ((11, "Zulu", "tag-zulu"), (12, "Alpha", "tag-alpha")),
            )
        article = KnowledgeRepository(self.path).create_article(
            article_code="TAX-02-SYNTHETIC", title="Synthetic", summary=None,
            body_markdown="Body", created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        with database_connection(self.path) as connection:
            connection.execute(
                "INSERT INTO knowledge_article_tags "
                "(knowledge_article_id, tag_id, created_at) VALUES (?, ?, '2026-01-01')",
                (article.knowledge_article_id, 11),
            )
        self.assertEqual(
            tuple(field.name for field in fields(CategoryRecord)),
            ("category_id", "scope", "name", "is_active", "sort_order"),
        )
        self.assertEqual(tuple(field.name for field in fields(TagRecord)), ("tag_id", "name"))
        self.assertEqual(
            [row.category_id for row in self.categories.list_categories(scope="TICKET")],
            [5, 4, 3],
        )
        self.assertEqual(
            [row.category_id for row in self.categories.list_categories(
                scope="TICKET", active_only=True,
            )],
            [4, 3],
        )
        self.assertEqual(
            [row.category_id for row in self.categories.list_categories(
                scope="KNOWLEDGE", active_only=True,
            )],
            [6],
        )
        self.assertEqual(
            [(row.tag_id, row.name) for row in self.tags.list_tags()],
            [(12, "Alpha"), (11, "Zulu")],
        )
        self.assertEqual(
            [(row.tag_id, row.name) for row in self.tags.list_article_tags(article.knowledge_article_id)],
            [(11, "Zulu")],
        )
        self.assertEqual(self.tags.list_article_tags(article.knowledge_article_id + 100), ())
        self.assertEqual(
            [(row.reference_id, row.label) for row in self.ticket.list_active_ticket_categories()],
            [(4, "Alpha"), (3, "Zulu")],
        )
        self.assertEqual(
            [(row.category_id, row.name) for row in self.knowledge.list_active_knowledge_categories()],
            [(6, "Knowledge")],
        )
        with self.assertRaises(KnowledgeValidationError):
            self.knowledge.list_article_tags(0)
        with database_connection(self.path, read_only=True) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_missing_primary_and_missing_parent_never_create_storage(self):
        for path in (self.root / "missing.db", self.root / "a" / "b" / "missing.db"):
            with self.subTest(path=path):
                self.path = path
                self.categories = CategoryRepository(path)
                self.tags = TagRepository(path)
                self.knowledge = KnowledgeService(KnowledgeRepository(path), self.categories, self.tags)
                self.ticket = TicketReferenceService(
                    CompanyRepository(path), ContactRepository(path), self.categories,
                )
                for read in self.repository_calls():
                    with self.assertRaises((sqlite3.Error, OSError, RuntimeError)):
                        read()
                    self.assert_no_storage(path)
                for read, error_type in self.consumer_calls():
                    with self.assertRaises(error_type) as caught:
                        read()
                    self.assertIsNotNone(caught.exception.__cause__)
                    self.assert_no_storage(path)
                self.assertFalse((self.root / "a").exists())

    def test_malformed_bytes_zero_byte_and_missing_schema_fail_without_repair(self):
        for contents in (b"not a sqlite database", b""):
            with self.subTest(contents=contents):
                self.path.write_bytes(contents)
                for read in self.repository_calls():
                    with self.assertRaises(sqlite3.Error):
                        read()
                for read, error_type in self.consumer_calls():
                    with self.assertRaises(error_type):
                        read()
                self.assertEqual(self.path.read_bytes(), contents)
                self.path.unlink()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TABLE unrelated (value TEXT)")
        before = self.path.read_bytes()
        for read in self.repository_calls():
            with self.assertRaises(sqlite3.Error):
                read()
        for read, error_type in self.consumer_calls():
            with self.assertRaises(error_type):
                read()
        self.assertEqual(self.path.read_bytes(), before)

    def test_three_repository_calls_bind_read_only_flag(self):
        for module in (
            "f7hub.repositories.category_repository",
            "f7hub.repositories.tag_repository",
        ):
            with patch(module + ".database_connection", wraps=database_connection) as connection:
                calls = self.repository_calls()[:1] if "category" in module else self.repository_calls()[1:]
                for read in calls:
                    with self.assertRaises(sqlite3.Error):
                        read()
                self.assertEqual(connection.call_count, len(calls))
                self.assertTrue(all(call.kwargs == {"read_only": True} for call in connection.call_args_list))


if __name__ == "__main__":
    unittest.main()