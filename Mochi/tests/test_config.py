import json
from pathlib import Path
import tempfile
import unittest

from mochi.core.config import Settings, load_settings


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        self.path = self.root / "config/settings.json"

    def write(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def test_valid_configuration(self):
        self.write({"app": {"name": "Fixture", "enabled": False},
                    "pet": {"always_on_top": False, "opacity": 0.5},
                    "animation": {"idle_row": 3, "frame_interval_ms": 200, "frame_directory": "frames"}})
        settings = load_settings(self.root)
        self.assertEqual(settings, Settings("Fixture", False, False, 0.5, "frames", 3, 200))

    def test_missing_configuration_uses_defaults_without_writing(self):
        with self.assertLogs("mochi.config", level="WARNING"):
            self.assertEqual(load_settings(self.root), Settings())
        self.assertFalse(self.path.exists())

    def test_malformed_configuration_preserved(self):
        original = b'{"app": '
        self.path.write_bytes(original)
        with self.assertLogs("mochi.config", level="WARNING"):
            self.assertEqual(load_settings(self.root), Settings())
        self.assertEqual(self.path.read_bytes(), original)

    def test_non_object_invalid_encoding_and_oversized_configuration(self):
        for content in (b'[]', b'null', b'\xff', b' ' * 65537):
            with self.subTest(content=content[:10]):
                self.path.write_bytes(content)
                with self.assertLogs("mochi.config", level="WARNING"):
                    self.assertEqual(load_settings(self.root), Settings())

    def test_invalid_types_and_bounds_use_defaults(self):
        self.write({"app": {"name": " ", "enabled": "false"},
                    "pet": {"always_on_top": 1, "opacity": True},
                    "animation": {"idle_row": True, "frame_interval_ms": -1}})
        with self.assertLogs("mochi.config", level="WARNING"):
            self.assertEqual(load_settings(self.root), Settings())

    def test_opacity_bounds_and_nonfinite_values(self):
        for opacity in (0, 1.1, float('nan'), float('inf'), 10 ** 400, "0.5"):
            with self.subTest(opacity=opacity):
                self.write({"pet": {"opacity": opacity}})
                with self.assertLogs("mochi.config", level="WARNING"):
                    self.assertEqual(load_settings(self.root).opacity, 1.0)

    def test_invalid_sections(self):
        self.write({"app": [], "pet": None, "animation": "invalid"})
        with self.assertLogs("mochi.config", level="WARNING"):
            self.assertEqual(load_settings(self.root), Settings())

    def test_directory_escape_absolute_and_empty_rejected(self):
        for directory in ("../outside", str(self.root.parent), "", "\x00"):
            with self.subTest(directory=directory):
                self.write({"animation": {"frame_directory": directory}})
                with self.assertLogs("mochi.config", level="WARNING"):
                    self.assertEqual(load_settings(self.root).frame_directory, Settings().frame_directory)

    def test_unknown_settings_preserved_and_sensitive_capabilities_not_enabled(self):
        self.write({"custom": {"keep": 123}, "pet": {"click_through": True},
                    "privacy": {"screen_capture": True, "clipboard_access": True, "ocr": True},
                    "f7hub": {"integration_enabled": True, "read_only": False}})
        original = self.path.read_bytes()
        with self.assertLogs("mochi.config", level="WARNING") as captured:
            self.assertEqual(load_settings(self.root), Settings())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(sum("remains disabled" in message for message in captured.output), 5)

    def test_empty_object_and_bom(self):
        self.path.write_bytes(b'\xef\xbb\xbf{}')
        self.assertEqual(load_settings(self.root), Settings())
