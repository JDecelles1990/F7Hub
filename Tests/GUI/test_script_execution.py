"""Run ownership across the runner's idle-before-callback gap."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from types import SimpleNamespace
import unittest
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication

from f7hub.domain.diagnostic_results import DiagnosticResult, ScriptDiagnosticRunResult
from f7hub.gui.script_workspace import ScriptWorkspace
from f7hub.gui.main_window import MainWindow
from f7hub.services.script_service import ScriptCatalogEntry
from f7hub.services.ticket_service import TicketService
from f7hub.services.powershell_service import SYSTEM_SNAPSHOT_CODE, APPROVED_DIAGNOSTICS
from f7hub.domain.diagnostic_results import LOCAL_BASELINE_PACK, DiagnosticPackResult
from dataclasses import replace
from unittest.mock import patch
from f7hub.repositories.script_repository import ScriptRecord


class Runner(QObject):
    busy_changed = Signal(bool)
    def __init__(self):
        super().__init__()
        self.busy = False
        self.accept = True

    def submit(self, work, success, error):
        if self.busy or not self.accept:
            return False
        self.work, self.success, self.error = work, success, error
        self.busy = True
        self.busy_changed.emit(True)
        return True

    def gap(self):
        self.busy = False
        self.busy_changed.emit(False)


def entry(code=SYSTEM_SNAPSHOT_CODE):
    spec = APPROVED_DIAGNOSTICS.get(code, APPROVED_DIAGNOSTICS[SYSTEM_SNAPSHOT_CODE])
    return ScriptCatalogEntry(ScriptRecord(1, None, None, code, "Windows System Snapshot", "local",
        spec.relative_path, "DIAGNOSTIC", "POWERSHELL_7", "LOW", "STANDARD_USER", "1.0.0",
        spec.digest, 60, 1, 1, "created", "updated"), "AVAILABLE")


def result(*, cleanup=True):
    return ScriptDiagnosticRunResult(SYSTEM_SNAPSHOT_CODE, "digest", "COMPLETED", "<b>Collected</b>",
        DiagnosticResult("Get-SystemSnapshot", "PASS", "<b>Collected</b>", {"value":0}, (), ()),
        .1, 0, cleanup)


class ScriptExecutionGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.runner = Runner()
        self.executions = []
        self.scripts = SimpleNamespace(list_scripts=lambda **kw: (entry(),))
        self.powershell = SimpleNamespace(execute_diagnostic=lambda code: self.executions.append(code) or result(),
            pack_readiness=lambda: (True, "Ready"),
            execute_diagnostic_pack=lambda code: self.executions.append(code) or DiagnosticPackResult(code,"COMPLETED","PASS","Collected",(result(),)))
        self.widget = ScriptWorkspace(self.scripts, self.runner, powershell_service=self.powershell)
        self.widget._loaded((entry(),), None)

    def tearDown(self):
        self.widget.deleteLater()
        self.app.processEvents()

    def test_explicit_run_only_and_duplicate_suppression(self):
        self.assertEqual(self.executions, [])
        self.assertTrue(self.widget.run_diagnostic())
        self.assertFalse(self.widget.run_diagnostic())
        self.assertFalse(self.widget.run_button.isEnabled())
        self.assertFalse(self.widget.refresh_list())
        self.assertFalse(self.widget.copy_script())
        self.assertFalse(self.widget.search_scripts())
        self.assertIsNone(self.widget.open_management())
        self.runner.work()
        self.assertEqual(self.executions, [SYSTEM_SNAPSHOT_CODE])

    def test_pending_spans_idle_and_result_presentation_then_allows_next_run(self):
        self.widget.run_diagnostic()
        self.runner.gap()
        self.assertTrue(self.widget.run_pending)
        self.assertFalse(self.widget.run_button.isEnabled())
        self.assertFalse(self.widget.run_diagnostic())
        self.runner.success(result())
        self.assertFalse(self.widget.run_pending)
        self.assertIn("<b>Collected</b>", self.widget.results.toPlainText())
        self.assertIn('"value": 0', self.widget.results.toPlainText())
        self.assertTrue(self.widget.run_diagnostic())

    def test_stale_completion_does_not_release_new_owner(self):
        self.widget.run_diagnostic()
        obsolete = self.runner.success
        self.runner.gap()
        obsolete(result())
        self.widget.run_diagnostic()
        identity = self.widget._run_identity
        obsolete(result())
        self.assertIs(self.widget._run_identity, identity)
        self.assertEqual(self.widget.results.toPlainText(), "")

    def test_dispatch_and_worker_failure_release_ownership(self):
        self.runner.accept = False
        self.assertFalse(self.widget.run_diagnostic())
        self.assertFalse(self.widget.run_pending)
        self.runner.accept = True
        self.widget.run_diagnostic()
        self.runner.gap()
        self.runner.error(RuntimeError("private failure"))
        self.assertFalse(self.widget.run_pending)
        self.assertNotIn("private", self.widget.feedback.text())

    def test_cleanup_failure_blocks_second_run(self):
        self.widget.run_diagnostic()
        self.runner.gap()
        self.runner.success(result(cleanup=False))
        self.assertFalse(self.widget.run_button.isEnabled())
        self.assertFalse(self.widget.run_diagnostic())

    def test_unpermitted_script_has_no_run(self):
        self.widget._loaded((entry("diagnostic.windows.unapproved"),), None)
        self.assertFalse(self.widget.run_button.isEnabled())
        self.assertFalse(self.widget.run_diagnostic())

    def test_main_window_guards_direct_navigation_and_close_in_callback_gap(self):
        window = MainWindow(TicketService(None), script_service=self.scripts, powershell_service=self.powershell)
        try:
            scripts = window.script_workspace
            window.pages.setCurrentWidget(scripts)
            scripts._run_identity = object()
            scripts.run_pending_changed.emit(True)
            window.runner.busy_changed.emit(False)
            self.assertFalse(window.tickets_action.isEnabled())
            self.assertFalse(window.scripts_action.isEnabled())
            for action in (window.show_tickets, window.show_scripts, window.show_knowledge, window.show_new_ticket):
                action()
                self.assertIs(window.pages.currentWidget(), scripts)
            close = QCloseEvent()
            window.closeEvent(close)
            self.assertFalse(close.isAccepted())
            scripts._run_identity = None
            scripts.run_pending_changed.emit(False)
            self.assertTrue(window.tickets_action.isEnabled())
        finally:
            window.deleteLater()

    def test_pack_readiness_is_independent_of_filtered_rows(self):
        self.widget._loaded((), "absent", (True, "Ready"))
        self.assertTrue(self.widget.pack_button.isEnabled())
        self.assertFalse(self.widget.run_button.isEnabled())
        self.assertIn("Shown: 0", self.widget.summary.text())
        self.assertTrue(self.widget.run_pack())
        self.assertFalse(self.widget.run_pack())
        self.assertFalse(self.widget.run_diagnostic())
        self.assertFalse(self.widget.refresh_list())
        self.assertIsNone(self.widget.open_management())
        self.runner.gap()
        self.assertTrue(self.widget.run_pending)
        self.assertFalse(self.widget.pack_button.isEnabled())
        self.assertFalse(self.widget.table.isEnabled())
        self.runner.success(self.runner.work())
        self.assertEqual(self.executions, [LOCAL_BASELINE_PACK.code])
        self.assertFalse(self.widget.run_pending)
        self.assertTrue(self.widget.pack_button.isEnabled())

    def test_aborted_pack_preserves_partial_identity_and_skipped_members(self):
        self.widget._loaded((entry(),), None, (True, "Ready"))
        self.widget.run_pack()
        self.runner.gap()
        partial = DiagnosticPackResult(LOCAL_BASELINE_PACK.code, "ABORTED", None, "Stopped safely",
            (result(),), .2, LOCAL_BASELINE_PACK.diagnostic_codes[1], "TIMEOUT",
            (LOCAL_BASELINE_PACK.diagnostic_codes[2],), True)
        self.runner.success(partial)
        text = self.widget.results.toPlainText()
        for expected in ("SystemSnapshot", "TIMEOUT", "Not available (pack aborted)",
                         LOCAL_BASELINE_PACK.diagnostic_codes[2], "<b>Collected</b>"):
            self.assertIn(expected, text)
        self.widget._loaded((entry(LOCAL_BASELINE_PACK.diagnostic_codes[1]),), None, (True, "Ready"))
        self.assertEqual(self.widget.results.toPlainText(), text)
        self.assertIs(self.widget._last_result, partial)

    def test_presentation_failure_releases_owner_and_preserves_quarantine(self):
        self.widget._loaded((entry(),), None, (True, "Ready"))
        self.widget.run_pack()
        self.runner.gap()
        failed = DiagnosticPackResult(LOCAL_BASELINE_PACK.code, "ABORTED", None, "Cleanup unverified",
            (result(cleanup=False),), .1, SYSTEM_SNAPSHOT_CODE, "CLEANUP_FAILED",
            LOCAL_BASELINE_PACK.diagnostic_codes[1:], False)
        with patch.object(self.widget, "_present_result", side_effect=RuntimeError("private")):
            self.runner.success(failed)
        self.assertFalse(self.widget.run_pending)
        self.assertIs(self.widget._last_result, failed)
        self.assertNotIn("private", self.widget.feedback.text())
        for query in (None, "filtered"):
            self.widget._loaded((entry(),), query, (True, "Ready"))
            self.assertFalse(self.widget.run_pack())
            self.assertFalse(self.widget.run_diagnostic())
        self.assertTrue(self.widget._execution_blocked)

    def test_file_availability_and_policy_are_distinct(self):
        missing = replace(entry(), file_status="MISSING")
        wrong_type = replace(entry(), metadata=replace(entry().metadata, script_type="UTILITY"))
        self.widget._loaded((missing, wrong_type), None, (False, "System missing"))
        self.assertEqual(self.widget.model.item(0, 4).text(), "Approved")
        self.assertEqual(self.widget.model.item(1, 3).text(), "AVAILABLE")
        self.assertEqual(self.widget.model.item(1, 4).text(), "Not approved")
        self.assertFalse(self.widget.run_diagnostic())
        self.widget.table.selectRow(1)
        self.widget.table.setCurrentIndex(self.widget.model.index(1, 0))
        self.assertFalse(self.widget.run_diagnostic())
        self.assertIn("Version: 1.0.0", self.widget.details.toPlainText())
        self.assertFalse(self.widget.pack_button.isEnabled())
