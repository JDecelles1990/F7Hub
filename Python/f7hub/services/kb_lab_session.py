"""Fixed-fixture temporary session owner, with no operational dependency injection."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
import stat
import tempfile

from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories.category_repository import CategoryRepository
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.repositories.tag_repository import TagRepository
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_service import TicketService
from f7hub.services.kb_preview_service import (
    KBPreviewService, NOTICE, PROFILE, load_fixed_package,
)


class LabCleanupError(RuntimeError):
    """Fixed feedback plus the retained owner; raw exceptions are not feedback."""

    def __init__(self, owner, message):
        super().__init__(message)
        self.owner = owner


class LabSetupError(RuntimeError):
    """Preparation failed; the owner records whether cleanup also failed."""

    def __init__(self, owner):
        self.owner = owner
        super().__init__(
            "Synthetic lab setup failed; owned temporary storage remains. No broader cleanup attempted."
            if owner.cleanup_failed else
            "Synthetic lab setup failed; owned temporary storage was removed."
        )


class SyntheticLabSession:
    """One-shot owner. Asset root only; all storage and services are created here.

    Callers reserve the owner before prepare(). Exceptions retain that same owner.
    This is capability separation for trusted code, not an OS security sandbox.
    """

    def __init__(self, project_root: Path):
        self._project_root = Path(project_root)
        self._attempted = False
        self._service = None
        self._snapshots = ()
        self._allocated_root = None
        self._absolute_root = None
        self._temp_parent = None
        self._directory_identity = None
        self._terminal = False
        self._cleanup_complete = False
        self.setup_failed = False
        self.cleanup_failed = False

    @property
    def service(self):
        if self._service is None:
            raise RuntimeError("Synthetic lab is not prepared.")
        return self._service

    @property
    def snapshots(self):
        return self._snapshots

    @property
    def allocated_root(self):
        """Exact allocation retained for diagnostics, including failed preparation."""
        return self._allocated_root

    @property
    def database_path(self):
        """Disposable diagnostic target only; never passed to the editor."""
        return None if self._absolute_root is None else self._absolute_root / "synthetic-lab.sqlite3"

    @property
    def terminal(self):
        return self._terminal

    @property
    def cleanup_complete(self):
        return self._cleanup_complete

    def prepare(self):
        if self._attempted or self._terminal:
            raise RuntimeError("Synthetic lab preparation is one-shot.")
        self._attempted = True
        # Admission must precede the first allocation.
        package = load_fixed_package(self._project_root)
        self._temp_parent = Path(tempfile.gettempdir()).resolve()
        self._allocated_root = Path(tempfile.mkdtemp(prefix="f7hub-kb-sg02-"))
        try:
            self._absolute_root = self._allocated_root.resolve()
            info = self._allocated_root.lstat()
            self._directory_identity = (info.st_dev, info.st_ino)
            self._verify_ownership()
            database = self.database_path
            bootstrap_database(database, self._project_root / "Database" / "Migrations")
            tickets = TicketService(TicketRepository(database))
            knowledge = KnowledgeService(KnowledgeRepository(database), CategoryRepository(database), TagRepository(database))
            reference = knowledge.create_article(
                article_code="KB-SG02-LAB-REFERENCE", title="Synthetic lab reference, not technical guidance",
                summary="Temporary fixture only.",
                body=NOTICE + "\nManually review source qualifications. No causal or publication authority is granted.",
            )
            service = self._service = KBPreviewService(package)
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
            self._snapshots = tuple(snapshots)
            return self
        except Exception:
            self.setup_failed = True
            try:
                self.close()
            except LabCleanupError:
                pass  # Residue and cleanup failure stay on this exact owner.
            raise LabSetupError(self) from None

    def _verify_ownership(self):
        root = self._allocated_root
        try:
            info = root.lstat()
            valid = (
                self._absolute_root is not None
                and root.is_absolute()
                and root.resolve() == self._absolute_root
                and self._absolute_root.parent == self._temp_parent
                and root.name.startswith("f7hub-kb-sg02-")
                and stat.S_ISDIR(info.st_mode)
                and not (getattr(info, "st_file_attributes", 0)
                         & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
                and not root.is_symlink()
                and (info.st_dev, info.st_ino) == self._directory_identity
            )
        except (OSError, ValueError):
            valid = False
        if not valid:
            raise LabCleanupError(self, "Lab cleanup refused: temporary ownership changed.")

    def invalidate(self):
        """Commit terminal invalidation once, also when context exit follows dialog."""
        if self._terminal:
            return
        self._terminal = True
        if self._service is not None:
            self._service.invalidate()

    def close(self):
        """One explicit attempt; successful cleanup is idempotent, failures retain identity."""
        self.invalidate()
        if self._cleanup_complete:
            return
        if self._allocated_root is None:
            self._cleanup_complete = True
            return
        try:
            self._verify_ownership()
            shutil.rmtree(self._absolute_root)
        except LabCleanupError:
            self.cleanup_failed = True
            raise
        except OSError:
            self.cleanup_failed = True
            raise LabCleanupError(
                self, "Lab cleanup failed; owned temporary storage remains. No broader cleanup attempted."
            ) from None
        self.cleanup_failed = False
        self._cleanup_complete = True


@contextmanager
def open_lab(project_root: Path):
    owner = SyntheticLabSession(project_root)
    owner.prepare()  # prepare owns failure cleanup; never retry it in finally.
    try:
        yield owner
    finally:
        owner.close()
