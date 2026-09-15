"""Status filter behavior in the real Knowledge workspace hierarchy."""

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from Tests.Database.test_knowledge_categories import seed_knowledge_categories


class KnowledgeStatusFilterGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "status-filter-ui.db"
        self.context = bootstrap_application(database_path=self.path)
        seed_knowledge_categories(self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.workspace = self.window.knowledge_workspace
        self.service = self.context.knowledge_service
        self.wait_idle()
        self.rows = {}
        for code, category_id, status in (
            ("A", 11, "DRAFT"),
            ("B", 11, "PUBLISHED"),
            ("C", 22, "PUBLISHED"),
            ("D", None, "ARCHIVED"),
        ):
            article = self.service.create_article(
                article_code=code, title="DNS status", summary=None, body="DNS steps"
            )
            if category_id is not None:
                article = self.service.set_article_category(
                    article.knowledge_article_id, article.version_number,
                    article.updated_at, category_id,
                )
            if status != "DRAFT":
                with database_connection(self.path) as connection:
                    connection.execute(
                        "UPDATE knowledge_articles SET status = ?, published_at = ? "
                        "WHERE knowledge_article_id = ?",
                        (status, "2026-09-15T12:00:00.000Z",
                         article.knowledge_article_id),
                    )
                article = self.service.get_article(article.knowledge_article_id)
            self.rows[code] = article

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
        while (self.window.runner.busy or
               (references and self.workspace.filter_loading)) and time.monotonic() < deadline:
            QTest.qWait(10)
        self.app.processEvents()
        self.assertFalse(self.window.runner.busy)
        if references:
            self.assertFalse(self.workspace.filter_loading)

    def show(self):
        self.window.show_knowledge()
        self.wait_idle()

    def choose_category(self, category_id):
        index = (0 if category_id == "ALL" else 1 if category_id is None
                 else self.workspace.category_filter.findData(category_id))
        self.workspace.category_filter.setCurrentIndex(index)
        self.wait_idle()

    def choose_status(self, status):
        self.workspace.status_filter.setCurrentIndex(
            0 if status is None else self.workspace.status_filter.findData(status)
        )
        self.wait_idle()

    def codes(self):
        return [article.article_code for article in self.workspace.articles]

    def test_static_options_default_accessibility_and_1000x700_layout(self):
        self.show()
        combo = self.workspace.status_filter
        self.assertEqual(combo.accessibleName(), "Filter knowledge articles by status")
        self.assertEqual(combo.currentText(), "All statuses")
        self.assertEqual(
            [(combo.itemText(i), combo.itemData(i)) for i in range(combo.count())],
            [("All statuses", None), ("Draft", "DRAFT"),
             ("Published", "PUBLISHED"), ("Archived", "ARCHIVED")],
        )
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        for control in (
            self.workspace.search_input, self.workspace.category_filter,
            self.workspace.status_filter, self.workspace.search_button,
            self.workspace.clear_search_button,
        ):
            self.assertTrue(control.isVisible())
            self.assertTrue(self.workspace.rect().contains(control.geometry()))

    def test_normal_status_and_category_changes_compose_in_one_async_request(self):
        self.show()
        self.choose_category(11)
        gate = threading.Event()
        threads = []
        original = self.service.list_articles

        def listing(**arguments):
            threads.append(threading.get_ident())
            gate.wait(3)
            return original(**arguments)

        with patch.object(self.service, "list_articles", side_effect=listing) as call:
            try:
                self.workspace.status_filter.setCurrentIndex(
                    self.workspace.status_filter.findData("PUBLISHED")
                )
                self.assertTrue(self.window.runner.busy)
                self.assertFalse(self.workspace.status_filter.isEnabled())
                self.assertIsNone(self.workspace.article)
                self.assertEqual(self.workspace.model.rowCount(), 0)
                self.workspace.refresh_list()
            finally:
                gate.set()
            self.wait_idle()
            call.assert_called_once_with(category_id=11, status="PUBLISHED")
        self.assertNotEqual(threads, [threading.get_ident()])
        self.assertEqual(self.codes(), ["B"])

        with patch.object(self.service, "list_articles", wraps=original) as call:
            self.choose_category(22)
            call.assert_called_once_with(category_id=22, status="PUBLISHED")
        self.assertEqual(self.codes(), ["C"])

    def test_search_uses_both_filters_last_executed_query_and_clear_preserves_both(self):
        self.show()
        self.choose_category(11)
        self.choose_status("PUBLISHED")
        self.workspace.search_input.setText("DNS")
        self.workspace.search_articles()
        self.wait_idle()
        self.assertEqual(self.codes(), ["B"])
        self.workspace.search_input.setText("unsubmitted text")
        with patch.object(self.service, "search_articles", wraps=self.service.search_articles) as search:
            self.choose_category("ALL")
            search.assert_called_once_with("DNS", status="PUBLISHED")
        self.assertEqual(set(self.codes()), {"B", "C"})
        self.workspace.clear_search_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentText(), "All categories")
        self.assertEqual(self.workspace.status_filter.currentData(), "PUBLISHED")
        self.assertEqual(self.workspace.search_input.text(), "")
        self.assertEqual(set(self.codes()), {"B", "C"})

    def test_empty_and_failed_replacements_clear_stale_detail_but_keep_status(self):
        self.show()
        self.choose_category(22)
        self.choose_status("ARCHIVED")
        self.assertIn("archived", self.workspace.empty_state.text())
        self.assertIn("this category", self.workspace.empty_state.text())
        self.assertIsNone(self.workspace.article)
        with patch.object(self.service, "list_articles", side_effect=RuntimeError("private")):
            self.choose_status("PUBLISHED")
        self.assertEqual(self.codes(), [])
        self.assertIsNone(self.workspace.article)
        self.assertEqual(self.workspace.detail_body.toPlainText(), "")
        self.assertEqual(self.workspace.status_filter.currentData(), "PUBLISHED")
        self.assertNotIn("private", self.workspace.feedback.text())

    def test_new_publish_and_archive_reset_only_filters_needed_to_reveal_result(self):
        self.show()
        self.choose_category(11)
        self.choose_status("PUBLISHED")
        dialog = self.workspace.open_new_article()
        dialog.code_input.setText("NEW")
        dialog.title_input.setText("New DNS")
        dialog.body_input.setPlainText("DNS")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentText(), "All categories")
        self.assertEqual(self.workspace.status_filter.currentText(), "All statuses")
        self.assertEqual(self.workspace.article.article_code, "NEW")

        self.choose_category(11)
        self.choose_status("DRAFT")
        self.assertEqual(self.workspace.article.article_code, "A")
        with patch.object(self.workspace, "_confirm_publish", return_value=True):
            self.workspace.publish_article()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertEqual(self.workspace.status_filter.currentText(), "All statuses")
        self.assertEqual(self.workspace.article.status, "PUBLISHED")

        self.choose_status("PUBLISHED")
        with patch.object(self.workspace, "_confirm_archive", return_value=True):
            self.workspace.archive_article()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertEqual(self.workspace.status_filter.currentText(), "All statuses")
        self.assertEqual(self.workspace.article.status, "ARCHIVED")

    def test_category_mutation_preserves_status_filter(self):
        self.show()
        self.choose_category(11)
        self.choose_status("DRAFT")
        dialog = self.workspace.open_category()
        self.wait_idle()
        dialog.category_input.setCurrentIndex(dialog.category_input.findData(22))
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertEqual(self.workspace.status_filter.currentData(), "DRAFT")
        self.assertEqual(self.codes(), [])
        self.assertIsNone(self.workspace.article)


if __name__ == "__main__":
    unittest.main()
