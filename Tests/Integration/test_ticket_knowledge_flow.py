import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from threading import Barrier
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from f7hub.repositories.ticket_knowledge_repository import TicketKnowledgeRepository
from f7hub.services.ticket_knowledge_service import (
    TicketKnowledgeAlreadyLinkedError, TicketKnowledgeNotLinkedError, TicketKnowledgeService,
)


class TicketKnowledgeFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "ticket-knowledge.db"
        self.boot()
        self.ticket = self.context.ticket_service.create_ticket(subject="Synthetic printer ticket")
        self.article = self.context.knowledge_service.create_article(
            article_code="KB0001", title="Reset a Windows print spooler", summary=None, body="# Synthetic procedure",
        )

    def boot(self):
        self.context = bootstrap_application(project_root=Path(__file__).resolve().parents[2], database_path=self.path)
        self.window = self.context.main_window
        self.window.resize(1000, 700)
        self.window.show()
        self.wait_idle()
        self.panel = self.window.workspace.knowledge_tab

    def tearDown(self):
        self.close_window()
        self.temp.cleanup()

    def close_window(self):
        self.wait_idle()
        if self.panel._dialog:
            self.panel._dialog.close()
        self.window.workspace._clear_drafts()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        self.application.processEvents()
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(10)
        self.application.processEvents()
        self.assertFalse(self.window.runner.busy)

    def open_ticket(self):
        self.window.show_tickets()
        self.wait_idle()
        self.window.workspace.open_ticket(self.ticket.ticket_id)
        self.wait_idle()
        self.window.workspace.detail_tabs.setCurrentWidget(self.panel)

    def link_dialog(self, article_id=None):
        self.open_ticket()
        dialog = self.panel.open_link_dialog()
        self.wait_idle()
        if article_id is not None:
            row = next(i for i, record in enumerate(dialog.table.records) if record.knowledge_article_id == article_id)
            dialog.table.selectRow(row)
        return dialog

    def link(self, article_id=None):
        dialog = self.link_dialog(article_id)
        dialog.submit()
        self.wait_idle()
        self.assertFalse(dialog.isVisible())

    def assert_open_article(self, article_id):
        row = next(i for i, record in enumerate(self.panel.table.records) if record.knowledge_article_id == article_id)
        self.panel.table.selectRow(row)
        self.panel.open_button.click()
        self.wait_idle()
        workspace = self.window.knowledge_workspace
        self.assertIs(self.window.pages.currentWidget(), workspace)
        self.assertEqual(workspace.article.knowledge_article_id, article_id)
        self.assertEqual(workspace.model.item(workspace.table.currentIndex().row(), 0).text(), workspace.article.article_code)
        return workspace

    def count(self):
        with database_connection(self.path) as connection:
            return connection.execute("SELECT count(*) FROM ticket_knowledge_articles").fetchone()[0]

    def test_link_read_and_second_article_navigation(self):
        before = self.context.ticket_service.get_ticket_details(self.ticket.ticket_id)
        self.link()
        self.assertEqual(self.count(), 1)
        link = self.panel.table.records[0]
        self.assertEqual((link.ticket_id, link.knowledge_article_id, link.relationship_type),
                         (self.ticket.ticket_id, self.article.knowledge_article_id, "RELATED"))
        self.assertTrue(link.linked_at.endswith("Z"))
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        self.assertEqual(workspace.detail_body.toPlainText(), "# Synthetic procedure")
        self.assertEqual(workspace.detail_version.text(), "Version 1")
        second = self.context.knowledge_service.create_article(article_code="KB0002", title="Second", summary=None, body="Second body")
        self.link(second.knowledge_article_id)
        self.assertEqual(self.count(), 2)
        self.assertEqual([x.article_code for x in self.panel.table.records], ["KB0001", "KB0002"])
        self.assertEqual(self.assert_open_article(second.knowledge_article_id).detail_body.toPlainText(), "Second body")
        self.assertEqual(self.context.ticket_service.get_ticket_details(self.ticket.ticket_id), before)

    def test_duplicate_after_candidate_load_is_safe_and_keeps_one_row(self):
        dialog = self.link_dialog()
        service = self.context.ticket_knowledge_service
        service.link_related_article(self.ticket.ticket_id, self.article.knowledge_article_id)
        dialog.submit()
        self.wait_idle()
        self.assertEqual(dialog.feedback.text(), "This article is already linked to this ticket.")
        self.assertEqual(dialog.table.selected_article_id(), self.article.knowledge_article_id)
        self.assertEqual(self.count(), 1)
        with self.assertRaises(TicketKnowledgeAlreadyLinkedError):
            service.link_related_article(self.ticket.ticket_id, self.article.knowledge_article_id)

    def test_edit_refresh_and_reconstruction_reads_persisted_current_article(self):
        self.link()
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        editor = workspace.open_edit_article()
        editor.title_input.setText("Revised spooler procedure")
        editor.body_input.setPlainText("Updated synthetic procedure")
        editor.submit()
        self.wait_idle()
        self.open_ticket()
        self.assertEqual((self.panel.table.records[0].article_title, self.panel.table.records[0].article_version_number),
                         ("Revised spooler procedure", 2))
        self.close_window()
        self.boot()
        self.open_ticket()
        self.assertEqual(self.panel.table.records[0].article_title, "Revised spooler procedure")
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        self.assertEqual(workspace.detail_version.text(), "Version 2")
        self.assertEqual(workspace.detail_body.toPlainText(), "Updated synthetic procedure")
        history_dialog = workspace.open_version_history()
        self.wait_idle()
        self.wait_idle()
        self.assertEqual([version.version_number for version in history_dialog.versions], [2, 1])
        history_dialog.table.selectRow(1)
        self.wait_idle()
        self.assertEqual(history_dialog.detail_body.toPlainText(), "# Synthetic procedure")
        self.assertEqual(workspace.detail_body.toPlainText(), "Updated synthetic procedure")
        history_dialog.close()
        self.assertEqual(self.count(), 1)

    def test_article_deleted_after_candidates_loaded_is_rejected(self):
        dialog = self.link_dialog()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (self.article.knowledge_article_id,))
        dialog.submit()
        self.wait_idle()
        self.assertEqual(dialog.feedback.text(), "This article no longer exists.")
        self.assertEqual(self.count(), 0)

    def test_ticket_deleted_after_candidates_loaded_is_rejected(self):
        dialog = self.link_dialog()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM tickets WHERE ticket_id = ?", (self.ticket.ticket_id,))
        dialog.submit()
        self.wait_idle()
        self.assertEqual(dialog.feedback.text(), "This ticket no longer exists.")
        self.assertEqual(self.count(), 0)

    def test_article_deleted_after_link_list_loaded_has_safe_navigation_and_cascade(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (self.article.knowledge_article_id,))
        self.panel.open_selected_article()
        self.wait_idle()
        self.assertIs(self.window.pages.currentWidget(), self.window.knowledge_workspace)
        self.assertIsNone(self.window.knowledge_workspace.article)
        self.assertIn("no longer exists", self.window.knowledge_workspace.feedback.text())
        self.open_ticket()
        self.assertEqual(self.panel.table.records, ())
        self.assertEqual(self.count(), 0)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)

    def test_navigation_respects_unsaved_ticket_activity(self):
        self.link()
        self.window.workspace.note_input.setPlainText("Unsaved synthetic note")
        with patch.object(self.window.workspace, "confirm_discard", return_value=False):
            self.panel.open_selected_article()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertEqual(self.window.workspace.note_input.toPlainText(), "Unsaved synthetic note")

    def unlink(self, article_id=None, *, confirmed=True):
        target = self.article.knowledge_article_id if article_id is None else article_id
        row = next(i for i, record in enumerate(self.panel.table.records) if record.knowledge_article_id == target)
        self.panel.table.selectRow(row)
        with patch.object(self.panel, "_confirm_unlink", return_value=confirmed):
            self.panel.unlink_button.click()
        self.wait_idle()

    def test_unlink_preserves_entities_other_link_and_activity_reconstruction_and_exact_open(self):
        self.link()
        second = self.context.knowledge_service.create_article(article_code="KB0002", title="Second", summary=None, body="Second body")
        self.link(second.knowledge_article_id)
        self.context.knowledge_service.update_article(article_id=second.knowledge_article_id, expected_version_number=1,
                                                      title="Current second", summary=None, body="Current second body")
        before = self.context.ticket_service.get_ticket_details(self.ticket.ticket_id)
        self.unlink()
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.context.ticket_service.get_ticket_details(self.ticket.ticket_id), before)
        self.assertEqual(self.context.knowledge_service.get_article(self.article.knowledge_article_id), self.article)
        self.assertEqual([x.knowledge_article_id for x in self.panel.table.records], [second.knowledge_article_id])
        self.assertEqual(self.panel.feedback.text(), "Article unlinked.")
        self.close_window()
        self.boot()
        self.open_ticket()
        self.assertEqual([x.knowledge_article_id for x in self.panel.table.records], [second.knowledge_article_id])
        workspace = self.assert_open_article(second.knowledge_article_id)
        self.assertEqual(workspace.detail_version.text(), "Version 2")
        self.assertEqual(workspace.detail_body.toPlainText(), "Current second body")
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 5)

    def test_unlink_candidate_reappears_and_relink_has_new_timestamp_and_one_row(self):
        with patch("f7hub.services.ticket_knowledge_service.datetime") as clock:
            clock.now.return_value = datetime(2026, 9, 7, 10, 0, tzinfo=timezone.utc)
            self.link()
        original_timestamp = self.panel.table.records[0].linked_at
        self.unlink()
        self.assertEqual(self.count(), 0)
        dialog = self.panel.open_link_dialog()
        self.wait_idle()
        self.assertEqual([x.knowledge_article_id for x in dialog.table.records], [self.article.knowledge_article_id])
        with patch("f7hub.services.ticket_knowledge_service.datetime") as clock:
            clock.now.return_value = datetime(2026, 9, 7, 11, 0, tzinfo=timezone.utc)
            dialog.link_button.click()
            self.wait_idle()
        self.assertEqual(self.count(), 1)
        self.assertNotEqual(self.panel.table.records[0].linked_at, original_timestamp)
        self.assertEqual(self.panel.table.records[0].linked_at, "2026-09-07T11:00:00.000Z")
        self.assertTrue(self.panel.unlink_button.isEnabled())
        self.assert_open_article(self.article.knowledge_article_id)

    def test_unlink_cancel_preserves_relationship_and_selected_article(self):
        self.link()
        original = self.panel.table.records
        with patch.object(self.context.ticket_knowledge_service, "unlink_related_article") as unlink:
            self.unlink(confirmed=False)
            unlink.assert_not_called()
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.panel.table.records, original)
        self.assertEqual(self.panel.table.selected_article_id(), self.article.knowledge_article_id)

    def test_unlink_concurrent_independent_services_return_one_safe_not_linked(self):
        self.link()
        services = [TicketKnowledgeService(TicketKnowledgeRepository(self.path)) for _ in range(2)]
        gate = Barrier(2)
        def attempt(service):
            gate.wait(timeout=5)
            try:
                service.unlink_related_article(self.ticket.ticket_id, self.article.knowledge_article_id)
                return "unlinked"
            except TicketKnowledgeNotLinkedError as error:
                return str(error)
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, services))
        self.assertCountEqual(outcomes, ["unlinked", "This article is no longer linked to this ticket. Refresh the linked articles."])
        self.assertEqual(self.count(), 0)
        self.assertIsNotNone(self.context.ticket_service.get_ticket_details(self.ticket.ticket_id))
        self.assertEqual(self.context.knowledge_service.get_article(self.article.knowledge_article_id), self.article)

    def test_unlink_stale_relationship_reports_not_linked_and_refresh_reconciles(self):
        self.link()
        self.context.ticket_knowledge_service.unlink_related_article(self.ticket.ticket_id, self.article.knowledge_article_id)
        self.unlink()
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.panel.table.selected_article_id(), self.article.knowledge_article_id)
        self.assertIn("no longer linked", self.panel.feedback.text())
        self.panel.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.panel.table.records, ())

    def test_unlink_deleted_article_returns_safe_missing_feedback_and_preserves_ticket(self):
        self.link()
        before = self.context.ticket_service.get_ticket_details(self.ticket.ticket_id)
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM knowledge_articles WHERE knowledge_article_id = ?", (self.article.knowledge_article_id,))
        self.unlink()
        self.assertEqual(self.panel.feedback.text(), "This article no longer exists.")
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.context.ticket_service.get_ticket_details(self.ticket.ticket_id), before)
        self.panel.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.panel.table.records, ())

    def test_unlink_deleted_ticket_returns_safe_missing_feedback_and_preserves_article(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM tickets WHERE ticket_id = ?", (self.ticket.ticket_id,))
        self.unlink()
        self.assertEqual(self.panel.feedback.text(), "This ticket no longer exists.")
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.context.knowledge_service.get_article(self.article.knowledge_article_id), self.article)

    def test_unlink_persistence_failure_keeps_relationship_and_safe_retry(self):
        self.link()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_unlink AFTER DELETE ON ticket_knowledge_articles BEGIN SELECT RAISE(FAIL, 'Sensitive SQL'); END")
        self.unlink()
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.panel.table.selected_article_id(), self.article.knowledge_article_id)
        self.assertIn("Could not unlink", self.panel.feedback.text())
        self.assertNotIn("Sensitive", self.panel.feedback.text())
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_unlink")
        self.unlink()
        self.assertEqual(self.count(), 0)

    def test_unlink_committed_refresh_failure_does_not_repeat_delete(self):
        self.link()
        service = self.context.ticket_knowledge_service
        with patch.object(service, "unlink_related_article", wraps=service.unlink_related_article) as unlink:
            with patch.object(service, "list_linked_articles", side_effect=RuntimeError("Sensitive read failure")):
                self.unlink()
            self.assertEqual(self.count(), 0)
            self.assertIn("Article unlinked.", self.panel.feedback.text())
            self.assertNotIn("Could not unlink", self.panel.feedback.text())
            self.assertNotIn("Sensitive", self.panel.feedback.text())
            self.assertTrue(self.panel.refresh_button.isEnabled())
            self.panel.refresh_button.click()
            self.wait_idle()
            unlink.assert_called_once_with(self.ticket.ticket_id, self.article.knowledge_article_id)
        self.assertEqual(self.panel.table.records, ())
