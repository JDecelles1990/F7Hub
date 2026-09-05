from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from f7hub.app.bootstrap import bootstrap_application
from f7hub.app.main import main
from f7hub.infrastructure.database import database_connection
from f7hub.infrastructure.migrations import MigrationDiscoveryError


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ApplicationBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temporary_directory.name) / "application-bootstrap.db"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

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

        with database_connection(self.database_path) as connection:
            applied_versions = tuple(
                row[0]
                for row in connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                )
            )
        self.assertEqual(applied_versions, (1, 2, 3, 4, 5))

    def test_missing_migrations_stop_before_application_composition(self) -> None:
        missing_project_root = Path(self.temporary_directory.name) / "missing-root"

        with self.assertRaises(MigrationDiscoveryError):
            bootstrap_application(
                project_root=missing_project_root,
                database_path=self.database_path,
            )

        self.assertFalse(self.database_path.exists())

    def test_main_entry_point_bootstraps_and_enters_event_loop(self) -> None:
        with patch.object(QApplication, "exec", return_value=0) as event_loop:
            exit_code = main(
                ["f7hub", "--database", str(self.database_path)]
            )

        self.assertEqual(exit_code, 0)
        event_loop.assert_called_once_with()
        with database_connection(self.database_path) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM schema_migrations"
                ).fetchone()[0],
                5,
            )

    def test_main_entry_point_reports_startup_failure(self) -> None:
        with (
            patch(
                "f7hub.app.main.bootstrap_application",
                side_effect=RuntimeError("internal startup detail"),
            ),
            patch("f7hub.app.main.QMessageBox.critical") as show_error,
            self.assertLogs("f7hub.app.main", level="ERROR"),
        ):
            exit_code = main(
                ["f7hub", "--database", str(self.database_path)]
            )

        self.assertEqual(exit_code, 1)
        show_error.assert_called_once_with(
            None,
            "F7Hub could not start",
            "The application services could not be initialized. "
            "No ticket data was changed.",
        )


if __name__ == "__main__":
    unittest.main()
