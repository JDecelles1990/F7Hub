"""CP02-S3 basename profile and original-target acquisition; synthetic only."""
import ctypes
import threading
import unittest
from ctypes import wintypes as W
from unittest.mock import Mock
from f7hub.domain.clipboard import ClipboardSelectionAcquisition, normalize_source_process_basename
from f7hub.infrastructure.windows_selection_copy import WindowsSelectionAPI, Target, copy_selection, SelectionCopyError
from Tests.Unit.test_windows_selection_copy import FakeAPI

class SourceProcessProfileTests(unittest.TestCase):
    def test_normalization_unicode_bounds_and_private_repr(self):
        for raw, expected in [('NOTEPAD.EXE','notepad.exe'),('E\u0301diteur.EXE','éditeur.exe'),('😀'*251+'.exe','😀'*251+'.exe')]:
            self.assertEqual(normalize_source_process_basename(raw),expected)
            self.assertEqual(normalize_source_process_basename(expected),expected)
        result=ClipboardSelectionAcquisition('SYNTHETIC SELECTED CONTENT','notepad.exe')
        self.assertNotIn('SYNTHETIC',repr(result)); self.assertNotIn('notepad',repr(result))

    def test_invalid_optional_values_are_omitted(self):
        for value in (None,1,b'a.exe','','.exe',' a.exe','.hidden.exe','a.exe ','a.dll','a'*252+'.exe',
                      '😀'*252+'.exe','C:\\Private\\notepad.exe','../a.exe','https://example.invalid/a.exe',
                      'a:stream.exe','title<secret>.exe','a\x00.exe','a\n.exe','a\x85.exe',
                      'a\u202e.exe','a\u200d.exe','a\u2028.exe','a\ud800.exe'):
            with self.subTest(kind=type(value).__name__):
                self.assertIsNone(normalize_source_process_basename(value))
                self.assertIsNone(ClipboardSelectionAcquisition('ordinary note',value).source_process_basename)

    def test_native_reuses_one_required_original_target_query(self):
        api=object.__new__(WindowsSelectionAPI); api.kernel,api.advapi,api.user=Mock(),Mock(),Mock()
        api.kernel.OpenProcess.return_value=999
        def image(handle,flags,buffer,size):
            self.assertEqual(handle,999); buffer.value='C:\\SyntheticPrivateFolder\\NOTEPAD.EXE'; return True
        def token(handle,kind,output,size,used):
            ctypes.cast(output,ctypes.POINTER(W.DWORD)).contents.value=0
            ctypes.cast(used,ctypes.POINTER(W.DWORD)).contents.value=4
            return True
        api.kernel.QueryFullProcessImageNameW.side_effect=image
        api.advapi.GetTokenInformation.side_effect=token
        names=[]; handle=api.pin(Target(100,987654),on_source_process=names.append)
        self.assertEqual(names,['notepad.exe']); api.kernel.QueryFullProcessImageNameW.assert_called_once()
        api.kernel.OpenProcess.assert_called_once_with(0x101000,False,987654)
        api.user.GetClipboardOwner.assert_not_called(); api.unpin(handle)
        self.assertEqual(api.kernel.CloseHandle.call_args.args,(999,))

    def test_failed_pin_never_emits_provenance(self):
        api=object.__new__(WindowsSelectionAPI); api.kernel=Mock()
        api.kernel.QueryFullProcessImageNameW.return_value=False; callback=Mock()
        with self.assertRaises(SelectionCopyError): api.pin(Target(100,987654),on_source_process=callback)
        callback.assert_not_called(); api.kernel.CloseHandle.assert_called_once()

    def test_copy_typed_result_is_delivered_after_handle_cleanup(self):
        api=FakeAPI(); api.source_process_basename='MSEdge.EXE'
        result=copy_selection(api,api.target,threading.Event(),with_metadata=True)
        self.assertIs(type(result),ClipboardSelectionAcquisition)
        self.assertEqual((result.text,result.source_process_basename),('NEW SELECTED TEXT','msedge.exe'))
        self.assertEqual((api.closed,api.sent),(1,1))
