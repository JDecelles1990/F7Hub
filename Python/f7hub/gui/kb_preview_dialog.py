"""Thin standalone host for the shared synthetic editor."""

from PySide6.QtWidgets import QDialog, QVBoxLayout

from f7hub.gui.kb_preview_editor import KBPreviewEditor
from f7hub.services.kb_lab_session import SyntheticLabSession


class KBPreviewDialog(QDialog):
    def __init__(self, session: SyntheticLabSession, parent=None):
        super().__init__(parent)
        self._session = session
        self._closed = False
        self._transitioning = False
        self.setWindowTitle("KB-SG02 — Synthetic Preview Lab")
        self.resize(1080, 780)
        self.setMinimumSize(860, 620)
        self.editor = KBPreviewEditor(session.service, session.snapshots, self)
        self.editor.close_requested.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

    def done(self, result):
        if self._closed or self._transitioning:
            return
        self._transitioning = True
        try:
            if not self.editor.confirm_close():
                return
            self.editor.commit_close()
            self._session.invalidate()
            self._closed = True
            super().done(QDialog.DialogCode.Rejected)
        finally:
            self._transitioning = False

    def reject(self):
        self.done(QDialog.DialogCode.Rejected)

    def accept(self):
        self.reject()  # Enter/accept cannot grant any stronger meaning.

    def closeEvent(self, event):
        self.reject()
        event.setAccepted(self._closed)
