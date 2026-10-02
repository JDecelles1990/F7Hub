"""Own one bounded Mochi handler; never configure F7Hub or the root logger."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import time


def configure_logging(root: Path) -> logging.Handler:
    logger = logging.getLogger("mochi")
    try:
        directory = root / "logs"
        directory.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(directory / "mochi.log", maxBytes=1024 * 1024,
                                      backupCount=2, encoding="utf-8")
    except OSError as error:
        print(f"Mochi file logging unavailable; exception_type={type(error).__name__}", file=sys.stderr)
        handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", "%Y-%m-%dT%H:%M:%SZ")
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    return handler


def close_logging(handler: logging.Handler) -> None:
    logging.getLogger("mochi").removeHandler(handler)
    handler.flush()
    handler.close()
