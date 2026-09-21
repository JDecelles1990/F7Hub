"""Single-tag filter behavior in the real Knowledge workspace hierarchy."""

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from Tests.Database.test_knowledge_categories import seed_knowledge_categories


class KnowledgeTagFilterGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "tag-filter-ui.db"
        self.context = bootstrap_application(database_path=self.path)
        seed_knowledge_categories(self.path)
        with database_connection(self.path) as connection:
            connection.executemany(
                "INSERT INTO tags (tag_id, name, slug, created_at) VALUES (?, ?, ?, ?)",
                (
                    (11, "VPN", "vpn", "2026-09-15T10:00:00Z"),
                    (22, "Windows", "windows", "2026-09-15T10:00:00Z"),
                    (33, "Security", "security", "2026-09-15T10:00:00Z"),
                    (44, "Unused", "unused", "2026-09-15T10:00:00Z"),
                ),
            )
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.workspace = self.window.knowledge_workspace
        self.service = self.context.knowledge_service
        self.wait_idle()
        self.rows = {}
        for code, category_id, status, tag_ids in (
            ("A", 11, "DRAFT", (11, 22)),
            ("B", 11, "PUBLISHED", (11,)),
            ("C", 22, "PUBLISHED", (33,)),
            ("D", None, "ARCHIVED", ()),
            ("E", 11, "ARCHIVED", (11, 33, 22)),
        ):
            article = self.service.create_article(
                article_code=code, title="DNS tag filter", summary=None, body="DNS steps"
            )
            if category_id is not None:
                article = self.service.set_article_category(
                    article.knowledge_article_id, article.version_number,
                    article.updated_at, category_id,
                )
            if tag_ids:
                article = self.service.set_article_tags(
                    article.knowledge_article_id, article.version_number,
                    article.updated_at, tag_ids,
                )
            if status != "DRAFT":
                with database_connection(self.path) as connection:
                    connection.execute(
                        "UPDATE knowledge_articles SET status = ?, published_at = ? "
                        "WHERE knowledge_article_id = ?",
                        (status, "2026-09-15T12:00:00.000Z", article.knowledge_article_id),
                    )
                article = self.service.get_article(article.knowledge_article_id)
            self.rows[code] = article

    def tearDown(self):
        self.wait_idle()
        if self.workspace._tags_dialog:
            self.workspace._tags_dialog.reject()
        self.window.workspace._clear_drafts()
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

    def choose_tag(self, name):
        index = next(
            i for i in range(self.workspace.tag_filter.count())
            if self.workspace.tag_filter.itemText(i) == name
        )
        self.workspace.tag_filter.setCurrentIndex(index)
        self.wait_idle()

    def choose_category(self, category_id):
        self.workspace.category_filter.setCurrentIndex(
            1 if category_id is None else self.workspace.category_filter.findData(category_id)
        )
        self.wait_idle()

    def choose_status(self, status):
        self.workspace.status_filter.setCurrentIndex(
            0 if status is None else self.workspace.status_filter.findData(status)
        )
        self.wait_idle()

    def codes(self):
        return [article.article_code for article in self.workspace.articles]

    def test_options_default_order_population_is_signal_blocked_and_layout_fits(self):
        with patch.object(self.service, "list_articles", wraps=self.service.list_articles) as listing:
            self.show()
            listing.assert_called_once_with()
        combo = self.workspace.tag_filter
        self.assertEqual(combo.currentText(), "All tags")
        self.assertEqual(
            [combo.itemText(i) for i in range(combo.count())],
            ["All tags", "Untagged", "Security", "Unused", "VPN", "Windows"],
        )
        self.assertEqual(combo.accessibleName(), "Filter knowledge articles by tag")
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        for control in (
            self.workspace.search_input, self.workspace.search_button,
            self.workspace.clear_search_button, self.workspace.category_filter,
            self.workspace.status_filter, self.workspace.tag_filter,
        ):
            self.assertTrue(control.isVisible())
            top_left = control.mapTo(self.workspace, control.rect().topLeft())
            bottom_right = control.mapTo(self.workspace, control.rect().bottomRight())
            self.assertTrue(self.workspace.rect().contains(top_left))
            self.assertTrue(self.workspace.rect().contains(bottom_right))

    def test_normal_search_composition_last_query_and_clear_preserves_all_filters(self):
        self.show()
        self.choose_category(11)
        self.choose_status("PUBLISHED")
        with patch.object(self.service, "list_articles", wraps=self.service.list_articles) as listing:
            self.choose_tag("VPN")
            listing.assert_called_once_with(category_id=11, status="PUBLISHED", tag_id=11)
        self.assertEqual(self.codes(), ["B"])

        self.workspace.search_input.setText("DNS")
        self.workspace.search_articles()
        self.wait_idle()
        self.assertEqual(self.codes(), ["B"])
        self.workspace.search_input.setText("unsubmitted text")
        with patch.object(self.service, "search_articles", wraps=self.service.search_articles) as search:
            self.choose_tag("Security")
            search.assert_called_once_with(
                "DNS", category_id=11, status="PUBLISHED", tag_id=33
            )
        self.assertEqual(self.codes(), [])
        self.workspace.clear_search_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.search_input.text(), "")
        self.assertEqual(self.workspace.category_filter.currentData(), 11)
        self.assertEqual(self.workspace.status_filter.currentData(), "PUBLISHED")
        self.assertEqual(self.workspace.tag_filter.currentText(), "Security")
        self.assertEqual(self.codes(), [])

    def test_untagged_specific_empty_states_selection_and_read_only_mutation_reconciliation(self):
        self.show()
        self.choose_tag("VPN")
        self.assertEqual(set(self.codes()), {"A", "B", "E"})
        self.assertEqual(len(self.codes()), len(set(self.codes())))

        row = next(i for i, article in enumerate(self.workspace.articles) if article.article_code == "A")
        self.workspace.table.selectRow(row)
        self.wait_idle()
        current = self.workspace.article
        changed = self.service.set_article_tags(
            current.knowledge_article_id, current.version_number,
            current.updated_at, (22,),
        )
        self.workspace._tags_updated(changed)
        self.wait_idle()
        self.assertNotIn("A", self.codes())
        self.assertNotEqual(getattr(self.workspace.article, "article_code", None), "A")
        self.assertEqual(self.workspace.tag_filter.currentText(), "VPN")

        self.choose_tag("Untagged")
        self.assertEqual(self.codes(), ["D"])
        self.assertEqual(self.workspace.article.article_code, "D")
        current = self.service.get_article(self.rows["D"].knowledge_article_id)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE knowledge_articles SET status = 'DRAFT', published_at = NULL WHERE knowledge_article_id = ?",
                               (current.knowledge_article_id,))
        current = self.service.get_article(current.knowledge_article_id)
        changed = self.service.set_article_tags(
            current.knowledge_article_id, current.version_number,
            current.updated_at, (22,),
        )
        self.workspace._tags_updated(changed)
        self.wait_idle()
        self.assertEqual(self.codes(), [])
        self.assertIsNone(self.workspace.article)
        self.assertEqual(self.workspace.empty_state.text(), "No untagged knowledge articles.")

    def test_specific_match_retained_new_article_reveal_and_ticket_style_reset(self):
        self.show()
        self.choose_tag("VPN")
        row = next(i for i, article in enumerate(self.workspace.articles) if article.article_code == "A")
        self.workspace.table.selectRow(row)
        self.wait_idle()
        current = self.workspace.article
        changed = self.service.set_article_tags(
            current.knowledge_article_id, current.version_number,
            current.updated_at, (11, 22, 33),
        )
        self.workspace._tags_updated(changed)
        self.wait_idle()
        self.assertEqual(self.workspace.tag_filter.currentText(), "VPN")
        self.assertIn("A", self.codes())

        self.choose_category(11)
        self.choose_status("PUBLISHED")
        self.choose_tag("VPN")
        dialog = self.workspace.open_new_article()
        dialog.code_input.setText("NEW")
        dialog.title_input.setText("New DNS")
        dialog.body_input.setPlainText("DNS")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.category_filter.currentText(), "All categories")
        self.assertEqual(self.workspace.status_filter.currentText(), "All statuses")
        self.assertEqual(self.workspace.tag_filter.currentText(), "All tags")
        self.assertEqual(self.workspace.article.article_code, "NEW")

        self.choose_tag("Untagged")
        dialog = self.workspace.open_new_article()
        dialog.code_input.setText("NEW-UNTAGGED")
        dialog.title_input.setText("New untagged DNS")
        dialog.body_input.setPlainText("DNS")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.tag_filter.currentText(), "Untagged")
        self.assertEqual(self.workspace.article.article_code, "NEW-UNTAGGED")

        self.choose_category(11)
        self.choose_status("DRAFT")
        self.choose_tag("VPN")
        self.workspace.search_input.setText("DNS")
        self.workspace.search_articles()
        self.wait_idle()
        self.workspace.open_article_by_id(self.rows["C"].knowledge_article_id)
        self.wait_idle()
        self.assertEqual(self.workspace.search_input.text(), "")
        self.assertEqual(self.workspace.category_filter.currentText(), "All categories")
        self.assertEqual(self.workspace.status_filter.currentText(), "All statuses")
        self.assertEqual(self.workspace.tag_filter.currentText(), "All tags")
        self.assertEqual(self.workspace.article.article_code, "C")

    def test_tag_failure_is_independent_and_tag_runner_guards_close(self):
        gate = threading.Event()
        original = self.service.list_available_tags
        with patch.object(
            self.service, "list_available_tags",
            side_effect=lambda: (gate.wait(3), original())[1],
        ):
            try:
                self.window.show_knowledge()
                self.wait_idle(references=False)
                self.assertTrue(self.workspace.filter_loading)
                self.assertFalse(self.window.close())
                self.assertTrue(self.workspace.category_filter.isEnabled())
            finally:
                gate.set()
            self.wait_idle()

        self.close_for_rebuild()
        self.context = bootstrap_application(database_path=self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.workspace = self.window.knowledge_workspace
        self.service = self.context.knowledge_service
        with patch.object(self.service, "list_available_tags", side_effect=RuntimeError("private")):
            self.window.show_knowledge()
            self.wait_idle()
        self.assertTrue(self.workspace.category_filter.isEnabled())
        self.assertTrue(self.workspace.status_filter.isEnabled())
        self.assertTrue(self.workspace.tag_filter.isEnabled())
        self.assertEqual(self.workspace.tag_filter.count(), 2)
        self.assertNotIn("private", self.workspace.tag_filter_feedback.text())
        self.choose_tag("Untagged")
        self.assertTrue(self.workspace.table.isVisible() or self.workspace.empty_state.isVisible())

    def close_for_rebuild(self):
        self.wait_idle()
        self.window.workspace._clear_drafts()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
