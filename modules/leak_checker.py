"""Checks a chatbot response for reappearance of the original sensitive values.

This module only ever receives the original values already held in memory
from the scan step. It does not store them anywhere itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Leak:
    category: str
    value: str


def check_for_leaks(response_text, original_findings):
    """Return a list of Leak objects for any original value found in response_text."""
    if not response_text or not original_findings:
        return []

    leaks = []
    seen_values = set()
    response_lower = response_text.lower()

    for finding in original_findings:
        value = finding.value
        if value in seen_values:
            continue
        if value.lower() in response_lower:
            leaks.append(Leak(category=finding.category, value=value))
            seen_values.add(value)

    return leaks
