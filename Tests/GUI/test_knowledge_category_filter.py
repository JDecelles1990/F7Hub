"""Filter state and asynchronous failures in the real MainWindow hierarchy."""

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from Tests.Database.test_knowledge_categories import seed_knowledge_categories


class KnowledgeCategoryFilterGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'filter-ui.db'
        self.context = bootstrap_application(database_path=self.path)
        seed_knowledge_categories(self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.workspace = self.window.knowledge_workspace
        self.service = self.context.knowledge_service
        self.wait_idle()
        self.rows = []
        for code, category in (('A1', 11), ('A2', 22), ('A3', None)):
            article = self.service.create_article(article_code=code, title='DNS procedure', summary=None, body='DNS steps')
            if category is not None:
                article = self.service.set_article_category(article.knowledge_article_id, 1, article.updated_at, category)
            self.rows.append(article)

    def tearDown(self):
        self.wait_idle()
        if self.workspace._category_dialog:
            self.workspace._category_dialog.reject()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def wait_idle(self, *, references=True):
        deadline = time.monotonic() + 5
        self.app.processEvents()
        while (self.window.runner.busy or (references and self.workspace.filter_loading)) and time.monotonic() < deadline:
            QTest.qWait(10)
        self.app.processEvents()
        self.assertFalse(self.window.runner.busy)
        if references:
            self.assertFalse(self.workspace.filter_loading)

    def show(self):
        self.window.show_knowledge()
        self.wait_idle()

    def choose(self, category):
        index = 1 if category is None else self.workspace.category_filter.findData(category)
        self.workspace.category_filter.setCurrentIndex(index)
        self.wait_idle()

    def codes(self):
        return [a.article_code for a in self.workspace.articles]

    def refresh_filters(self):
        self.workspace.refresh_filters_button.click()
        self.wait_idle()

    def test_options_default_order_population_does_not_request_redundant_list(self):
        with patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            self.show()
            listing.assert_called_once_with()
        combo = self.workspace.category_filter
        self.assertEqual(combo.currentText(), 'All categories')
        self.assertEqual([combo.itemData(i) for i in range(combo.count())], [None, None, 22, 66, 11])
        self.assertEqual(combo.itemText(1), 'Not selected')
        self.assertEqual(self.workspace.refresh_filters_button.text(), 'Refresh filters')
        self.assertEqual(
            self.workspace.refresh_filters_button.accessibleName(),
            'Refresh knowledge filter choices',
        )
        self.assertTrue(
            self.workspace.refresh_filters_button.focusPolicy() & Qt.FocusPolicy.TabFocus
        )
        self.assertTrue(self.workspace.refresh_filters_button.isEnabled())

    def test_manual_refresh_requests_both_sources_once_adds_category_and_preserves_static_modes(self):
        self.show()
        self.workspace.category_filter.setCurrentIndex(1)
        self.wait_idle()
        with database_connection(self.path) as connection:
            connection.execute(
                "INSERT INTO categories (category_id, scope, name, is_active, sort_order, slug, created_at, updated_at) "
                "VALUES (77, 'KNOWLEDGE', 'Fresh category', 1, 5, 'fresh-category', ?, ?)",
                ('2026-09-22T12:00:00Z', '2026-09-22T12:00:00Z'),
            )
        with patch.object(
            self.service, 'list_active_knowledge_categories',
            wraps=self.service.list_active_knowledge_categories,
        ) as categories, patch.object(
            self.service, 'list_available_tags', wraps=self.service.list_available_tags,
        ) as tags, patch.object(
            self.service, 'list_articles', wraps=self.service.list_articles,
        ) as listing:
            self.refresh_filters()
            categories.assert_called_once_with()
            tags.assert_called_once_with()
            listing.assert_not_called()
        self.assertEqual(self.workspace.category_filter.currentText(), 'Not selected')
        self.assertGreaterEqual(self.workspace.category_filter.findData(77), 0)

        self.workspace.category_filter.setCurrentIndex(0)
        self.wait_idle()
        with patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            self.refresh_filters()
            listing.assert_not_called()
        self.assertEqual(self.workspace.category_filter.currentText(), 'All categories')

    def test_manual_refresh_preserves_specific_id_rename_status_and_unsubmitted_input(self):
        self.show()
        self.choose(11)
        self.workspace.status_filter.setCurrentIndex(
            self.workspace.status_filter.findData('DRAFT')
        )
        self.wait_idle()
        self.workspace.search_input.setText('typed but not submitted')
        with database_connection(self.path) as connection:
            connection.execute(
                "UPDATE categories SET name = 'Renamed networking', updated_at = ? "
                "WHERE category_id = 11",
                ('2026-09-22T12:01:00Z',),
            )
        with patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing, \
                patch.object(self.service, 'search_articles', wraps=self.service.search_articles) as search:
            self.refresh_filters()
            listing.assert_not_called()
            search.assert_not_called()
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertEqual(self.workspace.category_filter.currentText(), 'Renamed networking')
        self.assertEqual(self.workspace.status_filter.currentData(), 'DRAFT')
        self.assertEqual(self.workspace.search_input.text(), 'typed but not submitted')

    def test_manual_refresh_deactivated_category_resets_only_category_and_lists_once(self):
        self.show()
        self.choose(11)
        self.workspace.status_filter.setCurrentIndex(
            self.workspace.status_filter.findData('DRAFT')
        )
        self.wait_idle()
        self.workspace.search_input.setText('typed but not submitted')
        with database_connection(self.path) as connection:
            connection.execute(
                "UPDATE categories SET is_active = 0, updated_at = ? WHERE category_id = 11",
                ('2026-09-22T12:02:00Z',),
            )
        with patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            self.refresh_filters()
            listing.assert_called_once_with(status='DRAFT')
        self.assertEqual(self.workspace.category_filter.currentText(), 'All categories')
        self.assertEqual(self.workspace.status_filter.currentData(), 'DRAFT')
        self.assertEqual(self.workspace.tag_filter.currentText(), 'All tags')
        self.assertEqual(self.workspace.search_input.text(), 'typed but not submitted')

    def test_manual_refresh_deleted_category_resets_category_and_lists_once(self):
        self.show()
        self.choose(66)
        with database_connection(self.path) as connection:
            connection.execute('DELETE FROM categories WHERE category_id = 66')
        with patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            self.refresh_filters()
            listing.assert_called_once_with()
        self.assertEqual(self.workspace.category_filter.currentText(), 'All categories')

    def test_manual_refresh_both_completion_orders_block_duplicates_and_close(self):
        self.show()
        original_categories = self.service.list_active_knowledge_categories
        original_tags = self.service.list_available_tags
        for first_source in ('tag', 'category'):
            with self.subTest(first_source=first_source):
                category_gate = threading.Event()
                tag_gate = threading.Event()
                with patch.object(
                    self.service, 'list_active_knowledge_categories',
                    side_effect=lambda: (category_gate.wait(3), original_categories())[1],
                ) as categories, patch.object(
                    self.service, 'list_available_tags',
                    side_effect=lambda: (tag_gate.wait(3), original_tags())[1],
                ) as tags:
                    try:
                        self.workspace.refresh_filters_button.click()
                        deadline = time.monotonic() + 3
                        while (
                            (categories.call_count < 1 or tags.call_count < 1)
                            and time.monotonic() < deadline
                        ):
                            QTest.qWait(10)
                        self.workspace.refresh_filter_options()
                        self.assertTrue(self.workspace.filter_loading)
                        self.assertFalse(self.workspace.refresh_filters_button.isEnabled())
                        self.assertFalse(self.window.close())
                        categories.assert_called_once_with()
                        tags.assert_called_once_with()

                        first_gate = tag_gate if first_source == 'tag' else category_gate
                        first_runner = (
                            self.workspace._tag_filter_runner
                            if first_source == 'tag' else self.workspace._filter_runner
                        )
                        second_runner = (
                            self.workspace._filter_runner
                            if first_source == 'tag' else self.workspace._tag_filter_runner
                        )
                        first_gate.set()
                        deadline = time.monotonic() + 3
                        while first_runner.busy and time.monotonic() < deadline:
                            QTest.qWait(10)
                        self.assertFalse(first_runner.busy)
                        self.assertTrue(second_runner.busy)
                        self.assertFalse(self.workspace.refresh_filters_button.isEnabled())
                    finally:
                        category_gate.set()
                        tag_gate.set()
                    self.wait_idle()
                self.assertTrue(self.workspace.refresh_filters_button.isEnabled())

    def test_manual_category_failure_retains_cache_while_tag_succeeds_and_retry_works(self):
        self.show()
        self.choose(11)
        cached = [
            (self.workspace.category_filter.itemText(index),
             self.workspace.category_filter.itemData(index))
            for index in range(self.workspace.category_filter.count())
        ]
        with database_connection(self.path) as connection:
            connection.execute(
                "INSERT INTO tags (tag_id, name, slug, created_at) VALUES (77, 'Fresh tag', 'fresh-tag', ?)",
                ('2026-09-22T12:03:00Z',),
            )
        with patch.object(
            self.service, 'list_active_knowledge_categories',
            side_effect=RuntimeError('private category failure'),
        ), patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            self.refresh_filters()
            listing.assert_not_called()
        self.assertEqual(
            [(self.workspace.category_filter.itemText(index),
              self.workspace.category_filter.itemData(index))
             for index in range(self.workspace.category_filter.count())],
            cached,
        )
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertIn(
            ('tag', 77),
            [self.workspace.tag_filter.itemData(index)
             for index in range(self.workspace.tag_filter.count())],
        )
        self.assertNotIn('private category failure', self.workspace.filter_feedback.text())
        self.assertIn('retained', self.workspace.filter_feedback.text())

        self.refresh_filters()
        self.assertFalse(self.workspace.filter_feedback.isVisible())
        self.assertEqual(self.workspace.category_filter.currentData(), 11)

    def test_filter_one_async_call_busy_state_and_detail_reconciliation(self):
        self.show()
        gate = threading.Event()
        threads = []
        original = self.service.list_articles
        def listing(**kw):
            threads.append(threading.get_ident())
            gate.wait(3)
            return original(**kw)
        with patch.object(self.service, 'list_articles', side_effect=listing) as call:
            try:
                self.workspace.category_filter.setCurrentIndex(self.workspace.category_filter.findData(11))
                self.assertTrue(self.window.runner.busy)
                self.assertFalse(self.workspace.category_filter.isEnabled())
                self.assertIsNone(self.workspace.article)
                self.assertEqual(self.workspace.model.rowCount(), 0)
                self.workspace.refresh_list()
            finally:
                gate.set()
            self.wait_idle()
            call.assert_called_once_with(category_id=11)
        self.assertNotEqual(threads, [threading.get_ident()])
        self.assertEqual(self.codes(), ['A1'])
        self.assertEqual(self.workspace.article, self.rows[0])

    def test_search_filter_change_uses_executed_query_and_clear_preserves_filter(self):
        self.show()
        self.choose(11)
        self.workspace.search_input.setText('DNS')
        self.workspace.search_articles()
        self.wait_idle()
        self.assertEqual(self.codes(), ['A1'])
        self.workspace.search_input.setText('unsubmitted text')
        with patch.object(self.service, 'search_articles', wraps=self.service.search_articles) as search:
            self.choose(None)
            search.assert_called_once_with('DNS', uncategorized_only=True)
        self.assertEqual(self.codes(), ['A3'])
        self.workspace.clear_search_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentText(), 'Not selected')
        self.assertEqual(self.workspace.search_input.text(), '')
        self.assertFalse(self.workspace._search_active)
        self.assertEqual(self.codes(), ['A3'])

    def test_options_load_does_not_block_article_list_and_close_is_guarded(self):
        gate = threading.Event()
        original = self.service.list_active_knowledge_categories
        with patch.object(self.service, 'list_active_knowledge_categories', side_effect=lambda: (gate.wait(3), original())[1]):
            try:
                self.window.show_knowledge()
                self.wait_idle(references=False)
                self.assertEqual(len(self.codes()), 3)
                self.assertTrue(self.workspace.table.isEnabled())
                self.assertTrue(self.workspace.search_button.isEnabled())
                self.assertFalse(self.workspace.category_filter.isEnabled())
                self.assertFalse(self.window.close())
                self.workspace.search_input.setText('DNS')
                self.workspace.search_articles()
                self.wait_idle(references=False)
                self.assertEqual(len(self.codes()), 3)
            finally:
                gate.set()
            self.wait_idle()

    def test_option_failure_keeps_all_list_search_and_retry(self):
        with patch.object(self.service, 'list_active_knowledge_categories', side_effect=RuntimeError('private')):
            self.show()
        self.assertEqual(len(self.codes()), 3)
        self.assertIsNotNone(self.workspace.article)
        self.assertEqual(self.workspace.category_filter.currentIndex(), 0)
        self.assertTrue(self.workspace.category_filter.isEnabled())
        self.assertTrue(self.workspace.tag_filter.isEnabled())
        self.assertGreaterEqual(self.workspace.tag_filter.count(), 2)
        self.assertNotIn('private', self.workspace.filter_feedback.text())
        self.workspace.search_input.setText('DNS')
        self.workspace.search_articles()
        self.wait_idle()
        self.assertEqual(len(self.codes()), 3)
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertTrue(self.workspace.category_filter.isEnabled())
        self.assertFalse(self.workspace.filter_feedback.isVisible())
        self.assertEqual(self.workspace.category_filter.count(), 5)

    def test_filtered_list_and_search_failures_clear_rows_and_all_details(self):
        self.show()
        with patch.object(self.service, 'list_articles', side_effect=RuntimeError('private')):
            self.choose(11)
        self.assertEqual(self.codes(), [])
        self.assertIsNone(self.workspace.article)
        self.assertEqual(self.workspace.detail_category.text(), '')
        self.assertNotIn('private', self.workspace.feedback.text())
        self.workspace.refresh_list()
        self.wait_idle()
        self.workspace.search_input.setText('DNS')
        self.workspace.search_articles()
        self.wait_idle()
        with patch.object(self.service, 'search_articles', side_effect=RuntimeError('private')):
            self.choose(22)
        self.assertEqual(self.codes(), [])
        self.assertEqual(self.workspace.detail_body.toPlainText(), '')
        self.assertEqual(self.workspace.detail_title.text(), '')
        self.assertEqual(self.workspace.detail_category.text(), '')
        self.assertEqual(self.workspace.search_input.text(), 'DNS')

    def test_empty_states_and_selection_preserved_if_still_matching(self):
        self.show()
        self.workspace.table.selectRow(next(i for i,a in enumerate(self.workspace.articles) if a.article_code == 'A1'))
        self.wait_idle()
        self.choose(11)
        self.assertEqual(self.workspace.article.article_code, 'A1')
        self.choose(66)
        self.assertIn('in this category', self.workspace.empty_state.text())
        self.assertIsNone(self.workspace.article)
        uncategorized = self.rows[2]
        self.service.set_article_category(uncategorized.knowledge_article_id, 1, uncategorized.updated_at, 11)
        self.choose(None)
        self.assertIn('uncategorized', self.workspace.empty_state.text())
        self.assertIsNone(self.workspace.article)

    def test_category_dialog_mutation_reconciles_list_and_search(self):
        self.show()
        for search_mode in (False, True):
            article = self.service.get_article(self.rows[0].knowledge_article_id)
            if article.category_id != 11:
                self.service.set_article_category(article.knowledge_article_id, article.version_number, article.updated_at, 11)
            self.choose(11)
            self.workspace.refresh_list()
            self.wait_idle()
            if search_mode:
                self.workspace.search_input.setText('DNS')
                self.workspace.search_articles()
                self.wait_idle()
            dialog = self.workspace.open_category()
            self.wait_idle()
            dialog.category_input.setCurrentIndex(dialog.category_input.findData(22))
            dialog.save_button.click()
            self.wait_idle()
            self.assertEqual(self.workspace.category_filter.currentData(), 11)
            self.assertEqual(self.codes(), [])
            self.assertIsNone(self.workspace.article)
            self.assertNotIn('no longer exists', self.workspace.feedback.text())
            self.assertEqual(self.workspace._search_active, search_mode)

    def test_new_article_reveals_under_all_and_layout_fits(self):
        self.show()
        self.choose(11)
        dialog = self.workspace.open_new_article()
        dialog.code_input.setText('NEW')
        dialog.title_input.setText('New DNS')
        dialog.body_input.setPlainText('DNS')
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentIndex(), 0)
        self.assertEqual(self.workspace.article.article_code, 'NEW')
        self.assertNotIn('no longer exists', self.workspace.feedback.text())
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        for control in (self.workspace.category_filter, self.workspace.search_input,
                self.workspace.search_button, self.workspace.clear_search_button):
            self.assertTrue(control.isVisible())
            self.assertTrue(self.workspace.rect().contains(control.geometry()))
