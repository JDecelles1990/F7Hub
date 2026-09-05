"""Thin command-line entry point for the F7Hub desktop application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from f7hub.app.bootstrap import bootstrap_application


LOGGER = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> int:
    """Start F7Hub and return its process exit code."""

    process_arguments = list(sys.argv if argv is None else argv)
    parser = argparse.ArgumentParser(description="Start the F7Hub desktop application.")
    parser.add_argument(
        "--database",
        type=Path,
        help="Use an explicit SQLite database path instead of Database/Dev.",
    )
    arguments, qt_arguments = parser.parse_known_args(process_arguments[1:])

    application = QApplication.instance() or QApplication(
        [process_arguments[0], *qt_arguments]
    )
    application.setApplicationName("F7Hub")
    application.setOrganizationName("F7Hub")

    try:
        context = bootstrap_application(database_path=arguments.database)
    except Exception:
        LOGGER.exception("F7Hub application startup failed.")
        QMessageBox.critical(
            None,
            "F7Hub could not start",
            "The application services could not be initialized. "
            "No ticket data was changed.",
        )
        return 1

    context.main_window.show()
    return application.exec()
