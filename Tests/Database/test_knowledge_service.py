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
    KnowledgeUpdateError,
    KnowledgeEditConflictError,
    KnowledgeNoChangesError,
    KnowledgeHistoryArticleMissingError,
    KnowledgeHistoryError,
    KnowledgeHistoryVersionMissingError,
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

    def create_for_edit(self):
        return self.service.create_article(article_code="KB0001", title="Title", summary=None, body="Body")

    def update(self, article, **overrides):
        return self.service.update_article(**(dict(
            article_id=article.knowledge_article_id, expected_version_number=article.version_number,
            title=" Revised title ", summary=" Revised summary ", body="  # Body\n\n\tStep  \n",
        ) | overrides))

    def test_valid_update_normalizes_metadata_and_preserves_body_exactly(self):
        first = self.create_for_edit()
        second = self.update(first)
        self.assertEqual(second.title, "Revised title")
        self.assertEqual(second.summary, "Revised summary")
        self.assertEqual(second.body_markdown, "  # Body\n\n\tStep  \n")
        self.assertEqual(second.article_code, first.article_code)
        self.assertEqual(second.version_number, 2)
        self.assertRegex(second.updated_at, r"Z$")
        for summary in (" \n\t", None):
            second = self.update(second, title=f"Title {second.version_number}", summary=summary)
            self.assertIsNone(second.summary)

    def test_update_id_and_expected_version_reject_nonpositive_and_noninteger(self):
        first = self.create_for_edit()
        with patch.object(self.repository, "update_draft_article") as update:
            for field in ("article_id", "expected_version_number"):
                for value in (True, False, 0, -1, 1.5, "1", None):
                    with self.subTest(field=field, value=value), self.assertRaises(KnowledgeValidationError):
                        self.update(first, **{field: value})
            update.assert_not_called()

    def test_update_text_validation_and_code_is_not_mutable_input(self):
        first = self.create_for_edit()
        with patch.object(self.repository, "update_draft_article") as update:
            for field in ("title", "body"):
                for value in (None, 7, True, "", " \n\t"):
                    with self.subTest(field=field, value=value), self.assertRaises(KnowledgeValidationError):
                        self.update(first, **{field: value})
            with self.assertRaises(KnowledgeValidationError):
                self.update(first, summary=7)
            with self.assertRaises(TypeError):
                self.update(first, article_code="Changed")
            update.assert_not_called()

    def test_update_condition_errors_are_safe_specific_and_typed(self):
        from f7hub.repositories.knowledge_repository import (
            ArticleMissingError, ArticleNotEditableError, StaleArticleVersionError, ArticleUnchangedError,
        )
        first = self.create_for_edit()
        for error, expected, message in (
            (ArticleMissingError, KnowledgeEditConflictError, "no longer exists"),
            (ArticleNotEditableError, KnowledgeEditConflictError, "Only draft"),
            (StaleArticleVersionError, KnowledgeEditConflictError, "Reopen the latest version"),
            (ArticleUnchangedError, KnowledgeNoChangesError, "No changes to save"),
            (sqlite3.OperationalError, KnowledgeUpdateError, "Could not save"),
            (PermissionError, KnowledgeUpdateError, "Could not save"),
            (RuntimeError, KnowledgeUpdateError, "Could not save"),
        ):
            with self.subTest(error=error), patch.object(self.repository, "update_draft_article", side_effect=error("private SQL path")):
                with self.assertRaises(expected) as caught:
                    self.update(first)
                self.assertIn(message, str(caught.exception))
                self.assertNotIn("private", str(caught.exception))

    def test_normalized_no_change_and_stale_no_change_are_authoritative(self):
        first = self.create_for_edit()
        with self.assertRaises(KnowledgeNoChangesError):
            self.update(first, title=" Title ", summary="  ", body="Body")
        second = self.update(first)
        with self.assertRaises(KnowledgeEditConflictError):
            self.update(first, title=second.title, summary=second.summary, body=second.body_markdown)
        self.assertEqual(self.service.get_article(first.knowledge_article_id), second)

    def test_history_validates_positive_ids_and_rejects_bool(self):
        article = self.create_for_edit()
        with patch.object(self.repository, "list_article_versions") as list_versions, patch.object(
            self.repository, "get_article_version"
        ) as get_version:
            for value in (True, False, 0, -1, 1.5, "1", None):
                with self.subTest(article_id=value), self.assertRaises(KnowledgeValidationError):
                    self.service.list_article_versions(value)
                with self.subTest(detail_article_id=value), self.assertRaises(KnowledgeValidationError):
                    self.service.get_article_version(value, 1)
                with self.subTest(version_number=value), self.assertRaises(KnowledgeValidationError):
                    self.service.get_article_version(article.knowledge_article_id, value)
            list_versions.assert_not_called()
            get_version.assert_not_called()

    def test_history_returns_records_and_translates_failures_safely(self):
        from f7hub.repositories.knowledge_repository import ArticleMissingError, ArticleVersionMissingError

        article = self.create_for_edit()
        self.assertEqual(self.service.list_article_versions(article.knowledge_article_id)[0].version_number, 1)
        self.assertEqual(
            self.service.get_article_version(article.knowledge_article_id, 1).body_markdown,
            "Body",
        )
        cases = (
            ("list_article_versions", ArticleMissingError("private"), KnowledgeHistoryArticleMissingError),
            ("list_article_versions", sqlite3.OperationalError("private"), KnowledgeHistoryError),
            ("get_article_version", ArticleMissingError("private"), KnowledgeHistoryArticleMissingError),
            ("get_article_version", ArticleVersionMissingError("private"), KnowledgeHistoryVersionMissingError),
            ("get_article_version", PermissionError("private"), KnowledgeHistoryError),
        )
        for method, error, expected in cases:
            with self.subTest(method=method, error=type(error).__name__), patch.object(
                self.repository, method, side_effect=error
            ):
                with self.assertRaises(expected) as caught:
                    if method == "list_article_versions":
                        self.service.list_article_versions(article.knowledge_article_id)
                    else:
                        self.service.get_article_version(article.knowledge_article_id, 1)
                self.assertNotIn("private", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
