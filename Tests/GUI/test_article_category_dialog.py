"""Category modal behavior in the actual MainWindow ownership hierarchy."""

from dataclasses import replace
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
from f7hub.services.knowledge_service import KnowledgeCategoryConflictError
from Tests.Database.test_knowledge_categories import seed_knowledge_categories


class ArticleCategoryDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'category-ui.db'
        self.context = bootstrap_application(database_path=self.path)
        seed_knowledge_categories(self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.wait_idle()
        self.service = self.context.knowledge_service
        self.article = self.service.create_article(article_code='KB-UI', title='Synthetic article', summary=None, body='Body')
        self.window.show_knowledge()
        self.wait_idle()
        self.workspace = self.window.knowledge_workspace

    def tearDown(self):
        self.wait_idle()
        if self.workspace._category_dialog is not None:
            self.workspace._category_dialog.reject()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def wait_idle(self):
        deadline = time.monotonic() + 8
        settled = 0
        while time.monotonic() < deadline and settled < 3:
            self.app.processEvents()
            QTest.qWait(5)
            settled = 0 if self.window.runner.busy else settled + 1
        self.assertFalse(self.window.runner.busy)

    def open_dialog(self):
        dialog = self.workspace.open_category()
        self.assertIsNotNone(dialog)
        self.wait_idle()
        return dialog

    def test_action_state_and_service_availability(self):
        self.assertTrue(self.workspace.category_button.isEnabled())
        for status in ('PUBLISHED', 'ARCHIVED'):
            self.workspace._show_article(replace(self.article, status=status))
            self.assertFalse(self.workspace.category_button.isEnabled())
            self.assertIsNone(self.workspace.open_category())
        self.workspace._show_article(None)
        self.assertFalse(self.workspace.category_button.isEnabled())
        self.workspace._show_article(self.article)
        self.workspace._service = None
        self.workspace._update_actions(False)
        self.assertFalse(self.workspace.category_button.isEnabled())

    def test_choices_are_active_knowledge_and_cancel_does_not_write_or_refresh(self):
        with patch.object(self.service, 'set_article_category', wraps=self.service.set_article_category) as write:
            dialog = self.open_dialog()
            self.assertEqual([dialog.category_input.itemData(i) for i in range(dialog.category_input.count())], [None, 22, 66, 11])
            self.assertEqual(dialog.category_input.itemText(0), 'Not selected')
            self.assertEqual(dialog.category_input.currentIndex(), 0)
            with patch.object(self.workspace, 'refresh_list') as refresh:
                QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
                refresh.assert_not_called()
            write.assert_not_called()
        self.assertEqual(self.service.get_article(self.article.knowledge_article_id), self.article)

    def test_assign_change_remove_are_one_async_call_each_and_show_authoritative_record(self):
        for category_id, label in ((11, 'Networking'), (22, 'Microsoft 365'), (None, 'Not selected')):
            before = self.workspace.article
            dialog = self.open_dialog()
            self.assertEqual(dialog.category_input.currentData(), before.category_id)
            dialog.category_input.setCurrentIndex(dialog.category_input.findData(category_id))
            threads = []
            original = self.service.set_article_category
            def save(*args):
                threads.append(threading.get_ident())
                return original(*args)
            with patch.object(self.service, 'set_article_category', side_effect=save) as write:
                dialog.submit()
                dialog.submit()
                self.wait_idle()
                write.assert_called_once_with(before.knowledge_article_id, before.version_number, before.updated_at, category_id)
            self.assertNotEqual(threads, [threading.get_ident()])
            self.assertEqual(self.workspace.article, self.service.get_article(before.knowledge_article_id))
            self.assertEqual(self.workspace.detail_category.text(), f'Category: {label}')
            self.assertEqual(self.workspace.article.version_number, before.version_number)

    def test_reference_failure_keeps_article_readable_and_can_retry(self):
        before = self.workspace.article
        with patch.object(self.service, 'list_active_knowledge_categories', side_effect=RuntimeError('private')):
            dialog = self.open_dialog()
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertNotIn('private', dialog.feedback.text())
        self.assertIs(self.workspace.article, before)
        self.assertEqual(self.workspace.detail_body.toPlainText(), before.body_markdown)
        dialog.load_categories()
        self.wait_idle()
        self.assertTrue(dialog.save_button.isEnabled())
        dialog.reject()
        self.assertTrue(self.workspace.edit_button.isEnabled())

    def test_cancel_and_escape_remain_enabled_during_reference_read(self):
        for escape in (False, True):
            gate = threading.Event()
            self.addCleanup(gate.set)
            threads = []
            def read():
                threads.append(threading.get_ident())
                gate.wait(3)
                return ()
            with patch.object(self.service, 'list_active_knowledge_categories', side_effect=read), patch.object(self.service, 'set_article_category') as write:
                dialog = self.workspace.open_category()
                self.app.processEvents()
                self.assertIs(dialog.parent(), self.window)
                self.assertFalse(self.window.pages.isEnabled())
                self.assertTrue(dialog.cancel_button.isEnabled())
                if escape:
                    QTest.keyClick(dialog, Qt.Key.Key_Escape)
                else:
                    QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
                self.assertFalse(dialog.isVisible())
                gate.set()
                self.wait_idle()
                self.assertEqual(dialog.category_input.count(), 0)
                write.assert_not_called()
            self.assertNotEqual(threads, [threading.get_ident()])

    def test_write_busy_blocks_cancel_duplicate_and_competing_actions(self):
        dialog = self.open_dialog()
        dialog.category_input.setCurrentIndex(dialog.category_input.findData(11))
        gate = threading.Event()
        self.addCleanup(gate.set)
        original = self.service.set_article_category
        def save(*args):
            gate.wait(3)
            return original(*args)
        with patch.object(self.service, 'set_article_category', side_effect=save) as write:
            dialog.submit()
            self.app.processEvents()
            for control in (self.workspace.category_button, self.workspace.edit_button, self.workspace.publish_button,
                            self.workspace.version_history_button, self.workspace.search_button, dialog.save_button, dialog.cancel_button):
                self.assertFalse(control.isEnabled())
            self.assertFalse(self.window.pages.isEnabled())
            self.assertFalse(self.window.tickets_action.isEnabled())
            QTest.keyClick(dialog, Qt.Key.Key_Escape)
            dialog.close()
            dialog.submit()
            self.assertTrue(dialog.isVisible())
            self.assertEqual(self.workspace.article, self.article)
            gate.set()
            self.wait_idle()
            write.assert_called_once()

    def test_failure_preserves_truthful_state_and_retry(self):
        dialog = self.open_dialog()
        dialog.category_input.setCurrentIndex(dialog.category_input.findData(11))
        with patch.object(self.service, 'set_article_category', side_effect=RuntimeError('private SQLite')):
            dialog.submit()
            self.wait_idle()
        self.assertEqual(self.workspace.article, self.article)
        self.assertEqual(self.workspace.detail_category.text(), 'Category: Not selected')
        self.assertNotIn('private', dialog.feedback.text())
        self.assertTrue(dialog.save_button.isEnabled())
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.article.category_id, 11)

    def test_stale_failure_requires_reopen_and_changed_context_cannot_submit(self):
        dialog = self.open_dialog()
        with patch.object(self.service, 'set_article_category', side_effect=KnowledgeCategoryConflictError('Reopen the latest article.')):
            dialog.submit()
            self.wait_idle()
        self.assertIn('Reopen', dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        dialog.reject()
        dialog = self.open_dialog()
        self.workspace._show_article(replace(self.article, updated_at='changed'))
        with patch.object(self.service, 'set_article_category') as write:
            dialog.submit()
            write.assert_not_called()
        self.assertFalse(dialog.save_button.isEnabled())

    def test_inactive_current_is_shown_as_plaintext_but_not_selectable(self):
        self.service.set_article_category(self.article.knowledge_article_id, 1, self.article.updated_at, 11)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE categories SET is_active = 0, name = '<b>Legacy</b>' WHERE category_id = 11")
        self.workspace.refresh_list()
        self.wait_idle()
        dialog = self.open_dialog()
        self.assertIn('<b>Legacy</b>', dialog.current_label.text())
        self.assertEqual(dialog.current_label.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(dialog.category_input.findData(11), -1)
        self.assertIn('no longer selectable', dialog.feedback.text())
        dialog.submit()
        self.wait_idle()
        self.assertIsNone(self.workspace.article.category_id)
