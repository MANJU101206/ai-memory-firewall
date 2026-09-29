"""Detects sensitive values (email, phone, API-key-like strings) using regex."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    """One detected sensitive value and where it sits in the text."""
    category: str   # "EMAIL", "PHONE" or "API_KEY"
    value: str      # the original sensitive text
    start: int      # index where it begins
    end: int        # index where it ends (exclusive)


EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)

PHONE_CANDIDATE = re.compile(r"(?<![\w+])[+(]?\d[\d\s().-]{8,18}\d(?!\w)")

API_KEY_PATTERNS = [
    re.compile(r"\b(?i:sk|pk|api|key|token)[-_][A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
]


def _find_emails(text):
    return [Finding("EMAIL", m.group(), m.start(), m.end())
            for m in EMAIL_PATTERN.finditer(text)]


def _find_phones(text):
    findings = []
    for m in PHONE_CANDIDATE.finditer(text):
        digit_count = sum(ch.isdigit() for ch in m.group())
        if 10 <= digit_count <= 13:
            findings.append(Finding("PHONE", m.group(), m.start(), m.end()))
    return findings


def _find_api_keys(text):
    findings = []
    for pattern in API_KEY_PATTERNS:
        for m in pattern.finditer(text):
            findings.append(Finding("API_KEY", m.group(), m.start(), m.end()))
    return findings


def _remove_overlaps(findings):
    """If two findings overlap, keep the earlier / longer one."""
    findings = sorted(findings, key=lambda f: (f.start, -(f.end - f.start)))
    kept = []
    for f in findings:
        if not kept or f.start >= kept[-1].end:
            kept.append(f)
    return kept


def detect_sensitive_text(text):
    """Return a list of Finding objects, ordered by position in the text."""
    if not text or not text.strip():
        return []
    all_findings = _find_emails(text) + _find_phones(text) + _find_api_keys(text)
    return _remove_overlaps(all_findings)
