"""Current global-tag metadata behavior for draft Knowledge articles."""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.knowledge_repository import (
    ArticleMissingError, ArticleNotEditableError, ArticleTagUnavailableError,
    ArticleUnchangedError, KnowledgeRepository, StaleArticleMetadataError,
    StaleArticleVersionError,
)
from f7hub.repositories.tag_repository import TagRepository
from f7hub.services.knowledge_service import (
    KnowledgeTagConflictError, KnowledgeTagError, KnowledgeService, KnowledgeValidationError,
)


class TagFixture:
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "tags.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        with database_connection(self.path) as connection:
            connection.executemany(
                "INSERT INTO tags (tag_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
                ((11, "Windows", "windows", "2026-09-15T10:00:00Z"),
                 (22, "Networking", "networking", "2026-09-15T10:00:00Z"),
                 (33, "VPN", "vpn", "2026-09-15T10:00:00Z")),
            )
        self.repository = KnowledgeRepository(self.path)
        self.tags = TagRepository(self.path)
        self.service = KnowledgeService(self.repository, CategoryRepository(self.path), self.tags)
        self.article = self.repository.create_article(
            article_code="KB-TAGS", title="Synthetic tags", summary="Summary", body_markdown="Body",
            created_at="2026-09-15T10:00:00.000000Z", updated_at="2026-09-15T10:00:00.000000Z",
        )

    def assign(self, article=None, tag_ids=(22,), **overrides):
        article = article or self.article
        return self.repository.set_draft_tags(**(dict(
            article_id=article.knowledge_article_id, expected_version_number=article.version_number,
            expected_updated_at=article.updated_at, tag_ids=tag_ids,
            updated_at="2026-09-15T11:00:00.000000Z",
        ) | overrides))

    def dump(self):
        with database_connection(self.path) as connection:
            return "\n".join(connection.iterdump())


class KnowledgeTagRepositoryTests(TagFixture, unittest.TestCase):
    def test_global_and_article_reads_are_stable_and_replacement_is_current_metadata(self):
        self.assertEqual([(tag.tag_id, tag.name) for tag in self.tags.list_tags()], [(22, "Networking"), (33, "VPN"), (11, "Windows")])
        history = self.repository.get_article_version(self.article.knowledge_article_id, 1)
        current = self.assign(tag_ids=(22, 11))
        self.assertEqual(current.tag_names, ("Networking", "Windows"))
        self.assertEqual([(tag.tag_id, tag.name) for tag in self.tags.list_article_tags(current.knowledge_article_id)], [(22, "Networking"), (11, "Windows")])
        changed = self.assign(current, (33, 11), updated_at="2026-09-15T11:00:01.000000Z")
        self.assertEqual(changed.tag_names, ("VPN", "Windows"))
        self.assertEqual(changed.version_number, 1)
        self.assertEqual(changed.category_id, self.article.category_id)
        self.assertEqual(changed.status, "DRAFT")
        self.assertEqual(changed.published_at, self.article.published_at)
        self.assertEqual(self.repository.get_article_version(changed.knowledge_article_id, 1), history)
        cleared = self.assign(changed, (), updated_at="2026-09-15T11:00:02.000000Z")
        self.assertEqual(cleared.tag_names, ())

    def test_invalid_missing_non_draft_stale_and_noop_leave_no_partial_bridge_rows(self):
        before = self.dump()
        with self.assertRaises(ArticleTagUnavailableError):
            self.assign(tag_ids=(999,))
        self.assertEqual(self.dump(), before)
        current = self.assign()
        before = self.dump()
        with self.assertRaises(ArticleUnchangedError):
            self.assign(current)
        with self.assertRaises(StaleArticleMetadataError):
            self.assign(tag_ids=(33,))
        with self.assertRaises(StaleArticleVersionError):
            self.assign(current, tag_ids=(33,), expected_version_number=2)
        self.assertEqual(self.dump(), before)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE knowledge_articles SET status = 'PUBLISHED' WHERE knowledge_article_id = ?", (current.knowledge_article_id,))
        before = self.dump()
        with self.assertRaises(ArticleNotEditableError):
            self.assign(current, tag_ids=(33,))
        with self.assertRaises(ArticleMissingError):
            self.assign(article=replace(current, knowledge_article_id=999), tag_ids=(33,))
        self.assertEqual(self.dump(), before)

    def test_content_and_category_metadata_races_reject_the_stale_tag_writer(self):
        content = self.service.update_article(article_id=self.article.knowledge_article_id, expected_version_number=1, title="V2", summary=None, body="New body")
        with self.assertRaises(StaleArticleVersionError):
            self.assign(tag_ids=(22,))
        self.assertEqual(self.tags.list_article_tags(content.knowledge_article_id), ())
        with database_connection(self.path) as connection:
            connection.execute(
                "INSERT INTO categories (category_id, scope, name, slug, created_at, updated_at) "
                "VALUES (44, 'KNOWLEDGE', 'Security', 'security', ?, ?)",
                ("2026-09-15T10:00:00Z", "2026-09-15T10:00:00Z"),
            )
        category = self.repository.set_draft_category(
            article_id=content.knowledge_article_id,
            expected_version_number=content.version_number,
            expected_updated_at=content.updated_at,
            category_id=44,
            updated_at="2026-09-15T12:00:00.000000Z",
        )
        with self.assertRaises(StaleArticleMetadataError):
            self.assign(content, (33,), updated_at="2026-09-15T12:01:00.000000Z")
        self.assertEqual(self.repository.get_article(content.knowledge_article_id), category)
        self.assertEqual(self.tags.list_article_tags(content.knowledge_article_id), ())

    def test_same_version_tag_race_rejects_stale_writer_and_retains_winner(self):
        reviewed = self.article
        winner = self.assign(reviewed, (22, 11))
        with self.assertRaises(StaleArticleMetadataError):
            self.assign(reviewed, (33,), updated_at="2026-09-15T11:00:01.000000Z")
        self.assertEqual(self.repository.get_article(reviewed.knowledge_article_id), winner)
        self.assertEqual(
            tuple(tag.tag_id for tag in self.tags.list_article_tags(reviewed.knowledge_article_id)),
            (22, 11),
        )

    def test_rollback_after_bridge_write_failure(self):
        before = self.dump()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_tag_insert BEFORE INSERT ON knowledge_article_tags BEGIN SELECT RAISE(ABORT, 'blocked'); END")
        with self.assertRaises(sqlite3.Error):
            self.assign(tag_ids=(22,))
        # The assertion excludes the test trigger itself; no relationship or article data was changed.
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_article_tags").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT updated_at FROM knowledge_articles").fetchone()[0], self.article.updated_at)

    def test_article_token_update_failure_rolls_back_bridge_removals_and_additions(self):
        current = self.assign(tag_ids=(22, 11))
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
            connection.execute(
                "CREATE TRIGGER skip_tag_token BEFORE UPDATE OF updated_at ON knowledge_articles "
                "BEGIN SELECT RAISE(IGNORE); END"
            )
        with self.assertRaises(StaleArticleMetadataError):
            self.assign(current, (33,), updated_at="2026-09-15T11:00:01.000000Z")
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER skip_tag_token")
            self.assertEqual(tuple(connection.iterdump()), before)


class KnowledgeTagServiceTests(TagFixture, unittest.TestCase):
    def test_input_validation_safe_errors_and_strict_timestamp(self):
        with patch.object(self.repository, "set_draft_tags") as write:
            for bad in (None, True, 1, "1", {1}, (1, 1), (True,), (0,), (-1,), ("1",)):
                with self.subTest(bad=bad), self.assertRaises(KnowledgeValidationError):
                    self.service.set_article_tags(1, 1, self.article.updated_at, bad)
            write.assert_not_called()
        instant = datetime(2026, 9, 15, 9, tzinfo=timezone.utc)
        with patch("f7hub.services.knowledge_service.datetime", wraps=datetime) as clock:
            clock.now.return_value = instant
            changed = self.service.set_article_tags(1, 1, self.article.updated_at, (22,))
            clock.now.assert_called_once_with(timezone.utc)
        self.assertGreater(changed.updated_at, self.article.updated_at)
        for error, message in ((ArticleTagUnavailableError(), "no longer available"), (ArticleUnchangedError(), "already selected"), (StaleArticleMetadataError(), "Reopen"), (sqlite3.OperationalError("private"), "Could not update")):
            with self.subTest(error=error), patch.object(self.repository, "set_draft_tags", side_effect=error):
                with self.assertRaisesRegex((KnowledgeTagError, KnowledgeTagConflictError), message) as caught:
                    self.service.set_article_tags(1, 1, changed.updated_at, ())
                self.assertNotIn("private", str(caught.exception))
