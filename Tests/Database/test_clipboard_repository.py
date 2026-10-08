from contextlib import contextmanager
import sqlite3
from unittest.mock import patch

from f7hub.domain.clipboard import ClipboardValidationError
from f7hub.infrastructure.database import database_connection
from f7hub.repositories.clipboard_repository import ClipboardRepository, ClipboardRepositoryError, _RECENT_SQL
from Tests.Database.clipboard_fixtures import (
    AS_OF, RECEIVED, ClipboardDatabaseTestCase, FixtureCapture, seed_item,
)


class ClipboardRepositoryTests(ClipboardDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.repository = ClipboardRepository(self.database_path)

    def test_empty_database(self):
        page = self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual((page.rows, page.has_more, page.limit, page.as_of), ((), False, 50, AS_OF))

    def test_bounds_sentinel_and_id_ties(self):
        with database_connection(self.database_path) as connection:
            for identity in range(1, 102):
                seed_item(connection, item_id=identity)
        for limit in (1, 50, 100):
            with self.subTest(limit=limit):
                page = self.repository.get_recent(limit=limit, as_of=AS_OF)
                self.assertEqual(tuple(row.item_ref.clipboard_item_id for row in page.rows), tuple(range(101, 101-limit, -1)))
                self.assertTrue(page.has_more)
                self.assertEqual(len(page.rows), limit)

    def test_exact_limit_has_no_more(self):
        with database_connection(self.database_path) as connection:
            for _ in range(50):
                seed_item(connection)
        page = self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual(len(page.rows), 50)
        self.assertFalse(page.has_more)

    def test_invalid_limit_rejected_before_open(self):
        with patch("f7hub.repositories.clipboard_repository.database_connection") as opened:
            for limit in (0, -1, 101, True, False, 1.0, "50", None, [], {}):
                with self.subTest(kind=type(limit).__name__), self.assertRaises(ClipboardValidationError):
                    self.repository.get_recent(limit=limit, as_of=AS_OF)
            opened.assert_not_called()

    def test_invalid_as_of_rejected_before_open(self):
        with patch("f7hub.repositories.clipboard_repository.database_connection") as opened:
            for instant in (None, "private argument", "2026-02-30T12:00:00.000Z", "2026-10-08T12:00:00Z", AS_OF + "tail"):
                with self.subTest(kind=type(instant).__name__), self.assertRaises(ClipboardValidationError):
                    self.repository.get_recent(limit=50, as_of=instant)
            opened.assert_not_called()

    def test_receipt_order_and_one_item_for_multiple_events(self):
        later = "2026-10-08T11:00:00.000Z"
        with database_connection(self.database_path) as connection:
            seed_item(connection, item_id=90)
            seed_item(connection, item_id=1, captures=(FixtureCapture(), FixtureCapture(
                received_at=later, observed_at="2020-01-01T00:00:00.000Z")))
        page = self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual(tuple(row.item_ref.clipboard_item_id for row in page.rows), (1, 90))
        self.assertEqual(page.rows[0].last_received_at, later)
        with database_connection(self.database_path) as connection:
            self.assertEqual(connection.execute("SELECT captured_total FROM clipboard_items WHERE clipboard_item_id=1").fetchone()[0], 2)

    def test_lifetime_summary_survives_fixture_history_pruning(self):
        with database_connection(self.database_path) as connection:
            identity = seed_item(connection)
            connection.execute("DELETE FROM clipboard_capture_events WHERE clipboard_item_id=?", (identity,))
        row = self.repository.get_recent(limit=1, as_of=AS_OF).rows[0]
        self.assertEqual(row.last_received_at, RECEIVED)

    def test_retention_eligibility(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection, item_id=1, expires_at="2026-10-08T11:00:00.000Z")
            seed_item(connection, item_id=2, expires_at=AS_OF)
            seed_item(connection, item_id=3)
            seed_item(connection, item_id=4, retention_intent="SAVED", expires_at=None)
            seed_item(connection, item_id=5, retention_intent="SAVED", expires_at=None, is_pinned=True)
        page = self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual(tuple(row.item_ref.clipboard_item_id for row in page.rows), (5, 4, 3))
        self.assertTrue(page.rows[0].is_pinned)

    def test_privacy_predicate_excludes_ineligible_corrupted_rows(self):
        with database_connection(self.database_path) as connection:
            for identity in range(1, 5):
                seed_item(connection, item_id=identity)
            # Deliberately corrupt isolated fixtures to test the read boundary,
            # independently of migration CHECK constraints.
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute("UPDATE clipboard_items SET sensitivity='NEEDS_REVIEW' WHERE clipboard_item_id=1")
            connection.execute("UPDATE clipboard_items SET sensitivity='POSSIBLE_SECRET' WHERE clipboard_item_id=2")
            connection.execute("UPDATE clipboard_items SET assessment_complete=0 WHERE clipboard_item_id=3")
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        page = self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual(tuple(row.item_ref.clipboard_item_id for row in page.rows), (4,))

    def test_projection_excludes_raw_and_normalizes_excerpt(self):
        raw = "<script>synthetic</script>\r\n\u202e" + "é" * 260 + "SYNTHETIC_OUTSIDE_PREVIEW"
        with database_connection(self.database_path) as connection:
            seed_item(connection, raw_text=raw)
        row = self.repository.get_recent(limit=1, as_of=AS_OF).rows[0]
        self.assertEqual(len(row.preview), 240)
        self.assertTrue(row.preview_truncated)
        self.assertTrue(row.preview.startswith("<script>synthetic</script>   "))
        self.assertNotIn("SYNTHETIC_OUTSIDE_PREVIEW", repr(row))
        self.assertIsNone(row.kind)
        for name in ("raw_text", "content_hash", "events", "source_class", "source_title", "entities", "tags", "holds"):
            self.assertFalse(hasattr(row, name))
        with database_connection(self.database_path) as connection:
            self.assertEqual(connection.execute("SELECT raw_text FROM clipboard_items").fetchone()[0], raw)

    def test_missing_path_does_not_create_storage(self):
        path = self.root / "missing" / "absent.db"
        with self.assertRaises(ClipboardRepositoryError) as caught:
            ClipboardRepository(path).get_recent(limit=1, as_of=AS_OF)
        self.assertFalse(path.parent.exists())
        self.assertNotIn(str(path), str(caught.exception))

    def test_wrong_schema_is_safe_failure(self):
        path = self.root / "wrong.db"
        with database_connection(path) as connection:
            connection.execute("CREATE TABLE unrelated (value TEXT)")
        with self.assertRaises(ClipboardRepositoryError) as caught:
            ClipboardRepository(path).get_recent(limit=1, as_of=AS_OF)
        self.assertNotIn("clipboard_items", str(caught.exception))

    def test_read_uses_readonly_connection_and_select_only(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection)
            before_rows = tuple(tuple(row) for row in connection.execute("SELECT * FROM clipboard_items"))
            before_events = tuple(tuple(row) for row in connection.execute("SELECT * FROM clipboard_capture_events"))
        before = self.database_path.read_bytes()
        statements = []
        @contextmanager
        def instrumented(path, *, read_only):
            self.assertTrue(read_only)
            with database_connection(path, read_only=read_only) as connection:
                connection.set_trace_callback(statements.append)
                yield connection
        with patch("f7hub.repositories.clipboard_repository.database_connection", instrumented):
            self.repository.get_recent(limit=1, as_of=AS_OF)
        self.assertEqual(len(statements), 1)
        self.assertTrue(statements[0].lstrip().startswith("SELECT"))
        self.assertIn("LIMIT 2", statements[0])
        self.assertNotIn("SELECT *", statements[0])
        self.assertEqual(before, self.database_path.read_bytes())
        with database_connection(self.database_path) as connection:
            self.assertEqual(before_rows, tuple(tuple(row) for row in connection.execute("SELECT * FROM clipboard_items")))
            self.assertEqual(before_events, tuple(tuple(row) for row in connection.execute("SELECT * FROM clipboard_capture_events")))

    def test_locked_database_failure_is_bounded_and_no_write(self):
        @contextmanager
        def short_timeout(path, *, read_only):
            with database_connection(path, read_only=read_only, busy_timeout_ms=50) as connection:
                yield connection
        with database_connection(self.database_path) as writer:
            writer.execute("BEGIN EXCLUSIVE")
            with patch("f7hub.repositories.clipboard_repository.database_connection", short_timeout):
                with self.assertRaises(ClipboardRepositoryError):
                    self.repository.get_recent(limit=1, as_of=AS_OF)
            writer.rollback()
        self.assertEqual(self.repository.get_recent(limit=1, as_of=AS_OF).rows, ())

    def test_malformed_projection_fails_without_partial_rows(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection, retention_intent="SAVED", expires_at=None)
            # SQL enforces timestamp shape; actual calendar validity is checked at mapping.
            connection.execute("UPDATE clipboard_items SET last_received_at=?", ("2026-99-08T10:00:00.000Z",))
        before = self.database_path.read_bytes()
        with self.assertRaises(ClipboardRepositoryError):
            self.repository.get_recent(limit=50, as_of=AS_OF)
        self.assertEqual(before, self.database_path.read_bytes())

    def test_index_used_without_temporary_sort(self):
        with database_connection(self.database_path, read_only=True) as connection:
            plan = " ".join(row[3] for row in connection.execute("EXPLAIN QUERY PLAN " + _RECENT_SQL, (AS_OF, 51)))
        self.assertIn("idx_clipboard_items_recent", plan)
        self.assertNotIn("TEMP B-TREE", plan)
