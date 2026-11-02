"""Shared QWidget behavior; no storage, terminal owner or standalone size policy."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QWidget
from f7hub.gui.kb_preview_editor import KBPreviewEditor
from f7hub.services.kb_preview_service import NOTICE, PreviewUnavailableError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Unit"))
from test_kb_preview import bound_service


class KBPreviewEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service, self.snapshots = bound_service()
        self.host = QWidget()
        self.editor = KBPreviewEditor(self.service, self.snapshots, self.host)
        self.host.resize(800, 600)
        self.editor.resize(800, 600)
        self.host.show()
        self.app.processEvents()

    def tearDown(self):
        self.editor.commit_close()
        self.service.invalidate()
        self.host.hide()
        self.host.deleteLater()
        self.app.processEvents()

    def select(self, index=1):
        self.editor.fixture_selector.setCurrentIndex(index)
        self.app.processEvents()

    def test_reusable_widget_has_no_dialog_size_or_storage_capability(self):
        self.assertIsInstance(self.editor, QWidget)
        self.assertNotIsInstance(self.editor, QDialog)
        self.assertLess(self.editor.minimumWidth(), 860)
        self.assertFalse(hasattr(self.editor, "database_path"))
        self.assertFalse(hasattr(self.editor, "_session"))
        self.assertEqual([b.text() for b in self.editor.findChildren(QPushButton)], ["Close"])
        self.assertEqual(self.editor.notice.text(), NOTICE)
        self.assertFalse(self.editor.body_input.isEnabled())

    def test_all_six_fixture_identities_and_source_provenance(self):
        self.assertEqual(self.editor.fixture_selector.count(), 7)
        for index, snapshot in enumerate(self.snapshots, 1):
            self.select(index)
            self.assertIs(self.editor._preview.source, snapshot)
            self.assertIn(snapshot.fixture.fixture_id, self.editor.source_display.toPlainText())
            self.assertIn(snapshot.package_digest, self.editor.source_display.toPlainText())
        self.select(2)
        self.assertIn("deuxième", self.editor.source_display.toPlainText())
        self.select(3)
        self.assertIn("canonical target: UNRESOLVED", self.editor.source_display.toPlainText())

    def test_plain_text_and_annotations_do_not_mutate_source(self):
        self.select()
        before = self.editor.source_display.toPlainText()
        self.editor.body_input.setPlainText('<img src="https://example.invalid/">')
        self.editor.annotations_input.setPlainText("Not causal acceptance")
        self.assertIn("<img", self.editor.body_input.toPlainText())
        self.assertEqual(self.editor.source_display.toPlainText(), before)
        self.assertTrue(self.editor.dirty)

    def test_unicode_scalar_and_utf8_boundaries(self):
        self.select()
        for name, valid, invalid in (
            ("title", "🔧" * 200, "🔧" * 201),
            ("summary", "é" * 1000, "é" * 1001),
            ("body", "🔧" * 16384, "🔧" * 16385),
            ("annotations", "é" * 8192, "é" * 8193),
        ):
            field = self.editor._editors[name]
            self.editor._set_value(field, valid)
            self.editor._edited(name)
            self.assertEqual(self.editor._accepted[name], valid)
            self.editor._set_value(field, invalid)
            self.editor._edited(name)
            self.assertEqual(self.editor._value(field), valid)
            self.assertIn("rejected", self.editor.feedback.text())

    def test_cancel_preserves_full_draft_selection_undo_and_identity(self):
        self.select()
        self.editor.title_input.setText("new title")
        self.editor.summary_input.setText("new summary")
        self.editor.annotations_input.setPlainText("annotation")
        body = self.editor.body_input
        body.setFocus()
        QTest.keyClicks(body, " synthetic edit")
        cursor = body.textCursor()
        cursor.setPosition(1)
        cursor.setPosition(4, cursor.MoveMode.KeepAnchor)
        body.setTextCursor(cursor)
        before = (tuple(self.editor._value(e) for e in self.editor._editors.values()),
                  self.editor.source_display.toPlainText(), self.editor._preview,
                  cursor.position(), cursor.anchor(), body.document().isUndoAvailable())
        with patch.object(self.editor, "_confirm_discard", return_value=False):
            self.select(2)
            self.assertFalse(self.editor.confirm_close())
        after_cursor = body.textCursor()
        after = (tuple(self.editor._value(e) for e in self.editor._editors.values()),
                 self.editor.source_display.toPlainText(), self.editor._preview,
                 after_cursor.position(), after_cursor.anchor(), body.document().isUndoAvailable())
        self.assertEqual(before, after)
        self.assertIs(self.editor._preview.source, self.snapshots[0])
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)
        body.undo()
        self.assertNotEqual(self.editor._value(body), before[0][2])

    def test_replacement_failure_never_asks_discard_or_loses_undo(self):
        self.select()
        QTest.keyClicks(self.editor.body_input, " edited")
        before = self.editor.body_input.toPlainText()
        with patch.object(self.service, "build_preview", side_effect=PreviewUnavailableError("Unavailable")),                 patch.object(self.editor, "_confirm_discard") as question:
            self.select(2)
        question.assert_not_called()
        self.assertEqual(self.editor.body_input.toPlainText(), before)
        self.assertTrue(self.editor.body_input.document().isUndoAvailable())
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)

    def test_prepare_precedes_discard_and_discard_resets_annotations_and_undo(self):
        self.select()
        QTest.keyClicks(self.editor.body_input, " dirty")
        self.editor.annotations_input.setPlainText("annotation")
        events = []
        build = self.service.build_preview
        def prepare(snapshot):
            events.append("prepare")
            return build(snapshot)
        def discard():
            events.append("discard")
            return True
        with patch.object(self.service, "build_preview", side_effect=prepare),                 patch.object(self.editor, "_confirm_discard", side_effect=discard):
            self.select(2)
        self.assertEqual(events, ["prepare", "discard"])
        self.assertEqual(self.editor.annotations_input.toPlainText(), "")
        self.assertFalse(self.editor.body_input.document().isUndoAvailable())
        self.assertFalse(self.editor.dirty)

    def test_terminal_commit_clears_once_without_invalidating_service(self):
        self.select()
        QTest.keyClicks(self.editor.body_input, " dirty")
        with patch.object(self.service, "invalidate") as invalidate:
            self.assertTrue(self.editor.commit_close())
            self.assertFalse(self.editor.commit_close())
        invalidate.assert_not_called()
        self.assertEqual(self.editor.body_input.toPlainText(), "")
        self.assertFalse(self.editor.body_input.document().isUndoAvailable())
        self.assertFalse(self.editor.title_input.isUndoAvailable())
        self.assertEqual(self.editor.source_display.toPlainText(), "")
        self.assertFalse(self.editor.body_input.isEnabled())
        self.assertFalse(self.editor.fixture_selector.isEnabled())
        self.assertIsNone(self.editor._preview)
        self.service.build_preview(self.snapshots[0])

    def test_close_intent_does_not_commit_and_reentry_cannot_override_cancel(self):
        self.select()
        self.editor.body_input.setPlainText("keep")
        intents = []
        self.editor.close_requested.connect(lambda: intents.append(True))
        self.editor.close_button.click()
        self.assertEqual(intents, [True])
        self.assertFalse(self.editor._closed)
        def cancel():
            self.assertFalse(self.editor.confirm_close())
            self.assertFalse(self.editor.commit_close())
            self.select(3)
            return False
        with patch.object(self.editor, "_confirm_discard", side_effect=cancel):
            self.assertFalse(self.editor.confirm_close())
        self.assertEqual(self.editor.body_input.toPlainText(), "keep")
        self.assertEqual(self.editor.fixture_selector.currentIndex(), 1)


if __name__ == "__main__":
    unittest.main()
