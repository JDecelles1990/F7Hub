"""Real SQLite/consent/GUI/service to synthetic OS delivery; no Clipboard writes."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from datetime import datetime,timezone
import threading,time
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from Tests.Database.test_clipboard_consent import _ConsentFixture
from Tests.Database.clipboard_fixtures import seed_item,FixtureCapture
from f7hub.gui.clipboard_workspace import ClipboardWorkspace
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED
from f7hub.infrastructure.database import database_connection,validate_database_integrity


class SelectedCopyFlowTests(_ConsentFixture):
    def test_complete_flow_order_source_metadata_no_writes_and_revocation(self):
        app=QApplication.instance() or QApplication([]); self.grant()
        self.service._clock=lambda:datetime(2026,10,8,12,tzinfo=timezone.utc)
        with database_connection(self.database_path) as c:
            seed_item(c,raw_text="Synthetic first\nRésumé 😀 "+"x"*300,captures=(FixtureCapture(),FixtureCapture()))
            seed_item(c,raw_text="Synthetic second\r\n東京")
            before=tuple(c.iterdump())
        effects=[]
        def deliver(text,owner,guard):
            guard(); effects.append((text,threading.get_ident()));return "WRITTEN"
        w=ClipboardWorkspace(clipboard_service=self.service,settings_service=self.settings,copy_delivery=deliver)
        def idle():
            end=time.monotonic()+4
            while w.loading and time.monotonic()<end:
                app.processEvents();time.sleep(.005)
            self.assertFalse(w.loading)
        try:
            w.show();w.activate();idle();w.select_all_button.click()
            self.assertEqual(w.copy_selected_button.text(),"Copy Selected (2)")
            w.copy_selected_button.click();idle()
            self.assertEqual(len(effects),1,w.status_message.text())
            self.assertEqual(effects[0][0],"Synthetic second\r\n東京\n\nSynthetic first\nRésumé 😀 "+"x"*300)
            self.assertNotEqual(effects[0][1],threading.get_ident())
            with database_connection(self.database_path,read_only=True) as c:
                self.assertEqual(tuple(c.iterdump()),before)
                self.assertEqual(validate_database_integrity(c),(("ok",),()))
            snapshot=self.settings.refresh();self.settings.apply({WORKFLOW_ENABLED:False},expected_revision=snapshot.revision)
            w.copy_selected_button.click();idle();self.assertEqual(len(effects),1)
            self.assertEqual(w.model.selected_items(),())
        finally:
            idle();w.close();w.deleteLater();app.processEvents()
