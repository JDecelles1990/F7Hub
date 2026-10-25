"""Setup GUI through real Settings services and isolated migrated SQLite stores."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.app.bootstrap import bootstrap_application
from f7hub.domain.clipboard_settings import (
    CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED,
)
from f7hub.gui.clipboard_setup import ClipboardSetup
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.repositories.settings_repository import SettingsRepository
from f7hub.services.settings_service import SettingsService
from Tests.Database.clipboard_fixtures import seed_item
from Tests.GUI.test_clipboard_setup import wait_idle


ROOT = Path(__file__).resolve().parents[2]


class ClipboardSetupFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        startup = patch('f7hub.services.mochi_service.MochiService.automatic_start', return_value=False)
        startup.start()
        self.addCleanup(startup.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "selected.db"
        bootstrap_database(self.path, ROOT / "Database/Migrations")
        self.service = self.new_service()
        self.editors = []

    def new_service(self, path=None):
        return SettingsService(SettingsRepository(path or self.path), CLIPBOARD_SETTING_DEFINITIONS)

    def compose(self, service=None):
        editor = ClipboardSetup(service or self.service)
        self.editors.append(editor)
        editor.reload()
        self.wait(editor)
        return editor

    def wait(self, editor):
        wait_idle(self.application, lambda: editor.pending)

    def save(self, editor, keys):
        for key in keys:
            editor.checkboxes[key].setChecked(True)
        self.assertTrue(editor.apply())
        self.wait(editor)

    def tearDown(self):
        for editor in self.editors:
            self.wait(editor)
            editor.cancel()
            editor.close()
            editor.deleteLater()
        self.application.processEvents()
        with database_connection(self.path, read_only=True) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_grouped_gui_apply_restart_and_selected_database_scope(self):
        editor = self.compose()
        with patch.object(self.service, "apply", wraps=self.service.apply) as apply:
            self.save(editor, (WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED))
            apply.assert_called_once_with({d.key: True for d in CLIPBOARD_SETTING_DEFINITIONS}, expected_revision=0)
        self.assertEqual(editor.loaded_revision, 1)
        restarted = self.compose(self.new_service())
        self.assertEqual(restarted._snapshot, editor._snapshot)
        other = Path(self.temporary.name) / "other.db"
        bootstrap_database(other, ROOT / "Database/Migrations")
        scoped = self.compose(self.new_service(other))
        self.assertEqual(scoped.loaded_revision, 0)
        self.assertTrue(all(not c.isChecked() for c in scoped.checkboxes.values()))
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM settings_user_overrides").fetchone()[0], 3)

    def test_noop_and_cancel_preserve_bytes_rows_and_revision(self):
        editor = self.compose()
        before = self.path.read_bytes()
        editor.apply()
        editor.checkboxes[WORKFLOW_ENABLED].setChecked(True)
        editor.cancel()
        editor.apply()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.new_service().get_snapshot().revision, 0)

    def test_two_services_stale_draft_preserved_until_explicit_reload(self):
        first, stale = self.compose(), self.compose(self.new_service())
        self.save(first, (WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED))
        self.save(stale, (SOURCE_TITLE_ENABLED,))
        self.assertTrue(stale.dirty)
        self.assertEqual(stale.loaded_revision, 0)
        self.assertIn("changed elsewhere", stale.status_message.text())
        persisted = self.new_service().get_snapshot()
        self.assertTrue(persisted.get(WORKFLOW_ENABLED).value)
        self.assertFalse(persisted.get(SOURCE_TITLE_ENABLED).value)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            stale.reload()
        self.wait(stale)
        self.assertEqual(stale.loaded_revision, 1)
        self.assertFalse(stale.dirty)
        self.save(stale, (SOURCE_TITLE_ENABLED,))
        self.assertEqual(stale.loaded_revision, 2)

    def test_master_disable_preserves_source_flags_and_existing_history(self):
        with database_connection(self.path) as connection:
            seed_item(connection, item_id=1, retention_intent="SAVED", expires_at=None)
            history = tuple(connection.execute("SELECT * FROM clipboard_items").fetchall()[0])
            event = tuple(connection.execute("SELECT * FROM clipboard_capture_events").fetchall()[0])
        editor = self.compose()
        with (
            patch.object(QApplication, "clipboard", side_effect=AssertionError("No Clipboard effect")),
            patch("subprocess.Popen", side_effect=AssertionError("No process effect")),
        ):
            self.save(editor, (WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED))
            editor.checkboxes[WORKFLOW_ENABLED].setChecked(False)
            editor.apply()
            self.wait(editor)
        self.assertTrue(editor.checkboxes[SOURCE_PROCESS_ENABLED].isChecked())
        self.assertTrue(editor.checkboxes[SOURCE_TITLE_ENABLED].isChecked())
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.execute("SELECT * FROM clipboard_items").fetchall()[0]), history)
            self.assertEqual(tuple(connection.execute("SELECT * FROM clipboard_capture_events").fetchall()[0]), event)

    def test_real_observer_failure_commits_without_false_failed_save(self):
        def broken_observer(_change):
            raise RuntimeError("Synthetic observer failure")
        self.service.subscribe(broken_observer)
        editor = self.compose()
        self.save(editor, (WORKFLOW_ENABLED,))
        self.assertIn("Preferences saved", editor.status_message.text())
        self.assertIn("observer", editor.status_message.text())
        self.assertEqual(self.new_service().get_snapshot().revision, 1)

    def test_missing_store_safe_disabled_and_invalid_sensitive_override(self):
        missing = self.compose(self.new_service(Path(self.temporary.name) / "missing.db"))
        self.assertFalse(missing.apply_button.isEnabled())
        self.assertTrue(all(not c.isChecked() for c in missing.checkboxes.values()))
        with database_connection(self.path) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute("INSERT INTO settings_user_overrides VALUES (?, 'BOOLEAN', ?)", (WORKFLOW_ENABLED, "invalid synthetic Boolean"))
        editor = self.compose()
        self.assertFalse(editor.checkboxes[WORKFLOW_ENABLED].isChecked())
        self.assertIn("Invalid stored", editor.status_message.text())
        self.save(editor, (WORKFLOW_ENABLED,))
        self.assertTrue(self.new_service().get_snapshot().get(WORKFLOW_ENABLED).value)

    def test_bootstrap_injects_same_service_and_retains_one_setup(self):
        with patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False):
            context = bootstrap_application(project_root=ROOT, database_path=self.path)
            window = context.main_window
            try:
                self.assertIs(window.settings_service, context.settings_service)
                window.show_clipboard()
                workspace = window.clipboard_workspace
                wait_idle(self.application, lambda: workspace.loading)
                self.assertIs(workspace.setup._service, context.settings_service)
                workspace.show_setup()
                self.wait(workspace.setup)
                self.save(workspace.setup, (SOURCE_TITLE_ENABLED,))
                workspace.setup.checkboxes[WORKFLOW_ENABLED].setChecked(True)
                with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
                    window.show_knowledge()
                    window.open_knowledge_article(1)
                    window.show_scripts()
                    self.assertIs(window.pages.currentWidget(), workspace)
                    self.assertTrue(workspace.setup.dirty)
                workspace.setup.cancel()
                workspace.show_recent()
                self.assertTrue(window.show_clipboard())
                self.assertEqual(workspace.findChildren(ClipboardSetup), [workspace.setup])
            finally:
                window.request_exit()
                window.deleteLater()
                self.application.processEvents()

    def test_source_guard_and_true_preferences_preserve_database_and_capability(self):
        with patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False):
            context = bootstrap_application(project_root=ROOT, database_path=self.path)
            window = context.main_window
            try:
                window.show_clipboard()
                workspace = window.clipboard_workspace
                wait_idle(self.application, lambda: workspace.loading)
                workspace.show_setup()
                self.wait(workspace.setup)
                self.save(workspace.setup, (WORKFLOW_ENABLED, SOURCE_TITLE_ENABLED))
                editor = workspace.setup
                editor.checkboxes[SOURCE_PROCESS_ENABLED].setChecked(True)
                draft = dict(editor._draft)
                before_bytes = self.path.read_bytes()
                with database_connection(self.path, read_only=True) as connection:
                    before_rows = tuple(connection.iterdump())
                revision = context.settings_service.get_snapshot().revision
                with (patch.object(QApplication, "clipboard", side_effect=AssertionError("OS Clipboard forbidden")),
                      patch("subprocess.Popen", side_effect=AssertionError("Process forbidden")),
                      patch.object(context.settings_service, "apply", side_effect=AssertionError("Switch write forbidden")),
                      patch.object(context.settings_service, "refresh", side_effect=AssertionError("Switch read forbidden")),
                      patch.object(context.clipboard_service, "get_recent", side_effect=AssertionError("Switch read forbidden"))):
                    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
                        self.assertFalse(workspace.select_source("windows"))
                    self.assertEqual(prompt.call_count, 1)
                    self.assertEqual(editor._draft, draft)
                    self.assertEqual(workspace.source_selector.currentData(), "f7hub")
                    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard) as prompt:
                        self.assertTrue(workspace.select_source("windows"))
                    self.assertEqual(prompt.call_count, 1)
                    self.assertFalse(editor.dirty)
                    self.assertFalse(workspace.windows_refresh_button.isEnabled())
                    self.assertTrue(workspace.select_source("f7hub"))
                    self.assertIs(workspace.setup, editor)
                    self.assertIs(editor._service, context.settings_service)
                self.assertEqual(context.settings_service.get_snapshot().revision, revision)
                self.assertEqual(self.path.read_bytes(), before_bytes)
                with database_connection(self.path, read_only=True) as connection:
                    self.assertEqual(tuple(connection.iterdump()), before_rows)
                    self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            finally:
                workspace.setup.cancel()
                window.request_exit()
                window.deleteLater()
                self.application.processEvents()


if __name__ == "__main__":
    unittest.main()
