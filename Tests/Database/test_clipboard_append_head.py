"""H01-B real SQLite, synthetic exact text, deterministic clocks; no native effects."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import shutil
import sqlite3
import threading
from unittest.mock import patch
from uuid import uuid4

from f7hub.domain.clipboard import (
    AdmittedManualText, ClipboardCaptureCommand, ClipboardItemRef,
    ClipboardPasteError, ClipboardPasteCode as P, ClipboardPersistenceError,
    ClipboardValidationError,
)
from f7hub.domain.clipboard_settings import CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED
from f7hub.infrastructure.database import bootstrap_database, database_connection, open_database, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationApplicationError, MigrationChecksumError
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.repositories.settings_repository import SettingsRepository
from f7hub.services.clipboard_service import ClipboardService
from f7hub.services import clipboard_service as clipboard_service_module
from f7hub.services.settings_service import SettingsService
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT, seed_item
from Tests.Database.test_clipboard_receipts_migration import insert_receipt
from Tests.Database.test_clipboard_persistence import FaultConnection
from Tests.Unit.test_clipboard_capture_contract import SyntheticClock


class AppendHeadMigrationTests(ClipboardDatabaseTestCase):
    def test_fresh_empty_schema_configuration_and_constraints(self):
        with database_connection(self.database_path) as c:
            self.assertEqual(c.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(c.execute('PRAGMA busy_timeout').fetchone()[0], 5000)
            self.assertEqual(c.execute('SELECT count(*) FROM clipboard_append_head').fetchone()[0], 0)
            self.assertEqual([r[1] for r in c.execute('PRAGMA table_info(clipboard_append_head)')],
                             ['singleton_id', 'append_token', 'live_item_id', 'item_revision'])
            token = '12345678-1234-4abc-8def-123456789abc'
            for values in ((0, token, None, 1), (2, token, None, 1),
                           (1, 'z'*36, None, 1), (1, token.upper(), None, 1),
                           (1, token, None, 0), (1, token, None, 1.5),
                           (1, token, 999, 1), (1, token, -1, 1), (1, None, None, 1)):
                with self.subTest(values=values), self.assertRaises(sqlite3.IntegrityError):
                    c.execute('INSERT INTO clipboard_append_head VALUES (?,?,?,?)', values)
            c.execute('INSERT INTO clipboard_append_head VALUES (1,?,NULL,1)', (token,))
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute('INSERT INTO clipboard_append_head VALUES (1,?,NULL,1)', (str(uuid4()),))
            self.assertEqual(validate_database_integrity(c), (('ok',), ()))

    def prior(self):
        directory = self.root/'prior-migrations'
        directory.mkdir()
        for path in (PROJECT_ROOT/'Database/Migrations').glob('*.sql'):
            if int(path.name[:4]) <= 16:
                shutil.copyfile(path, directory/path.name)
        path = self.root/'prior.db'
        bootstrap_database(path, directory)
        return path, directory

    def test_upgrade_preserves_all_prior_records_no_backfill_and_repeat_protection(self):
        path, _ = self.prior()
        with database_connection(path) as c:
            item = seed_item(c)
            insert_receipt(c, item)
            tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            before = {name: tuple(tuple(r) for r in c.execute('SELECT * FROM "'+name+'"')) for name in tables}
        result = bootstrap_database(path, PROJECT_ROOT/'Database/Migrations')
        self.assertEqual(result.migration_result.applied_versions, (17, 18))
        with database_connection(path) as c:
            for name, rows in before.items():
                query = 'SELECT * FROM "'+name+'"'+(' WHERE version<=16' if name=='schema_migrations' else '')
                self.assertEqual(tuple(tuple(r)[:-1] if name == "clipboard_capture_events" else tuple(r)
                                       for r in c.execute(query)), rows, name)
            self.assertEqual(c.execute('SELECT count(*) FROM clipboard_append_head').fetchone()[0], 0)
            self.assertEqual(validate_database_integrity(c), (('ok',), ()))
        self.assertEqual(bootstrap_database(path, PROJECT_ROOT/'Database/Migrations').migration_result.applied_versions, ())

    def test_migration_history_failure_rolls_back_table_and_preserves_history(self):
        path, directory = self.prior()
        shutil.copyfile(PROJECT_ROOT/'Database/Migrations/0017_clipboard_append_head.sql',
                        directory/'0017_clipboard_append_head.sql')
        with database_connection(path) as c:
            c.execute("CREATE TRIGGER fail_head_migration BEFORE INSERT ON schema_migrations WHEN NEW.version=17 BEGIN SELECT RAISE(ABORT,'synthetic'); END")
        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(path, directory)
        with database_connection(path) as c:
            self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='clipboard_append_head'").fetchone())
            self.assertEqual(c.execute('SELECT max(version) FROM schema_migrations').fetchone()[0], 16)
            self.assertEqual(validate_database_integrity(c), (('ok',), ()))

    def test_new_migration_checksum_is_protected(self):
        directory = self.root/'changed'
        shutil.copytree(PROJECT_ROOT/'Database/Migrations', directory)
        with (directory/'0017_clipboard_append_head.sql').open('a') as out:
            out.write('\n-- changed synthetic fixture\n')
        with self.assertRaises(MigrationChecksumError):
            bootstrap_database(self.database_path, directory)


class _PasteFixture(ClipboardDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.clock = SyntheticClock()
        self.repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
        self.settings = SettingsService(SettingsRepository(self.database_path), CLIPBOARD_SETTING_DEFINITIONS)
        self.service = self.new_service()
        snapshot, epoch, _ = self.service.refresh_setup()
        self.service.enable_history_from_setup({WORKFLOW_ENABLED: True},
            expected_revision=snapshot.revision, expected_epoch=epoch)
        self.context = self.service.open_admission_context('synthetic-head')

    def tearDown(self):
        try:
            with database_connection(self.database_path) as c:
                self.assertEqual(validate_database_integrity(c), (('ok',), ()))
        finally:
            super().tearDown()

    def new_service(self):
        return ClipboardService(self.repository, settings=self.settings,
            clock=self.clock.utc, monotonic=self.clock.monotonic)

    def command(self, text='Synthetic ordinary technician note', *, service=None, context=None):
        service = service or self.service
        context = context or self.context
        return ClipboardCaptureCommand(service.new_operation(context), AdmittedManualText(text))

    def capture(self, text='Synthetic ordinary technician note'):
        command = self.command(text)
        return self.service.capture_manual_text(self.context, command)

    def head(self, *, as_of=None):
        return self.repository._read_latest_paste_source(self.repository._read_paste_consent(),
            as_of=as_of or self.clock.utc().isoformat(timespec='milliseconds').replace('+00:00','Z'))

    def prepare(self, **kwargs):
        return self.service.prepare_latest_paste(self.context,
            press_id=kwargs.get('press_id', str(uuid4())), target_token=kwargs.get('target_token', str(uuid4())))

    def consume(self, authorization):
        return self.service.consume_latest_paste(self.context, authorization)

    def deny(self, code, action):
        with self.assertRaises(ClipboardPasteError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def sql(self, sql, parameters=()):
        with database_connection(self.database_path) as c:
            return c.execute(sql, parameters).fetchall()

    def counts(self):
        return tuple(self.sql('SELECT count(*) FROM '+table)[0][0] for table in
            ('clipboard_items','clipboard_capture_events','clipboard_operation_receipts','clipboard_append_head'))


class AppendHeadRepositoryTests(_PasteFixture):
    def test_first_append_consecutive_append_recapture_and_old_replay(self):
        first_command = self.command('Synthetic first exact source')
        first = self.service.capture_manual_text(self.context, first_command)
        head1 = self.head()
        second = self.capture('Synthetic second exact source')
        head2 = self.head()
        self.assertEqual(head1.item_ref, first.live_item_ref)
        self.assertEqual(head2.item_ref, second.live_item_ref)
        self.assertNotEqual(head1.append_token, head2.append_token)
        self.service.capture_manual_text(self.context, first_command)
        self.assertEqual(self.head(), head2)
        third = self.capture('Synthetic first exact source')
        self.assertEqual(third.live_item_ref, first.live_item_ref)
        self.assertEqual(self.head().item_revision, 2)
        self.assertNotEqual(self.head().append_token, head1.append_token)
        self.assertEqual(self.counts(), (2,3,3,1))

    def test_each_required_write_failure_rolls_back_item_event_receipt_and_head(self):
        self.capture()
        before, counts = self.head(), self.counts()
        for table in ('clipboard_items','clipboard_capture_events','clipboard_operation_receipts','clipboard_append_head'):
            with self.subTest(table=table):
                command = self.command('Synthetic rollback candidate')
                with patch('f7hub.repositories.clipboard_repository.open_database',
                           side_effect=lambda path: FaultConnection(open_database(path), fail_table=table)):
                    with self.assertRaises(ClipboardPersistenceError):
                        self.service.capture_manual_text(self.context, command)
                self.assertEqual(self.head(), before)
                self.assertEqual(self.counts(), counts)

    def test_first_head_failure_leaves_no_partial_append(self):
        with patch('f7hub.repositories.clipboard_repository.open_database',
                   side_effect=lambda path: FaultConnection(open_database(path), fail_table='clipboard_append_head')):
            with self.assertRaises(ClipboardPersistenceError):
                self.capture()
        self.assertEqual(self.counts(), (0,0,0,0))
        self.deny(P.EMPTY, self.head)

    def test_head_failure_rolls_back_duplicate_item_revision_and_lifetime(self):
        self.capture()
        before = self.head()
        with patch('f7hub.repositories.clipboard_repository.open_database',
                   side_effect=lambda path: FaultConnection(open_database(path), fail_table='clipboard_append_head')):
            with self.assertRaises(ClipboardPersistenceError):
                self.capture()
        self.assertEqual(self.head(), before)
        self.assertEqual(self.counts(), (1,1,1,1))
        self.assertEqual(self.sql('SELECT captured_total,revision FROM clipboard_items')[0][:], (1,1))

    def test_rejected_capture_does_not_advance_head(self):
        self.capture()
        before = self.head()
        with self.assertRaises(ClipboardPersistenceError):
            self.capture('password=synthetic-credential')
        self.assertEqual(self.head(), before)

    def test_missing_head_does_not_fall_back_to_history(self):
        with database_connection(self.database_path) as c:
            seed_item(c, retention_intent='SAVED', expires_at=None)
        self.deny(P.EMPTY, self.head)

    def test_delete_nulls_reference_and_id_reuse_never_restores_head(self):
        self.capture('Synthetic earlier eligible source')
        latest = self.capture()
        token = self.head().append_token
        self.sql('DELETE FROM clipboard_items WHERE clipboard_item_id=?', (latest.live_item_ref.clipboard_item_id,))
        self.deny(P.SOURCE_UNAVAILABLE, self.head)
        self.assertEqual(self.sql('SELECT append_token,live_item_id FROM clipboard_append_head')[0][:], (token,None))
        with database_connection(self.database_path) as c:
            seed_item(c, item_id=latest.live_item_ref.clipboard_item_id, retention_intent='SAVED', expires_at=None)
        self.deny(P.SOURCE_UNAVAILABLE, self.head)

    def test_expiry_equality_and_saved_retention(self):
        with database_connection(self.database_path) as c:
            older = seed_item(c, raw_text='Synthetic older permanently saved',
                retention_intent='SAVED', expires_at=None)
        self.capture()
        expiry = self.head().expires_at
        self.deny(P.EXPIRED, lambda: self.head(as_of=expiry))
        self.assertEqual(self.repository.get_recent(limit=50, as_of=expiry).rows[0].item_ref,
            ClipboardItemRef(older))
        self.sql("UPDATE clipboard_items SET retention_intent='SAVED',expires_at=NULL,is_pinned=1")
        self.assertIsNone(self.head(as_of=expiry).expires_at)

    def test_invalid_head_revision_and_token_fail_closed(self):
        self.capture()
        self.sql('UPDATE clipboard_append_head SET item_revision=item_revision+1')
        self.deny(P.STALE_SOURCE, self.head)
        with database_connection(self.database_path) as c:
            c.execute('PRAGMA ignore_check_constraints=ON')
            c.execute("UPDATE clipboard_append_head SET item_revision=1,append_token='invalid'")
        self.deny(P.STALE_SOURCE, self.head)
        # Restore only deliberately corrupted synthetic state for final integrity assertion.
        self.sql('UPDATE clipboard_append_head SET append_token=?', (str(uuid4()),))

    def test_database_access_error_is_not_empty(self):
        with patch('f7hub.repositories.clipboard_repository.database_connection', side_effect=sqlite3.OperationalError('private')):
            self.deny(P.UNAVAILABLE, self.head)

    def test_competing_writers_head_follows_committed_order(self):
        other = self.new_service()
        other_context = other.open_admission_context('synthetic-competing')
        # Second request is created earlier, then commits after the first writer.
        second_command = self.command('Synthetic second committed source', service=other, context=other_context)
        first_command = self.command('Synthetic first committed source')
        reserved, release, second_started = threading.Event(), threading.Event(), threading.Event()

        class FirstWriter(FaultConnection):
            def execute(proxy, sql, parameters=()):
                result = proxy.connection.execute(sql, parameters)
                if sql == 'BEGIN IMMEDIATE':
                    reserved.set()
                    if not release.wait(3):
                        raise AssertionError('synthetic release deadline')
                return result

        def first():
            # Patch only first thread's constructor using thread identity.
            return self.service.capture_manual_text(self.context, first_command)

        owner_thread = [None]
        def connection(path):
            raw = open_database(path)
            return FirstWriter(raw) if threading.get_ident() == owner_thread[0] else raw

        def first_entry():
            owner_thread[0] = threading.get_ident()
            return first()

        def second_entry():
            second_started.set()
            return other.capture_manual_text(other_context, second_command)

        with patch('f7hub.repositories.clipboard_repository.open_database', side_effect=connection):
            with ThreadPoolExecutor(max_workers=2) as pool:
                one = pool.submit(first_entry)
                try:
                    self.assertTrue(reserved.wait(3))
                    two = pool.submit(second_entry)
                    self.assertTrue(second_started.wait(3))
                finally:
                    release.set()
                one.result(timeout=5)
                second_result = two.result(timeout=5)
        self.assertEqual(self.head().item_ref, second_result.live_item_ref)
        self.assertEqual(self.counts(), (2,2,2,1))


class LatestPasteServiceTests(_PasteFixture):
    def setUp(self):
        super().setUp()
        self.text = 'Synthetic exact\r\n\t e\u0301 😀 {literal}\n'
        self.capture(self.text)

    def test_success_exact_full_source_content_free_prepare_and_one_use(self):
        before = self.counts()
        authorization = self.prepare()
        self.assertNotIn(self.text, repr(authorization))
        result = self.consume(authorization)
        self.assertEqual(result.source.text, self.text)
        self.assertNotIn(self.text, repr(result))
        self.assertEqual(result.effect_lease_expires_at, '2026-10-15T12:00:01.000Z')
        self.deny(P.REPLAYED, lambda: self.consume(authorization))
        self.assertEqual(self.counts(), before)

    def test_two_consumers_exactly_one_success(self):
        authorization = self.prepare()
        gate = threading.Barrier(2)
        def attempt():
            gate.wait(timeout=3)
            try:
                return self.consume(authorization).source.text
            except ClipboardPasteError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = [f.result(timeout=5) for f in (pool.submit(attempt), pool.submit(attempt))]
        self.assertCountEqual(results, [self.text, P.REPLAYED])

    def test_revocation_before_consume_denies_and_burns_ticket(self):
        authorization = self.prepare()
        self.settings.apply({WORKFLOW_ENABLED:False}, expected_revision=self.settings.refresh().revision)
        self.deny(P.DENIED, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_consent_regrant_cannot_retarget_prepared_ticket(self):
        authorization = self.prepare()
        snapshot, epoch, _ = self.service.refresh_setup()
        self.service.enable_history_from_setup({WORKFLOW_ENABLED:True}, expected_revision=snapshot.revision, expected_epoch=epoch)
        self.deny(P.DENIED, lambda: self.consume(authorization))

    def test_new_capture_before_consume_denies_no_substitution(self):
        authorization = self.prepare()
        self.capture('Synthetic replacement source')
        self.deny(P.STALE_HEAD, lambda: self.consume(authorization))

    def test_same_text_genuine_recapture_also_invalidates(self):
        authorization = self.prepare()
        self.capture(self.text)
        self.deny(P.STALE_HEAD, lambda: self.consume(authorization))

    def test_deleted_before_consume_no_older_fallback(self):
        authorization = self.prepare()
        self.sql('DELETE FROM clipboard_items')
        self.deny(P.SOURCE_UNAVAILABLE, lambda: self.consume(authorization))

    def test_expired_before_consume(self):
        authorization = self.prepare()
        self.clock.advance(7*86400)
        # Generation also expires; a fresh generation still cannot authorize expired source.
        self.deny(P.EXPIRED, lambda: self.consume(authorization))
        self.context = self.service.open_admission_context('synthetic-after-expiry')
        self.deny(P.EXPIRED, self.prepare)

    def test_item_expires_inside_current_generation(self):
        self.sql("UPDATE clipboard_items SET expires_at='2026-10-15T12:00:01.000Z'")
        authorization = self.prepare()
        self.clock.advance(1)
        self.deny(P.EXPIRED, lambda: self.consume(authorization))

    def test_effect_lease_is_also_bounded_by_known_item_expiry(self):
        self.sql("UPDATE clipboard_items SET expires_at='2026-10-15T12:00:00.500Z'")
        result = self.consume(self.prepare())
        self.assertEqual(result.effect_lease_expires_at, '2026-10-15T12:00:00.500Z')

    def test_generation_expiry_and_restart_invalidate_ticket(self):
        authorization = self.prepare()
        self.clock.advance(300)
        self.deny(P.EXPIRED, lambda: self.consume(authorization))
        other = self.new_service()
        other_context = other.open_admission_context('synthetic-restart')
        self.deny(P.REPLAYED, lambda: other.consume_latest_paste(other_context, authorization))

    def test_restart_preserves_durable_head_but_requires_new_authorization(self):
        old = self.prepare()
        head = self.head()
        other = self.new_service()
        context = other.open_admission_context('synthetic-new-owner')
        self.assertEqual(self.head(), head)
        self.deny(P.REPLAYED, lambda: other.consume_latest_paste(context, old))
        new = other.prepare_latest_paste(context, press_id=str(uuid4()), target_token=str(uuid4()))
        self.assertEqual(other.consume_latest_paste(context, new).source.text, self.text)

    def test_privacy_policy_reassessed_on_export(self):
        authorization = self.prepare()
        with patch('f7hub.services.clipboard_service.assess_manual_text', side_effect=RuntimeError('private-source')):
            self.deny(P.UNAVAILABLE, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_changed_source_same_revision_denied(self):
        authorization = self.prepare()
        self.sql("UPDATE clipboard_items SET raw_text='Synthetic altered exact content'")
        self.deny(P.STALE_SOURCE, lambda: self.consume(authorization))

    def test_stored_privacy_ineligible_denied(self):
        authorization = self.prepare()
        with database_connection(self.database_path) as c:
            c.execute('PRAGMA ignore_check_constraints=ON')
            c.execute('UPDATE clipboard_items SET assessment_complete=0')
        self.deny(P.DENIED, lambda: self.consume(authorization))
        self.sql('UPDATE clipboard_items SET assessment_complete=1')

    def test_current_detector_rejects_previously_permitted_source(self):
        self.sql("UPDATE clipboard_items SET raw_text='password=synthetic-credential'")
        self.deny(P.DENIED, self.prepare)

    def test_bad_binding_invalid_token_and_malformed_authorization(self):
        for field, value in (('target_token',str(uuid4())), ('head_token',str(uuid4())),
                             ('item_ref',ClipboardItemRef(999)), ('revision',2)):
            authorization = self.prepare()
            self.deny(P.DENIED, lambda: self.consume(replace(authorization, **{field:value})))
            self.deny(P.REPLAYED, lambda: self.consume(authorization))
        authorization = self.prepare()
        self.deny(P.REPLAYED, lambda: self.consume(replace(authorization, prepared_id=str(uuid4()))))
        self.deny(P.DENIED, lambda: self.consume({'source':'private'}))
        self.assertEqual(self.consume(authorization).source.text, self.text)
        with self.assertRaises(ClipboardValidationError):
            replace(authorization, prepared_id='private malformed input')

    def test_one_active_ticket_and_replayed_press_cannot_mint_another(self):
        press = str(uuid4())
        authorization = self.prepare(press_id=press)
        self.deny(P.BUSY, self.prepare)
        self.consume(authorization)
        self.deny(P.REPLAYED, lambda: self.prepare(press_id=press))

    def test_busy_press_cannot_later_be_upgraded_to_authorization(self):
        authorization = self.prepare()
        denied_press = str(uuid4())
        self.deny(P.BUSY, lambda: self.prepare(press_id=denied_press))
        self.consume(authorization)
        self.deny(P.REPLAYED, lambda: self.prepare(press_id=denied_press))

    def test_capacity_fences_context_before_dropping_used_press_identity(self):
        with patch('f7hub.services.clipboard_service.MAX_GENERATION_OPERATIONS', 2):
            authorization = self.prepare()
            self.deny(P.UNAVAILABLE, self.prepare)
        self.deny(P.EXPIRED, lambda: self.consume(authorization))

    def test_new_explicit_press_can_bind_replaced_head_without_old_busy_ticket(self):
        old = self.prepare()
        self.capture('Synthetic new current source')
        new = self.prepare()
        self.deny(P.REPLAYED, lambda: self.consume(old))
        self.assertEqual(self.consume(new).source.text, 'Synthetic new current source')

    def test_new_explicit_press_observes_revocation_instead_of_busy(self):
        self.prepare()
        self.settings.apply({WORKFLOW_ENABLED:False}, expected_revision=self.settings.refresh().revision)
        self.deny(P.DENIED, self.prepare)
        snapshot, epoch, _ = self.service.refresh_setup()
        self.service.enable_history_from_setup({WORKFLOW_ENABLED:True}, expected_revision=snapshot.revision, expected_epoch=epoch)
        self.assertEqual(self.consume(self.prepare()).source.text, self.text)

    def test_prepare_budget_and_consume_lease_never_extend(self):
        assess = self.service._assess_paste_source
        def slow(head):
            assess(head)
            self.clock.advance(2)
        with patch.object(self.service, '_assess_paste_source', side_effect=slow):
            self.deny(P.EXPIRED, self.prepare)
        authorization = self.prepare()
        with patch.object(self.service, '_assess_paste_source', side_effect=slow):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_final_fence_detects_changes_after_assessment(self):
        original = self.repository._validate_latest_paste
        for change, code in (("UPDATE clipboard_append_head SET append_token='"+str(uuid4())+"'",P.STALE_HEAD),
                             ('DELETE FROM clipboard_items', P.SOURCE_UNAVAILABLE)):
            with self.subTest(code=code):
                if not self.sql('SELECT * FROM clipboard_items'):
                    self.capture()
                authorization = self.prepare()
                def race(*args, **kwargs):
                    self.sql(change)
                    return original(*args, **kwargs)
                with patch.object(self.repository, '_validate_latest_paste', side_effect=race):
                    self.deny(code, lambda: self.consume(authorization))

    def test_final_fence_detects_revocation_after_assessment(self):
        authorization = self.prepare()
        original = self.repository._validate_latest_paste
        def race(*args, **kwargs):
            self.settings.apply({WORKFLOW_ENABLED:False}, expected_revision=self.settings.refresh().revision)
            return original(*args, **kwargs)
        with patch.object(self.repository, '_validate_latest_paste', side_effect=race):
            self.deny(P.DENIED, lambda: self.consume(authorization))

    def test_invalidation_after_final_linearization_does_not_rewrite_authorization(self):
        authorization = self.prepare()
        original = self.repository._validate_latest_paste
        def after(*args, **kwargs):
            head = original(*args, **kwargs)
            self.settings.apply({WORKFLOW_ENABLED:False}, expected_revision=self.settings.refresh().revision)
            self.sql('DELETE FROM clipboard_items')
            return head
        with patch.object(self.repository, '_validate_latest_paste', side_effect=after):
            self.assertEqual(self.consume(authorization).source.text, self.text)
        self.deny(P.DENIED, self.prepare)

    def test_final_snapshot_is_writer_reserved_no_assessment_inside(self):
        authorization = self.prepare()
        queries = []
        real_open = open_database
        def traced(path, **kwargs):
            c = real_open(path, **kwargs)
            c.set_trace_callback(queries.append)
            return c
        with patch('f7hub.infrastructure.database.open_database', side_effect=traced):
            self.consume(authorization)
        start = queries.index('BEGIN IMMEDIATE')
        end = queries.index('COMMIT', start)
        self.assertTrue(any('clipboard_history_consent' in q for q in queries[start:end]))
        self.assertTrue(any('clipboard_append_head' in q for q in queries[start:end]))
        self.assertFalse(any(q.lstrip().startswith(('INSERT','UPDATE','DELETE')) for q in queries))

    def test_database_contention_denies_without_second_export(self):
        authorization = self.prepare()
        # Preserve production's 5000-ms policy; lower only the isolated fixture connection.
        from f7hub.infrastructure import database as db
        real_open = db.open_database
        def bounded(path, **kwargs):
            return real_open(path, **dict(kwargs, busy_timeout_ms=25))
        with database_connection(self.database_path) as blocker:
            blocker.execute('BEGIN IMMEDIATE')
            with patch('f7hub.infrastructure.database.open_database', side_effect=bounded):
                self.deny(P.UNAVAILABLE, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_final_commit_acknowledgment_failure_never_reexports(self):
        for mode in ('before','after'):
            with self.subTest(mode=mode):
                authorization = self.prepare()
                def fault(path, **kwargs):
                    return FaultConnection(open_database(path, **kwargs), commit_mode=mode)
                with patch('f7hub.infrastructure.database.open_database', side_effect=fault):
                    self.deny(P.UNAVAILABLE, lambda: self.consume(authorization))
                self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_waiting_for_final_reservation_cannot_renew_effect_lease(self):
        authorization = self.prepare()
        original = self.repository._validate_latest_paste
        def waited(*args, **kwargs):
            self.clock.advance(1)
            return original(*args, **kwargs)
        with patch.object(self.repository, '_validate_latest_paste', side_effect=waited):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))

    def test_item_expiry_during_final_wait_denies_with_time_left_in_effect_lease(self):
        self.sql("UPDATE clipboard_items SET expires_at='2026-10-15T12:00:00.500Z'")
        authorization = self.prepare()
        original = self.repository._validate_latest_paste
        def waited(*args, **kwargs):
            self.clock.advance(0.6)
            return original(*args, **kwargs)
        with patch.object(self.repository, '_validate_latest_paste', side_effect=waited):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))

    def test_lease_includes_waiting_for_service_serialization(self):
        authorization = self.prepare()
        entered = threading.Event()
        original = self.service._paste_started
        def started():
            value = original()
            entered.set()
            return value
        with patch.object(self.service, '_paste_started', side_effect=started):
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.service._lock:
                    future = pool.submit(self.consume, authorization)
                    self.assertTrue(entered.wait(3))
                    self.clock.advance(1)
                self.deny(P.EXPIRED, lambda: future.result(timeout=3))

    def test_unexpected_final_exception_is_safe_and_ticket_stays_used(self):
        authorization = self.prepare()
        with patch.object(self.repository, '_validate_latest_paste', side_effect=RuntimeError(self.text)):
            with self.assertRaises(ClipboardPasteError) as caught:
                self.consume(authorization)
        self.assertNotIn(self.text, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_missing_consent_and_database_error_are_distinct(self):
        self.sql('DELETE FROM clipboard_history_consent')
        self.deny(P.DENIED, self.prepare)
        with patch('f7hub.repositories.clipboard_repository.database_connection', side_effect=sqlite3.OperationalError('private')):
            self.deny(P.UNAVAILABLE, self.prepare)

    def test_unavailable_composition_never_exports(self):
        service = ClipboardService(self.repository, clock=self.clock.utc, monotonic=self.clock.monotonic)
        context = service.open_admission_context('synthetic-unavailable')
        self.deny(P.DENIED, lambda: service.prepare_latest_paste(context, press_id=str(uuid4()), target_token=str(uuid4())))


class SecurityCorrectionTests(_PasteFixture):
    """Independent-review F1/F2 regressions at the exact bypass/delay boundaries."""

    def setUp(self):
        super().setUp()
        self.older = self.capture('Synthetic older eligible source').live_item_ref
        self.sql("UPDATE clipboard_items SET retention_intent='SAVED',expires_at=NULL")
        self.text = 'Synthetic exact current source\r\n\t e\u0301 😀 {literal}\n' * 12
        self.latest = self.capture(self.text).live_item_ref

    def revoke(self):
        self.settings.apply({WORKFLOW_ENABLED:False}, expected_revision=self.settings.refresh().revision)

    def as_of(self):
        return self.clock.utc().isoformat(timespec='milliseconds').replace('+00:00','Z')

    def construct(self, symbol, *, seconds=0, action=None):
        constructor = getattr(clipboard_service_module, symbol)
        def injected(*args, **kwargs):
            result = constructor(*args, **kwargs)
            self.clock.advance(seconds)
            if action is not None:
                action()
            return result
        return patch.object(clipboard_service_module, symbol, side_effect=injected)

    def test_f1_removed_public_getter_cannot_return_plaintext_after_revocation(self):
        self.revoke()
        with self.assertNoLogs(), self.assertRaises(AttributeError) as caught:
            self.repository.get_append_head(as_of=self.as_of())
        self.assertNotIn(self.text, str(caught.exception))
        self.assertFalse(hasattr(self.service, 'get_append_head'))

    def test_f1_internal_read_and_final_fence_deny_before_loading_revoked_source(self):
        consent, head = self.repository._read_paste_consent(), self.head()
        self.revoke()
        with self.assertNoLogs(), patch('f7hub.repositories.clipboard_repository._append_head') as load:
            self.deny(P.DENIED, lambda: self.repository._read_latest_paste_source(consent, as_of=self.as_of()))
            self.deny(P.DENIED, lambda: self.repository._validate_latest_paste(head, consent, as_of=self.as_of()))
            load.assert_not_called()

    def test_f1_missing_and_forged_snapshots_cannot_bypass_current_consent(self):
        consent = self.repository._read_paste_consent()
        for invalid in (None, object(), replace(consent, consent_epoch=consent.consent_epoch+1),
                        replace(consent, profile_scope='c'*64)):
            with self.subTest(snapshot=type(invalid).__name__):
                self.deny(P.DENIED, lambda: self.repository._read_latest_paste_source(invalid, as_of=self.as_of()))

    def test_f1_application_facing_prepare_and_consume_deny_without_content_or_fallback(self):
        authorization = self.prepare()
        self.revoke()
        with self.assertNoLogs():
            # Consume first so each boundary exercises its own consent denial;
            # a denied prepare would already retire the pending ticket.
            for action in (lambda: self.consume(authorization), self.prepare):
                with self.assertRaises(ClipboardPasteError) as caught:
                    action()
                self.assertEqual(caught.exception.code, P.DENIED)
                self.assertNotIn(self.text, str(caught.exception))
                self.assertNotIn('Synthetic older eligible source', str(caught.exception))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))
        # Existing read-only Recent remains its approved preview projection.
        page = self.service.get_recent()
        self.assertFalse(hasattr(page.rows[0], 'source'))
        self.assertNotIn(self.text, repr(page))
        self.assertEqual(self.sql('SELECT live_item_id FROM clipboard_append_head')[0][0],
                         self.latest.clipboard_item_id)

    def test_f1_authorized_consume_preserves_exact_full_source_once(self):
        authorization = self.prepare()
        result = self.consume(authorization)
        self.assertEqual(result.source.text, self.text)
        self.assertEqual(result.authorization.item_ref, self.latest)
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_prepare_response_and_ticket_construction_past_cutoff_denies_unpublished_ticket(self):
        for symbol in ('ClipboardPasteAuthorization', '_PreparedPaste'):
            press = str(uuid4())
            with self.subTest(constructor=symbol), self.construct(symbol, seconds=2.001):
                self.deny(P.EXPIRED, lambda: self.prepare(press_id=press))
            self.assertIsNone(self.service._prepared_paste)
            self.deny(P.REPLAYED, lambda: self.prepare(press_id=press))
            self.assertEqual(self.consume(self.prepare()).source.text, self.text)

    def test_f2_consume_response_construction_past_lease_denies_and_stays_spent(self):
        authorization = self.prepare()
        with self.construct('ClipboardPasteSource', seconds=1.001):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))
        self.assertIsNone(self.service._prepared_paste)
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_prepare_generation_expires_during_construction(self):
        self.clock.advance(299.5)
        with self.construct('ClipboardPasteAuthorization', seconds=0.5):
            self.deny(P.EXPIRED, self.prepare)
        self.assertIsNone(self.service._prepared_paste)

    def test_f2_consume_generation_expires_during_construction(self):
        authorization = self.prepare()
        self.clock.advance(299.5)
        with self.construct('ClipboardPasteSource', seconds=0.5):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))
        self.assertIsNone(self.service._prepared_paste)
        self.context = self.service.open_admission_context('synthetic-after-generation')
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_prepare_item_expires_during_construction_without_older_fallback(self):
        self.sql("UPDATE clipboard_items SET expires_at='2026-10-15T12:00:00.500Z' WHERE clipboard_item_id=?",
                 (self.latest.clipboard_item_id,))
        with self.construct('ClipboardPasteAuthorization', seconds=0.5):
            self.deny(P.EXPIRED, self.prepare)
        self.assertIsNone(self.service._prepared_paste)
        self.assertEqual(self.service.get_recent().rows[0].item_ref, self.older)

    def test_f2_consume_item_expires_during_construction_without_older_fallback(self):
        self.sql("UPDATE clipboard_items SET expires_at='2026-10-15T12:00:00.500Z' WHERE clipboard_item_id=?",
                 (self.latest.clipboard_item_id,))
        authorization = self.prepare()
        with self.construct('ClipboardPasteSource', seconds=0.5):
            self.deny(P.EXPIRED, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))
        self.assertEqual(self.service.get_recent().rows[0].item_ref, self.older)

    def test_f2_prepare_construction_revocation_precedes_final_authorization(self):
        with self.construct('ClipboardPasteAuthorization', action=self.revoke):
            self.deny(P.DENIED, self.prepare)
        self.assertIsNone(self.service._prepared_paste)

    def test_f2_consume_construction_revocation_precedes_final_authorization(self):
        authorization = self.prepare()
        with self.construct('ClipboardPasteSource', action=self.revoke):
            self.deny(P.DENIED, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_consume_construction_head_change_precedes_final_authorization(self):
        authorization = self.prepare()
        with self.construct('ClipboardPasteSource', action=lambda: self.capture('Synthetic replacement source')):
            self.deny(P.STALE_HEAD, lambda: self.consume(authorization))
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_construction_exception_denies_without_plaintext_and_stays_spent(self):
        authorization = self.prepare()
        with self.assertNoLogs(), patch.object(clipboard_service_module, 'ClipboardPasteSource', side_effect=RuntimeError(self.text)):
            with self.assertRaises(ClipboardPasteError) as caught:
                self.consume(authorization)
        self.assertEqual(caught.exception.code, P.UNAVAILABLE)
        self.assertNotIn(self.text, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.deny(P.REPLAYED, lambda: self.consume(authorization))

    def test_f2_nonexpired_construction_succeeds_without_renewing_effect_expiry(self):
        with self.construct('ClipboardPasteAuthorization', seconds=0.1):
            authorization = self.prepare()
        with self.construct('ClipboardPasteSource', seconds=0.1):
            result = self.consume(authorization)
        self.assertEqual(result.source.text, self.text)
        self.assertEqual(result.effect_lease_expires_at, '2026-10-15T12:00:01.100Z')
