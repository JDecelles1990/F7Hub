"""Current Knowledge metadata: scoped references, atomic writes and concurrency."""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.tag_repository import TagRepository
from f7hub.repositories.knowledge_repository import (
    ArticleCategoryUnavailableError, ArticleMissingError, ArticleNotEditableError,
    ArticleUnchangedError, KnowledgeRepository, StaleArticleMetadataError, StaleArticleVersionError,
)
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import TicketService
from f7hub.repositories.ticket_knowledge_repository import TicketKnowledgeRepository
from f7hub.services.ticket_knowledge_service import TicketKnowledgeService
from f7hub.services.knowledge_service import (
    KnowledgeCategoryConflictError, KnowledgeCategoryError, KnowledgeService, KnowledgeValidationError,
)


def seed_knowledge_categories(path):
    rows = [(11, 'KNOWLEDGE', 'Networking', 1, 20),
            (22, 'KNOWLEDGE', 'Microsoft 365', 1, 10),
            (33, 'KNOWLEDGE', 'Legacy', 0, 0),
            (44, 'TICKET', 'Ticket only', 1, 0),
            (55, 'GENERAL', 'General only', 1, 0),
            (66, 'KNOWLEDGE', 'microsoft 365', 1, 10)]
    with database_connection(path) as connection:
        connection.executemany(
            'INSERT INTO categories (category_id, scope, name, is_active, sort_order, slug, created_at, updated_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            [(*row, f'kb-category-{row[0]}', '2026-09-14T12:00:00Z', '2026-09-14T12:00:00Z') for row in rows],
        )


class CategoryFixture:
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / 'knowledge.db'
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / 'Database/Migrations')
        seed_knowledge_categories(self.path)
        self.repository = KnowledgeRepository(self.path)
        self.categories = CategoryRepository(self.path)
        self.service = KnowledgeService(self.repository, self.categories, TagRepository(self.path))
        self.article = self.repository.create_article(
            article_code='KB-CAT', title='Synthetic Outlook', summary='Summary', body_markdown='Mail repair',
            created_at='2026-09-14T12:00:00.000Z', updated_at='2026-09-14T12:00:00.000Z',
        )

    def assign(self, article=None, category_id=11, **overrides):
        article = article or self.article
        return self.repository.set_draft_category(**(dict(
            article_id=article.knowledge_article_id, expected_version_number=article.version_number,
            expected_updated_at=article.updated_at, category_id=category_id,
            updated_at='2026-09-14T13:00:00.000Z',
        ) | overrides))

    def dump(self):
        with database_connection(self.path) as connection:
            return '\n'.join(connection.iterdump())


class KnowledgeCategoryRepositoryTests(CategoryFixture, unittest.TestCase):
    def test_knowledge_reference_scope_active_and_stable_order(self):
        self.assertEqual([c.category_id for c in self.categories.list_categories(scope='KNOWLEDGE', active_only=True)], [22, 66, 11])

    def test_assign_change_remove_change_only_category_and_timestamp(self):
        ticket = TicketService(TicketRepository(self.path)).create_ticket(subject='Synthetic ticket')
        links = TicketKnowledgeService(TicketKnowledgeRepository(self.path))
        links.link_related_article(ticket.ticket_id, self.article.knowledge_article_id)
        before_links = links.list_linked_articles(ticket.ticket_id)
        history = self.repository.get_article_version(self.article.knowledge_article_id, 1)
        current = self.article
        for i, (category_id, name) in enumerate(((11, 'Networking'), (22, 'Microsoft 365'), (None, None))):
            timestamp = f'2026-09-14T13:00:0{i}.000Z'
            result = self.assign(current, category_id, updated_at=timestamp)
            self.assertEqual(result, replace(current, category_id=category_id, category_name=name, updated_at=timestamp))
            self.assertEqual(self.repository.get_article(result.knowledge_article_id), result)
            self.assertEqual(self.repository.list_articles(), (result,))
            self.assertEqual(self.repository.get_article_version(result.knowledge_article_id, 1), history)
            self.assertEqual(links.list_linked_articles(ticket.ticket_id), before_links)
            self.assertEqual(len(self.repository.search_articles('"Outlook"')), 1)
            current = result
        with database_connection(self.path) as connection:
            connection.execute("INSERT INTO knowledge_articles_fts(knowledge_articles_fts, rank) VALUES ('integrity-check', 1)")
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(connection.execute('SELECT count(*) FROM schema_migrations').fetchone()[0], 6)

    def test_invalid_category_is_rejected_without_changes(self):
        before = self.dump()
        for category_id in (33, 44, 55, 999):
            with self.subTest(category_id=category_id), self.assertRaises(ArticleCategoryUnavailableError):
                self.assign(category_id=category_id)
            self.assertEqual(self.dump(), before)

    def test_missing_article_and_non_draft_are_rejected(self):
        with self.assertRaises(ArticleMissingError):
            self.assign(article_id=999)
        for status in ('PUBLISHED', 'ARCHIVED'):
            with database_connection(self.path) as connection:
                connection.execute('UPDATE knowledge_articles SET status = ?', (status,))
            before = self.dump()
            with self.assertRaises(ArticleNotEditableError):
                self.assign()
            self.assertEqual(self.dump(), before)

    def test_stale_version_and_same_version_metadata_precede_noop(self):
        current = self.assign()
        before = self.dump()
        with self.assertRaises(StaleArticleMetadataError):
            self.assign(category_id=11)
        with self.assertRaises(StaleArticleVersionError):
            self.assign(current, expected_version_number=2)
        self.assertEqual(self.dump(), before)

    def test_noop_and_reused_timestamp_leave_database_unchanged(self):
        before = self.dump()
        with self.assertRaises(ArticleUnchangedError):
            self.assign(category_id=None)
        with self.assertRaises(RuntimeError):
            self.assign(updated_at=self.article.updated_at)
        self.assertEqual(self.dump(), before)

    def test_inactive_current_name_is_readable_and_can_be_cleared(self):
        current = self.assign()
        with database_connection(self.path) as connection:
            connection.execute('UPDATE categories SET is_active = 0 WHERE category_id = 11')
        current = self.repository.get_article(current.knowledge_article_id)
        self.assertEqual(current.category_name, 'Networking')
        self.assertEqual(self.repository.list_articles()[0].category_name, 'Networking')
        with self.assertRaises(ArticleCategoryUnavailableError):
            self.assign(current)
        self.assertIsNone(self.assign(current, None, updated_at='2026-09-14T14:00:00Z').category_id)

    def test_reload_failure_rolls_back_with_existing_ticket_link(self):
        ticket = TicketService(TicketRepository(self.path)).create_ticket(subject='Rollback ticket')
        TicketKnowledgeService(TicketKnowledgeRepository(self.path)).link_related_article(ticket.ticket_id, self.article.knowledge_article_id)
        before = self.dump()
        for failure in (None, sqlite3.OperationalError('private')):
            with patch('f7hub.repositories.knowledge_repository._get_article', side_effect=[self.article, failure]):
                with self.assertRaises((RuntimeError, sqlite3.Error)):
                    self.assign()
            self.assertEqual(self.dump(), before)

    def test_zero_row_update_is_rejected(self):
        with database_connection(self.path) as connection:
            connection.execute('CREATE TRIGGER skip_category BEFORE UPDATE OF category_id ON knowledge_articles BEGIN SELECT RAISE(IGNORE); END')
        before = self.dump()
        with self.assertRaises(StaleArticleMetadataError):
            self.assign()
        self.assertEqual(self.dump(), before)


class KnowledgeCategoryServiceTests(CategoryFixture, unittest.TestCase):
    def test_scoped_reference_read_and_safe_failure(self):
        with patch.object(self.categories, 'list_categories', wraps=self.categories.list_categories) as read:
            options = self.service.list_active_knowledge_categories()
        read.assert_called_once_with(scope='KNOWLEDGE', active_only=True)
        self.assertEqual([(c.category_id, c.name) for c in options], [(22, 'Microsoft 365'), (66, 'microsoft 365'), (11, 'Networking')])
        with patch.object(self.categories, 'list_categories', side_effect=sqlite3.OperationalError('private')):
            with self.assertRaisesRegex(KnowledgeCategoryError, '^Could not load Knowledge categories'):
                self.service.list_active_knowledge_categories()
        self.assertEqual(self.service.get_article(self.article.knowledge_article_id), self.article)

    def test_input_validation_without_write(self):
        valid = [1, 1, self.article.updated_at, 11]
        with patch.object(self.repository, 'set_draft_category') as write:
            for index in (0, 1, 3):
                for invalid in (True, False, 0, -1, '1', 1.5, [], None):
                    if index == 3 and invalid is None:
                        continue
                    args = valid.copy()
                    args[index] = invalid
                    with self.subTest(args=args), self.assertRaises(KnowledgeValidationError):
                        self.service.set_article_category(*args)
            for token in ('', '  ', None, True, 1):
                with self.assertRaises(KnowledgeValidationError):
                    self.service.set_article_category(1, 1, token, 11)
            write.assert_not_called()

    def test_one_clock_read_assign_and_clear(self):
        instant = datetime(2026, 9, 14, 14, tzinfo=timezone.utc)
        with patch('f7hub.services.knowledge_service.datetime', wraps=datetime) as clock:
            clock.now.return_value = instant
            current = self.service.set_article_category(1, 1, self.article.updated_at, 11)
            clock.now.assert_called_once_with(timezone.utc)
        self.assertEqual(current.updated_at, '2026-09-14T14:00:00.000000Z')
        removed = self.service.set_article_category(1, 1, current.updated_at, None)
        self.assertIsNone(removed.category_id)
        self.assertNotEqual(removed.updated_at, current.updated_at)

    def test_repeated_or_backward_clock_advances_token_and_rejects_old_token(self):
        instant = datetime(2026, 9, 14, 11, tzinfo=timezone.utc)
        with patch('f7hub.services.knowledge_service.datetime', wraps=datetime) as clock:
            clock.now.return_value = instant
            current = self.service.set_article_category(1, 1, self.article.updated_at, 11)
            changed = self.service.set_article_category(1, 1, current.updated_at, 22)
            self.assertGreater(changed.updated_at, current.updated_at)
            self.assertNotEqual(current.updated_at, self.article.updated_at)
            with self.assertRaises(KnowledgeCategoryConflictError):
                self.service.set_article_category(1, 1, current.updated_at, None)
        self.assertEqual(self.repository.get_article(1), changed)

    def test_error_meanings_and_sanitization(self):
        cases = ((ArticleMissingError(), 'no longer exists'),
                 (ArticleNotEditableError(), 'Only draft'),
                 (StaleArticleVersionError(), 'Reopen the latest'),
                 (StaleArticleMetadataError(), 'Reopen the latest'),
                 (ArticleCategoryUnavailableError(), 'no longer available'),
                 (ArticleUnchangedError(), 'already selected'),
                 (sqlite3.OperationalError('private'), 'Could not update'),
                 (RuntimeError('private'), 'Could not update'),
                 (OSError('private'), 'Could not update'))
        for error, message in cases:
            with self.subTest(error=error), patch.object(self.repository, 'set_draft_category', side_effect=error):
                with self.assertRaisesRegex(KnowledgeCategoryError, message) as caught:
                    self.service.set_article_category(1, 1, self.article.updated_at, 11)
                self.assertNotIn('private', str(caught.exception))
