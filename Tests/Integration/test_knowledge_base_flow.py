from __future__ import annotations

import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.infrastructure.database import database_connection
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.services.knowledge_service import KnowledgeService


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class KnowledgeBaseFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "knowledge-flow.db"
        self.context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.application.processEvents()
        self.wait_idle(self.window.runner)

    def tearDown(self) -> None:
        self.wait_idle(self.window.runner)
        self.window.workspace._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.temporary_directory.cleanup()

    def test_navigation_create_list_read_and_reopen_persisted_articles(self):
        self.assertTrue(self.window.knowledge_action.isVisible())
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        workspace = self.window.knowledge_workspace
        self.assertIs(self.window.pages.currentWidget(), workspace)
        self.assertTrue(workspace.empty_state.isVisible())

        self.create_through_dialog("KB0001", "Reset a stuck print spooler")
        self.create_through_dialog("KB0002", "Verify Microsoft 365 sign-in")
        self.assertEqual(workspace.model.rowCount(), 2)
        self.assertEqual(workspace.article.article_code, "KB0002")

        row = next(index for index, article in enumerate(workspace.articles) if article.article_code == "KB0001")
        workspace.table.selectRow(row)
        self.wait_idle(self.window.runner)
        self.assertEqual(workspace.article.article_code, "KB0001")
        self.assertEqual(workspace.detail_title.text(), "Reset a stuck print spooler")

        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_articles").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT count(*) FROM knowledge_article_versions").fetchone()[0], 2)

        runner = ServiceTaskRunner()
        reopened = KnowledgeWorkspace(
            KnowledgeService(KnowledgeRepository(self.path)), runner
        )
        reopened.show()
        reopened.refresh_list(select_article_id=workspace.article.knowledge_article_id)
        self.wait_idle(runner)
        self.wait_idle(runner)
        self.assertEqual(reopened.model.rowCount(), 2)
        self.assertEqual(reopened.article.article_code, "KB0001")
        reopened.close()
        reopened.deleteLater()
        runner.deleteLater()

    def test_existing_ticket_navigation_remains_available(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.window.show_new_ticket()
        self.assertIs(self.window.pages.currentWidget(), self.window.ticket_create_widget)
        self.window.show_tickets()
        self.wait_idle(self.window.runner)
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)

    def history(self):
        with database_connection(self.path) as connection:
            return [tuple(row) for row in connection.execute(
                "SELECT version_number, title, summary, body_markdown "
                "FROM knowledge_article_versions WHERE knowledge_article_id = 1 ORDER BY version_number"
            )]

    def test_create_edit_two_editors_conflict_and_reconstruction(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KB0001", "Reset a stuck print spooler")
        workspace = self.window.knowledge_workspace
        self.assertEqual(workspace.detail_version.text(), "Version 1")
        original = self.history()
        dialog = workspace.open_edit_article()
        dialog.title_input.setText("Reset a Windows print spooler")
        dialog.summary_input.setText("Revised synthetic summary")
        dialog.body_input.setPlainText("# Revised synthetic body\n\n  1. Synthetic step.  \n")
        dialog.save_button.click()
        self.wait_idle(self.window.runner)
        self.assertEqual(workspace.detail_version.text(), "Version 2")
        self.assertEqual(workspace.article.article_code, "KB0001")
        self.assertEqual(self.history()[:1], original)
        self.assertEqual(len(self.history()), 2)
        self.assertEqual(self.history()[1][1:], (
            workspace.article.title, workspace.article.summary, workspace.article.body_markdown,
        ))
        self.window.show_new_ticket()
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.assertEqual(workspace.detail_title.text(), "Reset a Windows print spooler")

        editor_a = workspace.open_edit_article()
        editor_b = workspace.open_edit_article()
        editor_b.title_input.setText("Editor B unsaved title")
        editor_b.body_input.setPlainText("Editor B unsaved body")
        editor_a.title_input.setText("Editor A latest title")
        editor_a.submit()
        self.wait_idle(self.window.runner)
        self.assertEqual(workspace.detail_version.text(), "Version 3")
        # The successful edit has refreshed this same workspace while B stays open.
        self.assertEqual(editor_b.version_label.text(), "Version 2")
        saved_history = self.history()
        editor_b.submit()
        self.wait_idle(self.window.runner)
        self.assertTrue(editor_b.isVisible())
        self.assertIn("Reopen the latest version", editor_b.feedback.text())
        self.assertEqual(editor_b.title_input.text(), "Editor B unsaved title")
        self.assertEqual(editor_b.body_input.toPlainText(), "Editor B unsaved body")
        self.assertFalse(editor_b.save_button.isEnabled())
        editor_b.submit()
        self.assertFalse(self.window.runner.busy)
        self.assertEqual(self.history(), saved_history)
        self.assertEqual([row[0] for row in saved_history], [1, 2, 3])
        editor_b.reject()

        reconstructed = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.path)
        restored = reconstructed.main_window
        try:
            self.wait_idle(restored.runner)
            restored.show_knowledge()
            self.wait_idle(restored.runner)
            self.assertEqual(restored.knowledge_workspace.detail_version.text(), "Version 3")
            self.assertEqual(restored.knowledge_workspace.detail_title.text(), "Editor A latest title")
            self.assertEqual(self.history(), saved_history)
        finally:
            self.wait_idle(restored.runner)
            restored.close()
            restored.deleteLater()
            self.application.processEvents()
        self.create_through_dialog("KB0002", "Another synthetic article")
        self.assertEqual(workspace.article.article_code, "KB0002")
        self.assertEqual(workspace.detail_version.text(), "Version 1")

    def test_external_status_change_and_deletion_preserve_editor_input(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        for index, status in enumerate(("PUBLISHED", "ARCHIVED", "DELETED"), 1):
            with self.subTest(status=status):
                self.create_through_dialog(f"KB{index:04}", "Synthetic original")
                workspace = self.window.knowledge_workspace
                article = workspace.article
                dialog = workspace.open_edit_article()
                dialog.title_input.setText("Unsaved title")
                dialog.body_input.setPlainText("Unsaved body")
                with database_connection(self.path) as connection:
                    if status == "DELETED":
                        connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (article.knowledge_article_id,))
                    else:
                        connection.execute("UPDATE knowledge_articles SET status = ? WHERE knowledge_article_id = ?", (status, article.knowledge_article_id))
                dialog.submit()
                self.wait_idle(self.window.runner)
                self.assertTrue(dialog.isVisible())
                self.assertEqual(dialog.title_input.text(), "Unsaved title")
                self.assertEqual(dialog.body_input.toPlainText(), "Unsaved body")
                self.assertIn("no longer exists" if status == "DELETED" else "Only draft", dialog.feedback.text())
                self.assertFalse(dialog.save_button.isEnabled())
                current = self.context.knowledge_service.get_article(article.knowledge_article_id)
                if status == "DELETED":
                    self.assertIsNone(current)
                else:
                    self.assertEqual(current.title, article.title)
                    self.assertEqual(current.version_number, 1)
                with database_connection(self.path) as connection:
                    count = connection.execute("SELECT count(*) FROM knowledge_article_versions WHERE knowledge_article_id = ?", (article.knowledge_article_id,)).fetchone()[0]
                    self.assertEqual(count, 0 if status == "DELETED" else 1)
                    self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                dialog.reject()

    def test_no_change_save_keeps_dialog_and_revision_then_changed_retry_succeeds(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KB0001", "Synthetic title")
        workspace = self.window.knowledge_workspace
        dialog = workspace.open_edit_article()
        dialog.submit()
        self.wait_idle(self.window.runner)
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.feedback.text(), "No changes to save.")
        self.assertEqual(len(self.history()), 1)
        dialog.title_input.setText("Changed title")
        dialog.submit()
        self.wait_idle(self.window.runner)
        self.assertFalse(dialog.isVisible())
        self.assertEqual(workspace.detail_version.text(), "Version 2")

    def test_snapshot_failure_preserves_dialog_and_retry_commits_once(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KB0001", "Synthetic title")
        workspace = self.window.knowledge_workspace
        dialog = workspace.open_edit_article()
        dialog.title_input.setText("Retry title")
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_revision BEFORE INSERT ON knowledge_article_versions BEGIN SELECT RAISE(ABORT, 'private synthetic failure'); END")
        dialog.submit()
        self.wait_idle(self.window.runner)
        self.assertTrue(dialog.isVisible())
        self.assertNotIn("private", dialog.feedback.text())
        self.assertEqual(dialog.title_input.text(), "Retry title")
        self.assertEqual(len(self.history()), 1)
        self.assertEqual(self.context.knowledge_service.get_article(1).title, "Synthetic title")
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_revision")
        dialog.submit()
        self.wait_idle(self.window.runner)
        self.assertEqual(workspace.detail_version.text(), "Version 2")
        self.assertEqual(len(self.history()), 2)

    def test_read_only_history_exact_snapshots_and_reconstruction(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KB0001", "Title A")
        workspace = self.window.knowledge_workspace
        first = workspace.article
        initial = workspace.open_version_history()
        self.wait_idle(self.window.runner)
        self.assertEqual([version.version_number for version in initial.versions], [1])
        first_snapshot = initial.version
        self.assertEqual(first_snapshot.body_markdown, first.body_markdown)
        initial.close()
        editor = workspace.open_edit_article()
        editor.title_input.setText("Title B")
        editor.summary_input.setText("Summary B")
        editor.body_input.setPlainText("Body B")
        editor.submit()
        self.wait_idle(self.window.runner)
        editor = workspace.open_edit_article()
        editor.title_input.setText("Title C")
        editor.summary_input.setText("Summary C")
        editor.body_input.setPlainText("Body C")
        editor.submit()
        self.wait_idle(self.window.runner)
        current_before = self.context.knowledge_service.get_article(first.knowledge_article_id)
        history_before = self.history()
        with database_connection(self.path) as connection:
            dump_before = tuple(connection.iterdump())

        dialog = workspace.open_version_history()
        self.wait_idle(self.window.runner)
        self.wait_idle(self.window.runner)
        self.assertEqual([version.version_number for version in dialog.versions], [3, 2, 1])
        self.assertEqual(dialog.version.version_number, 3)
        expected = {
            1: ("Title A", "Synthetic summary", "# Synthetic body\n\n1. Synthetic step."),
            2: ("Title B", "Summary B", "Body B"),
            3: ("Title C", "Summary C", "Body C"),
        }
        for row, number in enumerate((3, 2, 1)):
            dialog.table.selectRow(row)
            self.wait_idle(self.window.runner)
            self.assertEqual(
                (dialog.version.title, dialog.version.summary, dialog.version.body_markdown),
                expected[number],
            )
        dialog.close()
        self.assertEqual(self.context.knowledge_service.get_article(first.knowledge_article_id), current_before)
        self.assertEqual(self.history(), history_before)
        self.assertEqual(
            self.context.knowledge_service.get_article_version(first.knowledge_article_id, 1),
            first_snapshot,
        )
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), dump_before)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)

        reconstructed = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.path)
        restored = reconstructed.main_window
        restored.resize(1000, 700)
        restored.show()
        try:
            self.wait_idle(restored.runner)
            restored.show_knowledge()
            self.wait_idle(restored.runner)
            self.wait_idle(restored.runner)
            restored_workspace = restored.knowledge_workspace
            restored_workspace.open_article_by_id(first.knowledge_article_id)
            self.wait_idle(restored.runner)
            self.wait_idle(restored.runner)
            self.assertEqual(restored_workspace.detail_version.text(), "Version 3")
            reopened = restored_workspace.open_version_history()
            self.wait_idle(restored.runner)
            self.wait_idle(restored.runner)
            self.assertEqual([version.version_number for version in reopened.versions], [3, 2, 1])
            reopened.table.selectRow(2)
            self.wait_idle(restored.runner)
            self.assertEqual(reopened.detail_body.toPlainText(), expected[1][2])
            reopened.close()
        finally:
            restored.close()
            restored.deleteLater()
            self.application.processEvents()

    def test_history_real_missing_revision_and_article_show_safe_feedback(self):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KB0001", "Original")
        workspace = self.window.knowledge_workspace
        dialog = workspace.open_version_history()
        self.wait_idle(self.window.runner)
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_article_versions WHERE knowledge_article_id = 1")
        dialog._load_version(1)
        self.wait_idle(self.window.runner)
        self.assertIn("revision is no longer available", dialog.feedback.text())
        self.assertEqual(dialog.detail_body.toPlainText(), "")
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = 1")
        dialog._load_version(1)
        self.wait_idle(self.window.runner)
        self.assertIn("article no longer exists", dialog.feedback.text())
        self.assertEqual(dialog.detail_body.toPlainText(), "")
        dialog.close()
        dialog = workspace.open_version_history()
        self.wait_idle(self.window.runner)
        self.assertIn("article no longer exists", dialog.feedback.text())
        self.assertEqual(dialog.model.rowCount(), 0)
        dialog.close()

    def test_pending_history_list_close_in_main_window(self):
        self.check_pending_history_dismissal("list_article_versions", "close")

    def test_pending_history_list_escape_in_main_window(self):
        self.check_pending_history_dismissal("list_article_versions", "escape")

    def test_pending_history_detail_close_in_main_window(self):
        self.check_pending_history_dismissal("get_article_version", "close")

    def test_pending_history_detail_escape_in_main_window(self):
        self.check_pending_history_dismissal("get_article_version", "escape")

    def check_pending_history_dismissal(self, method, action):
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        self.create_through_dialog("KBPENDING", "Original")
        workspace = self.window.knowledge_workspace
        current = workspace.article
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        service = self.context.knowledge_service
        original = getattr(service, method)
        entered, release = threading.Event(), threading.Event()

        def delayed(*args):
            entered.set()
            if not release.wait(10):
                raise RuntimeError("Test read gate timed out")
            return original(*args)

        try:
            with patch.object(service, method, side_effect=delayed) as read:
                QTest.mouseClick(workspace.version_history_button, Qt.MouseButton.LeftButton)
                dialog = workspace._version_history_dialog
                deadline = time.monotonic() + 5
                while not entered.is_set() and time.monotonic() < deadline:
                    QTest.qWait(10)
                self.assertTrue(entered.is_set())
                self.assertTrue(self.window.runner.busy)
                self.assertFalse(self.window.pages.isEnabled())
                self.assertFalse(self.window.knowledge_action.isEnabled())
                self.assertFalse(workspace.new_button.isEnabled())
                self.assertFalse(workspace.edit_button.isEnabled())
                self.assertFalse(workspace.version_history_button.isEnabled())
                self.assertIsNone(workspace.open_version_history())
                self.assertFalse(dialog.table.isEnabled())
                self.assertTrue(dialog.close_button.isEnabled())
                if action == "close":
                    QTest.mouseClick(dialog.close_button, Qt.MouseButton.LeftButton)
                else:
                    QTest.keyClick(dialog, Qt.Key.Key_Escape)
                self.assertFalse(dialog.isVisible())
                self.assertTrue(self.window.runner.busy)
                self.assertIsNone(workspace.open_version_history())
                rows, feedback = dialog.model.rowCount(), dialog.feedback.text()
                release.set()
                self.wait_idle(self.window.runner)
                self.assertEqual(read.call_count, 1)
                self.assertFalse(dialog.isVisible())
                self.assertEqual(dialog.model.rowCount(), rows)
                self.assertEqual(dialog.feedback.text(), feedback)
                self.assertIsNone(dialog.version)
                self.assertEqual(dialog.detail_body.toPlainText(), "")
                self.assertEqual(workspace.article, current)
                self.assertTrue(self.window.pages.isEnabled())
                with database_connection(self.path) as connection:
                    self.assertEqual(tuple(connection.iterdump()), before)
        finally:
            release.set()
            self.wait_idle(self.window.runner)
            if hasattr(workspace, "_version_history_dialog"):
                workspace._version_history_dialog.close()

    def test_long_historical_metadata_scrolls_to_end_with_body_visible(self):
        service = self.context.knowledge_service
        summary = 'START-OF-LONG-SUMMARY\n' + '<tag> & "quotes" **literal** ' * 210 + '\nEND-OF-LONG-SUMMARY'
        first = service.create_article(
            article_code="KBLONG", title="Historical title", summary=summary, body="Historical body",
        )
        service.update_article(
            article_id=first.knowledge_article_id, expected_version_number=1,
            title="Current title", summary="Short current summary", body="Current body",
        )
        self.window.show_knowledge()
        self.wait_idle(self.window.runner)
        workspace = self.window.knowledge_workspace
        workspace.open_article_by_id(first.knowledge_article_id)
        self.wait_idle(self.window.runner)
        dialog = workspace.open_version_history()
        self.wait_idle(self.window.runner)
        dialog.resize(900, 620)
        dialog.table.selectRow(1)
        self.wait_idle(self.window.runner)
        try:
            self.assertEqual(dialog.detail_summary.text(), "Summary: " + summary)
            self.assertEqual(dialog.detail_summary.textFormat(), Qt.TextFormat.PlainText)
            self.assertTrue(dialog.detail_body.isReadOnly())
            scroll = dialog.metadata_scroll
            bar = scroll.verticalScrollBar()
            self.assertGreater(bar.maximum(), 0)
            bar.setValue(0)
            QTest.qWait(30)
            label = dialog.detail_summary
            self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()))
            start = label.mapTo(scroll.viewport(), QPoint(0, 0))
            self.assertTrue(scroll.viewport().rect().contains(start))
            bar.setValue(bar.maximum())
            QTest.qWait(30)
            end = label.mapTo(scroll.viewport(), QPoint(0, label.height() - 1))
            self.assertTrue(scroll.viewport().rect().contains(end))
            self.assertGreaterEqual(dialog.detail_body.height(), 150)
            self.assertTrue(dialog.detail_body.isVisible())
            self.assertEqual(dialog.detail_body.toPlainText(), "Historical body")
            self.assertLess(scroll.geometry().bottom(), dialog.detail_body.geometry().top())
            self.assertEqual((dialog.width(), dialog.height()), (900, 620))
            self.assertEqual(workspace.detail_body.toPlainText(), "Current body")
        finally:
            dialog.close()

    def create_through_dialog(self, code, title):
        dialog = self.window.knowledge_workspace.open_new_article()
        dialog.code_input.setText(code)
        dialog.title_input.setText(title)
        dialog.summary_input.setText("Synthetic summary")
        dialog.body_input.setPlainText("# Synthetic body\n\n1. Synthetic step.")
        dialog.submit()
        self.wait_idle(self.window.runner)
        self.wait_idle(self.window.runner)

    @staticmethod
    def wait_idle(runner):
        deadline = time.monotonic() + 5
        while runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        if runner.busy:
            raise AssertionError("Background task did not finish")
        QTest.qWait(10)


if __name__ == "__main__":
    unittest.main()
