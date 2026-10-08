"""Clipboard shell presentation and keyboard-only navigation."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from f7hub.gui.clipboard_workspace import ClipboardWorkspace


class ClipboardWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.workspace = ClipboardWorkspace()
        self.workspace.show()
        self.application.processEvents()

    def tearDown(self):
        self.workspace.close()
        self.workspace.deleteLater()
        self.application.processEvents()

    def test_unavailable_state_is_plain_truthful_and_has_only_navigation(self):
        self.assertEqual(self.workspace.heading.text(), "Clipboard Center")
        self.assertEqual(self.workspace.unavailable_message.text(),
                         "Clipboard history is not available yet.")
        self.assertEqual(self.workspace.heading.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(self.workspace.unavailable_message.textFormat(), Qt.TextFormat.PlainText)
        self.assertTrue(self.workspace.unavailable_message.wordWrap())
        self.assertEqual(self.workspace.findChildren(QAbstractItemView), [])
        self.assertEqual(self.workspace.findChildren(QPushButton), [self.workspace.back_button])
        self.assertEqual(self.workspace.property("moduleKey"), "clipboard")

    def test_return_button_is_named_focusable_and_emits_on_click(self):
        button = self.workspace.back_button
        self.assertEqual(button.text(), "Back to Tickets")
        self.assertEqual(button.accessibleName(), "Back to Tickets")
        self.assertEqual(self.workspace.accessibleName(), "Clipboard Center")
        self.assertEqual(self.workspace.unavailable_message.accessibleName(),
                         self.workspace.unavailable_message.text())
        self.assertNotEqual(button.focusPolicy(), Qt.FocusPolicy.NoFocus)
        requested = QSignalSpy(self.workspace.tickets_requested)
        button.click()
        self.assertEqual(requested.count(), 1)

    def test_space_on_focused_return_button_emits_one_navigation_request(self):
        button = self.workspace.back_button
        button.setFocus()
        self.application.processEvents()
        self.assertTrue(button.hasFocus())
        requested = QSignalSpy(self.workspace.tickets_requested)
        QTest.keyClick(button, Qt.Key.Key_Space)
        self.assertEqual(requested.count(), 1)


if __name__ == "__main__":
    unittest.main()
