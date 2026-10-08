from datetime import datetime, timezone
import os
import time
import threading
from contextlib import contextmanager
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from f7hub.app.bootstrap import bootstrap_application

from f7hub.infrastructure.database import database_connection, validate_database_integrity
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.services.clipboard_service import ClipboardService, ClipboardQueryError
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, FixtureCapture, PROJECT_ROOT, seed_item


class ClipboardRecentFlowTests(ClipboardDatabaseTestCase):
    def test_migrated_service_repository_flow(self):
        latest = "2026-10-08T11:00:00.000Z"
        with database_connection(self.database_path) as connection:
            repeated = seed_item(connection, raw_text="Synthetic repeated note\nsecond line", captures=(
                FixtureCapture(), FixtureCapture(received_at=latest)))
            seed_item(connection, retention_intent="SAVED", expires_at=None, is_pinned=True)
            seed_item(connection, expires_at="2026-10-08T11:30:00.000Z")
        before = self.database_path.read_bytes()
        service = ClipboardService(ClipboardRepository(self.database_path),
                                   clock=lambda: datetime(2026, 10, 8, 12, tzinfo=timezone.utc))
        page = service.get_recent(limit=1)
        self.assertEqual(page.rows[0].item_ref.clipboard_item_id, repeated)
        self.assertEqual(page.rows[0].last_received_at, latest)
        self.assertEqual(page.rows[0].preview, "Synthetic repeated note second line")
        self.assertTrue(page.has_more)
        all_recent = service.get_recent()
        self.assertEqual(len(all_recent.rows), 2)
        self.assertFalse(all_recent.has_more)
        self.assertEqual(self.database_path.read_bytes(), before)
        with database_connection(self.database_path, read_only=True) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clipboard_capture_events WHERE clipboard_item_id=?", (repeated,)).fetchone()[0], 2)

    def test_absent_owner_database_is_unavailable_without_creation(self):
        path = self.root / "absent" / "history.db"
        service = ClipboardService(ClipboardRepository(path))
        with self.assertRaises(ClipboardQueryError):
            service.get_recent()
        self.assertFalse(path.parent.exists())


class ClipboardRecentGuiFlowTests(ClipboardDatabaseTestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def wait_idle(self, window):
        deadline = time.monotonic() + 5
        while (window.runner.busy or
               (window.clipboard_workspace is not None and window.clipboard_workspace.loading)):
            if time.monotonic() >= deadline:
                self.fail("Synthetic application read did not settle")
            QTest.qWait(5)
            time.sleep(0.001)

    def test_knowledge_navigation_and_hidden_close_guard_during_clipboard_read(self):
        gate = threading.Event()
        with patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False):
            context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
            window = context.main_window
            window.show()
            self.wait_idle(window)
            read = context.clipboard_service.get_recent

            def gated_read():
                if not gate.wait(5):
                    raise RuntimeError("Synthetic gate timed out")
                return read()

            try:
                with patch.object(context.clipboard_service, "get_recent", side_effect=gated_read):
                    window.show_clipboard()
                    clipboard = window.clipboard_workspace
                    self.assertTrue(clipboard.loading)
                    self.assertTrue(window.knowledge_action.isEnabled())
                    window.show_knowledge()
                    deadline = time.monotonic() + 5
                    while (window.runner.busy or window.knowledge_workspace.filter_loading) and time.monotonic() < deadline:
                        QTest.qWait(5)
                        time.sleep(0.001)
                    self.assertFalse(window.runner.busy)
                    self.assertIs(window.pages.currentWidget(), window.knowledge_workspace)
                    self.assertTrue(clipboard.loading)
                    self.assertFalse(window.close())
                    gate.set()
                    self.wait_idle(window)
                    self.assertIs(window.pages.currentWidget(), window.knowledge_workspace)
            finally:
                gate.set()
                self.wait_idle(window)
                window.close()
                window.deleteLater()
                self.application.processEvents()

    def browse(self, expected_count, has_more):
        with patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False):
            context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
            window = context.main_window
            window.show()
            self.wait_idle(window)
            before_bytes = self.database_path.read_bytes()
            with database_connection(self.database_path, read_only=True) as connection:
                before_logical = tuple(connection.iterdump())
            reads, statements = [], []

            @contextmanager
            def observed_connection(path, *, read_only=False):
                reads.append((path, read_only))
                with database_connection(path, read_only=read_only) as connection:
                    connection.set_trace_callback(statements.append)
                    yield connection

            try:
                with (
                    patch("f7hub.repositories.clipboard_repository.database_connection", observed_connection),
                    patch.object(context.clipboard_service, "get_recent", wraps=context.clipboard_service.get_recent) as recent,
                    patch.object(QApplication, "clipboard", side_effect=AssertionError("OS Clipboard forbidden")),
                    patch("subprocess.Popen", side_effect=AssertionError("External processes forbidden")),
                    patch.object(context.mochi_service.gateway, "start", side_effect=AssertionError("IPC forbidden")),
                    patch.object(window.altf7hub_service, "show_guide", side_effect=AssertionError("Provider forbidden")),
                ):
                    self.assertTrue(window.show_clipboard())
                    self.wait_idle(window)
                    clipboard = window.clipboard_workspace
                    self.assertIs(clipboard._service, context.clipboard_service)
                    self.assertTrue(window.show_clipboard())
                    recent.assert_called_once_with()
                    self.assertEqual(clipboard.model.rowCount(), expected_count)
                    self.assertEqual(clipboard.model.columnCount(), 4)
                    self.assertEqual(clipboard.page_message.text(), f"Showing {expected_count} recent items." +
                                     (" More items are available." if has_more else ""))
                    if expected_count:
                        self.assertEqual(clipboard.model.data(clipboard.model.index(0, 1)), "Synthetic 054 😀")
                        self.assertEqual(clipboard.model.data(clipboard.model.index(0, 2)), "Saved")
                        self.assertEqual(clipboard.model.data(clipboard.model.index(0, 3)), "Yes")
                    else:
                        self.assertEqual(clipboard.status_message.text(), "No recent Clipboard history is available.")
                self.assertEqual(reads, [(self.database_path.resolve(), True)])
                queries = [sql for sql in statements if sql.lstrip().upper().startswith("SELECT")]
                self.assertEqual(len(queries), 1)
                self.assertIn("LIMIT 51", queries[0])
                self.assertFalse(any(sql.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "REPLACE"))
                                     for sql in statements))
                self.assertEqual(self.database_path.read_bytes(), before_bytes)
                with database_connection(self.database_path, read_only=True) as connection:
                    self.assertEqual(tuple(connection.iterdump()), before_logical)
                    self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            finally:
                self.wait_idle(window)
                window.close()
                window.deleteLater()
                self.application.processEvents()

    def test_composed_populated_first_page_is_bounded_and_read_only(self):
        with database_connection(self.database_path) as connection:
            for number in range(55):
                seed_item(connection, raw_text=f"Synthetic {number:03d} 😀", retention_intent="SAVED",
                          expires_at=None, is_pinned=number == 54)
        self.browse(50, True)

    def test_composed_empty_page_is_success_and_read_only(self):
        self.browse(0, False)
