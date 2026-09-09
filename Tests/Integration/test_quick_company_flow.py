"""Quick company creation through real application workers and SQLite."""

import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from f7hub.app.bootstrap import bootstrap_application
from f7hub.infrastructure.database import bootstrap_database, database_connection
from Tests.Database.test_category_references import seed_categories
from Tests.Database.test_ticket_references import seed_references


class QuickCompanyFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "quick-company.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.company, *_ = seed_references(self.path)
        seed_categories(self.path)
        self.context = bootstrap_application(database_path=self.path)
        self.window = self.context.main_window
        self.form = self.window.ticket_create_widget
        self.window.resize(1000, 700)
        self.window.show()
        self.wait_idle()
        self.form.company_input.setCurrentIndex(self.form.company_input.findData(self.company.company_id))
        self.wait_idle()
        self.form.contact_input.setCurrentIndex(1)
        self.form.ticket_number_input.setText("SYNTHETIC-008")
        self.form.subject_input.setText("Synthetic network incident")
        self.form.description_input.setPlainText("Synthetic description for company creation")
        self.form.ticket_type_input.setCurrentIndex(1)
        self.form.priority_input.setCurrentIndex(2)
        self.form.category_input.setCurrentIndex(self.form.category_input.findData(31))
        self.original_draft = self.draft()

    def wait_idle(self):
        self.app.processEvents()
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy)

    def tearDown(self):
        self.wait_idle()
        if self.form._company_dialog is not None:
            self.form._company_dialog.reject()
        self.form.reset_form()
        self.window.workspace._clear_drafts()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def draft(self):
        return (self.form.ticket_number_input.text(), self.form.subject_input.text(),
                self.form.description_input.toPlainText(), self.form.ticket_type_input.currentData(),
                self.form.priority_input.currentData(), self.form.category_input.currentData())

    def open_dialog(self):
        QTest.mouseClick(self.form.add_company_button, Qt.MouseButton.LeftButton)
        self.app.processEvents()
        dialog = self.form._company_dialog
        self.assertTrue(dialog.isVisible())
        return dialog

    def company_count(self):
        with database_connection(self.path) as connection:
            return connection.execute("SELECT count(*) FROM companies").fetchone()[0]

    def test_create_company_save_ticket_and_reopen(self):
        dialog = self.open_dialog()
        QTest.keyClicks(dialog.name_input, "Fabrikam Demo Systems")
        QTest.mouseClick(dialog.create_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        self.assertIsNone(self.form._company_dialog)
        company_id = self.form.company_input.currentData()
        self.assertEqual(self.form.company_input.currentText(), "Fabrikam Demo Systems")
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.contact_input.count(), 1)
        self.app.processEvents()
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        QTest.mouseClick(self.form.save_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        workspace = self.window.workspace
        ticket_id = workspace.details.ticket.ticket_id
        self.assertIs(self.window.pages.currentWidget(), workspace)
        with database_connection(self.path) as connection:
            row = connection.execute("SELECT name, is_active FROM companies WHERE company_id = ?", (company_id,)).fetchone()
            self.assertEqual(tuple(row), ("Fabrikam Demo Systems", 1))
            row = connection.execute("SELECT company_id, contact_id, category_id FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
            self.assertEqual(tuple(row), (company_id, None, 31))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)
        self.window.show_new_ticket()
        self.window.show_tickets()
        self.wait_idle()
        workspace.table.setCurrentIndex(workspace.model.index(0, 0))
        QTest.keyClick(workspace.table, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertIn("Company: Fabrikam Demo Systems", workspace.summary.toPlainText())

    def test_cancel_changes_neither_database_nor_draft(self):
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        dialog = self.open_dialog()
        QTest.keyClicks(dialog.name_input, "Contoso Test Support")
        QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.company_input.currentData(), self.company.company_id)
        self.assertIsNotNone(self.form.contact_input.currentData())

    def test_worker_responsive_double_submit_and_busy_close_protection(self):
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        gate = threading.Event()
        gui_thread = threading.get_ident()
        worker_threads = []
        heartbeats = []
        original = self.form._company_service.create_company
        before = self.company_count()

        def delayed(**values):
            worker_threads.append(threading.get_ident())
            gate.wait(3)
            return original(**values)

        with patch.object(self.form._company_service, "create_company", side_effect=delayed) as create:
            try:
                dialog.create_button.click()
                self.assertTrue(self.window.runner.busy)
                self.assertFalse(dialog.create_button.isEnabled())
                self.assertFalse(dialog.cancel_button.isEnabled())
                self.assertFalse(self.window.new_ticket_action.isEnabled())
                dialog.submit()
                QTest.keyClick(dialog.name_input, Qt.Key.Key_Return)
                QTest.keyClick(dialog, Qt.Key.Key_Escape)
                dialog.reject()
                dialog.close()
                self.window.close()
                self.assertTrue(dialog.isVisible())
                self.assertTrue(self.window.isVisible())
                QTimer.singleShot(0, lambda: heartbeats.append(True))
                QTest.qWait(30)
                self.assertEqual(heartbeats, [True])
                self.assertNotEqual(worker_threads, [gui_thread])
            finally:
                gate.set()
                self.wait_idle()
            create.assert_called_once()
        self.assertEqual(len(worker_threads), 1)
        self.assertEqual(self.company_count(), before + 1)
        self.assertEqual(self.draft(), self.original_draft)
        self.assertTrue(self.form.save_button.isEnabled())

    def test_postcommit_refresh_failure_recovers_existing_company_once(self):
        before = self.company_count()
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        with patch.object(self.form._reference_service, "list_active_companies", side_effect=sqlite3.OperationalError("private")):
            dialog.create_button.click()
            self.wait_idle()
            self.assertIsNone(self.form._company_dialog)
            self.assertIn("Company created successfully", self.form.reference_feedback.text())
            self.assertEqual(self.company_count(), before + 1)
            self.assertEqual(self.draft(), self.original_draft)
            self.app.processEvents()
            self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.assertEqual(self.form.company_input.currentText(), "Fabrikam Demo Systems")
        self.assertEqual(self.company_count(), before + 1)
        ids = [self.form.company_input.itemData(i) for i in range(self.form.company_input.count())]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.draft(), self.original_draft)

    def test_sqlite_write_failure_preserves_dialog_and_can_retry(self):
        before = self.company_count()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER test_write_failure BEFORE INSERT ON companies "
                               "BEGIN SELECT RAISE(ABORT, 'private write failure'); END")
        dialog = self.open_dialog()
        dialog.name_input.setText("Fabrikam Demo Systems")
        dialog.create_button.click()
        self.wait_idle()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.name_input.text(), "Fabrikam Demo Systems")
        self.assertNotIn("private", dialog.feedback.text())
        self.assertEqual(self.company_count(), before)
        self.assertEqual(self.draft(), self.original_draft)
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER test_write_failure")
        dialog.create_button.click()
        self.wait_idle()
        self.assertEqual(self.company_count(), before + 1)
        self.assertEqual(self.form.company_input.currentText(), "Fabrikam Demo Systems")
