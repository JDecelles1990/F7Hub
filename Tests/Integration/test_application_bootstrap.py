from __future__ import annotations

from io import StringIO
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.app.main import main
from f7hub.infrastructure.database import database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationDiscoveryError


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ApplicationBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
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

        with database_connection(self.database_path) as connection:
            applied_versions = tuple(
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                )
            )
        self.assertEqual(applied_versions, (1, 2, 3, 4, 5, 6))

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
                6,
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
        with (
            patch("f7hub.app.logging_config.RotatingFileHandler", side_effect=OSError(secret)),
            patch("sys.stderr", new_callable=StringIO) as stderr,
            patch.object(QApplication, "exec", return_value=0) as event_loop,
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
