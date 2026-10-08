from __future__ import annotations

from io import StringIO
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from f7hub.app.bootstrap import bootstrap_application
from f7hub.app.main import main
from f7hub.infrastructure.database import database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationDiscoveryError
from f7hub.services.altf7hub_service import AltF7HubService
from f7hub.infrastructure.altf7hub_gateway import WindowsAltF7HubGateway


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ApplicationBootstrapTests(unittest.TestCase):
    def test_bootstrap_composes_guide_for_the_resolved_checkout(self):
        context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
        self.addCleanup(context.main_window.deleteLater)
        service = context.main_window.altf7hub_service
        self.assertIsInstance(service, AltF7HubService)
        self.assertIsInstance(service.gateway, WindowsAltF7HubGateway)
        self.assertEqual(service.gateway.project_root, PROJECT_ROOT.resolve())
        self.assertTrue(context.main_window.altf7hub_action.isEnabled())

    def test_clipboard_shell_reuses_real_bootstrap_without_data_or_external_effects(self):
        with patch("f7hub.services.mochi_service.MochiService.automatic_start", return_value=False):
            context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
            window = context.main_window
            self.addCleanup(window.deleteLater)
            try:
                window.show()
                self.wait_window_idle(window)
                self.assertIs(window.pages.currentWidget(), window.workspace)
                self.assertIsNone(window.clipboard_workspace)
                original_count = window.pages.count()
                original_bytes = self.database_path.read_bytes()
                with database_connection(self.database_path) as connection:
                    original_schema = tuple(connection.execute(
                        "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
                    ))
                    original_migrations = tuple(connection.execute(
                        "SELECT * FROM schema_migrations ORDER BY version"
                    ))
                with (
                    patch.object(window.runner, "submit", side_effect=AssertionError("No Clipboard service task")) as submit,
                    patch.object(QApplication, "clipboard", side_effect=AssertionError("No OS clipboard access")) as clipboard_access,
                    patch("subprocess.Popen", side_effect=AssertionError("No external process")) as launch,
                    patch.object(context.mochi_service.gateway, "start", side_effect=AssertionError("No companion IPC")) as ipc,
                    patch.object(window.altf7hub_service, "show_guide", side_effect=AssertionError("No guide launch")) as guide,
                ):
                    window.clipboard_action.trigger()
                    clipboard = window.clipboard_workspace
                    self.assertIsNotNone(clipboard)
                    self.assertIs(window.pages.currentWidget(), clipboard)
                    self.assertTrue(window.show_clipboard())
                    self.assertEqual(window.pages.count(), original_count + 1)
                    submit.assert_not_called()
                    clipboard_access.assert_not_called()
                    launch.assert_not_called()
                    ipc.assert_not_called()
                    guide.assert_not_called()
                self.assertEqual(self.database_path.read_bytes(), original_bytes)
                with database_connection(self.database_path) as connection:
                    self.assertEqual(tuple(connection.execute(
                        "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
                    )), original_schema)
                    self.assertEqual(tuple(connection.execute(
                        "SELECT * FROM schema_migrations ORDER BY version"
                    )), original_migrations)
                    self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

                for action, destination in (
                    (window.tickets_action, window.workspace),
                    (window.knowledge_action, window.knowledge_workspace),
                    (window.scripts_action, window.script_workspace),
                ):
                    with self.subTest(destination=action.text()):
                        action.trigger()
                        self.wait_window_idle(window)
                        self.assertIs(window.pages.currentWidget(), destination)
                        window.clipboard_action.trigger()
                        self.assertIs(window.pages.currentWidget(), clipboard)
                        self.assertIs(window.clipboard_workspace, clipboard)
                        self.assertEqual(window.pages.count(), original_count + 1)
            finally:
                self.wait_window_idle(window)
                self.assertTrue(window.close())

    def wait_window_idle(self, window):
        self.application.processEvents()
        deadline = time.monotonic() + 5
        while (window.runner.busy or window.workspace.note_pending
               or window.workspace.creation_pending or window.workspace.status_pending
               or window.workspace.classification_pending
               or (window.knowledge_workspace is not None and window.knowledge_workspace.filter_loading)):
            if time.monotonic() >= deadline:
                self.fail("Application work did not settle within five seconds")
            QTest.qWait(5)

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.mochi_launch = patch('f7hub.infrastructure.mochi_gateway.MochiGateway.launch', return_value=False)
        self.mochi_launch.start()
        self.addCleanup(self.mochi_launch.stop)
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"LOCALAPPDATA": self.temporary_directory.name})
        self.environment.start()
        self.database_path = (
            Path(self.temporary_directory.name) / "application-bootstrap.db"
        )

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary_directory.cleanup()

    def log_text(self) -> str:
        return (Path(self.temporary_directory.name) / "F7Hub" / "Logs" /
                "Application" / "f7hub.log").read_text(encoding="utf-8")

    def test_bootstrap_composes_window_service_repository_and_database(self) -> None:
        context = bootstrap_application(
            project_root=PROJECT_ROOT,
            database_path=self.database_path,
        )
        self.addCleanup(context.main_window.deleteLater)

        self.assertEqual(context.database_path, self.database_path.resolve())
        self.assertEqual(context.bootstrap_result.integrity_results, ("ok",))
        self.assertIs(
            context.main_window.ticket_create_widget._ticket_service,
            context.ticket_service,
        )
        self.assertEqual(context.main_window.backup_service.database_path, self.database_path.resolve())
        self.assertEqual(context.script_repository._database_path, self.database_path.resolve())
        self.assertIs(context.script_service._repository, context.script_repository)
        self.assertEqual(context.script_service._project_root, PROJECT_ROOT.resolve())
        self.assertIs(context.main_window.script_workspace._service, context.script_service)
        scripts = context.script_service.list_scripts()
        self.assertEqual(tuple(entry.metadata.script_code for entry in scripts), (
            "diagnostic.windows.network_snapshot", "diagnostic.windows.services_snapshot",
            "diagnostic.windows.system_snapshot",
        ))
        self.assertTrue(all(entry.file_status == "AVAILABLE" for entry in scripts))

        with database_connection(self.database_path) as connection:
            applied_versions = tuple(
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                )
            )
        self.assertEqual(applied_versions, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

    def test_missing_migrations_stop_before_application_composition(self) -> None:
        missing_project_root = Path(self.temporary_directory.name) / "missing-root"

        with self.assertRaises(MigrationDiscoveryError):
            bootstrap_application(
                project_root=missing_project_root,
                database_path=self.database_path,
            )

        self.assertFalse(self.database_path.exists())

    def test_composed_backup_service_copies_initialized_database_without_migration(self) -> None:
        context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
        self.addCleanup(context.main_window.deleteLater)
        with database_connection(self.database_path) as connection:
            before = tuple(connection.execute("SELECT version FROM schema_migrations ORDER BY version"))
        snapshot_path = context.main_window.backup_service.create_backup()
        self.assertEqual(snapshot_path.parent,
                         Path(self.temporary_directory.name) / "F7Hub" / "Backups")
        with database_connection(snapshot_path) as snapshot:
            self.assertEqual(validate_database_integrity(snapshot), (("ok",), ()))
            self.assertEqual(tuple(snapshot.execute("SELECT version FROM schema_migrations ORDER BY version")), before)
        with database_connection(self.database_path) as connection:
            self.assertEqual(tuple(connection.execute("SELECT version FROM schema_migrations ORDER BY version")), before)

    def test_main_entry_point_bootstraps_and_enters_event_loop(self) -> None:
        with patch.object(QApplication, "exec", return_value=0) as event_loop:
            exit_code = main(
                ["f7hub", "--database", str(self.database_path)]
            )

        self.assertEqual(exit_code, 0)
        event_loop.assert_called_once_with()
        self.assertIn("Application startup completed.", self.log_text())
        with database_connection(self.database_path) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM schema_migrations"
                ).fetchone()[0],
                12,
            )

    def test_main_entry_point_reports_startup_failure(self) -> None:
        secret = "S037_PRIVATE_STARTUP_MARKER"
        with (
            patch(
                "f7hub.app.main.bootstrap_application",
                side_effect=RuntimeError(secret),
            ),
            patch("f7hub.app.main.QMessageBox.critical") as show_error,
            patch("sys.stderr", new_callable=StringIO) as stderr,
        ):
            exit_code = main(
                ["f7hub", "--database", str(self.database_path)]
            )

        self.assertEqual(exit_code, 1)
        log_text = self.log_text()
        self.assertIn("Application startup failed; exception_type=RuntimeError", log_text)
        self.assertNotIn(secret, log_text)
        self.assertNotIn("Traceback", log_text)
        self.assertNotIn(secret, stderr.getvalue())
        show_error.assert_called_once_with(
            None,
            "F7Hub could not start",
            "The application services could not be initialized. "
            "No ticket data was changed.",
        )

    def test_main_entry_point_continues_with_safe_stderr_fallback(self) -> None:
        secret = "S037_PRIVATE_LOG_SETUP_MARKER"
        contexts = []
        def compose(**kwargs):
            context = bootstrap_application(**kwargs)
            contexts.append(context)
            return context
        def finish_event_loop():
            self.application.processEvents()
            for context in contexts:
                window = context.main_window
                deadline = time.monotonic() + 5
                while window.runner.busy and time.monotonic() < deadline:
                    QTest.qWait(5)
                self.assertFalse(window.runner.busy)
                self.assertTrue(window.close())
                window.deleteLater()
            self.application.processEvents()
            return 0
        with (
            patch("f7hub.app.logging_config.RotatingFileHandler", side_effect=OSError(secret)),
            patch("sys.stderr", new_callable=StringIO) as stderr,
            patch("f7hub.app.main.bootstrap_application", side_effect=compose),
            patch.object(QApplication, "exec", side_effect=finish_event_loop) as event_loop,
        ):
            exit_code = main(["f7hub", "--database", str(self.database_path)])

        self.assertEqual(exit_code, 0)
        event_loop.assert_called_once_with()
        self.assertFalse((Path(self.temporary_directory.name) / "F7Hub" / "Logs" /
                          "Application" / "f7hub.log").exists())
        output = stderr.getvalue()
        self.assertIn("application log file unavailable; exception_type=OSError", output)
        self.assertIn("Application startup completed.", output)
        self.assertNotIn(secret, output)
        self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
