from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from f7hub.gui import TicketCreateWidget
from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories import TicketRepository
from f7hub.services import TicketService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = PROJECT_ROOT / "Database" / "Migrations"


class TicketCreationGuiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "f7hub_test.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = TicketRepository(self.database_path)
        self.service = TicketService(
            self.repository,
            ticket_number_factory=lambda: "TKT-GUI-FLOW",
        )
        self.widget = TicketCreateWidget(self.service)

    def tearDown(self) -> None:
        self.widget.close()
        self.widget.deleteLater()
        self.application.processEvents()
        self._temporary_directory.cleanup()

    def test_form_submission_persists_complete_initial_ticket_activity(self) -> None:
        created: list[object] = []
        self.widget.ticket_created.connect(created.append)
        self.widget.subject_input.setText("GUI integration ticket")
        self.widget.description_input.setPlainText("Created through the form")

        self.widget.submit()

        self.assertEqual(len(created), 1)
        ticket = self.repository.get_ticket_by_number("TKT-GUI-FLOW")
        self.assertIsNotNone(ticket)
        assert ticket is not None
        self.assertEqual(ticket.subject, "GUI integration ticket")
        self.assertEqual(len(self.repository.list_status_history(ticket.ticket_id)), 1)
        self.assertEqual(len(self.repository.list_timeline_events(ticket.ticket_id)), 1)


if __name__ == "__main__":
    unittest.main()
