"""Headless Qt evidence only; separate Windows-native smoke is required."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton
from f7hub.gui.kb_preview_dialog import KBPreviewDialog
from f7hub.services.kb_preview_service import NOTICE, PreviewUnavailableError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Unit"))
from test_kb_preview import bound_service


class KBPreviewDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service, self.snapshots = bound_service()
        self.dialog = KBPreviewDialog(self.service, self.snapshots)
        self.dialog.show()
        self.app.processEvents()

    def tearDown(self):
        with patch.object(self.dialog, "_confirm_discard", return_value=True):
            self.dialog.reject()
        self.dialog.deleteLater()
        self.app.processEvents()

    def select(self, index=1):
        self.dialog.fixture_selector.setCurrentIndex(index)
        self.app.processEvents()

    def test_requires_explicit_selection_and_has_no_write_action(self):
        self.assertFalse(self.dialog.title_input.isEnabled())
        self.assertEqual(self.dialog.notice.text(), NOTICE)
        self.assertEqual([b.text() for b in self.dialog.findChildren(QPushButton)], ["Close"])
        self.select()
        self.assertTrue(self.dialog.body_input.isEnabled())
        self.assertFalse(self.dialog.dirty)

    def test_plain_text_source_provenance_and_edit_remain_separate(self):
        self.select(2)
        provenance = self.dialog.source_display.toPlainText()
        self.assertIn("deuxième", provenance)
        self.assertIn("canonical target: UNRESOLVED", provenance)
        self.dialog.body_input.setPlainText('<img src="https://example.invalid/"> edited')
        self.dialog.annotations_input.setPlainText("Needs technical review")
        self.assertTrue(self.dialog.dirty)
        self.assertEqual(self.dialog.source_display.toPlainText(), provenance)
        self.assertEqual(self.dialog.notice.text(), NOTICE)
        self.assertTrue(self.dialog.source_display.isReadOnly())

    def test_oversize_edits_are_rejected_and_prior_text_preserved(self):
        self.select()
        for editor, value in ((self.dialog.title_input, "🔧" * 201),
                              (self.dialog.summary_input, "x" * 1001),
                              (self.dialog.body_input, "é" * 32769),
                              (self.dialog.annotations_input, "x" * 16385)):
            old = self.dialog._value(editor)
            if hasattr(editor, "setPlainText"):
                editor.setPlainText(value)
            else:
                editor.setText(value)
            self.assertEqual(self.dialog._value(editor), old)
            self.assertIn("rejected", self.dialog.feedback.text())

    def test_cancel_switch_and_close_preserve_edits(self):
        self.select()
        self.dialog.body_input.setPlainText("Retain my draft")
        with patch.object(self.dialog, "_confirm_discard", return_value=False):
            self.select(2)
            self.dialog.reject()
        self.assertEqual(self.dialog.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.dialog.body_input.toPlainText(), "Retain my draft")
        self.assertTrue(self.dialog.isVisible())

    def test_discard_switch_then_close_erases_all_draft_state(self):
        self.select()
        self.dialog.annotations_input.setPlainText("Discard this annotation")
        with patch.object(self.dialog, "_confirm_discard", return_value=True):
            self.select(2)
            self.assertEqual(self.dialog.annotations_input.toPlainText(), "")
            self.dialog.reject()
        self.assertEqual(self.dialog.body_input.toPlainText(), "")
        self.assertEqual(self.dialog.source_display.toPlainText(), "")
        self.assertIsNone(self.dialog._preview)
        with self.assertRaises(PreviewUnavailableError):
            self.service.build_preview(self.snapshots[0])

    def test_replacement_failure_preserves_edits_without_discard_question(self):
        self.select()
        self.dialog.body_input.setPlainText("Retain despite unavailable source")
        self.service.invalidate()
        with patch.object(self.dialog, "_confirm_discard") as question:
            self.select(2)
            question.assert_not_called()
        self.assertEqual(self.dialog.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.dialog.body_input.toPlainText(), "Retain despite unavailable source")
        self.assertIn("unavailable", self.dialog.feedback.text())

    def test_real_discard_cancel_dialog_defaults_to_cancel(self):
        self.select()
        self.dialog.title_input.setText("Edited title")
        def cancel():
            box = QApplication.activeModalWidget()
            self.assertIsInstance(box, QMessageBox)
            self.assertEqual(box.defaultButton(), box.button(QMessageBox.StandardButton.Cancel))
            box.button(QMessageBox.StandardButton.Cancel).click()
        QTimer.singleShot(0, cancel)
        self.dialog.reject()
        self.assertEqual(self.dialog.title_input.text(), "Edited title")
        QTimer.singleShot(0, lambda: QApplication.activeModalWidget().button(QMessageBox.StandardButton.Discard).click())
        self.dialog.reject()
        self.assertFalse(self.dialog.isVisible())

    def test_keyboard_edit_focus_and_escape_dirty_guard(self):
        self.select()
        self.dialog.title_input.setFocus()
        QTest.keyClicks(self.dialog.title_input, " edited")
        self.assertIn("edited", self.dialog.title_input.text())
        QTest.keyClick(self.dialog.title_input, Qt.Key.Key_Tab)
        self.assertTrue(self.dialog.summary_input.hasFocus())
        with patch.object(self.dialog, "_confirm_discard", return_value=False):
            QTest.keyClick(self.dialog, Qt.Key.Key_Escape)
        self.assertTrue(self.dialog.isVisible())

    def test_reentrant_close_cannot_bypass_discard_cancel(self):
        self.select()
        self.dialog.body_input.setPlainText("Dirty")
        def cancel_with_reentry():
            self.dialog.reject()
            self.dialog.fixture_selector.setCurrentIndex(3)
            return False
        with patch.object(self.dialog, "_confirm_discard", side_effect=cancel_with_reentry):
            self.dialog.reject()
        self.assertTrue(self.dialog.isVisible())
        self.assertEqual(self.dialog.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.dialog.body_input.toPlainText(), "Dirty")


if __name__ == "__main__":
    unittest.main()
