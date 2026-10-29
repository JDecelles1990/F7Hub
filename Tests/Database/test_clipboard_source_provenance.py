"""CP02-S3: isolated SQLite, real consent/services, synthetic acquisition."""
from dataclasses import replace
import shutil
import sqlite3
import threading
from unittest.mock import patch
from uuid import uuid4
from Tests.Database.test_clipboard_consent import _ConsentFixture
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT, seed_item, AS_OF, FixtureCapture
from f7hub.domain.clipboard import ClipboardSelectionAcquisition, ClipboardValidationError, ReplayDisposition
from f7hub.domain.clipboard_settings import SOURCE_PROCESS_ENABLED
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationApplicationError
from f7hub.repositories.clipboard_repository import ClipboardRepository, _RECENT_SQL

class SourceProvenanceMigrationTests(ClipboardDatabaseTestCase):
    def prior(self):
        directory=self.root/'prior'; directory.mkdir()
        for p in (PROJECT_ROOT/'Database/Migrations').glob('*.sql'):
            if int(p.name[:4])<=17: shutil.copyfile(p,directory/p.name)
        path=self.root/'prior.db'; bootstrap_database(path,directory)
        return path,directory

    def test_fresh_nullable_column_and_integrity(self):
        with database_connection(self.database_path) as c:
            columns={r[1]:r for r in c.execute('PRAGMA table_info(clipboard_capture_events)')}
            self.assertEqual(columns['source_process_basename'][2:5],('TEXT',0,None))
            self.assertEqual(c.execute('SELECT max(version) FROM schema_migrations').fetchone()[0],18)
            self.assertEqual(c.execute('PRAGMA foreign_keys').fetchone()[0],1)
            self.assertEqual(c.execute('PRAGMA busy_timeout').fetchone()[0],5000)
            self.assertEqual(validate_database_integrity(c),(('ok',),()))

    def test_upgrade_preserves_every_record_with_null_legacy(self):
        path,directory=self.prior()
        from Tests.Database.test_clipboard_consent import grant_synthetic_consent
        from Tests.Database.test_clipboard_receipts_migration import insert_receipt
        grant_synthetic_consent(path)
        with database_connection(path) as c:
            item=seed_item(c); insert_receipt(c,item)
            c.execute('INSERT INTO clipboard_append_head VALUES (1,?,?,1)',(str(uuid4()),item))
            names=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            before={t:[tuple(r) for r in c.execute('SELECT * FROM "'+t+'"')] for t in names}
        self.assertEqual(bootstrap_database(path,PROJECT_ROOT/'Database/Migrations').migration_result.applied_versions,(18,))
        with database_connection(path) as c:
            for t,rows in before.items():
                query='SELECT * FROM "'+t+'"'+(' WHERE version<=17' if t=='schema_migrations' else '')
                after=[tuple(r)[:-1] if t=='clipboard_capture_events' else tuple(r) for r in c.execute(query)]
                self.assertEqual(after,rows,t)
            self.assertIsNone(c.execute('SELECT source_process_basename FROM clipboard_capture_events').fetchone()[0])
            self.assertEqual(validate_database_integrity(c),(('ok',),()))
        self.assertEqual(bootstrap_database(path,PROJECT_ROOT/'Database/Migrations').migration_result.applied_versions,())

    def test_failed_migration_rolls_back_column_and_history(self):
        path,directory=self.prior(); migration=PROJECT_ROOT/'Database/Migrations/0018_clipboard_source_process_basename.sql'
        (directory/migration.name).write_bytes(migration.read_bytes()+b'\nINSERT INTO synthetic_missing_table VALUES (1);\n')
        with self.assertRaises(MigrationApplicationError): bootstrap_database(path,directory)
        with database_connection(path) as c:
            self.assertNotIn('source_process_basename',[r[1] for r in c.execute('PRAGMA table_info(clipboard_capture_events)')])
            self.assertEqual(c.execute('SELECT max(version) FROM schema_migrations').fetchone()[0],17)
            self.assertEqual(validate_database_integrity(c),(('ok',),()))

    def test_sql_shape_unicode_bounds_and_constraints(self):
        with database_connection(self.database_path) as c:
            seed_item(c)
            for value in (None,'notepad.exe','éditeur.exe','😀'*251+'.exe'):
                c.execute('UPDATE clipboard_capture_events SET source_process_basename=?',(value,))
            for value in ('','.exe','a'*252+'.exe','C:\\private\\a.exe','a/a.exe','a:cmd.exe','a<secret>.exe',
                          'a\0.exe','a\n.exe','a\x85.exe','a\u202e.exe','a\u200d.exe','a\u2028.exe',sqlite3.Binary(b'a.exe')):
                with self.subTest(kind=type(value).__name__),self.assertRaises(sqlite3.IntegrityError):
                    c.execute('UPDATE clipboard_capture_events SET source_process_basename=?',(value,))
            self.assertEqual(validate_database_integrity(c),(('ok',),()))

class SourceProvenanceConsentTests(_ConsentFixture):
    def enabled(self,value=True):
        snapshot=self.settings.refresh(); self.settings.apply({SOURCE_PROCESS_ENABLED:value},expected_revision=snapshot.revision)
    def receive(self,name='notepad.exe',text='Synthetic ordinary note',acquire=None):
        return self.service.capture_active_selection(acquire or (lambda:ClipboardSelectionAcquisition(text,name)),threading.Event())
    def names(self):
        with database_connection(self.database_path,read_only=True) as c:
            self.assertEqual(validate_database_integrity(c),(('ok',),()))
            return [r[0] for r in c.execute('SELECT source_process_basename FROM clipboard_capture_events ORDER BY clipboard_capture_event_id')]

    def test_off_on_off_preserves_prior_history(self):
        self.grant(); self.assertEqual(self.receive().persistence,'PERSISTED')
        self.enabled(); self.assertEqual(self.receive('MSEdge.EXE').persistence,'PERSISTED')
        self.enabled(False); self.assertEqual(self.receive().persistence,'PERSISTED')
        self.assertEqual(self.names(),[None,'msedge.exe',None]); self.assertEqual(self.counts(),(1,3,3))
        self.assertIsNone(self.service.get_recent().rows[0].source_process_basename)

    def test_same_text_different_apps_one_item_two_events(self):
        self.grant(); self.enabled(); self.receive(); self.receive('msedge.exe')
        self.assertEqual(self.names(),['notepad.exe','msedge.exe']); self.assertEqual(self.counts(),(1,2,2))
        self.assertEqual(self.service.get_recent().rows[0].source_process_basename,'msedge.exe')

    def test_preference_changes_during_acquisition_never_retarget(self):
        self.grant()
        def enable_during():
            self.enabled(); return ClipboardSelectionAcquisition('Synthetic note','notepad.exe')
        self.assertEqual(self.receive(acquire=enable_during).persistence,'NOT_SAVED')
        def disable_during():
            self.enabled(False); return ClipboardSelectionAcquisition('Synthetic note','notepad.exe')
        self.assertEqual(self.receive(acquire=disable_during).persistence,'NOT_SAVED')
        self.assertEqual(self.counts(),(0,0,0))

    def test_disable_at_final_writer_fence(self):
        self.grant(); self.enabled(); original=self.repository._persist_admitted
        def fence(*args,**kwargs):
            self.enabled(False); return original(*args,**kwargs)
        with patch.object(self.repository,'_persist_admitted',side_effect=fence):
            self.assertEqual(self.receive().persistence,'NOT_SAVED')
        self.assertEqual(self.names(),[])

    def test_optional_missing_invalid_plain_text_adapter_and_no_logs(self):
        self.grant(); self.enabled()
        with self.assertNoLogs(level='DEBUG'):
            for name in (None,'C:\\private\\a.exe','source title','a\u202e.exe',123):
                self.assertEqual(self.receive(name).persistence,'PERSISTED')
            self.assertEqual(self.receive(acquire=lambda:'Synthetic ordinary note').persistence,'PERSISTED')
        self.assertEqual(self.names(),[None]*6)

    def test_no_consent_or_sensitive_content_has_no_records(self):
        self.enabled(); self.assertEqual(self.receive().persistence,'PREVIEW_ONLY'); self.grant()
        with self.assertNoLogs(level='DEBUG'),self.assertRaises(ClipboardValidationError):
            self.receive(text='password=synthetic-only')
        self.assertEqual(self.counts(),(0,0,0))

    def test_replay_preserves_original_event_and_append_head(self):
        self.grant(); self.enabled(); context,command=self.command()
        command=replace(command,source_process_basename='notepad.exe')
        first=self.service.capture_manual_text(context,command)
        with database_connection(self.database_path,read_only=True) as c:
            head=tuple(c.execute('SELECT * FROM clipboard_append_head').fetchone())
        replay=self.service.capture_manual_text(context,replace(command,source_process_basename='msedge.exe'))
        self.assertEqual(replay.disposition,ReplayDisposition.SAME_OPERATION); self.assertEqual(first.outcome,replay.outcome)
        self.assertEqual(self.names(),['notepad.exe']); self.assertEqual(self.counts(),(1,1,1))
        with database_connection(self.database_path,read_only=True) as c:
            self.assertEqual(tuple(c.execute('SELECT * FROM clipboard_append_head').fetchone()),head)

    def test_repository_off_omits_name_from_typed_command(self):
        self.grant(); context,command=self.command()
        self.service.capture_manual_text(context,replace(command,source_process_basename='notepad.exe'))
        self.assertEqual(self.names(),[None])

    def test_event_failure_rolls_back_item_receipt_head(self):
        self.grant(); self.enabled(); self.receive()
        with database_connection(self.database_path) as c:
            before=[tuple(r) for r in c.execute('SELECT * FROM clipboard_append_head')]
            c.execute("CREATE TRIGGER synthetic_failure BEFORE INSERT ON clipboard_capture_events BEGIN SELECT RAISE(ABORT,'synthetic'); END")
        self.assertEqual(self.receive('msedge.exe',text='Another ordinary note').persistence,'NOT_SAVED')
        self.assertEqual(self.counts(),(1,1,1)); self.assertEqual(self.names(),['notepad.exe'])
        with database_connection(self.database_path,read_only=True) as c:
            self.assertEqual([tuple(r) for r in c.execute('SELECT * FROM clipboard_append_head')],before)

class SourceProvenanceQueryTests(ClipboardDatabaseTestCase):
    def test_latest_committed_id_over_timestamps_null_expiry_deletion(self):
        with database_connection(self.database_path) as c:
            item=seed_item(c,captures=(FixtureCapture(),FixtureCapture(),FixtureCapture(received_at='2026-10-08T09:00:00.000Z')))
            ids=[r[0] for r in c.execute('SELECT clipboard_capture_event_id FROM clipboard_capture_events ORDER BY clipboard_capture_event_id')]
            for event_id,name in zip(ids,('notepad.exe','msedge.exe',None)):
                c.execute('UPDATE clipboard_capture_events SET source_process_basename=? WHERE clipboard_capture_event_id=?',(name,event_id))
        repo=ClipboardRepository(self.database_path)
        self.assertIsNone(repo.get_recent(limit=50,as_of=AS_OF).rows[0].source_process_basename)
        with database_connection(self.database_path) as c:
            c.execute('UPDATE clipboard_capture_events SET source_process_basename=? WHERE clipboard_capture_event_id=?',('editor.exe',ids[2]))
        self.assertEqual(repo.get_recent(limit=50,as_of=AS_OF).rows[0].source_process_basename,'editor.exe')
        self.assertEqual(repo.get_recent(limit=50,as_of='2026-10-10T00:00:00.000Z').rows,())
        with database_connection(self.database_path) as c:
            c.execute('DELETE FROM clipboard_capture_events WHERE clipboard_item_id=?',(item,))
        self.assertIsNone(repo.get_recent(limit=50,as_of=AS_OF).rows[0].source_process_basename)
        with database_connection(self.database_path) as c:
            c.execute('DELETE FROM clipboard_items WHERE clipboard_item_id=?',(item,))
            self.assertEqual(validate_database_integrity(c),(('ok',),()))
        self.assertEqual(repo.get_recent(limit=50,as_of=AS_OF).rows,())

    def test_large_history_reuses_indexes_unique_bounded_page(self):
        with database_connection(self.database_path) as c:
            for i in range(1,301): seed_item(c,item_id=i)
            sql="INSERT INTO clipboard_capture_events (clipboard_item_id,received_at,capture_method,producer_binding,ingress_generation,operation_id,source_process_basename) VALUES (?,'2026-10-08T10:00:00.000Z','F7HUB','synthetic','synthetic',?,'notepad.exe')"
            c.execute("BEGIN")
            c.executemany(sql,((i,str(uuid4())) for i in range(1,301) for _ in range(50)))
            c.commit()
            plan=[r[3] for r in c.execute('EXPLAIN QUERY PLAN '+_RECENT_SQL,(AS_OF,101))]
            self.assertTrue(any('idx_clipboard_items_recent' in x for x in plan),plan)
            self.assertTrue(any('idx_clipboard_capture_events_item' in x for x in plan),plan)
            self.assertFalse(any('TEMP B-TREE' in x for x in plan),plan)
            self.assertEqual(c.execute('SELECT count(*) FROM clipboard_capture_events').fetchone()[0],15300)
            self.assertEqual(validate_database_integrity(c),(('ok',),()))
        repo=ClipboardRepository(self.database_path)
        for limit in (1,50,100):
            page=repo.get_recent(limit=limit,as_of=AS_OF)
            self.assertEqual(len(page.rows),limit); self.assertTrue(page.has_more)
            self.assertEqual([r.item_ref.clipboard_item_id for r in page.rows],list(range(300,300-limit,-1)))
            self.assertTrue(all(r.source_process_basename=='notepad.exe' for r in page.rows))
