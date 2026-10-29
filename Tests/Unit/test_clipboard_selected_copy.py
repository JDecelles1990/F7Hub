"""CP02-S4 pure request/assembly and synthetic delivery contracts."""
import unittest
from unittest.mock import Mock
from f7hub.domain.clipboard import (ClipboardItemRef, ClipboardCopyItem, ClipboardCopyError,
    validate_copy_selection, assemble_copy_text)
from f7hub.infrastructure.windows_selected_copy import write_selected_text
from f7hub.infrastructure.windows_latest_paste import PasteEffectError


class SelectedCopyUnitTests(unittest.TestCase):
    def test_exact_unicode_multiline_and_separator(self):
        self.assertEqual(assemble_copy_text(("  Résumé 😀\r\nline\n", "東京\n ")),
                         "  Résumé 😀\r\nline\n\n\n東京\n ")

    def test_exact_byte_bound_includes_separators(self):
        self.assertEqual(len(assemble_copy_text(("x" * 65533, "y")).encode()), 65536)
        with self.assertRaisesRegex(ClipboardCopyError, "TOO_LARGE"):
            assemble_copy_text(("x" * 65534, "y"))
        self.assertEqual(len(assemble_copy_text(("😀" * 16384,)).encode()), 65536)

    def test_reject_invalid_text(self):
        for text in ("", " ", "x\0y", "\ud800", None, 5):
            with self.subTest(kind=type(text).__name__), self.assertRaises(ClipboardCopyError):
                assemble_copy_text((text,))

    def test_request_count_identity_revision_and_duplicates(self):
        one = ClipboardCopyItem(ClipboardItemRef(1), 1)
        for selection in ((), [one], (one, one), (None,), tuple(ClipboardCopyItem(ClipboardItemRef(i), 1) for i in range(1, 102))):
            with self.assertRaises(ClipboardCopyError): validate_copy_selection(selection)
        validate_copy_selection(tuple(ClipboardCopyItem(ClipboardItemRef(i), 1) for i in range(1, 101)))
        for revision in (0, -1, True, 1.5, "1"):
            with self.assertRaises(ClipboardCopyError): ClipboardCopyItem(ClipboardItemRef(1), revision)

    def test_errors_never_echo_unknown_details(self):
        error = ClipboardCopyError("synthetic private content")
        self.assertEqual((str(error), error.code), ("UNAVAILABLE", "UNAVAILABLE"))

    def test_adapter_only_writes_once(self):
        api = Mock(); guard = Mock()
        api.write_text.side_effect = lambda text, owner, check: check()
        self.assertEqual(write_selected_text("Synthetic text", 12, guard, api=api), "WRITTEN")
        self.assertEqual(api.method_calls[0][0], "write_text")
        self.assertEqual(len(api.method_calls), 1)
        self.assertEqual(guard.call_count, 2)

    def test_adapter_preserves_all_failure_states_without_retry(self):
        for state in ("UNCHANGED", "MAY_HAVE_CHANGED", "WRITTEN"):
            api = Mock(); api.write_text.side_effect = PasteEffectError("CLEANUP_FAILED", state)
            with self.assertRaises(ClipboardCopyError) as caught:
                write_selected_text("Synthetic text", 12, lambda: None, api=api)
            self.assertEqual((caught.exception.code, caught.exception.clipboard), ("CLEANUP_FAILED", state))
            self.assertEqual(api.write_text.call_count, 1)

    def test_adapter_guard_failure_never_calls_writer(self):
        api = Mock()
        def deny(): raise ClipboardCopyError("DENIED")
        with self.assertRaises(ClipboardCopyError): write_selected_text("Synthetic text", 12, deny, api=api)
        self.assertFalse(api.method_calls)

    def test_adapter_unexpected_writer_exception_is_uncertain_and_safe(self):
        api = Mock(); api.write_text.side_effect = RuntimeError("synthetic private content")
        with self.assertRaises(ClipboardCopyError) as caught:
            write_selected_text("Synthetic text", 12, lambda: None, api=api)
        self.assertEqual((str(caught.exception), caught.exception.clipboard), ("UNAVAILABLE", "MAY_HAVE_CHANGED"))
        self.assertEqual(api.write_text.call_count, 1)
