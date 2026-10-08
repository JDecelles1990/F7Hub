from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import sqlite3
import unittest
from unittest.mock import Mock

from f7hub.domain.clipboard import (
    ClipboardItemRef, ClipboardRecentPage, normalize_preview, ClipboardValidationError,
)
from f7hub.infrastructure.database import database_connection
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.services.clipboard_service import ClipboardService, ClipboardQueryError
from Tests.Database.clipboard_fixtures import AS_OF, ClipboardDatabaseTestCase, seed_item


class ClipboardServiceTests(ClipboardDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.clock = Mock(return_value=datetime(2026, 10, 8, 12, tzinfo=timezone.utc))
        self.service = ClipboardService(ClipboardRepository(self.database_path), clock=self.clock)

    def test_default_limit_and_one_clock_sample(self):
        page = self.service.get_recent()
        self.assertEqual((page.limit, page.as_of, page.rows, page.has_more), (50, AS_OF, (), False))
        self.clock.assert_called_once_with()

    def test_valid_custom_limits(self):
        for limit in (1, 50, 100):
            with self.subTest(limit=limit):
                self.assertEqual(self.service.get_recent(limit=limit).limit, limit)
        self.assertEqual(self.clock.call_count, 3)

    def test_invalid_limit_never_samples_clock_or_repository(self):
        repository = Mock()
        service = ClipboardService(repository, clock=self.clock)
        for limit in (True, False, 0, -1, 101, None, 5.0, "50", [], {}):
            with self.subTest(kind=type(limit).__name__), self.assertRaises(ClipboardValidationError):
                service.get_recent(limit=limit)
        self.clock.assert_not_called()
        repository.get_recent.assert_not_called()

    def test_utc_conversion_and_millisecond_precision(self):
        repository = Mock()
        expected = "2026-10-08T12:00:00.123Z"
        repository.get_recent.return_value = ClipboardRecentPage((), False, 50, expected)
        clock = Mock(return_value=datetime(2026, 10, 8, 8, 0, 0, 123456, timezone(timedelta(hours=-4))))
        page = ClipboardService(repository, clock=clock).get_recent()
        self.assertEqual(page.as_of, expected)
        repository.get_recent.assert_called_once_with(limit=50, as_of=expected)
        clock.assert_called_once_with()

    def test_clock_failure_is_safe_query_error(self):
        for clock in (lambda: datetime(2026, 10, 8), lambda: None, Mock(side_effect=RuntimeError("synthetic internals"))):
            with self.subTest(clock_type=type(clock).__name__), self.assertRaises(ClipboardQueryError) as caught:
                ClipboardService(Mock(), clock=clock).get_recent()
            self.assertNotIn("synthetic internals", str(caught.exception))

    def test_repository_failure_is_not_empty_and_is_safe(self):
        for failure in (sqlite3.OperationalError("synthetic SQL/raw/path"), OSError("synthetic SQL/raw/path"), RuntimeError("synthetic SQL/raw/path")):
            repository = Mock()
            repository.get_recent.side_effect = failure
            with self.subTest(kind=type(failure).__name__), self.assertRaises(ClipboardQueryError) as caught:
                ClipboardService(repository, clock=self.clock).get_recent()
            self.assertNotIn("synthetic SQL/raw/path", str(caught.exception))
            self.assertTrue(caught.exception.__suppress_context__)

    def test_wrong_repository_contract_is_failure(self):
        for value in ((), None, ClipboardRecentPage((), False, 1, AS_OF)):
            repository = Mock()
            repository.get_recent.return_value = value
            with self.assertRaises(ClipboardQueryError):
                ClipboardService(repository, clock=self.clock).get_recent()

    def test_success_is_deeply_immutable_and_no_write(self):
        with database_connection(self.database_path) as connection:
            seed_item(connection)
        before = self.database_path.read_bytes()
        page = self.service.get_recent()
        self.assertEqual(before, self.database_path.read_bytes())
        self.assertIsInstance(page.rows, tuple)
        for obj, field, value in ((page, "limit", 1), (page.rows[0], "preview", "other"),
                                   (page.rows[0].item_ref, "clipboard_item_id", 9)):
            with self.assertRaises(FrozenInstanceError):
                setattr(obj, field, value)
        for name in ("capture", "save", "pin", "delete", "insert"):
            self.assertFalse(hasattr(self.service, name))

    def test_value_objects_reject_invalid_identity_and_unbounded_page(self):
        for identity in (True, 0, -1, 2**63):
            with self.assertRaises(ClipboardValidationError):
                ClipboardItemRef(identity)
        with self.assertRaises(ClipboardValidationError):
            ClipboardRecentPage([], False, 50, AS_OF)


class ClipboardPreviewTests(unittest.TestCase):
    def test_plain_markup_url_and_unicode_remain_literal(self):
        for text in ("Short synthetic note", "<script>synthetic()</script>", "https://example.invalid/synthetic", "café e\u0301 😀"):
            with self.subTest(text=text):
                self.assertEqual(normalize_preview(text), (text, False))

    def test_scalar_truncation_boundaries(self):
        for count in (0, 1, 239, 240, 241):
            with self.subTest(count=count):
                self.assertEqual(normalize_preview("😀" * count), ("😀" * min(count, 240), count > 240))

    def test_line_control_format_and_bidi_replacement(self):
        unsafe = "\r\n\t\0\x7f\u0085\u2028\u2029\u200b\u200d\u202e\u2066\u2069"
        self.assertEqual(normalize_preview("a" + unsafe + "z"), ("a" + " " * len(unsafe) + "z", False))

    def test_invalid_or_unbounded_preview_rejected(self):
        for text in (None, b"text", "x" * 242, "\udfff"):
            with self.assertRaises(ClipboardValidationError):
                normalize_preview(text)
