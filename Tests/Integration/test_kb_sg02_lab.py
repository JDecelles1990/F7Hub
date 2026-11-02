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
        original_mkdtemp = lab.tempfile.mkdtemp
        roots, connections = [], []
        def owned_directory(*args, **kwargs):
            result = original_mkdtemp(*args, **kwargs)
            roots.append(Path(result).resolve())
            return result
        def guarded_connect(database, *args, **kwargs):
            target = Path(database).resolve()
            self.assertTrue(roots)
            self.assertEqual(target, roots[0] / "synthetic-lab.sqlite3")
            connections.append(target)
            return original_connect(database, *args, **kwargs)
        read_tickets, read_knowledge = TicketService.get_ticket_details, KnowledgeService.get_article
        with patch.object(lab.tempfile, "mkdtemp", side_effect=owned_directory), \
                patch("sqlite3.connect", side_effect=guarded_connect), \
                patch.object(TicketService, "get_ticket_details", autospec=True, side_effect=read_tickets) as ticket_reads, \
                patch.object(KnowledgeService, "get_article", autospec=True, side_effect=read_knowledge) as knowledge_reads:
            with lab.open_lab() as session:
                database = session.database_path
                self.assertEqual(ticket_reads.call_count, 6)
                self.assertEqual(knowledge_reads.call_count, 6)
                self.assertEqual(len(session.snapshots), 6)
                before = self.dump(database)
                count = len(connections)
                with ExitStack() as stack:
                    stack.enter_context(patch("sqlite3.connect", side_effect=AssertionError("Unexpected preview database access")))
                    for owner, names in ((TicketService, ("create_ticket", "add_note", "change_status")),
                                         (KnowledgeService, ("create_article", "update_article", "publish_article", "archive_article")),
                                         (TicketKnowledgeService, ("link_related_article", "unlink_related_article"))):
                        for name in names:
                            stack.enter_context(patch.object(owner, name, side_effect=AssertionError("Unexpected preview mutation")))
                    dialog = KBPreviewDialog(session.service, session.snapshots)
                    for index in range(1, 7):
                        with patch.object(dialog, "_confirm_discard", return_value=True):
                            dialog.fixture_selector.setCurrentIndex(index)
                        dialog.body_input.setPlainText("Temporary prose")
                        dialog.annotations_input.setPlainText("Needs human review")
                    with patch.object(dialog, "_confirm_discard", return_value=False):
                        dialog.reject()
                    self.assertEqual(dialog.body_input.toPlainText(), "Temporary prose")
                    with patch.object(dialog, "_confirm_discard", return_value=True):
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
        with patch.object(lab, "load_fixed_package", side_effect=PreviewAdmissionError("Denied")), \
                patch.object(lab.tempfile, "mkdtemp") as create:
            with self.assertRaises(PreviewAdmissionError):
                with lab.open_lab():
                    self.fail("Admission failed")
            create.assert_not_called()

    def test_setup_failure_cleans_only_owned_temporary_directory(self):
        targets = []
        original = lab.shutil.rmtree
        def remove(path):
            targets.append(Path(path))
            self.assertEqual(Path(path).parent, Path(lab.tempfile.gettempdir()).resolve())
            self.assertTrue(Path(path).name.startswith("f7hub-kb-sg02-"))
            original(path)
        with patch.object(lab, "bootstrap_database", side_effect=RuntimeError("PRIVATE_SENTINEL")), \
                patch.object(lab.shutil, "rmtree", side_effect=remove):
            with self.assertRaises(RuntimeError):
                with lab.open_lab():
                    self.fail("Setup failed")
        self.assertEqual(len(targets), 1)
        self.assertFalse(targets[0].exists())

    def test_cleanup_failure_reported_once_without_raw_exception(self):
        owned = None
        try:
            with patch.object(lab.shutil, "rmtree", side_effect=PermissionError("PRIVATE_SENTINEL")) as remove:
                with self.assertRaises(lab.LabCleanupError) as caught:
                    with lab.open_lab() as session:
                        owned = session.database_path.parent
                self.assertEqual(remove.call_count, 1)
                self.assertNotIn("PRIVATE_SENTINEL", str(caught.exception))
                self.assertTrue(owned.exists())
        finally:
            if owned is not None and owned.exists():
                self.assertEqual(owned.resolve().parent, Path(lab.tempfile.gettempdir()).resolve())
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


if __name__ == "__main__":
    unittest.main()
