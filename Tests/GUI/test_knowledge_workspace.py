from __future__ import annotations

import os
from types import SimpleNamespace
import threading
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.service_task_runner import ServiceTaskRunner


class RecordingKnowledgeService:
    def __init__(self):
        self.articles = []
        self.create_calls = 0
        self.error = None
        self.gate = None

    def create_article(self, **values):
        self.create_calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        article = SimpleNamespace(
            knowledge_article_id=len(self.articles) + 1,
            article_code=values["article_code"].strip(),
            title=values["title"].strip(),
            summary=values["summary"].strip() or None,
            body_markdown=values["body"].strip(),
            status="DRAFT",
        )
        self.articles.append(article)
        return article

    def list_articles(self):
        return tuple(reversed(self.articles))

    def get_article(self, article_id):
        return next((article for article in self.articles if article.knowledge_article_id == article_id), None)


class KnowledgeWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.service = RecordingKnowledgeService()
        self.runner = ServiceTaskRunner()
        self.workspace = KnowledgeWorkspace(self.service, self.runner)
        self.workspace.resize(1000, 700)
        self.workspace.show()
        self.application.processEvents()

    def tearDown(self) -> None:
        if self.service.gate:
            self.service.gate.set()
        self.wait_idle()
        dialog = getattr(self.workspace, "_new_article_dialog", None)
        if dialog is not None:
            dialog.close()
        self.workspace.close()
        self.workspace.deleteLater()
        self.runner.deleteLater()
        self.application.processEvents()

    def test_empty_state_and_new_article_validation_and_cancel(self):
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertTrue(self.workspace.empty_state.isVisible())
        self.assertEqual(self.workspace.model.rowCount(), 0)
        dialog = self.workspace.open_new_article()
        dialog.submit()
        self.assertEqual(dialog.feedback.text(), "Article code is required.")
        self.assertEqual(self.service.create_calls, 0)
        dialog.code_input.setText("KB0001")
        dialog.title_input.setText("Synthetic")
        dialog.body_input.setPlainText("Body")
        dialog.reject()
        self.assertEqual(self.service.create_calls, 0)

    def test_failed_create_preserves_input_and_hides_internal_error(self):
        self.service.error = RuntimeError("Sensitive SQLite path")
        dialog = self.workspace.open_new_article()
        self.fill(dialog, "KB0001")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(dialog.code_input.text(), "KB0001")
        self.assertEqual(dialog.title_input.text(), "Article KB0001")
        self.assertEqual(dialog.body_input.toPlainText(), "# Body")
        self.assertNotIn("Sensitive", dialog.feedback.text())
        self.assertTrue(dialog.create_button.isEnabled())

    def test_success_refreshes_list_selects_and_reads_article(self):
        dialog = self.workspace.open_new_article()
        self.fill(dialog, "KB0001")
        dialog.submit()
        self.wait_idle()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 1)
        self.assertEqual(self.workspace.article.article_code, "KB0001")
        self.assertEqual(self.workspace.detail_title.text(), "Article KB0001")
        self.assertEqual(self.workspace.detail_status.text(), "Status: DRAFT")
        self.assertEqual(self.workspace.detail_body.toPlainText(), "# Body")

    def test_background_create_is_responsive_and_double_submit_is_ignored(self):
        self.service.gate = threading.Event()
        dialog = self.workspace.open_new_article()
        self.fill(dialog, "KB0001")
        dialog.submit()
        dialog.submit()
        ticks = []
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: ticks.append(True))
        QTest.qWait(30)
        self.assertTrue(ticks)
        self.assertTrue(self.runner.busy)
        self.assertFalse(dialog.create_button.isEnabled())
        self.assertEqual(self.service.create_calls, 1)
        self.service.gate.set()
        self.wait_idle()

    def test_untrusted_article_metadata_and_body_remain_plain_text(self):
        from PySide6.QtCore import Qt

        dialog = self.workspace.open_new_article()
        self.fill(dialog, "<b>KB0001</b>")
        dialog.title_input.setText("<img src='file:///synthetic.png'>Title")
        dialog.summary_input.setText("<a href='https://invalid.example'>Summary</a>")
        dialog.body_input.setPlainText("<script>synthetic()</script>")
        dialog.submit()
        self.wait_idle()
        self.wait_idle()
        for label in (
            self.workspace.detail_code, self.workspace.detail_title,
            self.workspace.detail_status, self.workspace.detail_summary,
        ):
            self.assertEqual(label.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(self.workspace.detail_code.text(), "<b>KB0001</b>")
        self.assertEqual(self.workspace.detail_title.text(), "<img src='file:///synthetic.png'>Title")
        self.assertEqual(self.workspace.detail_body.toPlainText(), "<script>synthetic()</script>")
        self.assertTrue(self.workspace.detail_body.isReadOnly())

    @staticmethod
    def fill(dialog, code):
        dialog.code_input.setText(code)
        dialog.title_input.setText(f"Article {code}")
        dialog.summary_input.setText("Synthetic summary")
        dialog.body_input.setPlainText("# Body")

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.runner.busy, "Background task did not finish")
        QTest.qWait(10)


if __name__ == "__main__":
    unittest.main()
