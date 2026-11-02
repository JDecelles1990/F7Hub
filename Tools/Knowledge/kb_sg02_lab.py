"""Launch only the fixed synthetic lab using its shared session owner."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "Python") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "Python"))

from f7hub.services.kb_lab_session import (
    LabCleanupError, LabSetupError, open_lab as _open_lab,
)
from f7hub.services.kb_preview_service import PreviewAdmissionError


def open_lab():
    """Fixed standalone assets; no arbitrary CLI or database override."""
    return _open_lab(PROJECT_ROOT)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Open the fixed synthetic KB-SG02 preview lab. No article is saved.")
    parser.parse_args(argv)
    from PySide6.QtWidgets import QApplication
    from f7hub.gui.kb_preview_dialog import KBPreviewDialog

    app = QApplication.instance() or QApplication([sys.argv[0]])
    try:
        with open_lab() as session:
            dialog = KBPreviewDialog(session)
            dialog.exec()
            dialog.deleteLater()
            app.processEvents()
    except PreviewAdmissionError:
        print("KB-SG02 synthetic source admission denied. No preview was created.", file=sys.stderr)
        return 1
    except (LabCleanupError, LabSetupError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print("KB-SG02 lab failed. No production operation was requested.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
