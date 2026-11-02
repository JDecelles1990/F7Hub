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
        original_settled = self.workspace._manual_filter_source_settled
        for first_source in ('tag', 'category'):
            with self.subTest(first_source=first_source):
                category_gate = threading.Event()
                tag_gate = threading.Event()
                observations = []

                def settled(source, **kwargs):
                    original_settled(source, **kwargs)
                    runner = (self.workspace._filter_runner if source == 'category'
                              else self.workspace._tag_filter_runner)
                    observations.append((source, runner.completing,
                                         self.workspace._manual_filter_refresh_active,
                                         self.workspace.refresh_filters_button.isEnabled(),
                                         self.workspace.category_filter.isEnabled(),
                                         self.workspace.tag_filter.isEnabled()))
                    # Reentrant activation while the final callback is on the stack.
                    self.workspace.refresh_filter_options()
                    self.workspace.refresh_filters_button.click()

                with patch.object(
                    self.service, 'list_active_knowledge_categories',
                    side_effect=lambda: (category_gate.wait(3), original_categories())[1],
                ) as categories, patch.object(
                    self.service, 'list_available_tags',
                    side_effect=lambda: (tag_gate.wait(3), original_tags())[1],
                ) as tags, patch.object(
                    self.workspace, '_manual_filter_source_settled', side_effect=settled,
                ), patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
                    try:
                        self.assertTrue(self.workspace.refresh_filters_button.isEnabled())
                        self.workspace.refresh_filters_button.click()
                        deadline = time.monotonic() + 3
                        while ((categories.call_count < 1 or tags.call_count < 1)
                               and time.monotonic() < deadline):
                            QTest.qWait(10)
                        self.workspace.refresh_filter_options()
                        self.assertTrue(self.workspace.filter_loading)
                        self.assertFalse(self.workspace.refresh_filters_button.isEnabled())
                        self.assertFalse(self.window.close())
                        categories.assert_called_once_with()
                        tags.assert_called_once_with()
                        first_gate = tag_gate if first_source == 'tag' else category_gate
                        first_runner = (self.workspace._tag_filter_runner if first_source == 'tag'
                                        else self.workspace._filter_runner)
                        second_runner = (self.workspace._filter_runner if first_source == 'tag'
                                         else self.workspace._tag_filter_runner)
                        first_gate.set()
                        deadline = time.monotonic() + 3
                        while (first_runner.busy or first_runner.completing) and time.monotonic() < deadline:
                            QTest.qWait(10)
                        self.assertFalse(first_runner.busy or first_runner.completing)
                        self.assertTrue(second_runner.busy)
                        self.assertTrue(self.workspace._manual_filter_refresh_active)
                        self.assertFalse(self.workspace.refresh_filters_button.isEnabled())
                        listing.assert_not_called()
                    finally:
                        category_gate.set()
                        tag_gate.set()
                    self.wait_idle()
                    categories.assert_called_once_with()
                    tags.assert_called_once_with()
                    listing.assert_not_called()
                self.assertEqual([row[0] for row in observations],
                                 [first_source, 'category' if first_source == 'tag' else 'tag'])
                self.assertEqual([row[1:] for row in observations],
                                 [(True, True, False, False, False)] * 2)
                self.assertFalse(self.workspace._manual_filter_refresh_active)
                self.assertEqual(self.workspace._manual_filter_refresh_pending, set())
                self.assertTrue(self.workspace.refresh_filters_button.isEnabled())
                self.assertTrue(self.workspace.category_filter.isEnabled())
                self.assertTrue(self.workspace.tag_filter.isEnabled())

    def test_initial_reference_callbacks_keep_own_selector_disabled_until_completion(self):
        self.show()
        for fails in (False, True):
            with self.subTest(fails=fails):
                observations = []
                names = ('_filter_options_failed', '_tag_filter_options_failed') if fails else (
                    '_filter_options_succeeded', '_tag_filter_options_succeeded')

                def observe(callback, runner, combo):
                    def completed(result):
                        callback(result)
                        observations.append((runner.completing, combo.isEnabled()))
                    return completed

                category_callback = getattr(self.workspace, names[0])
                tag_callback = getattr(self.workspace, names[1])
                category_work = self.service.list_active_knowledge_categories
                tag_work = self.service.list_available_tags
                self.workspace._filter_options_loaded = False
                self.workspace._tag_filter_options_loaded = False
                with patch.object(self.workspace, names[0], side_effect=observe(
                    category_callback, self.workspace._filter_runner, self.workspace.category_filter,
                )), patch.object(self.workspace, names[1], side_effect=observe(
                    tag_callback, self.workspace._tag_filter_runner, self.workspace.tag_filter,
                )), patch.object(self.service, 'list_active_knowledge_categories',
                                 side_effect=RuntimeError('private category') if fails else category_work), \
                        patch.object(self.service, 'list_available_tags',
                                     side_effect=RuntimeError('private tag') if fails else tag_work):
                    self.workspace._load_filter_options()
                    self.wait_idle()
                self.assertEqual(observations, [(True, False), (True, False)])
                self.assertTrue(self.workspace.category_filter.isEnabled())
                self.assertTrue(self.workspace.tag_filter.isEnabled())
                self.assertTrue(self.workspace.refresh_filters_button.isEnabled())

    def test_manual_reset_waits_for_shared_runner_and_preserves_navigation_and_input(self):
        self.show()
        self.choose(11)
        selected_id = self.workspace.article.knowledge_article_id
        self.workspace.search_input.setText('unsubmitted input')
        with database_connection(self.path) as connection:
            connection.execute('UPDATE categories SET is_active = 0 WHERE category_id = 11')
        reference_gate = threading.Event()
        ticket_gate = threading.Event()
        original_categories = self.service.list_active_knowledge_categories
        original_tags = self.service.list_available_tags
        original_tickets = self.context.ticket_service.list_tickets
        with patch.object(self.service, 'list_active_knowledge_categories',
                          side_effect=lambda: (reference_gate.wait(5), original_categories())[1]), \
                patch.object(self.service, 'list_available_tags',
                             side_effect=lambda: (reference_gate.wait(5), original_tags())[1]), \
                patch.object(self.context.ticket_service, 'list_tickets',
                             side_effect=lambda **kwargs: (ticket_gate.wait(5), original_tickets(**kwargs))[1]), \
                patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            try:
                self.workspace.refresh_filters_button.click()
                self.window.show_tickets()
                self.assertTrue(self.window.runner.busy)
                reference_gate.set()
                deadline = time.monotonic() + 4
                while self.workspace.filter_loading and time.monotonic() < deadline:
                    QTest.qWait(10)
                self.assertFalse(self.workspace.filter_loading)
                self.assertFalse(self.workspace._manual_filter_refresh_active)
                self.assertTrue(self.workspace._articles_refresh_required)
                self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
                listing.assert_not_called()
                self.assertEqual(self.workspace.search_input.text(), 'unsubmitted input')
            finally:
                reference_gate.set()
                ticket_gate.set()
            self.wait_idle()
            listing.assert_called_once_with()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertFalse(self.workspace._articles_refresh_required)
        self.assertEqual(self.workspace.article.knowledge_article_id, selected_id)
        self.assertEqual(self.workspace.search_input.text(), 'unsubmitted input')

    def test_manual_reset_defers_while_articles_tab_is_inactive(self):
        from PySide6.QtWidgets import QWidget

        self.show()
        self.choose(11)
        self.workspace.search_input.setText('retained draft query')
        with database_connection(self.path) as connection:
            connection.execute('UPDATE categories SET is_active = 0 WHERE category_id = 11')
        reference_gate = threading.Event()
        original_categories = self.service.list_active_knowledge_categories
        original_tags = self.service.list_available_tags
        retained_tab = QWidget(self.workspace.knowledge_tabs)
        self.workspace.knowledge_tabs.addTab(retained_tab, 'Retained context')
        with patch.object(self.service, 'list_active_knowledge_categories',
                          side_effect=lambda: (reference_gate.wait(5), original_categories())[1]), \
                patch.object(self.service, 'list_available_tags',
                             side_effect=lambda: (reference_gate.wait(5), original_tags())[1]), \
                patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing:
            try:
                self.workspace.refresh_filters_button.click()
                self.workspace.knowledge_tabs.setCurrentWidget(retained_tab)
            finally:
                reference_gate.set()
            self.wait_idle()
            self.assertIs(self.workspace.knowledge_tabs.currentWidget(), retained_tab)
            self.assertTrue(self.workspace._articles_refresh_required)
            self.assertFalse(self.workspace.refresh_filters_button.isEnabled())
            self.assertFalse(self.workspace.category_filter.isEnabled())
            self.assertFalse(self.workspace.tag_filter.isEnabled())
            listing.assert_not_called()
            self.workspace.knowledge_tabs.setCurrentWidget(self.workspace.articles_tab)
            self.wait_idle()
            listing.assert_called_once_with()
        self.assertEqual(self.workspace.search_input.text(), 'retained draft query')
        self.assertFalse(self.workspace._articles_refresh_required)

    def _assert_r1_deferred_manual_refresh(
        self, failed_source, first_source, defer_mode, *, search=False, supersede=None,
    ):
        from PySide6.QtWidgets import QWidget

        w = self.workspace
        with database_connection(self.path) as connection:
            connection.executemany(
                "INSERT INTO tags(tag_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
                ((11, 'VPN', 'r1-vpn', '2026-11-02T12:00:00Z'),
                 (22, 'Windows', 'r1-windows', '2026-11-02T12:00:00Z')),
            )
        article = self.rows[0]
        self.rows[0] = self.service.set_article_tags(
            article.knowledge_article_id, article.version_number, article.updated_at, (11,),
        )
        methods = {'category': 'list_active_knowledge_categories', 'tag': 'list_available_tags'}
        originals = {source: getattr(self.service, name) for source, name in methods.items()}
        with patch.object(self.service, methods[failed_source], side_effect=RuntimeError('private initial')):
            self.show()
            if failed_source == 'tag':
                self.choose(11)
            else:
                index = next(i for i in range(w.tag_filter.count())
                             if w.tag_filter.itemData(i) == ('tag', 11))
                w.tag_filter.setCurrentIndex(index)
                self.wait_idle()
            if search:
                w.search_articles(query='DNS')
                self.wait_idle()
        self.assertFalse(w._tag_filter_options_loaded if failed_source == 'tag'
                         else w._filter_options_loaded)
        selected_id = w.article.knowledge_article_id
        w.search_input.setText('newer unsubmitted R1 input')
        with database_connection(self.path) as connection:
            if failed_source == 'tag':
                connection.execute('UPDATE categories SET is_active=0 WHERE category_id=11')
            else:
                connection.execute('DELETE FROM tags WHERE tag_id=11')
            before = tuple(connection.iterdump())

        gates = {source: threading.Event() for source in methods}
        shared_gate = threading.Event()
        reads = {source: 0 for source in methods}
        callback_errors, completing_observations, dispatch_observations = [], [], []
        record_dispatch = [False]
        retained_tab = QWidget(w.knowledge_tabs)
        w.knowledge_tabs.addTab(retained_tab, 'Retained R1 context')
        feedback = w.tag_filter_feedback if failed_source == 'tag' else w.filter_feedback

        def wait_for(predicate):
            deadline = time.monotonic() + 5
            while not predicate() and time.monotonic() < deadline:
                QTest.qWait(10)
            self.assertTrue(predicate(), 'bounded R1 condition did not settle')

        def reference_read(source):
            reads[source] += 1
            if not gates[source].wait(6):
                raise RuntimeError('R1 test reference gate timeout')
            if source == failed_source and reads[source] == 1:
                raise RuntimeError('private manual failure')
            return originals[source]()

        def drain_references():
            first = w._filter_runner if first_source == 'category' else w._tag_filter_runner
            second_source = 'tag' if first_source == 'category' else 'category'
            second = w._tag_filter_runner if second_source == 'tag' else w._filter_runner
            gates[first_source].set()
            wait_for(lambda: not first.busy and not first.completing)
            self.assertTrue(second.busy)
            self.assertTrue(w._manual_filter_refresh_active)
            gates[second_source].set()
            wait_for(lambda: not w.filter_loading)

        def during_shared_completion(_result):
            try:
                drain_references()
                completing_observations.append((self.window.runner.completing,
                                                w._articles_refresh_required,
                                                w._articles_refresh_load_filter_options))
                w._reconcile_articles()
                record_dispatch[0] = True
            except Exception as error:
                callback_errors.append(str(error))
            finally:
                for gate in gates.values():
                    gate.set()

        def reentrant_action_update(busy):
            if busy and record_dispatch[0]:
                dispatch_observations.append((w._articles_refresh_required,
                                              w._articles_refresh_load_filter_options))
                w._reconcile_articles()

        self.window.runner.busy_changed.connect(reentrant_action_update)
        try:
            with patch.object(self.service, methods['category'],
                              side_effect=lambda: reference_read('category')) as categories, \
                    patch.object(self.service, methods['tag'],
                                 side_effect=lambda: reference_read('tag')) as tags, \
                    patch.object(self.service, 'list_articles', wraps=self.service.list_articles) as listing, \
                    patch.object(self.service, 'search_articles', wraps=self.service.search_articles) as searching:
                try:
                    w.refresh_filters_button.click()
                    if defer_mode == 'inactive':
                        w.knowledge_tabs.setCurrentWidget(retained_tab)
                        drain_references()
                    elif defer_mode == 'busy':
                        self.window.runner.submit(lambda: shared_gate.wait(6), lambda _result: None,
                                                  lambda error: callback_errors.append(str(error)))
                        drain_references()
                    else:
                        self.window.runner.submit(lambda: None, during_shared_completion,
                                                  lambda error: callback_errors.append(str(error)))
                        self.wait_idle()
                        self.assertEqual(completing_observations, [(True, True, False)])
                    self.assertEqual(callback_errors, [])
                    categories.assert_called_once_with()
                    tags.assert_called_once_with()
                    if defer_mode != 'completing':
                        self.assertTrue(w._articles_refresh_required)
                        self.assertEqual(w._articles_refresh_pending, selected_id)
                        self.assertFalse(w._articles_refresh_load_filter_options)
                        self.assertFalse(w._manual_filter_refresh_active)
                        listing.assert_not_called()
                        searching.assert_not_called()
                    record_dispatch[0] = True
                    expected_id = selected_id
                    if supersede == 'filter':
                        w._filter_changed(0)
                        self.assertTrue(w._articles_refresh_load_filter_options)
                    elif supersede == 'created':
                        created = self.service.get_article(self.rows[1].knowledge_article_id)
                        expected_id = created.knowledge_article_id
                        w._article_created(created)
                        self.assertTrue(w._articles_refresh_load_filter_options)
                        self.assertEqual(w._articles_refresh_pending, expected_id)
                    if supersede == 'reveal':
                        expected_id = self.rows[1].knowledge_article_id
                        w.open_article_by_id(expected_id)
                    elif defer_mode == 'inactive':
                        w.knowledge_tabs.setCurrentWidget(w.articles_tab)
                    elif defer_mode == 'busy':
                        shared_gate.set()
                    self.wait_idle()
                finally:
                    shared_gate.set()
                    for gate in gates.values():
                        gate.set()
                self.assertEqual(callback_errors, [])
                self.assertEqual(categories.call_count, 1)
                self.assertEqual(tags.call_count, 2 if supersede else 1)
                self.assertEqual(listing.call_count, 0 if search else 1)
                self.assertEqual(searching.call_count, 1 if search else 0)
                self.assertEqual(w.article.knowledge_article_id, expected_id)
                self.assertFalse(w._articles_refresh_required)
                self.assertIsNone(w._articles_refresh_pending)
                self.assertTrue(w._articles_refresh_load_filter_options)
                self.assertTrue(dispatch_observations)
                self.assertTrue(all(row == (False, True) for row in dispatch_observations))
                if supersede != 'reveal':
                    self.assertEqual(w.search_input.text(), 'newer unsubmitted R1 input')
                if search:
                    self.assertTrue(w._search_active)
                    self.assertEqual(w._search_query, 'DNS')
                if not supersede:
                    self.assertTrue(feedback.isVisible())
                    self.assertIn('retained', feedback.text())
                    self.assertNotIn('private', feedback.text())
                w._reconcile_articles()
                w._filter_runner.completion_finished.emit()
                w._tag_filter_runner.completion_finished.emit()
                self.wait_idle()
                self.assertEqual(listing.call_count + searching.call_count, 1)
                previous_categories, previous_tags = categories.call_count, tags.call_count
                self.assertTrue(w.refresh_filters_button.isEnabled())
                w.refresh_filters_button.click()
                self.wait_idle()
                self.assertEqual(categories.call_count, previous_categories + 1)
                self.assertEqual(tags.call_count, previous_tags + 1)
                self.assertEqual(listing.call_count + searching.call_count, 1)
                self.assertFalse(feedback.isVisible())
                self.assertTrue(w.refresh_filters_button.isEnabled())
        finally:
            shared_gate.set()
            for gate in gates.values():
                gate.set()
            self.window.runner.busy_changed.disconnect(reentrant_action_update)
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_r1_tag_failure_inactive_category_first(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'inactive')

    def test_r1_tag_failure_inactive_tag_first(self):
        self._assert_r1_deferred_manual_refresh('tag', 'tag', 'inactive')

    def test_r1_category_failure_inactive_category_first(self):
        self._assert_r1_deferred_manual_refresh('category', 'category', 'inactive')

    def test_r1_category_failure_inactive_tag_first(self):
        self._assert_r1_deferred_manual_refresh('category', 'tag', 'inactive')

    def test_r1_tag_failure_shared_busy_category_first(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'busy')

    def test_r1_tag_failure_shared_busy_tag_first(self):
        self._assert_r1_deferred_manual_refresh('tag', 'tag', 'busy')

    def test_r1_category_failure_shared_busy_category_first(self):
        self._assert_r1_deferred_manual_refresh('category', 'category', 'busy')

    def test_r1_category_failure_shared_busy_tag_first(self):
        self._assert_r1_deferred_manual_refresh('category', 'tag', 'busy')

    def test_r1_tag_failure_shared_completing(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'completing')

    def test_r1_category_failure_shared_completing(self):
        self._assert_r1_deferred_manual_refresh('category', 'tag', 'completing')

    def test_r1_search_state_and_selection_survive_deferred_reset(self):
        self._assert_r1_deferred_manual_refresh('tag', 'tag', 'inactive', search=True)

    def test_r1_ordinary_filter_request_supersedes_manual_option(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'inactive', supersede='filter')

    def test_r1_article_created_request_supersedes_manual_option(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'inactive', supersede='created')

    def test_r1_explicit_reveal_clears_manual_option_and_selection(self):
        self._assert_r1_deferred_manual_refresh('tag', 'category', 'inactive', supersede='reveal')

    def test_r1_ordinary_refresh_preserves_initial_reference_retry(self):
        with patch.object(self.service, 'list_available_tags', side_effect=RuntimeError('private initial')):
            self.show()
        self.assertFalse(self.workspace._tag_filter_options_loaded)
        self.assertTrue(self.workspace.tag_filter_feedback.isVisible())
        with patch.object(self.service, 'list_available_tags',
                          wraps=self.service.list_available_tags) as tags:
            self.workspace.refresh_list()
            self.wait_idle()
            tags.assert_called_once_with()
        self.assertTrue(self.workspace._tag_filter_options_loaded)
        self.assertFalse(self.workspace.tag_filter_feedback.isVisible())
        self.assertTrue(self.workspace._articles_refresh_load_filter_options)

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
