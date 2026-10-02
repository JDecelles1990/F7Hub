"""Compose only Mochi runtime dependencies; startup loads before the event loop."""

import logging
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from .core.config import load_settings
from .core.logging import close_logging, configure_logging
from .pet.animation_loader import AnimationLoadError, load_animation
from .services.pet_runtime import PetRuntime
from .ui.pet_window import PetWindow

logger = logging.getLogger("mochi.app")


def main(root: Path | None = None) -> int:
    root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
    handler = configure_logging(root)
    window = None
    try:
        logger.info("Mochi startup")
        settings = load_settings(root)
        if not settings.enabled:
            logger.info("Application disabled by configuration")
            return 0
        loaded = load_animation(root / settings.frame_directory, settings.idle_row, settings.frame_interval_ms)
        app = QApplication.instance() or QApplication(sys.argv[:1])
        app.setApplicationName("Mochi")
        app.setQuitOnLastWindowClosed(False)
        window = PetWindow(settings, loaded, PetRuntime(loaded.animation))
        screen = app.primaryScreen()
        if screen is None:
            raise RuntimeError("No screen available")
        available = screen.availableGeometry()
        window.move(available.x() + max(0, available.width() - window.width() - 24),
                    available.y() + max(0, available.height() - window.height() - 24))
        app.aboutToQuit.connect(window.shutdown)
        window.start()
        window.show()
        logger.info("Pet window shown; state=IDLE")
        return app.exec()
    except AnimationLoadError as error:
        logger.error("Animation loading failed; %s", error)
        print(f"Mochi: {error} Check animation settings and PNG assets.", file=sys.stderr)
        return 1
    except Exception as error:
        logger.error("Mochi runtime failed; exception_type=%s", type(error).__name__)
        print(f"Mochi could not start; exception_type={type(error).__name__}. Check the Mochi log.", file=sys.stderr)
        return 1
    finally:
        if window is not None:
            window.shutdown()
            window.hide()
        logger.info("Mochi shutdown")
        close_logging(handler)
