"""Embedded lab invariants with disposable real sessions and bounded worker gates."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from contextlib import closing
from pathlib import Path
import sqlite3
import threading
import time
import unittest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest, QSignalSpy
from PySide6.QtWidgets import QApplication, QTabBar, QMessageBox
from f7hub.gui.knowledge_workspace import KnowledgeWorkspace
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.kb_lab_session import SyntheticLabSession
from Tests.GUI.test_knowledge_workspace import RecordingKnowledgeService

ROOT = Path(__file__).resolve().parents[2]

def wait_for(app, predicate, seconds=6):
    deadline = time.monotonic() + seconds
    while not predicate():
        app.processEvents()
        if time.monotonic() >= deadline:
            raise AssertionError("Bounded lab condition did not complete")
        QTest.qWait(5)
        time.sleep(.001)  # Yield the GIL to the real Python/QThread setup worker.
    app.processEvents()

class LabFixture:
    """Shared fixture helper, not a second test case or editor."""
    def __init__(self, app, factory=None):
        self.app = app
        self.owners = []
        self.gates = []
        self.runner = ServiceTaskRunner()
        self.service = RecordingKnowledgeService()
        def reserve():
            owner = factory() if factory else SyntheticLabSession(ROOT)
            self.owners.append(owner)
            return owner
        self.widget = KnowledgeWorkspace(self.service, self.runner, lab_session_factory=reserve)
        self.widget.resize(1180, 800)
        self.widget.show()
        self.widget.activateWindow()
        app.processEvents()

    def idle(self):
        runner = self.widget._lab_runner
        wait_for(self.app, lambda: not runner.busy and not runner.completing)

    def ready(self):
        self.widget.open_synthetic_kb_lab()
        wait_for(self.app, lambda: self.widget._lab_state == "OPEN")
        self.idle()
        return self.widget.lab_editor

    def cleanup(self):
        for gate in self.gates:
            gate.set()
        self.idle()
        wait_for(self.app, lambda: not self.runner.busy and not self.runner.completing
                 and not self.widget.filter_loading)
        if self.widget.lab_editor is not None:
            self.widget.lab_editor._confirm_discard = lambda: True
        if self.widget._lab_tab is not None:
            self.widget.close_synthetic_kb_lab()
            wait_for(self.app, lambda: self.widget._lab_tab is None or self.widget._lab_state == "FAILED")
            self.idle()
        # Test-only explicit disposal of our exact synthetic residues after injected failure ends.
        for owner in self.owners:
            if not owner.cleanup_complete:
                owner.close()
        self.widget.hide()
        self.widget.deleteLater()
        self.runner.deleteLater()
        self.app.processEvents()

class EmbeddedLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.fixture = LabFixture(self.app)
        self.widget = self.fixture.widget

    def tearDown(self):
        self.fixture.cleanup()

    def test_toolbar_accessibility_permanent_articles_and_lazy_start(self):
        button = self.widget.open_synthetic_kb_lab_button
        self.assertEqual(button.text(), "Open Synthetic KB Lab")
        self.assertEqual(button.objectName(), "open_synthetic_kb_lab_button")
        self.assertTrue(button.accessibleName() and button.accessibleDescription())
        self.assertIn("synthetic", button.toolTip())
        self.assertEqual(self.widget.knowledge_tabs.count(), 1)
        for side in (QTabBar.ButtonPosition.LeftSide, QTabBar.ButtonPosition.RightSide):
            self.assertIsNone(self.widget.knowledge_tabs.tabBar().tabButton(0, side))
        self.widget._close_knowledge_tab(0)
        self.assertEqual(self.widget.knowledge_tabs.count(), 1)
        self.assertEqual(self.fixture.owners, [])

    def test_keyboard_activation_one_embedded_editor_and_parentage(self):
        button = self.widget.open_synthetic_kb_lab_button
        button.setFocus()
        QTest.keyClick(button, Qt.Key.Key_Space)
        wait_for(self.app, lambda: self.widget._lab_state == "OPEN")
        editor = self.widget.lab_editor
        self.assertFalse(editor.isWindow())
        self.assertIs(editor.window(), self.widget)
        self.assertTrue(self.widget._lab_tab.isAncestorOf(editor))
        self.assertFalse(any(w.windowTitle() == "Synthetic Knowledge Lab" for w in QApplication.topLevelWidgets()))
        self.widget.open_synthetic_kb_lab()
        self.assertIs(self.widget.lab_editor, editor)
        self.assertEqual(len(self.fixture.owners), 1)
        self.assertEqual(self.widget.knowledge_tabs.count(), 2)
        self.assertIs(QApplication.focusWidget(), editor.fixture_selector)

    def test_navigation_preserves_all_fields_identity_selection_and_undo(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(2)
        editor.title_input.insert(" retained")
        editor.summary_input.insert(" summary")
        editor.body_input.insertPlainText(" body")
        editor.annotations_input.insertPlainText(" annotation")
        editor.title_input.setSelection(1, 4)
        before = (editor._preview, editor.source_display.toPlainText(), editor._baseline,
                  tuple(editor._value(e) for e in editor._editors.values()))
        with patch.object(self.fixture.service, "list_articles", side_effect=AssertionError("No refresh on lab return")):
            self.widget.knowledge_tabs.setCurrentIndex(0)
            self.widget.knowledge_tabs.setCurrentIndex(1)
            self.app.processEvents()
        self.assertIs(self.widget.lab_editor, editor)
        self.assertEqual((editor._preview, editor.source_display.toPlainText(), editor._baseline,
                          tuple(editor._value(e) for e in editor._editors.values())), before)
        self.assertEqual(editor.title_input.selectedText(), before[3][0][1:5])
        self.assertTrue(editor.dirty)
        self.assertTrue(editor.body_input.document().isUndoAvailable())
        editor.body_input.undo()
        self.assertNotEqual(editor.body_input.toPlainText(), before[3][2])

    def test_cancel_tab_x_and_editor_close_preserve_complete_session(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        editor.title_input.insert(" dirty")
        before = editor.title_input.text()
        owner = self.widget._lab_owner
        with patch.object(editor, "_confirm_discard", return_value=False):
            self.widget._close_knowledge_tab(1)
            editor.close_button.click()
        self.assertIs(self.widget.lab_editor, editor)
        self.assertEqual(editor.title_input.text(), before)
        self.assertFalse(owner.terminal)
        self.assertTrue(owner.allocated_root.exists())
        self.assertTrue(editor.title_input.isUndoAvailable())

    def test_discard_clear_once_cleanup_and_explicit_fresh_reopen(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        editor.body_input.insertPlainText(" dirty")
        owner = self.widget._lab_owner
        old_root = owner.allocated_root
        with patch.object(owner.service, "invalidate", wraps=owner.service.invalidate) as invalidated, patch.object(
                editor, "_confirm_discard", return_value=True):
            self.assertIsNone(self.widget.close_synthetic_kb_lab())
            self.assertFalse(editor.body_input.isEnabled())
            self.assertEqual(editor.body_input.toPlainText(), "")
            self.assertFalse(editor.body_input.document().isUndoAvailable())
            self.assertIsNone(self.widget.close_synthetic_kb_lab())
            wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
            invalidated.assert_called_once()
        self.assertFalse(old_root.exists())
        self.assertTrue(owner.cleanup_complete)
        second = self.fixture.ready()
        self.assertIsNot(second, editor)
        self.assertNotEqual(self.widget._lab_owner.allocated_root, old_root)
        self.assertEqual(second.fixture_selector.currentIndex(), 0)

    def test_preparation_worker_reservation_repeated_activation_close_and_heartbeat(self):
        self.fixture.cleanup()
        gate = threading.Event()
        entered = threading.Event()
        gui_thread = threading.get_ident()
        class GatedSession(SyntheticLabSession):
            def prepare(owner):
                owner.worker_thread = threading.get_ident()
                entered.set()
                if not gate.wait(4):
                    raise AssertionError("Test setup gate timed out")
                return super().prepare()
        self.fixture = LabFixture(self.app, lambda: GatedSession(ROOT))
        self.fixture.gates.append(gate)
        self.widget = self.fixture.widget
        self.widget.open_synthetic_kb_lab()
        wait_for(self.app, entered.is_set)
        owner = self.widget._lab_owner
        for _ in range(4):
            self.widget.open_synthetic_kb_lab()
        ticks = []
        QTimer.singleShot(0, lambda: ticks.append(True))
        wait_for(self.app, lambda: bool(ticks))
        self.assertNotEqual(owner.worker_thread, gui_thread)
        self.assertEqual(len(self.fixture.owners), 1)
        self.assertIsNone(self.widget.close_synthetic_kb_lab())
        gate.set()
        wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
        self.assertIsNone(self.widget.lab_editor)
        self.assertTrue(owner.cleanup_complete)
        self.assertFalse(owner.allocated_root.exists())

    def test_stale_callbacks_cannot_attach_reopen_or_close_new_owner(self):
        self.fixture.ready()
        old_owner, old_generation = self.widget._lab_owner, self.widget._lab_generation
        self.widget.close_synthetic_kb_lab()
        wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
        editor = self.fixture.ready()
        current = self.widget._lab_owner
        self.widget._lab_prepared(old_owner, old_generation, old_owner)
        self.widget._lab_prepare_failed(old_owner, old_generation, RuntimeError("private"))
        self.widget._lab_cleanup_failed(old_owner, old_generation, RuntimeError("private"))
        self.widget._settle_lab(old_owner, old_generation)
        self.assertIs(self.widget.lab_editor, editor)
        self.assertIs(self.widget._lab_owner, current)
        self.assertEqual(self.widget._lab_state, "OPEN")

    def test_busy_false_completing_gap_defers_cleanup_submission(self):
        self.fixture.ready()
        runner = self.widget._lab_runner
        seen = []
        def during_gap(busy):
            if not busy and self.widget._lab_state == "OPEN":
                seen.append(runner.completing)
                self.widget.close_synthetic_kb_lab()
                self.assertFalse(runner.busy)
        runner.busy_changed.connect(during_gap)
        runner.submit(lambda: None, lambda _: None, lambda error: self.fail(str(type(error))))
        wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
        self.assertEqual(seen, [True])

    def test_submit_refusal_retains_owner_until_explicit_close(self):
        with patch.object(self.widget._lab_runner, "submit", return_value=False):
            self.widget.open_synthetic_kb_lab()
        owner = self.widget._lab_owner
        self.assertEqual(self.widget._lab_state, "FAILED")
        self.widget.open_synthetic_kb_lab()
        self.assertEqual(len(self.fixture.owners), 1)
        self.widget.close_synthetic_kb_lab()
        wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
        self.assertTrue(owner.cleanup_complete)

    def test_admission_failure_allocates_no_storage_and_can_close(self):
        with patch("f7hub.services.kb_lab_session.load_fixed_package", side_effect=ValueError("private")):
            self.widget.open_synthetic_kb_lab()
            wait_for(self.app, lambda: self.widget._lab_state == "FAILED")
        self.assertIsNone(self.widget._lab_owner.allocated_root)
        self.assertNotIn("private", self.widget._lab_feedback.text())
        self.widget.close_synthetic_kb_lab()
        wait_for(self.app, lambda: self.widget.lab_shutdown_ready)

    def test_setup_and_cleanup_double_failure_retains_exact_owner_no_retry_and_ack(self):
        with patch("f7hub.services.kb_lab_session.bootstrap_database", side_effect=OSError("private")), patch(
                "f7hub.services.kb_lab_session.shutil.rmtree", side_effect=PermissionError("private")) as cleanup:
            self.widget.open_synthetic_kb_lab()
            wait_for(self.app, lambda: self.widget._lab_state == "FAILED")
            self.fixture.idle()
            owner = self.widget._lab_owner
            self.assertTrue(owner.setup_failed and owner.cleanup_failed)
            self.assertTrue(owner.allocated_root.exists())
            self.widget.open_synthetic_kb_lab()
            self.assertFalse(self.widget.close_synthetic_kb_lab())
            self.assertFalse(self.widget.close_synthetic_kb_lab())
            self.assertEqual(cleanup.call_count, 1)
            self.assertEqual(len(self.fixture.owners), 1)
            self.assertNotIn("private", self.widget._lab_feedback.text())
            with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Cancel):
                self.assertFalse(self.widget.acknowledge_lab_residual())
            self.assertIs(self.widget._lab_owner, owner)
            with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Ok):
                self.assertTrue(self.widget.acknowledge_lab_residual())
            self.assertIn(owner, self.widget._lab_residual_owners)
            self.assertFalse(owner.cleanup_complete)
            self.assertTrue(owner.allocated_root.exists())
            self.assertIn("did not succeed", self.widget.feedback.text())

    def test_committed_discard_cleanup_failure_never_restores_draft_or_retries(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        editor.title_input.insert(" discarded")
        with patch.object(editor, "_confirm_discard", return_value=True), patch(
                "f7hub.services.kb_lab_session.shutil.rmtree", side_effect=PermissionError("private")) as cleanup:
            self.widget.close_synthetic_kb_lab()
            wait_for(self.app, lambda: self.widget._lab_state == "FAILED")
            self.fixture.idle()
            self.assertEqual(editor.title_input.text(), "")
            self.assertTrue(editor._closed)
            self.assertTrue(self.widget._lab_owner.terminal)
            self.assertFalse(self.widget.close_synthetic_kb_lab())
            self.assertEqual(cleanup.call_count, 1)

    def test_reentrant_close_cannot_bypass_cancel(self):
        editor = self.fixture.ready()
        def question():
            self.assertFalse(self.widget.close_synthetic_kb_lab())
            return False
        with patch.object(editor, "_confirm_discard", side_effect=question):
            self.assertFalse(self.widget.close_synthetic_kb_lab())
        self.assertFalse(editor._closed)
        self.assertFalse(self.widget._lab_owner.terminal)

    def test_cleanup_worker_heartbeat_and_placeholder_until_drained(self):
        self.fixture.ready()
        owner = self.widget._lab_owner
        gate, entered = threading.Event(), threading.Event()
        self.fixture.gates.append(gate)
        original = owner.close
        def cleanup():
            entered.set()
            if not gate.wait(4):
                raise AssertionError("Test cleanup gate timed out")
            original()
        with patch.object(owner, "close", side_effect=cleanup):
            self.widget.close_synthetic_kb_lab()
            wait_for(self.app, entered.is_set)
            self.assertEqual(self.widget.knowledge_tabs.count(), 2)
            self.widget.open_synthetic_kb_lab()
            self.assertEqual(len(self.fixture.owners), 1)
            ticks = []
            QTimer.singleShot(0, lambda: ticks.append(True))
            wait_for(self.app, lambda: bool(ticks))
            gate.set()
            wait_for(self.app, lambda: self.widget.lab_shutdown_ready)
        self.assertTrue(owner.cleanup_complete)

    def test_operational_controls_handlers_and_callbacks_are_isolated(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        calls = ["open_new_article", "open_edit_article", "publish_article", "archive_article",
                 "open_category", "open_tags", "open_version_history", "search_articles",
                 "clear_search", "refresh_filter_options", "refresh_list", "open_tag_filter"]
        before = editor.source_display.toPlainText()
        self.widget._update_actions(False)
        for button in (self.widget.new_button, self.widget.edit_button, self.widget.publish_button,
                       self.widget.archive_button, self.widget.search_button, self.widget.version_history_button):
            self.assertFalse(button.isEnabled())
        with patch.object(self.widget._runner, "submit", side_effect=AssertionError("Operational dispatch from Lab")):
            for name in calls:
                getattr(self.widget, name)()
            self.widget.open_article(777)
            self.widget._list_loaded(())
            self.widget._load_failed(RuntimeError("private"))
            self.widget._update_actions(False)
        self.assertIs(self.widget.knowledge_tabs.currentWidget(), self.widget._lab_tab)
        self.assertEqual(editor.source_display.toPlainText(), before)
        self.assertFalse(self.widget.new_button.isEnabled())

    def test_real_setup_only_exact_disposable_db_closed_connections_and_zero_preview_io(self):
        targets, handles = [], []
        original = sqlite3.connect
        def connect(database, *args, **kwargs):
            owner = self.widget._lab_owner
            self.assertEqual(Path(database).resolve(), owner.database_path)
            targets.append(Path(database))
            connection = original(database, *args, **kwargs)
            handles.append(connection)
            return connection
        with patch("sqlite3.connect", side_effect=connect), patch(
                "f7hub.infrastructure.database_paths.resolve_development_database_path",
                side_effect=AssertionError("No production path resolution")):
            editor = self.fixture.ready()
        self.assertTrue(targets)
        for handle in handles:
            with self.assertRaises(sqlite3.ProgrammingError):
                handle.execute("SELECT 1")
        owner = self.widget._lab_owner
        def dump():
            with closing(original(owner.database_path)) as connection:
                self.assertEqual(connection.execute("PRAGMA integrity_check").fetchall(), [("ok",)])
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM tickets WHERE status='NEW'").fetchone(), (6,))
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM knowledge_articles WHERE status='DRAFT'").fetchone(), (1,))
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM ticket_knowledge_articles").fetchone(), (0,))
                return tuple(connection.iterdump())
        before = dump()
        with patch("sqlite3.connect", side_effect=AssertionError("No preview SQL")), patch.object(
                Path, "read_bytes", side_effect=AssertionError("No preview source I/O")), patch(
                "socket.socket", side_effect=AssertionError("No preview network")):
            editor.fixture_selector.setCurrentIndex(1)
            editor.title_input.insert(" edit")
            editor.annotations_input.insertPlainText(" note")
            with patch.object(editor, "_confirm_discard", return_value=True):
                editor.fixture_selector.setCurrentIndex(2)
                self.assertTrue(editor.confirm_close())
        self.assertEqual(dump(), before)

    def test_queued_cursor_restore_respects_newer_deliberate_focus(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        editor.title_input.setFocus()
        editor.title_input.setSelection(1, 3)
        self.widget.knowledge_tabs.setCurrentWidget(self.widget.articles_tab)
        self.widget.knowledge_tabs.setCurrentWidget(self.widget._lab_tab)
        editor.summary_input.setFocus()
        self.app.processEvents()
        self.assertIs(self.widget.focusWidget(), editor.summary_input)
        self.assertEqual(self.widget._lab_state, "OPEN")

    def test_queued_cursor_restore_yields_to_new_keyboard_input(self):
        editor = self.fixture.ready()
        editor.fixture_selector.setCurrentIndex(1)
        editor.title_input.setFocus()
        editor.title_input.setSelection(1, 3)
        self.widget.knowledge_tabs.setCurrentWidget(self.widget.articles_tab)
        self.widget.knowledge_tabs.setCurrentWidget(self.widget._lab_tab)
        QTest.keyClick(editor.title_input, Qt.Key.Key_End)
        expected = editor.title_input.cursorPosition()
        self.app.processEvents()
        self.assertEqual(editor.title_input.cursorPosition(), expected)
        self.assertEqual(editor.title_input.selectedText(), "")
