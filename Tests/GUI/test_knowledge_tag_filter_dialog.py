"""Keyboard and cancellation behavior of cached Knowledge tag choices."""

import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog

from f7hub.gui.knowledge_tag_filter_dialog import KnowledgeTagFilterDialog


class KnowledgeTagFilterDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_selected_ids_are_stable_and_keyboard_checkable(self):
        literal = "<b>Literal</b> " + "long name " * 30
        dialog = KnowledgeTagFilterDialog((
            SimpleNamespace(tag_id=22, name=literal),
            SimpleNamespace(tag_id=11, name="VPN"),
        ), (11,))
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        self.app.processEvents()
        self.assertEqual(dialog.tag_list.item(0).text(), literal)
        self.assertEqual(dialog.selected_ids(), (11,))
        dialog.tag_list.setCurrentRow(0)
        dialog.tag_list.setFocus()
        QTest.keyClick(dialog.tag_list, Qt.Key.Key_Space)
        self.assertEqual(dialog.selected_ids(), (11, 22))
        for button in (dialog.cancel_button, dialog.apply_button):
            self.assertTrue(button.isVisible())
            self.assertTrue(dialog.rect().contains(
                button.mapTo(dialog, button.rect().bottomRight())
            ))
        QTest.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)

    def test_empty_choices_and_escape(self):
        dialog = KnowledgeTagFilterDialog(())
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        self.app.processEvents()
        self.assertEqual(dialog.selected_ids(), ())
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)
