"""Post-close verification through actual writer/read/guard code; fake Win32 only."""
import ctypes as C
from datetime import datetime,timedelta,timezone
import os,threading,unittest
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI,paste_latest,PasteEffectError,PasteSequenceDiagnostic
from f7hub.infrastructure.windows_selection_copy import Target
from f7hub.domain.clipboard import AdmittedManualText,ClipboardItemRef,ClipboardPasteAuthorization,ClipboardPasteSource
from uuid import uuid4

class Memory:
    def __init__(self,padding=0):self.blocks={};self.serial=1000;self.padding=padding;self.freed=[];self.unlocked=[]
    def GlobalAlloc(self,flags,size):
        self.serial+=1;self.blocks[self.serial]=C.create_string_buffer(size+self.padding);return self.serial
    def store(self,raw):
        h=self.GlobalAlloc(2,len(raw));C.memmove(C.addressof(self.blocks[h]),raw,len(raw));return h
    def GlobalLock(self,h):return C.addressof(self.blocks[h])
    def GlobalUnlock(self,h):self.unlocked.append(h);return True
    def GlobalSize(self,h):return C.sizeof(self.blocks[h])
    def GlobalFree(self,h):self.freed.append(h);self.blocks.pop(h,None);return None

class NativeClipboard:
    def __init__(self,memory,case='stable'):
        self.memory=memory;self.case=case;self.sequence=20;self.owner=self.expected_owner=123;self.open_owner=None
        self.formats={};self.closes=0;self.opens=0;self.sent=0;self.trace=[];self.read_formats=[];self.reads=0;self.owner_reads=0;self.input_calls=0
    def OpenClipboard(self,hwnd):
        self.opens+=1;self.trace.append('OPEN')
        if self.opens==2 and self.case=='verify_locked':return False
        if self.opens==2 and self.case=='change_before_read_lock':self.sequence+=1
        self.open_owner=hwnd;self.expected_owner=hwnd;return True
    def EmptyClipboard(self):self.trace.append('EMPTY');self.owner=self.open_owner;self.formats={};self.sequence+=1;return True
    def SetClipboardData(self,fmt,h):
        self.trace.append('SET')
        if self.case=='write_failure' and fmt==13:return None
        self.formats[fmt]=h;self.sequence+=1;return h
    def CloseClipboard(self):
        self.trace.append('CLOSE');self.closes+=1;self.open_owner=None
        if self.closes==1:
            if self.case in ('close_change','same_owner_different_text','external_writer','same_owner_equivalent','marker_changed','marker_missing','invalid_unicode','oversized_allocation'):
                self.sequence+=1
            if self.case in ('same_owner_different_text','external_writer'):
                self.formats[13]=self.memory.store(('Synthetic different text\0').encode('utf-16-le'))
            if self.case=='external_writer':self.owner=999999
            if self.case=='wrong_owner':self.owner=999999
            if self.case=='marker_changed':self.formats[101]=self.memory.store(b'\1\0\0\0')
            if self.case=='marker_missing':self.formats.pop(103,None)
            if self.case=='invalid_unicode':self.formats[13]=self.memory.store(b'\0\xd8\0\0')
            if self.case=='oversized_allocation':self.formats[13]=self.memory.GlobalAlloc(2,200000)
        if self.closes==2 and self.case=='change_after_verified_baseline':self.sequence+=1
        return not (self.case=='write_close_failure' and self.closes==1 or self.case=='read_close_failure' and self.closes==2)
    def GetClipboardSequenceNumber(self):
        self.trace.append('SEQUENCE');self.reads+=1
        if self.case=='zero_s1' and self.closes==0:return 0
        if self.case=='zero_s3' and self.closes>=2:return 0
        if self.case=='sequence_exception' and self.closes>=2:raise RuntimeError('PRIVATE SENTINEL')
        if self.closes>=1 and self.case=='zero_sequence':return 0
        if self.closes>=1 and self.case=='invalid_sequence':return -1
        return self.sequence
    def GetClipboardOwner(self):
        self.trace.append('OWNER');self.owner_reads+=1
        if self.case=='owner_observation_exception' and self.owner_reads==2:raise RuntimeError('PRIVATE SENTINEL')
        return self.owner
    def GetWindowThreadProcessId(self,hwnd,pid):pid._obj.value=os.getpid() if hwnd==self.expected_owner else os.getpid()+1;return 1
    def GetAsyncKeyState(self,key):return 0
    def IsClipboardFormatAvailable(self,fmt):return fmt in self.formats
    def GetClipboardData(self,fmt):
        self.trace.append('READ');self.read_formats.append(fmt)
        if self.case=='read_exception':raise RuntimeError('PRIVATE SENTINEL')
        return self.formats.get(fmt)
    def SendInput(self,count,events,size):self.trace.append('SEND');self.sent+=1;self.input_calls+=1;return count
    def text_is(self,text):
        h=self.formats[13];raw=C.string_at(C.addressof(self.memory.blocks[h]),C.sizeof(self.memory.blocks[h]));expected=(text+'\0').encode('utf-16-le');return raw[:len(expected)]==expected

def api_for(case='stable',padding=0):
    api=object.__new__(WindowsPasteAPI);api.kernel=Memory(padding);api.user=NativeClipboard(api.kernel,case);api.permissions=(101,102);api.exclusions=(103,104)
    api.target=Target(456,200);api.pin_paste=lambda t:900;api.unpin=lambda h:None;api.live=lambda h:True;api.foreground=lambda:api.target
    return api

class PostCloseVerificationTests(unittest.TestCase):
    def exercise(self,case='stable',text='Synthetic ordinary note',padding=0,diagnostic=False):
        api=api_for(case,padding);instant=datetime(2026,10,28,tzinfo=timezone.utc);d=PasteSequenceDiagnostic() if diagnostic else None
        def prepare(token):return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):return ClipboardPasteSource(auth,AdmittedManualText(text),(instant+timedelta(seconds=1)).isoformat())
        try:
            result=paste_latest(api,api.target,123,threading.Event(),prepare,consume,clock=lambda:100.,utc=lambda:instant,sequence_diagnostic=d);code='SUCCESS'
        except PasteEffectError as e:result=None;code=str(e);self.assertEqual(e.dispatch,'NOT_SENT');self.assertIn(e.clipboard,('WRITTEN','MAY_HAVE_CHANGED'))
        return api,result,code,d
    def denied(self,case):
        api,result,code,d=self.exercise(case);self.assertIsNone(result);self.assertEqual(api.user.sent,0);return api,code
    def test_verified_close_boundary_change_is_eligible(self):
        api,result,code,d=self.exercise('close_change');self.assertTrue(api.user.text_is('Synthetic ordinary note'));self.assertEqual(api.user.owner,123)
        self.assertEqual(result,('WRITTEN','DISPATCHED'),code);self.assertEqual(api.user.sent,1)
    def test_stable_authorized_state_is_eligible(self):
        api,result,code,d=self.exercise();self.assertEqual(result,('WRITTEN','DISPATCHED'));self.assertEqual(api.user.opens,2);self.assertEqual(api.user.closes,2)
    def test_external_writer_before_verification_is_rejected(self):self.denied('external_writer')
    def test_same_owner_different_text_is_rejected(self):self.denied('same_owner_different_text')
    def test_wrong_owner_is_rejected_before_text_read(self):
        api,code=self.denied('wrong_owner');self.assertNotIn(13,api.user.read_formats)
    def test_sequence_change_between_snapshot_and_read_lock_is_rejected(self):self.denied('change_before_read_lock')
    def test_sequence_change_after_verified_baseline_is_rejected(self):self.denied('change_after_verified_baseline')
    def test_zero_post_close_sequence_is_rejected(self):self.denied('zero_sequence')
    def test_invalid_post_close_sequence_is_rejected(self):self.denied('invalid_sequence')
    def test_failed_native_write_remains_rejected(self):self.denied('write_failure')
    def test_failed_write_close_never_reopens(self):
        api,code=self.denied('write_close_failure');self.assertEqual(code,'CLEANUP_FAILED');self.assertEqual(api.user.opens,1)
    def test_failed_read_close_is_rejected(self):
        api,code=self.denied('read_close_failure');self.assertEqual(code,'CLEANUP_FAILED')
    def test_read_lock_failure_has_no_retry(self):
        api,code=self.denied('verify_locked');self.assertEqual(api.user.opens,2)
    def test_verification_and_target_cleanup_failure_preserve_written_outcome(self):
        api=api_for('verify_locked')
        instant=datetime(2026,10,28,tzinfo=timezone.utc)
        def prepare(token):
            return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):
            return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),
                                        (instant+timedelta(seconds=1)).isoformat())
        def fail_unpin(handle):
            raise RuntimeError('PRIVATE SENTINEL')
        api.unpin=fail_unpin
        with self.assertRaises(PasteEffectError) as caught:
            paste_latest(api,api.target,123,threading.Event(),prepare,consume,
                         clock=lambda:100.,utc=lambda:instant)
        error=caught.exception
        self.assertEqual((str(error),error.clipboard,error.dispatch,error.guard),
                         ('CLEANUP_FAILED','WRITTEN','NOT_SENT','CLEANUP_HANDLE_CLOSE_FAILED'))
        self.assertIsInstance(error.__cause__,PasteEffectError)
        self.assertEqual(str(error.__cause__),'CLIPBOARD_VERIFY_LOCKED')
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))
        self.assertEqual(api.user.sent,0)

    def test_target_cleanup_failure_preserves_prewrite_and_partial_states(self):
        instant=datetime(2026,10,28,tzinfo=timezone.utc)
        def prepare(token):
            return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):
            return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),
                                        (instant+timedelta(seconds=1)).isoformat())
        for case,expected_state,expected_cause in (
            ('prewrite_locked','UNCHANGED','CLIPBOARD_LOCKED'),
            ('write_failure','MAY_HAVE_CHANGED','CLIPBOARD_WRITE_FAILED'),
        ):
            with self.subTest(case=case):
                api=api_for(case)
                if case=='prewrite_locked':
                    api.user.OpenClipboard=lambda hwnd:False
                def fail_unpin(handle):
                    raise RuntimeError('PRIVATE SENTINEL')
                api.unpin=fail_unpin
                with self.assertRaises(PasteEffectError) as caught:
                    paste_latest(api,api.target,123,threading.Event(),prepare,consume,
                                 clock=lambda:100.,utc=lambda:instant)
                error=caught.exception
                self.assertEqual((str(error),error.clipboard,error.dispatch),
                                 ('CLEANUP_FAILED',expected_state,'NOT_SENT'))
                self.assertIsInstance(error.__cause__,PasteEffectError)
                self.assertEqual(str(error.__cause__),expected_cause)
                self.assertEqual(api.user.sent,0)

    def test_verified_write_then_target_cleanup_failure_reports_dispatch(self):
        api=api_for()
        instant=datetime(2026,10,28,tzinfo=timezone.utc)
        def prepare(token):
            return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):
            return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),
                                        (instant+timedelta(seconds=1)).isoformat())
        def fail_unpin(handle):
            raise RuntimeError('PRIVATE SENTINEL')
        api.unpin=fail_unpin
        with self.assertRaises(PasteEffectError) as caught:
            paste_latest(api,api.target,123,threading.Event(),prepare,consume,
                         clock=lambda:100.,utc=lambda:instant)
        error=caught.exception
        self.assertEqual((str(error),error.clipboard,error.dispatch),
                         ('CLEANUP_FAILED','WRITTEN','DISPATCHED'))
        self.assertEqual(api.user.sent,1)
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))

    def _write_cleanup_failure(self, *, case='stable', target_cleanup=False,
                               close_mode='raises', prewrite=False, free_mode=None):
        api=api_for(case)
        instant=datetime(2026,10,28,tzinfo=timezone.utc)
        cancelled=threading.Event()
        close_error=OSError('Synthetic write close failure')
        free_error=OSError('Synthetic allocation cleanup failure')
        target_error=RuntimeError('Synthetic target cleanup failure')
        close,free,open_clipboard=api.user.CloseClipboard,api.kernel.GlobalFree,api.user.OpenClipboard
        closes=[];frees=[];unpins=[]
        def close_write():
            closes.append(1)
            result=close()
            if close_mode=='raises':
                raise close_error
            return False if close_mode=='false' else result
        def free_owned(handle):
            frees.append(handle)
            if len(frees)==1:
                if free_mode=='raises':
                    raise free_error
                if free_mode=='false':
                    return handle
            return free(handle)
        def open_write(hwnd):
            result=open_clipboard(hwnd)
            if prewrite:
                cancelled.set()  # Final guard fails after opening, before EmptyClipboard.
            return result
        def unpin(handle):
            unpins.append(handle)
            if target_cleanup:
                raise target_error
        api.user.CloseClipboard=close_write
        api.user.OpenClipboard=open_write
        api.kernel.GlobalFree=free_owned
        api.unpin=unpin
        def prepare(token):
            return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):
            return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),
                                        (instant+timedelta(seconds=1)).isoformat())
        with self.assertRaises(PasteEffectError) as caught:
            paste_latest(api,api.target,123,cancelled,prepare,consume,
                         clock=lambda:100.,utc=lambda:instant)
        error=caught.exception
        state='UNCHANGED' if prewrite else 'MAY_HAVE_CHANGED' if case=='write_failure' else 'WRITTEN'
        self.assertEqual((str(error),error.clipboard,error.dispatch),
                         ('CLEANUP_FAILED',state,'NOT_SENT'))
        self.assertEqual((len(closes),api.user.opens,api.user.closes,api.user.input_calls),(1,1,1,0))
        self.assertEqual(unpins,[900])
        self.assertEqual(len(frees),len(set(frees)))
        self.assertFalse(set(frees).intersection(api.user.formats.values()))
        cleanup=error.__cause__ if target_cleanup else error
        self.assertIsInstance(cleanup,PasteEffectError)
        self.assertEqual((str(cleanup),cleanup.clipboard,cleanup.dispatch),
                         ('CLEANUP_FAILED',state,'NOT_SENT'))
        if close_mode=='raises':
            self.assertIs(cleanup.__cause__,close_error)
        elif free_mode=='raises':
            self.assertIs(cleanup.__cause__,free_error)
        if target_cleanup:
            self.assertIs(error.__context__,target_error)
        self.assertEqual(len(frees),5 if prewrite else 1 if case=='write_failure' else 0)
        if free_mode is None:
            self.assertEqual(set(api.kernel.blocks),set(api.user.formats.values()))
        return api,error,cleanup,frees

    def test_exceptional_write_close_retains_completed_write(self):
        api,_,_,_=self._write_cleanup_failure()
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))
        self.assertEqual(api.kernel.freed,[])

    def test_exceptional_write_close_and_target_failure_retain_completed_write(self):
        api,_,_,_=self._write_cleanup_failure(target_cleanup=True)
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))
        self.assertEqual(api.kernel.freed,[])

    def test_exceptional_write_close_and_target_failure_free_partial_write(self):
        api,_,_,frees=self._write_cleanup_failure(case='write_failure',target_cleanup=True)
        self.assertNotIn(13,api.user.formats)
        self.assertEqual(api.kernel.freed,frees)

    def test_false_write_close_preserves_complete_and_partial_states(self):
        for case in ('stable','write_failure'):
            with self.subTest(case=case):
                self._write_cleanup_failure(case=case,target_cleanup=True,close_mode='false')

    def test_exceptional_write_close_before_modification_retains_unchanged(self):
        api,_,_,frees=self._write_cleanup_failure(prewrite=True,target_cleanup=True)
        self.assertNotIn('EMPTY',api.user.trace)
        self.assertEqual(api.kernel.freed,frees)
        self.assertEqual(api.kernel.blocks,{})

    def test_write_close_and_free_exception_still_attempt_all_owned_allocations(self):
        api,_,_,frees=self._write_cleanup_failure(prewrite=True,target_cleanup=True,free_mode='raises')
        self.assertEqual(api.kernel.freed,frees[1:])
        self.assertEqual(set(api.kernel.blocks),{frees[0]})
        self.assertNotIn('EMPTY',api.user.trace)

    def test_free_exception_or_false_result_does_not_skip_remaining_allocations(self):
        for free_mode in ('raises','false'):
            with self.subTest(free_mode=free_mode):
                api,_,_,frees=self._write_cleanup_failure(prewrite=True,target_cleanup=True,
                                                       close_mode='success',free_mode=free_mode)
                self.assertEqual(api.kernel.freed,frees[1:])
                self.assertEqual(set(api.kernel.blocks),{frees[0]})

    def _readback_close_failure(self, *, raises=True, target_cleanup=False, case='stable'):
        api=api_for(case)
        instant=datetime(2026,10,28,tzinfo=timezone.utc)
        close_error=OSError('Synthetic readback close failure')
        target_error=RuntimeError('Synthetic target close failure')
        close=api.user.CloseClipboard
        unpins=[]
        def close_readback():
            result=close()
            if api.user.closes==2:
                if raises:
                    raise close_error
                return False
            return result
        def unpin(handle):
            unpins.append(handle)
            if target_cleanup:
                raise target_error
        api.user.CloseClipboard=close_readback
        api.unpin=unpin
        def prepare(token):
            return ClipboardPasteAuthorization(str(uuid4()),str(uuid4()),ClipboardItemRef(1),1,token)
        def consume(auth):
            return ClipboardPasteSource(auth,AdmittedManualText('Synthetic ordinary note'),
                                        (instant+timedelta(seconds=1)).isoformat())
        with self.assertRaises(PasteEffectError) as caught:
            paste_latest(api,api.target,123,threading.Event(),prepare,consume,
                         clock=lambda:100.,utc=lambda:instant)
        error=caught.exception
        self.assertEqual((str(error),error.clipboard,error.dispatch),
                         ('CLEANUP_FAILED','WRITTEN','NOT_SENT'))
        self.assertEqual((api.user.opens,api.user.closes,api.user.input_calls),(2,2,0))
        self.assertEqual(unpins,[900])
        return api,error,close_error,target_error

    def test_exceptional_readback_close_and_target_cleanup_preserve_written_and_cause(self):
        api,error,close_error,target_error=self._readback_close_failure(target_cleanup=True)
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))
        self.assertIsInstance(error.__cause__,PasteEffectError)
        self.assertEqual((str(error.__cause__),error.__cause__.clipboard,error.__cause__.dispatch),
                         ('CLEANUP_FAILED','WRITTEN','NOT_SENT'))
        self.assertIs(error.__cause__.__cause__,close_error)
        self.assertIs(error.__context__,target_error)
        self.assertEqual(api.kernel.freed,[])
        self.assertEqual(len(api.kernel.unlocked),10)

    def test_exceptional_readback_close_with_successful_target_cleanup_retains_cause(self):
        api,error,close_error,_=self._readback_close_failure()
        self.assertIs(error.__cause__,close_error)
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))

    def test_content_rejection_survives_exceptional_or_false_readback_close(self):
        for raises in (True,False):
            with self.subTest(close_raises=raises):
                api,error,close_error,_=self._readback_close_failure(
                    raises=raises,target_cleanup=True,case='same_owner_different_text')
                pending=[error];seen=set();errors=[]
                while pending:
                    current=pending.pop()
                    if id(current) in seen:
                        continue
                    seen.add(id(current));errors.append(current)
                    pending.extend(e for e in (current.__cause__,current.__context__) if e is not None)
                self.assertTrue(any(isinstance(e,PasteEffectError)
                                    and str(e)=='CLIPBOARD_CONTENT_MISMATCH' for e in errors))
                if raises:
                    self.assertIn(close_error,errors)
                self.assertFalse(api.user.text_is('Synthetic ordinary note'))

    def test_false_readback_close_and_target_cleanup_preserve_written(self):
        api,error,_,_=self._readback_close_failure(raises=False,target_cleanup=True)
        self.assertIsInstance(error.__cause__,PasteEffectError)
        self.assertEqual(str(error.__cause__),'CLEANUP_FAILED')
        self.assertTrue(api.user.text_is('Synthetic ordinary note'))

    def test_read_failure_is_fixed_and_content_free(self):
        api,code=self.denied('read_exception');self.assertEqual(code,'CLIPBOARD_VERIFY_FAILED');self.assertNotIn('PRIVATE',code)
    def test_missing_or_modified_privacy_markers_are_rejected(self):
        for case in ('marker_missing','marker_changed'):
            with self.subTest(case=case):api,code=self.denied(case);self.assertNotIn(13,api.user.read_formats)
    def test_invalid_unicode_is_rejected(self):self.denied('invalid_unicode')
    def test_oversized_native_allocation_is_rejected(self):self.denied('oversized_allocation')
    def test_full_unicode_and_allocator_padding_are_preserved(self):
        text='Synthetic multiline\r\n\U0001f642 e\u0301 note';api,result,code,d=self.exercise(text=text,padding=8);self.assertEqual(result,('WRITTEN','DISPATCHED'));self.assertTrue(api.user.text_is(text))
    def test_maximum_authorized_ascii_size_remains_eligible(self):
        api,result,code,d=self.exercise(text='Z'*65536,padding=8);self.assertEqual(result,('WRITTEN','DISPATCHED'))
    def test_identical_same_owner_state_has_no_producer_attribution(self):
        api,result,code,d=self.exercise('same_owner_equivalent');self.assertEqual(result,('WRITTEN','DISPATCHED')) # Exact same semantic state is indistinguishable; not provenance proof.
    def test_post_write_expiry_reports_written_and_no_dispatch(self):
        api=api_for();calls=[]
        def check():
            calls.append(1)
            if len(calls)==2:raise PasteEffectError('EXPIRED')
        with self.assertRaises(PasteEffectError) as caught:api.write_text('Synthetic ordinary note',123,check)
        self.assertEqual((str(caught.exception),caught.exception.clipboard,caught.exception.dispatch),('EXPIRED','WRITTEN','NOT_SENT'))
        self.assertEqual(api.user.sent,0)
    def test_post_read_cancellation_releases_read_lock(self):
        api=api_for();calls=[]
        def check():
            calls.append(1)
            if len(calls)==4:raise PasteEffectError('CANCELLED')
        with self.assertRaises(PasteEffectError) as caught:api.write_text('Synthetic ordinary note',123,check)
        self.assertEqual(caught.exception.clipboard,'WRITTEN');self.assertEqual(api.user.closes,2)
    def test_borrowed_read_handles_are_unlocked_not_freed(self):
        api,result,code,d=self.exercise();self.assertEqual(result,('WRITTEN','DISPATCHED'));self.assertEqual(api.kernel.freed,[])
        self.assertEqual(api.user.read_formats,[101,102,103,104,13]);self.assertEqual(len(api.kernel.unlocked),10)
    def test_same_hwnd_with_wrong_process_is_rejected_without_reading(self):
        api=api_for()
        def wrong_pid(hwnd,pid):pid._obj.value=os.getpid()+1;return 1
        api.user.GetWindowThreadProcessId=wrong_pid
        with self.assertRaises(PasteEffectError):api.write_text('Synthetic ordinary note',123,lambda:None)
        self.assertEqual(api.user.read_formats,[]);self.assertEqual(api.user.sent,0)
    def test_change_during_content_read_is_rejected_and_unlocks(self):
        api=api_for();original=api.user.GetClipboardData
        def changed(fmt):
            handle=original(fmt)
            if fmt==13:api.user.sequence+=1
            return handle
        api.user.GetClipboardData=changed
        with self.assertRaises(PasteEffectError) as caught:api.write_text('Synthetic ordinary note',123,lambda:None)
        self.assertEqual(str(caught.exception),'CLIPBOARD_CHANGED');self.assertEqual(api.user.closes,2)
    def test_invalid_global_size_is_rejected_before_lock(self):
        api=api_for();api.kernel.GlobalSize=lambda h:0
        with self.assertRaises(PasteEffectError) as caught:api.write_text('Synthetic ordinary note',123,lambda:None)
        self.assertEqual(str(caught.exception),'CLIPBOARD_VERIFY_FAILED');self.assertEqual(api.user.sent,0)
    def test_diagnostic_still_never_dispatches_after_verified_boundary(self):
        api,result,code,d=self.exercise('close_change',diagnostic=True);self.assertEqual(result,('WRITTEN','NOT_SENT'));self.assertEqual(api.user.sent,0)
        summary=d.summary('GUARDS_PASSED_NO_DISPATCH','WRITTEN');self.assertIn('D12=CHANGED',summary);self.assertIn('D23=SAME',summary);self.assertNotIn('Synthetic',summary)
