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
from f7hub.services.ticket_reference_service import CompanyReferenceUnavailableError, TicketReferenceOption


class QuickContactFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "quick-contact.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.company, *_ = seed_references(self.path)
        with database_connection(self.path) as connection:
            connection.execute("UPDATE companies SET name = ? WHERE company_id = ?", ("Fabrikam Demo Systems", self.company.company_id))
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
        self.form.ticket_number_input.setText("SYNTHETIC-009")
        self.form.subject_input.setText("Synthetic contact issue")
        self.form.description_input.setPlainText("Synthetic Slice 009 verification.")
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
        if self.form._contact_dialog is not None:
            self.form._contact_dialog.reject()
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
        QTest.mouseClick(self.form.add_contact_button, Qt.MouseButton.LeftButton)
        self.app.processEvents()
        dialog = self.form._contact_dialog
        self.assertTrue(dialog.isVisible())
        return dialog

    def contact_count(self):
        with database_connection(self.path) as connection:
            return connection.execute("SELECT count(*) FROM contacts").fetchone()[0]

    def create_contact(self, name="Alice Example"):
        dialog = self.open_dialog()
        QTest.keyClicks(dialog.name_input, name)
        QTest.keyClicks(dialog.email_input, "alice@example.invalid")
        QTest.mouseClick(dialog.create_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        self.assertIsNone(self.form._contact_dialog)
        return self.form.contact_input.currentData()

    def save_and_reopen(self, company_id, contact_id, company_name, contact_name):
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.company_input.currentData(), company_id)
        self.assertEqual(self.form.contact_input.currentData(), contact_id)
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        QTest.mouseClick(self.form.save_button, Qt.MouseButton.LeftButton)
        self.wait_idle()
        workspace = self.window.workspace
        ticket_id = workspace.details.ticket.ticket_id
        with database_connection(self.path) as connection:
            row = connection.execute("SELECT company_id, contact_id, category_id FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
            self.assertEqual(tuple(row), (company_id, contact_id, 31))
            row = connection.execute("SELECT company_id, display_name, is_active, email FROM contacts WHERE contact_id = ?", (contact_id,)).fetchone()
            self.assertEqual(tuple(row), (company_id, contact_name, 1, "alice@example.invalid"))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)
        self.window.show_new_ticket()
        self.window.show_tickets()
        self.wait_idle()
        workspace.table.setCurrentIndex(workspace.model.index(0, 0))
        QTest.keyClick(workspace.table, Qt.Key.Key_Return)
        self.wait_idle()
        self.assertIn("Company: " + company_name, workspace.summary.toPlainText())
        self.assertIn("Contact: " + contact_name, workspace.summary.toPlainText())

    def test_create_contact_save_ticket_and_reopen(self):
        contact_id = self.create_contact()
        self.save_and_reopen(self.company.company_id, contact_id, "Fabrikam Demo Systems", "Alice Example")

    def test_combined_company_contact_save_and_reopen(self):
        self.form.add_company_button.click()
        dialog = self.form._company_dialog
        dialog.name_input.setText("Northwind Field Services")
        dialog.create_button.click()
        self.wait_idle()
        company_id = self.form.company_input.currentData()
        self.assertTrue(self.form.add_contact_button.isEnabled())
        contact_id = self.create_contact("Bob Example")
        self.save_and_reopen(company_id, contact_id, "Northwind Field Services", "Bob Example")

    def test_cancel_changes_neither_database_nor_draft(self):
        with database_connection(self.path) as connection:
            before = tuple(connection.iterdump())
        dialog = self.open_dialog()
        dialog.name_input.setText("Alice Example")
        dialog.cancel_button.click()
        self.wait_idle()
        with database_connection(self.path) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual(self.form.company_input.currentData(), self.company.company_id)

    def test_worker_responsive_double_submit_and_busy_close_protection(self):
        dialog = self.open_dialog()
        dialog.name_input.setText("Alice Example")
        gate = threading.Event()
        gui_thread = threading.get_ident()
        worker_threads = []
        heartbeats = []
        original = self.form._contact_service.create_contact
        before = self.contact_count()
        def delayed(**values):
            worker_threads.append(threading.get_ident())
            gate.wait(3)
            return original(**values)
        with patch.object(self.form._contact_service, "create_contact", side_effect=delayed) as create:
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
            finally:
                gate.set()
                self.wait_idle()
            create.assert_called_once()
        self.assertEqual(len(worker_threads), 1)
        self.assertNotEqual(worker_threads[0], gui_thread)
        self.assertEqual(self.contact_count(), before + 1)
        self.assertEqual(self.draft(), self.original_draft)

    def test_postcommit_failure_recovers_once_and_saves_original_identity(self):
        before = self.contact_count()
        dialog = self.open_dialog()
        dialog.name_input.setText("Alice Example")
        dialog.email_input.setText("alice@example.invalid")
        with patch.object(self.form._reference_service, "list_active_contacts_for_company", side_effect=sqlite3.OperationalError("private")):
            dialog.create_button.click()
            self.wait_idle()
            contact_id = self.form._pending_contact.contact_id
            self.assertEqual(self.contact_count(), before + 1)
            self.assertIn("Contact created successfully", self.form.reference_feedback.text())
            self.assertEqual(self.draft(), self.original_draft)
            self.assertFalse(self.form.company_input.isEnabled())
            self.assertFalse(self.form.abandon_contact_button.isVisible())
            self.form.company_input.setCurrentIndex(0)
            self.assertEqual(self.form.company_input.currentData(), self.company.company_id)
            self.form.submit()
            self.assertEqual(self.context.ticket_service.list_tickets(), ())
            self.form.refresh_references_button.click()
            self.wait_idle()
            self.assertEqual(self.form._pending_contact.contact_id, contact_id)
            self.assertEqual(self.contact_count(), before + 1)
            self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.assertEqual(self.contact_count(), before + 1)
        self.save_and_reopen(self.company.company_id, contact_id, "Fabrikam Demo Systems", "Alice Example")

    def committed_contact_with_unavailable_company(self, *, delete=False):
        before = self.contact_count()
        original = self.form._contact_service.create_contact

        def commit_then_change_company(**values):
            contact = original(**values)
            # A separate connection proves the contact committed before the mutation.
            with database_connection(self.path) as connection:
                self.assertEqual(connection.execute(
                    "SELECT count(*) FROM contacts WHERE contact_id = ?", (contact.contact_id,)
                ).fetchone()[0], 1)
                connection.execute(
                    "DELETE FROM companies WHERE company_id = ?" if delete else
                    "UPDATE companies SET is_active = 0 WHERE company_id = ?",
                    (self.company.company_id,),
                )
            return contact

        with patch.object(self.form._contact_service, "create_contact", side_effect=commit_then_change_company) as create:
            self.create_contact()
            create.assert_called_once()
        pending = self.form._pending_contact
        self.assertIsNotNone(pending)
        for _ in range(2):
            self.assertTrue(self.form.abandon_contact_button.isVisible())
            self.assertTrue(self.form.abandon_contact_button.isEnabled())
            self.assertIn("company is no longer available", self.form.reference_feedback.text())
            self.assertFalse(self.form.company_input.isEnabled())
            self.assertEqual(self.draft(), self.original_draft)
            self.form.submit()
            self.assertEqual(self.context.ticket_service.list_tickets(), ())
            self.form.refresh_references_button.click()
            self.wait_idle()
            self.assertEqual(self.form._pending_contact, pending)
            self.assertEqual(self.contact_count(), before + 1)
        with database_connection(self.path) as connection:
            row = connection.execute("SELECT company_id FROM contacts WHERE contact_id = ?", (pending.contact_id,)).fetchone()
            self.assertEqual(row[0], None if delete else self.company.company_id)
        return pending, before

    def abandon_and_check(self):
        with patch.object(self.form._reference_service, "list_active_ticket_categories", wraps=self.form._reference_service.list_active_ticket_categories) as categories:
            QTest.mouseClick(self.form.abandon_contact_button, Qt.MouseButton.LeftButton)
            self.wait_idle()
            categories.assert_not_called()
        self.assertIsNone(self.form._pending_contact)
        self.assertIsNone(self.form._pending_company_id)
        self.assertFalse(self.form.abandon_contact_button.isVisible())
        self.assertTrue(self.form.company_input.isEnabled())
        self.assertTrue(self.form.add_company_button.isEnabled())
        self.assertIsNone(self.form.company_input.currentData())
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.form.company_input.findData(self.company.company_id), -1)
        self.assertEqual(self.draft(), self.original_draft)
        self.assertEqual((self.window.width(), self.window.height()), (1000, 700))
        heartbeats = []
        QTimer.singleShot(0, lambda: heartbeats.append(True))
        QTest.qWait(20)
        self.assertEqual(heartbeats, [True])

    def unavailable_company_recovery(self, *, delete=False, without_references=False):
        pending, before = self.committed_contact_with_unavailable_company(delete=delete)
        self.abandon_and_check()
        self.form.abandon_pending_contact()  # Repeated recovery is harmless.
        self.form.refresh_references_button.click()
        self.wait_idle()
        company_id = contact_id = None
        if not without_references:
            self.form.company_input.setCurrentIndex(1)
            self.wait_idle()
            company_id = self.form.company_input.currentData()
            self.form.contact_input.setCurrentIndex(1)
            contact_id = self.form.contact_input.currentData()
            self.assertIsNotNone(contact_id)
            self.assertNotEqual(contact_id, pending.contact_id)
        self.assertEqual(self.draft(), self.original_draft)
        self.form.save_button.click()
        self.wait_idle()
        ticket = self.window.workspace.details.ticket
        self.assertEqual((ticket.company_id, ticket.contact_id), (company_id, contact_id))
        self.assertEqual(self.contact_count(), before + 1)
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0], 6)

    def test_inactive_company_after_commit_recovers_and_saves(self):
        self.unavailable_company_recovery()

    def test_deleted_company_after_commit_recovers_and_saves(self):
        self.unavailable_company_recovery(delete=True)

    def test_abandoned_contact_allows_ticket_without_references(self):
        self.unavailable_company_recovery(without_references=True)

    def test_abandoned_contact_ignores_delayed_success_and_failure_for_same_company(self):
        callbacks = []
        original = self.form._reference_task

        def capture(work, success, failure):
            callbacks.append((success, failure))
            original(work, success, failure)

        with patch.object(self.form, "_reference_task", side_effect=capture):
            pending, before = self.committed_contact_with_unavailable_company()
        success, failure = callbacks[-1]
        self.abandon_and_check()
        # Even returning to the same company must not revive the old request.
        with database_connection(self.path) as connection:
            connection.execute("UPDATE companies SET is_active = 1 WHERE company_id = ?", (self.company.company_id,))
        self.form.refresh_references_button.click()
        self.wait_idle()
        self.form.company_input.setCurrentIndex(self.form.company_input.findData(self.company.company_id))
        self.wait_idle()
        options_before = self.form.contact_input.count()
        feedback_before = self.form.reference_feedback.text()
        success((TicketReferenceOption(pending.contact_id, "Stale result"),))
        failure(CompanyReferenceUnavailableError("private"))
        self.assertIsNone(self.form._pending_contact)
        self.assertIsNone(self.form.contact_input.currentData())
        self.assertEqual(self.form.contact_input.count(), options_before)
        self.assertEqual(self.form.reference_feedback.text(), feedback_before)
        self.assertFalse(self.form.abandon_contact_button.isVisible())
        self.assertTrue(self.form.company_input.isEnabled())
        self.assertEqual(self.contact_count(), before + 1)
        self.assertEqual(self.draft(), self.original_draft)

    def test_sqlite_write_failure_preserves_inputs_and_retry_inserts_once(self):
        before = self.contact_count()
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER test_write_failure BEFORE INSERT ON contacts BEGIN SELECT RAISE(ABORT, 'private'); END")
        dialog = self.open_dialog()
        dialog.name_input.setText("Alice Example")
        dialog.email_input.setText("alice@example.invalid")
        dialog.create_button.click()
        self.wait_idle()
        self.assertTrue(dialog.isVisible())
        self.assertEqual(dialog.name_input.text(), "Alice Example")
        self.assertEqual(dialog.email_input.text(), "alice@example.invalid")
        self.assertNotIn("private", dialog.feedback.text())
        self.assertEqual(self.contact_count(), before)
        self.assertEqual(self.draft(), self.original_draft)
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER test_write_failure")
        dialog.create_button.click()
        self.wait_idle()
        self.assertEqual(self.contact_count(), before + 1)

    def test_stale_inactive_or_deleted_company_rejects_creation(self):
        for delete in (False, True):
            before = self.contact_count()
            dialog = self.open_dialog()
            dialog.name_input.setText("Alice Example")
            with database_connection(self.path) as connection:
                connection.execute("DELETE FROM companies WHERE company_id = ?" if delete else "UPDATE companies SET is_active = 0 WHERE company_id = ?", (self.company.company_id,))
            dialog.create_button.click()
            self.wait_idle()
            self.assertTrue(dialog.isVisible())
            self.assertIn("no longer available", dialog.feedback.text())
            self.assertEqual(self.contact_count(), before)
            self.assertEqual(self.draft(), self.original_draft)
            dialog.cancel_button.click()

    def test_no_company_disables_creation(self):
        self.form.company_input.setCurrentIndex(0)
        self.wait_idle()
        self.assertFalse(self.form.add_contact_button.isEnabled())
        self.form.open_contact_dialog()
        self.assertIsNone(self.form._contact_dialog)
