"""Bounded offline Clipboard assessment; findings never grant capture consent.

Rules recognize selected secret shapes, not every possible secret. No content,
digest, preview, match span or reversible fingerprint leaves this pure owner.
There is deliberately no persistence, logging, Settings or authority dependency.
"""

from dataclasses import dataclass
from enum import Enum
import re
import unicodedata
from typing import ClassVar

from f7hub.domain.clipboard import AdmittedManualText, IDENTITY_PROFILE, MAX_TEXT_BYTES


class ClipboardPrivacyFinding(str, Enum):
    PERMITTED = "PERMITTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    POSSIBLE_SECRET = "POSSIBLE_SECRET"
    ASSESSMENT_FAILED = "ASSESSMENT_FAILED"
    INCOMPLETE = "INCOMPLETE"


class ClipboardAssessmentReason(str, Enum):
    NO_RECOGNIZED_RISK = "NO_RECOGNIZED_RISK"
    CREDENTIAL_SHAPE = "CREDENTIAL_SHAPE"
    AMBIGUOUS_OR_SENSITIVE = "AMBIGUOUS_OR_SENSITIVE"
    UNSUPPORTED_SOURCE = "UNSUPPORTED_SOURCE"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    DETECTOR_ERROR = "DETECTOR_ERROR"


_F = ClipboardPrivacyFinding
_R = ClipboardAssessmentReason
_REASONS = {
    _F.PERMITTED: (_R.NO_RECOGNIZED_RISK,),
    _F.NEEDS_REVIEW: (_R.AMBIGUOUS_OR_SENSITIVE,),
    _F.POSSIBLE_SECRET: (_R.CREDENTIAL_SHAPE,),
    _F.ASSESSMENT_FAILED: (_R.DETECTOR_ERROR,),
    _F.INCOMPLETE: (_R.UNSUPPORTED_SOURCE, _R.RESOURCE_LIMIT),
}


@dataclass(frozen=True, slots=True)
class ClipboardPrivacyAssessment:
    """Fixed content-free provenance. A constructible finding is not authority."""

    finding: ClipboardPrivacyFinding
    reason: ClipboardAssessmentReason
    assessment_method: ClassVar[str] = "clipboard_local_rules"
    assessment_version: ClassVar[str] = "1"

    def __post_init__(self) -> None:
        if (type(self.finding) is not ClipboardPrivacyFinding
                or type(self.reason) is not ClipboardAssessmentReason
                or self.reason not in _REASONS[self.finding]):
            raise ValueError("Clipboard assessment classification is invalid.")

    @property
    def assessment_complete(self) -> bool:
        return self.finding in (_F.PERMITTED, _F.NEEDS_REVIEW, _F.POSSIBLE_SECRET)


# No configurable rules, plugins or caller-provided detector/permission flags.
# Repetition is over simple character classes; input and normalized view are
# bounded before scanning. No decoding, recursive parsing or regex backreferences.
_LABEL = (
    r"(?:pass(?:word|wd|phrase)?|pwd|mot[ _-]*de[ _-]*passe|credential[s]?|"
    r"secret|client[ _-]*secret|api[ _-]*key|access[ _-]*key|"
    r"(?:access|refresh|auth|id|session)[ _-]*token|token|"
    r"account[ _-]*key|shared[ _-]*access[ _-]*signature|"
    r"aws[ _-]*secret[ _-]*access[ _-]*key|private[ _-]*key|"
    r"recovery[ _-]*(?:code|key)|backup[ _-]*code|"
    r"one[ _-]*time[ _-]*(?:password|code)|verification[ _-]*code|"
    r"security[ _-]*code|otp|totp|mfa[ _-]*code|pin|sig)"
)
_SECRET_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE | re.ASCII) for pattern in (
    r"(?<![A-Za-z0-9])" + _LABEL + r"\b[ \t\"']{0,8}(?:=|:|\bis\b|\best\b)",
    r"\b(?:authorization|proxy-authorization|cookie|set-cookie)[ \t]*:",
    r"\b(?:bearer|basic)[ \t]+[A-Za-z0-9+/=_~.-]+",
    r"-{2,5}[ \t]*BEGIN[ \t]+(?:[A-Z0-9]+[ \t]+){0,3}PRIVATE[ \t]+KEY\b",
    r"\b(?:ssh-rsa|ssh-ed25519|ecdsa-sha2-nistp[0-9]+)[ \t]+[A-Za-z0-9+/=]{20,}",
    r"\b[a-z][a-z0-9+.-]{0,31}://[^\s/@]{1,256}@",
    r"\b(?:eyJ[A-Za-z0-9_-]{5,})\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    r"\b(?:sk-(?:proj-|live-|test-)?|gh[pousr]_|github_pat_|xox[baprs]-|"
    r"AIza|SG\.)[A-Za-z0-9_.-]{8,}",
    r"\b(?:password|passphrase|recovery[ -]*code|one[ -]*time[ -]*code|otp|mfa)"
    r"[ \t]+[A-Za-z0-9_-]{4,}",
    r"^\s*[0-9]{6,8}\s*$",
))
_AMBIGUOUS_LABEL = re.compile(r"(?<![A-Za-z0-9])" + _LABEL + r"\b", re.IGNORECASE | re.ASCII)
_OPAQUE_TOKEN = re.compile(r"[A-Za-z0-9_+/=-]{24,}", re.ASCII)
_SENSITIVE = re.compile(
    r"\b[^\s@]{1,254}@[^\s@]{1,254}"
    r"|\b[A-Za-z]:[\\/]|\\\\[^\s\\]+\\|/(?:home|Users|etc)/"
    r"|\b(?:hostname|computername|device[ _-]*name|tenant[ _-]*id|"
    r"customer[ _-]*name|confidential)\b"
    r"|\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b"
    r"|%[0-9a-f]{2}|\\[ux][0-9a-f]{2}",
    re.IGNORECASE | re.ASCII,
)
MAX_ASSESSMENT_SCALARS = MAX_TEXT_BYTES * 2


def _scan(text: str) -> ClipboardPrivacyAssessment:
    if any(pattern.search(text) is not None for pattern in _SECRET_PATTERNS):
        return ClipboardPrivacyAssessment(_F.POSSIBLE_SECRET, _R.CREDENTIAL_SHAPE)
    for match in _OPAQUE_TOKEN.finditer(text):
        token = match.group()
        if any(c.isalpha() for c in token) and any(c.isdigit() for c in token):
            return ClipboardPrivacyAssessment(_F.POSSIBLE_SECRET, _R.CREDENTIAL_SHAPE)
    if (_AMBIGUOUS_LABEL.search(text) is not None or _SENSITIVE.search(text) is not None
            or any(unicodedata.category(c) in ("Cf", "Cs")
                   or (unicodedata.category(c) == "Cc" and c not in "\r\n\t") for c in text)):
        return ClipboardPrivacyAssessment(_F.NEEDS_REVIEW, _R.AMBIGUOUS_OR_SENSITIVE)
    return ClipboardPrivacyAssessment(_F.PERMITTED, _R.NO_RECOGNIZED_RISK)


def assess_manual_text(source: AdmittedManualText) -> ClipboardPrivacyAssessment:
    """Assess a complete exact-text candidate, with no persistence permission.

    The original is never changed. NFKC is a bounded detection-only view to catch
    compatibility forms; unsupported/obfuscated formats are not decoded. Missing
    or failed work denies eligibility. Only ordinary Exception is converted;
    process cancellation still propagates without opening any writer.
    """
    try:
        if (type(source) is not AdmittedManualText or type(source.text) is not str
                or source.media_type != "text/plain" or source.identity_profile != IDENTITY_PROFILE):
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.UNSUPPORTED_SOURCE)
        text = source.text
        if len(text) > MAX_TEXT_BYTES:
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.RESOURCE_LIMIT)
        if not text.strip() or "\0" in text:
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.UNSUPPORTED_SOURCE)
        try:
            size = len(text.encode("utf-8", errors="strict"))
        except UnicodeError:
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.UNSUPPORTED_SOURCE)
        if size > MAX_TEXT_BYTES:
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.RESOURCE_LIMIT)
        view = unicodedata.normalize("NFKC", text)
        if len(view) > MAX_ASSESSMENT_SCALARS:
            return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.RESOURCE_LIMIT)
        # Scan both views: normalization may expose credential spellings but may
        # also remove controls/presentation distinctions relevant to sensitivity.
        original = _scan(text)
        normalized = _scan(view)
        for finding in (_F.POSSIBLE_SECRET, _F.NEEDS_REVIEW):
            for result in (original, normalized):
                if result.finding == finding:
                    return result
        return original
    except MemoryError:
        return ClipboardPrivacyAssessment(_F.INCOMPLETE, _R.RESOURCE_LIMIT)
    except Exception:
        # Never stringify, log, retain or chain a detector exception.
        return ClipboardPrivacyAssessment(_F.ASSESSMENT_FAILED, _R.DETECTOR_ERROR)
