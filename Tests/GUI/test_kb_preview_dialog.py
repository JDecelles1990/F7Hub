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
from f7hub.services.kb_lab_session import SyntheticLabSession
from f7hub.services.kb_preview_service import NOTICE, PreviewUnavailableError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Unit"))
from test_kb_preview import bound_service


class KBPreviewDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service, self.snapshots = bound_service()
        self.owner = SyntheticLabSession(Path(__file__).resolve().parents[2])
        self.owner._service, self.owner._snapshots = self.service, self.snapshots
        self.dialog = KBPreviewDialog(self.owner)
        self.editor = self.dialog.editor
        self.dialog.show()
        self.app.processEvents()

    def tearDown(self):
        with patch.object(self.editor, "_confirm_discard", return_value=True):
            self.dialog.reject()
        self.dialog.deleteLater()
        self.app.processEvents()

    def select(self, index=1):
        self.editor.fixture_selector.setCurrentIndex(index)
        self.app.processEvents()

    def test_requires_explicit_selection_and_has_no_write_action(self):
        self.assertFalse(self.editor.title_input.isEnabled())
        self.assertEqual(self.editor.notice.text(), NOTICE)
        self.assertEqual([b.text() for b in self.dialog.findChildren(QPushButton)], ["Close"])
        self.select()
        self.assertTrue(self.editor.body_input.isEnabled())
        self.assertFalse(self.editor.dirty)

    def test_plain_text_source_provenance_and_edit_remain_separate(self):
        self.select(2)
        provenance = self.editor.source_display.toPlainText()
        self.assertIn("deuxième", provenance)
        self.assertIn("canonical target: UNRESOLVED", provenance)
        self.editor.body_input.setPlainText('<img src="https://example.invalid/"> edited')
        self.editor.annotations_input.setPlainText("Needs technical review")
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.editor.source_display.toPlainText(), provenance)
        self.assertEqual(self.editor.notice.text(), NOTICE)
        self.assertTrue(self.editor.source_display.isReadOnly())

    def test_oversize_edits_are_rejected_and_prior_text_preserved(self):
        self.select()
        for editor, value in ((self.editor.title_input, "🔧" * 201),
                              (self.editor.summary_input, "x" * 1001),
                              (self.editor.body_input, "é" * 32769),
                              (self.editor.annotations_input, "x" * 16385)):
            old = self.editor._value(editor)
            if hasattr(editor, "setPlainText"):
                editor.setPlainText(value)
            else:
                editor.setText(value)
            self.assertEqual(self.editor._value(editor), old)
            self.assertIn("rejected", self.editor.feedback.text())

    def test_cancel_switch_and_close_preserve_edits(self):
        self.select()
        self.editor.body_input.setPlainText("Retain my draft")
        with patch.object(self.editor, "_confirm_discard", return_value=False):
            self.select(2)
            self.dialog.reject()
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.editor.body_input.toPlainText(), "Retain my draft")
        self.assertTrue(self.dialog.isVisible())

    def test_discard_switch_then_close_erases_all_draft_state(self):
        self.select()
        self.editor.annotations_input.setPlainText("Discard this annotation")
        with patch.object(self.editor, "_confirm_discard", return_value=True):
            self.select(2)
            self.assertEqual(self.editor.annotations_input.toPlainText(), "")
            self.dialog.reject()
        self.assertEqual(self.editor.body_input.toPlainText(), "")
        self.assertEqual(self.editor.source_display.toPlainText(), "")
        self.assertIsNone(self.editor._preview)
        with self.assertRaises(PreviewUnavailableError):
            self.service.build_preview(self.snapshots[0])

    def test_replacement_failure_preserves_edits_without_discard_question(self):
        self.select()
        self.editor.body_input.setPlainText("Retain despite unavailable source")
        self.service.invalidate()
        with patch.object(self.editor, "_confirm_discard") as question:
            self.select(2)
            question.assert_not_called()
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.editor.body_input.toPlainText(), "Retain despite unavailable source")
        self.assertIn("unavailable", self.editor.feedback.text())

    def test_real_discard_cancel_dialog_defaults_to_cancel(self):
        self.select()
        self.editor.title_input.setText("Edited title")
        def cancel():
            box = QApplication.activeModalWidget()
            self.assertIsInstance(box, QMessageBox)
            self.assertEqual(box.defaultButton(), box.button(QMessageBox.StandardButton.Cancel))
            box.button(QMessageBox.StandardButton.Cancel).click()
        QTimer.singleShot(0, cancel)
        self.dialog.reject()
        self.assertEqual(self.editor.title_input.text(), "Edited title")
        QTimer.singleShot(0, lambda: QApplication.activeModalWidget().button(QMessageBox.StandardButton.Discard).click())
        self.dialog.reject()
        self.assertFalse(self.dialog.isVisible())

    def test_keyboard_edit_focus_and_escape_dirty_guard(self):
        self.select()
        self.editor.title_input.setFocus()
        QTest.keyClicks(self.editor.title_input, " edited")
        self.assertIn("edited", self.editor.title_input.text())
        QTest.keyClick(self.editor.title_input, Qt.Key.Key_Tab)
        self.assertTrue(self.editor.summary_input.hasFocus())
        with patch.object(self.editor, "_confirm_discard", return_value=False):
            QTest.keyClick(self.dialog, Qt.Key.Key_Escape)
        self.assertTrue(self.dialog.isVisible())

    def test_reentrant_close_cannot_bypass_discard_cancel(self):
        self.select()
        self.editor.body_input.setPlainText("Dirty")
        def cancel_with_reentry():
            self.dialog.reject()
            self.editor.fixture_selector.setCurrentIndex(3)
            return False
        with patch.object(self.editor, "_confirm_discard", side_effect=cancel_with_reentry):
            self.dialog.reject()
        self.assertTrue(self.dialog.isVisible())
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)
        self.assertEqual(self.editor.body_input.toPlainText(), "Dirty")


    def test_all_terminal_routes_invalidate_owner_once_and_never_accept(self):
        from PySide6.QtWidgets import QDialog
        self.select()
        with patch.object(self.service, "invalidate", wraps=self.service.invalidate) as invalidate:
            self.dialog.accept()
            self.dialog.reject()
            self.dialog.done(QDialog.DialogCode.Accepted)
            self.owner.close()
            self.owner.close()
        self.assertEqual(invalidate.call_count, 1)
        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Rejected)
        self.assertTrue(self.owner.cleanup_complete)

    def test_x_and_close_button_share_cancel_guard(self):
        self.select()
        self.editor.body_input.setPlainText("keep")
        with patch.object(self.editor, "_confirm_discard", return_value=False):
            self.assertFalse(self.dialog.close())
            self.editor.close_button.click()
        self.assertTrue(self.dialog.isVisible())
        self.assertFalse(self.owner.terminal)
        self.assertEqual(self.editor.body_input.toPlainText(), "keep")


    def test_return_in_clean_and_dirty_single_line_fields_never_requests_close(self):
        self.select()
        self.assertFalse(self.editor.close_button.autoDefault())
        self.assertFalse(self.editor.close_button.isDefault())
        with patch.object(self.editor, "_confirm_discard", return_value=False) as question,                 patch.object(self.service, "invalidate", wraps=self.service.invalidate) as invalidate:
            for field in (self.editor.title_input, self.editor.summary_input):
                baseline = field.text()
                field.setFocus()
                QTest.keyClick(field, Qt.Key.Key_Return)
                self.assertTrue(self.dialog.isVisible())
                self.assertFalse(self.owner.terminal)
                self.assertEqual(field.text(), baseline)
                field.setText(baseline + " edited")
                QTest.keyClick(field, Qt.Key.Key_Return)
                self.assertTrue(self.dialog.isVisible())
                self.assertFalse(self.owner.terminal)
                self.assertEqual(field.text(), baseline + " edited")
                field.setText(baseline)
            question.assert_not_called()
            invalidate.assert_not_called()
        self.editor.close_button.setFocus()
        QTest.keyClick(self.editor.close_button, Qt.Key.Key_Space)
        self.assertFalse(self.dialog.isVisible())
        self.assertTrue(self.owner.terminal)


if __name__ == "__main__":
    unittest.main()
