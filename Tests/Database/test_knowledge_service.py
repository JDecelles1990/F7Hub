from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.services.knowledge_service import (
    KnowledgeCreationError,
    KnowledgeService,
    KnowledgeValidationError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "knowledge-service.db"
        bootstrap_database(self.path, PROJECT_ROOT / "Database" / "Migrations")
        self.repository = KnowledgeRepository(self.path)
        self.service = KnowledgeService(self.repository)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_valid_create_normalizes_fields_and_list_get_return_record(self):
        article = self.service.create_article(
            article_code="  KB0001  ", title="  Reset spooler  ",
            summary="  Synthetic summary  ", body="  # Steps  ",
        )
        self.assertEqual(article.article_code, "KB0001")
        self.assertEqual(article.title, "Reset spooler")
        self.assertEqual(article.summary, "Synthetic summary")
        self.assertEqual(article.body_markdown, "  # Steps  ")
        self.assertEqual(article.status, "DRAFT")
        self.assertEqual(article.version_number, 1)
        self.assertRegex(article.created_at, r"Z$")
        self.assertEqual(article.created_at, article.updated_at)
        self.assertEqual(self.service.list_articles(), (article,))
        self.assertEqual(self.service.get_article(article.knowledge_article_id), article)

    def test_empty_summary_becomes_null(self):
        article = self.service.create_article(
            article_code="KB0001", title="Synthetic", summary="  ", body="# Body"
        )
        self.assertIsNone(article.summary)

    def test_required_and_type_validation(self):
        valid = dict(article_code="KB0001", title="Title", summary=None, body="Body")
        for field in ("article_code", "title", "body"):
            values = dict(valid)
            values[field] = "   "
            with self.subTest(field=field), self.assertRaises(KnowledgeValidationError):
                self.service.create_article(**values)
            values[field] = 7
            with self.subTest(field=f"{field}-type"), self.assertRaises(KnowledgeValidationError):
                self.service.create_article(**values)
        with self.assertRaises(KnowledgeValidationError):
            self.service.create_article(**(valid | {"summary": 7}))

    def test_duplicate_code_has_safe_specific_feedback(self):
        values = dict(article_code="KB0001", title="Title", summary=None, body="Body")
        self.service.create_article(**values)
        with self.assertRaises(KnowledgeValidationError) as caught:
            self.service.create_article(**(values | {"article_code": "kb0001"}))
        self.assertIn("already in use", str(caught.exception))
        self.assertNotIn("UNIQUE", str(caught.exception))

    def test_persistence_and_read_failures_are_translated(self):
        with patch.object(self.repository, "create_article", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(KnowledgeCreationError) as caught:
                self.service.create_article(article_code="KB0001", title="Title", summary=None, body="Body")
        self.assertNotIn("private", str(caught.exception))
        with patch.object(self.repository, "list_articles", side_effect=PermissionError("private")):
            with self.assertRaises(KnowledgeCreationError):
                self.service.list_articles()
        with patch.object(self.repository, "get_article", side_effect=RuntimeError("private")):
            with self.assertRaises(KnowledgeCreationError):
                self.service.get_article(1)


if __name__ == "__main__":
    unittest.main()
