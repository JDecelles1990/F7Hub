import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mochi.app import main
from mochi.core.logging import close_logging, configure_logging


class LoggingAndApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_bounded_file_logging_and_cleanup(self):
        root_handlers = tuple(logging.getLogger().handlers)
        handler = configure_logging(self.root)
        self.assertIsInstance(handler, RotatingFileHandler)
        self.assertEqual(handler.maxBytes, 1024 * 1024)
        self.assertEqual(handler.backupCount, 2)
        logging.getLogger("mochi.test").info("Fixture event")
        close_logging(handler)
        self.assertIn("Fixture event", (self.root / "logs/mochi.log").read_text(encoding="utf-8"))
        self.assertIsNone(handler.stream)
        self.assertNotIn(handler, logging.getLogger("mochi").handlers)
        self.assertEqual(root_handlers, tuple(logging.getLogger().handlers))

    def test_file_logging_falls_back_to_stderr(self):
        with patch("mochi.core.logging.RotatingFileHandler", side_effect=OSError("fixture")):
            handler = configure_logging(self.root)
        try:
            self.assertIsInstance(handler, logging.StreamHandler)
            self.assertNotIsInstance(handler, RotatingFileHandler)
        finally:
            close_logging(handler)

    def test_disabled_application_exits_without_loading_animation_or_creating_gui(self):
        (self.root / "config").mkdir()
        (self.root / "config/settings.json").write_text(json.dumps({"app": {"enabled": False}}), encoding="utf-8")
        with patch("mochi.app.load_animation") as loader, patch("mochi.app.QApplication") as application:
            self.assertEqual(main(self.root), 0)
        loader.assert_not_called()
        application.assert_not_called()
        self.assertIn("Mochi shutdown", (self.root / "logs/mochi.log").read_text(encoding="utf-8"))

    def test_missing_animation_returns_nonzero_and_closes_log(self):
        self.assertEqual(main(self.root), 1)
        messages = (self.root / "logs/mochi.log").read_text(encoding="utf-8")
        self.assertIn("Animation loading failed", messages)
        self.assertIn("Mochi shutdown", messages)
        self.assertFalse(logging.getLogger("mochi").handlers)

    def test_unexpected_startup_error_has_safe_diagnostic_and_cleanup(self):
        with patch("mochi.app.load_settings", side_effect=RuntimeError("secret fixture value")), \
             patch("mochi.app.sys.stderr") as stderr:
            self.assertEqual(main(self.root), 1)
        diagnostic = " ".join(str(call) for call in stderr.write.call_args_list)
        self.assertNotIn("secret fixture value", diagnostic)
        messages = (self.root / "logs/mochi.log").read_text(encoding="utf-8")
        self.assertNotIn("secret fixture value", messages)
        self.assertIn("Mochi shutdown", messages)
