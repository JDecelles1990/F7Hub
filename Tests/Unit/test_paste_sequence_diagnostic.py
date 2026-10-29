"""Real diagnostic/writer/guard functions with synthetic Win32 only; no live input."""
import ctypes as C
from datetime import datetime,timedelta,timezone
import os,threading,time,unittest
from unittest.mock import Mock,patch
from uuid import uuid4
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QMainWindow
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI,paste_latest,PasteEffectError,PasteSequenceDiagnostic
from f7hub.infrastructure.windows_selection_copy import Target
from f7hub.domain.clipboard import ClipboardPasteAuthorization,ClipboardPasteSource,ClipboardItemRef,AdmittedManualText,ClipboardPasteError
from f7hub.gui.selection_capture import SelectionCapture
from Tests.Database.test_clipboard_append_head import _PasteFixture

from Tests.Unit.test_post_close_paste_verification import api_for as verification_api

def api_for(case='stable'):
    mapped={'after_close_change':'change_after_verified_baseline','close_failure':'write_close_failure','both_change':'external_writer'}.get(case,case)
    api=verification_api(mapped)
    for method in ('register','unregister','register_paste','unregister_paste'):setattr(api,method,lambda:True)
    return api

def prepare(token):return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
def consume(auth):return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),(datetime.now(timezone.utc)+timedelta(seconds=1)).isoformat())

class SequenceDiagnosticTests(unittest.TestCase):
    def exercise(self,case='stable',diagnostic=True):
        api=api_for(case);record=PasteSequenceDiagnostic() if diagnostic else None
        try:
            result=paste_latest(api,api.target,123,threading.Event(),prepare,consume,sequence_diagnostic=record)
            code='GUARDS_PASSED_NO_DISPATCH' if diagnostic else 'SUCCESS';clipboard=result[0]
        except PasteEffectError as error:result=None;code=str(error);clipboard=error.clipboard
        return api,record,result,code,(record.summary(code,clipboard) if record else '')
    def test_stable_real_writer_collects_three_samples_and_never_sends(self):
        api,d,result,code,text=self.exercise();self.assertEqual(result,('WRITTEN','NOT_SENT'));self.assertEqual(api.user.input_calls,0)
        self.assertEqual(set(d.samples),{1,2,3});self.assertIn('CLASS=F',text);self.assertIn('P=PASS',text);self.assertIn('D12=SAME D23=SAME',text)
        t=api.user.trace;self.assertLess(t.index('SET'),t.index('CLOSE'));self.assertEqual(t[t.index('CLOSE')+1],'SEQUENCE')
    def test_write_time_change_is_in_s1_baseline(self):
        api,d,result,code,text=self.exercise('before_close_change');self.assertIn('CLASS=F',text);self.assertEqual(result,('WRITTEN','NOT_SENT'))
    def test_close_time_change_is_verified_without_dispatch_and_remains_ambiguous(self):
        api,d,result,code,text=self.exercise('close_change');self.assertEqual(result,('WRITTEN','NOT_SENT'));self.assertIn('CLASS=A',text)
        self.assertIn('D12=CHANGED',text);self.assertIn('UPDATE=AMBIGUOUS_SAME_OWNER',text);self.assertIn('P=PASS',text);self.assertEqual(api.user.input_calls,0)
    def test_external_after_close_change_is_b_and_never_rebaselined(self):
        api,d,result,code,text=self.exercise('after_close_change');self.assertEqual(code,'CLIPBOARD_CHANGED');self.assertIn('CLASS=B',text);self.assertIn('D12=SAME D23=CHANGED',text)
    def test_wrong_owner_is_c_and_remains_rejected(self):
        api,d,result,code,text=self.exercise('wrong_owner');self.assertEqual(code,'CLIPBOARD_CHANGED');self.assertIn('CLASS=INCOMPLETE',text);self.assertIn('P=NONE',text)
    def test_sequence_and_owner_change_is_d(self):
        api,d,result,code,text=self.exercise('both_change');self.assertIn('D12=CHANGED',text);self.assertIn('CLASS=INCOMPLETE',text);self.assertEqual(code,'CLIPBOARD_CHANGED')
    def test_zero_s1_is_original_writer_rejection(self):
        api,d,result,code,text=self.exercise('zero_s1');self.assertEqual(code,'SEQUENCE_UNAVAILABLE');self.assertIn('S1[Q=OK,Z=1',text);self.assertNotIn(3,d.samples)
    def test_zero_s3_names_actual_predicate(self):
        api,d,result,code,text=self.exercise('zero_s3');self.assertEqual(code,'CLIPBOARD_CHANGED');self.assertIn('P=ACTUAL_ZERO',text);self.assertEqual(api.user.input_calls,0)
    def test_close_failure_has_no_s2_or_s3_and_preserves_cleanup_error(self):
        api,d,result,code,text=self.exercise('close_failure');self.assertEqual(code,'CLEANUP_FAILED');self.assertEqual(d.close,'FAIL');self.assertEqual(set(d.samples),{1});self.assertEqual(api.user.input_calls,0)
    def test_failed_write_stays_rejected(self):
        api,d,result,code,text=self.exercise('write_failure');self.assertEqual(code,'CLIPBOARD_WRITE_FAILED');self.assertIn('CLIPBOARD=MAY_HAVE_CHANGED',text);self.assertEqual(api.user.input_calls,0)
    def test_extra_observation_failure_is_content_free_and_not_a_dispatch(self):
        api,d,result,code,text=self.exercise('owner_observation_exception');self.assertEqual(result,('WRITTEN','NOT_SENT'));self.assertIn('O=UNKNOWN,A=FAIL',text);self.assertIn('CLASS=INCOMPLETE',text);self.assertNotIn('PRIVATE',text)
    def test_original_sequence_api_exception_propagates_fixed_native_failure(self):
        api,d,result,code,text=self.exercise('sequence_exception');self.assertEqual(code,'AUTHORIZATION_OR_NATIVE_UNAVAILABLE');self.assertIn('P=SEQUENCE_API_FAILED',text);self.assertNotIn('PRIVATE',text)
    def test_normal_mode_keeps_existing_dispatch_and_call_count(self):
        api,d,result,code,text=self.exercise(diagnostic=False);self.assertEqual(result,('WRITTEN','DISPATCHED'));self.assertEqual(api.user.input_calls,1);self.assertEqual(api.user.opens,2);self.assertEqual(api.user.closes,2)
    def test_normal_mode_accepts_only_verified_close_change(self):
        api,d,result,code,text=self.exercise('close_change',diagnostic=False);self.assertEqual(result,('WRITTEN','DISPATCHED'));self.assertEqual(api.user.input_calls,1)
    def test_unknown_owner_is_not_reported_as_confirmed_same_owner(self):
        d=PasteSequenceDiagnostic();d.samples={1:(20,True,True,True),2:(21,True,None,False),3:(21,True,True,True)}
        text=d.summary('CLIPBOARD_CHANGED','WRITTEN');self.assertIn('CLASS=INCOMPLETE',text);self.assertIn('UPDATE=AMBIGUOUS_OWNER_UNKNOWN',text)
    def test_result_code_is_allowlisted(self):
        d=PasteSequenceDiagnostic();self.assertNotIn('PRIVATE',d.summary('PRIVATE SECRET'));self.assertIn('RESULT=UNCLASSIFIED',d.summary('PRIVATE SECRET'))

class SequenceServiceTests(_PasteFixture):
    def test_real_consent_and_single_use_service_no_extra_capture_event(self):
        self.capture('Synthetic ordinary note');api=api_for();d=PasteSequenceDiagnostic();tickets=[];before=self.counts()
        def deliver(p,c):
            def bound(token):a=p(token);tickets.append(a);return a
            return paste_latest(api,api.target,123,threading.Event(),bound,c,clock=self.clock.monotonic,utc=self.clock.utc,sequence_diagnostic=d)
        self.assertEqual(self.service.paste_latest(deliver),('WRITTEN','NOT_SENT'));self.assertEqual(api.user.input_calls,0);self.assertEqual(self.counts(),before)
        with self.assertRaises(ClipboardPasteError):self.service.consume_latest_paste(self.service._context,tickets[0])

class SequenceOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.env=patch.dict(os.environ,{'F7HUB_DEV_PASTE_SEQUENCE_DIAGNOSTIC':'1','F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC':'0'});self.env.start();self.addCleanup(self.env.stop)
        self.window=QMainWindow();self.api=api_for();self.service=Mock();self.service.paste_latest.side_effect=lambda deliver:deliver(prepare,consume)
        self.owner=SelectionCapture(self.window,self.service,api=self.api);self.owner.start()
    def drain(self):
        end=time.monotonic()+3
        while self.owner.busy and time.monotonic()<end:self.owner.poll();self.app.processEvents();time.sleep(.005)
        self.assertFalse(self.owner.busy)
    def tearDown(self):self.drain();self.owner.close();self.window.deleteLater();self.app.processEvents()
    def test_existing_owner_service_writer_and_persistent_fixed_feedback(self):
        self.assertTrue(self.owner.sequence_diagnostic);self.assertFalse(self.owner.target_diagnostic);self.assertTrue(self.owner.trigger(action='paste'));self.drain()
        self.assertIn('SEQ_DIAG',self.window.statusBar().currentMessage());self.assertIn('CLASS=F',self.window.statusBar().currentMessage());self.assertEqual(self.api.user.input_calls,0)
        first=self.window.statusBar().currentMessage();self.assertFalse(self.owner.trigger(action='paste'));self.assertEqual(self.window.statusBar().currentMessage(),first);self.service.paste_latest.assert_called_once()
    def test_cleanup_failure_disables_both_hotkeys(self):
        self.api.user.case='write_close_failure';self.owner.trigger(action='paste');self.drain();self.assertTrue(self.owner.cleanup_failed);self.assertFalse(self.owner.registered or self.owner.paste_registered)
        self.assertIn('CLOSE=FAIL',self.window.statusBar().currentMessage())
    def test_development_mode_requires_exact_enablement_and_source(self):
        for value in ('0','','true'):
            with patch.dict(os.environ,{'F7HUB_DEV_PASTE_SEQUENCE_DIAGNOSTIC':value}):self.assertFalse(SelectionCapture(self.window,self.service,api=self.api).sequence_diagnostic)
        with patch('f7hub.gui.selection_capture.sys.frozen',True,create=True):self.assertFalse(SelectionCapture(self.window,self.service,api=self.api).sequence_diagnostic)
        with patch('f7hub.gui.selection_capture.Path.exists',return_value=False):self.assertFalse(SelectionCapture(self.window,self.service,api=self.api).sequence_diagnostic)
    def test_target_only_mode_takes_priority_without_real_write(self):
        with patch.dict(os.environ,{'F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC':'1'}):
            owner=SelectionCapture(self.window,self.service,api=self.api);self.assertTrue(owner.target_diagnostic);self.assertFalse(owner.sequence_diagnostic)
