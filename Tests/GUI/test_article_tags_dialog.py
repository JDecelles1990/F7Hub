"""Existing-tag dialog behavior through the MainWindow hierarchy."""

import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from f7hub.services.knowledge_service import KnowledgeTagConflictError


class ArticleTagsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "tags-ui.db"
        self.context = bootstrap_application(database_path=self.path)
        with database_connection(self.path) as connection:
            connection.executemany("INSERT INTO tags (name, slug, created_at) VALUES (?, ?, ?)", (
                ("Windows", "windows", "2026-09-15T10:00:00Z"),
                ("Networking", "networking", "2026-09-15T10:00:00Z"),
                ("VPN", "vpn", "2026-09-15T10:00:00Z"),
            ))
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.wait_idle()
        self.service = self.context.knowledge_service
        self.article = self.service.create_article(article_code="KB-TAG-UI", title="Synthetic tags", summary=None, body="Body")
        self.window.show_knowledge()
        self.wait_idle()
        self.workspace = self.window.knowledge_workspace

    def tearDown(self):
        self.wait_idle()
        if self.workspace._tags_dialog is not None:
            self.workspace._tags_dialog.reject()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def wait_idle(self):
        deadline, settled = time.monotonic() + 8, 0
        while time.monotonic() < deadline and settled < 3:
            self.app.processEvents()
            QTest.qWait(5)
            settled = 0 if self.window.runner.busy else settled + 1
        self.assertFalse(self.window.runner.busy)

    def open_dialog(self):
        dialog = self.workspace.open_tags()
        self.assertIsNotNone(dialog)
        self.wait_idle()
        return dialog

    def selected_ids(self, dialog):
        return tuple(dialog.tag_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(dialog.tag_list.count()) if dialog.tag_list.item(i).checkState() == Qt.CheckState.Checked)

    def test_draft_action_choices_cancel_and_escape_are_safe(self):
        self.assertTrue(self.workspace.tags_button.isEnabled())
        dialog = self.open_dialog()
        self.assertEqual([dialog.tag_list.item(i).text() for i in range(dialog.tag_list.count())], ["Networking", "VPN", "Windows"])
        self.assertEqual(self.selected_ids(dialog), ())
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
        self.assertEqual(self.service.list_article_tags(self.article.knowledge_article_id), ())
        for status in ("PUBLISHED", "ARCHIVED"):
            self.workspace._show_article(type("Article", (), {**vars(self.article), "status": status})())
            self.assertFalse(self.workspace.tags_button.isEnabled())
            self.assertIsNone(self.workspace.open_tags())

    def test_multi_select_replace_and_remove_all_show_authoritative_names(self):
        dialog = self.open_dialog()
        for index in (0, 2):
            dialog.tag_list.item(index).setCheckState(Qt.CheckState.Checked)
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.detail_tags.text(), "Tags: Networking, Windows")
        dialog = self.open_dialog()
        self.assertEqual(self.selected_ids(dialog), (2, 1))
        for index in range(dialog.tag_list.count()):
            dialog.tag_list.item(index).setCheckState(Qt.CheckState.Unchecked)
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.detail_tags.text(), "Tags: None")
        self.assertEqual(self.service.list_article_tags(self.article.knowledge_article_id), ())

    def test_reference_failure_and_stale_save_do_not_fake_tags(self):
        with patch.object(self.service, "list_available_tags", side_effect=RuntimeError("private")):
            dialog = self.open_dialog()
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertNotIn("private", dialog.feedback.text())
        self.assertEqual(self.workspace.detail_body.toPlainText(), self.article.body_markdown)
        dialog.reject()
        dialog = self.open_dialog()
        dialog.tag_list.item(0).setCheckState(Qt.CheckState.Checked)
        with patch.object(self.service, "set_article_tags", side_effect=KnowledgeTagConflictError("Reopen latest article.")):
            dialog.submit()
            self.wait_idle()
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(self.workspace.detail_tags.text(), "Tags: None")

    def test_replacement_load_clears_stale_tag_detail(self):
        self.workspace.detail_tags.setText("Tags: stale")
        self.workspace._show_article(None)
        self.assertEqual(self.workspace.detail_tags.text(), "")
