"""Pure, immutable Settings definitions and safe effective preference snapshots.

Stage 1 admits Boolean USER preferences only; this is not a secrets or runtime
capability API. Future types/sources require a bounded owner-approved extension.
"""

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Iterable, Mapping


class SettingsValidationError(ValueError):
    """Safe definition/input failure, without rejected values in the message."""


def validate_setting_key(key: object) -> None:
    if (type(key) is not str or len(key) > 128
            or re.fullmatch(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", key) is None):
        raise SettingsValidationError("Setting key must be a stable module.setting_name.")


def validate_revision(revision: object) -> None:
    if type(revision) is not int or not 0 <= revision <= 9_223_372_036_854_775_807:
        raise SettingsValidationError("Expected Settings revision is invalid.")


@dataclass(frozen=True)
class SettingDefinition:
    key: str
    owner: str
    default: bool
    data_type: str = "BOOLEAN"
    scope: str = "USER"
    allowed_sources: tuple[str, ...] = ("USER",)
    persistence: str = "SQLITE"
    editable: bool = True
    sensitivity: str = "PRIVACY_SENSITIVE"
    update_behavior: str = "NEXT_OPERATION"
    allowed_values: tuple[bool, ...] = (False, True)

    def __post_init__(self) -> None:
        validate_setting_key(self.key)
        if self.owner != self.key.split(".")[0]:
            raise SettingsValidationError("Definition owner must match its namespace.")
        if (self.data_type != "BOOLEAN" or self.scope != "USER"
                or type(self.allowed_sources) is not tuple or self.allowed_sources != ("USER",)
                or self.persistence != "SQLITE" or type(self.editable) is not bool
                or self.sensitivity not in ("ORDINARY", "PRIVACY_SENSITIVE")
                or self.update_behavior != "NEXT_OPERATION"
                or type(self.allowed_values) is not tuple
                or len(self.allowed_values) != 2
                or any(type(value) is not bool for value in self.allowed_values)
                or self.allowed_values != (False, True)):
            raise SettingsValidationError("Unsupported or incompatible setting metadata.")
        self.validate(self.default)
        if self.sensitivity == "PRIVACY_SENSITIVE" and self.default is not False:
            raise SettingsValidationError("Sensitive Boolean preferences require a disabled default.")

    def validate(self, value: object) -> bool:
        if type(value) is not bool:
            raise SettingsValidationError("Setting value must be a Boolean.")
        return value


def compose_definitions(definitions: Iterable[SettingDefinition]) -> Mapping[str, SettingDefinition]:
    admitted: dict[str, SettingDefinition] = {}
    for definition in definitions:
        if not isinstance(definition, SettingDefinition):
            raise SettingsValidationError("Invalid setting definition.")
        if definition.key in admitted:
            raise SettingsValidationError("Duplicate setting definition.")
        admitted[definition.key] = definition
    return MappingProxyType(admitted)


@dataclass(frozen=True)
class EffectiveSetting:
    key: str
    value: bool
    source: str
    diagnostic: str | None = None


@dataclass(frozen=True)
class SettingsSnapshot:
    """Saved preferences only; no field asserts runtime availability/activation."""

    revision: int | None
    values: tuple[EffectiveSetting, ...]
    storage_available: bool
    unknown_override_count: int = 0

    def get(self, key: str) -> EffectiveSetting:
        for entry in self.values:
            if entry.key == key:
                return entry
        raise SettingsValidationError("Setting is not defined.")


@dataclass(frozen=True)
class SettingsChange:
    snapshot: SettingsSnapshot
    changed_keys: tuple[str, ...]


@dataclass(frozen=True)
class SettingsApplyResult:
    snapshot: SettingsSnapshot
    changed_keys: tuple[str, ...]
    notification_failures: int = 0
