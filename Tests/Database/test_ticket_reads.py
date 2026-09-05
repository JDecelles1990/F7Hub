from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import (
    TicketService, TicketValidationError, TicketReadError, TicketNotFoundError,
)


class TicketReadTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "reads.db"
        bootstrap_database(self.path, Path(__file__).resolve().parents[2] / "Database/Migrations")
        self.repo = TicketRepository(self.path)
        self.service = TicketService(self.repo)

    def test_list_filters_and_pages_with_stable_timestamp_ties(self):
        tickets = [self.repo.create_ticket(
            ticket_number=f"T-{index}", subject=f"Subject {index}",
            created_at="2026-09-04T00:00:00.000Z", updated_at="2026-09-04T00:00:00.000Z",
            status="OPEN" if index % 2 else "CLOSED",
        ) for index in range(5)]
        self.assertEqual(self.service.list_tickets(limit=2), (tickets[4], tickets[3]))
        self.assertEqual(self.service.list_tickets(limit=2, offset=2), (tickets[2], tickets[1]))
        self.assertEqual(self.service.list_tickets(status="OPEN"), (tickets[3], tickets[1]))
        self.assertEqual(self.service.list_tickets(offset=99), ())
        self.assertEqual(self.repo.list_tickets(status="OPEN' OR 1=1 --"), ())

    def test_detail_reloads_ticket_and_related_activity(self):
        ticket = self.service.create_ticket(subject="Read me")
        note = self.service.add_note(ticket.ticket_id, note_text="First note")
        updated = self.service.change_status(ticket.ticket_id, new_status="OPEN")
        details = TicketService(TicketRepository(self.path)).get_ticket_details(ticket.ticket_id)
        self.assertEqual(details.ticket, updated)
        self.assertEqual(details.notes, (note,))
        self.assertEqual(tuple(h.new_status for h in details.status_history), ("NEW", "OPEN"))
        self.assertEqual(len(details.timeline_events), 3)

    def test_read_validation_and_missing_ticket(self):
        for args in ({"limit": 0}, {"limit": True}, {"limit": 201},
                     {"offset": -1}, {"offset": True}, {"offset": 2**64}, {"status": "BAD"}):
            with self.subTest(args=args), self.assertRaises(TicketValidationError):
                self.service.list_tickets(**args)
        with self.assertRaises(TicketNotFoundError):
            self.service.get_ticket_details(999)
        with self.assertRaises(TicketValidationError):
            self.service.get_ticket_details(True)

    def test_read_failures_have_safe_service_errors(self):
        with patch.object(self.repo, "list_tickets", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketReadError) as caught:
                self.service.list_tickets()
        self.assertNotIn("private", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, sqlite3.OperationalError)
        with patch.object(self.repo, "get_ticket_details", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketReadError):
                self.service.get_ticket_details(1)


if __name__ == "__main__":
    unittest.main()
