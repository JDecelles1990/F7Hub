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
        self.update_calls = []
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
            version_number=1,
        )
        self.articles.append(article)
        return article

    def list_articles(self):
        return tuple(reversed(self.articles))

    def update_article(self, **values):
        self.update_calls.append((values, threading.get_ident()))
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        old = self.get_article(values["article_id"])
        article = SimpleNamespace(**(vars(old) | dict(
            title=values["title"], summary=values["summary"],
            body_markdown=values["body"], version_number=old.version_number + 1,
        )))
        self.articles[self.articles.index(old)] = article
        return article

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
        for name in ("_new_article_dialog", "_edit_article_dialog"):
            dialog = getattr(self.workspace, name, None)
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

    def prepare_article(self, status="DRAFT"):
        article = self.service.create_article(
            article_code="KB0001", title="Original title", summary="Summary", body="Original body",
        )
        article.status = status
        self.workspace.refresh_list(select_article_id=article.knowledge_article_id)
        self.wait_idle()
        return article

    def test_edit_availability_uses_loaded_detail_and_clears_during_reload(self):
        self.assertFalse(self.workspace.edit_button.isEnabled())
        self.assertIsNone(self.workspace.open_edit_article())
        for status in ("DRAFT", "PUBLISHED", "ARCHIVED"):
            self.service.articles.clear()
            article = self.prepare_article(status)
            self.assertEqual(self.workspace.edit_button.isEnabled(), status == "DRAFT")
            if status != "DRAFT":
                self.assertIsNone(self.workspace.open_edit_article())
            self.assertEqual(self.workspace.detail_body.toPlainText(), article.body_markdown)
        self.service.articles[0].status = "DRAFT"
        self.workspace.open_article(article.knowledge_article_id)
        self.assertFalse(self.workspace.edit_button.isEnabled())
        self.wait_idle()
        self.assertTrue(self.workspace.edit_button.isEnabled())

    def test_edit_prefill_readonly_identity_and_cancel_does_not_write(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLabel
        article = self.prepare_article()
        dialog = self.workspace.open_edit_article()
        self.assertIsInstance(dialog.code_label, QLabel)
        self.assertIsInstance(dialog.version_label, QLabel)
        self.assertEqual(dialog.code_label.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(dialog.code_label.text(), article.article_code)
        self.assertEqual(dialog.version_label.text(), "Version 1")
        self.assertEqual(dialog.title_input.text(), article.title)
        self.assertEqual(dialog.summary_input.text(), article.summary)
        self.assertEqual(dialog.body_input.toPlainText(), article.body_markdown)
        dialog.title_input.setText("Unsaved title")
        dialog.cancel_button.click()
        self.assertFalse(dialog.isVisible())
        self.assertEqual(self.service.update_calls, [])

    def test_revision_success_refreshes_same_selection_and_current_version(self):
        article = self.prepare_article()
        self.service.create_article(article_code="KB0002", title="Other", summary="", body="Other")
        dialog = self.workspace.open_edit_article()
        dialog.title_input.setText("Edited title")
        dialog.body_input.setPlainText("Edited body")
        dialog.save_button.click()
        self.wait_idle()
        self.assertFalse(dialog.isVisible())
        self.assertEqual(self.workspace.article.knowledge_article_id, article.knowledge_article_id)
        self.assertEqual(self.workspace.detail_title.text(), "Edited title")
        self.assertEqual(self.workspace.detail_body.toPlainText(), "Edited body")
        self.assertEqual(self.workspace.detail_version.text(), "Version 2")
        self.assertEqual(self.workspace.model.item(self.workspace.table.currentIndex().row(), 0).text(), "KB0001")
        values, _thread = self.service.update_calls[0]
        self.assertNotIn("article_code", values)
        self.assertEqual(values["expected_version_number"], 1)

    def test_revision_runs_in_background_blocks_duplicate_and_close(self):
        from PySide6.QtCore import QTimer
        self.prepare_article()
        self.service.gate = threading.Event()
        dialog = self.workspace.open_edit_article()
        dialog.title_input.setText("Edited")
        dialog.submit()
        dialog.submit()
        dialog.reject()
        dialog.close()
        ticks = []
        QTimer.singleShot(0, lambda: ticks.append(True))
        QTest.qWait(30)
        self.assertTrue(ticks)
        self.assertTrue(dialog.isVisible())
        self.assertTrue(self.runner.busy)
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertFalse(dialog.cancel_button.isEnabled())
        self.assertEqual(len(self.service.update_calls), 1)
        self.assertNotEqual(self.service.update_calls[0][1], threading.get_ident())
        self.service.gate.set()
        self.wait_idle()
        self.assertFalse(dialog.isVisible())

    def test_stale_feedback_retains_input_and_requires_new_editor(self):
        from f7hub.services.knowledge_service import KnowledgeEditConflictError
        self.prepare_article()
        self.service.error = KnowledgeEditConflictError("This article changed. Reopen the latest version.")
        dialog = self.workspace.open_edit_article()
        dialog.title_input.setText("My title")
        dialog.summary_input.setText("My summary")
        dialog.body_input.setPlainText("My body")
        dialog.submit()
        self.wait_idle()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.title_input.text(), "My title")
        self.assertEqual(dialog.summary_input.text(), "My summary")
        self.assertEqual(dialog.body_input.toPlainText(), "My body")
        self.assertIn("Reopen the latest version", dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertTrue(dialog.body_input.isEnabled())
        dialog.submit()
        self.assertEqual(len(self.service.update_calls), 1)

    def test_workspace_reload_does_not_replace_open_editor_token(self):
        self.prepare_article()
        dialog = self.workspace.open_edit_article()
        self.service.articles[0] = SimpleNamespace(**(vars(self.service.articles[0]) | {"version_number": 2}))
        self.workspace.refresh_list(select_article_id=1)
        self.wait_idle()
        self.assertEqual(self.workspace.detail_version.text(), "Version 2")
        self.assertEqual(dialog.version_label.text(), "Version 1")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.service.update_calls[0][0]["expected_version_number"], 1)

    def test_revision_failures_and_no_change_preserve_input_allow_retry(self):
        from f7hub.services.knowledge_service import KnowledgeNoChangesError, KnowledgeValidationError
        self.prepare_article()
        dialog = self.workspace.open_edit_article()
        for error, message in (
            (RuntimeError("private database path"), "Could not save"),
            (KnowledgeValidationError("Title is required."), "Title is required"),
            (KnowledgeNoChangesError("No changes to save."), "No changes to save"),
        ):
            self.service.error = error
            dialog.submit()
            self.wait_idle()
            self.assertTrue(dialog.isVisible())
            self.assertTrue(dialog.save_button.isEnabled())
            self.assertEqual(dialog.body_input.toPlainText(), "Original body")
            self.assertIn(message, dialog.feedback.text())
            self.assertNotIn("private", dialog.feedback.text())
        self.service.error = None
        dialog.title_input.setText("Retry")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(self.workspace.detail_version.text(), "Version 2")

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
