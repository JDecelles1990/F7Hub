"""Noninteractive draft, async, safe feedback and shell lifecycle checks."""

import os
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.domain.clipboard_settings import (
    CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED,
)
from f7hub.domain.settings import EffectiveSetting, SettingsSnapshot, SettingsApplyResult, SettingsValidationError
from f7hub.gui.clipboard_setup import ClipboardSetup
from f7hub.gui.main_window import MainWindow
from f7hub.repositories.settings_repository import (
    SettingsConflictError, SettingsContentionError, SettingsPersistenceError,
)
from Tests.GUI.test_main_window import RecordingTicketService, RecordingScriptService


def snapshot(revision=0, values=None, available=True, diagnostic=None):
    values = values or {}
    return SettingsSnapshot(revision if available else None, tuple(
        EffectiveSetting(d.key, values.get(d.key, d.default), "USER" if d.key in values else "DEFAULT", diagnostic)
        for d in CLIPBOARD_SETTING_DEFINITIONS), available)


class RecordingSettingsService:
    def __init__(self):
        self.snapshot = snapshot()
        self.calls = []
        self.reads = 0
        self.gate = None
        self.error = None
        self.notifications = 0
        self.thread_ids = []

    def refresh(self):
        self.reads += 1
        self._wait()
        return self.snapshot

    def _wait(self):
        self.thread_ids.append(threading.get_ident())
        if self.gate is not None and not self.gate.wait(3):
            raise RuntimeError("Synthetic bounded test timeout")

    def apply(self, changes, *, expected_revision):
        self.calls.append((dict(changes), expected_revision))
        self._wait()
        if self.error:
            raise self.error
        values = {e.key: e.value for e in self.snapshot.values}
        values.update(changes)
        self.snapshot = snapshot(expected_revision + 1, values)
        return SettingsApplyResult(self.snapshot, tuple(changes), self.notifications)


def wait_idle(application, predicate):
    deadline = time.monotonic() + 5
    while predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("Owned async work did not finish within five seconds")
        QTest.qWait(5)
        time.sleep(0.001)
    application.processEvents()


class ClipboardSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingSettingsService()
        self.editor = ClipboardSetup(self.service)
        self.editor.show()
        self.application.processEvents()
        self.editor.reload()
        self.wait()

    def wait(self):
        wait_idle(self.application, lambda: self.editor.pending)

    def tearDown(self):
        if self.service.gate:
            self.service.gate.set()
        self.wait()
        self.editor.cancel()
        self.editor.close()
        self.editor.deleteLater()
        self.application.processEvents()

    def edit(self, key=WORKFLOW_ENABLED, value=True):
        self.editor.checkboxes[key].setChecked(value)

    def test_authoritative_defaults_and_async_read(self):
        self.assertEqual(self.editor.loaded_revision, 0)
        self.assertFalse(self.editor.dirty)
        self.assertTrue(all(not c.isChecked() for c in self.editor.checkboxes.values()))
        self.assertNotIn(threading.get_ident(), self.service.thread_ids)
        self.service.snapshot = snapshot(4, {SOURCE_TITLE_ENABLED: True})
        self.editor.reload()
        self.wait()
        self.assertTrue(self.editor.checkboxes[SOURCE_TITLE_ENABLED].isChecked())
        self.assertEqual(self.editor.loaded_revision, 4)

    def test_independent_optional_preferences_with_master_off(self):
        self.edit(SOURCE_PROCESS_ENABLED)
        self.edit(SOURCE_TITLE_ENABLED)
        self.editor.apply()
        self.wait()
        self.assertEqual(self.service.calls, [({SOURCE_PROCESS_ENABLED: True, SOURCE_TITLE_ENABLED: True}, 0)])
        self.assertFalse(self.editor.checkboxes[WORKFLOW_ENABLED].isChecked())
        self.assertTrue(all(c.isEnabled() for c in self.editor.checkboxes.values()))

    def test_grouped_apply_uses_original_revision_and_cancel_keeps_commit(self):
        for key in self.editor.checkboxes:
            self.edit(key)
        self.assertIn("Unsaved changes", self.editor.draft_message.text())
        self.editor.apply()
        self.wait()
        self.assertEqual(len(self.service.calls), 1)
        self.assertEqual(len(self.service.calls[0][0]), 3)
        self.assertEqual(self.editor.loaded_revision, 1)
        self.edit(value=False)
        self.editor.cancel()
        self.assertTrue(self.editor.checkboxes[WORKFLOW_ENABLED].isChecked())
        self.assertFalse(self.editor.dirty)
        self.assertIn("saved", self.editor.status_message.text())
        self.assertEqual(len(self.service.calls), 1)

    def test_cancel_draft_and_noop_apply_have_no_service_write(self):
        self.edit()
        self.editor.cancel()
        self.editor.apply()
        self.assertEqual(self.service.calls, [])
        self.assertEqual(self.editor.loaded_revision, 0)

    def test_optin_runtime_wording_and_sensitive_description(self):
        descriptions = " ".join(c.accessibleDescription() for c in self.editor.checkboxes.values())
        for text in ("explicit setup opt-in", "eligible durable manual captures", "TEMPORARY", "does not delete", "basename", "sensitive", "independent"):
            self.assertIn(text, descriptions)
        self.assertIn("not implemented or active", self.editor.runtime_message.text())
        self.assertIn("unavailable", self.editor.runtime_message.text())

    def test_unavailable_snapshot_is_safe_disabled_with_reload(self):
        self.service.snapshot = snapshot(available=False)
        self.editor.reload()
        self.wait()
        self.assertFalse(self.editor.apply_button.isEnabled())
        self.assertTrue(all(not c.isEnabled() and not c.isChecked() for c in self.editor.checkboxes.values()))
        self.assertTrue(self.editor.reload_button.isEnabled())
        self.assertFalse(self.editor.apply())
        self.service.snapshot = snapshot(3, {SOURCE_TITLE_ENABLED: True})
        self.editor.reload()
        self.wait()
        self.assertTrue(self.editor.apply_button.isEnabled())
        self.assertTrue(self.editor.checkboxes[SOURCE_TITLE_ENABLED].isChecked())

    def test_invalid_sensitive_value_is_effective_disabled_and_explained(self):
        self.service.snapshot = snapshot(diagnostic="INVALID_STORED_VALUE")
        self.editor.reload()
        self.wait()
        self.assertIn("Invalid stored", self.editor.status_message.text())
        self.assertTrue(all(not c.isChecked() for c in self.editor.checkboxes.values()))

    def test_conflict_preserves_complete_draft_and_requires_explicit_reload(self):
        for key in self.editor.checkboxes:
            self.edit(key)
        draft = dict(self.editor._draft)
        self.service.error = SettingsConflictError("private database text")
        self.editor.apply()
        self.wait()
        self.assertEqual(self.editor._draft, draft)
        self.assertFalse(self.editor.apply())
        self.assertEqual(self.service.reads, 1)
        self.assertIn("changed elsewhere", self.editor.status_message.text())
        self.assertNotIn("private", self.editor.status_message.text())
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
            self.assertFalse(self.editor.reload())
            prompt.assert_called_once()
        self.assertEqual(self.editor._draft, draft)
        self.service.snapshot = snapshot(8, {SOURCE_PROCESS_ENABLED: True})
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.editor.reload())
        self.wait()
        self.assertEqual(self.editor.loaded_revision, 8)
        self.assertFalse(self.editor.dirty)
        self.assertEqual(len(self.service.calls), 1)
        self.assertIn("Review before Apply", self.editor.status_message.text())

    def test_classified_precommit_failures_preserve_draft_and_safe_feedback(self):
        for error, text in (
            (SettingsValidationError("raw secret"), "validated"),
            (SettingsContentionError("raw sqlite"), "busy"),
            (SettingsPersistenceError("raw path"), "unavailable"),
            (RuntimeError("raw title"), "could not be completed"),
        ):
            with self.subTest(error=type(error)):
                self.editor.cancel()
                self.service.error = None
                self.editor.reload()
                self.wait()
                self.edit()
                self.service.error = error
                self.editor.apply()
                self.wait()
                self.assertTrue(self.editor.dirty)
                self.assertEqual(self.editor.loaded_revision, 0)
                self.assertIn(text, self.editor.status_message.text())
                self.assertNotIn("raw", self.editor.status_message.text())

    def test_local_validation_reuses_definitions_without_write(self):
        self.editor._draft[WORKFLOW_ENABLED] = "not a Boolean"
        self.assertFalse(self.editor.apply())
        self.assertEqual(self.service.calls, [])
        self.assertIn("validated", self.editor.status_message.text())

    def test_observer_failure_is_acknowledged_as_saved(self):
        self.service.notifications = 1
        self.edit()
        self.editor.apply()
        self.wait()
        self.assertIn("Preferences saved", self.editor.status_message.text())
        self.assertIn("observer", self.editor.status_message.text())
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.loaded_revision, 1)

    def test_presentation_failure_after_commit_retains_saved_baseline(self):
        self.edit()
        with patch.object(self.editor, "_present_values", side_effect=RuntimeError("private title")):
            self.editor.apply()
            self.wait()
        self.assertIn("Preferences saved", self.editor.status_message.text())
        self.assertIn("display", self.editor.status_message.text())
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.loaded_revision, 1)
        self.assertFalse(self.editor.apply())
        self.editor.reload()
        self.wait()
        self.assertTrue(self.editor.checkboxes[WORKFLOW_ENABLED].isChecked())
        self.assertEqual(len(self.service.calls), 1)

    def test_load_presentation_failure_finishes_and_allows_reload(self):
        with patch.object(self.editor, "_present_values", side_effect=RuntimeError("private value")):
            self.editor.reload()
            self.wait()
        self.assertFalse(self.editor.pending)
        self.assertFalse(self.editor.apply_button.isEnabled())
        self.assertIn("could not be displayed", self.editor.status_message.text())
        self.editor.reload()
        self.wait()
        self.assertTrue(self.editor.apply_button.isEnabled())

    def test_duplicate_operations_and_callback_gap_are_refused(self):
        self.edit()
        self.service.gate = threading.Event()
        observations = []
        self.editor.runner.busy_changed.connect(
            lambda busy: observations.append((self.editor.pending, self.editor.apply(), self.editor.reload())) if not busy else None)
        self.assertTrue(self.editor.apply())
        self.assertFalse(self.editor.apply())
        self.assertFalse(self.editor.reload())
        self.assertFalse(self.editor.cancel())
        self.assertFalse(self.editor.end_session())
        self.assertFalse(self.editor.close())
        self.service.gate.set()
        self.wait()
        self.assertEqual(observations, [(True, False, False)])
        self.assertEqual(len(self.service.calls), 1)
        self.assertNotIn(threading.get_ident(), self.service.thread_ids)

    def test_reopen_and_close_protect_drafts(self):
        self.edit()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.editor.reload())
            self.assertFalse(self.editor.close())
        self.assertTrue(self.editor.dirty)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.editor.close())
        self.assertEqual(self.service.calls, [])

    def test_keyboard_names_tab_order_and_space(self):
        controls = list(self.editor.checkboxes.values())
        controls[0].setFocus()
        self.application.processEvents()
        self.assertTrue(controls[0].hasFocus())
        QTest.keyClick(controls[0], Qt.Key.Key_Space)
        self.assertTrue(self.editor.dirty)
        QTest.keyClick(controls[0], Qt.Key.Key_Tab)
        self.assertTrue(controls[1].hasFocus())
        for control in (*controls, self.editor.apply_button, self.editor.cancel_button, self.editor.reload_button):
            self.assertTrue(control.accessibleName())
            self.assertNotEqual(control.focusPolicy(), Qt.FocusPolicy.NoFocus)


class ClipboardSetupShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = RecordingSettingsService()
        self.window = MainWindow(RecordingTicketService(), script_service=RecordingScriptService(), settings_service=self.service)
        self.window.show()
        self.application.processEvents()
        wait_idle(self.application, lambda: self.window.runner.busy)
        self.window.show_clipboard()
        self.workspace = self.window.clipboard_workspace
        self.workspace.show_setup()
        self.editor = self.workspace.setup
        self.wait()

    def wait(self):
        wait_idle(self.application, lambda: self.window.runner.busy or self.editor.pending)

    def tearDown(self):
        if self.service.gate:
            self.service.gate.set()
        self.wait()
        self.editor.cancel()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def test_retained_editor_and_new_session_authoritative_load(self):
        self.workspace.show_recent()
        self.service.snapshot = snapshot(9, {SOURCE_TITLE_ENABLED: True})
        self.workspace.show_setup()
        self.wait()
        self.assertIs(self.editor, self.workspace.setup)
        self.assertEqual(self.workspace.findChildren(ClipboardSetup), [self.editor])
        self.assertEqual(self.editor.loaded_revision, 9)

    def test_setup_activation_focus_preserves_dirty_edit_and_pending_selector(self):
        field = self.editor.checkboxes[WORKFLOW_ENABLED]
        self.assertIs(self.workspace.activation_focus_target(), field)
        field.setChecked(True)
        field.setFocus()
        self.assertTrue(self.window.show_clipboard())
        self.assertTrue(field.hasFocus())
        self.assertTrue(self.editor.dirty)
        self.service.gate = threading.Event()
        self.assertTrue(self.editor.apply())
        self.assertTrue(self.editor.pending)
        self.window.navigation_buttons["clipboard"].setFocus()
        self.assertIs(self.workspace.activation_focus_target(), self.workspace.setup_button)
        self.assertTrue(self.window.show_clipboard())
        self.assertTrue(self.window.navigation_buttons["clipboard"].hasFocus())
        self.service.gate.set()
        self.wait()
        self.assertTrue(self.window.navigation_buttons["clipboard"].hasFocus())

    def test_all_shell_and_section_navigation_protect_dirty_draft(self):
        self.editor.checkboxes[WORKFLOW_ENABLED].setChecked(True)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel) as prompt:
            for action in (self.workspace.show_recent, self.workspace.show_setup,
                           self.window.show_tickets, self.window.show_scripts,
                           self.window.show_new_ticket, self.window.close, self.workspace.close):
                action()
                self.assertIs(self.window.pages.currentWidget(), self.workspace)
                self.assertIs(self.workspace.sections.currentWidget(), self.editor)
                self.assertTrue(self.editor.dirty)
            self.assertEqual(prompt.call_count, 7)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            QTest.mouseClick(self.window.navigation_buttons["tickets"], Qt.MouseButton.LeftButton)
        self.wait()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.service.calls, [])

    def test_loading_and_saving_refuse_navigation_close_and_reopen(self):
        for operation in ("load", "save"):
            with self.subTest(operation=operation):
                self.service.gate = threading.Event()
                if operation == "load":
                    self.editor.reload()
                else:
                    self.editor.checkboxes[WORKFLOW_ENABLED].setChecked(True)
                    self.editor.apply()
                self.window.show_tickets()
                self.window.show_new_ticket()
                self.window.show_scripts()
                self.assertFalse(self.workspace.show_recent())
                self.assertFalse(self.workspace.show_setup())
                self.assertFalse(self.window.close())
                self.assertFalse(self.workspace.close())
                self.assertIs(self.window.pages.currentWidget(), self.workspace)
                self.service.gate.set()
                self.wait()
                self.assertIs(self.workspace.sections.currentWidget(), self.editor)
        self.window.show_tickets()
        self.wait()
        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertEqual(len(self.service.calls), 1)


if __name__ == "__main__":
    unittest.main()
