"""A fake chatbot so the project runs with no API keys and no internet.

It picks a canned response based on simple keyword matching. It never sees
the original sensitive values, only the sanitized prompt, unless the demo
"simulate a leak" option deliberately injects one value for testing.
"""

import random

_KEYWORD_RESPONSES = [
    (("debug", "error", "bug", "script"),
     "Sure, I can help debug that. Could you share the exact error message "
     "and the relevant lines of code?"),
    (("sort", "sorting", "algorithm"),
     "Common sorting algorithms include bubble sort, merge sort and quick "
     "sort. Merge sort runs in O(n log n) time in all cases."),
    (("binary search",),
     "Binary search repeatedly halves a sorted list to find a target value "
     "in O(log n) time."),
    (("resume", "cv", "interview"),
     "Happy to help with that. Could you share which role you're targeting "
     "and I'll suggest how to phrase it?"),
    (("report", "send", "email", "contact"),
     "Got it, I've noted the request. Let me know if there's anything else "
     "you'd like included."),
]

_DEFAULT_RESPONSES = [
    "Thanks for the message! Could you tell me a bit more about what "
    "you're trying to achieve?",
    "I can help with that. What would you like me to focus on first?",
    "Understood. Here's a general starting point — let me know if you'd "
    "like more detail on any part of it.",
]


def generate_mock_response(sanitized_prompt, original_findings=None, simulate_leak=False):
    """Return a canned reply to sanitized_prompt.

    simulate_leak (demo/testing only): when True and original_findings is
    non-empty, one original sensitive value is deliberately inserted into
    the reply so the leak checker has something real to catch. This mirrors
    test case "a chatbot response containing a seeded sensitive value" and
    must only be used for that purpose, never for real prompts.
    """
    text_lower = sanitized_prompt.lower()
    response = None
    for keywords, reply in _KEYWORD_RESPONSES:
        if any(keyword in text_lower for keyword in keywords):
            response = reply
            break
    if response is None:
        response = random.choice(_DEFAULT_RESPONSES)

    if simulate_leak and original_findings:
        leaked_value = random.choice(original_findings).value
        response += f" By the way, just to confirm, was that {leaked_value}?"

    return response
