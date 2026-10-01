from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import bootstrap_database, database_connection


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-09-30T00:00:00.000Z"


class ScriptCatalogFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        migrations = self.root / "Database" / "Migrations"
        migrations.mkdir(parents=True)
        for source in (ROOT / "Database" / "Migrations").glob("*.sql"):
            if int(source.name[:4]) <= 7:
                # Preserve the pre-production-data empty catalog fixture.
                shutil.copyfile(source, migrations / source.name)
        self.database = self.root / "catalog.db"
        self.context = bootstrap_application(project_root=self.root, database_path=self.database)
        self.window = self.context.main_window
        self.window.show()
        self.application.processEvents()
        self.wait_idle()

    def tearDown(self):
        self.wait_idle()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while (self.window.runner.busy or self.window.script_workspace._loading) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Catalog worker did not finish")
        self.assertFalse(self.window.script_workspace._loading, "Catalog callback did not finish")

    def insert_script(self, code, *, enabled=1, path=None, category_id=None):
        with database_connection(self.database) as connection:
            connection.execute(
                "INSERT INTO scripts (script_code, name, description, relative_path, "
                "script_type, category_id, is_enabled, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (code, code.title(), "<b>plain text</b>",
                 path or f"PowerShell/Diagnostics/{code}.ps1", "DIAGNOSTIC",
                 category_id, enabled, STAMP, STAMP),
            )

    def test_empty_then_enabled_catalog_status_and_disabled_exclusion(self):
        workspace = self.window.script_workspace
        self.window.scripts_action.trigger()
        self.wait_idle()
        self.assertTrue(workspace.empty_state.isVisible(),
                        f"page={self.window.pages.currentWidget() is workspace}, "
                        f"feedback={workspace.feedback.text()!r}, rows={workspace.model.rowCount()}")
        fixture = self.root / "PowerShell" / "Diagnostics"
        fixture.mkdir(parents=True)
        (fixture / "present.ps1").write_text("# fixture only\n", encoding="utf-8")
        with database_connection(self.database) as connection:
            category_id = connection.execute(
                "INSERT INTO categories (scope, name, slug, created_at, updated_at) "
                "VALUES ('SCRIPT', 'Networking', 'networking', ?, ?)",
                (STAMP, STAMP),
            ).lastrowid
        self.insert_script("present", category_id=category_id)
        self.insert_script("missing")
        self.insert_script("disabled", enabled=0)
        with patch("subprocess.Popen", side_effect=AssertionError("execution attempted")) as execute:
            workspace.refresh_button.click()
            self.wait_idle()
            execute.assert_not_called()
        self.assertEqual(workspace.model.rowCount(), 2)
        self.assertEqual([workspace.model.item(row, 1).text() for row in range(2)],
                         ["missing", "present"])
        self.assertEqual([workspace.model.item(row, 3).text() for row in range(2)],
                         ["MISSING", "AVAILABLE"])
        self.assertIn("Description: <b>plain text</b>", workspace.details.toPlainText())
        self.assertIn("File status: MISSING", workspace.details.toPlainText())
        workspace.table.selectRow(1)
        self.assertIn("Category: Networking", workspace.details.toPlainText())
        self.assertIn("File found at last refresh.", workspace.details.toPlainText())
        self.assertFalse(workspace.empty_state.isVisible())

    def test_production_snapshot_visible_without_execution(self):
        migrations = self.root / "Database" / "Migrations"
        shutil.copyfile(ROOT / "Database/Migrations/0008_system_snapshot_script.sql",
                        migrations / "0008_system_snapshot_script.sql")
        script = self.root / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
        script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1", script)
        bootstrap_database(self.database, migrations)
        workspace = self.window.script_workspace
        with patch("subprocess.Popen", side_effect=AssertionError("PowerShell launched")) as execute:
            self.window.scripts_action.trigger()
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 1)
            self.assertEqual([workspace.model.item(0, column).text() for column in range(4)],
                             ["Windows System Snapshot", "diagnostic.windows.system_snapshot",
                              "Not selected", "AVAILABLE"])
            details = workspace.details.toPlainText()
            for value in ("Type: DIAGNOSTIC", "Runtime: POWERSHELL_7", "Risk: LOW",
                          "Privilege: STANDARD_USER", "PowerShell reference: PowerShell/Diagnostics/Get-SystemSnapshot.ps1"):
                self.assertIn(value, details)
            workspace.table.selectRow(0)
            workspace.refresh_button.click()
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 1)
            self.assertEqual(workspace.model.item(0, 3).text(), "AVAILABLE")
            execute.assert_not_called()
        self.assertFalse(any(control.text().lower() in {"run", "test", "execute"}
                             for control in workspace.findChildren(QPushButton)))


if __name__ == "__main__":
    unittest.main()
