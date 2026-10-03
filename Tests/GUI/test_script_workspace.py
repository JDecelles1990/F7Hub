from __future__ import annotations

import os
import threading
import time
import unittest
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from f7hub.gui.script_workspace import ScriptWorkspace
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.services.script_service import ScriptCatalogEntry, ScriptCopyError, ScriptValidationError


def entry(code="ONE", *, status="AVAILABLE", description="Details", name=None):
    return ScriptCatalogEntry(SimpleNamespace(
        name=name or code, script_code=code, category_name="Networking",
        description=description, script_type="DIAGNOSTIC", runtime="POWERSHELL_7",
        risk_level="LOW", privilege_level="STANDARD_USER",
        relative_path=f"PowerShell/Diagnostics/{code}.ps1",
    ), status)


class RecordingService:
    def __init__(self):
        self.entries = ()
        self.calls = 0
        self.queries = []
        self.gate = None
        self.error = None
        self.copy_gate = None
        self.copy_error = None
        self.source = "# exact source\r\nWrite-Output 'hello'\r\n"
        self.read_calls = []

    def list_scripts(self, *, text_query=None):
        self.calls += 1
        self.queries.append(text_query)
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        if text_query is not None and "\x00" in text_query:
            raise ScriptValidationError("invalid search")
        if text_query is None:
            return self.entries
        return tuple(item for item in self.entries if any(
            text_query.lower() in (value or "").lower() for value in
            (item.metadata.name, item.metadata.script_code, item.metadata.description)))

    def read_verified_script(self, code):
        self.read_calls.append(code)
        if self.copy_gate:
            self.copy_gate.wait(3)
        if self.copy_error:
            raise self.copy_error
        return self.source


class ScriptWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingService()
        self.runner = ServiceTaskRunner()
        self.workspace = ScriptWorkspace(self.service, self.runner)
        self.workspace.show()
        self.application.processEvents()
        self.previous_clipboard = self.application.clipboard().text()

    def tearDown(self):
        if self.service.gate:
            self.service.gate.set()
        if self.service.copy_gate:
            self.service.copy_gate.set()
        self.wait_idle()
        self.application.clipboard().setText(self.previous_clipboard)
        self.workspace.close()
        self.workspace.deleteLater()
        self.runner.deleteLater()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while (self.runner.busy or self.workspace._loading or self.workspace._copying) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.runner.busy, "Catalog worker did not finish")
        self.assertFalse(self.workspace._loading, "Catalog callback did not finish")
        self.assertFalse(self.workspace._copying, "Copy callback did not finish")

    def test_construction_empty_and_columns(self):
        self.assertEqual(self.workspace.heading.text(), "Scripts")
        self.assertEqual([self.workspace.model.headerData(i, Qt.Orientation.Horizontal)
                          for i in range(4)], ["Name", "Code", "Category", "File status"])
        self.assertTrue(self.workspace.refresh_list())
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertTrue(self.workspace.empty_state.isVisible())
        self.assertEqual(self.workspace.empty_state.text(), "No scripts available.")
        self.assertEqual(self.workspace.details.toPlainText(), "")

    def test_populated_selection_detail_and_keyboard(self):
        self.service.entries = (entry("ONE"), entry("TWO", description="Second"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.assertEqual(self.workspace.model.item(0, 0).text(), "ONE")
        self.assertEqual(self.workspace.model.item(0, 2).text(), "Networking")
        self.assertEqual(self.workspace.table.currentIndex().row(), 0)
        self.assertIn("Code: ONE", self.workspace.details.toPlainText())
        self.assertIn("Type: DIAGNOSTIC", self.workspace.details.toPlainText())
        self.assertIn("File found at last refresh.", self.workspace.details.toPlainText())
        self.workspace.table.setFocus()
        QTest.keyClick(self.workspace.table, Qt.Key.Key_Down)
        self.assertEqual(self.workspace.table.currentIndex().row(), 1)
        self.assertIn("Description: Second", self.workspace.details.toPlainText())
        self.assertTrue(self.workspace.table.hasFocus())

    def test_refresh_preserves_code_then_falls_back_and_clears_stale_data(self):
        self.service.entries = (entry("ONE"), entry("TWO"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.workspace.table.selectRow(1)
        self.service.entries = (entry("TWO"), entry("THREE"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertEqual(self.workspace.table.currentIndex().row(), 0)
        self.assertIn("Code: TWO", self.workspace.details.toPlainText())
        self.service.entries = (entry("THREE"),)
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertIn("Code: THREE", self.workspace.details.toPlainText())

    def test_statuses_unknown_long_plain_text_and_nonclickable_reference(self):
        long_text = "<b>not markup</b>\n" + "x" * 1000
        self.service.entries = tuple(entry(str(i), status=status, description=long_text)
                                     for i, status in enumerate((
                                         "AVAILABLE", "MISSING", "INACCESSIBLE",
                                         "INVALID_REFERENCE", "SURPRISE",
                                     )))
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertEqual([self.workspace.model.item(i, 3).text() for i in range(5)],
                         ["AVAILABLE", "MISSING", "INACCESSIBLE", "INVALID_REFERENCE", "Unknown"])
        self.assertTrue(self.workspace.details.isReadOnly())
        self.assertIn(long_text, self.workspace.details.toPlainText())
        self.assertIn("PowerShell reference: PowerShell/Diagnostics/0.ps1",
                      self.workspace.details.toPlainText())
        self.assertNotIn("<b>not markup</b>", self.workspace.details.document().toHtml())
        for row, status in enumerate(("AVAILABLE", "MISSING", "INACCESSIBLE", "INVALID_REFERENCE")):
            self.workspace.table.selectRow(row)
            self.assertIn(f"File status: {status}", self.workspace.details.toPlainText())
        self.workspace.table.selectRow(4)
        self.assertIn("File status: Unknown", self.workspace.details.toPlainText())
        self.assertNotIn("File found", self.workspace.details.toPlainText())
        self.assertEqual(set(self.workspace.findChildren(QPushButton)),
                         {self.workspace.refresh_button, self.workspace.copy_button, self.workspace.manage_button,
                          self.workspace.search_button, self.workspace.clear_search_button, self.workspace.run_button})
        self.assertEqual(self.workspace.copy_button.text(), "Copy Script")
        self.assertEqual(self.workspace.copy_button.accessibleName(), "Copy Script")
        self.assertEqual(self.workspace.run_button.text(), "Run diagnostic")
        self.assertFalse(self.workspace.run_button.isEnabled(), "Unpermitted selection has no execution action")

    def test_loading_duplicate_prevention_failure_and_retry(self):
        self.service.entries = (entry(),)
        self.workspace.refresh_list()
        self.wait_idle()
        self.service.gate = threading.Event()
        self.service.error = RuntimeError("PRIVATE_SCRIPT_ERROR")
        self.assertTrue(self.workspace.refresh_list())
        self.assertEqual(self.workspace.feedback.text(), "Loading scripts…")
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertEqual(self.workspace.details.toPlainText(), "")
        self.assertFalse(self.workspace.refresh_button.isEnabled())
        self.assertFalse(self.workspace.refresh_list())
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(self.service.calls, 2)
        self.assertEqual(self.workspace.feedback.text(),
                         "Could not load scripts. Select Refresh to try again.")
        self.assertNotIn("PRIVATE_SCRIPT_ERROR", self.workspace.feedback.text())
        self.assertFalse(self.workspace.empty_state.isVisible())
        self.assertTrue(self.workspace.refresh_button.isEnabled())
        self.service.error = None
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.service.calls, 3)
        self.assertEqual(self.workspace.model.rowCount(), 1)
        self.assertEqual(self.workspace.feedback.text(), "")

    def test_copy_requires_available_selection_and_copies_exact_source(self):
        self.assertFalse(self.workspace.copy_button.isEnabled())
        self.assertFalse(self.workspace.copy_script())
        self.service.entries = (entry("MISSING", status="MISSING"), entry("ONE"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertFalse(self.workspace.copy_button.isEnabled())
        self.workspace.table.selectRow(1)
        self.assertTrue(self.workspace.copy_button.isEnabled())
        self.application.clipboard().setText("unchanged")
        self.workspace.copy_button.click()
        self.wait_idle()
        self.assertEqual(self.service.read_calls, ["ONE"])
        self.assertEqual(self.application.clipboard().text(), self.service.source)
        self.assertEqual(self.workspace.feedback.text(), "PowerShell script copied to clipboard.")

    def test_copy_failures_keep_clipboard_and_hide_raw_error(self):
        self.service.entries = (entry(),)
        self.workspace.refresh_list()
        self.wait_idle()
        for error, message in (
            (ScriptCopyError("INTEGRITY_NOT_APPROVED"), "Script integrity has not been approved."),
            (ScriptCopyError("INTEGRITY_MISMATCH"), "Script changed since approval. Copy blocked."),
            (ScriptCopyError("FILE_UNAVAILABLE"), "Script file is no longer available."),
            (RuntimeError("PRIVATE_SCRIPT_ERROR"), "Script could not be read."),
        ):
            with self.subTest(error=error):
                self.application.clipboard().setText("unchanged")
                self.service.copy_error = error
                self.workspace.copy_button.click()
                self.wait_idle()
                self.assertEqual(self.application.clipboard().text(), "unchanged")
                self.assertEqual(self.workspace.feedback.text(), message)
                self.assertNotIn("PRIVATE_SCRIPT_ERROR", self.workspace.feedback.text())

    def test_duplicate_click_and_stale_selection_discard(self):
        self.service.entries = (entry("ONE"), entry("TWO"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.application.clipboard().setText("unchanged")
        self.service.copy_gate = threading.Event()
        self.assertTrue(self.workspace.copy_script())
        self.assertEqual(self.workspace.feedback.text(), "Verifying script…")
        self.assertFalse(self.workspace.copy_button.isEnabled())
        self.assertFalse(self.workspace.copy_script())
        self.workspace.table.selectRow(1)
        self.service.copy_gate.set()
        self.wait_idle()
        self.assertEqual(self.service.read_calls, ["ONE"])
        self.assertEqual(self.application.clipboard().text(), "unchanged")
        self.assertNotEqual(self.workspace.feedback.text(), "PowerShell script copied to clipboard.")
        self.assertTrue(self.workspace.copy_button.isEnabled())

    def test_manual_search_enter_clear_draft_refresh_and_selection(self):
        self.service.entries = (entry("ONE", name="Needle"), entry("TWO", description="Needle"), entry("THREE"))
        self.workspace.refresh_list()
        self.wait_idle()
        self.workspace.table.selectRow(1)
        self.workspace.search_input.setText("  needle  ")
        self.assertEqual(self.workspace.model.rowCount(), 3)
        self.workspace.search_button.click()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.assertIn("Code: TWO", self.workspace.details.toPlainText())
        self.workspace.search_input.setText("THREE")
        self.workspace.refresh_button.click()
        self.wait_idle()
        self.assertEqual(self.service.queries[-1], "needle")
        self.assertEqual(self.workspace.search_input.text(), "THREE")
        self.assertEqual(self.workspace.model.rowCount(), 2)
        self.workspace.search_input.setFocus()
        QTest.keyClick(self.workspace.search_input, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertEqual(self.service.queries[-1], "THREE")
        self.assertIn("Code: THREE", self.workspace.details.toPlainText())
        self.workspace.clear_search_button.click()
        self.wait_idle()
        self.assertIsNone(self.service.queries[-1])
        self.assertEqual(self.workspace.search_input.text(), "")
        self.assertEqual(self.workspace.model.rowCount(), 3)
        self.workspace.search_input.setText(" \t ")
        self.workspace.search_scripts()
        self.wait_idle()
        self.assertIsNone(self.service.queries[-1])

    def test_filtered_empty_failure_retry_and_validation_recovery(self):
        self.service.entries = (entry(),)
        self.workspace.search_input.setText("missing")
        self.workspace.search_scripts()
        self.wait_idle()
        self.assertEqual(self.workspace.empty_state.text(), "No scripts match your search.")
        self.assertTrue(self.workspace.empty_state.isVisible())
        self.assertEqual(self.workspace.details.toPlainText(), "")
        self.assertFalse(self.workspace.copy_button.isEnabled())
        self.assertTrue(self.workspace.manage_button.isEnabled())
        self.service.error = RuntimeError("private failure")
        self.workspace.search_input.setText("ONE")
        self.workspace.search_scripts()
        self.wait_idle()
        self.assertFalse(self.workspace.empty_state.isVisible())
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.assertNotIn("private", self.workspace.feedback.text())
        self.service.error = None
        self.workspace.search_input.setText("draft")
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertEqual(self.service.queries[-1], "ONE")
        self.assertEqual(self.workspace.search_input.text(), "draft")
        self.assertEqual(self.workspace.model.rowCount(), 1)
        self.workspace.search_input.setText("ONE\x00missing")
        self.workspace.search_scripts()
        self.wait_idle()
        self.assertIn("Edit it", self.workspace.feedback.text())
        self.assertEqual(self.workspace.model.rowCount(), 0)
        self.workspace.clear_search()
        self.wait_idle()
        self.assertEqual(self.workspace.model.rowCount(), 1)
        self.service.entries = ()
        self.workspace.refresh_list()
        self.wait_idle()
        self.assertEqual(self.workspace.empty_state.text(), "No scripts available.")

    def test_search_busy_and_idle_before_callbacks_preserve_request_state(self):
        self.service.entries = (entry("ONE"), entry("TWO"))
        self.service.gate = threading.Event()
        self.workspace.search_input.setText("ONE")
        self.assertTrue(self.workspace.search_scripts())
        self.workspace.search_input.setText("TWO")
        self.assertFalse(self.workspace.search_scripts())
        self.assertFalse(self.workspace.clear_search())
        self.assertFalse(self.workspace.refresh_list())
        attempts = []
        def premature(busy):
            if not busy and self.workspace._loading:
                attempts.append((self.workspace.search_scripts(), self.workspace.clear_search(),
                                 self.workspace.refresh_list(), self.workspace.search_button.isEnabled()))
        self.runner.busy_changed.connect(premature)
        self.service.gate.set()
        self.wait_idle()
        self.runner.busy_changed.disconnect(premature)
        self.assertEqual(attempts, [(False, False, False, False)])
        self.assertEqual(self.service.queries, ["ONE"])
        self.assertEqual(self.workspace.search_input.text(), "TWO")
        self.assertEqual(self.workspace.model.item(0, 0).text(), "ONE")

    def test_copy_busy_search_guards_and_page_departure(self):
        self.service.entries = (entry(),)
        self.workspace.refresh_list()
        self.wait_idle()
        self.application.clipboard().setText("preserve")
        self.service.copy_gate = threading.Event()
        self.workspace.copy_script()
        self.workspace.search_input.setText("missing")
        self.assertFalse(self.workspace.search_scripts())
        self.assertFalse(self.workspace.clear_search())
        self.assertFalse(self.workspace.refresh_list())
        attempts = []
        def premature(busy):
            if not busy and self.workspace._copying:
                attempts.append((self.workspace.search_scripts(), self.workspace.clear_search(),
                                 self.workspace.refresh_list()))
        self.runner.busy_changed.connect(premature)
        self.workspace.hide()
        self.service.copy_gate.set()
        self.wait_idle()
        self.runner.busy_changed.disconnect(premature)
        self.assertEqual(attempts, [(False, False, False)])
        self.assertEqual(self.application.clipboard().text(), "preserve")
        self.assertEqual(self.service.queries, [None])


if __name__ == "__main__":
    unittest.main()
