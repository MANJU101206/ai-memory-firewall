"""AI Memory Firewall - Streamlit interface.
Day 1: text scanning + redaction.
Day 2: face blurring, mock chatbot, response leak checking.
"""

import base64

import pandas as pd
import streamlit as st
from PIL import Image

from modules.audit_log import (
    get_summary,
    init_audit_state,
    record_chatbot_send,
    record_image_scan,
    record_leak_check,
    record_text_scan,
    reset_audit,
)
from modules.image_blur import detect_and_blur_faces
from modules.leak_checker import check_for_leaks
from modules.mock_chatbot import generate_mock_response
from modules.redactor import count_by_category, redact_text
from modules.text_detector import detect_sensitive_text

init_audit_state()

SAMPLE_PROMPT = (
    "Hi, I'm Asha. Email me at asha.demo@example.com or call +91 98765 43210. "
    "My API key is sk-demo-1234567890abcdefghij, please help me debug my script."
)

CATEGORY_LABELS = {"EMAIL": "Emails", "PHONE": "Phone numbers", "API_KEY": "API keys"}

with open("assets/logo.png", "rb") as _f:
    LOGO_B64 = base64.b64encode(_f.read()).decode()
LOGO_DATA_URI = f"data:image/png;base64,{LOGO_B64}"

st.set_page_config(page_title="AI Memory Firewall", page_icon=Image.open("assets/logo_small.png"), layout="wide")

# --- Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html {scroll-behavior: smooth;}
    #MainMenu, footer {visibility: hidden;}
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}

    @keyframes bgShift {
        0%   {background-position: 0% 50%;}
        50%  {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(120deg, #0B1120, #0F172A, #0B1120, #111827);
        background-size: 300% 300%;
        animation: bgShift 18s ease infinite;
    }

    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(14px);}
        to   {opacity: 1; transform: translateY(0);}
    }
    .block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1100px;}

    .navbar {
        display: flex; align-items: center; justify-content: space-between;
        background: #0B1120;
        border: 1px solid #1F2937; border-radius: 14px;
        padding: .7rem 1.2rem; margin: .4rem 0 1.2rem;
    }
    .navbar .brand {font-weight: 800; color: #E2E8F0; font-size: 1.02rem;}
    .navbar .brand span {color: #14B8A6;}
    .navbar .links {display: flex; gap: 1.4rem;}
    .navbar .links a {
        color: #94A3B8; text-decoration: none; font-size: .85rem; font-weight: 600;
        transition: color .15s ease;
    }
    .navbar .links a:hover {color: #5EEAD4;}
    .navbar .pill {
        background: #0B3B36; color: #5EEAD4; border: 1px solid #115E59;
        border-radius: 999px; padding: .2rem .7rem; font-size: .75rem; font-weight: 700;
    }
    @media (max-width: 640px) {.navbar .links {display: none;}}

    .hero {
        background: linear-gradient(135deg, #0F766E 0%, #115E59 55%, #0B3B36 100%);
        color: #fff; padding: 2.2rem 2.4rem; border-radius: 18px; margin-bottom: 1.3rem;
        box-shadow: 0 10px 30px -12px rgba(20,184,166,.35);
        animation: fadeInUp .6s ease-out;
    }
    .hero .badge {
        display: inline-block; background: rgba(255,255,255,.14); color: #fff;
        padding: .2rem .7rem; border-radius: 999px; font-size: .75rem; font-weight: 600;
        letter-spacing: .04em; margin-bottom: .6rem;
    }
    .hero h1 {margin: 0; font-size: 2.3rem; color: #fff; font-weight: 800;}
    .hero p {margin: .5rem 0 0; font-size: 1.05rem; opacity: .9; color: #fff; max-width: 640px;}

    .note {
        background: #2A1E0E; border: 1px solid #78350F; border-left: 4px solid #F59E0B;
        padding: .75rem 1.1rem; border-radius: 10px; font-size: .9rem; color: #FCD34D;
        margin-bottom: 1.4rem; animation: fadeInUp .6s ease-out .1s backwards;
    }

    .card {
        background: #111827; border: 1px solid #1F2937; border-radius: 16px;
        padding: 1.6rem 1.8rem; margin-bottom: 1.3rem;
        box-shadow: 0 1px 3px rgba(0,0,0,.4);
        animation: fadeInUp .55s ease-out backwards;
    }
    .card h2, .card h3, .card label, .card p, .card div {color: #E2E8F0;}

    .step {
        display: inline-flex; align-items: center; gap: .4rem;
        background: #0B3B36; color: #5EEAD4; border: 1px solid #115E59;
        border-radius: 999px; padding: .25rem .85rem; font-size: .8rem; font-weight: 700;
        letter-spacing: .03em; margin-bottom: .7rem;
    }

    .feature-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; margin-top: .8rem;
        animation: fadeInUp .6s ease-out .15s backwards;
    }
    .feature {
        background: #111827; border: 1px solid #1F2937; border-radius: 12px;
        padding: .9rem 1rem; text-align: center;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .feature:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px -8px rgba(20,184,166,.45);
    }
    .feature .icon {font-size: 1.5rem;}
    .feature .label {font-weight: 600; font-size: .85rem; color: #E2E8F0; margin-top: .3rem;}

    .chat-bubble {
        background: #0B3B36; border: 1px solid #115E59; border-radius: 14px;
        padding: 1rem 1.2rem; margin-top: .5rem; font-size: .95rem; color: #99F6E4;
        animation: fadeInUp .4s ease-out;
    }

    div[data-testid="stMetric"] {
        background: #111827; border: 1px solid #1F2937; border-radius: 12px; padding: .8rem 1rem;
        transition: transform .15s ease;
    }
    div[data-testid="stMetric"]:hover {transform: translateY(-2px);}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {color: #E2E8F0 !important;}

    div.stButton > button {
        border-radius: 10px; font-weight: 600;
        transition: transform .15s ease, box-shadow .15s ease;
        background: #1F2937; color: #E2E8F0; border: 1px solid #374151;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px -6px rgba(0,0,0,.5);
        border-color: #14B8A6;
    }
    div.stButton > button[kind="primary"] {background: #0F766E; border-color: #0F766E; color: #fff;}
    div.stButton > button[kind="primary"]:hover {background: #14B8A6; border-color: #14B8A6;}

    .app-footer {
        text-align: center; color: #64748B; font-size: .82rem;
        margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #1F2937;
    }

    section[data-testid="stSidebar"] {background: #0B1120; border-right: 1px solid #1F2937;}

    .anchor {display: block; position: relative; top: -80px; visibility: hidden;}

    .logo-img {vertical-align: middle; border-radius: 8px;}

    .welcome-wrap {
        display: flex; align-items: center; justify-content: center;
        min-height: 70vh; animation: fadeInUp .5s ease-out;
    }
    .welcome-card {
        background: #111827; border: 1px solid #1F2937; border-radius: 20px;
        padding: 2.6rem 2.8rem; box-shadow: 0 20px 45px -20px rgba(0,0,0,.6);
        text-align: center; max-width: 440px;
    }
    .welcome-card .icon {font-size: 2.6rem;}
    .welcome-card h2 {margin: .6rem 0 .2rem; color: #E2E8F0;}
    .welcome-card p {color: #94A3B8; font-size: .92rem; margin-bottom: 1.2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def load_sample():
    st.session_state["prompt"] = SAMPLE_PROMPT


def clear_prompt():
    st.session_state["prompt"] = ""
    for key in ("findings", "scanned_text", "chatbot_response", "leaks"):
        st.session_state.pop(key, None)


# --- Welcome gate (cosmetic only: no accounts, no passwords, nothing stored) ---
if "visitor_name" not in st.session_state:
    st.session_state["visitor_name"] = ""

if not st.session_state["visitor_name"]:
    st.markdown('<div class="welcome-wrap"><div class="welcome-card">', unsafe_allow_html=True)
    st.markdown(
        f'<img src="{LOGO_DATA_URI}" class="logo-img" width="72"><h2>AI Memory Firewall</h2>'
        '<p>Enter your name to start your session. This is just a greeting — '
        "no account is created and nothing is saved.</p>",
        unsafe_allow_html=True,
    )
    name_input = st.text_input("Your name", placeholder="e.g. Asha", label_visibility="collapsed")
    if st.button("Enter →", type="primary", width="stretch"):
        st.session_state["visitor_name"] = name_input.strip() or "Guest"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# --- Top navbar ---
st.markdown(
    f"""
    <div class="navbar">
      <div class="brand"><img src="{LOGO_DATA_URI}" class="logo-img" width="26"> AI Memory <span>Firewall</span></div>
      <div class="links">
        <a href="#sec-text">Text</a>
        <a href="#sec-image">Image</a>
        <a href="#sec-chatbot">Chatbot</a>
        <a href="#sec-dashboard">Dashboard</a>
      </div>
      <div class="pill">👋 {st.session_state['visitor_name']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown(f'<img src="{LOGO_DATA_URI}" class="logo-img" width="28"> **AI Memory Firewall**', unsafe_allow_html=True)
    st.caption("Mini-project · CSE 3rd year")
    st.divider()
    st.write(
        "A privacy layer that sits between you and an AI chatbot. It finds sensitive "
        "details in text and faces in images, lets you redact or blur them, and "
        "checks the chatbot's reply for anything that slipped through."
    )
    st.markdown("**How it works**")
    st.markdown(
        "1. Type or paste a prompt, optionally attach an image\n"
        "2. Scan for sensitive text and faces\n"
        "3. Review and choose what to redact / blur\n"
        "4. Send the sanitized version to the (mock) chatbot\n"
        "5. Check the reply for leaked data"
    )
    st.markdown("**Currently detects**")
    st.markdown("📧 Email addresses  \n📱 Phone numbers  \n🔑 API-key-like strings  \n🙂 Faces in images")
    st.divider()
    st.markdown("**Limitations**")
    st.caption(
        "Pattern matching can miss data such as names or addresses, face "
        "detection can miss angled or low-light faces, and the chatbot here "
        "is a offline mock, not a real AI model. This tool reduces risk; it "
        "does not guarantee complete privacy."
    )

    st.divider()
    st.caption(f"Signed in as **{st.session_state['visitor_name']}**")
    if st.button("Switch session"):
        st.session_state["visitor_name"] = ""
        st.rerun()

# --- Hero ---
st.markdown(
    f"""
    <div class="hero">
      <span class="badge">🔒 PRIVACY PROTOTYPE</span>
      <h1><img src="{LOGO_DATA_URI}" class="logo-img" width="40"> AI Memory Firewall</h1>
      <p>Welcome, {st.session_state['visitor_name']} 👋 — catch and redact sensitive text and faces
      before they ever reach an AI chatbot, running entirely on your machine.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="note">🔎 Use <b>synthetic (fake) data and sample photos only</b> '
    "while testing. All scanning and blurring run locally on your computer — "
    "nothing is uploaded.</div>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="feature-grid">
      <div class="feature"><div class="icon">📧</div><div class="label">Email detection</div></div>
      <div class="feature"><div class="icon">📱</div><div class="label">Phone detection</div></div>
      <div class="feature"><div class="icon">🔑</div><div class="label">API key detection</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# ============================ STEP 1: TEXT ============================
st.markdown('<span id="sec-text" class="anchor"></span>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<span class="step">STEP 1</span>', unsafe_allow_html=True)
st.subheader("Enter your prompt")
st.text_area(
    "Prompt to send to the chatbot",
    key="prompt",
    height=160,
    placeholder="Type or paste a prompt here, or click 'Load sample'...",
)

col1, col2, col3, _ = st.columns([1, 1, 1.3, 3])
col1.button("Load sample", on_click=load_sample)
col2.button("Clear", on_click=clear_prompt)
scan_clicked = col3.button("🔍 Scan prompt", type="primary")

if scan_clicked:
    prompt_text = st.session_state.get("prompt", "")
    if not prompt_text.strip():
        st.warning("Please enter some text first.")
    else:
        new_findings = detect_sensitive_text(prompt_text)
        st.session_state["findings"] = new_findings
        st.session_state["scanned_text"] = prompt_text
        record_text_scan(new_findings)
        for key in ("chatbot_response", "leaks"):
            st.session_state.pop(key, None)
st.markdown("</div>", unsafe_allow_html=True)

# ============================ STEP 2: TEXT REVIEW ============================
findings = st.session_state.get("findings")
to_redact = []
if findings is not None:
    scanned_text = st.session_state["scanned_text"]
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step">STEP 2</span>', unsafe_allow_html=True)
    st.subheader("Privacy review — text")

    if not findings:
        st.success("✅ No sensitive information detected by the current rules.")
        sanitized_text = scanned_text
        st.text_area("Text that would be sent", sanitized_text, height=120, disabled=True)
    else:
        st.warning(f"⚠️ Detected {len(findings)} sensitive item(s). Review them below.")
        found_categories = sorted({f.category for f in findings})
        chosen = st.multiselect(
            "Categories to redact", found_categories, default=found_categories
        )
        to_redact = [f for f in findings if f.category in chosen]

        counts = count_by_category(to_redact)
        metric_cols = st.columns(max(len(found_categories), 1))
        for col, category in zip(metric_cols, found_categories):
            col.metric(f"{CATEGORY_LABELS.get(category, category)} redacted", counts.get(category, 0))

        left, right = st.columns(2)
        with left:
            st.markdown("**Detected items**")
            st.dataframe(
                pd.DataFrame([{"Category": f.category, "Value": f.value, "Position": f.start} for f in findings]),
                width="stretch", hide_index=True,
            )
        with right:
            st.markdown("**Sanitized text (what the chatbot would receive)**")
            sanitized_text = redact_text(scanned_text, to_redact)
            st.text_area("sanitized", sanitized_text, height=200, disabled=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================ STEP 3: IMAGE ============================
st.markdown('<span id="sec-image" class="anchor"></span>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<span class="step">STEP 3 · OPTIONAL</span>', unsafe_allow_html=True)
st.subheader("Upload an image to blur faces")
uploaded_image = st.file_uploader("Image (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    original_img = Image.open(uploaded_image)
    blurred_img, face_count = detect_and_blur_faces(original_img)
    if st.session_state.get("last_image_id") != uploaded_image.file_id:
        record_image_scan(face_count)
        st.session_state["last_image_id"] = uploaded_image.file_id

    img_col1, img_col2 = st.columns(2)
    with img_col1:
        st.markdown("**Original**")
        st.image(original_img, width="stretch")
    with img_col2:
        st.markdown("**Faces blurred (what would be sent)**")
        st.image(blurred_img, width="stretch")

    if face_count > 0:
        st.warning(f"⚠️ {face_count} face(s) detected and blurred.")
    else:
        st.info("No faces detected in this image.")
st.markdown("</div>", unsafe_allow_html=True)

# ============================ STEP 4: MOCK CHATBOT ============================
if findings is not None:
    st.markdown('<span id="sec-chatbot" class="anchor"></span>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="step">STEP 4</span>', unsafe_allow_html=True)
    st.subheader("Send to chatbot (mock, offline)")
    st.caption(
        "This is a local, rule-based fake chatbot — no API key and no internet "
        "needed. It only ever sees the sanitized text above."
    )

    simulate_leak = st.checkbox(
        "🧪 Demo only: simulate a response that leaks a redacted value",
        value=False,
        help="For testing the leak checker below. A real chatbot would not "
             "normally do this, since it never saw the original value.",
    )
    send_clicked = st.button("💬 Send sanitized prompt to chatbot")

    if send_clicked:
        response = generate_mock_response(sanitized_text, findings, simulate_leak=simulate_leak)
        leaks_found = check_for_leaks(response, findings)
        st.session_state["chatbot_response"] = response
        st.session_state["leaks"] = leaks_found
        record_chatbot_send()
        record_leak_check(leaks_found)

    if "chatbot_response" in st.session_state:
        st.markdown("**Chatbot response**")
        st.markdown(f'<div class="chat-bubble">{st.session_state["chatbot_response"]}</div>', unsafe_allow_html=True)

        st.markdown("**Leak check**")
        leaks = st.session_state.get("leaks", [])
        if leaks:
            st.error(f"🚨 Possible leak: {len(leaks)} original sensitive value(s) reappeared in the response.")
            st.dataframe(
                pd.DataFrame([{"Category": l.category, "Value": l.value} for l in leaks]),
                width="stretch", hide_index=True,
            )
        else:
            st.success("✅ No original sensitive values found in the chatbot's response.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================ STEP 5: AUDIT DASHBOARD ============================
st.markdown('<span id="sec-dashboard" class="anchor"></span>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<span class="step">STEP 5</span>', unsafe_allow_html=True)
st.subheader("Audit dashboard")
st.caption(
    "Counts only — this dashboard never stores your raw prompts, original "
    "sensitive values, or uploaded images. Counters reset when the app restarts."
)

summary = get_summary()

top_cols = st.columns(4)
top_cols[0].metric("Text scans", summary["text_scans"])
top_cols[1].metric("Images processed", summary["image_scans"])
top_cols[2].metric("Chatbot sends", summary["chatbot_sends"])
total_leak_checks = summary["leak_checks_clean"] + summary["leak_checks_flagged"]
top_cols[3].metric("Leak checks run", total_leak_checks)

st.markdown("**Redactions by category**")
redaction_counts = summary["redaction_counts"]
if redaction_counts:
    chart_df = pd.DataFrame(
        {CATEGORY_LABELS.get(cat, cat): [n] for cat, n in redaction_counts.items()}
    ).T
    chart_df.columns = ["Times detected"]
    st.bar_chart(chart_df, color="#14B8A6", height=220)
    st.dataframe(
        pd.DataFrame(
            [{"Category": CATEGORY_LABELS.get(cat, cat), "Times detected": n}
             for cat, n in redaction_counts.items()]
        ),
        width="stretch", hide_index=True,
    )
else:
    st.caption("No text scans yet.")

img_col1, img_col2 = st.columns(2)
img_col1.metric("Images with a face detected", summary["images_with_faces"])
img_col2.metric("Total faces blurred", summary["faces_blurred"])

leak_col1, leak_col2, leak_col3 = st.columns(3)
leak_col1.metric("Clean responses", summary["leak_checks_clean"])
leak_col2.metric("Flagged responses", summary["leak_checks_flagged"])
leak_col3.metric("Leaked values caught", summary["leaked_value_count"])

if total_leak_checks > 0:
    leak_rate = summary["leak_checks_flagged"] / total_leak_checks * 100
    st.markdown("**Chatbot response outcomes**")
    outcome_df = pd.DataFrame(
        {"Clean": [summary["leak_checks_clean"]], "Flagged": [summary["leak_checks_flagged"]]}
    ).T
    outcome_df.columns = ["Responses"]
    st.bar_chart(outcome_df, color="#F97316", height=180)
    st.caption(f"Leak-flag rate this session: {leak_rate:.1f}% of chatbot responses were flagged.")

if st.button("🗑️ Reset audit counters"):
    reset_audit()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="app-footer">AI Memory Firewall · College mini-project prototype · '
    'Day 3: audit dashboard</div>',
    unsafe_allow_html=True,
)
