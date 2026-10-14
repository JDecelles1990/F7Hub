"""S003 routes share one guarded Guide command and retain workspace state."""
from __future__ import annotations

import os
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton

from f7hub.gui.main_window import MainWindow
from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.services.altf7hub_service import AltF7HubOpenError, AltF7HubService
from Tests.GUI.test_main_window import RecordingTicketService
from Tests.GUI.test_knowledge_workspace import RecordingKnowledgeService


class RecordingGuideGateway:
    def __init__(self):
        self.calls = 0
        self.gate = None
        self.error = None
        self.outcome = "SHOWN"

    def show_guide(self):
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        return self.outcome


class GuideRelocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.gateway = RecordingGuideGateway()
        self.knowledge = RecordingKnowledgeService()
        self.windows = []
        self.window = self.make_window(knowledge_service=self.knowledge)

    def make_window(self, **kwargs):
        window = MainWindow(RecordingTicketService(),
                            altf7hub_service=AltF7HubService(self.gateway), **kwargs)
        self.windows.append(window)
        window.show()
        self.app.processEvents()
        self.wait_idle(window)
        return window

    def wait_idle(self, window=None):
        window = window or self.window
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self.app.processEvents()
            kb = window.knowledge_workspace
            runners = [window.runner]
            if kb:
                runners += [kb._filter_runner, kb._tag_filter_runner]
            if not any(r.busy or r.completing for r in runners):
                return
            QTest.qWait(5)
            time.sleep(0.001)
        self.fail("Guide/workspace workers did not become idle")

    def tearDown(self):
        if self.gateway.gate:
            self.gateway.gate.set()
        for window in self.windows:
            self.wait_idle(window)
            window.workspace._clear_drafts()
            window.ticket_create_widget.reset_form()
            window.close()
            window.deleteLater()
        self.app.processEvents()

    def test_routes_share_existing_action_without_global_button(self):
        w = self.window
        action = w.altf7hub_action
        self.assertEqual((action.text(), action.objectName()), ("Guide", "altF7HubGuideAction"))
        self.assertIs(w.knowledge_workspace.guide_button.defaultAction(), action)
        self.assertEqual(w.knowledge_tools_menu.title(), "Knowledge Base tools")
        self.assertEqual(w.knowledge_tools_menu.actions(), [action])
        self.assertIn(w.knowledge_tools_menu.menuAction(), w.utility_menu.actions())
        self.assertIs(w.knowledge_tools_menu.parent(), w.utility_menu)
        self.assertIsNone(w.menuWidget())
        for toolbar in w.findChildren(QToolBar):
            self.assertNotIn(action, toolbar.actions())
        self.assertEqual(w.knowledge_workspace.findChildren(QToolButton, "knowledgeGuideButton"),
                         [w.knowledge_workspace.guide_button])

    def test_kb_click_preserves_article_search_filters_ticket_and_page(self):
        article = self.knowledge.create_article(article_code="KB-S003", title="Synthetic Guide",
                                                summary="Fixture", body="Retained article body")
        w = self.window
        w.ticket_create_widget.subject_input.setText("Unsaved Ticket S003")
        w.ticket_create_widget.description_input.setPlainText("Retained Ticket description")
        w.show_knowledge()
        self.wait_idle()
        kb = w.knowledge_workspace
        kb.search_input.setText("Synthetic")
        kb.search_button.click()
        self.wait_idle()
        kb.table.selectRow(0)
        self.wait_idle()
        self.assertEqual(kb.article.knowledge_article_id, article.knowledge_article_id)
        before = (kb.article, kb.search_input.text(), kb._search_query, kb._search_active,
                  kb.category_filter.currentData(), kb.status_filter.currentData(),
                  kb.tag_filter.currentData(), kb.table.currentIndex().row(),
                  kb.detail_body.toPlainText(), w.pages.currentWidget(), w.pages.count())
        QTest.mouseClick(kb.guide_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        after = (kb.article, kb.search_input.text(), kb._search_query, kb._search_active,
                 kb.category_filter.currentData(), kb.status_filter.currentData(),
                 kb.tag_filter.currentData(), kb.table.currentIndex().row(),
                 kb.detail_body.toPlainText(), w.pages.currentWidget(), w.pages.count())
        self.assertEqual(after, before)
        self.assertEqual(self.gateway.calls, 1)
        self.assertEqual(w.ticket_create_widget.subject_input.text(), "Unsaved Ticket S003")
        self.assertEqual(w.ticket_create_widget.description_input.toPlainText(), "Retained Ticket description")

    def test_independent_fallback_when_knowledge_not_composed(self):
        w = self.make_window()
        self.assertIsNone(w.knowledge_workspace)
        self.assertFalse(w.knowledge_action.isEnabled())
        self.assertTrue(w.knowledge_tools_menu.menuAction().isEnabled())
        w.knowledge_tools_menu.actions()[0].trigger()
        self.wait_idle(w)
        self.assertEqual(self.gateway.calls, 1)

    def test_guide_survives_article_load_failure(self):
        with patch.object(self.knowledge, "list_articles", side_effect=RuntimeError("fixture unavailable")):
            self.window.show_knowledge()
            self.wait_idle()
        self.assertTrue(self.window.knowledge_workspace.feedback.text())
        self.window.knowledge_workspace.guide_button.click()
        self.wait_idle()
        self.assertEqual(self.gateway.calls, 1)

    def test_independent_fallback_when_knowledge_construction_fails(self):
        class BrokenWorkspace(KnowledgeWorkspace):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                raise RuntimeError("private construction detail")

        with patch("f7hub.gui.main_window.KnowledgeWorkspace",
                   BrokenWorkspace), self.assertLogs(
                       "f7hub.gui.main_window", level="WARNING") as logs:
            w = self.make_window(knowledge_service=self.knowledge)
        self.assertIsNone(w.knowledge_workspace)
        self.assertFalse(w.findChildren(KnowledgeWorkspace))
        self.assertFalse(w.knowledge_action.isEnabled())
        self.assertIn("Knowledge Base is unavailable", w.knowledge_action.toolTip())
        self.assertNotIn("private construction detail", " ".join(logs.output))
        self.assertTrue(w.knowledge_tools_menu.menuAction().isEnabled())
        w.knowledge_tools_menu.actions()[0].trigger()
        self.wait_idle(w)
        self.assertEqual(self.gateway.calls, 1)

    def test_busy_routes_dispatch_once_and_recover(self):
        self.gateway.gate = threading.Event()
        w = self.window
        w.show_knowledge()
        self.wait_idle()
        w.knowledge_workspace.guide_button.click()
        w.knowledge_tools_menu.actions()[0].trigger()
        w.show_altf7hub()
        self.assertTrue(w.runner.busy)
        self.assertFalse(w.altf7hub_action.isEnabled())
        self.assertFalse(w.knowledge_workspace.guide_button.isEnabled())
        self.gateway.gate.set()
        self.wait_idle()
        self.assertEqual(self.gateway.calls, 1)
        self.assertTrue(w.knowledge_workspace.guide_button.isEnabled())

    def test_ticket_pending_guards_apply_to_both_routes(self):
        w = self.window
        for field in ("_note_pending", "_creation_pending", "status_pending", "classification_pending"):
            with self.subTest(field=field):
                with patch.object(w.workspace, field, True):
                    w._set_busy(False)
                    self.assertFalse(w.altf7hub_action.isEnabled())
                    w.show_altf7hub()
                    self.assertEqual(self.gateway.calls, 0)
                w._set_busy(False)

    def test_unavailable_guide_is_disabled_on_both_routes(self):
        w = self.window
        w.altf7hub_service = None
        w._set_busy(False)
        self.assertFalse(w.altf7hub_action.isEnabled())
        self.assertFalse(w.knowledge_workspace.guide_button.isEnabled())
        w.show_altf7hub()
        self.assertEqual(self.gateway.calls, 0)

    def test_keyboard_activation_editor_feedback_and_safe_failure(self):
        w = self.window
        w.show_knowledge()
        self.wait_idle()
        button = w.knowledge_workspace.guide_button
        self.assertEqual(button.accessibleName(), "Guide")
        self.assertEqual(button.focusPolicy(), Qt.FocusPolicy.StrongFocus)
        self.gateway.outcome = "FOCUSED_EDITOR"
        button.setFocus()
        self.app.processEvents()
        self.assertTrue(button.hasFocus())
        QTest.keyClick(button, Qt.Key.Key_Tab)
        self.assertTrue(w.knowledge_workspace.new_button.hasFocus())
        QTest.keyClick(w.knowledge_workspace.new_button, Qt.Key.Key_Backtab)
        self.assertTrue(button.hasFocus())
        QTest.keyClick(button, Qt.Key.Key_Space)
        self.wait_idle()
        self.assertEqual(self.gateway.calls, 1)
        self.assertEqual(w.statusBar().currentMessage(), "Guide editor focused.")
        self.gateway.error = AltF7HubOpenError("Synthetic unconfirmed request; use Alt+F7.")
        with patch("f7hub.gui.main_window.QMessageBox.warning") as warning:
            button.click()
            self.wait_idle()
        self.assertEqual(warning.call_args.args[1], "Guide could not open")
        self.assertIn("not confirmed", w.statusBar().currentMessage())
        self.assertTrue(button.isEnabled())

    def test_guide_reachable_in_compact_standard_and_desktop_layouts(self):
        w = self.window
        w.show_knowledge()
        self.wait_idle()
        for width, height in ((660, 592), (1000, 700), (1180, 850)):
            with self.subTest(size=(width, height)):
                w.resize(width, height)
                self.app.processEvents()
                self.assertEqual((w.width(), w.height()), (width, height))
                button = w.knowledge_workspace.guide_button
                for corner in (button.rect().topLeft(), button.rect().bottomRight()):
                    point = button.mapTo(w.pages, corner)
                    w.workspace_viewport.ensureVisible(point.x(), point.y(), 1, 1)
                    self.app.processEvents()
                    self.assertTrue(w.workspace_viewport.viewport().rect().contains(
                        button.mapTo(w.workspace_viewport.viewport(), corner)))
