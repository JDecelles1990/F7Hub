from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.knowledge_repository import (
    KnowledgeRepository, ArticleMissingError, ArticleNotEditableError,
    ArticleUnchangedError, ArticleVersionMissingError, StaleArticleVersionError,
)


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

    def update(self, article, **overrides):
        values = dict(
            article_id=article.knowledge_article_id,
            expected_version_number=article.version_number,
            title="Revised title", summary="Revised summary",
            body_markdown="  # Revised body\n\tStep\n", updated_at="2026-09-06T16:00:00.000Z",
        )
        return self.repository.update_draft_article(**(values | overrides))

    def history(self):
        with database_connection(self.path) as connection:
            return [tuple(row) for row in connection.execute(
                "SELECT * FROM knowledge_article_versions ORDER BY version_number"
            )]

    def test_revisions_preserve_full_history_and_stable_metadata(self):
        first = self.create()
        initial_history = self.history()
        second = self.update(first)
        self.assertEqual(second.version_number, 2)
        for field in ("article_code", "created_at", "created_by", "updated_by", "category_id", "status", "published_at"):
            self.assertEqual(getattr(second, field), getattr(first, field))
        second_history = self.history()
        self.assertEqual(second_history[:1], initial_history)
        self.assertEqual(second_history[1][2:6], (2, second.title, second.summary, second.body_markdown))
        self.assertEqual(second_history[1][-1], second.updated_at)
        third = self.update(second, title="Third title", summary=None, body_markdown="Third body")
        self.assertEqual(self.repository.get_article(first.knowledge_article_id), third)
        self.assertEqual(self.repository.list_articles(), (third,))
        self.assertEqual(self.history()[:2], second_history)
        self.assertEqual([row[2] for row in self.history()], [1, 2, 3])
        self.assertEqual(self.history()[2][2:6], (3, "Third title", None, "Third body"))
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)

    def test_stale_editor_cannot_overwrite_or_create_snapshot_even_if_content_matches(self):
        first = self.create()
        second = self.update(first)
        history = self.history()
        for title in ("Stale editor content", second.title):
            with self.subTest(title=title), self.assertRaises(StaleArticleVersionError):
                self.update(first, title=title)
            self.assertEqual(self.repository.get_article(first.knowledge_article_id), second)
            self.assertEqual(self.history(), history)

    def test_external_status_changes_prevent_edit(self):
        first = self.create()
        history = self.history()
        for status in ("PUBLISHED", "ARCHIVED"):
            with database_connection(self.path) as connection:
                connection.execute("UPDATE knowledge_articles SET status = ?", (status,))
            before = self.repository.get_article(first.knowledge_article_id)
            with self.subTest(status=status), self.assertRaises(ArticleNotEditableError):
                self.update(first)
            self.assertEqual(self.repository.get_article(first.knowledge_article_id), before)
            self.assertEqual(self.history(), history)

    def test_deleted_article_does_not_gain_orphan_version(self):
        first = self.create()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (first.knowledge_article_id,))
        with self.assertRaises(ArticleMissingError):
            self.update(first)
        self.assertEqual(self.history(), [])
        self.assertEqual(self.repository.list_articles(), ())

    def test_snapshot_failure_rolls_back_update_and_retry_creates_exactly_v2(self):
        first = self.create()
        history = self.history()
        with database_connection(self.path) as connection:
            connection.execute(
                "CREATE TRIGGER reject_revision BEFORE INSERT ON knowledge_article_versions "
                "BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.update(first)
        self.assertEqual(self.repository.get_article(first.knowledge_article_id), first)
        self.assertEqual(self.history(), history)
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_revision")
        self.assertEqual(self.update(first).version_number, 2)
        self.assertEqual([row[2] for row in self.history()], [1, 2])

    def test_final_reload_failure_rolls_back_update_and_snapshot_then_retry_succeeds(self):
        first = self.create()
        history = self.history()
        for failed_reload in (None, sqlite3.OperationalError("synthetic failure")):
            with patch("f7hub.repositories.knowledge_repository._get_article", side_effect=[first, failed_reload]):
                with self.assertRaises((RuntimeError, sqlite3.Error)):
                    self.update(first)
            self.assertEqual(self.repository.get_article(first.knowledge_article_id), first)
            self.assertEqual(self.history(), history)
        self.assertEqual(self.update(first).version_number, 2)
        self.assertEqual([row[2] for row in self.history()], [1, 2])

    def test_unchanged_current_content_does_not_create_revision_or_touch_timestamp(self):
        first = self.create()
        history = self.history()
        with self.assertRaises(ArticleUnchangedError):
            self.update(first, title=first.title, summary=first.summary, body_markdown=first.body_markdown)
        self.assertEqual(self.repository.get_article(first.knowledge_article_id), first)
        self.assertEqual(self.history(), history)

    def test_conditional_update_rowcount_guard_prevents_snapshot(self):
        first = self.create()
        history = self.history()
        with database_connection(self.path) as connection:
            connection.execute(
                "CREATE TRIGGER ignore_revision BEFORE UPDATE ON knowledge_articles "
                "BEGIN SELECT RAISE(IGNORE); END"
            )
        with self.assertRaises(StaleArticleVersionError):
            self.update(first)
        self.assertEqual(self.repository.get_article(first.knowledge_article_id), first)
        self.assertEqual(self.history(), history)

    def test_history_list_is_lightweight_newest_first_and_detail_is_exact(self):
        first = self.create()
        second = self.update(
            first, title="Title B", summary="Summary B", body_markdown="Body B",
        )
        third = self.update(
            second, title="Title C", summary="Summary C", body_markdown="Body C",
        )
        before_article = self.repository.get_article(first.knowledge_article_id)
        before_history = self.history()
        versions = self.repository.list_article_versions(first.knowledge_article_id)
        self.assertEqual([version.version_number for version in versions], [3, 2, 1])
        self.assertFalse(hasattr(versions[0], "body_markdown"))
        self.assertEqual(
            (versions[1].title, versions[1].change_summary, versions[1].created_by),
            ("Title B", None, None),
        )
        expected = (
            (1, first.title, first.summary, first.body_markdown),
            (2, "Title B", "Summary B", "Body B"),
            (3, "Title C", "Summary C", "Body C"),
        )
        for number, title, summary, body in expected:
            version = self.repository.get_article_version(first.knowledge_article_id, number)
            self.assertEqual(
                (version.version_number, version.title, version.summary, version.body_markdown),
                (number, title, summary, body),
            )
        self.assertEqual(self.repository.get_article(first.knowledge_article_id), before_article)
        self.assertEqual(self.history(), before_history)
        self.assertEqual(third, before_article)

    def test_history_reads_execute_no_writes_and_use_existing_index(self):
        article = self.create()
        statements = []
        original = database_connection

        from contextlib import contextmanager

        @contextmanager
        def traced_connection(path):
            with original(path) as connection:
                connection.set_trace_callback(statements.append)
                yield connection

        with patch(
            "f7hub.repositories.knowledge_repository.database_connection",
            traced_connection,
        ):
            self.repository.list_article_versions(article.knowledge_article_id)
            list_statements = tuple(statements)
            statements.clear()
            self.repository.get_article_version(article.knowledge_article_id, 1)
        for trace in (list_statements, statements):
            self.assertEqual(
                [statement.split()[0].upper() for statement in trace],
                ["BEGIN", "SELECT", "SELECT", "ROLLBACK"],
            )
        self.assertNotIn("body_markdown", " ".join(list_statements).lower())
        self.assertIn("body_markdown", " ".join(statements).lower())
        with database_connection(self.path) as connection:
            plan = connection.execute(
                "EXPLAIN QUERY PLAN SELECT knowledge_article_version_id, version_number "
                "FROM knowledge_article_versions WHERE knowledge_article_id = ? "
                "ORDER BY version_number DESC",
                (article.knowledge_article_id,),
            ).fetchall()
        self.assertIn("idx_knowledge_versions_article_version", " ".join(str(value) for row in plan for value in row))

    def test_history_distinguishes_missing_article_revision_and_empty_history(self):
        with self.assertRaises(ArticleMissingError):
            self.repository.list_article_versions(999)
        article = self.create()
        with self.assertRaises(ArticleVersionMissingError):
            self.repository.get_article_version(article.knowledge_article_id, 999)
        with database_connection(self.path) as connection:
            connection.execute(
                "DELETE FROM knowledge_article_versions WHERE knowledge_article_id = ?",
                (article.knowledge_article_id,),
            )
        self.assertEqual(self.repository.list_article_versions(article.knowledge_article_id), ())

    def test_history_detail_is_scoped_to_article_and_detects_cascaded_deletion(self):
        first = self.create()
        second = self.create("KB0002")
        self.update(second, title="Only second article has V2")
        with self.assertRaises(ArticleVersionMissingError):
            self.repository.get_article_version(first.knowledge_article_id, 2)
        with database_connection(self.path) as connection:
            connection.execute(
                "DELETE FROM knowledge_articles WHERE knowledge_article_id = ?",
                (first.knowledge_article_id,),
            )
        for operation in (
            lambda: self.repository.list_article_versions(first.knowledge_article_id),
            lambda: self.repository.get_article_version(first.knowledge_article_id, 1),
        ):
            with self.assertRaises(ArticleMissingError):
                operation()

    def test_history_reads_are_available_for_every_article_status(self):
        article = self.create()
        for status in ("DRAFT", "PUBLISHED", "ARCHIVED"):
            with database_connection(self.path) as connection:
                connection.execute(
                    "UPDATE knowledge_articles SET status = ?, published_at = ? "
                    "WHERE knowledge_article_id = ?",
                    (
                        status,
                        None if status == "DRAFT" else "2026-09-07T12:00:00.000Z",
                        article.knowledge_article_id,
                    ),
                )
            with self.subTest(status=status):
                self.assertEqual(
                    self.repository.list_article_versions(article.knowledge_article_id)[0].version_number,
                    1,
                )


if __name__ == "__main__":
    unittest.main()
