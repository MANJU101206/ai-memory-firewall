"""Quick checks for the Day 1 modules. Run with: python test_text_module.py"""

from modules.redactor import redact_text
from modules.text_detector import detect_sensitive_text

cases = [
    ("No sensitive data", "Explain how binary search works.", []),
    ("Email only", "Contact me at asha.demo@example.com", ["EMAIL"]),
    ("Phone only", "Call +91 98765 43210 tomorrow", ["PHONE"]),
    ("API key only", "My key is sk-demo-1234567890abcdefghij", ["API_KEY"]),
    (
        "Multiple values",
        "Mail asha.demo@example.com, call 9876543210, key sk-demo-1234567890abcdefghij",
        ["EMAIL", "PHONE", "API_KEY"],
    ),
]

passed = 0
for name, text, expected in cases:
    found = [f.category for f in detect_sensitive_text(text)]
    ok = found == expected
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'} | {name}: expected {expected}, got {found}")

print(f"\n{passed}/{len(cases)} passed")
print(redact_text(cases[4][1], detect_sensitive_text(cases[4][1])))
