from __future__ import annotations

import os
import hashlib
from pathlib import Path
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox

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
        while (self.window.runner.busy or self.window.script_workspace._loading or
               self.window.script_workspace._copying) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Catalog worker did not finish")
        self.assertFalse(self.window.script_workspace._loading, "Catalog callback did not finish")
        self.assertFalse(self.window.script_workspace._copying, "Copy callback did not finish")

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

    def test_register_enable_copy_rejection_disable_and_catalog_reconciliation(self):
        folder = self.root / "PowerShell" / "Diagnostics"
        folder.mkdir(parents=True)
        (folder / "registered.ps1").write_text("# fixture only", encoding="utf-8")
        self.window.show_scripts()
        self.wait_idle()
        workspace = self.window.script_workspace
        manager = workspace.open_management()
        self.wait_idle()
        self.assertIs(manager.parent(), self.window)
        child = manager.open_registration()
        child.code_input.setText("registered")
        child.name_input.setText("Registered fixture")
        child.path_input.setText("PowerShell\\Diagnostics\\registered.ps1")
        for combo in (child.type_input, child.risk_input, child.privilege_input):
            combo.setCurrentIndex(1)
        child.register_button.click()
        self.wait_idle()
        self.assertEqual(manager.model.rowCount(), 1)
        self.assertEqual(manager.model.item(0, 2).text(), "No")
        self.assertEqual(self.context.script_service.list_scripts(), ())
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            manager.toggle_button.click()
        self.wait_idle()
        self.assertEqual(manager.model.item(0, 2).text(), "Yes")
        row = self.context.script_service.list_scripts()[0].metadata
        self.assertEqual((row.timeout_seconds, row.is_enabled, row.checksum_sha256), (120, 1, None))
        manager.reject()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 1)
        original_clipboard = self.application.clipboard().text()
        try:
            self.application.clipboard().setText("preserve fixture")
            workspace.copy_button.click()
            self.wait_idle()
            self.assertEqual(self.application.clipboard().text(), "preserve fixture")
            self.assertEqual(workspace.feedback.text(), "Script integrity has not been approved.")
        finally:
            self.application.clipboard().setText(original_clipboard)
        manager = workspace.open_management()
        self.wait_idle()
        manager.toggle_button.click()
        self.wait_idle()
        manager.reject()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 0)
        self.assertEqual(len(self.context.script_service.list_registered_scripts()), 1)

    def test_denied_read_preserves_registration_form_and_persisted_visibility(self):
        folder = self.root / "PowerShell" / "Diagnostics"
        folder.mkdir(parents=True)
        (folder / "denied.ps1").write_bytes(b"# fixture only\n")
        self.window.show_scripts()
        self.wait_idle()
        manager = self.window.script_workspace.open_management()
        self.wait_idle()
        child = manager.open_registration()
        child.code_input.setText("denied")
        child.name_input.setText("Denied fixture")
        child.path_input.setText("PowerShell/Diagnostics/denied.ps1")
        for combo in (child.type_input, child.risk_input, child.privilege_input):
            combo.setCurrentIndex(1)

        def persisted():
            with database_connection(self.database) as connection:
                return tuple(connection.iterdump())

        before = persisted()
        with patch.object(Path, "open", side_effect=PermissionError("private ACL detail")):
            child.register_button.click()
            self.wait_idle()
        self.assertEqual(persisted(), before)
        self.assertTrue(child.isVisible())
        self.assertEqual(child.code_input.text(), "denied")
        self.assertEqual(child.path_input.text(), "PowerShell/Diagnostics/denied.ps1")
        self.assertNotIn("private", child.feedback.text())
        self.assertIn("existing readable", child.feedback.text())
        child.register_button.click()
        self.wait_idle()
        self.assertEqual(manager.model.rowCount(), 1)
        disabled = manager._selected()
        self.assertEqual(disabled.is_enabled, 0)
        self.assertIsNone(disabled.checksum_sha256)
        before = persisted()
        with patch.object(Path, "open", side_effect=PermissionError("private ACL detail")), \
                patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            manager.toggle_button.click()
            self.wait_idle()
        self.assertEqual(persisted(), before)
        self.assertEqual(manager._selected(), disabled)
        self.assertNotIn("private", manager.feedback.text())
        self.assertIn("existing readable", manager.feedback.text())
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            manager.toggle_button.click()
        self.wait_idle()
        self.assertEqual(manager._selected().is_enabled, 1)
        self.assertIsNone(manager._selected().checksum_sha256)
        with patch.object(Path, "open", side_effect=PermissionError("private ACL detail")) as opener:
            manager.toggle_button.click()
            self.wait_idle()
        opener.assert_not_called()
        self.assertEqual(manager._selected().is_enabled, 0)
        self.assertIsNone(manager._selected().checksum_sha256)
        self.assertEqual(manager.model.rowCount(), 1)
        manager.reject()
        self.wait_idle()

    def test_changed_manager_dismissed_during_read_refreshes_catalog_after_late_callback(self):
        folder = self.root / "PowerShell" / "Diagnostics"
        folder.mkdir(parents=True)
        (folder / "one.ps1").write_text("# fixture", encoding="utf-8")
        row = self.context.script_service.register_script(
            script_code="one", name="One", relative_path="PowerShell/Diagnostics/one.ps1",
            script_type="DIAGNOSTIC", risk_level="LOW", privilege_level="STANDARD_USER",
        )
        self.window.show_scripts()
        self.wait_idle()
        manager = self.window.script_workspace.open_management()
        self.wait_idle()
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            manager.toggle_selected()
        self.wait_idle()
        import threading
        gate = threading.Event()
        original_list = self.context.script_service.list_registered_scripts
        def delayed():
            gate.wait(5)
            return original_list()
        try:
            with patch.object(self.context.script_service, "list_registered_scripts", side_effect=delayed):
                manager.refresh_list()
                manager.reject()
                gate.set()
                self.wait_idle()
        finally:
            gate.set()
        self.assertEqual(self.window.script_workspace.model.rowCount(), 1)
        self.assertIsNone(self.window.script_workspace._management_dialog)

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

    def test_approved_snapshot_copies_exact_source_and_failures_preserve_clipboard(self):
        migrations = self.root / "Database" / "Migrations"
        for name in ("0008_system_snapshot_script.sql", "0009_system_snapshot_checksum.sql"):
            shutil.copyfile(ROOT / "Database/Migrations" / name, migrations / name)
        script = self.root / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1"
        script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "PowerShell/Diagnostics/Get-SystemSnapshot.ps1", script)
        original = script.read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        bootstrap_database(self.database, migrations)
        with database_connection(self.database) as connection:
            checksum = connection.execute("SELECT checksum_sha256 FROM scripts WHERE "
                                          "script_code='diagnostic.windows.system_snapshot'").fetchone()[0]
        self.assertEqual(checksum, original_hash)
        workspace = self.window.script_workspace
        clipboard = self.application.clipboard()
        previous = clipboard.text()
        self.addCleanup(clipboard.setText, previous)
        with patch("subprocess.Popen", side_effect=AssertionError("PowerShell launched")) as execute:
            self.window.scripts_action.trigger()
            self.wait_idle()
            self.assertEqual(workspace.model.item(0, 3).text(), "AVAILABLE")
            self.assertTrue(workspace.copy_button.isEnabled())
            workspace.copy_button.click()
            self.wait_idle()
            self.assertEqual(clipboard.text(), original.decode("utf-8"))
            self.assertEqual(workspace.feedback.text(), "PowerShell script copied to clipboard.")
            execute.assert_not_called()
        self.assertEqual(script.read_bytes(), original)

        clipboard.setText("preserve")
        script.write_bytes(original + b"# changed")
        workspace.copy_button.click()
        self.wait_idle()
        self.assertEqual(clipboard.text(), "preserve")
        self.assertEqual(workspace.feedback.text(), "Script changed since approval. Copy blocked.")
        script.unlink()
        workspace.copy_button.click()
        self.wait_idle()
        self.assertEqual(clipboard.text(), "preserve")
        self.assertEqual(workspace.feedback.text(), "Script file is no longer available.")


    def test_network_snapshot_search_copy_and_visibility_without_execution(self):
        migrations = self.root / "Database" / "Migrations"
        for name in ("0008_system_snapshot_script.sql", "0009_system_snapshot_checksum.sql",
                     "0010_network_snapshot_script.sql"):
            shutil.copyfile(ROOT / "Database/Migrations" / name, migrations / name)
        for name in ("Get-SystemSnapshot.ps1", "Get-NetworkSnapshot.ps1"):
            target = self.root / "PowerShell/Diagnostics" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "PowerShell/Diagnostics" / name, target)
        bootstrap_database(self.database, migrations)
        target = self.root / "PowerShell/Diagnostics/Get-NetworkSnapshot.ps1"
        original = target.read_bytes()
        workspace = self.window.script_workspace
        clipboard = self.application.clipboard()
        previous = clipboard.text()
        self.addCleanup(clipboard.setText, previous)
        with patch("subprocess.Popen", side_effect=AssertionError("PowerShell launched")) as execute:
            self.window.scripts_action.trigger()
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 2)
            workspace.search_input.setText("network configuration")
            QTest.keyClick(workspace.search_input, Qt.Key.Key_Return)
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 1)
            self.assertEqual(workspace.model.item(0, 1).text(), "diagnostic.windows.network_snapshot")
            self.assertIn("File status: AVAILABLE", workspace.details.toPlainText())
            self.assertIn("Privilege: STANDARD_USER", workspace.details.toPlainText())
            workspace.copy_button.click()
            self.wait_idle()
            self.assertEqual(clipboard.text(), original.decode("utf-8"))
            clipboard.setText("preserve")
            target.write_bytes(original + b"# changed\r\n")
            workspace.copy_button.click()
            self.wait_idle()
            self.assertEqual(clipboard.text(), "preserve")
            self.assertEqual(workspace.feedback.text(), "Script changed since approval. Copy blocked.")
            target.write_bytes(original)
            manager = workspace.open_management()
            self.wait_idle()
            self.assertEqual(manager.model.rowCount(), 2)
            self.assertIn("Stored checksum: " + hashlib.sha256(original).hexdigest(), manager.details.toPlainText())
            manager.toggle_button.click()
            self.wait_idle()
            self.assertEqual(self.context.script_service.list_scripts(text_query="network"), ())
            with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
                manager.toggle_button.click()
                self.wait_idle()
            row = self.context.script_repository.get_script("diagnostic.windows.network_snapshot")
            self.assertEqual(row.checksum_sha256, hashlib.sha256(original).hexdigest())
            manager.reject()
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 1)
            workspace.clear_search_button.click()
            self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 2)
            execute.assert_not_called()

    def test_search_navigation_reconstruction_and_persisted_metadata_no_writes(self):
        self.insert_script("code-needle")
        self.insert_script("name-only")
        self.insert_script("description-only")
        self.insert_script("unrelated")
        self.insert_script("disabled-needle", enabled=0)
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET name='Needle name', description=NULL WHERE script_code='name-only'")
            connection.execute("UPDATE scripts SET description='Needle purpose' WHERE script_code='description-only'")
            before = tuple(connection.iterdump())
        workspace = self.window.script_workspace
        self.window.show_scripts()
        self.wait_idle()
        workspace.search_input.setText("needle")
        workspace.search_button.click()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 3)
        workspace.search_input.setText("unrelated")
        self.window.show_tickets()
        self.wait_idle()
        self.window.show_scripts()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 3)
        self.assertEqual(workspace.search_input.text(), "unrelated")
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()
        self.context = bootstrap_application(project_root=self.root, database_path=self.database)
        self.window = self.context.main_window
        self.window.show()
        self.window.show_scripts()
        self.wait_idle()
        self.assertEqual(self.window.script_workspace.search_input.text(), "")
        self.assertEqual(self.window.script_workspace.model.rowCount(), 4)

    def test_filtered_management_write_success_and_failed_refresh_retry_without_rewrite(self):
        folder = self.root / "PowerShell" / "Diagnostics"
        folder.mkdir(parents=True)
        (folder / "needle.ps1").write_text("# harmless fixture", encoding="utf-8")
        registered = self.context.script_service.register_script(
            script_code="needle", name="Needle", relative_path="PowerShell/Diagnostics/needle.ps1",
            script_type="DIAGNOSTIC", risk_level="LOW", privilege_level="STANDARD_USER")
        self.insert_script("other")
        self.window.show_scripts()
        self.wait_idle()
        workspace = self.window.script_workspace
        workspace.search_input.setText("needle")
        workspace.search_scripts()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 0)
        manager = workspace.open_management()
        self.wait_idle()
        self.assertEqual(manager.model.rowCount(), 2)
        selected = next(i for i, item in enumerate(manager._entries)
                        if item.metadata.script_id == registered.script_id)
        manager.table.selectRow(selected)
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            manager.toggle_selected()
        self.wait_idle()
        manager.reject()
        self.wait_idle()
        self.assertEqual(workspace.model.rowCount(), 1)
        workspace.search_input.setText("unapplied draft")
        manager = workspace.open_management()
        self.wait_idle()
        manager.table.selectRow(next(i for i, item in enumerate(manager._entries)
                                    if item.metadata.script_id == registered.script_id))
        service = self.context.script_service
        with patch.object(service, "set_script_enabled", wraps=service.set_script_enabled) as write:
            with patch.object(service, "list_registered_scripts", side_effect=RuntimeError("private refresh failure")):
                manager.toggle_selected()
                self.wait_idle()
                self.assertIn("disabled", manager.feedback.text().lower())
                self.assertIn("Could not refresh", manager.feedback.text())
                self.assertNotIn("private", manager.feedback.text())
            with patch.object(service, "list_scripts", side_effect=RuntimeError("private catalog failure")):
                manager.reject()
                self.wait_idle()
            self.assertEqual(workspace.model.rowCount(), 0)
            self.assertIn("Select Refresh", workspace.feedback.text())
            self.assertEqual(workspace.search_input.text(), "unapplied draft")
            workspace.refresh_list()
            self.wait_idle()
            self.assertEqual(workspace.empty_state.text(), "No scripts match your search.")
            self.assertEqual(write.call_count, 1)
            with database_connection(self.database) as connection:
                record = connection.execute("SELECT is_enabled, checksum_sha256 FROM scripts WHERE script_id=?",
                                            (registered.script_id,)).fetchone()
                self.assertEqual(tuple(record), (0, None))

if __name__ == "__main__":
    unittest.main()
