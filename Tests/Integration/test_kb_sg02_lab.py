"""Real existing services on disposable storage, never operational SQLite."""

from contextlib import ExitStack, closing
from io import StringIO
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools" / "Knowledge"))
import kb_sg02_lab as lab
from f7hub.services import kb_lab_session as sessions

from PySide6.QtWidgets import QApplication
from f7hub.gui.kb_preview_dialog import KBPreviewDialog
from f7hub.services.kb_preview_service import PreviewAdmissionError, PreviewUnavailableError
from f7hub.services.ticket_service import TicketService
from f7hub.services.knowledge_service import KnowledgeService
from f7hub.services.ticket_knowledge_service import TicketKnowledgeService


class KBPreviewLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def dump(self, path):
        with closing(sqlite3.connect(path)) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchall(), [("ok",)])
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            return tuple(connection.iterdump())

    def test_existing_services_real_reads_only_owned_database_and_preview_zero_io(self):
        original_connect = sqlite3.connect
        original_mkdtemp = sessions.tempfile.mkdtemp
        roots, connections, handles = [], [], []
        def owned_directory(*args, **kwargs):
            result = original_mkdtemp(*args, **kwargs)
            roots.append(Path(result).resolve())
            return result
        def guarded_connect(database, *args, **kwargs):
            target = Path(database).resolve()
            self.assertTrue(roots)
            self.assertEqual(target, roots[0] / "synthetic-lab.sqlite3")
            connections.append(target)
            handle = original_connect(database, *args, **kwargs)
            handles.append(handle)
            return handle
        read_tickets, read_knowledge = TicketService.get_ticket_details, KnowledgeService.get_article
        with patch.object(sessions.tempfile, "mkdtemp", side_effect=owned_directory), \
                patch("sqlite3.connect", side_effect=guarded_connect), \
                patch.object(TicketService, "get_ticket_details", autospec=True, side_effect=read_tickets) as ticket_reads, \
                patch.object(KnowledgeService, "get_article", autospec=True, side_effect=read_knowledge) as knowledge_reads:
            with lab.open_lab() as session:
                database = session.database_path
                self.assertEqual(ticket_reads.call_count, 6)
                self.assertEqual(knowledge_reads.call_count, 6)
                self.assertEqual(len(session.snapshots), 6)
                for handle in handles:
                    with self.assertRaises(sqlite3.ProgrammingError):
                        handle.execute("SELECT 1")
                before = self.dump(database)
                count = len(connections)
                with ExitStack() as stack:
                    stack.enter_context(patch("sqlite3.connect", side_effect=AssertionError("Unexpected preview database access")))
                    for owner, names in ((TicketService, ("create_ticket", "add_note", "change_status")),
                                         (KnowledgeService, ("create_article", "update_article", "publish_article", "archive_article")),
                                         (TicketKnowledgeService, ("link_related_article", "unlink_related_article"))):
                        for name in names:
                            stack.enter_context(patch.object(owner, name, side_effect=AssertionError("Unexpected preview mutation")))
                    stack.enter_context(patch("pathlib.Path.open", side_effect=AssertionError("Unexpected source file I/O")))
                    stack.enter_context(patch("builtins.open", side_effect=AssertionError("Unexpected file I/O")))
                    stack.enter_context(patch("socket.socket", side_effect=AssertionError("Unexpected network I/O")))
                    for owner, names in ((TicketService, ("get_ticket_details",)),
                                         (KnowledgeService, ("get_article",))):
                        for name in names:
                            stack.enter_context(patch.object(owner, name, side_effect=AssertionError("Unexpected service read")))
                    dialog = KBPreviewDialog(session)
                    for index in range(1, 7):
                        with patch.object(dialog.editor, "_confirm_discard", return_value=True):
                            dialog.editor.fixture_selector.setCurrentIndex(index)
                        dialog.editor.body_input.setPlainText("Temporary prose")
                        dialog.editor.annotations_input.setPlainText("Needs human review")
                    with patch.object(dialog.editor, "_confirm_discard", return_value=False):
                        dialog.reject()
                    self.assertEqual(dialog.editor.body_input.toPlainText(), "Temporary prose")
                    with patch.object(dialog.editor, "_confirm_discard", return_value=True):
                        dialog.reject()
                    dialog.deleteLater()
                    self.app.processEvents()
                self.assertEqual(len(connections), count)
                self.assertEqual(self.dump(database), before)
            self.assertFalse(database.parent.exists())
        self.assertTrue(connections)
        with self.assertRaises(PreviewUnavailableError):
            session.service.build_preview(session.snapshots[0])

    def test_seeded_tickets_new_reference_draft_and_no_promoted_links(self):
        with lab.open_lab() as session:
            with closing(sqlite3.connect(session.database_path)) as connection:
                self.assertEqual(connection.execute("SELECT DISTINCT status FROM tickets").fetchall(), [("NEW",)])
                self.assertEqual(connection.execute("SELECT status, published_at FROM knowledge_articles").fetchall(), [("DRAFT", None)])
                self.assertEqual(connection.execute("SELECT count(*) FROM ticket_knowledge_articles").fetchone()[0], 0)
            self.dump(session.database_path)

    def test_new_session_never_restores_prior_preview_edits(self):
        with lab.open_lab() as first:
            old_session_id = first.service.session_id
            old_path = first.database_path
            first_preview = first.service.build_preview(first.snapshots[0])
        with lab.open_lab() as second:
            self.assertNotEqual(old_session_id, second.service.session_id)
            self.assertNotEqual(old_path, second.database_path)
            self.assertEqual(first_preview.body, second.service.build_preview(second.snapshots[0]).body)
        self.assertFalse(old_path.parent.exists())

    def test_admission_failure_creates_no_storage(self):
        with patch.object(sessions, "load_fixed_package", side_effect=PreviewAdmissionError("Denied")), \
                patch.object(sessions.tempfile, "mkdtemp") as create:
            with self.assertRaises(PreviewAdmissionError):
                with lab.open_lab():
                    self.fail("Admission failed")
            create.assert_not_called()

    def test_setup_failure_cleans_only_owned_temporary_directory(self):
        targets = []
        original = sessions.shutil.rmtree
        def remove(path):
            targets.append(Path(path))
            self.assertEqual(Path(path).parent, Path(sessions.tempfile.gettempdir()).resolve())
            self.assertTrue(Path(path).name.startswith("f7hub-kb-sg02-"))
            original(path)
        with patch.object(sessions, "bootstrap_database", side_effect=RuntimeError("PRIVATE_SENTINEL")), \
                patch.object(sessions.shutil, "rmtree", side_effect=remove):
            with self.assertRaises(sessions.LabSetupError):
                with lab.open_lab():
                    self.fail("Setup failed")
        self.assertEqual(len(targets), 1)
        self.assertFalse(targets[0].exists())

    def test_cleanup_failure_reported_once_without_raw_exception(self):
        owned = None
        try:
            with patch.object(sessions.shutil, "rmtree", side_effect=PermissionError("PRIVATE_SENTINEL")) as remove:
                with self.assertRaises(lab.LabCleanupError) as caught:
                    with lab.open_lab() as session:
                        owned = session.database_path.parent
                self.assertEqual(remove.call_count, 1)
                self.assertNotIn("PRIVATE_SENTINEL", str(caught.exception))
                self.assertTrue(owned.exists())
        finally:
            if owned is not None and owned.exists():
                self.assertEqual(owned.resolve().parent, Path(sessions.tempfile.gettempdir()).resolve())
                self.assertTrue(owned.name.startswith("f7hub-kb-sg02-"))
                shutil.rmtree(owned)

    def test_cli_rejects_arbitrary_input_and_database_overrides(self):
        for option in ("--database", "--input", "--root"):
            with self.subTest(option=option), patch("sys.stderr", new_callable=StringIO), \
                    patch.object(lab, "open_lab") as open_session:
                with self.assertRaises(SystemExit) as error:
                    lab.main([option, "unadmitted"])
                self.assertEqual(error.exception.code, 2)
                open_session.assert_not_called()

    def test_main_unexpected_failure_is_nonzero_and_content_free(self):
        with patch.object(lab, "open_lab", side_effect=RuntimeError("PRIVATE_SENTINEL")), \
                patch("sys.stderr", new_callable=StringIO) as output:
            self.assertEqual(lab.main([]), 1)
            self.assertNotIn("PRIVATE_SENTINEL", output.getvalue())


    def test_snapshots_and_fixture_identity_are_immutable(self):
        from dataclasses import FrozenInstanceError, replace
        with lab.open_lab() as owner:
            self.assertIsInstance(owner.snapshots, tuple)
            self.assertEqual([s.fixture.fixture_id for s in owner.snapshots],
                             [f"F{i:02d}" for i in range(1, 7)])
            with self.assertRaises(FrozenInstanceError):
                owner.snapshots[0].fixture.title = "changed"
            with self.assertRaises(FrozenInstanceError):
                owner.snapshots[0].ticket_revision = "changed"
            with self.assertRaises(PreviewUnavailableError):
                owner.service.build_preview(replace(owner.snapshots[0]))

    def test_setup_and_cleanup_double_failure_retains_exact_owner_and_diagnostics(self):
        owner = sessions.SyntheticLabSession(ROOT)
        owned = None
        try:
            with patch.object(sessions, "bootstrap_database", side_effect=RuntimeError("PRIVATE_SETUP")),                     patch.object(sessions.shutil, "rmtree", side_effect=PermissionError("PRIVATE_CLEANUP")) as remove:
                with self.assertRaises(sessions.LabSetupError) as caught:
                    owner.prepare()
                owned = owner.allocated_root
                self.assertIs(caught.exception.owner, owner)
                self.assertTrue(owner.setup_failed)
                self.assertTrue(owner.cleanup_failed)
                self.assertTrue(owner.terminal)
                self.assertFalse(owner.cleanup_complete)
                self.assertTrue(owned.exists())
                self.assertEqual(owner.database_path, owned / "synthetic-lab.sqlite3")
                self.assertNotIn("PRIVATE", str(caught.exception))
                self.assertIn("storage remains", str(caught.exception))
                remove.assert_called_once_with(owned)
            with self.assertRaises(RuntimeError):
                owner.prepare()
            self.assertEqual(owner.allocated_root, owned)
        finally:
            if owned is not None:
                owner.close()  # Explicit recovery after the injected denial is removed.
                self.assertFalse(owned.exists())
                self.assertEqual(owner.allocated_root, owned)

    def test_context_setup_double_failure_does_not_automatically_retry_cleanup(self):
        owner = None
        try:
            with patch.object(sessions, "bootstrap_database", side_effect=RuntimeError("PRIVATE")),                     patch.object(sessions.shutil, "rmtree", side_effect=PermissionError("PRIVATE")) as remove:
                with self.assertRaises(sessions.LabSetupError) as caught:
                    with lab.open_lab():
                        self.fail("must not yield")
                owner = caught.exception.owner
                self.assertEqual(remove.call_count, 1)
                self.assertTrue(owner.cleanup_failed)
                self.assertTrue(owner.allocated_root.exists())
        finally:
            if owner is not None:
                owner.close()

    def test_terminal_dialog_and_context_invalidate_and_cleanup_once(self):
        with patch.object(sessions.shutil, "rmtree", wraps=sessions.shutil.rmtree) as remove:
            with lab.open_lab() as owner:
                with patch.object(owner.service, "invalidate", wraps=owner.service.invalidate) as invalidate:
                    dialog = KBPreviewDialog(owner)
                    dialog.reject()
                    dialog.accept()
                    owner.close()
                    owner.close()
                    self.assertEqual(invalidate.call_count, 1)
                dialog.deleteLater()
                self.app.processEvents()
            self.assertEqual(remove.call_count, 1)
            self.assertTrue(owner.cleanup_complete)
            self.assertIsNotNone(owner.allocated_root)

    def test_changed_directory_identity_refuses_deletion_and_retains_original_target(self):
        owner = sessions.SyntheticLabSession(ROOT).prepare()
        original = owner.allocated_root
        moved = original.with_name(original.name + "-test-moved")
        self.assertFalse(moved.exists())
        try:
            original.rename(moved)
            original.mkdir()
            with patch.object(sessions.shutil, "rmtree") as remove:
                with self.assertRaises(sessions.LabCleanupError) as caught:
                    owner.close()
                remove.assert_not_called()
            self.assertIs(caught.exception.owner, owner)
            self.assertTrue(owner.cleanup_failed)
            self.assertFalse(owner.cleanup_complete)
            self.assertEqual(owner.allocated_root, original)
            self.assertTrue(moved.exists())
            self.assertTrue(original.exists())
        finally:
            # Exact test-owned replacement only; restore original identity before owner cleanup.
            self.assertEqual(original.parent, Path(sessions.tempfile.gettempdir()).resolve())
            self.assertEqual(moved.parent, original.parent)
            original.rmdir()
            moved.rename(original)
            owner.close()

    def test_partial_setup_service_is_invalidated_even_when_cleanup_fails(self):
        created = []
        real_service = sessions.KBPreviewService
        def service(package):
            result = real_service(package)
            created.append(result)
            return result
        owner = sessions.SyntheticLabSession(ROOT)
        try:
            with patch.object(sessions, "KBPreviewService", side_effect=service),                     patch.object(TicketService, "get_ticket_details", side_effect=RuntimeError("PRIVATE")),                     patch.object(sessions.shutil, "rmtree", side_effect=OSError("PRIVATE")):
                with self.assertRaises(sessions.LabSetupError):
                    owner.prepare()
            self.assertEqual(len(created), 1)
            self.assertFalse(created[0]._active)
            self.assertTrue(owner.cleanup_failed)
        finally:
            if owner.allocated_root is not None:
                owner.close()

    def test_constructor_accepts_asset_root_only(self):
        import inspect
        self.assertEqual(list(inspect.signature(sessions.SyntheticLabSession).parameters), ["project_root"])
        for forbidden in ("database_path", "repositories", "credentials", "settings_service", "application_context"):
            with self.assertRaises(TypeError):
                sessions.SyntheticLabSession(ROOT, **{forbidden: object()})

    def test_main_setup_double_failure_is_nonzero_and_fixed_feedback(self):
        owner = None
        try:
            with patch.object(sessions, "bootstrap_database", side_effect=RuntimeError("PRIVATE")),                     patch.object(sessions.shutil, "rmtree", side_effect=OSError("PRIVATE")),                     patch("sys.stderr", new_callable=StringIO) as output:
                real = sessions.SyntheticLabSession
                owners = []
                def reserve(root):
                    value = real(root)
                    owners.append(value)
                    return value
                with patch.object(sessions, "SyntheticLabSession", side_effect=reserve):
                    self.assertEqual(lab.main([]), 1)
                owner = owners[0]
                self.assertNotIn("PRIVATE", output.getvalue())
                self.assertIn("storage remains", output.getvalue())
                self.assertTrue(owner.allocated_root.exists())
        finally:
            if owner is not None:
                owner.close()


    def test_owner_setup_has_no_production_resolver_or_context_capability_use(self):
        from f7hub.infrastructure import database_paths
        from f7hub.app import bootstrap
        from f7hub.services.settings_service import SettingsService
        with ExitStack() as guards:
            for target, name in ((database_paths, "resolve_development_database_path"),
                                 (database_paths, "resolve_runtime_database_path"),
                                 (bootstrap, "resolve_development_database_path"),
                                 (bootstrap, "bootstrap_application"),
                                 (bootstrap, "ApplicationContext"),
                                 (SettingsService, "__init__")):
                guards.enter_context(patch.object(target, name, side_effect=AssertionError("Production capability used")))
            with lab.open_lab() as owner:
                self.assertEqual(len(owner.snapshots), 6)
                self.assertEqual(owner.database_path.parent, owner.allocated_root)
                self.dump(owner.database_path)


if __name__ == "__main__":
    unittest.main()
