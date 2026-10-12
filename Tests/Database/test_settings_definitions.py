"""Definition admission is pure and rejects coercion or metadata expansion."""

from dataclasses import FrozenInstanceError, replace
import unittest

from f7hub.domain.clipboard_settings import CLIPBOARD_SETTING_DEFINITIONS
from f7hub.domain.settings import SettingDefinition, SettingsValidationError, compose_definitions


class SettingsDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.definition = CLIPBOARD_SETTING_DEFINITIONS[0]

    def test_exact_initial_preferences_and_safe_defaults(self):
        definitions = compose_definitions(CLIPBOARD_SETTING_DEFINITIONS)
        self.assertEqual(tuple(definitions), (
            "clipboard.workflow_enabled", "clipboard.source_process_persistence_enabled",
            "clipboard.source_window_title_persistence_enabled"))
        for definition in definitions.values():
            self.assertIs(definition.default, False)
            self.assertEqual((definition.owner, definition.scope, definition.allowed_sources,
                              definition.persistence, definition.update_behavior),
                             ("clipboard", "USER", ("USER",), "SQLITE", "NEXT_OPERATION"))
            self.assertEqual(definition.sensitivity, "PRIVACY_SENSITIVE")
            self.assertIs(definition.validate(True), True)
            self.assertIs(definition.validate(False), False)

    def test_immutable_definition_and_composition(self):
        with self.assertRaises(FrozenInstanceError):
            self.definition.default = True
        definitions = compose_definitions((self.definition,))
        with self.assertRaises(TypeError):
            definitions[self.definition.key] = self.definition

    def test_duplicate_and_nondefinition_admission(self):
        for definitions in ((self.definition, self.definition), (object(),)):
            with self.subTest(definitions=definitions), self.assertRaises(SettingsValidationError):
                compose_definitions(definitions)

    def test_malformed_keys(self):
        for key in ("clipboard", "Clipboard.enabled", "clipboard.is-enabled", "clipboard..enabled",
                    "clipboard.enabled\n", "other.enabled", ".enabled", "clipboard." + "a" * 128, None, 1):
            with self.subTest(key=key), self.assertRaises(SettingsValidationError):
                replace(self.definition, key=key)

    def test_invalid_defaults_and_strict_booleans(self):
        for value in (1, 0, "true", "false", None, [], {}, 1.0, b"true"):
            with self.subTest(value_type=type(value)), self.assertRaises(SettingsValidationError):
                replace(self.definition, default=value)
            with self.assertRaises(SettingsValidationError):
                self.definition.validate(value)
        with self.assertRaises(SettingsValidationError):
            replace(self.definition, default=True)

    def test_unsupported_types_and_incompatible_metadata(self):
        for field, value in (("data_type", "INTEGER"), ("data_type", "JSON"), ("data_type", "SECRET"),
                             ("scope", "APPLICATION"), ("allowed_sources", ("USER", "ENVIRONMENT")),
                             ("allowed_sources", ["USER"]), ("persistence", "CONFIG_FILE"),
                             ("editable", 1), ("owner", "another"), ("sensitivity", "SECRET"),
                             ("update_behavior", "RESTART_REQUIRED"), ("allowed_values", (0, 1)),
                             ("allowed_values", [False, True]), ("allowed_values", (True,))):
            with self.subTest(field=field, value=value), self.assertRaises(SettingsValidationError):
                replace(self.definition, **{field: value})

    def test_ordinary_boolean_definition(self):
        definition = SettingDefinition("example.display_enabled", "example", True, sensitivity="ORDINARY")
        self.assertIs(definition.default, True)
