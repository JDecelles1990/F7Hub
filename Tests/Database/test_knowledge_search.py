from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.services.knowledge_service import (
    KnowledgeSearchError,
    KnowledgeService,
    KnowledgeValidationError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = PROJECT_ROOT / "Database" / "Migrations"


class KnowledgeSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "knowledge-search.db"
        bootstrap_database(self.database_path, MIGRATIONS)
        self.repository = KnowledgeRepository(self.database_path)
        self.service = KnowledgeService(self.repository)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def create(
        self,
        code: str,
        *,
        title: str,
        summary: str | None = None,
        body: str = "Body",
        updated_at: str = "2026-09-09T12:00:00.000Z",
    ):
        return self.repository.create_article(
            article_code=code,
            title=title,
            summary=summary,
            body_markdown=body,
            created_at=updated_at,
            updated_at=updated_at,
        )

    def test_title_summary_body_code_and_multiple_terms_search(self) -> None:
        title = self.create("KB-TITLE", title="Outlook cannot send mail")
        summary = self.create(
            "KB-SUMMARY", title="Summary article", summary="SMTP relay diagnostics",
        )
        body = self.create(
            "KB-BODY", title="Body article", body="Run SMTPAUTHCHECK before retrying.",
        )

        self.assertEqual(self.service.search_articles("Outlook send")[0].knowledge_article_id, title.knowledge_article_id)
        self.assertEqual(self.service.search_articles("relay")[0].knowledge_article_id, summary.knowledge_article_id)
        self.assertEqual(self.service.search_articles("SMTPAUTHCHECK")[0].knowledge_article_id, body.knowledge_article_id)
        self.assertEqual(self.service.search_articles("kb body")[0].knowledge_article_id, body.knowledge_article_id)

    def test_unicode_case_and_plain_punctuation_are_safe_literal_queries(self) -> None:
        article = self.create(
            "KB-001",
            title="Montréal C++ Outlook notes",
            body="Outlook won't send. AND OR NOT appear as ordinary words.",
        )
        queries = (
            "monTREAL",
            "KB-001",
            "C++",
            '"outlook won\'t send"',
            "(AND) OR NOT*",
        )
        with patch.object(self.repository, "search_articles", wraps=self.repository.search_articles) as search:
            for query in queries:
                with self.subTest(query=query):
                    results = self.service.search_articles(query)
                    self.assertEqual([result.knowledge_article_id for result in results], [article.knowledge_article_id])
            expressions = [call.args[0] for call in search.call_args_list]
        self.assertEqual(
            expressions,
            [
                '"monTREAL"',
                '"KB" "001"',
                '"C"',
                '"outlook" "won" "t" "send"',
                '"AND" "OR" "NOT"',
            ],
        )

    def test_empty_or_punctuation_only_query_does_not_execute_match(self) -> None:
        with patch.object(self.repository, "search_articles") as search:
            for query in ("", "  \r\n\t ", "*** ( ) +++"):
                with self.subTest(query=query):
                    self.assertEqual(self.service.search_articles(query), ())
            search.assert_not_called()
        with self.assertRaises(KnowledgeValidationError):
            self.service.search_articles(7)

    def test_all_current_statuses_return_authoritative_lightweight_records(self) -> None:
        articles = [
            self.create(f"KB-STATUS-{index}", title=f"Status target {status}")
            for index, status in enumerate(("DRAFT", "PUBLISHED", "ARCHIVED"), 1)
        ]
        with database_connection(self.database_path) as connection:
            for article, status in zip(articles, ("DRAFT", "PUBLISHED", "ARCHIVED")):
                connection.execute(
                    "UPDATE knowledge_articles SET status = ?, published_at = ? "
                    "WHERE knowledge_article_id = ?",
                    (
                        status,
                        None if status == "DRAFT" else "2026-09-09T12:00:00.000Z",
                        article.knowledge_article_id,
                    ),
                )

        results = self.service.search_articles("Status target")
        self.assertEqual({result.status for result in results}, {"DRAFT", "PUBLISHED", "ARCHIVED"})
        self.assertEqual({result.knowledge_article_id for result in results}, {a.knowledge_article_id for a in articles})
        for result in results:
            self.assertFalse(hasattr(result, "body_markdown"))
            self.assertFalse(hasattr(result, "summary"))

    def test_current_content_excludes_historical_only_terms(self) -> None:
        first = self.create(
            "KB-HISTORY",
            title="History separation",
            body="LEGACYONLYTERM",
        )
        current = self.repository.update_draft_article(
            article_id=first.knowledge_article_id,
            expected_version_number=1,
            title=first.title,
            summary=first.summary,
            body_markdown="CURRENTONLYTERM",
            updated_at="2026-09-09T13:00:00.000Z",
        )

        self.assertEqual(self.service.search_articles("LEGACYONLYTERM"), ())
        self.assertEqual(
            [result.knowledge_article_id for result in self.service.search_articles("CURRENTONLYTERM")],
            [first.knowledge_article_id],
        )
        self.assertEqual(
            self.repository.get_article_version(first.knowledge_article_id, 1).body_markdown,
            "LEGACYONLYTERM",
        )
        self.assertEqual(current.version_number, 2)

    def test_order_is_deterministic_and_query_plan_uses_fts_match(self) -> None:
        first = self.create("KB-ORDER-1", title="Shared ranking token", body="Same body")
        second = self.create("KB-ORDER-2", title="Shared ranking token", body="Same body")
        results = self.service.search_articles("Shared ranking token")
        self.assertEqual(
            [result.knowledge_article_id for result in results],
            [second.knowledge_article_id, first.knowledge_article_id],
        )

        with database_connection(self.database_path) as connection:
            plan = connection.execute(
                """
                EXPLAIN QUERY PLAN
                SELECT ka.knowledge_article_id
                FROM knowledge_articles_fts
                JOIN knowledge_articles AS ka
                    ON ka.knowledge_article_id = knowledge_articles_fts.rowid
                WHERE knowledge_articles_fts MATCH ?
                ORDER BY bm25(knowledge_articles_fts), ka.updated_at DESC,
                         ka.knowledge_article_id DESC
                """,
                ('"Shared" "ranking" "token"',),
            ).fetchall()
        detail = " ".join(str(value) for row in plan for value in row)
        self.assertIn("VIRTUAL TABLE INDEX", detail.upper())
        self.assertNotIn("LIKE", detail.upper())

    def test_search_persistence_failure_is_translated_without_private_detail(self) -> None:
        with patch.object(
            self.repository,
            "search_articles",
            side_effect=sqlite3.OperationalError("private FTS detail"),
        ):
            with self.assertRaises(KnowledgeSearchError) as caught:
                self.service.search_articles("Outlook")
        self.assertIn("Could not search", str(caught.exception))
        self.assertNotIn("private", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
