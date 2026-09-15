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
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import database_connection
from f7hub.repositories.ticket_knowledge_repository import TicketKnowledgeRepository
from f7hub.services.ticket_knowledge_service import (
    TicketKnowledgeAlreadyLinkedError, TicketKnowledgeNotLinkedError, TicketKnowledgeService,
)


class TicketKnowledgeFlowTests(unittest.TestCase):
    def confirm_publish(self, workspace, *, accept=True):
        def answer():
            box = QApplication.activeModalWidget()
            if accept:
                next(button for button in box.buttons() if button.text() == "Publish").click()
            else:
                box.button(QMessageBox.StandardButton.Cancel).click()
        QTimer.singleShot(30, answer)
        workspace.publish_button.click()
        self.wait_idle()

    def test_publish_v2_preserves_history_search_link_and_reconstructed_application(self):
        self.link()
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        editor = workspace.open_edit_article()
        editor.body_input.setPlainText("# Reviewed publication procedure V2")
        editor.submit()
        self.wait_idle()
        service = self.context.knowledge_service
        article_id = self.article.knowledge_article_id
        draft = service.get_article(article_id)
        history = tuple(service.get_article_version(article_id, n) for n in (2, 1))
        self.assertEqual([v.version_number for v in service.list_article_versions(article_id)], [2, 1])
        with database_connection(self.path) as connection:
            links = [tuple(row) for row in connection.execute("SELECT * FROM ticket_knowledge_articles WHERE knowledge_article_id = ?", (article_id,))]
        with patch.object(service, "publish_article", wraps=service.publish_article) as publish:
            self.confirm_publish(workspace, accept=False)
            publish.assert_not_called()
        self.assertEqual(service.get_article(article_id), draft)
        workspace.search_input.setText("publication procedure")
        workspace.search_button.click()
        self.wait_idle()
        self.assertEqual(workspace.model.item(0, 2).text(), "DRAFT")
        self.confirm_publish(workspace)
        published = service.get_article(article_id)
        self.assertEqual(workspace.article, published)
        self.assertEqual((published.status, published.version_number), ("PUBLISHED", 2))
        self.assertEqual(published.body_markdown, draft.body_markdown)
        self.assertEqual(published.published_at, published.updated_at)
        self.assertEqual(datetime.fromisoformat(published.published_at).utcoffset().total_seconds(), 0)
        self.assertFalse(workspace.edit_button.isEnabled())
        self.assertFalse(workspace.publish_button.isEnabled())
        self.assertTrue(workspace.version_history_button.isEnabled())
        self.assertIsNone(workspace.open_edit_article())
        self.assertEqual(tuple(service.get_article_version(article_id, n) for n in (2, 1)), history)
        viewer = workspace.open_version_history()
        self.wait_idle()
        self.assertEqual([v.version_number for v in viewer.versions], [2, 1])
        self.assertEqual(viewer.detail_body.toPlainText(), draft.body_markdown)
        viewer.close()
        workspace.search_input.setText("publication procedure")
        workspace.search_button.click()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 1)
        self.assertEqual(workspace.model.item(0, 2).text(), "PUBLISHED")
        self.assertEqual(workspace.article, published)
        self.open_ticket()
        self.assertEqual(self.panel.table.records[0].article_status, "PUBLISHED")
        self.assertEqual(self.assert_open_article(article_id).article, published)
        with database_connection(self.path) as connection:
            self.assertEqual([tuple(row) for row in connection.execute("SELECT * FROM ticket_knowledge_articles WHERE knowledge_article_id = ?", (article_id,))], links)
        self.close_window()
        self.boot()
        self.open_ticket()
        self.assertEqual(self.assert_open_article(article_id).article, published)

    def test_category_v1_v2_lifecycle_search_link_and_reconstruction(self):
        from Tests.Database.test_knowledge_categories import seed_knowledge_categories
        seed_knowledge_categories(self.path)
        self.link()
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        service = self.context.knowledge_service
        article_id = self.article.knowledge_article_id
        with database_connection(self.path) as connection:
            schema = tuple(tuple(row) for row in connection.execute('SELECT * FROM sqlite_master ORDER BY name'))
            links = tuple(tuple(row) for row in connection.execute('SELECT * FROM ticket_knowledge_articles'))
        def category(category_id):
            dialog = workspace.open_category()
            self.wait_idle()
            dialog.category_input.setCurrentIndex(dialog.category_input.findData(category_id))
            dialog.submit()
            self.wait_idle()
            self.assertEqual(workspace.article.category_id, category_id)
        category(11)
        self.assertEqual((workspace.article.status, workspace.article.version_number), ('DRAFT', 1))
        self.assertEqual([v.version_number for v in service.list_article_versions(article_id)], [1])
        editor = workspace.open_edit_article()
        editor.body_input.setPlainText('Category integration procedure V2')
        editor.submit()
        self.wait_idle()
        self.assertEqual(workspace.article.category_id, 11)
        history = tuple(service.get_article_version(article_id, n) for n in (2, 1))
        category(22)
        self.assertEqual(workspace.article.version_number, 2)
        self.confirm_publish(workspace)
        self.assertEqual(workspace.article.category_id, 22)
        self.assertFalse(workspace.category_button.isEnabled())
        self.confirm_archive(workspace)
        archived = workspace.article
        self.assertEqual((archived.category_id, archived.version_number, archived.status), (22, 2, 'ARCHIVED'))
        self.assertFalse(workspace.category_button.isEnabled())
        workspace.search_input.setText('Category integration')
        workspace.search_articles()
        self.wait_idle()
        self.assertEqual(workspace.article, archived)
        self.assertEqual(workspace.model.rowCount(), 1)
        self.open_ticket()
        self.assertEqual(self.assert_open_article(article_id).article, archived)
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(tuple(row) for row in connection.execute('SELECT * FROM ticket_knowledge_articles')), links)
            self.assertEqual(tuple(tuple(row) for row in connection.execute('SELECT * FROM sqlite_master ORDER BY name')), schema)
            connection.execute("INSERT INTO knowledge_articles_fts(knowledge_articles_fts, rank) VALUES ('integrity-check', 1)")
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.close_window()
        self.boot()
        self.open_ticket()
        self.assertEqual(self.assert_open_article(article_id).article, archived)
        self.assertEqual(tuple(self.context.knowledge_service.get_article_version(article_id, n) for n in (2, 1)), history)

    def test_category_same_version_external_update_rejects_reviewed_metadata_token(self):
        from Tests.Database.test_knowledge_categories import seed_knowledge_categories
        from f7hub.repositories.category_repository import CategoryRepository
        from f7hub.repositories.knowledge_repository import KnowledgeRepository
        from f7hub.services.knowledge_service import KnowledgeService
        seed_knowledge_categories(self.path)
        service = self.context.knowledge_service
        current = service.update_article(article_id=self.article.knowledge_article_id,
            expected_version_number=1, title='V2', summary=None, body='Metadata race')
        self.window.show_knowledge()
        self.wait_idle()
        workspace = self.window.knowledge_workspace
        dialog = workspace.open_category()
        self.wait_idle()
        external = KnowledgeService(KnowledgeRepository(self.path), CategoryRepository(self.path))
        latest = external.set_article_category(current.knowledge_article_id, 2, current.updated_at, 22)
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        dialog.category_input.setCurrentIndex(dialog.category_input.findData(11))
        dialog.submit()
        self.wait_idle()
        self.assertIn('Reopen the latest article', dialog.feedback.text())
        self.assertFalse(dialog.save_button.isEnabled())
        self.assertEqual(workspace.article, current)
        self.assertEqual(service.get_article(current.knowledge_article_id), latest)
        self.assertEqual(latest.version_number, 2)
        self.assertEqual([v.version_number for v in service.list_article_versions(current.knowledge_article_id)], [2, 1])
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        dialog.reject()
        workspace.open_article_by_id(current.knowledge_article_id)
        self.wait_idle()
        self.assertEqual(workspace.article, latest)

    def test_stale_publish_through_real_window_rejects_external_revision(self):
        workspace = self.window.knowledge_workspace
        self.window.show_knowledge()
        self.wait_idle()
        latest = self.context.knowledge_service.update_article(
            article_id=self.article.knowledge_article_id, expected_version_number=1,
            title="Externally reviewed", summary=None, body="Concurrent V2",
        )
        self.assertEqual(workspace.article.version_number, 1)
        self.confirm_publish(workspace)
        self.assertIn("Reopen the latest version before publishing", workspace.feedback.text())
        self.assertEqual(workspace.article.status, "DRAFT")
        self.assertEqual(self.context.knowledge_service.get_article(latest.knowledge_article_id), latest)
        self.assertIsNone(latest.published_at)
        self.assertEqual([v.version_number for v in self.context.knowledge_service.list_article_versions(latest.knowledge_article_id)], [2, 1])
        workspace.open_article_by_id(latest.knowledge_article_id)
        self.wait_idle()
        self.assertEqual(workspace.article, latest)

    def test_publish_failure_rolls_back_with_existing_link_and_all_history(self):
        from f7hub.repositories.knowledge_repository import _get_article
        from f7hub.services.knowledge_service import KnowledgePublishError
        self.link()
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        calls = 0
        def fail_after_update(connection, article_id):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("Synthetic failure after UPDATE")
            return _get_article(connection, article_id)
        with patch("f7hub.repositories.knowledge_repository._get_article", side_effect=fail_after_update):
            with self.assertRaises(KnowledgePublishError):
                self.context.knowledge_service.publish_article(self.article.knowledge_article_id, 1)
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def confirm_archive(self, workspace, *, accept=True):
        def answer():
            box = QApplication.activeModalWidget()
            if accept:
                next(button for button in box.buttons() if button.text() == "Archive").click()
            else:
                box.button(QMessageBox.StandardButton.Cancel).click()
        QTimer.singleShot(30, answer)
        workspace.archive_button.click()
        self.wait_idle()

    def test_archive_v2_preserves_publication_history_search_link_and_reconstruction(self):
        self.link()
        workspace = self.assert_open_article(self.article.knowledge_article_id)
        editor = workspace.open_edit_article()
        editor.body_input.setPlainText("# Reviewed archive procedure V2")
        editor.submit()
        self.wait_idle()
        with patch("f7hub.services.knowledge_service.datetime") as clock:
            clock.now.return_value = datetime(2026, 9, 14, 16, 30, tzinfo=timezone.utc)
            self.confirm_publish(workspace)
        service = self.context.knowledge_service
        article_id = self.article.knowledge_article_id
        published = service.get_article(article_id)
        history = tuple(service.get_article_version(article_id, n) for n in (2, 1))
        self.assertEqual((published.status, published.version_number), ("PUBLISHED", 2))
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
            links = [tuple(row) for row in connection.execute("SELECT * FROM ticket_knowledge_articles")]
        with patch.object(service, "archive_article", wraps=service.archive_article) as archive:
            self.confirm_archive(workspace, accept=False)
            archive.assert_not_called()
        self.assertEqual(workspace.article, published)
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        instant = datetime(2026, 9, 15, 16, 30, tzinfo=timezone.utc)
        with patch("f7hub.services.knowledge_service.datetime") as clock:
            clock.now.return_value = instant
            self.confirm_archive(workspace)
        archived = service.get_article(article_id)
        from dataclasses import replace
        self.assertEqual(archived, replace(published, status="ARCHIVED", updated_at="2026-09-15T16:30:00.000Z"))
        self.assertGreaterEqual(archived.updated_at, published.published_at)
        self.assertEqual(workspace.article, archived)
        for button in (workspace.edit_button, workspace.publish_button, workspace.archive_button):
            self.assertFalse(button.isEnabled())
        self.assertTrue(workspace.version_history_button.isEnabled())
        self.assertEqual(tuple(service.get_article_version(article_id, n) for n in (2, 1)), history)
        viewer = workspace.open_version_history()
        self.wait_idle()
        self.assertEqual([v.version_number for v in viewer.versions], [2, 1])
        self.assertEqual(viewer.detail_body.toPlainText(), published.body_markdown)
        viewer.close()
        workspace.search_input.setText("archive procedure")
        workspace.search_button.click()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 1)
        self.assertEqual(workspace.model.item(0, 2).text(), "ARCHIVED")
        self.assertEqual(workspace.article, archived)
        self.open_ticket()
        self.assertEqual(self.panel.table.records[0].article_status, "ARCHIVED")
        self.assertEqual(self.assert_open_article(article_id).article, archived)
        with database_connection(self.path) as connection:
            self.assertEqual([tuple(row) for row in connection.execute("SELECT * FROM ticket_knowledge_articles")], links)
        self.close_window()
        self.boot()
        self.open_ticket()
        self.assertEqual(self.assert_open_article(article_id).article, archived)
        self.assertEqual(tuple(self.context.knowledge_service.get_article_version(article_id, n) for n in (2, 1)), history)

    def test_archive_real_window_rejects_external_version_or_state_change(self):
        service = self.context.knowledge_service
        published = service.publish_article(self.article.knowledge_article_id, 1)
        self.window.show_knowledge()
        self.wait_idle()
        workspace = self.window.knowledge_workspace
        for sql, message in (
            ("UPDATE knowledge_articles SET version_number = 2", "Reopen the latest version before archiving"),
            ("UPDATE knowledge_articles SET status = 'ARCHIVED'", "Only published articles"),
        ):
            with database_connection(self.path) as connection:
                connection.execute(sql)
                before = tuple(connection.iterdump())
            self.assertEqual(workspace.article, published)
            self.confirm_archive(workspace)
            self.assertIn(message, workspace.feedback.text())
            self.assertEqual(workspace.article, published)
            with database_connection(self.path) as connection:
                self.assertEqual(tuple(connection.iterdump()), before)
        workspace.open_article_by_id(published.knowledge_article_id)
        self.wait_idle()
        self.assertEqual(workspace.article.status, "ARCHIVED")
        self.assertFalse(workspace.archive_button.isEnabled())

    def test_archive_busy_in_real_main_window_blocks_competing_actions(self):
        import threading
        service = self.context.knowledge_service
        published = service.publish_article(self.article.knowledge_article_id, 1)
        self.window.show_knowledge()
        self.wait_idle()
        workspace = self.window.knowledge_workspace
        entered, release = threading.Event(), threading.Event()
        calls = []
        original = service.archive_article
        def delayed(article_id, version):
            calls.append((article_id, version, threading.get_ident()))
            entered.set()
            if not release.wait(10):
                raise RuntimeError("Archive test gate timed out")
            return original(article_id, version)
        try:
            with patch.object(service, "archive_article", side_effect=delayed):
                with patch.object(workspace, "_confirm_archive", return_value=True):
                    workspace.archive_button.click()
                    deadline = time.monotonic() + 5
                    while not entered.is_set() and time.monotonic() < deadline:
                        QTest.qWait(10)
                    self.assertTrue(entered.is_set())
                    self.assertFalse(self.window.pages.isEnabled())
                    self.assertFalse(self.window.knowledge_action.isEnabled())
                    for button in (workspace.edit_button, workspace.publish_button, workspace.archive_button,
                                   workspace.new_button, workspace.version_history_button, workspace.search_button):
                        self.assertFalse(button.isEnabled())
                    workspace.archive_article()
                    workspace.publish_article()
                    self.assertIsNone(workspace.open_edit_article())
                    self.assertEqual(workspace.article, published)
                    self.assertEqual(service.get_article(published.knowledge_article_id), published)
                    release.set()
                    self.wait_idle()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][:2], (published.knowledge_article_id, 1))
            self.assertNotEqual(calls[0][2], threading.get_ident())
            self.assertEqual(workspace.article.status, "ARCHIVED")
            self.assertTrue(self.window.pages.isEnabled())
            self.assertTrue(workspace.version_history_button.isEnabled())
        finally:
            release.set()
            self.wait_idle()

    def test_archive_failure_rolls_back_with_existing_link_and_history(self):
        from f7hub.repositories.knowledge_repository import _get_article
        from f7hub.services.knowledge_service import KnowledgeArchiveError
        self.link()
        self.context.knowledge_service.publish_article(self.article.knowledge_article_id, 1)
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        calls = 0
        def fail_after_update(connection, article_id):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.assertEqual(_get_article(connection, article_id).status, "ARCHIVED")
                raise RuntimeError("Synthetic failure after UPDATE")
            return _get_article(connection, article_id)
        with patch("f7hub.repositories.knowledge_repository._get_article", side_effect=fail_after_update):
            with self.assertRaises(KnowledgeArchiveError):
                self.context.knowledge_service.archive_article(self.article.knowledge_article_id, 1)
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

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

    def test_knowledge_search_is_independent_of_ticket_open_article_navigation(self):
        self.link()
        self.window.show_knowledge()
        self.wait_idle()
        workspace = self.window.knowledge_workspace
        workspace.search_input.setText("Windows spooler")
        workspace.search_button.click()
        self.wait_idle()
        self.wait_idle()
        self.assertEqual(workspace.article.knowledge_article_id, self.article.knowledge_article_id)
        self.window.show_tickets()
        self.wait_idle()
        self.assert_open_article(self.article.knowledge_article_id)
        self.assertEqual(workspace.search_input.text(), "")
        self.assertEqual(workspace.detail_body.toPlainText(), "# Synthetic procedure")

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
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)

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
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)

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
