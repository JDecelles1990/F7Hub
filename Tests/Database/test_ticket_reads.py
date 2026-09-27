from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.repositories.ticket_repository import TicketRepositoryTransaction
from f7hub.repositories.knowledge_repository import KnowledgeRepository
from f7hub.services.ticket_service import (
    TicketService, TicketValidationError, TicketReadError, TicketNotFoundError,
    TicketEditConflictError, TicketUpdateError, TICKET_PRIORITIES,
    TICKET_TYPES,
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

    def test_priority_filter_composes_with_status_and_pages_without_writing(self):
        tickets = [self.repo.create_ticket(
            ticket_number=f"P-{index}", subject=f"Priority {index}",
            created_at="2026-09-04T00:00:00.000Z", updated_at="2026-09-04T00:00:00.000Z",
            status=status, priority=priority,
        ) for index, (status, priority) in enumerate((
            ("OPEN", "HIGH"), ("CLOSED", "HIGH"), ("OPEN", "LOW"),
            ("OPEN", "HIGH"), ("OPEN", "CRITICAL"),
        ))]
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        self.assertEqual(self.service.list_tickets(priority="HIGH"), (tickets[3], tickets[1], tickets[0]))
        self.assertEqual(self.service.list_tickets(status="OPEN", priority="HIGH"), (tickets[3], tickets[0]))
        self.assertEqual(self.service.list_tickets(status="OPEN", priority="HIGH", limit=1, offset=1), (tickets[0],))
        self.assertEqual(self.service.list_tickets(priority="CRITICAL"), (tickets[4],))
        self.assertEqual(self.service.list_tickets(priority="MEDIUM"), ())
        self.assertEqual(self.repo.list_tickets(priority="HIGH' OR 1=1 --"), ())
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_type_filter_composes_with_status_priority_and_stable_paging(self):
        timestamp = "2026-09-04T00:00:00.000Z"
        values = (
            ("INCIDENT", "OPEN", "HIGH"),
            ("SERVICE_REQUEST", "OPEN", "HIGH"),
            ("PROBLEM", "OPEN", "HIGH"),
            ("TASK", "OPEN", "HIGH"),
            ("INCIDENT", "CLOSED", "HIGH"),
            ("INCIDENT", "OPEN", "LOW"),
            ("INCIDENT", "OPEN", "HIGH"),
        )
        tickets = [self.repo.create_ticket(
            ticket_number=f"TYPE-{index}", subject=f"Type {index}",
            ticket_type=ticket_type, status=status, priority=priority,
            created_at=timestamp, updated_at=timestamp,
        ) for index, (ticket_type, status, priority) in enumerate(values)]
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        for ticket_type in ("INCIDENT", "SERVICE_REQUEST", "PROBLEM", "TASK"):
            with self.subTest(ticket_type=ticket_type):
                expected = tuple(ticket for ticket in reversed(tickets)
                                 if ticket.ticket_type == ticket_type)
                self.assertEqual(self.service.list_tickets(ticket_type=ticket_type), expected)
        self.assertEqual(
            self.service.list_tickets(status="OPEN", priority="HIGH", ticket_type="INCIDENT"),
            (tickets[6], tickets[0]),
        )
        self.assertEqual(
            self.service.list_tickets(status="OPEN", priority="HIGH", ticket_type="INCIDENT",
                                      limit=1, offset=1),
            (tickets[0],),
        )
        self.assertEqual(self.service.list_tickets(ticket_type=None), tuple(reversed(tickets)))
        self.assertEqual(self.repo.list_tickets(ticket_type="INCIDENT' OR 1=1 --"), ())
        with patch.object(self.repo, "list_tickets") as query:
            for value in ("", "incident", "INCIDENT' OR 1=1 --", True, 1, []):
                with self.subTest(invalid=value), self.assertRaises(TicketValidationError):
                    self.service.list_tickets(ticket_type=value)
            query.assert_not_called()
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_detail_reloads_ticket_and_related_activity(self):
        ticket = self.service.create_ticket(subject="Read me")
        note = self.service.add_note(ticket.ticket_id, note_text="First note")
        updated = self.service.change_status(ticket.ticket_id, new_status="OPEN")
        details = TicketService(TicketRepository(self.path)).get_ticket_details(ticket.ticket_id)
        self.assertEqual(details.ticket, updated)
        self.assertEqual(details.notes, (note,))
        self.assertEqual(tuple(h.new_status for h in details.status_history), ("NEW", "OPEN"))
        self.assertEqual(len(details.timeline_events), 3)

    def test_subject_edit_is_atomic_trimmed_and_preserves_other_ticket_data(self):
        ticket = self.service.create_ticket(
            subject="Printer offline", ticket_type="TASK", priority="HIGH",
            description="Original description",
        )
        self.service.add_note(ticket.ticket_id, note_text="Existing note")
        self.service.change_status(ticket.ticket_id, new_status="OPEN")
        article = KnowledgeRepository(self.path).create_article(
            article_code="KB-SUBJECT-30", title="Guide", summary=None,
            body_markdown="Body", created_at=ticket.created_at, updated_at=ticket.updated_at,
        )
        current = self.repo.get_ticket(ticket.ticket_id)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO ticket_knowledge_articles "
                "(ticket_id, knowledge_article_id, linked_at) VALUES (?, ?, ?)",
                (ticket.ticket_id, article.knowledge_article_id, current.updated_at),
            )
            connection.commit()
        edited = self.service.update_ticket_subject(
            ticket.ticket_id, expected_subject=current.subject,
            expected_updated_at=current.updated_at, subject="  Printer repaired  ",
        )
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertEqual(edited, details.ticket)
        self.assertEqual(edited.subject, "Printer repaired")
        self.assertEqual(edited.ticket_type, "TASK")
        self.assertEqual(edited.priority, "HIGH")
        self.assertEqual(edited.status, "OPEN")
        self.assertEqual(edited.description, "Original description")
        self.assertEqual(details.notes[0].note_text, "Existing note")
        self.assertEqual(len(details.status_history), 2)
        self.assertEqual([e.event_type for e in details.timeline_events].count("SUBJECT_CHANGED"), 1)
        self.assertNotIn("Printer", str(details.timeline_events[-1]))
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM ticket_knowledge_articles WHERE ticket_id = ?",
                (ticket.ticket_id,),
            ).fetchone(), (1,))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_subject_edit_rejects_invalid_missing_and_stale_before_no_op(self):
        ticket = self.service.create_ticket(subject="Original")
        args = dict(expected_subject=ticket.subject, expected_updated_at=ticket.updated_at)
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        for value in (0, -1, True, None):
            with self.subTest(ticket_id=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_subject(value, subject="Changed", **args)
        for value in ("", "  ", None, 42):
            with self.subTest(subject=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_subject(ticket.ticket_id, subject=value, **args)
        with self.assertRaises(TicketNotFoundError):
            self.service.update_ticket_subject(999, subject="Changed", **args)
        with self.assertRaises(TicketEditConflictError):
            self.service.update_ticket_subject(
                ticket.ticket_id, expected_subject="Older",
                expected_updated_at=ticket.updated_at, subject="Original",
            )
        with self.assertRaises(TicketEditConflictError):
            self.service.update_ticket_subject(
                ticket.ticket_id, expected_subject=ticket.subject,
                expected_updated_at="2020-01-01T00:00:00.000Z", subject="Original",
            )
        same = self.service.update_ticket_subject(ticket.ticket_id, subject=" Original ", **args)
        self.assertEqual(same, ticket)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_subject_edit_advances_same_millisecond_and_allows_closed_ticket(self):
        ticket = self.service.create_ticket(subject="Old")
        self.service.change_status(ticket.ticket_id, new_status="RESOLVED", resolution="Fixed")
        self.service.change_status(ticket.ticket_id, new_status="CLOSED")
        current = self.repo.get_ticket(ticket.ticket_id)
        from datetime import datetime
        fixed = datetime.fromisoformat(current.updated_at.replace("Z", "+00:00"))
        service = TicketService(self.repo, clock=lambda: fixed)
        edited = service.update_ticket_subject(
            ticket.ticket_id, expected_subject=current.subject,
            expected_updated_at=current.updated_at, subject="New",
        )
        self.assertGreater(edited.updated_at, current.updated_at)
        self.assertEqual(edited.status, "CLOSED")
        self.assertEqual(edited.resolution, current.resolution)

    def test_subject_edit_rolls_back_update_event_and_reload_failures(self):
        ticket = self.service.create_ticket(subject="Old")
        args = dict(expected_subject=ticket.subject, expected_updated_at=ticket.updated_at,
                    subject="New")
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        with patch.object(TicketRepositoryTransaction, "update_ticket_subject",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                self.service.update_ticket_subject(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "create_timeline_event",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                self.service.update_ticket_subject(ticket.ticket_id, **args)
        original_get = TicketRepositoryTransaction.get_ticket
        reads = 0

        def fail_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                raise sqlite3.OperationalError("private")
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", fail_second_read):
            with self.assertRaises(TicketUpdateError):
                self.service.update_ticket_subject(ticket.ticket_id, **args)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_description_edit_normalizes_multiline_clears_and_preserves_relationships(self):
        timestamp = "2026-09-27T12:00:00.000Z"
        with database_connection(self.path) as connection:
            company_id = connection.execute(
                "INSERT INTO companies (name, created_at, updated_at) VALUES (?, ?, ?)",
                ("Example Company", timestamp, timestamp),
            ).lastrowid
            contact_id = connection.execute(
                "INSERT INTO contacts (company_id, display_name, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                (company_id, "Example Contact", timestamp, timestamp),
            ).lastrowid
            category_id = connection.execute(
                "INSERT INTO categories (scope, name, slug, created_at, updated_at) "
                "VALUES ('TICKET', ?, ?, ?, ?)",
                ("Printing", "printing-s032", timestamp, timestamp),
            ).lastrowid
        ticket = self.service.create_ticket(
            subject="Printer offline", ticket_type="TASK", priority="HIGH",
            description="Initial description", assigned_to="Technician", source="Manual",
            company_id=company_id, contact_id=contact_id, category_id=category_id,
        )
        self.service.add_note(ticket.ticket_id, note_text="Existing note")
        self.service.change_status(ticket.ticket_id, new_status="RESOLVED", resolution="Fixed")
        self.service.change_status(ticket.ticket_id, new_status="CLOSED")
        article = KnowledgeRepository(self.path).create_article(
            article_code="KB-DESCRIPTION-32", title="Guide", summary=None,
            body_markdown="Body", created_at=ticket.created_at, updated_at=ticket.updated_at,
        )
        current = self.repo.get_ticket(ticket.ticket_id)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO ticket_knowledge_articles "
                "(ticket_id, knowledge_article_id, linked_at) VALUES (?, ?, ?)",
                (ticket.ticket_id, article.knowledge_article_id, current.updated_at),
            )
            connection.commit()
        original_details = self.service.get_ticket_details(ticket.ticket_id)
        for entered, expected in (
            ("  Line one\n  Line two\n", "Line one\n  Line two"),
            (" \n  ", None),
            ("  One line  ", "One line"),
        ):
            with self.subTest(entered=entered):
                previous = current
                current = self.service.update_ticket_description(
                    ticket.ticket_id, expected_description=previous.description,
                    expected_updated_at=previous.updated_at, description=entered,
                )
                self.assertEqual(current, replace(previous, description=expected,
                                                  updated_at=current.updated_at))
                self.assertGreater(current.updated_at, previous.updated_at)
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertEqual(details.ticket, current)
        self.assertEqual(details.notes, original_details.notes)
        self.assertEqual(details.status_history, original_details.status_history)
        events = [event for event in details.timeline_events
                  if event.event_type == "DESCRIPTION_CHANGED"]
        self.assertEqual(len(events), 3)
        self.assertTrue(all(event.details is None and event.metadata_json is None
                            and event.title == "Ticket description changed" for event in events))
        self.assertTrue(all("Line one" not in str(event) and "One line" not in str(event)
                            for event in events))
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute(
                "SELECT description FROM tickets WHERE ticket_id = ?", (ticket.ticket_id,),
            ).fetchone(), ("One line",))
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM ticket_knowledge_articles WHERE ticket_id = ?",
                (ticket.ticket_id,),
            ).fetchone(), (1,))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_description_edit_validates_stale_state_before_null_and_text_no_op(self):
        ticket = self.service.create_ticket(subject="Original")
        args = dict(expected_description=None, expected_updated_at=ticket.updated_at)
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        for value in (0, -1, True, None):
            with self.subTest(ticket_id=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_description(value, description="Text", **args)
        for value in (True, 42, []):
            with self.subTest(description=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_description(ticket.ticket_id, description=value, **args)
            with self.subTest(expected=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_description(
                    ticket.ticket_id, expected_description=value,
                    expected_updated_at=ticket.updated_at, description="Text",
                )
        with self.assertRaises(TicketNotFoundError):
            self.service.update_ticket_description(999, description="Text", **args)
        for expected in (args | {"expected_description": "stale"},
                         args | {"expected_updated_at": "2020-01-01T00:00:00.000Z"}):
            with self.subTest(expected=expected), self.assertRaises(TicketEditConflictError):
                self.service.update_ticket_description(
                    ticket.ticket_id, description=" \n ", **expected,
                )
        self.assertEqual(self.service.update_ticket_description(
            ticket.ticket_id, description=" \n ", **args,
        ), ticket)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        current = self.service.update_ticket_description(
            ticket.ticket_id, description="Text", **args,
        )
        self.assertEqual(current.description, "Text")
        with closing(sqlite3.connect(self.path)) as connection:
            after_change = tuple(connection.iterdump())
        for expected in (
            dict(expected_description=None, expected_updated_at=current.updated_at),
            dict(expected_description="Text", expected_updated_at=ticket.updated_at),
        ):
            with self.subTest(expected=expected), self.assertRaises(TicketEditConflictError):
                self.service.update_ticket_description(
                    ticket.ticket_id, description=" Text ", **expected,
                )
        self.assertEqual(self.service.update_ticket_description(
            ticket.ticket_id, expected_description="Text",
            expected_updated_at=current.updated_at, description=" Text ",
        ), current)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), after_change)
        with self.repo.transaction() as transaction:
            self.assertFalse(transaction.update_ticket_description(
                ticket.ticket_id, expected_description=None,
                expected_updated_at=current.updated_at, description="Wrong", updated_at="later",
            ))

    def test_description_edit_advances_same_millisecond_and_rolls_back_failures(self):
        ticket = self.service.create_ticket(subject="Original")
        from datetime import datetime
        fixed = datetime.fromisoformat(ticket.updated_at.replace("Z", "+00:00"))
        service = TicketService(self.repo, clock=lambda: fixed)
        args = dict(expected_description=None, expected_updated_at=ticket.updated_at,
                    description="Replacement")
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        with patch.object(TicketRepositoryTransaction, "update_ticket_description",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_description(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "update_ticket_description", return_value=False):
            with self.assertRaises(TicketEditConflictError):
                service.update_ticket_description(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "create_timeline_event",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_description(ticket.ticket_id, **args)
        original_get = TicketRepositoryTransaction.get_ticket
        reads = 0

        def fail_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                raise sqlite3.OperationalError("private")
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", fail_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_description(ticket.ticket_id, **args)
        reads = 0

        def lose_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                return None
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", lose_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_description(ticket.ticket_id, **args)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        edited = service.update_ticket_description(ticket.ticket_id, **args)
        self.assertGreater(edited.updated_at, ticket.updated_at)
        self.assertEqual(edited.description, "Replacement")
        self.assertEqual([event.event_type for event in
                          self.repo.list_timeline_events(ticket.ticket_id)].count(
                              "DESCRIPTION_CHANGED"), 1)

    def test_priority_edit_transitions_preserve_other_data_and_relationships(self):
        ticket = self.service.create_ticket(
            subject="Printer offline", ticket_type="TASK", priority="LOW",
            description="Original description", assigned_to="Technician", source="Manual",
        )
        self.service.add_note(ticket.ticket_id, note_text="Existing note")
        self.service.change_status(ticket.ticket_id, new_status="RESOLVED", resolution="Fixed")
        self.service.change_status(ticket.ticket_id, new_status="CLOSED")
        article = KnowledgeRepository(self.path).create_article(
            article_code="KB-PRIORITY-31", title="Guide", summary=None,
            body_markdown="Body", created_at=ticket.created_at, updated_at=ticket.updated_at,
        )
        current = self.repo.get_ticket(ticket.ticket_id)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO ticket_knowledge_articles "
                "(ticket_id, knowledge_article_id, linked_at) VALUES (?, ?, ?)",
                (ticket.ticket_id, article.knowledge_article_id, current.updated_at),
            )
            connection.commit()
        before_details = self.service.get_ticket_details(ticket.ticket_id)
        for priority in sorted(TICKET_PRIORITIES - {"LOW"}) + ["LOW"]:
            with self.subTest(priority=priority):
                previous = current
                current = self.service.update_ticket_priority(
                    ticket.ticket_id, expected_priority=previous.priority,
                    expected_updated_at=previous.updated_at, priority=priority,
                )
                self.assertEqual(current, replace(previous, priority=priority,
                                                  updated_at=current.updated_at))
                self.assertGreater(current.updated_at, previous.updated_at)
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertEqual(details.ticket, current)
        self.assertEqual(details.notes, before_details.notes)
        self.assertEqual(details.status_history, before_details.status_history)
        events = [event for event in details.timeline_events
                  if event.event_type == "PRIORITY_CHANGED"]
        self.assertEqual(len(events), len(TICKET_PRIORITIES))
        self.assertTrue(all(event.details is None and event.metadata_json is None
                            and event.title == "Ticket priority changed" for event in events))
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM ticket_knowledge_articles WHERE ticket_id = ?",
                (ticket.ticket_id,),
            ).fetchone(), (1,))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_priority_edit_rejects_invalid_missing_and_stale_before_no_op(self):
        ticket = self.service.create_ticket(subject="Original", priority="MEDIUM")
        args = dict(expected_priority=ticket.priority, expected_updated_at=ticket.updated_at)
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        for value in (0, -1, True, None):
            with self.subTest(ticket_id=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_priority(value, priority="HIGH", **args)
        for value in ("", "medium", "HIGH' OR 1=1 --", True, None, 42):
            with self.subTest(priority=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_priority(ticket.ticket_id, priority=value, **args)
        for field, value in (("expected_priority", "UNKNOWN"),
                             ("expected_updated_at", "")):
            with self.subTest(field=field), self.assertRaises(TicketValidationError):
                self.service.update_ticket_priority(
                    ticket.ticket_id, priority="HIGH", **(args | {field: value}),
                )
        with self.assertRaises(TicketNotFoundError):
            self.service.update_ticket_priority(999, priority="HIGH", **args)
        for expected in (args | {"expected_priority": "LOW"},
                         args | {"expected_updated_at": "2020-01-01T00:00:00.000Z"}):
            with self.subTest(expected=expected), self.assertRaises(TicketEditConflictError):
                self.service.update_ticket_priority(ticket.ticket_id, priority="MEDIUM", **expected)
        self.assertEqual(self.service.update_ticket_priority(ticket.ticket_id,
                         priority="MEDIUM", **args), ticket)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_every_priority_transition_is_allowed(self):
        for initial in TICKET_PRIORITIES:
            for destination in TICKET_PRIORITIES - {initial}:
                with self.subTest(initial=initial, destination=destination):
                    ticket = self.service.create_ticket(
                        subject=f"{initial} to {destination}", priority=initial,
                    )
                    updated = self.service.update_ticket_priority(
                        ticket.ticket_id, expected_priority=initial,
                        expected_updated_at=ticket.updated_at, priority=destination,
                    )
                    self.assertEqual(updated.priority, destination)
                    self.assertEqual([event.event_type for event in
                                      self.repo.list_timeline_events(ticket.ticket_id)]
                                     .count("PRIORITY_CHANGED"), 1)

    def test_priority_edit_advances_same_millisecond_and_rolls_back_failures(self):
        ticket = self.service.create_ticket(subject="Old", priority="LOW")
        from datetime import datetime
        fixed = datetime.fromisoformat(ticket.updated_at.replace("Z", "+00:00"))
        service = TicketService(self.repo, clock=lambda: fixed)
        args = dict(expected_priority=ticket.priority, expected_updated_at=ticket.updated_at,
                    priority="HIGH")
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        with patch.object(TicketRepositoryTransaction, "update_ticket_priority",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_priority(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "update_ticket_priority", return_value=False):
            with self.assertRaises(TicketEditConflictError):
                service.update_ticket_priority(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "create_timeline_event",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_priority(ticket.ticket_id, **args)
        original_get = TicketRepositoryTransaction.get_ticket
        reads = 0

        def fail_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                raise sqlite3.OperationalError("private")
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", fail_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_priority(ticket.ticket_id, **args)
        reads = 0

        def lose_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                return None
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", lose_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_priority(ticket.ticket_id, **args)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        edited = service.update_ticket_priority(ticket.ticket_id, **args)
        self.assertGreater(edited.updated_at, ticket.updated_at)
        self.assertEqual(edited.priority, "HIGH")
        self.assertEqual([event.event_type for event in self.repo.list_timeline_events(ticket.ticket_id)]
                         .count("PRIORITY_CHANGED"), 1)

    def test_type_edit_transitions_preserve_ticket_activity_and_relationships(self):
        ticket = self.service.create_ticket(
            subject="Printer offline", ticket_number="INC-UNCHANGED", ticket_type="INCIDENT",
            priority="HIGH", description="Original description", assigned_to="Technician",
            source="Manual",
        )
        self.service.add_note(ticket.ticket_id, note_text="Existing note")
        self.service.change_status(ticket.ticket_id, new_status="RESOLVED", resolution="Fixed")
        self.service.change_status(ticket.ticket_id, new_status="CLOSED")
        article = KnowledgeRepository(self.path).create_article(
            article_code="KB-TYPE-33", title="Guide", summary=None,
            body_markdown="Body", created_at=ticket.created_at, updated_at=ticket.updated_at,
        )
        current = self.repo.get_ticket(ticket.ticket_id)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO ticket_knowledge_articles "
                "(ticket_id, knowledge_article_id, linked_at) VALUES (?, ?, ?)",
                (ticket.ticket_id, article.knowledge_article_id, current.updated_at),
            )
            connection.commit()
        before_details = self.service.get_ticket_details(ticket.ticket_id)
        for destination in (*TICKET_TYPES[1:], TICKET_TYPES[0]):
            with self.subTest(destination=destination):
                previous = current
                current = self.service.update_ticket_type(
                    ticket.ticket_id, expected_ticket_type=previous.ticket_type,
                    expected_updated_at=previous.updated_at, ticket_type=destination,
                )
                self.assertEqual(current, replace(previous, ticket_type=destination,
                                                  updated_at=current.updated_at))
                self.assertGreater(current.updated_at, previous.updated_at)
        details = self.service.get_ticket_details(ticket.ticket_id)
        self.assertEqual(details.ticket, current)
        self.assertEqual(current.ticket_number, "INC-UNCHANGED")
        self.assertEqual(current.status, "CLOSED")
        self.assertEqual(details.notes, before_details.notes)
        self.assertEqual(details.status_history, before_details.status_history)
        events = [event for event in details.timeline_events
                  if event.event_type == "TYPE_CHANGED"]
        self.assertEqual(len(events), len(TICKET_TYPES))
        self.assertTrue(all(event.details is None and event.metadata_json is None
                            and event.title == "Ticket type changed" for event in events))
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM ticket_knowledge_articles WHERE ticket_id = ?",
                (ticket.ticket_id,),
            ).fetchone(), (1,))
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone(), ("ok",))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_every_type_transition_is_allowed(self):
        for initial in TICKET_TYPES:
            for destination in TICKET_TYPES:
                if destination == initial:
                    continue
                with self.subTest(initial=initial, destination=destination):
                    ticket = self.service.create_ticket(
                        subject=f"{initial} to {destination}", ticket_type=initial,
                    )
                    updated = self.service.update_ticket_type(
                        ticket.ticket_id, expected_ticket_type=initial,
                        expected_updated_at=ticket.updated_at, ticket_type=destination,
                    )
                    self.assertEqual(updated.ticket_type, destination)
                    self.assertEqual([event.event_type for event in
                                      self.repo.list_timeline_events(ticket.ticket_id)]
                                     .count("TYPE_CHANGED"), 1)

    def test_type_edit_rejects_invalid_missing_and_stale_before_no_op(self):
        ticket = self.service.create_ticket(subject="Original", ticket_type="INCIDENT")
        args = dict(expected_ticket_type=ticket.ticket_type,
                    expected_updated_at=ticket.updated_at)
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        for value in (0, -1, True, None):
            with self.subTest(ticket_id=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_type(value, ticket_type="TASK", **args)
        for value in ("", "incident", "TASK' OR 1=1 --", True, None, 42):
            with self.subTest(ticket_type=value), self.assertRaises(TicketValidationError):
                self.service.update_ticket_type(ticket.ticket_id, ticket_type=value, **args)
        for field, value in (("expected_ticket_type", "UNKNOWN"),
                             ("expected_updated_at", "")):
            with self.subTest(field=field), self.assertRaises(TicketValidationError):
                self.service.update_ticket_type(
                    ticket.ticket_id, ticket_type="TASK", **(args | {field: value}),
                )
        with self.assertRaises(TicketNotFoundError):
            self.service.update_ticket_type(999, ticket_type="TASK", **args)
        for expected in (args | {"expected_ticket_type": "TASK"},
                         args | {"expected_updated_at": "2020-01-01T00:00:00.000Z"}):
            with self.subTest(expected=expected), self.assertRaises(TicketEditConflictError):
                self.service.update_ticket_type(
                    ticket.ticket_id, ticket_type="INCIDENT", **expected,
                )
        self.assertEqual(self.service.update_ticket_type(
            ticket.ticket_id, ticket_type="INCIDENT", **args,
        ), ticket)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_type_edit_advances_same_millisecond_and_rolls_back_failures(self):
        ticket = self.service.create_ticket(subject="Old", ticket_type="INCIDENT")
        from datetime import datetime
        fixed = datetime.fromisoformat(ticket.updated_at.replace("Z", "+00:00"))
        service = TicketService(self.repo, clock=lambda: fixed)
        args = dict(expected_ticket_type=ticket.ticket_type,
                    expected_updated_at=ticket.updated_at, ticket_type="TASK")
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        with patch.object(TicketRepositoryTransaction, "update_ticket_type",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_type(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "update_ticket_type", return_value=False):
            with self.assertRaises(TicketEditConflictError):
                service.update_ticket_type(ticket.ticket_id, **args)
        with patch.object(TicketRepositoryTransaction, "create_timeline_event",
                          side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_type(ticket.ticket_id, **args)
        original_get = TicketRepositoryTransaction.get_ticket
        reads = 0

        def fail_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                raise sqlite3.OperationalError("private")
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", fail_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_type(ticket.ticket_id, **args)
        reads = 0

        def lose_second_read(transaction, ticket_id):
            nonlocal reads
            reads += 1
            if reads == 2:
                return None
            return original_get(transaction, ticket_id)

        with patch.object(TicketRepositoryTransaction, "get_ticket", lose_second_read):
            with self.assertRaises(TicketUpdateError):
                service.update_ticket_type(ticket.ticket_id, **args)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
        edited = service.update_ticket_type(ticket.ticket_id, **args)
        self.assertGreater(edited.updated_at, ticket.updated_at)
        self.assertEqual(edited.ticket_type, "TASK")
        self.assertEqual([event.event_type for event in self.repo.list_timeline_events(ticket.ticket_id)]
                         .count("TYPE_CHANGED"), 1)

    def test_exact_number_lookup_reloads_current_details_without_writing(self):
        ticket = self.service.create_ticket(subject="Read by number", ticket_number="INC-2042")
        self.service.add_note(ticket.ticket_id, note_text="Latest note")
        with closing(sqlite3.connect(self.path)) as connection:
            before = tuple(connection.iterdump())
        details = self.service.get_ticket_details_by_number("  inc-2042  ")
        self.assertEqual(details.ticket.ticket_id, ticket.ticket_id)
        self.assertEqual(details.notes[0].note_text, "Latest note")
        with self.assertRaises(TicketNotFoundError):
            self.service.get_ticket_details_by_number("INC-204")
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_number_lookup_validation_missing_and_disappearing_ticket(self):
        for value in ("", "  ", None, 7, True):
            with self.subTest(value=value), self.assertRaises(TicketValidationError):
                self.service.get_ticket_details_by_number(value)
        with self.assertRaises(TicketNotFoundError):
            self.service.get_ticket_details_by_number("missing")
        ticket = self.service.create_ticket(subject="Disappearing", ticket_number="INC-GONE")
        with patch.object(self.repo, "get_ticket_details", return_value=None):
            with self.assertRaises(TicketNotFoundError):
                self.service.get_ticket_details_by_number(ticket.ticket_number)

    def test_number_lookup_translates_repository_failure(self):
        with patch.object(self.repo, "get_ticket_by_number", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(TicketReadError) as caught:
                self.service.get_ticket_details_by_number("INC-2042")
        self.assertNotIn("private", str(caught.exception))

    def test_read_validation_and_missing_ticket(self):
        for args in ({"limit": 0}, {"limit": True}, {"limit": 201},
                     {"offset": -1}, {"offset": True}, {"offset": 2**64}, {"status": "BAD"},
                     {"priority": "BAD"}, {"priority": "high"}, {"priority": True},
                     {"priority": 1}):
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
