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
from f7hub.services.powershell_service import SYSTEM_SNAPSHOT_CODE


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
    return ScriptCatalogEntry(SimpleNamespace(name="Windows System Snapshot", script_code=code,
        category_name=None, description="local", script_type="DIAGNOSTIC", runtime="POWERSHELL_7",
        risk_level="LOW", privilege_level="STANDARD_USER", relative_path="PowerShell/Diagnostics/Get-SystemSnapshot.ps1"), "AVAILABLE")


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
        self.powershell = SimpleNamespace(execute_diagnostic=lambda code: self.executions.append(code) or result())
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
        self.widget._loaded((entry("diagnostic.windows.network_snapshot"),), None)
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
