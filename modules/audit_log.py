"""Tracks usage counts for the audit dashboard.

By design this module never stores raw prompts, original sensitive values,
or uploaded images — only counters. Everything lives in Streamlit's
session_state, so it resets whenever the app restarts (there is no database
and no file written to disk).
"""

import streamlit as st

_DEFAULT_STATE = {
    "text_scans": 0,               # number of times "Scan prompt" was clicked
    "redaction_counts": {},        # {"EMAIL": 3, "PHONE": 1, ...}
    "image_scans": 0,              # number of images processed
    "images_with_faces": 0,        # images where >=1 face was found
    "faces_blurred": 0,            # total faces blurred across all images
    "chatbot_sends": 0,            # number of times a prompt was sent to the mock chatbot
    "leak_checks_clean": 0,        # chatbot replies with no leak
    "leak_checks_flagged": 0,      # chatbot replies with >=1 leak
    "leaked_value_count": 0,       # total individual leaked values seen
}


def init_audit_state():
    """Make sure the audit counters exist in session_state. Call this once near the top of app.py."""
    if "audit" not in st.session_state:
        st.session_state["audit"] = dict(_DEFAULT_STATE)
        st.session_state["audit"]["redaction_counts"] = {}


def record_text_scan(findings):
    """Call after a text scan. findings: list of Finding objects (category, value, ...)."""
    audit = st.session_state["audit"]
    audit["text_scans"] += 1
    for f in findings:
        audit["redaction_counts"][f.category] = audit["redaction_counts"].get(f.category, 0) + 1


def record_image_scan(face_count):
    """Call after an image has been processed. face_count: number of faces detected."""
    audit = st.session_state["audit"]
    audit["image_scans"] += 1
    if face_count > 0:
        audit["images_with_faces"] += 1
    audit["faces_blurred"] += face_count


def record_chatbot_send():
    """Call whenever a sanitized prompt is sent to the mock chatbot."""
    st.session_state["audit"]["chatbot_sends"] += 1


def record_leak_check(leaks):
    """Call after checking a chatbot response. leaks: list of Leak objects."""
    audit = st.session_state["audit"]
    if leaks:
        audit["leak_checks_flagged"] += 1
        audit["leaked_value_count"] += len(leaks)
    else:
        audit["leak_checks_clean"] += 1


def get_summary():
    """Return the current audit counters as a plain dict, safe to display."""
    return dict(st.session_state["audit"])


def reset_audit():
    """Clear all counters back to zero."""
    st.session_state["audit"] = dict(_DEFAULT_STATE)
    st.session_state["audit"]["redaction_counts"] = {}
