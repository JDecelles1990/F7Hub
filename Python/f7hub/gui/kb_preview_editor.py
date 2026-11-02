"""Reusable temporary editor; storage and terminal invalidation belong to its host."""

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from f7hub.services.kb_preview_service import (
    KBPreviewService, NOTICE, PreviewAdmissionError, PreviewUnavailableError, validate_edit,
)


class KBPreviewEditor(QWidget):
    close_requested = Signal()

    def __init__(self, service: KBPreviewService, snapshots: tuple, parent=None):
        super().__init__(parent)
        self._service = service
        self._snapshots = snapshots
        self._current_index = 0
        self._preview = None
        self._baseline = ("", "", "", "")
        self._accepted = dict(zip(("title", "summary", "body", "annotations"), self._baseline))
        self._transitioning = False
        self._closed = False
        self.notice = QLabel(NOTICE, self)
        self.notice.setWordWrap(True)
        self.notice.setTextFormat(Qt.TextFormat.PlainText)
        self.notice.setAccessibleName(NOTICE)
        self.fixture_selector = QComboBox(self)
        self.fixture_selector.setAccessibleName("Select a synthetic fixture")
        self.fixture_selector.addItem("Select a synthetic fixture…")
        for snapshot in snapshots:
            self.fixture_selector.addItem(f"{snapshot.fixture.fixture_id} — {snapshot.fixture.title}")
        self.source_display = QPlainTextEdit(self)
        self.source_display.setReadOnly(True)
        self.source_display.setAccessibleName("Synthetic source and proposal provenance, read only")
        self.source_display.setTabChangesFocus(True)
        self.title_input = QLineEdit(self)
        self.summary_input = QLineEdit(self)
        for editor, name in ((self.title_input, "Temporary title"), (self.summary_input, "Temporary summary")):
            editor.setMaxLength(131072)  # Application limits reject, rather than silently truncate.
            editor.setAccessibleName(name)
        self.body_input = QPlainTextEdit(self)
        self.body_input.setAccessibleName("Temporary KB body, plain text")
        self.body_input.setTabChangesFocus(True)
        self.annotations_input = QPlainTextEdit(self)
        self.annotations_input.setAccessibleName("Temporary review annotations, no acceptance authority")
        self.annotations_input.setTabChangesFocus(True)
        self.annotations_input.setMaximumHeight(100)
        self.feedback = QLabel("Select a fixture to begin. No article will be saved.", self)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        self.close_button = QPushButton("Close", self)
        self.close_button.setAutoDefault(False)
        self.close_button.clicked.connect(self.close_requested.emit)
        self._editors = {"title": self.title_input, "summary": self.summary_input,
                         "body": self.body_input, "annotations": self.annotations_input}
        for name, editor in self._editors.items():
            editor.setEnabled(False)
            editor.textChanged.connect(lambda *_, name=name: self._edited(name))
        form = QFormLayout()
        form.addRow("&Title", self.title_input)
        form.addRow("&Summary", self.summary_input)
        form.addRow("&Body", self.body_input)
        form.addRow("Review &annotations", self.annotations_input)
        editor_panel = QWidget(self)
        editor_panel.setLayout(form)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self.source_display)
        splitter.addWidget(editor_panel)
        splitter.setSizes([430, 650])
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.close_button)
        layout = QVBoxLayout(self)
        layout.addWidget(self.notice)
        layout.addWidget(self.fixture_selector)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.feedback)
        layout.addLayout(actions)
        self.fixture_selector.currentIndexChanged.connect(self._select_case)

    @staticmethod
    def _value(editor):
        return editor.text() if isinstance(editor, QLineEdit) else editor.toPlainText()

    @staticmethod
    def _set_value(editor, value):
        with QSignalBlocker(editor):
            if isinstance(editor, QLineEdit):
                editor.setText(value)
            else:
                editor.setPlainText(value)

    @property
    def dirty(self):
        return tuple(self._value(e) for e in self._editors.values()) != self._baseline

    def _edited(self, name):
        editor = self._editors[name]
        value = self._value(editor)
        try:
            validate_edit(name, value)
        except PreviewAdmissionError as error:
            self._set_value(editor, self._accepted[name])
            self.feedback.setText(str(error))
            return
        self._accepted[name] = value
        self.feedback.setText("Temporary edits only. No article will be saved.")

    def _confirm_discard(self):
        if not self.dirty:
            return True
        box = QMessageBox(self)
        box.setWindowTitle("Discard temporary preview?")
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.setText("Discard the temporary edits and review annotations?")
        box.setStandardButtons(QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        return box.exec() == QMessageBox.StandardButton.Discard

    def _restore_selector(self):
        with QSignalBlocker(self.fixture_selector):
            self.fixture_selector.setCurrentIndex(self._current_index)

    def _select_case(self, index):
        if self._transitioning or self._closed:
            self._restore_selector()
            return
        if not 1 <= index <= len(self._snapshots):
            self._restore_selector()
            return
        self._transitioning = True
        try:
            # Prepare before discarding: failure must preserve an edited draft.
            try:
                preview = self._service.build_preview(self._snapshots[index - 1])
            except (PreviewAdmissionError, PreviewUnavailableError) as error:
                self.feedback.setText(str(error))
                self._restore_selector()
                return
            if not self._confirm_discard():
                self._restore_selector()
                return
            self._preview = preview
            self._current_index = index
            self._baseline = (preview.title, preview.summary, preview.body, "")
            for name, value in zip(self._editors, self._baseline):
                self._accepted[name] = value
                self._set_value(self._editors[name], value)
                self._editors[name].setEnabled(True)
            source = preview.source
            case = source.fixture
            details = [NOTICE, f"Fixture: {case.fixture_id}; lineage: {case.lineage}",
                       f"Parent: {case.parent_case or 'none; newly authored'}",
                       f"Package revision: {source.package_revision}", f"Package SHA-256: {source.package_digest}",
                       f"Projection: {source.projection_version}", f"Session: {source.session_id}",
                       f"Source: {source.ticket_reference}@{source.ticket_revision}",
                       f"Knowledge reference: {source.knowledge_reference}@{source.knowledge_revision}",
                       "Fictional observations only; technical verification NOT PERFORMED."]
            details.extend(f"{s.reference} [{s.origin}]\n{s.text}" for s in case.sources)
            details.extend(f"{p.proposal_id}: {p.role}\nSource: {p.source_field}\n"
                           f"Method: {p.method}; canonical target: UNRESOLVED\n"
                           + "; ".join(p.qualifications) for p in case.proposals)
            if not case.proposals:
                details.append("No authored proposals; not an extraction evaluation.")
            details.append("Review expectation (author proposed): " + case.expectation)
            self.source_display.setPlainText("\n\n".join(details))
            self.feedback.setText("Temporary preview ready. No article will be saved.")
            self.title_input.setFocus()
        finally:
            self._transitioning = False

    def confirm_close(self):
        """Nonterminal question. Cancel and reentry leave the complete draft alive."""
        if self._closed or self._transitioning:
            return False
        self._transitioning = True
        try:
            return self._confirm_discard()
        finally:
            self._transitioning = False

    def commit_close(self):
        """Freeze and erase view state after host approval; perform no I/O."""
        if self._closed or self._transitioning:
            return False
        self._closed = True
        self._preview = None
        self._snapshots = ()
        self._baseline = ("", "", "", "")
        for name, editor in self._editors.items():
            self._accepted[name] = ""
            self._set_value(editor, "")
            if not isinstance(editor, QLineEdit):
                editor.document().clearUndoRedoStacks()
            editor.setEnabled(False)
        self.source_display.clear()
        self.source_display.document().clearUndoRedoStacks()
        with QSignalBlocker(self.fixture_selector):
            self.fixture_selector.clear()
        self.fixture_selector.setEnabled(False)
        self.close_button.setEnabled(False)
        self.feedback.setText("Temporary preview discarded. No article was saved.")
        return True
