"""Own the small, process-local application logging setup for F7Hub."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import time


_LOGGER = logging.getLogger("f7hub")
_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_APPLICATION_HANDLER: logging.Handler | None = None
_ORIGINAL_STATE: tuple[int, bool] | None = None


def configure_application_logging() -> logging.Handler:
    """Install one F7Hub-owned handler without changing the process root logger."""

    global _APPLICATION_HANDLER, _ORIGINAL_STATE

    if _ORIGINAL_STATE is None:
        _ORIGINAL_STATE = (_LOGGER.level, _LOGGER.propagate)
    if _APPLICATION_HANDLER is not None:
        _LOGGER.removeHandler(_APPLICATION_HANDLER)
        _APPLICATION_HANDLER.close()

    try:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise ValueError("LOCALAPPDATA is unavailable")
        log_path = Path(local_app_data).expanduser().resolve(strict=False) / "F7Hub" / "Logs" / "Application" / "f7hub.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = RotatingFileHandler(
            log_path, maxBytes=1024 * 1024, backupCount=2, encoding="utf-8"
        )
    except Exception as error:
        print(
            f"F7Hub application log file unavailable; exception_type={type(error).__name__}",
            file=sys.stderr,
        )
        handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(_FORMAT, datefmt="%Y-%m-%dT%H:%M:%SZ")
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)
    _LOGGER.propagate = False
    _APPLICATION_HANDLER = handler
    return handler


def close_application_logging(handler: logging.Handler) -> None:
    """Close only the currently active handler installed by this module."""

    global _APPLICATION_HANDLER, _ORIGINAL_STATE

    if handler is not _APPLICATION_HANDLER:
        return
    _LOGGER.removeHandler(handler)
    handler.close()
    _APPLICATION_HANDLER = None
    if _ORIGINAL_STATE is not None:
        level, propagate = _ORIGINAL_STATE
        if _LOGGER.level == logging.INFO:
            _LOGGER.setLevel(level)
        if _LOGGER.propagate is False:
            _LOGGER.propagate = propagate
        _ORIGINAL_STATE = None
