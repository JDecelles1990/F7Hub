"""Temporary synthetic review proposals; no persistence or acceptance authority."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import secrets


PROFILE = "KB-SG02-LAB-v1"
PACKAGE_REVISION = "1"
MAX_PACKAGE_BYTES = 128 * 1024
MAX_SOURCE_BYTES = 16 * 1024
MAX_BODY_BYTES = 64 * 1024
NOTICE = "Synthetic lab — temporary, unpublished"
CORPUS = "Data/SemanticModel/Synthetic/synthetic_cases.jsonl"
SCHEMA = "Data/SemanticModel/Synthetic/synthetic_case_seed_v0_1.schema.json"
INPUT_HASHES = {
    CORPUS: "612e115caeabb000ab5e19e6782168d43f0bc1149b9ae725c93a143cf2790eeb",
    SCHEMA: "b024f4182c66a0d9280279ebfe4d1572fff228e01db8b04a26155da4575ac871",
}
FIXTURE_PATH = "Tests/Fixtures/kb_sg02/review_cases.json"
MANIFEST_PATH = "Tests/Fixtures/kb_sg02/manifest.json"
ROLES = frozenset({"symptom_report", "cause_hypothesis", "observation", "check"})


class PreviewAdmissionError(ValueError):
    """A fixed, content-free reason suitable for presentation."""


class PreviewUnavailableError(RuntimeError):
    """Session or bound source is no longer available."""


def _deny(message="Synthetic fixture admission denied."):
    raise PreviewAdmissionError(message)


def _utf8(text):
    if not isinstance(text, str):
        _deny()
    try:
        return text.encode("utf-8", errors="strict")
    except UnicodeError:
        _deny("Text contains invalid Unicode.")


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _deny("Duplicate JSON key.")
            result[key] = value
        return result
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=lambda _: _deny())
    except (UnicodeError, ValueError, RecursionError):
        _deny("Invalid synthetic fixture JSON.")


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected.split()):
        _deny()


def _text(value):
    if not isinstance(value, str) or not value.strip():
        _deny()
    _utf8(value)
    return value


@dataclass(frozen=True)
class SourceField:
    reference: str
    text: str = field(repr=False)
    origin: str


@dataclass(frozen=True)
class AuthoredProposal:
    proposal_id: str
    role: str
    source_field: str
    qualifications: tuple[str, ...]
    canonical_target: None = None
    method: str = "manual_fixture_authoring"


@dataclass(frozen=True)
class FixtureCase:
    fixture_id: str
    title: str
    parent_case: str | None
    lineage: str
    sources: tuple[SourceField, ...]
    proposals: tuple[AuthoredProposal, ...]
    expectation: str


@dataclass(frozen=True)
class FixturePackage:
    revision: str
    digest: str
    cases: tuple[FixtureCase, ...]


def admit_package(raw: bytes, manifest_raw: bytes, original_inputs: dict[str, bytes]) -> FixturePackage:
    try:
        return _admit_package(raw, manifest_raw, original_inputs)
    except (TypeError, KeyError, AttributeError, IndexError):
        _deny("Invalid synthetic fixture structure.")


def _admit_package(raw: bytes, manifest_raw: bytes, original_inputs: dict[str, bytes]) -> FixturePackage:
    """Validate a fixed local format, not the shared SemanticModel schema."""
    if type(raw) is not bytes or len(raw) > MAX_PACKAGE_BYTES or len(manifest_raw) > MAX_PACKAGE_BYTES:
        _deny("Synthetic package exceeds its bound.")
    manifest = _json(manifest_raw)
    _keys(manifest, "profile package_revision fixture_sha256 source_sha256 expectation_review")
    if (manifest["profile"] != PROFILE or manifest["package_revision"] != PACKAGE_REVISION
            or manifest["expectation_review"] != "AUTHOR_PROPOSED_INDEPENDENT_REVIEW_PENDING"
            or manifest["source_sha256"] != INPUT_HASHES
            or set(original_inputs) != set(INPUT_HASHES)):
        _deny("Synthetic manifest binding is invalid.")
    digest = hashlib.sha256(raw).hexdigest()
    if manifest["fixture_sha256"] != digest:
        _deny("Synthetic fixture hash changed.")
    for name, expected in INPUT_HASHES.items():
        if hashlib.sha256(original_inputs[name]).hexdigest() != expected:
            _deny("Original synthetic input changed.")
    corpus = {}
    for line in original_inputs[CORPUS].splitlines():
        row = _json(line)
        if not isinstance(row, dict) or not isinstance(row.get("case_id"), str) or row["case_id"] in corpus:
            _deny()
        corpus[row["case_id"]] = row
    records = _json(raw)
    if type(records) is not list or len(records) != 6:
        _deny("Exactly six synthetic cases are required.")
    cases = []
    for index, row in enumerate(records, 1):
        _keys(row, "fixture_id title parent_case lineage synthetic not_authoritative training_allowed production_knowledge_allowed sources proposals expectation")
        if len(_utf8(json.dumps(row, ensure_ascii=False))) > MAX_SOURCE_BYTES:
            _deny("Synthetic case exceeds its bound.")
        validate_edit("title", _text(row["title"]))
        if (row["fixture_id"] != f"F{index:02d}" or type(row["synthetic"]) is not bool
                or row["synthetic"] is not True or row["not_authoritative"] is not True
                or row["training_allowed"] is not False or row["production_knowledge_allowed"] is not False):
            _deny("Synthetic safety flags or fixture identity invalid.")
        parent = row["parent_case"]
        if parent not in ("SYN-IT-0004", "SYN-IT-0009", "SYN-IT-0010", None):
            _deny()
        if row["lineage"] not in ("selected_original_synthetic", "newly_authored_synthetic_variant"):
            _deny()
        if index <= 3 and (parent != ("SYN-IT-0004", "SYN-IT-0009", "SYN-IT-0010")[index - 1]
                           or row["lineage"] != "selected_original_synthetic"):
            _deny()
        if index > 3 and row["lineage"] != "newly_authored_synthetic_variant":
            _deny()
        if type(row["sources"]) is not list or not 1 <= len(row["sources"]) <= 4:
            _deny()
        sources = []
        for source in row["sources"]:
            _keys(source, "reference text origin")
            ref, text = _text(source["reference"]), _text(source["text"])
            if ref in {s.reference for s in sources}:
                _deny()
            if row["lineage"] == "selected_original_synthetic":
                if source["origin"] != "original_synthetic_field":
                    _deny()
                if ref not in ("customer_report.en", "customer_report.fr", "root_cause.hypothesis"):
                    _deny()
                section, key = ref.split(".")
                original = corpus.get(parent, {})
                if original.get(section, {}).get(key) != text:
                    _deny("Original field lineage mismatch.")
            elif source["origin"] != "newly_authored_synthetic_variant" or ref != "variant.note":
                _deny()
            sources.append(SourceField(ref, text, source["origin"]))
        if sum(len(_utf8(s.text)) for s in sources) > MAX_SOURCE_BYTES:
            _deny("Selected synthetic source exceeds its bound.")
        if type(row["proposals"]) is not list or len(row["proposals"]) > 8:
            _deny()
        proposals = []
        for proposal in row["proposals"]:
            _keys(proposal, "proposal_id role source_field qualifications canonical_target method")
            if (proposal["role"] not in ROLES or proposal["canonical_target"] is not None
                    or proposal["method"] != "manual_fixture_authoring"
                    or proposal["source_field"] not in {s.reference for s in sources}
                    or type(proposal["qualifications"]) is not list
                    or not 1 <= len(proposal["qualifications"]) <= 8):
                _deny("Authored proposal authority or reference invalid.")
            proposal_id = _text(proposal["proposal_id"])
            if proposal_id in {p.proposal_id for p in proposals}:
                _deny()
            proposals.append(AuthoredProposal(proposal_id, proposal["role"], proposal["source_field"],
                                             tuple(_text(q) for q in proposal["qualifications"])))
        cases.append(FixtureCase(row["fixture_id"], _text(row["title"]), parent, row["lineage"],
                                 tuple(sources), tuple(proposals), _text(row["expectation"])))
    return FixturePackage(PACKAGE_REVISION, digest, tuple(cases))


def load_fixed_package(project_root: Path) -> FixturePackage:
    """Internal composition helper. The CLI exposes no root or input overrides."""
    try:
        def bounded(path, limit):
            with (project_root / path).open("rb") as stream:
                value = stream.read(limit + 1)
            if len(value) > limit:
                _deny("Synthetic input exceeds its bound.")
            return value
        return admit_package(bounded(FIXTURE_PATH, MAX_PACKAGE_BYTES),
                             bounded(MANIFEST_PATH, MAX_PACKAGE_BYTES),
                             {p: bounded(p, MAX_PACKAGE_BYTES) for p in INPUT_HASHES})
    except (OSError, TypeError, KeyError, IndexError):
        _deny("Synthetic inputs unavailable.")


@dataclass(frozen=True)
class SourceSnapshot:
    session_id: str
    fixture: FixtureCase
    package_revision: str
    package_digest: str
    projection_version: str
    ticket_reference: str
    ticket_revision: str
    note_references: tuple[str, ...]
    knowledge_reference: str
    knowledge_revision: int
    reference_text: str = field(repr=False)


@dataclass(frozen=True)
class KBPreview:
    source: SourceSnapshot
    title: str
    summary: str
    body: str = field(repr=False)


def validate_edit(field_name: str, value: str) -> None:
    encoded = _utf8(value)
    limits = {"title": 200, "summary": 1000, "body": MAX_BODY_BYTES, "annotations": MAX_SOURCE_BYTES}
    if field_name not in limits:
        _deny()
    measured = len(encoded) if field_name in ("body", "annotations") else len(value)
    if measured > limits[field_name]:
        _deny(f"{field_name.capitalize()} exceeds its limit; edit was rejected.")


class KBPreviewService:
    """Own a short-lived synthetic session; never accept a repository or writer."""

    def __init__(self, package: FixturePackage):
        self.package = package
        self.session_id = secrets.token_hex(16)
        self._active = True
        self._snapshots: dict[str, SourceSnapshot] = {}

    def bind_sources(self, fixture: FixtureCase, *, ticket_details, reference_article) -> SourceSnapshot:
        if not self._active:
            raise PreviewUnavailableError("Lab session unavailable.")
        if fixture not in self.package.cases or fixture.fixture_id in self._snapshots:
            _deny("Fixture is not eligible for binding.")
        ticket = ticket_details.ticket
        notes = ticket_details.notes
        if (ticket.status != "NEW" or ticket.source != PROFILE or ticket.company_id is not None
                or ticket.contact_id is not None or ticket.category_id is not None
                or len(notes) != len(fixture.sources)
                or tuple(note.note_text for note in notes) != tuple(s.text for s in fixture.sources)
                or any(note.source != PROFILE or note.note_type != "INTERNAL" for note in notes)
                or reference_article.status != "DRAFT" or reference_article.article_code != "KB-SG02-LAB-REFERENCE"
                or not reference_article.body_markdown.startswith(NOTICE)):
            _deny("Lab service source binding is invalid.")
        snapshot = SourceSnapshot(self.session_id, fixture, self.package.revision, self.package.digest, PROFILE,
                                  f"lab-ticket:{ticket.ticket_id}", ticket.updated_at,
                                  tuple(f"lab-note:{n.ticket_note_id}@{n.updated_at}" for n in notes),
                                  f"lab-knowledge:{reference_article.knowledge_article_id}",
                                  reference_article.version_number, reference_article.body_markdown)
        self._snapshots[fixture.fixture_id] = snapshot
        return snapshot

    def build_preview(self, snapshot: SourceSnapshot) -> KBPreview:
        if not self._active or self._snapshots.get(snapshot.fixture.fixture_id) is not snapshot:
            raise PreviewUnavailableError("Lab source unavailable or stale; reopen an admitted session.")
        case = snapshot.fixture
        body = [NOTICE, "Fictional source statements and manually authored proposals; not verified technical guidance.",
                "", "Source statements"]
        body.extend(f"{s.reference}: {s.text}" for s in case.sources)
        body.extend(("", "Authored proposals — canonical targets unresolved"))
        body.extend(f"{p.role}: {'; '.join(p.qualifications)} [source: {p.source_field}]" for p in case.proposals)
        if not case.proposals:
            body.append("No authored proposals. This is not an extraction result.")
        body.extend(("", "Technical verification, causal acceptance and publication: NOT PERFORMED.",
                     "", "Synthetic reference", snapshot.reference_text))
        preview = KBPreview(snapshot, case.title, "Temporary synthetic review; canonical identities unresolved.", "\n".join(body))
        for name in ("title", "summary", "body"):
            validate_edit(name, getattr(preview, name))
        return preview

    def invalidate(self) -> None:
        self._active = False
        self._snapshots.clear()
