"""Synthetic S05 consent migration and admission contracts."""

import shutil
import sqlite3
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT
from f7hub.domain.clipboard import AdmittedManualText, ClipboardCaptureCommand, ClipboardAdmissionBinding, ClipboardPrivacyPolicy, ClipboardPersistenceError, ReplayDisposition
from f7hub.domain.clipboard_settings import CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_TITLE_ENABLED
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.repositories.settings_repository import SettingsRepository, SettingsConflictError, SettingsPersistenceError, SettingsUncertainError
from f7hub.services.settings_service import SettingsService
from f7hub.services.clipboard_service import ClipboardService


def grant_synthetic_consent(path):
    """Explicit test-only owner setup for the historical D02 synthetic authority."""
    settings = SettingsService(SettingsRepository(path), CLIPBOARD_SETTING_DEFINITIONS)
    service = ClipboardService(ClipboardRepository(path, profile_scope='b'*64), settings=settings)
    snapshot, epoch, _ = service.refresh_setup()
    service.enable_history_from_setup({WORKFLOW_ENABLED: True}, expected_revision=snapshot.revision, expected_epoch=epoch)


class ClipboardConsentMigrationTests(ClipboardDatabaseTestCase):
    def test_empty_evidence_and_integrity(self):
        with database_connection(self.database_path) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM clipboard_history_consent').fetchone()[0], 0)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            self.assertEqual(connection.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(connection.execute('PRAGMA busy_timeout').fetchone()[0], 5000)
            columns = {r[1] for r in connection.execute('PRAGMA table_info(clipboard_history_consent)')}
            self.assertFalse(columns & {'raw_text', 'preview', 'hash', 'credentials'})


class _ConsentFixture(ClipboardDatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.repository = ClipboardRepository(self.database_path, profile_scope='b'*64)
        self.settings = SettingsService(SettingsRepository(self.database_path), CLIPBOARD_SETTING_DEFINITIONS)
        self.service = ClipboardService(self.repository, settings=self.settings)

    def grant(self):
        snapshot, epoch, _ = self.service.refresh_setup()
        return self.service.enable_history_from_setup({WORKFLOW_ENABLED: True},
            expected_revision=snapshot.revision, expected_epoch=epoch)

    def command(self, text='Synthetic ordinary technician note'):
        context = self.service.open_admission_context('synthetic-consent')
        return context, ClipboardCaptureCommand(self.service.new_operation(context), AdmittedManualText(text))

    def counts(self):
        with database_connection(self.database_path, read_only=True) as c:
            self.assertEqual(validate_database_integrity(c), (("ok",), ()))
            return tuple(c.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in
                ('clipboard_items','clipboard_capture_events','clipboard_operation_receipts'))


class ClipboardConsentTests(_ConsentFixture):
    def test_generic_enabled_then_restart_still_denied(self):
        self.settings.apply({WORKFLOW_ENABLED: True}, expected_revision=0)
        self.assertIsNone(self.repository._prepare_consent())
        context, command = self.command()
        with self.assertRaises(ClipboardPersistenceError):
            self.service.capture_manual_text(context, command)
        self.assertEqual(self.counts(), (0,0,0))

    def test_explicit_grant_restart_and_consent_only_cas(self):
        self.grant()
        first = self.repository._prepare_consent()
        restarted = ClipboardService(ClipboardRepository(self.database_path, profile_scope='b'*64), settings=self.settings)
        self.assertTrue(restarted.refresh_setup()[2])
        self.assertEqual(first, self.repository._prepare_consent())
        self.service.enable_history_from_setup({WORKFLOW_ENABLED: True}, expected_revision=1, expected_epoch=1)
        with self.assertRaises(SettingsConflictError):
            self.service.enable_history_from_setup({WORKFLOW_ENABLED: True}, expected_revision=1, expected_epoch=1)

    def test_disable_generic_reenable_then_explicit_epoch(self):
        self.grant()
        first = self.repository._prepare_consent()
        self.settings.apply({WORKFLOW_ENABLED: False}, expected_revision=1)
        self.assertIsNone(self.repository._prepare_consent())
        self.settings.apply({WORKFLOW_ENABLED: True}, expected_revision=2)
        self.assertIsNone(self.repository._prepare_consent())
        self.grant()
        final = self.repository._prepare_consent()
        self.assertEqual(final.database_instance_id, first.database_instance_id)
        self.assertEqual(final.consent_epoch, 4)

    def test_reset_revokes_without_deleting_history(self):
        self.grant()
        context, command = self.command()
        self.service.capture_manual_text(context, command)
        self.settings.reset([WORKFLOW_ENABLED], expected_revision=1)
        self.assertIsNone(self.repository._prepare_consent())
        self.assertEqual(self.counts(), (1,1,1))

    def test_stale_settings_revision_and_revocation_final_fence(self):
        self.grant()
        prepared = self.repository._prepare_consent()
        context, command = self.command()
        binding = ClipboardAdmissionBinding(command, self.repository.database_scope)
        policy = ClipboardPrivacyPolicy('clipboard_local_rules','1','clipboard_history_consent_v1','PERMITTED',True,True)
        self.settings.apply({SOURCE_TITLE_ENABLED: True}, expected_revision=1)
        with self.assertRaises(ClipboardPersistenceError):
            self.repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=prepared)
        self.assertIsNotNone(self.repository._prepare_consent())
        self.settings.apply({WORKFLOW_ENABLED: False}, expected_revision=2)
        with self.assertRaises(ClipboardPersistenceError):
            self.repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=prepared)
        self.assertEqual(self.counts(), (0,0,0))

    def test_wrong_profile_copy_and_malformed_versions_deny(self):
        self.grant()
        self.assertIsNone(ClipboardRepository(self.database_path, profile_scope='c'*64)._prepare_consent())
        copied = self.root/'copy.db'
        shutil.copyfile(self.database_path,copied)
        self.assertIsNone(ClipboardRepository(copied, profile_scope='b'*64)._prepare_consent())
        with database_connection(self.database_path) as c:
            c.execute('PRAGMA ignore_check_constraints=ON')
            c.execute("UPDATE clipboard_history_consent SET policy_version='old'")
        self.assertIsNone(self.repository._prepare_consent())

    def test_failed_consent_insert_rolls_back_settings_and_no_notification(self):
        events=[]
        self.settings.subscribe(events.append)
        with database_connection(self.database_path) as c:
            c.execute("CREATE TRIGGER fail_consent BEFORE INSERT ON clipboard_history_consent BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
        with self.assertRaises(SettingsPersistenceError):
            self.grant()
        self.assertFalse(self.settings.refresh().get(WORKFLOW_ENABLED).value)
        self.assertEqual(events,[])
        self.assertEqual(self.service.refresh_setup()[1],None)

    def test_real_assessment_exact_text_replay_and_deleted_receipt(self):
        self.grant()
        context,command=self.command('Synthetic note\r\n e\u0301 😀\n')
        first=self.service.capture_manual_text(context,command)
        self.assertEqual(self.service.capture_manual_text(context,command).outcome,first.outcome)
        with database_connection(self.database_path) as c:
            self.assertEqual(c.execute('SELECT raw_text FROM clipboard_items').fetchone()[0],command.source.text)
            c.execute('DELETE FROM clipboard_items')
        self.assertEqual(self.service.lookup_receipt(command.operation).disposition,ReplayDisposition.KNOWN_COMMITTED_SOURCE_UNAVAILABLE)
        self.assertEqual(self.counts(),(0,0,1))

    def test_privacy_rejection_never_opens_writer(self):
        self.grant()
        for text in ('password=synthetic-credential','lab@example.invalid'):
            context,command=self.command(text)
            with patch.object(self.repository,'_write',side_effect=AssertionError('Writer must not open')):
                with self.assertRaises(ClipboardPersistenceError):
                    self.service.capture_manual_text(context,command)
        self.assertEqual(self.counts(),(0,0,0))

    def test_upgrade_preserves_enabled_preference_without_backfill(self):
        prior = self.root / 'prior'
        prior.mkdir()
        for path in (PROJECT_ROOT / 'Database/Migrations').glob('*.sql'):
            if int(path.name[:4]) <= 15:
                shutil.copyfile(path, prior / path.name)
        path = self.root / 'upgrade.db'
        bootstrap_database(path, prior)
        with database_connection(path) as connection:
            connection.execute("INSERT INTO settings_user_overrides VALUES ('clipboard.workflow_enabled','BOOLEAN','true')")
        self.assertEqual(bootstrap_database(path, PROJECT_ROOT / 'Database/Migrations').migration_result.applied_versions, (16, 17))
        with database_connection(path) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM clipboard_history_consent').fetchone()[0], 0)
            self.assertEqual(connection.execute('SELECT value_text FROM settings_user_overrides').fetchone()[0], 'true')
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
        self.assertEqual(bootstrap_database(path, PROJECT_ROOT / 'Database/Migrations').migration_result.applied_versions, ())

    def test_constraints_and_settings_foreign_key(self):
        values = dict(singleton_id=1, database_instance_id='a'*32, database_scope='a'*64,
                      profile_scope='b'*64, purpose='clipboard_manual_durable_v1',
                      disclosure_version='clipboard_setup_manual_history_v1',
                      policy_version='clipboard_history_consent_v1', consent_epoch=1, state='GRANTED',
                      grant_settings_revision=0, transition_settings_revision=0, last_action_id='b'*32,
                      granted_at='2026-10-15T12:00:00.000Z', revoked_at=None)
        with database_connection(self.database_path) as connection:
            for change in ({'consent_epoch':0}, {'consent_epoch':1.5}, {'profile_scope':'bad'},
                           {'state':'REVOKED'}, {'revoked_at':values['granted_at']},
                           {'purpose':'automatic'}, {'transition_settings_revision':-1}):
                row = values | change
                with self.subTest(fields=tuple(change)), self.assertRaises(sqlite3.IntegrityError):
                    connection.execute('INSERT INTO clipboard_history_consent ('+','.join(row)+') VALUES ('+','.join('?' for _ in row)+')', tuple(row.values()))
            connection.execute('INSERT INTO clipboard_history_consent ('+','.join(values)+') VALUES ('+','.join('?' for _ in values)+')', tuple(values.values()))
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute('DELETE FROM settings_state')
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_uncertain_grant_commit_before_and_after_reconciles_read_only(self):
        real = database_connection
        for mode in ('before', 'after'):
            # Each attempt uses a separate synthetic store/owner.
            path = self.root / (mode+'.db')
            bootstrap_database(path, PROJECT_ROOT/'Database/Migrations')
            settings = SettingsService(SettingsRepository(path), CLIPBOARD_SETTING_DEFINITIONS)
            service = ClipboardService(ClipboardRepository(path, profile_scope='b'*64), settings=settings)
            class LostCommit:
                def __init__(self,c): self.c=c
                def __getattr__(self,n): return getattr(self.c,n)
                def commit(self):
                    if mode == 'after': self.c.commit()
                    raise sqlite3.OperationalError('synthetic private commit acknowledgement')
            @contextmanager
            def faulty(*args, **kwargs):
                with real(*args, **kwargs) as c:
                    yield LostCommit(c)
            with patch('f7hub.repositories.settings_repository.database_connection', faulty):
                with self.assertRaises(SettingsUncertainError) as caught:
                    service.enable_history_from_setup({WORKFLOW_ENABLED:True},expected_revision=0,expected_epoch=None)
            before=path.read_bytes()
            self.assertEqual(service.refresh_setup()[2],mode=='after')
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(len(caught.exception.action_id),32)

    def test_postcommit_observer_can_reserve_another_writer(self):
        observed=[]
        def notified(event):
            with database_connection(self.database_path,busy_timeout_ms=0) as c:
                c.execute('BEGIN IMMEDIATE')
                observed.append(c.execute('SELECT state FROM clipboard_history_consent').fetchone()[0])
        self.settings.subscribe(notified)
        self.grant()
        self.assertEqual(observed,['GRANTED'])

    def test_incomplete_and_detector_exception_never_write(self):
        self.grant()
        with patch('f7hub.domain.clipboard_privacy._scan',side_effect=RuntimeError('synthetic')):
            context,command=self.command()
            with self.assertRaises(ClipboardPersistenceError):
                self.service.capture_manual_text(context,command)
        self.assertEqual(self.counts(),(0,0,0))

    def test_epoch_overflow_and_malformed_calendar_deny(self):
        self.grant()
        with database_connection(self.database_path) as c:
            c.execute('UPDATE clipboard_history_consent SET consent_epoch=?',(2**63-1,))
        self.assertIsNone(self.repository._prepare_consent())
        with self.assertRaises(SettingsPersistenceError):
            self.grant()
        with database_connection(self.database_path) as c:
            c.execute("UPDATE clipboard_history_consent SET granted_at='2026-02-30T12:00:00.000Z'")
        self.assertIsNone(self.repository._prepare_consent())

    def test_missing_settings_and_forged_preparation_fail_closed(self):
        self.grant()
        prepared=self.repository._prepare_consent()
        context,command=self.command()
        binding=ClipboardAdmissionBinding(command,self.repository.database_scope)
        policy=ClipboardPrivacyPolicy('clipboard_local_rules','1','clipboard_history_consent_v1','PERMITTED',True,True)
        for field,value in (('database_instance_id','f'*32),('profile_scope','e'*64),('consent_epoch',99)):
            with self.subTest(field=field),self.assertRaises(ClipboardPersistenceError):
                self.repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=replace(prepared,**{field:value}))
        with database_connection(self.database_path) as c:
            c.execute('DELETE FROM clipboard_history_consent')
            c.execute('DELETE FROM settings_state')
        self.assertIsNone(self.repository._prepare_consent())
        with self.assertRaises(ClipboardPersistenceError):
            self.repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=prepared)
        self.assertEqual(self.counts(),(0,0,0))

    def test_revoked_duplicate_has_zero_item_event_receipt_changes(self):
        self.grant()
        context,command=self.command()
        self.service.capture_manual_text(context,command)
        command=replace(command,operation=self.service.new_operation(context))
        def capture_rows():
            with database_connection(self.database_path,read_only=True) as c:
                return [tuple(tuple(row) for row in c.execute('SELECT * FROM '+name)) for name in
                    ('clipboard_items','clipboard_capture_events','clipboard_operation_receipts')]
        before=capture_rows()
        self.settings.apply({WORKFLOW_ENABLED:False},expected_revision=1)
        with self.assertRaises(ClipboardPersistenceError):self.service.capture_manual_text(context,command)
        self.assertEqual(capture_rows(),before)

    def test_assessment_completes_before_sqlite_writer_reservation(self):
        from f7hub.domain.clipboard_privacy import assess_manual_text
        self.grant()
        observed=[]
        def assess(source):
            with database_connection(self.database_path,busy_timeout_ms=0) as c:
                c.execute('BEGIN IMMEDIATE')
                observed.append(source.text)
            return assess_manual_text(source)
        context,command=self.command()
        with patch('f7hub.services.clipboard_service.assess_manual_text',assess):
            self.service.capture_manual_text(context,command)
        self.assertEqual(observed,[command.source.text])

    def test_settings_change_during_assessment_cannot_retarget_preparation(self):
        from f7hub.domain.clipboard_privacy import assess_manual_text
        self.grant()
        def assess(source):
            self.settings.apply({SOURCE_TITLE_ENABLED:True},expected_revision=1)
            return assess_manual_text(source)
        context,command=self.command()
        with patch('f7hub.services.clipboard_service.assess_manual_text',assess):
            with self.assertRaises(ClipboardPersistenceError):
                self.service.capture_manual_text(context,command)
        self.assertEqual(self.counts(),(0,0,0))


def _capture_reserved_worker(path, binding, policy, consent, reserved, release, outcome):
    from f7hub.repositories.clipboard_repository import _capture
    def held(*args):
        reserved.set()
        if not release.wait(10):
            raise RuntimeError('Owned capture reservation release timed out')
        return _capture(*args)
    try:
        with patch('f7hub.repositories.clipboard_repository._capture',held):
            repository=ClipboardRepository(path,profile_scope='b'*64)
            result=repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=consent)
        outcome.put(result.disposition.value)
    except ClipboardPersistenceError as error:
        outcome.put(error.code.value)


def _revoke_reserved_worker(path, reserved, release, outcome):
    real=database_connection
    class Held:
        def __init__(self,c):self.c=c
        def __getattr__(self,n):return getattr(self.c,n)
        def execute(self,sql,*args):
            result=self.c.execute(sql,*args)
            if sql=='BEGIN IMMEDIATE':
                reserved.set()
                if not release.wait(10):raise RuntimeError('Owned revocation release timed out')
            return result
    @contextmanager
    def held(*args,**kwargs):
        with real(*args,**kwargs) as c:yield Held(c)
    service=SettingsService(SettingsRepository(path),CLIPBOARD_SETTING_DEFINITIONS)
    with patch('f7hub.repositories.settings_repository.database_connection',held):
        service.apply({WORKFLOW_ENABLED:False},expected_revision=service.get_snapshot().revision)
    outcome.put('REVOKED')


class ClipboardConsentRaceTests(_ConsentFixture):
    """Real separate Windows processes plus independent SQLite connections."""

    def finish(self,process):
        process.join(12)
        if process.is_alive():
            process.terminate();process.join(3)
            self.fail('Owned synthetic process exceeded bound')
        self.assertEqual(process.exitcode,0)

    def test_windows_interrupted_revocation_rolls_back_without_false_disable(self):
        self.grant()
        before=self.repository._prepare_consent()
        ctx=multiprocessing.get_context('spawn')
        reserved,release,outcome=ctx.Event(),ctx.Event(),ctx.Queue()
        process=ctx.Process(target=_revoke_reserved_worker,args=(self.database_path,reserved,release,outcome))
        process.start()
        try:
            self.assertTrue(reserved.wait(10))
            process.terminate();process.join(5)
            self.assertFalse(process.is_alive())
        finally:
            if process.is_alive():process.terminate();process.join(3)
            outcome.close();outcome.join_thread()
        self.assertEqual(self.repository._prepare_consent(),before)
        self.assertEqual(self.counts(),(0,0,0))

    def test_windows_revocation_first_denies_prepared_capture(self):
        self.grant()
        context,command=self.command()
        consent=self.repository._prepare_consent()
        binding=ClipboardAdmissionBinding(command,self.repository.database_scope)
        policy=ClipboardPrivacyPolicy('clipboard_local_rules','1','clipboard_history_consent_v1','PERMITTED',True,True)
        ctx=multiprocessing.get_context('spawn')
        reserved,release,outcome=ctx.Event(),ctx.Event(),ctx.Queue()
        process=ctx.Process(target=_revoke_reserved_worker,args=(self.database_path,reserved,release,outcome))
        process.start()
        try:
            self.assertTrue(reserved.wait(10))
            release.set()
            self.assertEqual(outcome.get(timeout=10),'REVOKED')
            with self.assertRaises(ClipboardPersistenceError):
                self.repository._persist_admitted(binding,policy,accepted_at='2026-10-15T12:00:00.000Z',consent=consent)
        finally:
            release.set();self.finish(process);outcome.close();outcome.join_thread()
        self.assertEqual(self.counts(),(0,0,0))

    def test_windows_capture_first_commits_then_waiting_revocation(self):
        self.grant()
        context,command=self.command()
        consent=self.repository._prepare_consent()
        binding=ClipboardAdmissionBinding(command,self.repository.database_scope)
        policy=ClipboardPrivacyPolicy('clipboard_local_rules','1','clipboard_history_consent_v1','PERMITTED',True,True)
        ctx=multiprocessing.get_context('spawn')
        reserved,release,outcome=ctx.Event(),ctx.Event(),ctx.Queue()
        process=ctx.Process(target=_capture_reserved_worker,args=(self.database_path,binding,policy,consent,reserved,release,outcome))
        process.start()
        attempting=threading.Event()
        real=database_connection
        class Observe:
            def __init__(self,c):self.c=c
            def __getattr__(self,n):return getattr(self.c,n)
            def execute(self,sql,*args):
                if sql=='BEGIN IMMEDIATE':attempting.set()
                return self.c.execute(sql,*args)
        @contextmanager
        def observed(*args,**kwargs):
            with real(*args,**kwargs) as c:yield Observe(c)
        try:
            self.assertTrue(reserved.wait(10))
            with database_connection(self.database_path,busy_timeout_ms=0) as c:
                with self.assertRaises(sqlite3.OperationalError):c.execute('BEGIN IMMEDIATE')
            with ThreadPoolExecutor(max_workers=1) as pool:
                with patch('f7hub.repositories.settings_repository.database_connection',observed):
                    future=pool.submit(self.settings.apply,{WORKFLOW_ENABLED:False},expected_revision=1)
                    self.assertTrue(attempting.wait(5))
                    release.set()
                    future.result(timeout=10)
            self.assertEqual(outcome.get(timeout=10),'NEW_CAPTURE')
        finally:
            release.set();self.finish(process);outcome.close();outcome.join_thread()
        self.assertEqual(self.counts(),(1,1,1))
        self.assertIsNone(self.repository._prepare_consent())
