from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import (
    bootstrap_database,
    database_connection,
    validate_database_integrity,
)
from f7hub.repositories.ticket_repository import TicketRepository
from f7hub.services.ticket_service import (
    TicketNotFoundError,
    TicketService,
    TicketUpdateError,
    TicketValidationError,
)


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "Database" / "Migrations"
START = datetime(2026, 9, 4, 15, tzinfo=timezone.utc)


class TicketActivityServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "activity.db"
        bootstrap_database(self.database_path, MIGRATIONS_DIR)
        self.repository = TicketRepository(self.database_path)
        self.now = START
        self.service = TicketService(self.repository, clock=lambda: self.now)
        self.ticket = self.service.create_ticket(
            subject="Printer offline",
            description="Office printer",
            priority="HIGH",
            assigned_to="Jo",
            source="MANUAL",
        )
        self.now += timedelta(minutes=1)

    def test_note_preserves_metadata_and_updates_only_ticket_activity(self) -> None:
        note = self.service.add_note(
            self.ticket.ticket_id,
            note_text="  O'Reilly'); DROP TABLE tickets;--  ",
            note_type="WORKLOG",
            author_label="  Jo  ",
            source="  MANUAL  ",
            is_ai_generated=True,
        )

        reloaded_repository = TicketRepository(self.database_path)
        self.assertEqual(reloaded_repository.get_note(note.ticket_note_id), note)
        self.assertEqual(note.note_text, "O'Reilly'); DROP TABLE tickets;--")
        self.assertEqual(note.note_type, "WORKLOG")
        self.assertEqual(note.author_label, "Jo")
        self.assertEqual(note.source, "MANUAL")
        self.assertTrue(note.is_ai_generated)
        self.assertEqual(note.created_at, "2026-09-04T15:01:00.000Z")
        self.assertEqual(note.updated_at, note.created_at)
        ticket = reloaded_repository.get_ticket(self.ticket.ticket_id)
        self.assertEqual(ticket.updated_at, note.created_at)
        self.assertEqual(ticket.status, "NEW")
        self.assertEqual(ticket.subject, self.ticket.subject)
        self.assertEqual(ticket.description, self.ticket.description)
        self.assertEqual(ticket.priority, "HIGH")
        self.assertEqual(ticket.assigned_to, "Jo")
        self.assertEqual(ticket.source, "MANUAL")
        self.assertEqual(ticket.created_at, self.ticket.created_at)
        self.assertEqual(len(self.repository.list_status_history(ticket.ticket_id)), 1)
        event = self.repository.list_timeline_events(ticket.ticket_id)[-1]
        self.assertEqual(event.event_type, "NOTE_ADDED")
        self.assertEqual(json.loads(event.metadata_json), {
            "ticket_note_id": note.ticket_note_id,
        })
        self.assertIsNone(event.details)
        self.assertEqual(event.actor_label, "Jo")
        self.assertEqual(event.occurred_at, note.created_at)
        self._assert_integrity()

    def test_multiple_note_types_do_not_change_status(self) -> None:
        notes = tuple(
            self.service.add_note(
                self.ticket.ticket_id, note_text=kind, note_type=kind
            )
            for kind in ("INTERNAL", "PUBLIC", "WORKLOG", "RESOLUTION")
        )

        self.assertEqual(self.repository.list_notes(self.ticket.ticket_id), notes)
        self.assertEqual(self.repository.get_ticket(self.ticket.ticket_id).status, "NEW")
        self.assertTrue(all(not note.is_ai_generated for note in notes))

    def test_invalid_note_inputs_make_no_changes(self) -> None:
        before = self._snapshot()
        invalid = (
            {"note_text": ""}, {"note_text": " \n\t "}, {"note_text": 123},
            {"note_type": "ESCALATION"}, {"note_type": None},
            {"author_label": 12}, {"source": False},
            {"is_ai_generated": 1}, {"is_ai_generated": "false"},
        )
        for values in invalid:
            with self.subTest(values=values):
                arguments = {"note_text": "A valid note", **values}
                with self.assertRaises(TicketValidationError):
                    self.service.add_note(self.ticket.ticket_id, **arguments)
                self.assertEqual(self._snapshot(), before)

    def test_invalid_ticket_ids_are_rejected_for_both_operations(self) -> None:
        before = self._snapshot()
        for ticket_id in (None, True, 0, -1, "1", 1.5):
            with self.subTest(ticket_id=ticket_id):
                with self.assertRaises(TicketValidationError):
                    self.service.add_note(ticket_id, note_text="Note")
                with self.assertRaises(TicketValidationError):
                    self.service.change_status(ticket_id, new_status="OPEN")
        self.assertEqual(self._snapshot(), before)

    def test_missing_ticket_is_reported_without_orphan_activity(self) -> None:
        before = self._snapshot()
        with self.assertRaises(TicketNotFoundError):
            self.service.add_note(999_999, note_text="Note")
        with self.assertRaises(TicketNotFoundError):
            self.service.change_status(999_999, new_status="OPEN")
        self.assertEqual(self._snapshot(), before)

    def test_active_status_changes_record_exact_previous_state_and_actor(self) -> None:
        previous = "NEW"
        for status in ("OPEN", "IN_PROGRESS", "WAITING", "IN_PROGRESS", "OPEN"):
            with self.subTest(status=status):
                ticket = self.service.change_status(
                    self.ticket.ticket_id,
                    new_status=status,
                    reason="  Technician update  ",
                    changed_by="  Jo  ",
                )
                self.assertEqual(self.repository.get_ticket(ticket.ticket_id), ticket)
                self.assertEqual(ticket.status, status)
                self.assertEqual(ticket.subject, self.ticket.subject)
                self.assertEqual(ticket.description, self.ticket.description)
                self.assertEqual(ticket.assigned_to, self.ticket.assigned_to)
                self.assertEqual(ticket.priority, self.ticket.priority)
                self.assertEqual(ticket.created_at, self.ticket.created_at)
                history = self.repository.list_status_history(ticket.ticket_id)[-1]
                self.assertEqual((history.previous_status, history.new_status),
                                 (previous, status))
                self.assertEqual(history.reason, "Technician update")
                self.assertEqual(history.changed_by, "Jo")
                self.assertEqual(history.changed_at, ticket.updated_at)
                event = self.repository.list_timeline_events(ticket.ticket_id)[-1]
                self.assertEqual(event.event_type, "STATUS_CHANGED")
                self.assertEqual(event.details, "Technician update")
                self.assertEqual(event.actor_label, "Jo")
                self.assertEqual(event.occurred_at, ticket.updated_at)
                self.assertEqual(json.loads(event.metadata_json), {
                    "previous_status": previous, "new_status": status,
                })
                previous = status
                self.now += timedelta(minutes=1)
        self._assert_integrity()

    def test_resolve_close_reopen_and_resolve_again_preserve_prior_resolution(self) -> None:
        resolved = self.service.change_status(
            self.ticket.ticket_id,
            new_status="RESOLVED",
            resolution="  Replaced printer cable; test page printed.  ",
            changed_by="Jo",
        )
        self.assertEqual(resolved.resolution, "Replaced printer cable; test page printed.")
        self.assertEqual(resolved.resolved_at, resolved.updated_at)
        self.assertIsNone(resolved.closed_at)
        resolution_note = self.repository.list_notes(resolved.ticket_id)[0]
        self.assertEqual(resolution_note.note_text, resolved.resolution)
        self.assertEqual(resolution_note.note_type, "RESOLUTION")
        self.assertEqual(resolution_note.author_label, "Jo")
        self.assertEqual(resolution_note.created_at, resolved.resolved_at)
        self.assertEqual(
            tuple(e.event_type for e in self.repository.list_timeline_events(resolved.ticket_id)),
            ("TICKET_CREATED", "NOTE_ADDED", "STATUS_CHANGED"),
        )

        self.now += timedelta(hours=1)
        closed = self.service.change_status(resolved.ticket_id, new_status="CLOSED")
        self.assertEqual(closed.resolved_at, resolved.resolved_at)
        self.assertEqual(closed.resolution, resolved.resolution)
        self.assertEqual(closed.closed_at, closed.updated_at)
        self.assertNotEqual(closed.closed_at, closed.resolved_at)
        self.assertEqual(len(self.repository.list_notes(closed.ticket_id)), 1)

        self.now += timedelta(days=1)
        reopened = self.service.change_status(closed.ticket_id, new_status="OPEN")
        self.assertIsNone(reopened.resolution)
        self.assertIsNone(reopened.resolved_at)
        self.assertIsNone(reopened.closed_at)
        self.assertEqual(self.repository.get_note(resolution_note.ticket_note_id), resolution_note)

        self.now += timedelta(minutes=10)
        resolved_again = self.service.change_status(
            reopened.ticket_id, new_status="RESOLVED", resolution="Replaced the printer."
        )
        self.assertGreater(resolved_again.resolved_at, resolved.resolved_at)
        notes = self.repository.list_notes(reopened.ticket_id)
        self.assertEqual(tuple(n.note_text for n in notes),
                         (resolved.resolution, "Replaced the printer."))
        history = self.repository.list_status_history(reopened.ticket_id)
        self.assertEqual(tuple(h.new_status for h in history),
                         ("NEW", "RESOLVED", "CLOSED", "OPEN", "RESOLVED"))
        self._assert_integrity()

    def test_resolved_ticket_can_reopen_directly(self) -> None:
        self.service.change_status(
            self.ticket.ticket_id, new_status="RESOLVED", resolution="Fixed."
        )
        ticket = self.service.change_status(self.ticket.ticket_id, new_status="OPEN")
        self.assertIsNone(ticket.resolved_at)
        self.assertIsNone(ticket.resolution)
        self.assertEqual(len(self.repository.list_notes(ticket.ticket_id)), 1)

    def test_reopening_older_tickets_archives_resolution_before_clearing(self) -> None:
        for status in ("RESOLVED", "CLOSED"):
            with self.subTest(status=status):
                legacy = self.repository.create_ticket(
                    ticket_number=f"LEGACY-{status}",
                    subject="Older resolved ticket",
                    status=status,
                    resolution="Previous technician fixed the cable.",
                    resolved_at=self.ticket.created_at,
                    closed_at=self.ticket.created_at if status == "CLOSED" else None,
                    created_at=self.ticket.created_at,
                    updated_at=self.ticket.created_at,
                )
                reopened = self.service.change_status(legacy.ticket_id, new_status="OPEN")
                self.assertIsNone(reopened.resolution)
                self.assertIsNone(reopened.resolved_at)
                self.assertIsNone(reopened.closed_at)
                notes = self.repository.list_notes(legacy.ticket_id)
                self.assertEqual(len(notes), 1)
                self.assertEqual(notes[0].note_text, legacy.resolution)
                self.assertEqual(notes[0].note_type, "RESOLUTION")
                self.assertEqual(notes[0].source, "REOPEN_SNAPSHOT")
                self.assertIsNone(notes[0].author_label)
                events = self.repository.list_timeline_events(legacy.ticket_id)
                self.assertEqual(tuple(e.event_type for e in events),
                                 ("NOTE_ADDED", "STATUS_CHANGED"))
                self.assertEqual(json.loads(events[0].metadata_json), {
                    "ticket_note_id": notes[0].ticket_note_id,
                })
        self._assert_integrity()

    def test_legacy_resolution_snapshot_rolls_back_if_reopening_fails(self) -> None:
        legacy = self.repository.create_ticket(
            ticket_number="LEGACY-ROLLBACK",
            subject="Older resolution",
            status="RESOLVED",
            resolution="Only copy of resolution.",
            resolved_at=self.ticket.created_at,
            created_at=self.ticket.created_at,
            updated_at=self.ticket.created_at,
        )
        self._install_failure_trigger("BEFORE INSERT ON ticket_status_history")
        before = self._snapshot()
        with self.assertRaises(TicketUpdateError):
            self.service.change_status(legacy.ticket_id, new_status="OPEN")
        self.assertEqual(self._snapshot(), before)
        self._assert_integrity()

    def test_invalid_status_inputs_make_no_changes(self) -> None:
        before = self._snapshot()
        invalid = (
            {"new_status": "DONE"}, {"new_status": "open"}, {"new_status": None},
            {"new_status": "RESOLVED"},
            {"new_status": "RESOLVED", "resolution": " \n "},
            {"new_status": "RESOLVED", "resolution": 3},
            {"new_status": "OPEN", "resolution": "ignored text?"},
            {"new_status": "OPEN", "reason": 3},
            {"new_status": "OPEN", "changed_by": False},
        )
        for arguments in invalid:
            with self.subTest(arguments=arguments):
                with self.assertRaises(TicketValidationError):
                    self.service.change_status(self.ticket.ticket_id, **arguments)
                self.assertEqual(self._snapshot(), before)

    def test_no_op_and_invalid_lifecycle_edges_make_no_changes(self) -> None:
        for target in ("NEW", "CLOSED"):
            before = self._snapshot()
            with self.assertRaises(TicketValidationError):
                self.service.change_status(self.ticket.ticket_id, new_status=target)
            self.assertEqual(self._snapshot(), before)

        self.service.change_status(self.ticket.ticket_id, new_status="OPEN")
        before = self._snapshot()
        with self.assertRaises(TicketValidationError):
            self.service.change_status(self.ticket.ticket_id, new_status="NEW")
        self.assertEqual(self._snapshot(), before)

        self.service.change_status(
            self.ticket.ticket_id, new_status="RESOLVED", resolution="Fixed."
        )
        for target in ("IN_PROGRESS", "WAITING", "CANCELLED"):
            before = self._snapshot()
            with self.assertRaises(TicketValidationError):
                self.service.change_status(self.ticket.ticket_id, new_status=target)
            self.assertEqual(self._snapshot(), before)

    def test_cancellation_is_terminal_but_notes_remain_available(self) -> None:
        cancelled = self.service.change_status(self.ticket.ticket_id, new_status="CANCELLED")
        self.assertIsNone(cancelled.resolved_at)
        self.assertIsNone(cancelled.closed_at)
        before = self._snapshot()
        for target in ("NEW", "OPEN", "IN_PROGRESS", "WAITING", "RESOLVED", "CLOSED", "CANCELLED"):
            with self.subTest(target=target):
                arguments = {"new_status": target}
                if target == "RESOLVED":
                    arguments["resolution"] = "Unexpected resolution"
                with self.assertRaises(TicketValidationError):
                    self.service.change_status(cancelled.ticket_id, **arguments)
                self.assertEqual(self._snapshot(), before)
        note = self.service.add_note(cancelled.ticket_id, note_text="Cancellation follow-up")
        self.assertEqual(self.repository.get_note(note.ticket_note_id), note)
        self.assertEqual(self.repository.get_ticket(cancelled.ticket_id).status, "CANCELLED")

    def test_closed_ticket_accepts_notes_without_lifecycle_changes(self) -> None:
        self.service.change_status(
            self.ticket.ticket_id, new_status="RESOLVED", resolution="Fixed."
        )
        closed = self.service.change_status(self.ticket.ticket_id, new_status="CLOSED")
        self.now += timedelta(hours=1)
        self.service.add_note(closed.ticket_id, note_text="Customer confirmed.")
        updated = self.repository.get_ticket(closed.ticket_id)
        self.assertEqual(updated.status, "CLOSED")
        self.assertEqual(updated.resolution, closed.resolution)
        self.assertEqual(updated.resolved_at, closed.resolved_at)
        self.assertEqual(updated.closed_at, closed.closed_at)
        self.assertGreater(updated.updated_at, closed.updated_at)

    def test_note_secondary_write_failures_roll_back_all_changes(self) -> None:
        for trigger_clause in (
            "BEFORE INSERT ON ticket_timeline_events",
            "BEFORE UPDATE ON tickets",
        ):
            with self.subTest(trigger=trigger_clause):
                self._install_failure_trigger(trigger_clause)
                before = self._snapshot()
                with self.assertRaises(TicketUpdateError) as caught:
                    self.service.add_note(self.ticket.ticket_id, note_text="Must roll back")
                self.assertIsInstance(caught.exception.__cause__, sqlite3.IntegrityError)
                self.assertNotIn("injected failure", str(caught.exception))
                self.assertEqual(self._snapshot(), before)
                self._remove_failure_trigger()
                self._assert_integrity()

    def test_resolution_failure_at_each_write_rolls_back_complete_workflow(self) -> None:
        for trigger_clause in (
            "BEFORE INSERT ON ticket_notes",
            "BEFORE INSERT ON ticket_timeline_events WHEN NEW.event_type = 'NOTE_ADDED'",
            "BEFORE UPDATE ON tickets",
            "BEFORE INSERT ON ticket_status_history",
            "BEFORE INSERT ON ticket_timeline_events WHEN NEW.event_type = 'STATUS_CHANGED'",
        ):
            with self.subTest(trigger=trigger_clause):
                self._install_failure_trigger(trigger_clause)
                before = self._snapshot()
                with self.assertRaises(TicketUpdateError) as caught:
                    self.service.change_status(
                        self.ticket.ticket_id,
                        new_status="RESOLVED",
                        resolution="Everything must roll back.",
                    )
                self.assertIsInstance(caught.exception.__cause__, sqlite3.IntegrityError)
                self.assertEqual(self._snapshot(), before)
                self._remove_failure_trigger()
                self._assert_integrity()

    def test_reopen_failure_preserves_resolution_and_closed_timestamps(self) -> None:
        self.service.change_status(
            self.ticket.ticket_id, new_status="RESOLVED", resolution="Fixed."
        )
        self.service.change_status(self.ticket.ticket_id, new_status="CLOSED")
        self._install_failure_trigger("BEFORE INSERT ON ticket_status_history")
        before = self._snapshot()
        with self.assertRaises(TicketUpdateError):
            self.service.change_status(self.ticket.ticket_id, new_status="OPEN")
        self.assertEqual(self._snapshot(), before)
        self._assert_integrity()

    def _snapshot(self) -> tuple:
        with database_connection(self.database_path) as connection:
            return tuple(
                tuple(tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY 1"))
                for table in ("tickets", "ticket_notes", "ticket_status_history", "ticket_timeline_events")
            )

    def _install_failure_trigger(self, clause: str) -> None:
        # Only fixed test-authored SQL clauses reach this helper.
        with database_connection(self.database_path) as connection:
            connection.execute(
                f"CREATE TRIGGER reject_activity {clause} "
                "BEGIN SELECT RAISE(ABORT, 'injected failure'); END"
            )

    def _remove_failure_trigger(self) -> None:
        with database_connection(self.database_path) as connection:
            connection.execute("DROP TRIGGER reject_activity")

    def _assert_integrity(self) -> None:
        with database_connection(self.database_path) as connection:
            results, violations = validate_database_integrity(connection)
        self.assertEqual(results, ("ok",))
        self.assertEqual(violations, ())


if __name__ == "__main__":
    unittest.main()
