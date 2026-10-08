"""Clipboard shell presentation and keyboard-only navigation."""

import os
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from f7hub.gui.clipboard_workspace import ClipboardWorkspace
from f7hub.domain.clipboard import ClipboardItemRef, ClipboardRecentItem, ClipboardRecentPage


def recent_page(*, rows=None, has_more=False):
    if rows is None:
        rows = (
            ClipboardRecentItem(ClipboardItemRef(1), 1, "<b>Résumé 😀 東京</b>", False,
                                "2026-10-08T10:00:00.000Z", "TEMPORARY", False,
                                "2026-10-09T10:00:00.000Z", "PERMITTED"),
            ClipboardRecentItem(ClipboardItemRef(2), 1, "Synthetic long preview", True,
                                "2026-10-08T09:00:00.000Z", "SAVED", True, None, "PERMITTED"),
        )
    return ClipboardRecentPage(rows, has_more, 50, "2026-10-08T12:00:00.000Z")


class RecordingClipboardService:
    def __init__(self, page=None):
        self.page = page if page is not None else recent_page()
        self.calls = []
        self.gate = None
        self.error = None
        self.thread_ids = []

    def get_recent(self, *, limit=50):
        self.calls.append(limit)
        self.thread_ids.append(threading.get_ident())
        if self.gate is not None and not self.gate.wait(5):
            raise RuntimeError("Synthetic read gate timed out")
        if self.error is not None:
            raise self.error
        return self.page


class ClipboardWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.workspace = ClipboardWorkspace()
        self.workspace.show()
        self.application.processEvents()

    def tearDown(self):
        if getattr(self, "service", None) is not None and self.service.gate is not None:
            self.service.gate.set()
        self.wait_idle()
        self.workspace.close()
        self.workspace.deleteLater()
        self.application.processEvents()

    def compose(self, page=None):
        self.workspace.close()
        self.workspace.deleteLater()
        self.service = RecordingClipboardService(page)
        self.workspace = ClipboardWorkspace(clipboard_service=self.service)
        self.workspace.show()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.workspace.loading and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.workspace.loading, "Clipboard read did not settle")

    def test_populated_page_displays_exact_safe_fields_and_unicode(self):
        self.compose()
        model_threads = []
        self.workspace.model.modelReset.connect(lambda: model_threads.append(threading.get_ident()))
        with patch.object(QApplication, "clipboard", side_effect=AssertionError("OS access forbidden")):
            self.assertTrue(self.workspace.activate())
            self.wait_idle()
        model = self.workspace.model
        self.assertEqual(model.HEADERS, ("Time", "Preview", "Retention", "Pinned"))
        self.assertEqual(model.columnCount(), 4)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual([model.data(model.index(0, c)) for c in range(4)],
                         ["2026-10-08 10:00:00.000 UTC", "<b>Résumé 😀 東京</b>", "Temporary", "No"])
        self.assertEqual([model.data(model.index(1, c)) for c in range(1, 4)],
                         ["Synthetic long preview … [truncated]", "Saved", "Yes"])
        self.assertEqual(model.data(model.index(0, 1), Qt.ItemDataRole.AccessibleTextRole),
                         "<b>Résumé 😀 東京</b>")
        self.assertFalse(hasattr(self.service.page.rows[0], "raw_text"))
        self.assertEqual(self.workspace.status_message.text(), "")
        self.assertEqual(self.workspace.page_message.text(), "Showing 2 recent items.")
        self.assertEqual(self.service.calls, [50])
        self.assertNotEqual(self.service.thread_ids[0], threading.get_ident())
        self.assertEqual(model_threads, [threading.get_ident(), threading.get_ident()])

    def test_model_is_read_only_with_no_persistent_selection_or_tooltips(self):
        self.compose()
        self.workspace.activate()
        self.wait_idle()
        model = self.workspace.model
        index = model.index(0, 1)
        self.assertFalse(model.flags(index) & Qt.ItemFlag.ItemIsEditable)
        self.assertFalse(model.setData(index, "overwrite"))
        self.assertIsNone(model.data(index, Qt.ItemDataRole.ToolTipRole))
        self.assertIsNone(model.data(QModelIndex()))
        self.assertEqual(model.rowCount(index), 0)
        self.assertEqual(model.columnCount(index), 0)
        self.assertEqual(self.workspace.table.selectionMode(), QAbstractItemView.SelectionMode.NoSelection)
        self.assertFalse(self.workspace.table.isSortingEnabled())
        self.assertEqual([b.text() for b in self.workspace.findChildren(QPushButton)],
                         ["Back to Tickets", "Refresh"])

    def test_loading_refuses_duplicates_and_keeps_back_available(self):
        self.compose()
        self.service.gate = threading.Event()
        self.assertTrue(self.workspace.activate())
        self.assertEqual(self.workspace.status_message.text(), "Loading Clipboard history…")
        self.assertFalse(self.workspace.refresh_button.isEnabled())
        self.assertTrue(self.workspace.back_button.isEnabled())
        self.assertFalse(self.workspace.activate())
        self.assertFalse(self.workspace.refresh())
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(self.service.calls, [50])
        self.assertFalse(self.workspace.activate())

    def test_empty_success_and_explicit_refresh(self):
        self.compose(recent_page(rows=()))
        self.workspace.activate()
        self.wait_idle()
        self.assertEqual(self.workspace.status_message.text(), "No recent Clipboard history is available.")
        self.assertEqual(self.workspace.page_message.text(), "Showing 0 recent items.")
        self.assertTrue(self.workspace.refresh_button.isEnabled())
        self.service.page = recent_page()
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.assertEqual(self.service.calls, [50, 50])

    def test_failed_refresh_clears_rows_and_safe_retry_recovers(self):
        self.compose()
        self.workspace.activate()
        self.wait_idle()
        self.service.error = RuntimeError("PRIVATE SQL database path raw body traceback")
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.status_message.text(), "Clipboard history could not be loaded.")
        self.assertEqual(self.workspace.status_message.accessibleName(), self.workspace.status_message.text())
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertEqual(self.workspace.page_message.text(), "")
        self.assertEqual(self.workspace.page_message.accessibleName(), "")
        self.assertEqual(self.workspace.refresh_button.text(), "Retry")
        self.assertEqual(self.workspace.refresh_button.accessibleName(), "Retry")
        self.assertFalse(self.workspace.activate())
        self.service.error = None
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.assertEqual(self.workspace.refresh_button.text(), "Refresh")
        self.assertEqual(self.service.calls, [50, 50, 50])

    def test_has_more_is_feedback_without_paging_actions(self):
        self.compose(recent_page(has_more=True))
        self.workspace.activate()
        self.wait_idle()
        self.assertEqual(self.workspace.page_message.text(), "Showing 2 recent items. More items are available.")

    def test_completion_gap_still_refuses_duplicate_read(self):
        self.compose()
        self.service.gate = threading.Event()
        observed = []
        self.workspace.runner.busy_changed.connect(
            lambda busy: observed.append((self.workspace.loading, self.workspace.refresh())) if not busy else None)
        self.workspace.activate()
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(observed, [(True, False)])

    def test_composed_back_to_tickets_signal_remains(self):
        self.compose()
        requested = QSignalSpy(self.workspace.tickets_requested)
        self.workspace.back_button.click()
        self.assertEqual(requested.count(), 1)

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
