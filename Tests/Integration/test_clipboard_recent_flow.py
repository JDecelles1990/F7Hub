from datetime import datetime, timezone

from f7hub.infrastructure.database import database_connection, validate_database_integrity
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.services.clipboard_service import ClipboardService, ClipboardQueryError
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, FixtureCapture, seed_item


class ClipboardRecentFlowTests(ClipboardDatabaseTestCase):
    def test_migrated_service_repository_flow(self):
        latest = "2026-10-08T11:00:00.000Z"
        with database_connection(self.database_path) as connection:
            repeated = seed_item(connection, raw_text="Synthetic repeated note\nsecond line", captures=(
                FixtureCapture(), FixtureCapture(received_at=latest)))
            seed_item(connection, retention_intent="SAVED", expires_at=None, is_pinned=True)
            seed_item(connection, expires_at="2026-10-08T11:30:00.000Z")
        before = self.database_path.read_bytes()
        service = ClipboardService(ClipboardRepository(self.database_path),
                                   clock=lambda: datetime(2026, 10, 8, 12, tzinfo=timezone.utc))
        page = service.get_recent(limit=1)
        self.assertEqual(page.rows[0].item_ref.clipboard_item_id, repeated)
        self.assertEqual(page.rows[0].last_received_at, latest)
        self.assertEqual(page.rows[0].preview, "Synthetic repeated note second line")
        self.assertTrue(page.has_more)
        all_recent = service.get_recent()
        self.assertEqual(len(all_recent.rows), 2)
        self.assertFalse(all_recent.has_more)
        self.assertEqual(self.database_path.read_bytes(), before)
        with database_connection(self.database_path, read_only=True) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM clipboard_capture_events WHERE clipboard_item_id=?", (repeated,)).fetchone()[0], 2)

    def test_absent_owner_database_is_unavailable_without_creation(self):
        path = self.root / "absent" / "history.db"
        service = ClipboardService(ClipboardRepository(path))
        with self.assertRaises(ClipboardQueryError):
            service.get_recent()
        self.assertFalse(path.parent.exists())
