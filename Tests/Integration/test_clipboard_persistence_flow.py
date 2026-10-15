"""Dormant bootstrap/Recent compatibility and real Windows process-locking fixtures."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import multiprocessing
import os
import queue
import time
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from f7hub.app.bootstrap import bootstrap_application
from f7hub.domain.clipboard import (
    AdmittedManualText, ClipboardCaptureCommand, ClipboardAdmissionBinding,
    ClipboardPersistenceError, ClipboardPersistenceCode as Code, ReplayDisposition,
)
from f7hub.infrastructure.database import database_connection, validate_database_integrity
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.services.clipboard_service import ClipboardService
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT
from Tests.Unit.test_clipboard_capture_contract import SyntheticAuthority, SyntheticClock


def _hold_writer(path, ready, release):
    with database_connection(path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        ready.set()
        if not release.wait(15):
            raise RuntimeError("Synthetic parent did not release test-owned writer")


def _persist_worker(path, binding, policy, start, result):
    if not start.wait(10):
        raise RuntimeError("Synthetic start gate expired")
    try:
        outcome = ClipboardRepository(path)._persist_admitted(binding, policy, accepted_at="2026-10-15T12:00:00.000Z")
        result.put((outcome.disposition.value, outcome.outcome.historical_item_id))
    except ClipboardPersistenceError as error:
        result.put((error.code.value, None))


class ClipboardPersistenceFlowTests(ClipboardDatabaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        super().setUp()
        self.clock = SyntheticClock()
        self.authority = SyntheticAuthority()
        self.repository = ClipboardRepository(self.database_path)
        self.service = ClipboardService(self.repository, admission=self.authority,
            clock=self.clock.utc, monotonic=self.clock.monotonic)
        self.context = self.service.open_admission_context("synthetic")

    def command(self, text="Synthetic end-to-end note"):
        return ClipboardCaptureCommand(self.service.new_operation(self.context), AdmittedManualText(text))

    def test_default_real_bootstrap_remains_denied_even_after_settings_enable(self):
        from f7hub.domain.clipboard_settings import CLIPBOARD_SETTING_DEFINITIONS
        with (patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False),
              patch.object(QApplication, "clipboard", side_effect=AssertionError("No native Clipboard")) as clipboard,
              patch("subprocess.Popen", side_effect=AssertionError("No runtime launch")) as launch):
            app = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
            self.addCleanup(app.main_window.deleteLater)
            app.settings_service.apply({entry.key: True for entry in CLIPBOARD_SETTING_DEFINITIONS}, expected_revision=0)
            context = app.clipboard_service.open_admission_context("synthetic")
            command = ClipboardCaptureCommand(app.clipboard_service.new_operation(context), AdmittedManualText("Synthetic denied bootstrap"))
            before = self.database_path.read_bytes()
            with self.assertRaises(ClipboardPersistenceError) as caught:
                app.clipboard_service.capture_manual_text(context, command)
            self.assertEqual(caught.exception.code, Code.ADMISSION_UNAVAILABLE)
            self.assertEqual(self.database_path.read_bytes(), before)
            with database_connection(self.database_path) as connection:
                for table in ("clipboard_items", "clipboard_capture_events", "clipboard_operation_receipts"):
                    self.assertEqual(connection.execute("SELECT count(*) FROM " + table).fetchone()[0], 0)
                self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            clipboard.assert_not_called()
            launch.assert_not_called()

    def test_admitted_flow_recent_retry_and_restart_reconciliation(self):
        command = self.command("Synthetic first line\r\nsecond line")
        first = self.service.capture_manual_text(self.context, command)
        self.clock.advance(1)
        second = self.service.capture_manual_text(self.context, self.command(command.source.text))
        self.assertEqual(self.service.capture_manual_text(self.context, command).outcome, first.outcome)
        recent = self.service.get_recent()
        self.assertEqual(len(recent.rows), 1)
        self.assertEqual(recent.rows[0].preview, "Synthetic first line  second line")
        self.assertEqual(recent.rows[0].revision, 2)
        self.assertEqual(recent.rows[0].item_ref, first.live_item_ref)
        restarted = ClipboardService(ClipboardRepository(self.database_path), clock=self.clock.utc)
        before = self.database_path.read_bytes()
        self.assertEqual(restarted.lookup_receipt(command.operation).outcome, first.outcome)
        self.assertEqual(self.database_path.read_bytes(), before)
        self.assertEqual(second.outcome.captured_total, 2)
        with database_connection(self.database_path) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_service_two_workers_retry_one_issued_operation(self):
        command = self.command()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.service.capture_manual_text, self.context, command) for _ in range(2)]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual({r.disposition for r in results}, {ReplayDisposition.NEW_CAPTURE, ReplayDisposition.SAME_OPERATION})
        self.assertEqual(results[0].outcome, results[1].outcome)

    def _finish_owned_process(self, process):
        process.join(10)
        if process.is_alive():
            # Exact test-owned Process handle only, never user-owned processes.
            process.terminate()
            process.join(5)
            self.fail("Synthetic test-owned process exceeded its bound")
        self.assertEqual(process.exitcode, 0)

    def test_windows_native_separate_process_lock_serializes_prepared_write(self):
        if os.name != "nt":
            self.skipTest("WINDOWS_NATIVE process locking requires Windows")
        command = self.command()
        context = multiprocessing.get_context("spawn")
        ready, release = context.Event(), context.Event()
        process = context.Process(target=_hold_writer, args=(self.database_path, ready, release))
        process.start()
        try:
            self.assertTrue(ready.wait(10), "Synthetic child writer never became ready")
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.service.capture_manual_text, self.context, command)
                # Prove another connection cannot acquire the held writer, then release.
                with database_connection(self.database_path, busy_timeout_ms=0) as probe:
                    import sqlite3
                    with self.assertRaises(sqlite3.OperationalError):
                        probe.execute("BEGIN IMMEDIATE")
                release.set()
                result = future.result(timeout=10)
                self.assertEqual(result.disposition, ReplayDisposition.NEW_CAPTURE)
        finally:
            release.set()
            self._finish_owned_process(process)

    def test_windows_native_process_race_same_operation_and_conflicting_payloads(self):
        if os.name != "nt":
            self.skipTest("WINDOWS_NATIVE process locking requires Windows")
        for conflicting in (False, True):
            command = self.command("Synthetic native process " + str(conflicting))
            other = replace(command, source=AdmittedManualText("Synthetic native conflicting source")) if conflicting else command
            bindings = [ClipboardAdmissionBinding(c, self.repository.database_scope) for c in (command, other)]
            context = multiprocessing.get_context("spawn")
            start, results = context.Event(), context.Queue()
            processes = [context.Process(target=_persist_worker, args=(self.database_path, binding, self.authority.policy, start, results)) for binding in bindings]
            for process in processes:
                process.start()
            start.set()
            try:
                observations = [results.get(timeout=10) for _ in processes]
            finally:
                for process in processes:
                    self._finish_owned_process(process)
                results.close()
                results.join_thread()
            dispositions = {r[0] for r in observations}
            self.assertEqual(dispositions, {"NEW_CAPTURE", "OPERATION_CONFLICT" if conflicting else "SAME_OPERATION"})
        with database_connection(self.database_path) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM clipboard_capture_events").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT count(*) FROM clipboard_operation_receipts").fetchone()[0], 2)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
