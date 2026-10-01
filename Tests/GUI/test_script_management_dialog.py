import os
import threading
import time
from dataclasses import replace
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.gui.script_management_dialog import ScriptManagementDialog
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.script_repository import ScriptRecord
from f7hub.services.script_service import ScriptCatalogEntry, ScriptConflictError, ScriptWriteError


def record():
    return ScriptRecord(1, None, None, "one", "One", "<b>plain</b>",
                        "PowerShell/Diagnostics/one.ps1", "DIAGNOSTIC", "POWERSHELL_7", "LOW",
                        "STANDARD_USER", None, None, 120, 1, 0,
                        "2026-10-01T00:00:00.000Z", "2026-10-01T00:00:00.000Z")


class RecordingService:
    def __init__(self):
        self.row = record()
        self.entries = (ScriptCatalogEntry(self.row, "AVAILABLE"),)
        self.read_gate = None
        self.write_gate = None
        self.read_error = None
        self.write_error = None
        self.reads = 0
        self.registrations = []
        self.toggles = []
        self.fail_refresh_after_write = False

    def list_registered_scripts(self):
        self.reads += 1
        if self.read_gate:
            self.read_gate.wait(5)
        if self.read_error:
            raise self.read_error
        return self.entries

    def register_script(self, **values):
        self.registrations.append(values)
        if self.write_gate:
            self.write_gate.wait(5)
        if self.write_error:
            raise self.write_error
        if self.fail_refresh_after_write:
            self.read_error = RuntimeError("private")
        return self.row

    def set_script_enabled(self, script_id, **values):
        self.toggles.append((script_id, values))
        if self.write_gate:
            self.write_gate.wait(5)
        if self.write_error:
            raise self.write_error
        self.row = replace(self.row, is_enabled=int(values["enabled"]), updated_at="2026-10-01T00:00:00.001Z")
        self.entries = (ScriptCatalogEntry(self.row, "AVAILABLE"),)
        if self.fail_refresh_after_write:
            self.read_error = RuntimeError("private")
        return self.row


class ScriptManagementDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingService()
        self.runner = ServiceTaskRunner()
        self.dialog = ScriptManagementDialog(self.service, self.runner)
        self.dialog.show()
        self.app.processEvents()

    def tearDown(self):
        for gate in (self.service.read_gate, self.service.write_gate):
            if gate:
                gate.set()
        self.wait_idle()
        if self.dialog._registration_dialog:
            self.dialog._registration_dialog.reject()
        self.dialog.reject()
        self.dialog.deleteLater()
        self.runner.deleteLater()
        self.app.processEvents()

    def wait_idle(self):
        deadline = time.monotonic() + 6
        while (self.runner.busy or self.dialog._loading or self.dialog._writing) and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.runner.busy)
        self.assertFalse(self.dialog._loading)
        self.assertFalse(self.dialog._writing)

    def load(self):
        self.assertTrue(self.dialog.refresh_list())
        self.wait_idle()

    def registration(self):
        dialog = self.dialog.open_registration()
        self.assertIsNotNone(dialog)
        dialog.code_input.setText("one")
        dialog.name_input.setText("One")
        dialog.path_input.setText("PowerShell/Diagnostics/one.ps1")
        for combo in (dialog.type_input, dialog.risk_input, dialog.privilege_input):
            combo.setCurrentIndex(1)
        return dialog

    def test_scoped_rows_metadata_selection_refresh_and_empty_state(self):
        self.load()
        self.assertEqual(self.dialog.model.item(0, 2).text(), "No")
        self.assertEqual(self.dialog.toggle_button.text(), "Enable")
        self.assertIn("<b>plain</b>", self.dialog.details.toPlainText())
        self.assertIn("Stored checksum: None", self.dialog.details.toPlainText())
        self.service.entries = ()
        self.load()
        self.assertEqual(self.dialog.feedback.text(), "No registrations.")
        self.assertFalse(self.dialog.toggle_button.isEnabled())

    def test_enable_cancel_then_confirm_and_disable_uses_loaded_token(self):
        self.load()
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.dialog.toggle_selected())
        self.assertEqual(self.service.toggles, [])
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            self.assertTrue(self.dialog.toggle_selected())
        self.wait_idle()
        self.assertEqual(self.service.toggles[0], (1, dict(enabled=True, expected_updated_at=record().updated_at)))
        self.assertEqual(self.dialog.toggle_button.text(), "Disable")
        self.dialog.toggle_button.setFocus()
        QTest.keyClick(self.dialog.toggle_button, Qt.Key.Key_Space)
        self.wait_idle()
        self.assertFalse(self.service.toggles[-1][1]["enabled"])
        self.assertTrue(self.dialog.changed)

    def test_registration_cancel_and_failure_preserve_input_and_safe_feedback(self):
        child = self.registration()
        child.reject()
        self.assertEqual(self.service.registrations, [])
        child = self.registration()
        self.service.write_error = RuntimeError("private raw error")
        self.assertTrue(child.submit())
        self.wait_idle()
        self.assertEqual(child.code_input.text(), "one")
        self.assertTrue(child.isVisible())
        self.assertNotIn("private", child.feedback.text())
        self.assertTrue(child.register_button.isEnabled())

    def test_registration_busy_blocks_duplicates_dismissal_and_keeps_dialog_enabled_in_shell(self):
        child = self.registration()
        self.service.write_gate = threading.Event()
        self.assertTrue(child.submit())
        self.assertFalse(child.submit())
        child.reject()
        child.close()
        self.dialog.reject()
        self.assertTrue(child.isVisible())
        self.assertTrue(self.dialog.isVisible())
        self.assertFalse(child.cancel_button.isEnabled())
        self.service.write_gate.set()
        self.wait_idle()
        self.assertEqual(len(self.service.registrations), 1)
        self.assertTrue(self.dialog.changed)
        self.assertIn("registered disabled", self.dialog.feedback.text())

    def test_saved_registration_failed_refresh_then_retry_never_repeats_write(self):
        child = self.registration()
        self.service.fail_refresh_after_write = True
        child.submit()
        self.wait_idle()
        self.assertTrue(self.dialog.changed)
        self.assertIn("Script registered disabled.", self.dialog.feedback.text())
        self.assertIn("Could not refresh", self.dialog.feedback.text())
        self.assertFalse(self.dialog.toggle_button.isEnabled())
        self.assertEqual(self.dialog.model.rowCount(), 0)
        self.service.read_error = None
        self.load()
        self.assertEqual(len(self.service.registrations), 1)
        self.assertEqual(self.dialog.model.rowCount(), 1)

    def test_toggle_busy_stale_failure_and_read_retry(self):
        self.load()
        self.service.write_gate = threading.Event()
        self.service.write_error = ScriptConflictError("Registration changed. Refresh before trying again.")
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            self.assertTrue(self.dialog.toggle_selected())
        self.assertFalse(self.dialog.toggle_selected())
        self.dialog.reject()
        self.assertTrue(self.dialog.isVisible())
        self.service.write_gate.set()
        self.wait_idle()
        self.assertFalse(self.dialog.changed)
        self.assertFalse(self.dialog.toggle_button.isEnabled())
        self.assertIn("Refresh", self.dialog.feedback.text())
        self.load()
        self.assertEqual(self.dialog.model.rowCount(), 1)

    def test_saved_toggle_failed_reload_is_truthful(self):
        self.load()
        self.service.fail_refresh_after_write = True
        with patch.object(QMessageBox, "exec", return_value=QMessageBox.StandardButton.Yes):
            self.dialog.toggle_selected()
        self.wait_idle()
        self.assertIn("Script enabled.", self.dialog.feedback.text())
        self.assertIn("Could not refresh", self.dialog.feedback.text())
        self.assertTrue(self.dialog.changed)

    def test_dismissed_read_discards_late_success_or_error(self):
        for failure in (None, RuntimeError("private")):
            with self.subTest(failure=failure):
                dialog = ScriptManagementDialog(self.service, self.runner)
                dialog.show()
                self.service.read_gate = threading.Event()
                self.service.read_error = failure
                dialog.refresh_list()
                dialog.reject()
                self.service.read_gate.set()
                self.wait_idle()
                self.assertEqual(dialog.model.rowCount(), 0)
                self.assertTrue(dialog._closed)
                self.assertNotIn("private", dialog.feedback.text())
                dialog.deleteLater()
                self.app.processEvents()
