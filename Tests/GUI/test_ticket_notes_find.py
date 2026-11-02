"""Focused presentation checks for finding within the loaded ticket's notes."""

import os
import time
import unittest
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.gui.main_window import MainWindow
from Tests.GUI.test_main_window import RecordingTicketService


def note(text, *, author="Technician"):
    return SimpleNamespace(created_at="2026-11-02T12:00:00Z", note_type="INTERNAL",
                           author_label=author, is_ai_generated=False, note_text=text)


class TicketNotesFindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingTicketService()
        self.window = MainWindow(self.service)
        self.window.resize(1000, 700)
        self.window.show()
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy)
        self.workspace = self.window.workspace
        self.show_notes((note("Alpha Écran 😀 %_.* alpha"), note("Last alpha")))

    def tearDown(self):
        self.workspace._clear_drafts()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def show_notes(self, notes, *, ticket=None):
        details = SimpleNamespace(ticket=ticket or self.service.ticket, notes=notes,
                                  status_history=(), timeline_events=(), company_name=None,
                                  contact_name=None, category_name=None)
        self.workspace._display_details(details)
        self.workspace.detail_tabs.setCurrentWidget(self.workspace.notes_tab)
        self.application.processEvents()
        return details

    def test_literal_unicode_metadata_and_directional_wrap_preserve_history(self):
        workspace = self.workspace
        before = workspace.notes_history.toPlainText()
        self.assertEqual(workspace.detail_tabs.count(), 5)
        self.assertTrue(workspace.notes_history.isReadOnly())
        workspace.notes_find_input.setText("ALPHA")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_history.textCursor().selectedText(), "Alpha")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_history.textCursor().selectedText(), "alpha")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_history.textCursor().selectedText(), "alpha")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_find_feedback.text(), "Wrapped to start.")
        workspace.notes_find_previous_button.click()
        self.assertEqual(workspace.notes_find_feedback.text(), "Wrapped to end.")
        for query, expected in (("écran", "Écran"), ("😀", "😀"),
                                ("%_.*", "%_.*"), ("technician", "Technician")):
            workspace.notes_find_input.setText(query)
            workspace.notes_find_next_button.click()
            self.assertEqual(workspace.notes_history.textCursor().selectedText(), expected)
        workspace.notes_find_input.setText("not present")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_find_feedback.text(), "No matches.")
        self.assertNotIn("not present", workspace.notes_find_feedback.text())
        workspace.notes_find_input.setText("   ")
        self.assertEqual(workspace.notes_find_feedback.text(), "")
        self.assertFalse(workspace.notes_history.textCursor().hasSelection())
        self.assertEqual(workspace.notes_history.toPlainText(), before)

    def test_field_keyboard_scope_and_draft_preservation(self):
        workspace = self.workspace
        workspace.note_input.setPlainText("Keep this draft")
        workspace.notes_find_input.setText("alpha")
        workspace.notes_find_input.setFocus()
        QTest.keyClick(workspace.notes_find_input, Qt.Key.Key_Return)
        self.assertEqual(workspace.notes_history.textCursor().selectedText(), "Alpha")
        QTest.keyClick(workspace.notes_find_input, Qt.Key.Key_Return,
                       Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(workspace.notes_find_feedback.text(), "Wrapped to end.")
        QTest.keyClick(workspace.notes_find_input, Qt.Key.Key_Return,
                       Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(workspace.note_input.toPlainText(), "Keep this draft")
        workspace.notes_history.setFocus()
        QTest.keyClick(workspace.notes_history, Qt.Key.Key_F,
                       Qt.KeyboardModifier.ControlModifier)
        self.assertTrue(workspace.notes_find_input.hasFocus())
        self.assertEqual(workspace.notes_find_input.selectedText(), "alpha")
        QTest.keyClick(workspace.notes_find_input, Qt.Key.Key_Escape)
        self.assertEqual(workspace.notes_find_input.text(), "")
        self.assertTrue(workspace.notes_history.hasFocus())
        self.assertEqual(workspace.note_input.toPlainText(), "Keep this draft")
        self.assertTrue(workspace.has_draft())
        workspace.note_input.clear()
        workspace.notes_find_input.setText("alpha")
        self.assertFalse(workspace.has_draft())

    def test_reload_replacement_and_empty_history(self):
        workspace = self.workspace
        workspace.notes_find_input.setText("alpha")
        workspace.notes_find_next_button.click()
        details = self.show_notes((note("New alpha"),))
        self.assertEqual(workspace.notes_find_input.text(), "alpha")
        self.assertFalse(workspace.notes_history.textCursor().hasSelection())
        self.assertEqual(workspace.notes_find_feedback.text(), "")
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_history.textCursor().selectedText(), "alpha")
        other = SimpleNamespace(**vars(self.service.ticket))
        other.ticket_id = 2
        other.ticket_number = "TKT-1002"
        self.show_notes((note("Other alpha"),), ticket=other)
        self.assertEqual(workspace.notes_find_input.text(), "")
        self.show_notes((), ticket=other)
        workspace.notes_find_input.setText("No notes yet.")
        self.assertFalse(workspace.notes_find_next_button.isEnabled())
        workspace._find_in_notes()
        self.assertEqual(workspace.notes_find_feedback.text(), "No notes to search.")
        self.assertEqual(workspace.notes_history.toPlainText(), "No notes yet.")

    def test_hidden_pending_and_completing_guards(self):
        workspace = self.workspace
        workspace.notes_find_input.setText("alpha")
        workspace.detail_tabs.setCurrentWidget(workspace.summary)
        workspace._find_in_notes()
        self.assertFalse(workspace.notes_history.textCursor().hasSelection())
        workspace.detail_tabs.setCurrentWidget(workspace.notes_tab)
        for field in ("_note_pending", "status_pending", "classification_pending",
                      "_creation_pending"):
            setattr(workspace, field, True)
            workspace._update_notes_find_controls()
            self.assertFalse(workspace.notes_find_next_button.isEnabled(), field)
            workspace._find_in_notes()
            self.assertFalse(workspace.notes_history.textCursor().hasSelection(), field)
            setattr(workspace, field, False)
        workspace._runner._completion_depth += 1
        try:
            workspace._update_notes_find_controls()
            self.assertFalse(workspace.notes_find_next_button.isEnabled())
            workspace._find_in_notes()
            self.assertFalse(workspace.notes_history.textCursor().hasSelection())
        finally:
            workspace._runner._completion_depth -= 1
            workspace._update_notes_find_controls()
        self.assertTrue(workspace.notes_find_next_button.isEnabled())

    def test_manual_cursor_tab_traversal_and_accepted_creation(self):
        workspace = self.workspace
        workspace.notes_find_input.setText("alpha")
        workspace.notes_find_next_button.click()
        cursor = workspace.notes_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        workspace.notes_history.setTextCursor(cursor)
        workspace.notes_find_next_button.click()
        self.assertEqual(workspace.notes_find_feedback.text(), "Wrapped to start.")
        workspace.notes_find_input.setFocus()
        QTest.keyClick(workspace.notes_find_input, Qt.Key.Key_Tab)
        self.assertTrue(workspace.notes_find_previous_button.hasFocus())
        QTest.keyClick(workspace.notes_find_previous_button, Qt.Key.Key_Tab,
                       Qt.KeyboardModifier.ShiftModifier)
        self.assertTrue(workspace.notes_find_input.hasFocus())
        self.assertTrue(workspace.begin_creation())
        self.assertEqual(workspace.notes_find_input.text(), "")
        self.assertFalse(workspace.notes_find_next_button.isEnabled())
        self.assertTrue(workspace.cancel_creation())
        self.assertEqual(workspace.notes_find_input.text(), "")

    def test_module_hide_show_retains_query_and_reconciles_controls(self):
        workspace = self.workspace
        workspace.notes_find_input.setText("alpha")
        self.assertTrue(workspace.notes_find_next_button.isEnabled())
        workspace.hide()
        self.application.processEvents()
        self.assertEqual(workspace.notes_find_input.text(), "alpha")
        self.assertFalse(workspace.notes_find_next_button.isEnabled())
        workspace._find_in_notes()
        self.assertFalse(workspace.notes_history.textCursor().hasSelection())
        workspace.show()
        self.application.processEvents()
        self.assertEqual(workspace.notes_find_input.text(), "alpha")
        self.assertTrue(workspace.notes_find_next_button.isEnabled())

    def test_constrained_notes_page_keeps_controls_and_history_visible(self):
        workspace = self.workspace
        self.assertEqual(self.window.size().width(), 1000)
        self.assertEqual(self.window.size().height(), 700)
        for control in (workspace.notes_find_input, workspace.notes_find_previous_button,
                        workspace.notes_find_next_button, workspace.notes_find_clear_button,
                        workspace.notes_history):
            self.assertTrue(control.isVisible(), control.objectName())
            self.assertGreater(control.height(), 0)


if __name__ == "__main__":
    unittest.main()
