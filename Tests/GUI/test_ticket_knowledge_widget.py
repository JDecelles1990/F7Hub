import os
import threading
import time
from types import SimpleNamespace
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.gui.ticket_workspace import TicketWorkspace
from f7hub.services.ticket_knowledge_service import TicketKnowledgeAlreadyLinkedError
from Tests.GUI.test_knowledge_workspace import RecordingKnowledgeService


class RecordingLinkService:
    def __init__(self):
        self.candidates = [SimpleNamespace(
            knowledge_article_id=2, article_code="KB0002", article_title="<b>Synthetic</b>",
            article_status="DRAFT", article_version_number=1,
        )]
        self.links = []
        self.calls = []
        self.gate = None
        self.error = None
        self.read_error = None
        self.read_gate = None
        self.threads = []

    def list_linked_articles(self, ticket_id):
        self.threads.append(threading.get_ident())
        if self.read_gate:
            self.read_gate.wait(3)
        if self.read_error:
            raise self.read_error
        return tuple(x for x in self.links if x.ticket_id == ticket_id)

    def list_link_candidates(self, ticket_id):
        self.threads.append(threading.get_ident())
        if self.read_gate:
            self.read_gate.wait(3)
        if self.read_error:
            raise self.read_error
        return tuple(self.candidates)

    def link_related_article(self, ticket_id, article_id):
        self.calls.append((ticket_id, article_id))
        self.threads.append(threading.get_ident())
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        article = next(x for x in self.candidates if x.knowledge_article_id == article_id)
        link = SimpleNamespace(**vars(article), ticket_id=ticket_id, relationship_type="RELATED")
        self.links.append(link)
        return link


class TicketKnowledgeWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingLinkService()
        self.runner = ServiceTaskRunner()
        self.workspace = TicketWorkspace(None, self.runner, knowledge_link_service=self.service)
        self.panel = self.workspace.knowledge_tab
        self.workspace.resize(1000, 700)
        self.workspace.show()
        self.application.processEvents()

    def tearDown(self):
        for gate in (self.service.gate, self.service.read_gate):
            if gate:
                gate.set()
        self.wait_idle()
        if self.panel._dialog:
            self.panel._dialog.close()
        self.workspace.close()
        self.workspace.deleteLater()
        self.runner.deleteLater()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.runner.busy and time.monotonic() < deadline:
            QTest.qWait(10)
        self.application.processEvents()
        self.assertFalse(self.runner.busy)

    def open_ticket(self):
        self.workspace.detail_panel.setEnabled(True)
        self.workspace.detail_tabs.setCurrentWidget(self.panel)
        self.panel.set_ticket(1)
        self.panel.refresh_links()
        self.wait_idle()

    def dialog(self):
        self.open_ticket()
        dialog = self.panel.open_link_dialog()
        self.wait_idle()
        return dialog

    def test_tab_and_no_ticket_controls(self):
        self.assertEqual(self.workspace.detail_tabs.tabText(3), "Knowledge")
        self.assertFalse(self.panel.link_button.isEnabled())
        self.assertFalse(self.panel.open_button.isEnabled())
        self.assertIsNone(self.panel.open_link_dialog())
        self.assertEqual(self.service.calls, [])

    def test_empty_links_and_candidate_cancel_writes_nothing(self):
        dialog = self.dialog()
        self.assertEqual(self.panel.feedback.text(), "No knowledge articles linked.")
        self.assertEqual(dialog.table.identity_model.rowCount(), 1)
        self.assertTrue(dialog.link_button.isEnabled())
        dialog.reject()
        dialog.submit()
        self.assertEqual(self.service.calls, [])

    def test_success_refreshes_current_metadata_and_emits_workspace_signal(self):
        dialog = self.dialog()
        requested = []
        self.workspace.knowledge_article_requested.connect(requested.append)
        dialog.submit()
        self.wait_idle()
        self.assertFalse(dialog.isVisible())
        self.assertEqual(self.panel.table.selected_article_id(), 2)
        self.assertEqual([self.panel.table.identity_model.item(0, i).text() for i in range(4)],
                         ["KB0002", "<b>Synthetic</b>", "DRAFT", "1"])
        self.panel.open_selected_article()
        self.assertEqual(requested, [2])
        self.assertTrue(all(x != threading.get_ident() for x in self.service.threads))

    def test_duplicate_submit_and_close_blocked_while_responsive(self):
        dialog = self.dialog()
        self.service.gate = threading.Event()
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
        self.assertFalse(dialog.link_button.isEnabled())
        self.assertFalse(dialog.cancel_button.isEnabled())
        self.assertEqual(self.service.calls, [(1, 2)])
        self.service.gate.set()
        self.wait_idle()
        dialog.submit()
        self.assertEqual(self.service.calls, [(1, 2)])

    def test_failure_retains_selection_and_safe_duplicate_message(self):
        dialog = self.dialog()
        for error in (RuntimeError("Sensitive SQL"), TicketKnowledgeAlreadyLinkedError("This article is already linked to this ticket.")):
            self.service.error = error
            dialog.submit()
            self.wait_idle()
            self.assertEqual(dialog.table.selected_article_id(), 2)
            self.assertTrue(dialog.link_button.isEnabled())
            self.assertNotIn("Sensitive", dialog.feedback.text())
            self.assertEqual(dialog.feedback.textFormat(), Qt.TextFormat.PlainText)
        self.assertIn("already linked", dialog.feedback.text())

    def test_candidates_failure_retry_and_empty_state(self):
        self.open_ticket()
        self.service.read_error = RuntimeError("Sensitive path")
        dialog = self.panel.open_link_dialog()
        self.wait_idle()
        self.assertNotIn("Sensitive", dialog.feedback.text())
        self.assertTrue(dialog.retry_button.isVisible())
        self.assertFalse(dialog.link_button.isEnabled())
        self.service.read_error = None
        self.service.candidates = []
        dialog.load_candidates()
        self.wait_idle()
        self.assertEqual(dialog.feedback.text(), "No articles available to link.")
        self.assertFalse(dialog.link_button.isEnabled())

    def test_cancel_during_candidate_read_ignores_completion(self):
        self.open_ticket()
        self.service.read_gate = threading.Event()
        dialog = self.panel.open_link_dialog()
        dialog.reject()
        self.service.read_gate.set()
        self.wait_idle()
        self.assertFalse(dialog.isVisible())
        self.assertEqual(dialog.table.identity_model.rowCount(), 0)
        self.assertEqual(self.service.calls, [])

    def test_obsolete_ticket_read_does_not_populate_new_ticket(self):
        self.open_ticket()
        self.service.read_gate = threading.Event()
        self.panel.refresh_links()
        self.panel.set_ticket(9)
        self.service.read_gate.set()
        self.wait_idle()
        self.assertEqual(self.panel.table.identity_model.rowCount(), 0)
        self.assertEqual(self.panel.feedback.text(), "")

    def test_committed_link_with_refresh_failure_reports_saved_outcome(self):
        dialog = self.dialog()
        self.service.read_error = RuntimeError("Sensitive SQL")
        dialog.submit()
        self.wait_idle()
        self.assertEqual(len(self.service.links), 1)
        self.assertIn("Article linked.", self.panel.feedback.text())
        self.assertIn("Could not load", self.panel.feedback.text())
        self.assertFalse(self.panel.open_button.isEnabled())
        self.service.read_error = None
        self.panel.refresh_links()
        self.wait_idle()
        self.assertEqual(self.panel.table.identity_model.rowCount(), 1)

    def test_open_by_id_selects_correct_current_article(self):
        service = RecordingKnowledgeService()
        for code in ("KB0001", "KB0002"):
            service.create_article(article_code=code, title=code, summary="", body="Body " + code)
        workspace = KnowledgeWorkspace(service, self.runner, self.workspace)
        workspace.open_article_by_id(1)
        self.wait_idle()
        self.assertEqual(workspace.article.knowledge_article_id, 1)
        self.assertEqual(workspace.detail_body.toPlainText(), "Body KB0001")

    def test_open_by_id_missing_does_not_open_different_article(self):
        service = RecordingKnowledgeService()
        service.create_article(article_code="KB0002", title="Other", summary="", body="Other")
        workspace = KnowledgeWorkspace(service, self.runner, self.workspace)
        for articles in (service.articles, []):
            service.articles = articles
            workspace.open_article_by_id(999)
            self.wait_idle()
            self.assertIsNone(workspace.article)
            self.assertIn("no longer exists", workspace.feedback.text())
            self.assertFalse(workspace.table.selectionModel().selectedRows())

    def test_article_removed_between_list_and_detail_is_safe(self):
        service = RecordingKnowledgeService()
        service.create_article(article_code="KB0001", title="Gone", summary="", body="Gone")
        service.get_article = lambda _: None
        workspace = KnowledgeWorkspace(service, self.runner, self.workspace)
        workspace.open_article_by_id(1)
        self.wait_idle()
        self.assertIsNone(workspace.article)
        self.assertIn("no longer exists", workspace.feedback.text())
