"""Synthetic rule profiles only; no native Clipboard, files, network or consent."""

from dataclasses import FrozenInstanceError, fields
import unittest
from unittest.mock import patch

from f7hub.domain.clipboard import AdmittedManualText, IDENTITY_PROFILE
from f7hub.domain.clipboard_privacy import (
    assess_manual_text, ClipboardPrivacyAssessment, ClipboardPrivacyFinding as F,
    ClipboardAssessmentReason as R,
)


class ClipboardPrivacyTests(unittest.TestCase):
    def assess(self, text):
        return assess_manual_text(AdmittedManualText(text))

    def assert_finding(self, text, finding):
        # Never include synthetic content in unittest assertion output.
        result = self.assess(text)
        self.assertEqual(result.finding, finding)
        return result

    def test_ordinary_technical_information_is_distinct_from_secrets(self):
        for index, text in enumerate((
            "Restart the print spooler and review event 7036.",
            "DNS server 192.0.2.10; HTTPS port 443; timeout 5000 ms.",
            "SELECT name FROM sqlite_master; PRAGMA foreign_keys = ON;",
            "https://example.com/help", "Erreur réseau — résumé technique 😀",
            "Use integrated security; Server=example;Database=lab;Trusted_Connection=True",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.PERMITTED)

    def test_password_and_credential_assignment_profiles(self):
        for index, text in enumerate((
            "password=Synthetic-Only-42", "PWD: synthetic-lab-value",
            '{"password": "synthetic-lab-value"}', "DB_PASSWORD=synthetic-lab-value",
            "mot de passe : synthese-laboratoire", "credentials: synthetic fixture",
            "password =", "clientSecret: synthetic-lab-value",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)

    def test_authentication_header_and_session_profiles(self):
        for index, text in enumerate((
            "Authorization: Bearer synthetic-only-token", "bearer synthetic-only-token",
            "Proxy-Authorization: Basic c3ludGhldGlj", "Cookie: session=synthetic-only",
            "Set-Cookie: synthetic=only", "session_token=synthetic-only",
            "eyJzeW50aGV0aWM.eyJmaXh0dXJl.c2lnbmF0dXJl",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)

    def test_api_key_and_service_credential_profiles(self):
        for index, text in enumerate((
            "api_key=synthetic-only", "AccountKey=synthetic-only",
            "AWS_SECRET_ACCESS_KEY=synthetic-only", "AKIA0000000000000000",
            "sk-proj-syntheticOnly000000", "ghp_syntheticOnly000000",
            "xoxb-syntheticOnly000000", "https://example.com/?sig=synthetic-only",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)

    def test_private_key_and_malformed_key_profiles(self):
        for index, text in enumerate((
            "-----BEGIN PRIVATE KEY-----\nSYNTHETIC NOT A KEY\n-----END PRIVATE KEY-----",
            "-----BEGIN RSA PRIVATE KEY-----\nSYNTHETIC NOT A KEY",
            "-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN ENCRYPTED PRIVATE KEY-----",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)
        self.assert_finding("BEGIN PRIVATE KEY malformed synthetic fixture", F.NEEDS_REVIEW)

    def test_connection_string_credential_profiles(self):
        for index, text in enumerate((
            "Server=example;User Id=lab;Password=synthetic-only;",
            "postgresql://lab:synthetic-only@example.invalid/lab",
            "mongodb://lab:synthetic-only@example.invalid/lab",
            "DefaultEndpointsProtocol=https;AccountName=lab;AccountKey=synthetic-only",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)

    def test_mfa_recovery_and_one_time_code_profiles(self):
        for index, text in enumerate((
            "OTP: 000000", "MFA code: 000000", "recovery code = SYNTHETIC-ONLY",
            "one-time code: 000000", "verification_code: 000000", "000000",
            "backup_code=synthetic-only", "PIN: 0000",
        )):
            with self.subTest(profile=index):
                self.assert_finding(text, F.POSSIBLE_SECRET)

    def test_opaque_token_and_compatibility_forms_are_suspected_secrets(self):
        self.assert_finding("SyntheticOpaqueToken00000000000000000000", F.POSSIBLE_SECRET)
        self.assert_finding("ｐａｓｓｗｏｒｄ＝synthetic-only", F.POSSIBLE_SECRET)

    def test_sensitive_or_ambiguous_input_never_automatically_permitted(self):
        for index, text in enumerate((
            "credential handling guidance", "password", "lab@example.invalid",
            "hostname=LAB-PC", "customer_name: synthetic lab", "confidential note",
            "C:\\Users\\Lab\\note.txt", "\\\\lab\\share\\note.txt", "/home/lab/note",
            "Visible\u200bhidden", "visible\x1b[31m", "encoded=%73%79", "encoded=\\u0073",
        )):
            with self.subTest(profile=index):
                result = self.assert_finding(text, F.NEEDS_REVIEW)
                self.assertTrue(result.assessment_complete)

    def test_unicode_original_remains_exact_and_is_not_returned(self):
        text = "  e\u0301 ≠ é\r\n\tRésumé 😀\n"
        source = AdmittedManualText(text)
        result = assess_manual_text(source)
        self.assertEqual(result.finding, F.PERMITTED)
        self.assertIs(source.text, text)
        self.assertEqual(source.text.encode("utf-8"), text.encode("utf-8"))
        self.assertNotIn(text, repr(result))
        self.assertNotIn(text, repr(source))
        self.assertEqual({field.name for field in fields(result)}, {"finding", "reason"})

    def test_exact_65536_byte_boundaries(self):
        for index, text in enumerate(("q" * 65536, "é" * 32768, "😀" * 16384)):
            with self.subTest(profile=index):
                self.assertEqual(len(text.encode("utf-8")), 65536)
                self.assert_finding(text, F.PERMITTED)

    @staticmethod
    def forged_source(text, **changes):
        # Malformed in-process objects are not trusted by the pure boundary.
        source = object.__new__(AdmittedManualText)
        for key, value in dict(text=text, media_type="text/plain", identity_profile=IDENTITY_PROFILE,
                              **changes).items():
            object.__setattr__(source, key, value)
        return source

    def test_oversize_forged_source_denied_before_normalization(self):
        with patch("f7hub.domain.clipboard_privacy.unicodedata.normalize") as normalize:
            for text in ("q" * 65537, "é" * 32769, "😀" * 16385):
                result = assess_manual_text(self.forged_source(text))
                self.assertEqual(result.finding, F.INCOMPLETE)
                self.assertEqual(result.reason, R.RESOURCE_LIMIT)
                self.assertFalse(result.assessment_complete)
            normalize.assert_not_called()

    def test_malformed_unsupported_and_untyped_sources_fail_closed(self):
        malformed = [None, True, "synthetic-only", self.forged_source(""),
                     self.forged_source(" \n\t"), self.forged_source("bad\0shape"),
                     self.forged_source("\ud800"), self.forged_source(42)]
        source = self.forged_source("synthetic-only")
        object.__setattr__(source, "media_type", "application/octet-stream")
        malformed.append(source)
        source = self.forged_source("synthetic-only")
        object.__setattr__(source, "identity_profile", "unsupported")
        malformed.append(source)
        for index, source in enumerate(malformed):
            with self.subTest(profile=index):
                result = assess_manual_text(source)
                self.assertEqual(result.finding, F.INCOMPLETE)
                self.assertFalse(result.assessment_complete)

    def test_normalization_expansion_has_resource_limit(self):
        self.assertEqual(self.assess("\ufdfa" * 21845).reason, R.RESOURCE_LIMIT)

    def test_detector_exception_and_memory_limit_are_content_free_denial(self):
        sentinel = "synthetic-rejected-sentinel"
        with self.assertNoLogs(level="DEBUG"):
            for error, finding in ((RuntimeError(sentinel), F.ASSESSMENT_FAILED),
                                   (MemoryError(sentinel), F.INCOMPLETE)):
                with patch("f7hub.domain.clipboard_privacy._scan", side_effect=error):
                    result = self.assess(sentinel)
                self.assertEqual(result.finding, finding)
                self.assertFalse(result.assessment_complete)
                self.assertNotIn(sentinel, repr(result))

    def test_findings_are_deterministic_immutable_fixed_and_content_free(self):
        source = AdmittedManualText("api_key=synthetic-rejected-sentinel")
        first = assess_manual_text(source)
        self.assertEqual(first, assess_manual_text(source))
        self.assertEqual(first.assessment_method, "clipboard_local_rules")
        self.assertEqual(first.assessment_version, "1")
        self.assertNotIn("synthetic-rejected-sentinel", repr(first))
        with self.assertRaises(FrozenInstanceError):
            first.finding = F.PERMITTED
        for values in (("PERMITTED", R.NO_RECOGNIZED_RISK),
                       (F.PERMITTED, R.CREDENTIAL_SHAPE), (F.PERMITTED, "raw sentinel")):
            with self.assertRaises(ValueError) as caught:
                ClipboardPrivacyAssessment(*values)
            self.assertEqual(str(caught.exception), "Clipboard assessment classification is invalid.")

    def test_cancellation_propagates_without_assessment_success(self):
        with patch("f7hub.domain.clipboard_privacy._scan", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.assess("synthetic-only")


if __name__ == "__main__":
    unittest.main()
