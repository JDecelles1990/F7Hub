"""Read-only relational predicates shared by normal and FTS article reads."""

from contextlib import contextmanager
import sqlite3
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import database_connection
from f7hub.services.knowledge_service import KnowledgeCreationError, KnowledgeSearchError, KnowledgeValidationError
from Tests.Database.test_knowledge_categories import CategoryFixture


class KnowledgeCategoryFilterTests(CategoryFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.rows = []
        for i, (category, status) in enumerate(((11, 'DRAFT'), (11, 'PUBLISHED'),
                (11, 'ARCHIVED'), (22, 'DRAFT'), (None, 'DRAFT'), (33, 'ARCHIVED'))):
            article = self.repository.create_article(
                article_code=f'FILTER-{i}', title='DNS', summary=None,
                body_markdown='DNS DNS' if i == 0 else 'DNS',
                created_at='2026-09-15T12:00:00Z', updated_at='2026-09-15T12:00:00Z',
            )
            with database_connection(self.path) as connection:
                connection.execute('UPDATE knowledge_articles SET category_id=?, status=? WHERE knowledge_article_id=?',
                                   (category, status, article.knowledge_article_id))
            self.rows.append(self.repository.get_article(article.knowledge_article_id))

    @staticmethod
    def ids(rows):
        return [a.knowledge_article_id for a in rows]

    def test_all_list_preserves_order_statuses_and_inactive_name(self):
        result = self.repository.list_articles()
        self.assertEqual(self.ids(result), self.ids(list(reversed(self.rows)) + [self.article]))
        self.assertEqual({a.status for a in result}, {'DRAFT', 'PUBLISHED', 'ARCHIVED'})
        self.assertEqual(result[0].category_name, 'Legacy')

    def test_specific_list_exact_category_including_all_statuses(self):
        self.assertEqual(self.repository.list_articles(category_id=11), tuple(reversed(self.rows[:3])))
        self.assertEqual(self.repository.list_articles(category_id=33), (self.rows[5],))

    def test_uncategorized_list_null_only_and_unknown_category_empty(self):
        self.assertEqual(self.repository.list_articles(uncategorized_only=True), (self.rows[4], self.article))
        self.assertEqual(self.repository.list_articles(category_id=999), ())

    def test_fts_filters_preserve_global_ranking_relative_order_without_duplicates(self):
        all_rows = self.repository.search_articles('"DNS"')
        self.assertEqual(len(all_rows), 6)
        self.assertEqual(len(set(self.ids(all_rows))), 6)
        # More term occurrences rank first despite the older ID; equal scores use ID DESC.
        self.assertEqual(self.ids(all_rows), self.ids([self.rows[0]] + list(reversed(self.rows[1:]))))
        for arguments, accepted in (({'category_id': 11}, self.rows[:3]),
                ({'uncategorized_only': True}, [self.rows[4]]), ({'category_id': 33}, [self.rows[5]])):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.ids(self.repository.search_articles('"DNS"', **arguments)),
                                 [a.knowledge_article_id for a in all_rows if a.knowledge_article_id in self.ids(accepted)])

    def test_repository_values_cannot_inject_predicates(self):
        for value in ('11 OR 1=1', "11'; DROP TABLE knowledge_articles;--"):
            self.assertEqual(self.repository.list_articles(category_id=value), ())
            self.assertEqual(self.repository.search_articles('"DNS"', category_id=value), ())
        for operation in (self.repository.list_articles, lambda **kw: self.repository.search_articles('"DNS"', **kw)):
            with self.assertRaises(ValueError):
                operation(category_id=11, uncategorized_only=True)

    def test_service_maps_three_modes_and_preserves_literal_search(self):
        for arguments in ({}, {'uncategorized_only': True}, {'category_id': 11}):
            expected = {'category_id': None, 'uncategorized_only': False} | arguments
            with patch.object(self.repository, 'list_articles', return_value=()) as listing:
                self.service.list_articles(**arguments)
                listing.assert_called_once_with(**expected)
            with patch.object(self.repository, 'search_articles', return_value=()) as search:
                self.service.search_articles('DNS* (OR)', **arguments)
                search.assert_called_once_with('"DNS" "OR"', **expected)

    def test_service_rejects_invalid_filters_before_any_query(self):
        invalid = [{'category_id': x} for x in (True, False, 0, -1, 1.5, '11')]
        invalid += [{'uncategorized_only': x} for x in (0, 1, None, 'yes')]
        invalid += [{'category_id': 11, 'uncategorized_only': True}]
        with patch.object(self.repository, 'list_articles') as listing, patch.object(self.repository, 'search_articles') as search:
            for arguments in invalid:
                for operation in (self.service.list_articles, lambda **kw: self.service.search_articles('', **kw)):
                    with self.subTest(arguments=arguments), self.assertRaises(KnowledgeValidationError):
                        operation(**arguments)
            listing.assert_not_called()
            search.assert_not_called()

    def test_active_options_use_shared_scope_and_order(self):
        with patch.object(self.categories, 'list_categories', wraps=self.categories.list_categories) as categories:
            self.assertEqual([a.category_id for a in self.service.list_active_knowledge_categories()], [22, 66, 11])
            categories.assert_called_once_with(scope='KNOWLEDGE', active_only=True)

    def test_filtered_read_failures_have_safe_service_errors(self):
        for name, exception, arguments in (('list_articles', KnowledgeCreationError, ()),
                ('search_articles', KnowledgeSearchError, ('DNS',))):
            with patch.object(self.repository, name, side_effect=sqlite3.OperationalError('private path')):
                with self.assertRaises(exception) as caught:
                    getattr(self.service, name)(*arguments, category_id=11)
                self.assertNotIn('private', str(caught.exception))

    def test_reads_write_nothing_and_preserve_schema_fts_and_integrity(self):
        before = self.dump()
        statements = []
        @contextmanager
        def read_only(path):
            with database_connection(path) as connection:
                connection.execute('PRAGMA query_only=ON')
                connection.set_trace_callback(statements.append)
                yield connection
        with patch('f7hub.repositories.knowledge_repository.database_connection', read_only):
            for arguments in ({}, {'uncategorized_only': True}, {'category_id': 11}):
                self.service.list_articles(**arguments)
                self.service.search_articles('DNS', **arguments)
        self.assertTrue(statements)
        self.assertTrue(all(s.lstrip().upper().startswith(('SELECT', '--')) for s in statements), statements)
        self.assertEqual(self.dump(), before)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM schema_migrations').fetchone()[0], 6)
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            connection.execute("INSERT INTO knowledge_articles_fts(knowledge_articles_fts, rank) VALUES ('integrity-check', 1)")
