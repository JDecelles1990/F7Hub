"""Read-only single-tag predicates for current Knowledge article reads."""

from contextlib import contextmanager
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.tag_repository import TagRepository
from f7hub.services.knowledge_service import KnowledgeService, KnowledgeValidationError


class KnowledgeTagFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "tag-filter.db"
        bootstrap_database(
            self.path, Path(__file__).resolve().parents[2] / "Database" / "Migrations"
        )
        with database_connection(self.path) as connection:
            connection.executemany(
                "INSERT INTO categories (category_id, scope, name, slug, is_active, "
                "sort_order, created_at, updated_at) VALUES (?, 'KNOWLEDGE', ?, ?, 1, 0, ?, ?)",
                (
                    (11, "Networking", "networking", "2026-09-15T10:00:00Z", "2026-09-15T10:00:00Z"),
                    (22, "Microsoft 365", "microsoft-365", "2026-09-15T10:00:00Z", "2026-09-15T10:00:00Z"),
                ),
            )
            connection.executemany(
                "INSERT INTO tags (tag_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
                (
                    (11, "VPN", "vpn", "2026-09-15T10:00:00Z"),
                    (22, "Windows", "windows", "2026-09-15T10:00:00Z"),
                    (33, "Security", "security", "2026-09-15T10:00:00Z"),
                    (44, "Unused", "unused", "2026-09-15T10:00:00Z"),
                ),
            )
        self.repository = KnowledgeRepository(self.path)
        self.service = KnowledgeService(
            self.repository, CategoryRepository(self.path), TagRepository(self.path)
        )
        fixtures = (
            ("A", 11, "DRAFT", (11, 22), "DNS DNS DNS"),
            ("B", 11, "PUBLISHED", (11,), "DNS DNS"),
            ("C", 22, "PUBLISHED", (33,), "DNS"),
            ("D", None, "ARCHIVED", (), "DNS"),
            ("E", 11, "ARCHIVED", (11, 33, 22), "DNS"),
        )
        self.rows = {}
        for index, (code, category_id, status, tag_ids, body) in enumerate(fixtures, 1):
            timestamp = f"2026-09-15T12:00:0{index}Z"
            article = self.repository.create_article(
                article_code=code, title="DNS tag filter", summary=None,
                body_markdown=body, created_at=timestamp, updated_at=timestamp,
            )
            with database_connection(self.path) as connection:
                connection.execute(
                    "UPDATE knowledge_articles SET category_id = ?, status = ? "
                    "WHERE knowledge_article_id = ?",
                    (category_id, status, article.knowledge_article_id),
                )
                connection.executemany(
                    "INSERT INTO knowledge_article_tags "
                    "(knowledge_article_id, tag_id, created_at) VALUES (?, ?, ?)",
                    ((article.knowledge_article_id, tag_id, timestamp) for tag_id in tag_ids),
                )
            self.rows[code] = self.repository.get_article(article.knowledge_article_id)

    @staticmethod
    def codes(rows):
        return [row.article_code for row in rows]

    def dump(self):
        with database_connection(self.path) as connection:
            return "\n".join(connection.iterdump())

    def test_list_all_specific_untagged_and_composition_are_exact_and_unique(self):
        self.assertEqual(self.codes(self.repository.list_articles()), ["E", "D", "C", "B", "A"])
        self.assertEqual(self.codes(self.repository.list_articles(tag_id=11)), ["E", "B", "A"])
        self.assertEqual(self.codes(self.repository.list_articles(tag_id=33)), ["E", "C"])
        self.assertEqual(self.codes(self.repository.list_articles(untagged_only=True)), ["D"])
        self.assertEqual(
            self.codes(self.repository.list_articles(category_id=11, tag_id=11)),
            ["E", "B", "A"],
        )
        self.assertEqual(
            self.codes(self.repository.list_articles(category_id=11, status="PUBLISHED", tag_id=11)),
            ["B"],
        )
        self.assertEqual(
            self.codes(self.repository.list_articles(
                uncategorized_only=True, status="ARCHIVED", untagged_only=True
            )),
            ["D"],
        )
        self.assertEqual(len(self.repository.list_articles(tag_id=11)), 3)

    def test_fts_tag_filters_preserve_relative_ranking_and_never_duplicate(self):
        all_rows = self.repository.search_articles('"DNS"')
        self.assertEqual(self.codes(all_rows), ["A", "B", "E", "D", "C"])
        for arguments, accepted in (
            ({"tag_id": 11}, {"A", "B", "E"}),
            ({"tag_id": 33}, {"C", "E"}),
            ({"untagged_only": True}, {"D"}),
            ({"category_id": 11, "status": "PUBLISHED", "tag_id": 11}, {"B"}),
            ({"category_id": 22, "status": "PUBLISHED", "tag_id": 33}, {"C"}),
            ({"uncategorized_only": True, "status": "ARCHIVED", "untagged_only": True}, {"D"}),
        ):
            with self.subTest(arguments=arguments):
                expected = [row.article_code for row in all_rows if row.article_code in accepted]
                actual = self.codes(self.repository.search_articles('"DNS"', **arguments))
                self.assertEqual(actual, expected)
                self.assertEqual(len(actual), len(set(actual)))

    def test_service_validates_and_forwards_one_tag_mode(self):
        for arguments in ({}, {"tag_id": 11}, {"untagged_only": True},
                          {"category_id": 11, "status": "PUBLISHED", "tag_id": 11}):
            with self.subTest(arguments=arguments), patch.object(
                self.repository, "list_articles", return_value=()
            ) as listing:
                self.service.list_articles(**arguments)
                expected = {"category_id": None, "uncategorized_only": False} | arguments
                listing.assert_called_once_with(**expected)
            with self.subTest(search_arguments=arguments), patch.object(
                self.repository, "search_articles", return_value=()
            ) as search:
                self.service.search_articles("DNS", **arguments)
                expected = {"category_id": None, "uncategorized_only": False} | arguments
                search.assert_called_once_with('"DNS"', **expected)

        invalid = (
            {"tag_id": True}, {"tag_id": 0}, {"tag_id": -1}, {"tag_id": "11"},
            {"tag_id": 1.5}, {"untagged_only": 1},
            {"tag_id": 11, "untagged_only": True},
        )
        with patch.object(self.repository, "list_articles") as listing, patch.object(
            self.repository, "search_articles"
        ) as search:
            for arguments in invalid:
                with self.subTest(invalid=arguments), self.assertRaises(KnowledgeValidationError):
                    self.service.list_articles(**arguments)
                with self.subTest(invalid_search=arguments), self.assertRaises(KnowledgeValidationError):
                    self.service.search_articles("DNS", **arguments)
            listing.assert_not_called()
            search.assert_not_called()

    def test_all_global_options_are_ordered_even_when_unused(self):
        self.assertEqual(
            [(tag.tag_id, tag.name) for tag in self.service.list_available_tags()],
            [(33, "Security"), (44, "Unused"), (11, "VPN"), (22, "Windows")],
        )

    def test_any_selected_tags_compose_without_duplicates_or_writes(self):
        before = self.dump()
        selected = (11, 33)
        self.assertEqual(
            self.codes(self.service.list_articles(tag_ids=selected)),
            ["E", "C", "B", "A"],
        )
        self.assertEqual(
            self.codes(self.service.list_articles(
                category_id=11, status="ARCHIVED", tag_ids=selected,
            )), ["E"],
        )
        all_search = self.service.search_articles("DNS")
        filtered = self.service.search_articles("DNS", tag_ids=selected)
        self.assertEqual(
            self.codes(filtered),
            [row.article_code for row in all_search if row.article_code in {"A", "B", "C", "E"}],
        )
        self.assertEqual(len(filtered), len({row.knowledge_article_id for row in filtered}))
        self.assertEqual(self.codes(self.service.list_articles(tag_ids=())),
                         self.codes(self.service.list_articles()))
        self.assertEqual(self.dump(), before)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.rows["A"].tag_ids, (11, 22))

    def test_any_tag_validation_precedes_repository_calls(self):
        invalid = (
            {"tag_ids": [11, 33]}, {"tag_ids": (True, 11)},
            {"tag_ids": (0, 11)}, {"tag_ids": (11, 11)},
            {"tag_ids": (11,), "tag_id": 11},
            {"tag_ids": (), "untagged_only": True},
        )
        with patch.object(self.repository, "list_articles") as listing, patch.object(
            self.repository, "search_articles"
        ) as searching:
            for arguments in invalid:
                with self.subTest(arguments=arguments):
                    with self.assertRaises(KnowledgeValidationError):
                        self.service.list_articles(**arguments)
                    with self.assertRaises(KnowledgeValidationError):
                        self.service.search_articles("DNS", **arguments)
            listing.assert_not_called()
            searching.assert_not_called()
        for operation in (
            self.repository.list_articles,
            lambda **arguments: self.repository.search_articles('"DNS"', **arguments),
        ):
            for arguments in invalid:
                with self.subTest(operation=operation, arguments=arguments):
                    with self.assertRaises(ValueError):
                        operation(**arguments)

    def test_repository_rejects_contradiction_and_filtered_reads_write_nothing(self):
        for operation in (
            self.repository.list_articles,
            lambda **arguments: self.repository.search_articles('"DNS"', **arguments),
        ):
            with self.assertRaises(ValueError):
                operation(tag_id=11, untagged_only=True)

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
                {}, {"tag_id": 11}, {"untagged_only": True},
                {"tag_ids": (11, 33)},
                {"category_id": 11, "tag_id": 11},
                {"status": "ARCHIVED", "tag_id": 33},
                {"category_id": 11, "status": "ARCHIVED", "tag_id": 11},
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
