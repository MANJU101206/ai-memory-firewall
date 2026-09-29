"""Replaces detected sensitive values with placeholders."""

from collections import Counter

PLACEHOLDERS = {
    "EMAIL": "[EMAIL REDACTED]",
    "PHONE": "[PHONE REDACTED]",
    "API_KEY": "[API KEY REDACTED]",
}


def redact_text(text, findings):
    result = text
    for f in sorted(findings, key=lambda f: f.start, reverse=True):
        placeholder = PLACEHOLDERS.get(f.category, "[REDACTED]")
        result = result[:f.start] + placeholder + result[f.end:]
    return result


def count_by_category(findings):
    return dict(Counter(f.category for f in findings))
