"""Read settings without rewriting user configuration or enabling integrations."""

from dataclasses import dataclass
import json
import logging
import math
from pathlib import Path

logger = logging.getLogger("mochi.config")


@dataclass(frozen=True)
class Settings:
    name: str = "Mochi Luna Light"
    enabled: bool = True
    always_on_top: bool = True
    opacity: float = 1.0
    frame_directory: str = "assets/animations/frames"
    idle_row: int = 0
    frame_interval_ms: int = 120
    wave_row: int = 3


def load_settings(root: Path) -> Settings:
    """Return validated values; invalid/missing values use safe defaults."""
    path = root / "config" / "settings.json"
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            text = stream.read(65537)
        if len(text) > 65536:
            raise ValueError("Settings exceed size limit")
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Settings must be an object")
    except (OSError, UnicodeError, ValueError) as error:
        logger.warning("Configuration unavailable; using defaults; exception_type=%s", type(error).__name__)
        return Settings()

    defaults = Settings()

    def value(section, key, default, valid):
        group = data.get(section, {})
        if not isinstance(group, dict):
            logger.warning("Invalid configuration section=%s; using defaults", section)
            return default
        result = group.get(key, default)
        if not valid(result):
            logger.warning("Invalid configuration field=%s.%s; using default", section, key)
            return default
        return result

    def safe_directory(candidate):
        if not isinstance(candidate, str) or not candidate.strip() or "\x00" in candidate:
            return False
        try:
            relative = Path(candidate)
            return not relative.is_absolute() and (root / relative).resolve().is_relative_to(root.resolve())
        except (OSError, ValueError):
            return False

    boolean = lambda candidate: type(candidate) is bool
    for section, key in (("pet", "click_through"), ("privacy", "clipboard_access"),
                         ("privacy", "screen_capture"), ("privacy", "ocr"),
                         ("f7hub", "integration_enabled")):
        requested = value(section, key, False, boolean)
        if requested:
            logger.warning("Unsupported capability remains disabled; field=%s.%s", section, key)

    settings = Settings(
        name=value("app", "name", defaults.name, lambda v: isinstance(v, str) and 0 < len(v.strip()) <= 80),
        enabled=value("app", "enabled", defaults.enabled, boolean),
        always_on_top=value("pet", "always_on_top", defaults.always_on_top, boolean),
        opacity=value("pet", "opacity", defaults.opacity,
                      lambda v: type(v) in (int, float) and 0.1 <= v <= 1.0 and math.isfinite(v)),
        frame_directory=value("animation", "frame_directory", defaults.frame_directory, safe_directory),
        idle_row=value("animation", "idle_row", defaults.idle_row, lambda v: type(v) is int and 0 <= v <= 10),
        wave_row=value("animation", "wave_row", defaults.wave_row, lambda v: type(v) is int and 0 <= v <= 10),
        frame_interval_ms=value("animation", "frame_interval_ms", defaults.frame_interval_ms,
                                lambda v: type(v) is int and 20 <= v <= 2000),
    )
    logger.info("Configuration loaded")
    return settings
