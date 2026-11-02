"""Launch only the fixed KB-SG02 synthetic lab; no production bootstrap."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
import tempfile

# Repository tool only. No production path/configuration resolution.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "Python") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "Python"))

from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.tag_repository import TagRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_service import TicketService
from f7hub.services.kb_preview_service import (
    KBPreviewService, NOTICE, PROFILE, PreviewAdmissionError, load_fixed_package,
)


class LabCleanupError(RuntimeError):
    """Owned temporary storage could not be removed; no broader cleanup attempted."""


@dataclass(frozen=True)
class LabSession:
    service: KBPreviewService
    snapshots: tuple
    # For isolated tests and cleanup diagnostics, never passed to the dialog.
    database_path: Path


@contextmanager
def open_lab():
    """Own the only storage target; finish service reads before yielding UI data."""
    package = load_fixed_package(PROJECT_ROOT)
    owned_root = Path(tempfile.mkdtemp(prefix="f7hub-kb-sg02-"))
    absolute_root = owned_root.resolve()
    temp_parent = Path(tempfile.gettempdir()).resolve()
    service = None
    try:
        if absolute_root.parent != temp_parent or owned_root.is_symlink():
            raise LabCleanupError("Lab temporary ownership check failed.")
        database = absolute_root / "synthetic-lab.sqlite3"
        bootstrap_database(database, PROJECT_ROOT / "Database" / "Migrations")
        tickets = TicketService(TicketRepository(database))
        knowledge = KnowledgeService(KnowledgeRepository(database), CategoryRepository(database), TagRepository(database))
        reference = knowledge.create_article(
            article_code="KB-SG02-LAB-REFERENCE", title="Synthetic lab reference, not technical guidance",
            summary="Temporary fixture only.",
            body=NOTICE + "\nManually review source qualifications. No causal or publication authority is granted.",
        )
        service = KBPreviewService(package)
        snapshots = []
        for case in package.cases:
            ticket = tickets.create_ticket(subject=case.title, ticket_number=f"KB-SG02-{case.fixture_id}",
                                            source=PROFILE, created_by="Synthetic lab setup")
            for source in case.sources:
                tickets.add_note(ticket.ticket_id, note_text=source.text, source=PROFILE,
                                 author_label="Synthetic fixture author")
            details = tickets.get_ticket_details(ticket.ticket_id)
            article = knowledge.get_article(reference.knowledge_article_id)
            snapshots.append(service.bind_sources(case, ticket_details=details, reference_article=article))
        yield LabSession(service, tuple(snapshots), database)
    finally:
        if service is not None:
            service.invalidate()
        if (owned_root.is_symlink() or owned_root.resolve() != absolute_root
                or absolute_root.parent != temp_parent):
            raise LabCleanupError("Lab cleanup refused: temporary ownership changed.")
        try:
            shutil.rmtree(absolute_root)
        except OSError:
            raise LabCleanupError("Lab cleanup failed; owned temporary storage remains. No broader cleanup attempted.") from None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Open the fixed synthetic KB-SG02 preview lab. No article is saved.")
    parser.parse_args(argv)
    from PySide6.QtWidgets import QApplication
    from f7hub.gui.kb_preview_dialog import KBPreviewDialog

    app = QApplication.instance() or QApplication([sys.argv[0]])
    try:
        with open_lab() as session:
            dialog = KBPreviewDialog(session.service, session.snapshots)
            dialog.exec()
            dialog.deleteLater()
            app.processEvents()
    except PreviewAdmissionError:
        print("KB-SG02 synthetic source admission denied. No preview was created.", file=sys.stderr)
        return 1
    except LabCleanupError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print("KB-SG02 lab failed. No production operation was requested.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
