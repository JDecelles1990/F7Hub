"""Clipboard shell presentation and keyboard-only navigation."""

import os
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from f7hub.gui.clipboard_workspace import ClipboardWorkspace
from f7hub.domain.clipboard import ClipboardItemRef, ClipboardRecentItem, ClipboardRecentPage
from f7hub.gui.service_task_runner import ServiceTaskRunner


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

    def test_source_app_plain_accessible_bounded_display_and_refresh(self):
        from dataclasses import replace
        self.compose()
        rows = self.service.page.rows
        for name in ("notepad.exe", "msedge.exe", "é" * 251 + ".exe", None):
            self.service.page = replace(self.service.page, rows=(replace(rows[0], source_process_basename=name),))
            self.workspace.activate()
            self.wait_idle()
            self.workspace.refresh_button.click()
            self.wait_idle()
            index = self.workspace.model.index(0, 2)
            expected = name or "Not recorded"
            self.assertEqual(self.workspace.model.data(index), expected)
            self.assertEqual(self.workspace.model.data(index, Qt.ItemDataRole.AccessibleTextRole), expected)
            self.assertFalse(self.workspace.model.flags(index) & Qt.ItemFlag.ItemIsEditable)
            self.assertEqual(self.workspace.table.selectionMode(), QAbstractItemView.SelectionMode.NoSelection)
            self.assertFalse(self.workspace.table.isSortingEnabled())

    def test_populated_page_displays_exact_safe_fields_and_unicode(self):
        self.compose()
        model_threads = []
        self.workspace.model.modelReset.connect(lambda: model_threads.append(threading.get_ident()))
        with patch.object(QApplication, "clipboard", side_effect=AssertionError("OS access forbidden")):
            self.assertTrue(self.workspace.activate())
            self.wait_idle()
        model = self.workspace.model
        self.assertEqual(model.HEADERS, ("Time", "Preview", "Source App", "Retention", "Pinned", "Select"))
        self.assertEqual(model.columnCount(), 6)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual([model.data(model.index(0, c)) for c in range(5)],
                         ["2026-10-08 10:00:00.000 UTC", "<b>Résumé 😀 東京</b>", "Not recorded", "Temporary", "No"])
        self.assertEqual([model.data(model.index(1, c)) for c in range(1, 5)],
                         ["Synthetic long preview … [truncated]", "Not recorded", "Saved", "Yes"])
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
                         ["Refresh", "Refresh", "Select All Visible", "Clear Selection", "Copy Selected (0)"])

    def test_loading_refuses_duplicates_and_has_no_enabled_recent_control(self):
        self.compose()
        self.service.gate = threading.Event()
        self.assertTrue(self.workspace.activate())
        self.assertEqual(self.workspace.status_message.text(), "Loading Clipboard history…")
        self.assertFalse(self.workspace.refresh_button.isEnabled())
        self.assertIs(self.workspace.activation_focus_target(), self.workspace.source_selector)
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

    def test_obsolete_return_control_and_signal_are_absent(self):
        self.compose()
        self.assertFalse(hasattr(self.workspace, "back_button"))
        self.assertFalse(hasattr(self.workspace, "tickets_requested"))
        self.assertIsNone(self.workspace.findChild(QPushButton, "clipboardBackToTicketsButton"))
        self.assertIs(self.workspace.activation_focus_target(), self.workspace.refresh_button)

    def test_unavailable_state_is_plain_truthful_without_workspace_control(self):
        self.assertEqual(self.workspace.heading.text(), "Clipboard Center")
        self.assertEqual(self.workspace.unavailable_message.text(),
                         "Clipboard history is not available yet.")
        self.assertEqual(self.workspace.heading.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(self.workspace.unavailable_message.textFormat(), Qt.TextFormat.PlainText)
        self.assertTrue(self.workspace.unavailable_message.wordWrap())
        self.assertEqual(self.workspace.f7hub_page.findChildren(QAbstractItemView), [])
        self.assertIsNotNone(self.workspace.source_selector.view())
        self.assertEqual(self.workspace.findChildren(QPushButton), [self.workspace.windows_refresh_button])
        self.assertIs(self.workspace.activation_focus_target(), self.workspace.source_selector)
        self.assertEqual(self.workspace.property("moduleKey"), "clipboard")

    def test_unavailable_information_remains_accessible(self):
        self.assertEqual(self.workspace.accessibleName(), "Clipboard Center")
        self.assertEqual(self.workspace.unavailable_message.accessibleName(),
                         self.workspace.unavailable_message.text())

    def test_two_sources_default_and_truthful_selectable_windows(self):
        w = self.workspace
        self.assertEqual([(w.source_selector.itemText(i), w.source_selector.itemData(i))
                          for i in range(w.source_selector.count())],
                         [("F7Hub Clipboard", "f7hub"), ("Windows Clipboard", "windows")])
        self.assertEqual(w.source_key, "f7hub")
        self.assertIs(w.source_pages.currentWidget(), w.f7hub_page)
        self.assertEqual(w.source_selector.accessibleName(), "Clipboard source")
        self.assertFalse(w.source_selector.isEditable())
        self.assertIs(w.source_label.buddy(), w.source_selector)
        self.assertNotIn("&", w.source_label.text())
        self.assertTrue(w.select_source("windows"))
        self.assertIs(w.source_pages.currentWidget(), w.windows_page)
        self.assertEqual(w.windows_unavailable_message.text(), "Windows Clipboard snapshot is not available yet.")
        self.assertEqual(w.windows_unavailable_message.accessibleName(), w.windows_unavailable_message.text())
        self.assertEqual(w.windows_unavailable_message.textFormat(), Qt.TextFormat.PlainText)
        self.assertTrue(w.windows_unavailable_message.wordWrap())
        self.assertFalse(w.windows_refresh_button.isEnabled())
        self.assertIn("not available", w.windows_refresh_button.accessibleDescription())
        self.assertIs(w.activation_focus_target(), w.source_selector)
        self.assertFalse(w.activate())

    def test_switches_retain_model_widgets_workers_and_do_not_dispatch(self):
        self.compose()
        w = self.workspace
        w.activate()
        self.wait_idle()
        identities = (w.f7hub_page, w.windows_page, w.table, w.model, w.runner, w._service)
        resets = []
        w.model.modelReset.connect(lambda: resets.append(True))
        w.table.setColumnWidth(2, 121)
        with (patch.object(QApplication, "clipboard", side_effect=AssertionError("OS access forbidden")),
              patch("subprocess.Popen", side_effect=AssertionError("Process forbidden"))):
            for _ in range(4):
                self.assertTrue(w.select_source("windows"))
                self.assertFalse(w.refresh())
                self.assertTrue(w.select_source("windows"))
                self.assertTrue(w.select_source("f7hub"))
            self.assertFalse(w.select_source("unknown"))
        self.assertEqual(identities, (w.f7hub_page, w.windows_page, w.table, w.model, w.runner, w._service))
        self.assertEqual(w.findChildren(ServiceTaskRunner), [w.runner])
        self.assertEqual(self.service.calls, [50])
        self.assertEqual(resets, [])
        self.assertEqual(w.table.columnWidth(2), 121)
        self.assertEqual(w.model.rowCount(), 2)

    def test_pending_and_completion_gap_restore_selector_without_switch(self):
        self.compose()
        w = self.workspace
        self.service.gate = threading.Event()
        w.activate()
        observed = []
        w.runner.busy_changed.connect(
            lambda busy: observed.append(w.select_source("windows")) if not busy else None)
        w.source_selector.setCurrentIndex(1)
        w.source_selector.activated.emit(1)
        self.assertEqual(w.source_selector.currentData(), "f7hub")
        self.assertIs(w.source_pages.currentWidget(), w.f7hub_page)
        self.assertIn("finishing", w.source_message.text())
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(observed, [False])
        self.assertTrue(w.select_source("windows"))
        self.assertEqual(w.source_message.accessibleName(), "")

    def test_obsolete_success_and_failure_cannot_replace_windows_or_focus(self):
        self.compose()
        w = self.workspace
        w.activate()
        self.wait_idle()
        old_generation = w._recent_generation
        w.refresh()
        self.wait_idle()
        w.select_source("windows")
        before = (w.model._rows, w.status_message.text(), w.windows_unavailable_message.text())
        w.source_selector.setFocus()
        w._recent_completed(old_generation, recent_page(rows=()))
        w._recent_completed(old_generation, RuntimeError("PRIVATE"), failed=True)
        self.assertEqual((w.model._rows, w.status_message.text(), w.windows_unavailable_message.text()), before)
        self.assertEqual(w.source_key, "windows")
        self.assertTrue(w.source_selector.hasFocus())

    def test_source_scroll_callbacks_are_independent_synchronous_and_noop_safe(self):
        w = self.workspace
        position, restored = [12, 34], []
        w._capture_scroll = lambda: tuple(position)
        w._restore_scroll = lambda value: restored.append(value)
        self.assertTrue(w.select_source("windows"))
        self.assertEqual(restored, [(0, 0)])
        position[:] = [7, 19]
        self.assertTrue(w.select_source("f7hub"))
        self.assertEqual(restored[-1], (12, 34))
        self.assertTrue(w.select_source("windows"))
        self.assertEqual(restored[-1], (7, 19))
        count = len(restored)
        w.select_source("windows")
        self.application.processEvents()
        self.assertEqual(len(restored), count)

    def test_selector_keyboard_switch_and_table_tab_escape(self):
        self.compose()
        w = self.workspace
        w.activate()
        self.wait_idle()
        w.source_selector.setFocus()
        QTest.keyClick(w.source_selector, Qt.Key.Key_Down)
        self.application.processEvents()
        self.assertEqual(w.source_key, "windows")
        QTest.keyClick(w.source_selector, Qt.Key.Key_Up)
        self.application.processEvents()
        self.assertEqual(w.source_key, "f7hub")
        QTest.keyClick(w.source_selector, Qt.Key.Key_Tab)
        self.assertTrue(w.refresh_button.hasFocus())
        QTest.keyClick(w.refresh_button, Qt.Key.Key_Backtab)
        self.assertTrue(w.source_selector.hasFocus())
        w.table.setFocus()
        QTest.keyClick(w.table, Qt.Key.Key_Tab)
        self.assertFalse(w.table.hasFocus())
        self.assertFalse(w.table.tabKeyNavigation())

    def test_failed_recent_status_is_retained_separately_from_windows(self):
        self.compose()
        self.service.error = RuntimeError("PRIVATE")
        self.workspace.activate()
        self.wait_idle()
        self.workspace.select_source("windows")
        self.assertNotIn("could not be loaded", self.workspace.windows_unavailable_message.text())
        self.workspace.select_source("f7hub")
        self.assertEqual(self.workspace.refresh_button.text(), "Retry")
        self.assertEqual(self.service.calls, [50])
        self.service.error = None
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 2)

    def test_optional_services_do_not_change_source_choices_or_create_workers(self):
        from Tests.GUI.test_clipboard_setup import RecordingSettingsService
        for history, preferences in ((False, False), (True, False), (False, True), (True, True)):
            with self.subTest(history=history, preferences=preferences):
                service = RecordingClipboardService() if history else None
                settings = RecordingSettingsService() if preferences else None
                w = ClipboardWorkspace(clipboard_service=service, settings_service=settings)
                try:
                    self.assertEqual(w.source_selector.count(), 2)
                    self.assertEqual(w.source_pages.count(), 2)
                    self.assertTrue(w.select_source("windows"))
                    self.assertFalse(w.activate())
                    self.assertTrue(w.select_source("f7hub"))
                    self.assertEqual(len(w.findChildren(ServiceTaskRunner)), 2 if preferences else 1)
                    if service is not None:
                        self.assertEqual(service.calls, [])
                    if settings is not None:
                        self.assertEqual(settings.reads, 0)
                finally:
                    w.close()
                    w.deleteLater()
        self.application.processEvents()


if __name__ == "__main__":
    unittest.main()
