"""CP02-S4 model and asynchronous GUI, synthetic service/native boundary."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import threading
import time
import unittest
from dataclasses import replace
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QKeyEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from Tests.GUI import test_clipboard_workspace as fixture
from f7hub.gui.clipboard_workspace import ClipboardWorkspace, ClipboardRecentTableModel
from f7hub.domain.clipboard import ClipboardCopyError


class CopyService(fixture.RecordingClipboardService):
    def __init__(self):
        super().__init__(); self.copy_calls=[]; self.copy_gate=None; self.copy_error=None
    def copy_selected(self, selection, deliver):
        self.copy_calls.append((selection, threading.get_ident()))
        if self.copy_gate is not None and not self.copy_gate.wait(3):
            raise ClipboardCopyError("TIMEOUT")
        if self.copy_error is not None: raise self.copy_error
        return deliver("Synthetic complete source", lambda: None)


class SelectedCopyGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.service=CopyService(); self.effects=[]
        def deliver(text, owner, guard):
            guard(); self.effects.append((text,owner,threading.get_ident())); return "WRITTEN"
        self.workspace=ClipboardWorkspace(clipboard_service=self.service,copy_delivery=deliver)
        self.workspace.resize(1000,500); self.workspace.show(); self.workspace.activate(); self.wait_idle()
    def tearDown(self):
        if self.service.copy_gate is not None: self.service.copy_gate.set()
        self.wait_idle(); self.workspace.close(); self.workspace.deleteLater(); self.app.processEvents()
    def wait_idle(self):
        end=time.monotonic()+4
        while self.workspace.loading and time.monotonic()<end: QTest.qWait(5)
        self.assertFalse(self.workspace.loading)
    def check(self,row,state=Qt.CheckState.Checked):
        model=self.workspace.model
        return model.setData(model.index(row,model.CHECK_COLUMN),state,Qt.ItemDataRole.CheckStateRole)

    def test_zero_selection_and_individual_toggle_count_no_effect(self):
        w=self.workspace; self.assertEqual(w.copy_selected_button.text(),"Copy Selected (0)")
        self.assertFalse(w.copy_selected_button.isEnabled()); self.assertTrue(self.check(1))
        self.assertEqual(w.selected_count.text(),"1 selected"); self.assertTrue(w.copy_selected_button.isEnabled())
        self.assertEqual(self.effects,[]); self.check(1,Qt.CheckState.Unchecked)
        self.assertFalse(w.copy_selected_button.isEnabled()); self.assertFalse(w.copy_selected())

    def test_select_all_clear_and_visible_only_limit(self):
        w=self.workspace; w.select_all_button.click()
        self.assertEqual(len(w.model.selected_items()),2); self.assertFalse(w.select_all_button.isEnabled())
        w.clear_selection_button.click(); self.assertEqual(w.model.selected_items(),())
        row=self.service.page.rows[0]
        from f7hub.domain.clipboard import ClipboardItemRef
        w.model.replace_rows(tuple(replace(row,item_ref=ClipboardItemRef(i)) for i in range(1,101)))
        w.select_all_button.click(); self.assertEqual(len(w.model.selected_items()),100)
        self.assertEqual(self.effects,[])

    def test_copy_uses_display_order_async_and_retains_checks(self):
        self.check(1); self.check(0); self.workspace.copy_selected_button.click(); self.wait_idle()
        request,worker=self.service.copy_calls[0]
        self.assertEqual([i.item_ref.clipboard_item_id for i in request],[1,2])
        self.assertNotEqual(worker,threading.get_ident()); self.assertEqual(self.effects[0][2],worker)
        self.assertGreater(self.effects[0][1],0); self.assertEqual(len(self.effects),1)
        self.assertEqual(self.workspace.copy_selected_button.text(),"Copy Selected (2)")
        self.assertIn("Use Ctrl+V",self.workspace.status_message.text())

    def test_pending_freezes_selection_and_refuses_navigation_refresh_exit(self):
        w=self.workspace; self.service.copy_gate=threading.Event(); self.check(0)
        self.assertTrue(w.copy_selected()); self.assertFalse(self.check(1))
        self.assertFalse(w.copy_selected_button.isEnabled()); self.assertFalse(w.refresh())
        self.assertFalse(w.select_source("windows")); self.assertFalse(w.confirm_leave())
        self.assertFalse(w.copy_selected()); self.assertFalse(w.close())
        self.service.copy_gate.set(); self.wait_idle(); self.assertTrue(w.copy_selected_button.isEnabled())

    def test_completion_interval_cannot_dispatch_another_copy(self):
        w=self.workspace; results=[]
        w.runner.busy_changed.connect(lambda busy: results.append(w.copy_selected()) if not busy else None)
        self.check(0); w.copy_selected(); self.wait_idle()
        self.assertEqual(results,[False]); self.assertEqual(len(self.effects),1)

    def test_refresh_source_departure_and_revision_replacement_clear(self):
        w=self.workspace; self.check(0); w.refresh(); self.wait_idle()
        self.assertEqual(w.model.selected_items(),()); self.check(0)
        self.assertTrue(w.select_source("windows")); self.assertEqual(w.model.selected_items(),())
        self.assertFalse(w.copy_selected()); w.select_source("f7hub"); self.check(0); w.leave()
        self.assertEqual(w.model.selected_items(),()); self.check(0)
        rows=tuple(replace(r,revision=r.revision+1) for r in self.service.page.rows)
        w.model.replace_rows(rows); self.assertEqual(w.model.selected_items(),())

    def test_keyboard_space_arrows_tab_and_accessible_state(self):
        w=self.workspace; w.table.setFocus(); w.table.setCurrentIndex(w.model.index(0,0))
        QTest.keyClick(w.table,Qt.Key.Key_Space); self.assertEqual(len(w.model.selected_items()),1)
        QTest.keyClick(w.table,Qt.Key.Key_Down); QTest.keyClick(w.table,Qt.Key.Key_Space)
        self.assertEqual(len(w.model.selected_items()),2)
        index=w.model.index(1,w.model.CHECK_COLUMN)
        self.assertIn("checked",w.model.data(index,Qt.ItemDataRole.AccessibleTextRole))
        QTest.keyClick(w.table,Qt.Key.Key_Tab); self.assertIsNot(self.app.focusWidget(),w.table)
        self.assertEqual(self.effects,[])

    def test_mouse_check_and_text_columns_stay_read_only(self):
        w=self.workspace; self.assertEqual(w.table.horizontalHeader().visualIndex(w.model.CHECK_COLUMN),0)
        index=w.model.index(0,w.model.CHECK_COLUMN)
        rect=w.table.visualRect(index)
        QTest.mouseClick(w.table.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(rect.left()+8,rect.center().y()))
        self.assertEqual(len(w.model.selected_items()),1)
        for column in range(w.model.CHECK_COLUMN):
            index=w.model.index(0,column)
            self.assertFalse(w.model.flags(index)&Qt.ItemFlag.ItemIsEditable)
            self.assertFalse(w.model.setData(index,"overwrite"))

    def test_stale_denial_clears_and_hides_exception_text(self):
        self.check(0); self.service.copy_error=ClipboardCopyError("STALE_SELECTION")
        self.workspace.copy_selected(); self.wait_idle()
        self.assertEqual(self.workspace.model.selected_items(),()); self.assertEqual(self.effects,[])
        self.assertIn("Refresh",self.workspace.status_message.text())

    def test_uncertain_write_is_not_retried_or_reported_unchanged(self):
        self.check(0); self.service.copy_error=ClipboardCopyError("CLEANUP_FAILED","WRITTEN")
        self.workspace.copy_selected(); self.wait_idle()
        self.assertIn("may have changed",self.workspace.status_message.text())
        self.assertEqual(len(self.service.copy_calls),1)

    def test_unknown_error_is_content_free_and_stale_completion_ignored(self):
        self.check(0); self.service.copy_error=RuntimeError("Synthetic private detail")
        self.workspace.copy_selected(); self.wait_idle()
        self.assertNotIn("private",self.workspace.status_message.text())
        before=self.workspace.status_message.text()
        self.workspace._copy_completed(-1,"WRITTEN")
        self.assertEqual(self.workspace.status_message.text(),before)

    def test_setup_navigation_preserves_existing_read_behavior_but_blocks_copy(self):
        from Tests.GUI.test_clipboard_setup import RecordingSettingsService
        self.workspace.close();self.workspace.deleteLater();self.app.processEvents()
        w=ClipboardWorkspace(clipboard_service=self.service,settings_service=RecordingSettingsService(),
                             copy_delivery=lambda text,owner,guard:"WRITTEN")
        self.workspace=w;w.show();self.service.gate=threading.Event();w.activate()
        try:
            self.assertTrue(w.show_setup())  # Existing read-only Recent does not block Setup.
        finally:self.service.gate.set()
        end=time.monotonic()+4
        while (w.loading or w.settings_pending) and time.monotonic()<end:
            self.app.processEvents();time.sleep(.005)
        self.assertFalse(w.loading or w.settings_pending);self.assertTrue(w.show_recent())
        self.check(0);self.service.copy_gate=threading.Event();self.assertTrue(w.copy_selected())
        self.assertFalse(w.show_setup());self.service.copy_gate.set();self.wait_idle()
