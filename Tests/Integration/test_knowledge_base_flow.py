from __future__ import annotations

import os
from pathlib import Path
import tempfile
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
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
