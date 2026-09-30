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
from f7hub.services.script_service import ScriptCatalogEntry


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
        self.gate = None
        self.error = None

    def list_scripts(self):
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        return self.entries


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

    def tearDown(self):
        if self.service.gate:
            self.service.gate.set()
        self.wait_idle()
        self.workspace.close()
        self.workspace.deleteLater()
        self.runner.deleteLater()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while (self.runner.busy or self.workspace._loading) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.runner.busy, "Catalog worker did not finish")
        self.assertFalse(self.workspace._loading, "Catalog callback did not finish")

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
        self.assertEqual(self.workspace.findChildren(QPushButton), [self.workspace.refresh_button])

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


if __name__ == "__main__":
    unittest.main()
