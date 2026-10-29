"""CP02-S4 isolated SQLite and real privacy/consent/service validation."""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from contextlib import contextmanager
from Tests.Database.test_clipboard_consent import _ConsentFixture
from Tests.Database.clipboard_fixtures import seed_item, FixtureCapture, AS_OF
from f7hub.domain.clipboard import ClipboardCopyItem, ClipboardItemRef, ClipboardCopyError
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED
from f7hub.infrastructure.database import database_connection, validate_database_integrity
import f7hub.repositories.clipboard_repository as repository_module


class SelectedCopyDatabaseTests(_ConsentFixture):
    def setUp(self):
        super().setUp()
        self.service._clock = lambda: datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
        self.grant()
        self.delivered = []

    def seed(self, text="Synthetic ordinary technician note", **kwargs):
        with database_connection(self.database_path) as c:
            item = seed_item(c, raw_text=text, **kwargs)
        return ClipboardCopyItem(ClipboardItemRef(item), kwargs.get("revision", 1))

    def deliver(self, text, guard):
        guard(); self.delivered.append(text); return "WRITTEN"

    def deny(self, selection, code, delivery=None):
        with self.assertNoLogs(level="DEBUG"), self.assertRaises(ClipboardCopyError) as caught:
            self.service.copy_selected(selection, delivery or self.deliver)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.clipboard, "UNCHANGED")
        self.assertEqual(self.delivered, [])

    def test_complete_text_order_unicode_and_one_item_multiple_events(self):
        a = self.seed("Synthetic first\r\n  Résumé 😀 " + "q" * 400,
                      captures=(FixtureCapture(), FixtureCapture()))
        b = self.seed("Synthetic second\n東京")
        self.assertEqual(self.service.copy_selected((b, a), self.deliver), "WRITTEN")
        self.assertEqual(self.delivered, ["Synthetic second\n東京\n\nSynthetic first\r\n  Résumé 😀 " + "q" * 400])
        self.assertEqual(self.counts(), (2, 3, 0))

    def test_one_invalid_member_prevents_all_delivery(self):
        item = self.seed()
        self.deny((item, ClipboardCopyItem(ClipboardItemRef(999), 1)), "STALE_SELECTION")

    def test_revised_item_rejected(self):
        item = self.seed()
        self.deny((ClipboardCopyItem(item.item_ref, 2),), "STALE_SELECTION")

    def test_expired_member_rejected(self):
        item = self.seed(expires_at=AS_OF)
        self.deny((item,), "EXPIRED")

    def test_saved_item_without_expiry_allowed(self):
        item = self.seed(retention_intent="SAVED", expires_at=None)
        self.service.copy_selected((item,), self.deliver)
        self.assertEqual(len(self.delivered), 1)

    def test_privacy_reassessment_rejects_stored_sensitive_text(self):
        item = self.seed("password=synthetic-only")
        self.deny((item,), "DENIED")

    def test_consent_revoked_before_request(self):
        item = self.seed()
        snap = self.settings.refresh()
        self.settings.apply({WORKFLOW_ENABLED: False}, expected_revision=snap.revision)
        self.deny((item,), "DENIED")

    def test_revocation_during_native_wait_rejects_before_write(self):
        item = self.seed()
        def delivery(text, guard):
            snap = self.settings.refresh()
            self.settings.apply({WORKFLOW_ENABLED: False}, expected_revision=snap.revision)
            return self.deliver(text, guard)
        self.deny((item,), "DENIED", delivery)

    def test_deletion_revision_or_content_change_during_wait_rejected(self):
        for sql in ("DELETE FROM clipboard_items", "UPDATE clipboard_items SET revision=revision+1",
                    "UPDATE clipboard_items SET raw_text='Synthetic changed source'"):
            item = self.seed()
            def delivery(text, guard):
                with database_connection(self.database_path) as c: c.execute(sql)
                return self.deliver(text, guard)
            self.deny((item,), "STALE_SELECTION", delivery)

    def test_oversize_combination_never_delivered(self):
        a = self.seed("x" * 40000); b = self.seed("y" * 40000)
        self.deny((a, b), "TOO_LARGE")

    def test_budget_includes_native_wait_and_expiry_during_wait(self):
        item = self.seed()
        ticks = [100.0]; self.service._monotonic = lambda: ticks[0]
        def delivery(text, guard):
            ticks[0] += 3
            return self.deliver(text, guard)
        self.deny((item,), "TIMEOUT", delivery)

    def test_final_expiry_and_clock_reversal(self):
        item = self.seed(expires_at="2026-10-08T12:00:01.000Z")
        for instant, code in ((datetime(2026,10,8,12,0,1,tzinfo=timezone.utc),"EXPIRED"),
                              (datetime(2026,10,7,12,tzinfo=timezone.utc),"TIMEOUT")):
            self.service._clock=lambda:datetime(2026,10,8,12,tzinfo=timezone.utc)
            def delivery(text, guard):
                self.service._clock=lambda:instant
                return self.deliver(text,guard)
            self.deny((item,),code,delivery)

    def test_read_snapshot_remains_consistent_under_concurrent_writer(self):
        item = self.seed("Synthetic original")
        with database_connection(self.database_path) as c: c.execute("PRAGMA journal_mode=WAL")
        fired = []
        @contextmanager
        def observed(*args, **kwargs):
            with database_connection(*args, **kwargs) as c:
                def trace(sql):
                    if "WHERE clipboard_item_id IN" in sql and not fired:
                        fired.append(True)
                        with database_connection(self.database_path) as other:
                            other.execute("UPDATE clipboard_items SET raw_text='Synthetic newer', revision=2")
                c.set_trace_callback(trace)
                yield c
        with patch.object(repository_module, "database_connection", observed):
            snapshot = self.repository._read_copy_selection((item,), as_of=AS_OF)
        self.assertEqual(snapshot[1][0][0], "Synthetic original")
        self.assertEqual(fired, [True])
        self.deny((item,), "STALE_SELECTION")

    def test_no_database_mutations_and_integrity(self):
        item = self.seed()
        with database_connection(self.database_path, read_only=True) as c: before=tuple(c.iterdump())
        self.service.copy_selected((item,), self.deliver)
        with database_connection(self.database_path, read_only=True) as c:
            self.assertEqual(tuple(c.iterdump()), before)
            self.assertEqual(validate_database_integrity(c), (("ok",), ()))
            self.assertEqual(c.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(c.execute("PRAGMA busy_timeout").fetchone()[0], 5000)

    def test_retired_guard_and_parallel_selected_copy_cannot_write(self):
        item = self.seed(); retained = []
        def delivery(text, guard):
            retained.append(guard)
            self.deny((item,), "BUSY")
            return self.deliver(text, guard)
        self.service.copy_selected((item,), delivery)
        self.assertEqual(len(self.delivered), 1)
        with self.assertRaisesRegex(ClipboardCopyError, "STALE_SELECTION"): retained[0]()

    def test_unavailable_database_and_invalid_selection_are_content_free(self):
        item = self.seed(); delivery = Mock()
        with patch.object(self.repository, "_read_copy_selection", side_effect=RuntimeError("Synthetic private detail")):
            self.deny((item,), "UNAVAILABLE", delivery)
        self.assertFalse(delivery.called)
        self.deny((), "INVALID_SELECTION")

    def test_small_clock_rollback_rejects_before_effect(self):
        item = self.seed()
        def delivery(text, guard):
            self.service._clock = lambda: datetime(2026, 10, 8, 11, 59, 59, tzinfo=timezone.utc)
            return self.deliver(text, guard)
        self.deny((item,), "TIMEOUT", delivery)

    def test_unknown_delivery_failure_or_outcome_preserves_uncertainty(self):
        item = self.seed()
        for fail in (True, False):
            def delivery(text, guard):
                guard()
                if fail: raise RuntimeError("Synthetic private detail")
                return None
            with self.assertRaises(ClipboardCopyError) as caught:
                self.service.copy_selected((item,), delivery)
            self.assertEqual((caught.exception.code, caught.exception.clipboard), ("UNAVAILABLE", "MAY_HAVE_CHANGED"))

    def _r1_clock(self, offsets):
        base = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
        self.service._clock = Mock(side_effect=[base + timedelta(seconds=x) for x in offsets])
        self.service._monotonic = lambda: 100.0

    def test_r1_original_expiry_sample_is_not_discarded(self):
        item = self.seed(expires_at="2026-10-08T12:00:00.800Z")
        self._r1_clock([0, .1, .2, .9, .3, .3, .3, .3])
        writer = Mock(return_value="WRITTEN")
        self.deny((item,), "EXPIRED", writer)
        writer.assert_not_called()
        # The expired post-read sample decides; the later rollback is never used.
        self.assertEqual(self.service._clock.call_count, 4)

    def test_r1_increasing_and_equal_samples_allow_copy(self):
        item = self.seed(expires_at="2026-10-08T12:00:01.000Z")
        for samples in ([0, .1, .2, .3, .4, .5], [0] * 6):
            with self.subTest(samples=samples):
                self.delivered.clear()
                self._r1_clock(samples)
                self.assertEqual(self.service.copy_selected((item,), self.deliver), "WRITTEN")
                self.assertEqual(len(self.delivered), 1)

    def test_r1_rollback_at_each_guard_boundary_preserves_effect_state(self):
        from Tests.Unit.test_windows_latest_paste import PasteNativeBoundaryTests
        from f7hub.infrastructure.windows_selected_copy import write_selected_text
        item = self.seed("Synthetic note", expires_at="2026-10-08T12:00:02.000Z")
        # Initial read; service, adapter, writer and three readback guards. Every
        # rollback after boundary 1 stays later than the request's initial time.
        for boundary in range(1, 14):
            with self.subTest(boundary=boundary):
                samples = [i * .05 for i in range(14)]
                samples[boundary] = samples[boundary - 1] - .025
                self._r1_clock(samples)
                fixture = PasteNativeBoundaryTests()
                fixture.setUp()  # All native methods and memmove are synthetic.
                try:
                    api = fixture.api
                    api.write_text = Mock(wraps=api.write_text)
                    with self.assertRaises(ClipboardCopyError) as caught:
                        self.service.copy_selected((item,),
                            lambda text, guard: write_selected_text(text, 123, guard, api=api))
                    self.assertEqual(caught.exception.code, "TIMEOUT")
                    self.assertEqual(caught.exception.clipboard,
                                     "UNCHANGED" if boundary <= 7 else "WRITTEN")
                    if boundary <= 5:
                        api.write_text.assert_not_called()
                    if boundary <= 7:
                        api.user.EmptyClipboard.assert_not_called()
                        api.user.SetClipboardData.assert_not_called()
                    else:
                        api.write_text.assert_called_once()
                        api.user.EmptyClipboard.assert_called_once()
                finally:
                    fixture.doCleanups()

    def test_r1_expiry_during_native_wait_prevents_replacement(self):
        from Tests.Unit.test_windows_latest_paste import PasteNativeBoundaryTests
        from f7hub.infrastructure.windows_selected_copy import write_selected_text
        item = self.seed("Synthetic note", expires_at="2026-10-08T12:00:00.800Z")
        self._r1_clock([0, .1, .2, .3, .4, .5, .7, .8])
        fixture = PasteNativeBoundaryTests()
        fixture.setUp()
        try:
            api = fixture.api
            self.deny((item,), "EXPIRED",
                      lambda text, guard: write_selected_text(text, 123, guard, api=api))
            api.user.OpenClipboard.assert_called_once_with(123)
            api.user.EmptyClipboard.assert_not_called()
            api.user.SetClipboardData.assert_not_called()
            api.user.CloseClipboard.assert_called_once()
            self.assertEqual(api.kernel.GlobalFree.call_count, 5)
        finally:
            fixture.doCleanups()

    def test_r1_all_items_share_the_post_wait_expiry_timestamp(self):
        early = self.seed("Synthetic early", expires_at="2026-10-08T12:00:00.400Z")
        later = self.seed("Synthetic later", expires_at="2026-10-08T12:00:00.800Z")
        for selection in ((early, later), (later, early)):
            with self.subTest(order=selection):
                self._r1_clock([0, .1, .2, .6, .3])
                writer = Mock(return_value="WRITTEN")
                self.deny(selection, "EXPIRED", writer)
                writer.assert_not_called()
                self.assertEqual(self.service._clock.call_count, 4)

    def test_r1_exact_expiry_boundary_prevents_delivery(self):
        item = self.seed(expires_at="2026-10-08T12:00:00.800Z")
        self._r1_clock([0, .1, .2, .8])
        writer = Mock(return_value="WRITTEN")
        self.deny((item,), "EXPIRED", writer)
        writer.assert_not_called()
