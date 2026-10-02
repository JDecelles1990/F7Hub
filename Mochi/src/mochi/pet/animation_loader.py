"""Discover and decode PNGs once; presentation receives ready images."""

from dataclasses import dataclass
import logging
from pathlib import Path
import re

from PySide6.QtGui import QImage, QImageReader

from .animation import Animation

logger = logging.getLogger("mochi.animation")


class AnimationLoadError(ValueError):
    """A safe, actionable loading failure without raw filesystem diagnostics."""


@dataclass(frozen=True)
class LoadedAnimation:
    animation: Animation
    images: tuple[QImage, ...]


def discover_frames(directory: Path, row: int) -> tuple[Path, ...]:
    try:
        if not directory.is_dir():
            raise AnimationLoadError("Animation directory is missing or inaccessible.")
        pattern = re.compile(rf"r{row}c(\d+)\.png", re.IGNORECASE)
        frames = []
        resolved_directory = directory.resolve()
        for path in directory.iterdir():
            match = pattern.fullmatch(path.name)
            if match and path.is_file():
                if not path.resolve().is_relative_to(resolved_directory):
                    raise AnimationLoadError("Animation frame leaves the configured directory.")
                frames.append((int(match.group(1)), path))
        if not frames:
            raise AnimationLoadError("Animation directory has no frames for the selected idle row.")
        if len(frames) > 128 or len({column for column, _ in frames}) != len(frames):
            raise AnimationLoadError("Animation has too many frames or duplicate column numbers.")
        return tuple(path for _, path in sorted(frames))
    except OSError as error:
        raise AnimationLoadError("Animation directory cannot be read.") from error


def load_animation(directory: Path, row: int, interval_ms: int) -> LoadedAnimation:
    paths = discover_frames(directory, row)
    images = []
    dimensions = None
    for path in paths:
        reader = QImageReader(str(path))
        size = reader.size()
        if not size.isValid() or size.width() > 2048 or size.height() > 2048:
            raise AnimationLoadError("Animation frame is unreadable or exceeds the size limit.")
        image = reader.read()
        if image.isNull():
            raise AnimationLoadError("Animation frame cannot be decoded.")
        if dimensions is not None and image.size() != dimensions:
            raise AnimationLoadError("Animation frame dimensions are inconsistent.")
        dimensions = image.size()
        images.append(image)
    logger.info("Animation loaded; row=%d frames=%d interval_ms=%d", row, len(paths), interval_ms)
    return LoadedAnimation(Animation(paths, interval_ms), tuple(images))
