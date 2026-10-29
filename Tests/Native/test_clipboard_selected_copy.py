"""Opt-in real Windows Clipboard and native Qt paste; QTest input, not physical.

Prior MIME representations are held only in RAM for guarded restoration. No
prior content is printed, persisted or included in assertions/screenshots.
"""
import os,time,json
from pathlib import Path
from datetime import datetime,timezone
import unittest
from PySide6.QtCore import Qt,QMimeData
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QPlainTextEdit
from Tests.Database.test_clipboard_consent import _ConsentFixture
from Tests.Database.clipboard_fixtures import seed_item,FixtureCapture
from f7hub.gui.clipboard_workspace import ClipboardWorkspace
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI
from f7hub.infrastructure.database import database_connection


@unittest.skipUnless(os.name=="nt" and os.environ.get("F7HUB_CP02S4_NATIVE_ARTIFACT_DIR"),
                     "Explicit Windows-native artifact directory required")
class SelectedCopyNativeTests(_ConsentFixture):
    def test_actual_clipboard_complete_text_native_paste_and_validation_rejection(self):
        app=QApplication.instance() or QApplication([])
        self.assertEqual(app.platformName(),"windows")
        self.grant();self.service._clock=lambda:datetime(2026,10,8,12,tzinfo=timezone.utc)
        first="Synthetic first\r\nRésumé 😀 "+"x"*300
        second="Synthetic second\n東京"
        expected=second+"\n\n"+first
        with database_connection(self.database_path) as c:
            seed_item(c,raw_text=first,captures=(FixtureCapture(),FixtureCapture()))
            second_id=seed_item(c,raw_text=second)
        window=QWidget();window.setWindowTitle("F7Hub CP02-S4 synthetic native acceptance")
        layout=QVBoxLayout(window)
        workspace=ClipboardWorkspace(window,clipboard_service=self.service,settings_service=self.settings)
        editor=QPlainTextEdit(window);editor.setAccessibleName("Synthetic paste destination")
        editor.setPlaceholderText("Synthetic native paste destination")
        layout.addWidget(workspace,3);layout.addWidget(editor,1);window.resize(1000,700)
        api=WindowsPasteAPI();clipboard=app.clipboard();snapshot=QMimeData();old=clipboard.mimeData()
        formats=list(old.formats()) if old is not None else []
        self.assertLessEqual(len(formats),32,"Too many prior formats to preserve safely; no test write")
        total=0
        for fmt in formats:
            data=old.data(fmt);total+=data.size()
            self.assertLessEqual(total,4*1024*1024,"Prior MIME exceeds preservation budget; no test write")
            snapshot.setData(fmt,data)
        record={"environment":"WINDOWS_NATIVE","input":"QTEST_SYNTHETIC",
                "started_at":datetime.now(timezone.utc).isoformat(),"ready":False,
                "assertions":[],"screenshots":[],"prior_content_persisted":False,
                "restoration":"NOT NEEDED"}
        artifact=Path(os.environ["F7HUB_CP02S4_NATIVE_ARTIFACT_DIR"])
        owned_sequence=None
        def idle():
            end=time.monotonic()+5
            while workspace.loading and time.monotonic()<end:
                app.processEvents();time.sleep(.005)
            self.assertFalse(workspace.loading,"Native worker did not settle within five seconds")
        try:
            window.show();self.assertTrue(QTest.qWaitForWindowExposed(window,3000))
            workspace.activate();idle();record["ready"]=True
            workspace.select_all_button.click()
            self.assertEqual(workspace.copy_selected_button.text(),"Copy Selected (2)")
            workspace.copy_selected_button.click();idle()
            if api.user.GetClipboardOwner()==int(window.winId()):
                owned_sequence=api.sequence()
            self.assertIn("Use Ctrl+V",workspace.status_message.text())
            self.assertIsNotNone(owned_sequence)
            self.assertEqual(api.user.GetClipboardOwner(),int(window.winId()))
            self.assertTrue(api.user.OpenClipboard(int(window.winId())))
            try:
                raw=api._bytes(13,131200)[:len((expected+"\0").encode("utf-16-le"))]
                self.assertTrue(raw==(expected+"\0").encode("utf-16-le"),"Synthetic native text differs")
            finally:self.assertTrue(api.user.CloseClipboard())
            self.assertEqual(api.sequence(),owned_sequence)
            record["assertions"].append("Exact complete Unicode/CRLF text and two-newline separator verified through native CF_UNICODETEXT")
            editor.setFocus();QTest.keyClick(editor,Qt.Key.Key_V,Qt.KeyboardModifier.ControlModifier);app.processEvents()
            self.assertEqual(api.sequence(),owned_sequence)
            self.assertTrue(editor.toPlainText()==expected.replace("\r\n","\n"),"Synthetic Ctrl+V text differs")
            record["assertions"].append("QTest Ctrl+V pasted actual OS Clipboard into native Qt destination; no input dispatch by copy action")
            for width,height in ((1000,700),(660,500)):
                window.resize(width,height);app.processEvents()
                self.assertTrue(workspace.copy_selected_button.isVisible())
                self.assertGreater(workspace.copy_selected_button.width(),0)
                target=artifact/f"native-{window.width()}x{window.height()}.png"
                self.assertTrue(window.grab().save(str(target)))
                record["screenshots"].append({"path":str(target),"width":window.width(),"height":window.height(),
                                                "device_pixel_ratio":window.devicePixelRatioF(),"requested_size":[width,height]})
            with database_connection(self.database_path) as c:
                c.execute("DELETE FROM clipboard_items WHERE clipboard_item_id=?",(second_id,))
            workspace.copy_selected_button.click();idle()
            self.assertEqual(api.sequence(),owned_sequence)
            self.assertIn("Refresh",workspace.status_message.text())
            self.assertEqual(workspace.model.selected_items(),())
            record["assertions"].append("One deleted member rejected the full selection; native sequence unchanged")
            record["result"]="PASS"
        finally:
            # Respect newer external/user writes. Restoration is test cleanup,
            # not product behavior or an automatic retry of Copy Selected.
            if owned_sequence is not None and api.sequence()==owned_sequence:
                if formats:clipboard.setMimeData(snapshot)
                else:clipboard.clear()
                app.processEvents()
                restored=clipboard.mimeData()
                self.assertTrue(all(restored is not None and bytes(restored.data(fmt))==bytes(snapshot.data(fmt))
                                    for fmt in formats),"Prior MIME restoration verification failed; content withheld")
                record["restoration"]="PRIOR MIME REPRESENTATIONS RESTORED" if formats else "PRIOR EMPTY CLIPBOARD RESTORED"
            elif owned_sequence is not None:
                record["restoration"]="NEWER CLIPBOARD PRESERVED; NO RESTORATION"
            idle();window.close();window.deleteLater();app.processEvents()
            record["completed_at"]=datetime.now(timezone.utc).isoformat()
            (artifact/"native-validation.details.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
