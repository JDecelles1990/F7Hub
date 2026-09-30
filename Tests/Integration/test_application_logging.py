"""Application-owned logging configuration, content and lifecycle checks."""

from __future__ import annotations

from io import StringIO
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from f7hub.app import logging_config


class ApplicationLoggingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"LOCALAPPDATA": self.temporary_directory.name})
        self.environment.start()
        self.logger = logging.getLogger("f7hub")
        self.root = logging.getLogger()
        self.root_state = (self.root.level, self.root.propagate, tuple(self.root.handlers))
        self.logger_state = (self.logger.level, self.logger.propagate)
        self.log_path = (Path(self.temporary_directory.name) / "F7Hub" /
                         "Logs" / "Application" / "f7hub.log")

    def tearDown(self) -> None:
        if logging_config._APPLICATION_HANDLER is not None:
            logging_config.close_application_logging(logging_config._APPLICATION_HANDLER)
        self.environment.stop()
        self.temporary_directory.cleanup()

    def test_configures_bounded_utf8_application_log_without_root_propagation(self) -> None:
        root_stream = StringIO()
        external_root_handler = logging.StreamHandler(root_stream)
        self.root.addHandler(external_root_handler)
        try:
            handler = logging_config.configure_application_logging()
            self.assertIsInstance(handler, RotatingFileHandler)
            self.assertEqual(handler.maxBytes, 1024 * 1024)
            self.assertEqual(handler.backupCount, 2)
            self.assertEqual(handler.encoding, "utf-8")
            self.assertEqual(handler.baseFilename, str(self.log_path))
            self.assertEqual(self.logger.level, logging.INFO)
            self.assertFalse(self.logger.propagate)
            self.assertEqual(self.logger.handlers.count(handler), 1)
            self.assertEqual(tuple(self.root.handlers), self.root_state[2] + (external_root_handler,))

            logging.getLogger("f7hub.app.main").info("Safe startup record.")
            text = self.log_path.read_text(encoding="utf-8")
            self.assertIn("INFO f7hub.app.main Safe startup record.", text)
            self.assertEqual(text.count("Safe startup record."), 1)
            self.assertNotIn("Safe startup record.", root_stream.getvalue())
            logging_config.close_application_logging(handler)
            self.assertNotIn(handler, self.logger.handlers)
            self.assertIsNone(handler.stream)
            self.assertEqual((self.logger.level, self.logger.propagate), self.logger_state)
        finally:
            self.root.removeHandler(external_root_handler)
            external_root_handler.close()
        self.assertEqual((self.root.level, self.root.propagate, tuple(self.root.handlers)), self.root_state)

    def test_reconfiguration_replaces_only_owned_handler_and_does_not_duplicate(self) -> None:
        external = logging.NullHandler()
        self.logger.addHandler(external)
        try:
            first = logging_config.configure_application_logging()
            logging.getLogger("f7hub.app.main").info("First record.")
            second = logging_config.configure_application_logging()
            self.assertIsNone(first.stream)
            self.assertNotIn(first, self.logger.handlers)
            self.assertIn(external, self.logger.handlers)
            self.assertEqual(self.logger.handlers.count(second), 1)
            logging.getLogger("f7hub.app.main").info("Second record.")
            text = self.log_path.read_text(encoding="utf-8")
            self.assertEqual(text.count("First record."), 1)
            self.assertEqual(text.count("Second record."), 1)
            logging_config.close_application_logging(first)
            self.assertIn(second, self.logger.handlers)
            logging_config.close_application_logging(second)
            self.assertIn(external, self.logger.handlers)
            self.assertIsNone(second.stream)
            self.assertEqual((self.logger.level, self.logger.propagate), self.logger_state)
        finally:
            self.logger.removeHandler(external)
            external.close()

    def test_file_setup_failure_uses_safe_stderr_fallback(self) -> None:
        secret = "S037_PRIVATE_SETUP_MARKER"
        with (
            patch.object(Path, "mkdir", side_effect=OSError(secret)),
            patch("sys.stderr", new_callable=StringIO) as stderr,
        ):
            handler = logging_config.configure_application_logging()
            self.assertIsInstance(handler, logging.StreamHandler)
            self.assertNotIsInstance(handler, RotatingFileHandler)
            self.assertEqual(self.logger.handlers.count(handler), 1)
            logging.getLogger("f7hub.app.main").info("Application startup completed.")
            output = stderr.getvalue()
            self.assertIn("application log file unavailable; exception_type=OSError", output)
            self.assertIn("Application startup completed.", output)
            self.assertNotIn(secret, output)
            self.assertNotIn("Traceback", output)
            logging_config.close_application_logging(handler)
        self.assertNotIn(handler, self.logger.handlers)

    def test_rotation_retains_only_two_backups(self) -> None:
        handler = logging_config.configure_application_logging()
        self.assertIsInstance(handler, RotatingFileHandler)
        handler.maxBytes = 100
        for index in range(8):
            logging.getLogger("f7hub.app.main").info("Safe rotation record %s", index)
        handler.flush()
        self.assertTrue(self.log_path.exists())
        self.assertTrue(self.log_path.with_name("f7hub.log.1").exists())
        self.assertTrue(self.log_path.with_name("f7hub.log.2").exists())
        self.assertFalse(self.log_path.with_name("f7hub.log.3").exists())
        logging_config.close_application_logging(handler)


if __name__ == "__main__":
    unittest.main()
