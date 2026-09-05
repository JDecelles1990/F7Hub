from __future__ import annotations

import os
from types import SimpleNamespace
import threading
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import QTimer

from f7hub.gui.main_window import MainWindow
from f7hub.services.ticket_service import TicketService


class RecordingTicketService:
    def __init__(self):
        self.calls = 0
        self.gate = None
        self.error = None
        self.ticket = SimpleNamespace(
            ticket_id=1, ticket_number="TKT-1001", subject="Printer offline",
            description="Test printer", status="NEW", priority="MEDIUM",
            assigned_to=None, created_at="2026-09-04T15:00:00.000Z",
            updated_at="2026-09-04T15:00:00.000Z", resolved_at=None,
            closed_at=None, resolution=None,
        )

    def create_ticket(self, **values: object) -> object:
        self.calls += 1
        if self.gate:
            self.gate.wait(3)
        if self.error:
            raise self.error
        return self.ticket

    def list_tickets(self, **values):
        return (self.ticket,)

    def get_ticket_details(self, ticket_id):
        return SimpleNamespace(ticket=self.ticket, notes=(), status_history=(), timeline_events=())

    allowed_statuses = staticmethod(TicketService.allowed_statuses)


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.service = RecordingTicketService()
        self.window = MainWindow(self.service)
        self.window.show()
        self.application.processEvents()

    def tearDown(self) -> None:
        if self.service.gate:
            self.service.gate.set()
        self.wait_idle()
        self.window.workspace._clear_drafts()
        self.window.ticket_create_widget.reset_form()
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def test_window_hosts_ticket_form_and_application_chrome(self) -> None:
        self.assertEqual(self.window.windowTitle(), "F7Hub")
        self.assertIs(self.window.centralWidget(), self.window.pages)
        self.assertIs(self.window.pages.currentWidget(), self.window.ticket_create_widget)
        self.assertEqual(self.window.statusBar().currentMessage(), "Ready")
        self.assertEqual(self.window.exit_action.objectName(), "exitAction")

    def test_created_ticket_updates_application_status(self) -> None:
        self.window.ticket_create_widget.subject_input.setText("Printer offline")

        self.window.ticket_create_widget.submit()
        self.wait_idle()

        self.assertIs(self.window.pages.currentWidget(), self.window.workspace)
        self.assertEqual(self.window.workspace.details.ticket.ticket_number, "TKT-1001")
        self.assertEqual(self.window.workspace.model.rowCount(), 1)
        self.assertEqual(self.window.ticket_create_widget.subject_input.text(), "")

    def test_worker_keeps_event_loop_responsive_and_prevents_duplicate_submission(self):
        self.service.gate = threading.Event()
        self.window.ticket_create_widget.subject_input.setText("Pending save")
        self.window.ticket_create_widget.submit()
        self.window.ticket_create_widget.submit()
        ticks = []
        QTimer.singleShot(0, lambda: ticks.append(True))
        QTest.qWait(30)
        self.assertTrue(ticks)
        self.assertTrue(self.window.runner.busy)
        self.assertFalse(self.window.pages.isEnabled())
        self.assertFalse(self.window.close())
        self.assertTrue(self.window.isVisible())
        self.service.gate.set()
        self.wait_idle()
        self.assertEqual(self.service.calls, 1)

    def test_failed_background_save_preserves_new_ticket_draft(self):
        self.service.error = RuntimeError("Sensitive internal details")
        self.window.ticket_create_widget.subject_input.setText("Keep draft")
        self.window.ticket_create_widget.submit()
        self.wait_idle()
        form = self.window.ticket_create_widget
        self.assertEqual(form.subject_input.text(), "Keep draft")
        self.assertNotIn("Sensitive", form.form_error.text())
        self.assertTrue(form.save_button.isEnabled())
        self.assertIs(self.window.pages.currentWidget(), form)

    def test_saved_ticket_navigation_loads_and_opens_selected_row(self):
        self.window.show_tickets()
        self.wait_idle()
        workspace = self.window.workspace
        workspace._activate_row(workspace.model.index(0, 0))
        self.wait_idle()
        self.assertEqual(workspace.details.ticket.ticket_id, 1)
        self.assertIn("Printer offline", workspace.heading.text())

    def wait_idle(self):
        deadline = time.monotonic() + 5
        while self.window.runner.busy and time.monotonic() < deadline:
            QTest.qWait(5)
        self.assertFalse(self.window.runner.busy, "Background task did not finish")


if __name__ == "__main__":
    unittest.main()
