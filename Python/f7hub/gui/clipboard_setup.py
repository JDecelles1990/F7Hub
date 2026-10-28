"""Clipboard preference drafts; persistence and revision authority stay in Settings."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from f7hub.domain.clipboard_settings import (
    CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED,
)
from f7hub.domain.settings import SettingsValidationError
from f7hub.gui.service_task_runner import ServiceTaskRunner
from f7hub.repositories.settings_repository import (
    SettingsConflictError, SettingsContentionError, SettingsPersistenceError, SettingsUncertainError,
)
from f7hub.services.settings_service import SettingsService


class ClipboardSetup(QWidget):
    """One retained editing session, with immutable worker inputs and explicit reload."""

    def __init__(self, service: SettingsService, parent=None, *, clipboard_service=None):
        super().__init__(parent)
        self._service = service
        self._clipboard_service = clipboard_service
        self._consent_epoch = None
        self._consent_eligible = False
        self._affirmed = False
        self._grant_pending = False
        self.runner = ServiceTaskRunner(self)
        self._pending = False
        self._generation = 0
        self._snapshot = None
        self._loaded = {}
        self._draft = {}
        self._conflict = False
        self._save_available = False
        self.setObjectName("clipboardSetup")
        self.setAccessibleName("Clipboard Setup")
        layout = QVBoxLayout(self)
        heading = self._label("Clipboard Setup")
        layout.addWidget(heading)
        self.runtime_message = self._label(
            "Saved preferences only. Production Clipboard capture and Active Paste "
            "are not implemented or active. Ctrl+Alt+C and Ctrl+Alt+V are unavailable.")
        layout.addWidget(self.runtime_message)
        self.consent_message = self._label('Durable manual history needs explicit Setup enablement. Automatic capture is not authorized here.')
        layout.addWidget(self.consent_message)
        self.checkboxes = {}
        fields = (
            (WORKFLOW_ENABLED, "&Enable Clipboard workflow and local history",
             "This is the explicit setup opt-in for future eligible durable manual captures. "
             "TEMPORARY Clipboard content is retained locally for 7 days by default; an independently "
             "approved preservation action may use a different policy. Content detected as sensitive "
             "is rejected. Detection has limits and cannot guarantee all secrets are identified. "
             "Disabling this preference does not delete historical records."),
            (SOURCE_PROCESS_ENABLED, "Store source &application executable name",
             "For future captures, optionally store only the executable basename, not full paths, "
             "command lines or unrestricted application metadata. This preference remains "
             "independent when workflow is disabled."),
            (SOURCE_TITLE_ENABLED, "Store source window &title",
             "Window titles may contain sensitive information. Optional title collection is "
             "independent of executable-name collection and workflow enablement."),
        )
        for key, title, explanation in fields:
            checkbox = QCheckBox(title, self)
            checkbox.setObjectName(key)
            checkbox.setAccessibleName(title.replace("&", ""))
            checkbox.setAccessibleDescription(explanation)
            checkbox.toggled.connect(lambda value, key=key: self._edited(key, value))
            self.checkboxes[key] = checkbox
            layout.addWidget(checkbox)
            layout.addWidget(self._label(explanation))
        self.draft_message = self._label("Preferences have not been loaded.")
        self.status_message = self._label("")
        layout.addWidget(self.draft_message)
        layout.addWidget(self.status_message)
        buttons = QHBoxLayout()
        self.apply_button = QPushButton("&Apply", self)
        self.cancel_button = QPushButton("&Cancel", self)
        self.reload_button = QPushButton("&Reload", self)
        for button, name, callback in (
            (self.apply_button, "Apply Clipboard preferences", self.apply),
            (self.cancel_button, "Cancel Clipboard preference edits", self.cancel),
            (self.reload_button, "Reload Clipboard preferences", self.reload),
        ):
            button.setAccessibleName(name)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)
        layout.addStretch()
        controls = (*self.checkboxes.values(), self.apply_button, self.cancel_button, self.reload_button)
        for first, second in zip(controls, controls[1:]):
            self.setTabOrder(first, second)
        self._update_controls()

    def _label(self, text):
        label = QLabel(text, self)
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        label.setAccessibleName(text)
        return label

    def _status(self, text):
        self.status_message.setText(text)
        self.status_message.setAccessibleName(text)

    @property
    def pending(self):
        # Retains the guard across the runner's idle-before-callback interval.
        return self._pending or self.runner.busy

    @property
    def dirty(self):
        return self._draft != self._loaded or bool(self._clipboard_service is not None and self._affirmed
                and not self._consent_eligible and self._draft.get(WORKFLOW_ENABLED))

    @property
    def loaded_revision(self):
        return None if self._snapshot is None else self._snapshot.revision

    def _edited(self, key, value):
        self._draft[key] = value
        if key == WORKFLOW_ENABLED and value:
            self._affirmed = True
        self._update_controls()

    def _update_controls(self):
        editable = self._snapshot is not None and self._snapshot.storage_available and not self.pending
        for checkbox in self.checkboxes.values():
            checkbox.setEnabled(editable)
        self.apply_button.setEnabled(editable and self._save_available and not self._conflict)
        self.cancel_button.setEnabled(not self.pending and self._snapshot is not None)
        self.reload_button.setEnabled(not self.pending)
        if self._snapshot is not None:
            text = ("Unsaved changes" if self.dirty else "No unsaved changes")
            text += f". Loaded revision: {self.loaded_revision if self.loaded_revision is not None else 'unavailable'}."
            self.draft_message.setText(text)
            self.draft_message.setAccessibleName(text)

    def confirm_discard(self):
        if self.pending:
            return False
        if not self.dirty:
            return True
        answer = QMessageBox.question(
            self, "Unsaved Clipboard preferences", "Discard the unsaved Clipboard preference edits?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return answer == QMessageBox.StandardButton.Discard

    def cancel(self):
        if self.pending or self._snapshot is None:
            return False
        self._draft = dict(self._loaded)
        self._affirmed = False
        self._present_values()
        text = "Uncommitted edits discarded. Latest known saved preferences restored."
        if self._conflict:
            text += " Reload to resolve the revision conflict."
        self._status(text)
        self._update_controls()
        return True

    def end_session(self):
        if self.pending:
            return False
        self.cancel()
        self._generation += 1
        return True

    def reload(self):
        if not self.confirm_discard():
            return False
        self._generation += 1
        if self._clipboard_service is not None:
            return self._submit(self._clipboard_service.refresh_setup, self._loaded_setup, "Loading saved preferences…")
        return self._submit(self._service.refresh, self._loaded_snapshot, "Loading saved preferences…")

    def _loaded_setup(self, state):
        snapshot, self._consent_epoch, self._consent_eligible = state
        self._loaded_snapshot(snapshot)
        self._show_consent()

    def _show_consent(self):
        text = ('Eligible manual history consent is saved. Capture availability is reported by the application.' if self._consent_eligible else
                'Manual history is ineligible. To enable, deliberately uncheck/recheck Enable Clipboard workflow, then Apply. Saved preferences alone do not grant consent.')
        self.consent_message.setText(text)
        self.consent_message.setAccessibleName(text)

    def _submit(self, work, success, message):
        if self.pending:
            return False
        generation = self._generation
        self._pending = True
        self._status(message)
        self._update_controls()

        def completed(value):
            if generation == self._generation:
                try:
                    success(value)
                except Exception:
                    self._save_available = False
                    self._status("Saved preferences could not be displayed. Reload before editing.")
                finally:
                    self._pending = False
                    self._update_controls()

        def failed(error):
            if generation == self._generation:
                self._failed(error)
                self._pending = False
                self._update_controls()

        if not self.runner.submit(work, completed, failed):
            self._pending = False
            self._update_controls()
            return False
        return True

    def _accept_snapshot(self, snapshot):
        self._snapshot = snapshot
        self._loaded = {key: snapshot.get(key).value for key in self.checkboxes}
        self._draft = dict(self._loaded)
        self._affirmed = False
        self._conflict = False
        self._save_available = snapshot.storage_available

    def _present_values(self):
        for key, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            try:
                checkbox.setChecked(self._draft[key])
            finally:
                checkbox.blockSignals(False)

    def _loaded_snapshot(self, snapshot):
        self._accept_snapshot(snapshot)
        self._present_values()
        if not snapshot.storage_available:
            self._status("Settings storage is unavailable. Sensitive preferences are safely disabled. Reload to retry.")
        elif any(snapshot.get(key).diagnostic for key in self.checkboxes):
            self._status("Invalid stored preferences are safely disabled. Review before applying changes.")
        else:
            self._status("Saved preferences loaded. Review before Apply.")

    def apply(self):
        if (self.pending or not self._save_available or self._conflict
                or self._snapshot is None or not self._snapshot.storage_available):
            return False
        changes = {key: value for key, value in self._draft.items() if value != self._loaded[key]}
        grant = bool(self._clipboard_service is not None and self._affirmed and self._draft.get(WORKFLOW_ENABLED)
                     and (not self._loaded.get(WORKFLOW_ENABLED) or not self._consent_eligible))
        if grant:
            changes[WORKFLOW_ENABLED] = True
        try:
            for definition in CLIPBOARD_SETTING_DEFINITIONS:
                if definition.key in changes:
                    definition.validate(changes[definition.key])
        except SettingsValidationError as error:
            self._failed(error)
            return False
        if not changes:
            self._status("No changes to save. Saved revision is unchanged.")
            return True
        revision = self.loaded_revision
        self._grant_pending = grant
        epoch = self._consent_epoch
        return self._submit(
            (lambda: self._clipboard_service.enable_history_from_setup(changes, expected_revision=revision,
                       expected_epoch=epoch)) if grant else lambda: self._service.apply(changes, expected_revision=revision),
            self._saved, "Saving preferences…",
        )

    def _saved(self, result):
        # A returned Apply result is authoritative commit evidence. Establish the
        # saved baseline before presentation; downstream failure cannot retry a write.
        if self._grant_pending:
            self._consent_epoch = (self._consent_epoch or 0) + 1
            self._consent_eligible = True
        elif WORKFLOW_ENABLED in result.changed_keys:
            self._consent_eligible = False
            if self._consent_epoch is not None:
                self._consent_epoch += 1
        self._grant_pending = False
        self._accept_snapshot(result.snapshot)
        if self._clipboard_service is not None:
            self._show_consent()
        try:
            self._present_values()
        except Exception:
            self._save_available = False
            self._status("Preferences saved. The display could not be updated. Reload saved preferences.")
            return
        text = "Preferences saved. Capture and Active Paste remain unavailable."
        if result.notification_failures:
            text += " A downstream observer could not be notified."
        self._status(text)

    def _failed(self, error):
        if isinstance(error, SettingsUncertainError):
            self._save_available = False
            self._consent_eligible = False
            self._show_consent()
            text = 'Save outcome is uncertain; changes may have committed. Your draft is preserved. Reload to reconcile before a new explicit save.'
        elif isinstance(error, SettingsConflictError):
            self._conflict = True
            text = "Preferences changed elsewhere. Your draft is preserved. Reload explicitly, then review before Apply."
        elif isinstance(error, SettingsValidationError):
            text = "Preferences could not be validated. Your draft is preserved. Review the values."
        elif isinstance(error, SettingsContentionError):
            text = "Settings storage is busy. No changes were saved. Your draft is preserved; retry explicitly."
        elif isinstance(error, SettingsPersistenceError):
            self._save_available = False
            text = "Settings storage is unavailable. Your draft is preserved. Reload to verify saved state before retrying."
        else:
            self._save_available = False
            text = "The Settings operation could not be completed. Your draft is preserved. Reload saved preferences before retrying."
        self._status(text)

    def closeEvent(self, event):
        if not self.confirm_discard():
            event.ignore()
            return
        self.end_session()
        super().closeEvent(event)
