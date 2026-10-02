from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtGui import QColor, QImage

from mochi.pet.animation_loader import AnimationLoadError, discover_frames, load_animation


class AnimationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def frame(self, filename, width=16, height=20):
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor(80, 160, 120, 180))
        self.assertTrue(image.save(str(self.directory / filename)))

    def test_discovery_filters_other_rows_and_non_frames(self):
        for filename in ("r0c0.png", "r0c1.png", "r1c0.png", "preview.png"):
            self.frame(filename)
        (self.directory / "r0c2.png").mkdir()
        self.assertEqual([p.name for p in discover_frames(self.directory, 0)], ["r0c0.png", "r0c1.png"])

    def test_numeric_frame_ordering(self):
        for filename in ("r0c10.png", "r0c2.png", "r0c1.png"):
            self.frame(filename)
        self.assertEqual([p.name for p in discover_frames(self.directory, 0)],
                         ["r0c1.png", "r0c2.png", "r0c10.png"])

    def test_decode_frames_and_metadata(self):
        for index in range(3):
            self.frame(f"r0c{index}.png")
        loaded = load_animation(self.directory, 0, 120)
        self.assertEqual(len(loaded.images), 3)
        self.assertEqual(loaded.animation.interval_ms, 120)
        self.assertTrue(all(image.hasAlphaChannel() for image in loaded.images))

    def test_missing_directory(self):
        with self.assertRaisesRegex(AnimationLoadError, "missing"):
            discover_frames(self.directory / "missing", 0)

    def test_empty_directory(self):
        with self.assertRaisesRegex(AnimationLoadError, "no frames"):
            discover_frames(self.directory, 0)

    def test_missing_idle_row(self):
        self.frame("r1c0.png")
        with self.assertRaisesRegex(AnimationLoadError, "no frames"):
            discover_frames(self.directory, 0)

    def test_corrupt_frame(self):
        (self.directory / "r0c0.png").write_bytes(b"not an image")
        with self.assertRaisesRegex(AnimationLoadError, "unreadable"):
            load_animation(self.directory, 0, 120)

    def test_mismatched_dimensions(self):
        self.frame("r0c0.png")
        self.frame("r0c1.png", width=17)
        with self.assertRaisesRegex(AnimationLoadError, "inconsistent"):
            load_animation(self.directory, 0, 120)

    def test_duplicate_columns(self):
        self.frame("r0c0.png")
        self.frame("r0c00.png")
        with self.assertRaisesRegex(AnimationLoadError, "duplicate"):
            discover_frames(self.directory, 0)

    def test_oversized_image_rejected_before_decode(self):
        self.frame("r0c0.png", width=2049, height=1)
        with self.assertRaisesRegex(AnimationLoadError, "size limit"):
            load_animation(self.directory, 0, 120)

    def test_unreadable_directory(self):
        with patch.object(Path, "iterdir", side_effect=PermissionError("fixture")):
            with self.assertRaisesRegex(AnimationLoadError, "cannot be read"):
                discover_frames(self.directory, 0)

    def test_decode_failure_after_valid_header(self):
        self.frame("r0c0.png")
        with patch("mochi.pet.animation_loader.QImageReader") as reader_type:
            reader_type.return_value.size.return_value = QImage(16, 20, QImage.Format.Format_ARGB32).size()
            reader_type.return_value.read.return_value = QImage()
            with self.assertRaisesRegex(AnimationLoadError, "cannot be decoded"):
                load_animation(self.directory, 0, 120)
