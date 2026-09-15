"""Read-only lifecycle status predicates for current Knowledge articles."""

from contextlib import contextmanager
import sqlite3
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import database_connection
from f7hub.services.knowledge_service import (
    KnowledgeCreationError,
    KnowledgeSearchError,
    KnowledgeValidationError,
)
from Tests.Database.test_knowledge_categories import CategoryFixture


class KnowledgeStatusFilterTests(CategoryFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.rows = []
        fixtures = (
            ("A", 11, "DRAFT", "DNS DNS DNS", "2026-09-15T12:00:01Z"),
            ("B", 11, "PUBLISHED", "DNS DNS", "2026-09-15T12:00:02Z"),
            ("C", 22, "PUBLISHED", "DNS", "2026-09-15T12:00:03Z"),
            ("D", None, "ARCHIVED", "DNS", "2026-09-15T12:00:04Z"),
        )
        for code, category_id, status, body, timestamp in fixtures:
            article = self.repository.create_article(
                article_code=code,
                title="DNS status filter",
                summary=None,
                body_markdown=body,
                created_at=timestamp,
                updated_at=timestamp,
            )
            with database_connection(self.path) as connection:
                connection.execute(
                    "UPDATE knowledge_articles SET category_id = ?, status = ? "
                    "WHERE knowledge_article_id = ?",
                    (category_id, status, article.knowledge_article_id),
                )
            self.rows.append(self.repository.get_article(article.knowledge_article_id))

    @staticmethod
    def ids(rows):
        return [row.knowledge_article_id for row in rows]

    def test_list_all_and_each_status_preserve_order_without_duplicates(self):
        all_rows = self.repository.list_articles()
        self.assertEqual(self.ids(all_rows), self.ids(list(reversed(self.rows)) + [self.article]))
        self.assertEqual(len(self.ids(all_rows)), len(set(self.ids(all_rows))))
        expected = {
            "DRAFT": [self.rows[0], self.article],
            "PUBLISHED": [self.rows[2], self.rows[1]],
            "ARCHIVED": [self.rows[3]],
        }
        for status, rows in expected.items():
            with self.subTest(status=status):
                self.assertEqual(self.repository.list_articles(status=status), tuple(rows))

    def test_list_category_and_uncategorized_compose_with_status(self):
        self.assertEqual(
            self.repository.list_articles(category_id=11, status="PUBLISHED"),
            (self.rows[1],),
        )
        self.assertEqual(
            self.repository.list_articles(uncategorized_only=True, status="ARCHIVED"),
            (self.rows[3],),
        )
        self.assertEqual(self.repository.list_articles(category_id=22, status="DRAFT"), ())

    def test_search_status_composition_retains_global_ranking_and_no_duplicates(self):
        all_rows = self.repository.search_articles('"DNS"')
        self.assertEqual(len(all_rows), 4)
        self.assertEqual(len(self.ids(all_rows)), len(set(self.ids(all_rows))))
        for arguments, accepted in (
            ({"status": "DRAFT"}, [self.rows[0]]),
            ({"status": "PUBLISHED"}, [self.rows[1], self.rows[2]]),
            ({"status": "ARCHIVED"}, [self.rows[3]]),
            ({"category_id": 11, "status": "PUBLISHED"}, [self.rows[1]]),
            ({"uncategorized_only": True, "status": "ARCHIVED"}, [self.rows[3]]),
        ):
            with self.subTest(arguments=arguments):
                expected = [row.knowledge_article_id for row in all_rows
                            if row.knowledge_article_id in self.ids(accepted)]
                self.assertEqual(
                    self.ids(self.repository.search_articles('"DNS"', **arguments)),
                    expected,
                )

    def test_repository_status_values_are_bound_parameters(self):
        for value in ("draft", "OPEN", "' OR 1=1 --", 7, True):
            with self.subTest(value=value):
                self.assertEqual(self.repository.list_articles(status=value), ())
                self.assertEqual(self.repository.search_articles('"DNS"', status=value), ())

    def test_service_accepts_exact_domain_and_forwards_both_filters(self):
        for status in (None, "DRAFT", "PUBLISHED", "ARCHIVED"):
            with self.subTest(status=status), patch.object(
                self.repository, "list_articles", return_value=()
            ) as listing:
                self.service.list_articles(category_id=11, status=status)
                expected = {"category_id": 11, "uncategorized_only": False}
                if status is not None:
                    expected["status"] = status
                listing.assert_called_once_with(**expected)
            with self.subTest(search_status=status), patch.object(
                self.repository, "search_articles", return_value=()
            ) as search:
                self.service.search_articles("DNS", uncategorized_only=True, status=status)
                expected = {"category_id": None, "uncategorized_only": True}
                if status is not None:
                    expected["status"] = status
                search.assert_called_once_with('"DNS"', **expected)

    def test_service_rejects_invalid_status_before_repository(self):
        invalid = ("draft", "OPEN", "", 1, True, False, [], {})
        with patch.object(self.repository, "list_articles") as listing, patch.object(
            self.repository, "search_articles"
        ) as search:
            for status in invalid:
                with self.subTest(status=status), self.assertRaises(KnowledgeValidationError):
                    self.service.list_articles(status=status)
                with self.subTest(search_status=status), self.assertRaises(KnowledgeValidationError):
                    self.service.search_articles("DNS", status=status)
            listing.assert_not_called()
            search.assert_not_called()

    def test_failures_remain_safe_and_status_reads_write_nothing(self):
        for name, expected, arguments in (
            ("list_articles", KnowledgeCreationError, ()),
            ("search_articles", KnowledgeSearchError, ("DNS",)),
        ):
            with patch.object(
                self.repository, name, side_effect=sqlite3.OperationalError("private path")
            ):
                with self.assertRaises(expected) as caught:
                    getattr(self.service, name)(*arguments, status="PUBLISHED")
                self.assertNotIn("private", str(caught.exception))

        before = self.dump()
        statements = []

        @contextmanager
        def read_only(path):
            with database_connection(path) as connection:
                connection.execute("PRAGMA query_only=ON")
                connection.set_trace_callback(statements.append)
                yield connection

        with patch("f7hub.repositories.knowledge_repository.database_connection", read_only):
            for arguments in (
                {"status": "DRAFT"},
                {"category_id": 11, "status": "PUBLISHED"},
                {"uncategorized_only": True, "status": "ARCHIVED"},
            ):
                self.service.list_articles(**arguments)
                self.service.search_articles("DNS", **arguments)
        self.assertTrue(statements)
        self.assertTrue(
            all(statement.lstrip().upper().startswith(("SELECT", "--"))
                for statement in statements),
            statements,
        )
        self.assertEqual(self.dump(), before)


if __name__ == "__main__":
    unittest.main()
