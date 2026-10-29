"""Real consent/service/SQLite with fake target, Clipboard and input effects."""
import threading
from unittest.mock import patch
from f7hub.domain.clipboard import ClipboardValidationError, ClipboardPersistenceError, ClipboardPersistenceCode
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED
from f7hub.infrastructure.windows_latest_paste import paste_latest, PasteEffectError
from Tests.Database.test_clipboard_append_head import _PasteFixture
from Tests.Unit.test_windows_latest_paste import FakePasteAPI

class LatestPasteFlowTests(_PasteFixture):
    def setUp(self):
        super().setUp(); self.api=FakePasteAPI(); self.cancelled=threading.Event()
        self.prepare_effect=lambda auth: None
    def run_effect(self):
        def deliver(prepare,consume):
            def bound_prepare(token):
                auth=prepare(token); self.prepare_effect(auth); return auth
            return paste_latest(self.api,self.api.target,123,self.cancelled,bound_prepare,consume,
                clock=self.clock.monotonic,utc=self.clock.utc,sleep=self.clock.advance)
        return self.service.paste_latest(deliver)
    def deny_effect(self):
        with self.assertRaises(PasteEffectError): self.run_effect()
        self.assertEqual((self.api.writes,self.api.sent),(0,0))
    def selection(self,text='Synthetic latest highlighted note'):
        return self.service.capture_active_selection(lambda:text,threading.Event())
    def test_normal_latest_persisted_selection(self):
        self.capture('Synthetic older note')
        self.assertEqual(self.selection().persistence,'PERSISTED')
        before=self.counts()
        self.assertEqual(self.run_effect(),('WRITTEN','DISPATCHED'))
        self.assertEqual(self.counts(),before)
    def test_no_eligible_history(self): self.deny_effect()
    def test_consent_revoked_after_prepare(self):
        self.capture()
        self.prepare_effect=lambda auth:self.settings.apply({WORKFLOW_ENABLED:False},expected_revision=1)
        self.deny_effect()
    def test_new_capture_between_prepare_consume(self):
        self.capture()
        self.prepare_effect=lambda auth:self.service.capture_manual_text(self.service._context,
            self.command('Synthetic newer capture',context=self.service._context))
        self.deny_effect()
    def test_deleted_source_never_falls_back(self):
        self.capture('Synthetic older'); self.capture('Synthetic latest')
        self.prepare_effect=lambda auth:self.sql('DELETE FROM clipboard_items WHERE clipboard_item_id=?',(auth.item_ref.clipboard_item_id,))
        self.deny_effect()
    def test_expired_source(self):
        self.capture()
        from datetime import datetime
        expiry=datetime.fromisoformat(self.head().expires_at.replace('Z','+00:00'))
        self.clock.advance((expiry-self.clock.utc()).total_seconds())
        self.deny_effect()
    def test_changed_revision(self):
        self.capture()
        self.prepare_effect=lambda auth:self.sql('UPDATE clipboard_items SET revision=revision+1')
        self.deny_effect()
    def test_sensitive_source_reassessment(self):
        self.capture()
        self.prepare_effect=lambda auth:self.sql("UPDATE clipboard_items SET raw_text='password=synthetic-secret'")
        self.deny_effect()
    def test_rejected_new_selection_blocks_older_saved_item(self):
        self.capture()
        with self.assertRaises(ClipboardValidationError): self.selection('password=synthetic-secret')
        self.deny_effect()
    def test_transient_new_selection_blocks_older_saved_item(self):
        self.capture()
        with patch.object(self.repository,'_prepare_consent',return_value=None):
            self.assertEqual(self.selection().persistence,'PREVIEW_ONLY')
        self.deny_effect()
    def test_uncertain_new_capture_blocks_older_saved_item(self):
        self.capture()
        with patch.object(self.service,'capture_manual_text',side_effect=ClipboardPersistenceError(ClipboardPersistenceCode.UNCERTAIN)), patch.object(self.service,'lookup_receipt',side_effect=RuntimeError('synthetic')):
            self.assertEqual(self.selection().persistence,'PERSISTENCE_UNCERTAIN')
        self.deny_effect()
    def test_failed_acquisition_blocks_older_and_later_saved_capture_recovers(self):
        self.capture()
        def fail(): raise RuntimeError('synthetic acquisition failure')
        with self.assertRaises(RuntimeError): self.service.capture_active_selection(fail,threading.Event())
        self.deny_effect()
        self.assertEqual(self.selection().persistence,'PERSISTED')
        self.assertEqual(self.run_effect(),('WRITTEN','DISPATCHED'))
    def test_accepted_attempt_without_worker_never_falls_back(self):
        self.capture(); self.service.begin_selection_capture(); self.deny_effect()
    def test_cancelled_capture_blocks_older(self):
        self.capture(); event=threading.Event(); event.set()
        with self.assertRaises(ClipboardValidationError): self.service.capture_active_selection(lambda:'Synthetic note',event)
        self.deny_effect()
    def test_one_use_authorization_cannot_replay_after_write_failure(self):
        self.capture(); captured=[]
        self.prepare_effect=lambda auth:captured.append(auth)
        self.api.write_text=lambda *args:(_ for _ in ()).throw(PasteEffectError('CLIPBOARD_LOCKED'))
        self.deny_effect()
        from f7hub.domain.clipboard import ClipboardPasteError
        with self.assertRaises(ClipboardPasteError): self.service.consume_latest_paste(self.service._context,captured[0])

    def test_bootstrapped_owner_pastes_through_real_service_and_shutdown(self):
        import time
        from PySide6.QtWidgets import QApplication
        from f7hub.app.bootstrap import bootstrap_application
        from Tests.Database.clipboard_fixtures import PROJECT_ROOT
        app=QApplication.instance() or QApplication([])
        with patch('f7hub.services.mochi_service.MochiService.automatic_start',return_value=False):
            context=bootstrap_application(project_root=PROJECT_ROOT,database_path=self.database_path)
        window=context.main_window; owner=window.selection_capture
        for name in ('register','unregister','register_paste','unregister_paste'):
            setattr(self.api,name,lambda:True)
        owner.api=self.api
        try:
            deadline=time.monotonic()+5
            while window.runner.busy and time.monotonic()<deadline:
                app.processEvents();time.sleep(.005)
            self.assertFalse(window.runner.busy)
            service=owner.service
            snapshot,epoch,_=service.refresh_setup()
            service.enable_history_from_setup({WORKFLOW_ENABLED:True},expected_revision=snapshot.revision,expected_epoch=epoch)
            self.assertEqual(service.capture_active_selection(lambda:'Synthetic bootstrapped paste',threading.Event()).persistence,'PERSISTED')
            window.lifecycle.start()
            self.assertTrue(owner.trigger(action='paste'))
            while owner.busy and time.monotonic()<deadline:
                app.processEvents();owner.poll();time.sleep(.005)
            self.assertFalse(owner.busy)
            self.assertEqual((self.api.writes,self.api.sent),(1,1))
            self.assertIn('dispatched once',window.statusBar().currentMessage())
            self.assertTrue(window.confirm_exit())
            self.assertTrue(window.cleanup_shutdown())
            self.assertFalse(owner.registered or owner.paste_registered)
        finally:
            window.lifecycle.recovery_timer.stop();window.lifecycle.tray.hide()
            owner.cancel();window.cleanup_shutdown();window.deleteLater();app.processEvents()
