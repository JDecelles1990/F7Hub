from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.knowledge_repository import KnowledgeRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = PROJECT_ROOT / "Database" / "Migrations"


class KnowledgeRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "knowledge.db"
        bootstrap_database(self.path, MIGRATIONS)
        self.repository = KnowledgeRepository(self.path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create(self, code="KB0001", updated="2026-09-06T14:00:00.000Z"):
        return self.repository.create_article(
            article_code=code,
            title=f"Article {code}",
            summary="Synthetic summary",
            body_markdown="# Synthetic body",
            created_at=updated,
            updated_at=updated,
        )

    def test_create_get_and_initial_version_are_atomic(self):
        article = self.create()
        self.assertGreater(article.knowledge_article_id, 0)
        self.assertEqual(self.repository.get_article(article.knowledge_article_id), article)
        self.assertEqual(article.status, "DRAFT")
        self.assertEqual(article.version_number, 1)
        self.assertIsNone(article.category_id)
        self.assertIsNone(article.published_at)
        with database_connection(self.path) as connection:
            version = connection.execute(
                "SELECT version_number, title, summary, body_markdown "
                "FROM knowledge_article_versions WHERE knowledge_article_id = ?",
                (article.knowledge_article_id,),
            ).fetchone()
        self.assertEqual(tuple(version), (1, article.title, article.summary, article.body_markdown))

    def test_list_is_updated_descending_then_id_descending_and_includes_all_statuses(self):
        first = self.create("KB0001", "2026-09-06T14:00:00.000Z")
        second = self.create("KB0002", "2026-09-06T15:00:00.000Z")
        third = self.create("KB0003", "2026-09-06T15:00:00.000Z")
        with database_connection(self.path) as connection:
            connection.execute(
                "UPDATE knowledge_articles SET status = 'PUBLISHED', published_at = ? WHERE knowledge_article_id = ?",
                ("2026-09-06T15:00:00.000Z", second.knowledge_article_id),
            )
        self.assertEqual(
            tuple(article.article_code for article in self.repository.list_articles()),
            (third.article_code, second.article_code, first.article_code),
        )

    def test_duplicate_code_is_case_insensitive_and_leaves_one_complete_article(self):
        self.create("KB0001")
        with self.assertRaises(sqlite3.IntegrityError):
            self.create("kb0001")
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_articles").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_article_versions").fetchone()[0], 1)

    def test_initial_version_failure_rolls_back_article(self):
        with database_connection(self.path) as connection:
            connection.execute(
                "CREATE TRIGGER reject_version BEFORE INSERT ON knowledge_article_versions "
                "BEGIN SELECT RAISE(ABORT, 'synthetic version failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.create()
        self.assertEqual(self.repository.list_articles(), ())

    def test_reload_failure_rolls_back_article_and_version(self):
        with patch("f7hub.repositories.knowledge_repository._get_article", return_value=None):
            with self.assertRaises(RuntimeError):
                self.create()
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_articles").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_article_versions").fetchone()[0], 0)

    def test_integrity_foreign_keys_and_five_migrations(self):
        self.create()
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)


if __name__ == "__main__":
    unittest.main()
