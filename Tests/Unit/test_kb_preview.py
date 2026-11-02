"""Admission and authority tests for the isolated, manually authored lab."""

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from f7hub.services.kb_preview_service import (
    CORPUS, FIXTURE_PATH, INPUT_HASHES, MANIFEST_PATH, MAX_BODY_BYTES, MAX_PACKAGE_BYTES,
    KBPreviewService, NOTICE, PROFILE, PreviewAdmissionError, PreviewUnavailableError,
    admit_package, load_fixed_package, validate_edit,
)

ROOT = Path(__file__).resolve().parents[2]


def bound_service():
    package = load_fixed_package(ROOT)
    service = KBPreviewService(package)
    snapshots = []
    for index, case in enumerate(package.cases, 1):
        ticket = SimpleNamespace(ticket_id=index, status="NEW", source=PROFILE, company_id=None,
                                 contact_id=None, category_id=None, updated_at="lab-revision-1")
        notes = tuple(SimpleNamespace(note_text=s.text, source=PROFILE, note_type="INTERNAL",
                                      ticket_note_id=n, updated_at="note-revision-1")
                      for n, s in enumerate(case.sources, 1))
        article = SimpleNamespace(status="DRAFT", article_code="KB-SG02-LAB-REFERENCE",
                                  body_markdown=NOTICE + "\nSynthetic reference.",
                                  knowledge_article_id=1, version_number=1)
        snapshots.append(service.bind_sources(case, ticket_details=SimpleNamespace(ticket=ticket, notes=notes),
                                              reference_article=article))
    return service, tuple(snapshots)


class KBPreviewTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / FIXTURE_PATH).read_bytes()
        self.manifest = json.loads((ROOT / MANIFEST_PATH).read_bytes())
        self.originals = {p: (ROOT / p).read_bytes() for p in INPUT_HASHES}

    def admit_changed(self, change):
        rows = json.loads(self.raw)
        change(rows)
        raw = json.dumps(rows, ensure_ascii=False).encode()
        manifest = self.manifest | {"fixture_sha256": hashlib.sha256(raw).hexdigest()}
        return admit_package(raw, json.dumps(manifest).encode(), self.originals)

    def test_six_cases_exact_parent_and_bilingual_field_lineage(self):
        p = load_fixed_package(ROOT)
        self.assertEqual([c.fixture_id for c in p.cases], [f"F{i:02d}" for i in range(1, 7)])
        original = {r["case_id"]: r for r in map(json.loads, self.originals[CORPUS].splitlines())}
        self.assertEqual(p.cases[1].sources[0].text, original["SYN-IT-0009"]["customer_report"]["fr"])
        self.assertIn("deuxième", p.cases[1].sources[0].text)
        self.assertEqual([p.role for p in p.cases[2].proposals],
                         ["symptom_report", "symptom_report", "cause_hypothesis"])
        self.assertEqual(p.cases[2].sources[2].text, original["SYN-IT-0010"]["root_cause"]["hypothesis"])

    def test_authority_never_upgraded_in_generated_preview(self):
        service, snapshots = bound_service()
        for snapshot in snapshots:
            with self.subTest(case=snapshot.fixture.fixture_id):
                preview = service.build_preview(snapshot)
                self.assertIn(NOTICE, preview.body)
                self.assertIn("NOT PERFORMED", preview.body)
                self.assertTrue(all(p.canonical_target is None for p in snapshot.fixture.proposals))
                self.assertTrue(all(p.method == "manual_fixture_authoring" for p in snapshot.fixture.proposals))
                self.assertNotIn("SIMULATED_PASS", preview.body)
        self.assertIn("negated current failure", service.build_preview(snapshots[3]).body)
        self.assertIn("conditional planned check only", service.build_preview(snapshots[3]).body)
        self.assertIn("input source unverified", service.build_preview(snapshots[4]).body)
        self.assertEqual(snapshots[5].fixture.proposals, ())
        self.assertIn("not an extraction result", service.build_preview(snapshots[5]).body)

    def test_safety_flags_reject_truthy_strings_and_integers(self):
        for name, invalid in (("synthetic", "true"), ("synthetic", 1),
                              ("not_authoritative", 1), ("training_allowed", "false"),
                              ("training_allowed", 0), ("production_knowledge_allowed", True)):
            with self.subTest(name=name, invalid=invalid), self.assertRaises(PreviewAdmissionError):
                self.admit_changed(lambda rows: rows[0].__setitem__(name, invalid))

    def test_duplicate_ids_missing_lineage_and_extra_fields_denied(self):
        for change in (lambda r: r[1].__setitem__("fixture_id", "F01"),
                       lambda r: r[0].pop("lineage"),
                       lambda r: r[0].__setitem__("production_ticket_id", 13),
                       lambda r: r[3].__setitem__("lineage", "selected_original_synthetic")):
            with self.subTest(change=change), self.assertRaises(PreviewAdmissionError):
                self.admit_changed(change)

    def test_role_target_method_and_source_reference_overreach_denied(self):
        for key, value in (("role", "accepted_causal_claim"), ("role", []),
                           ("canonical_target", "approved-cause"), ("method", "automatic_match"),
                           ("source_field", "unadmitted.secret")):
            with self.subTest(key=key), self.assertRaises(PreviewAdmissionError):
                self.admit_changed(lambda rows: rows[0]["proposals"][0].__setitem__(key, value))

    def test_original_source_text_cannot_silently_change(self):
        with self.assertRaises(PreviewAdmissionError):
            self.admit_changed(lambda rows: rows[0]["sources"][0].__setitem__("text", "Altered original text"))

    def test_fixture_byte_identity_survives_existing_windows_checkout_policy(self):
        # The pinned original inputs already require their Windows CRLF bytes.
        checkout_form = self.raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.assertEqual(self.raw, checkout_form)
        self.assertEqual(hashlib.sha256(checkout_form).hexdigest(), self.manifest["fixture_sha256"])

    def test_input_or_fixture_hash_drift_denied(self):
        for raw, originals in ((self.raw + b" ", self.originals),
                               (self.raw, self.originals | {CORPUS: self.originals[CORPUS] + b"\n"})):
            with self.subTest(), self.assertRaises(PreviewAdmissionError):
                admit_package(raw, json.dumps(self.manifest).encode(), originals)

    def test_duplicate_json_keys_and_invalid_unicode_denied(self):
        raw = b'{"profile":"one","profile":"two"}'
        with self.assertRaises(PreviewAdmissionError):
            admit_package(self.raw, raw, self.originals)
        with self.assertRaises(PreviewAdmissionError):
            validate_edit("body", "invalid\ud800")

    def test_source_package_and_proposal_bounds_fail_without_truncation(self):
        with self.assertRaises(PreviewAdmissionError):
            admit_package(b" " * (MAX_PACKAGE_BYTES + 1), b"{}", self.originals)
        for change in (lambda r: r[3]["sources"][0].__setitem__("text", "x" * (16 * 1024 + 1)),
                       lambda r: r[0].__setitem__("proposals", r[0]["proposals"] * 9),
                       lambda r: r.pop()):
            with self.subTest(change=change), self.assertRaises(PreviewAdmissionError):
                self.admit_changed(change)

    def test_scalar_and_utf8_edit_limits(self):
        for name, value in (("title", "🔧" * 200), ("summary", "é" * 1000),
                            ("body", "é" * (MAX_BODY_BYTES // 2))):
            validate_edit(name, value)
            with self.subTest(name=name), self.assertRaises(PreviewAdmissionError):
                validate_edit(name, value + "x")

    def test_invalidation_and_forged_snapshot_cannot_generate(self):
        service, snapshots = bound_service()
        with self.assertRaises(PreviewUnavailableError):
            service.build_preview(replace(snapshots[0], ticket_revision="changed"))
        service.invalidate()
        with self.assertRaises(PreviewUnavailableError):
            service.build_preview(snapshots[0])

    def test_immutable_provenance_separate_from_editable_text(self):
        service, snapshots = bound_service()
        preview = service.build_preview(snapshots[0])
        with self.assertRaises(FrozenInstanceError):
            preview.source.fixture.proposals[0].canonical_target = "accepted"
        self.assertIs(replace(preview, body="Technician edit").source, preview.source)
        for forbidden in ("publish_article", "create_article", "update_article", "link_related_article"):
            self.assertFalse(hasattr(service, forbidden))

    def test_admission_errors_do_not_echo_content(self):
        marker = "PRIVATE_SENTINEL_DO_NOT_LOG"
        try:
            self.admit_changed(lambda r: r[0]["proposals"][0].__setitem__("role", marker))
        except PreviewAdmissionError as error:
            self.assertNotIn(marker, str(error))
        else:
            self.fail("Expected admission denial")


if __name__ == "__main__":
    unittest.main()
