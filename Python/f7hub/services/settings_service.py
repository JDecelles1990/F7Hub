"""Typed saved preferences with atomic Apply, explicit Reset and bounded refresh."""

from threading import RLock
from typing import Callable, Iterable, Mapping

from f7hub.domain.settings import (
    EffectiveSetting, SettingDefinition, SettingsApplyResult, SettingsChange,
    SettingsSnapshot, SettingsValidationError, compose_definitions, validate_revision,
)
from f7hub.repositories.settings_repository import (
    SettingsConflictError, SettingsPersistenceError, SettingsRepository, SettingsState,
)


class SettingsService:
    """One process snapshot; owning features still authorize and apply effects.

    refresh() performs one coherent read for future operation boundaries; there
    is no polling daemon. Failure replaces cached sensitive values with false.
    Apply requires an available snapshot and an explicit repository revision.
    """

    def __init__(self, repository: SettingsRepository,
                 definitions: Iterable[SettingDefinition]) -> None:
        self._repository = repository
        self._definitions = compose_definitions(definitions)
        self._gate = RLock()
        self._subscribers: list[Callable[[SettingsChange], None]] = []
        self._snapshot = self._unavailable()
        self.refresh()

    def get_snapshot(self) -> SettingsSnapshot:
        with self._gate:
            return self._snapshot

    def refresh(self) -> SettingsSnapshot:
        """Read once before new work; unavailable sensitive state fails closed."""
        with self._gate:
            try:
                snapshot = self._resolve(self._repository.load_state())
            except SettingsPersistenceError:
                snapshot = self._unavailable()
            self._snapshot = snapshot
            return snapshot

    def apply(self, changes: Mapping[str, bool], *, expected_revision: int,
              resets: Iterable[str] = ()) -> SettingsApplyResult:
        validate_revision(expected_revision)
        if not isinstance(changes, Mapping) or isinstance(resets, (str, bytes)):
            raise SettingsValidationError("Settings changes/reset group is invalid.")
        proposed = dict(changes)
        try:
            reset_keys = tuple(resets)
        except TypeError:
            raise SettingsValidationError("Settings reset group must contain defined keys.") from None
        if any(type(key) is not str for key in (*proposed, *reset_keys)):
            raise SettingsValidationError("Setting is not defined.")
        if len(set(reset_keys)) != len(reset_keys) or set(proposed).intersection(reset_keys):
            raise SettingsValidationError("A setting may occur only once in a group.")
        for key in (*proposed, *reset_keys):
            definition = self._definitions.get(key)
            if definition is None or not definition.editable:
                raise SettingsValidationError("Setting is undefined or not editable.")
            if key in proposed:
                definition.validate(proposed[key])
        with self._gate:
            if not self._snapshot.storage_available:
                raise SettingsPersistenceError("Settings are unavailable. Refresh before saving.")
            if expected_revision != self._snapshot.revision:
                raise SettingsConflictError("Reload Settings before applying this draft.")
            # An unchanged inherited default is not an instruction to seed a row.
            # Invalid retained overrides remain explicitly repairable by Apply.
            proposed = {key: value for key, value in proposed.items()
                        if not (self._snapshot.get(key).source == "DEFAULT"
                                and self._snapshot.get(key).diagnostic is None
                                and self._snapshot.get(key).value == value)}
            result = self._repository.apply(changes=proposed, resets=reset_keys,
                                            expected_revision=expected_revision)
            # The repository returns the coherent state read before its successful
            # commit, avoiding a second read that could fail or observe a later writer.
            snapshot = self._resolve(result.state)
            self._snapshot = snapshot
            failures = 0
            if result.changed_keys:
                event = SettingsChange(snapshot, result.changed_keys)
                for callback in tuple(self._subscribers):
                    try:
                        callback(event)
                    except Exception:
                        # Post-commit observer failure cannot become a failed save.
                        failures += 1
            return SettingsApplyResult(snapshot, result.changed_keys, failures)

    def reset(self, keys: Iterable[str], *, expected_revision: int) -> SettingsApplyResult:
        return self.apply({}, expected_revision=expected_revision, resets=keys)

    def subscribe(self, callback: Callable[[SettingsChange], None]) -> None:
        if not callable(callback):
            raise SettingsValidationError("Settings subscriber must be callable.")
        with self._gate:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[SettingsChange], None]) -> None:
        with self._gate:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def _resolve(self, state: SettingsState) -> SettingsSnapshot:
        stored = {entry.key: entry for entry in state.overrides}
        values: list[EffectiveSetting] = []
        for key, definition in self._definitions.items():
            entry = stored.get(key)
            if entry is None:
                values.append(EffectiveSetting(key, definition.default, "DEFAULT"))
            elif entry.value_type == "BOOLEAN" and type(entry.value_text) is str and entry.value_text in ("true", "false"):
                values.append(EffectiveSetting(key, entry.value_text == "true", "USER"))
            elif definition.sensitivity == "PRIVACY_SENSITIVE":
                values.append(EffectiveSetting(key, False, "FAIL_CLOSED", "INVALID_STORED_VALUE"))
            else:
                values.append(EffectiveSetting(key, definition.default, "DEFAULT", "INVALID_STORED_VALUE"))
        return SettingsSnapshot(state.revision, tuple(values), True,
                                sum(key not in self._definitions for key in stored))

    def _unavailable(self) -> SettingsSnapshot:
        return SettingsSnapshot(None, tuple(
            EffectiveSetting(key, False if definition.sensitivity == "PRIVACY_SENSITIVE" else definition.default,
                             "UNAVAILABLE", "STORAGE_UNAVAILABLE")
            for key, definition in self._definitions.items()), False)
