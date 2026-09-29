                                  AI Memory Firewall

**A Privacy Shield for Sensitive Text and Face Data in AI Chatbots**

AI Memory Firewall is a privacy-focused web application that sits between a user and an AI chatbot. It scans user prompts for sensitive information such as email addresses, phone numbers, and API-key-like strings, and scans uploaded images for human faces — redacting or blurring each before anything is sent onward.

A local, offline mock chatbot simulates a real AI response so the prototype works without any paid API or internet dependency. A response leakage checker then verifies whether any original sensitive value re-appears in that reply, and an audit dashboard tracks scan and redaction counts — without ever storing the raw prompts, original values, or uploaded images themselves.

The project demonstrates, in a small and explainable way, how accidental exposure of personal data can be reduced when interacting with AI chatbots.

## Problem Statement

- People frequently paste personal or confidential details — emails, phone numbers, API keys — directly into AI chatbot prompts, often without noticing.
- Uploaded images can contain identifiable faces that get sent to a third-party AI service along with the request.
- Most chat interfaces offer no local checkpoint to review or redact this information before it is sent.
- There is no lightweight way to check whether a chatbot's own reply has accidentally echoed back something sensitive.

**Objective:** build a privacy layer that catches this exposure locally, before data ever leaves the user's device.

## Objectives

1. **Detect** — Identify emails, phone numbers, API-key-like strings in text, and faces in images.
2. **Redact & Blur** — Let the user review findings and choose what gets masked before sending.
3. **Simulate Safely** — Send only the sanitized version to a local mock chatbot — no API key needed.
4. **Verify** — Check the chatbot's reply for reappearance of the original sensitive values.
5. **Audit** — Track scan and redaction counts, without ever storing the raw sensitive data.
6. **Explain** — Keep every module simple, modular, and easy to demonstrate in a viva.

## Proposed System

- A Streamlit web application acting as a checkpoint between the user and any AI chatbot.
- Regex-based scanning for sensitive text — fast, local, and fully explainable, with no external service calls.
- OpenCV Haar-cascade face detection for images, with Gaussian blur applied locally on the user's machine.
- An offline, rule-based mock chatbot so the entire demo runs with no API key and no internet dependency.
- A leak checker and a count-only audit dashboard that never stores raw prompts, values, or images.

**Design Principle:** Nothing sensitive leaves the checkpoint unreviewed, and nothing sensitive is stored once the session ends. The system reduces accidental exposure — it does not claim to guarantee complete privacy.

## System Architecture

```
User Prompt / Image
        │
        ▼
  Detect (regex + OpenCV)
        │
        ▼
  Review & Redact / Blur
        │
        ▼
     Mock Chatbot
        │
        ▼
    Leak Checker
        │
        ▼
   Audit Dashboard
```

Each stage is an independent Python module — `app.py` only calls them in sequence and displays the results. Only the sanitized text ever reaches the mock chatbot.

## Modules Implemented

| Module | Description |
|---|---|
| `text_detector.py` | Regex-based detection of emails, phone numbers, and API-key-like strings. |
| `redactor.py` | Replaces chosen detections with placeholders; counts redactions by category. |
| `image_blur.py` | OpenCV Haar-cascade face detection with local Gaussian blur. |
| `mock_chatbot.py` | Offline, rule-based fake chatbot — no API key, no internet needed. |
| `leak_checker.py` | Scans a chatbot reply for reappearance of the original sensitive values. |
| `audit_log.py` | Session-only counters for scans, redactions, and leaks — no raw data stored. |

## Technology Stack

| Category | Choice |
|---|---|
| Language | Python 3.10+ |
| Web Interface | Streamlit |
| Text Detection | Regex (built-in `re` module) |
| Image Processing | OpenCV (Haar cascade) + Pillow |
| Numerical Support | NumPy |
| Chatbot | Local rule-based mock — no external API |
| Data Storage | None — session-only, in-memory counters |
| Development Tool | VS Code + Python virtual environment (venv) |

## Key Features

- Live scan of prompts for 3 sensitive-data categories
- User-controlled redaction by category, not all-or-nothing
- Local face detection and blurring on uploaded images
- Offline mock chatbot — zero API keys, zero internet calls
- Automatic leak check comparing replies to original values
- Session audit dashboard with live charts — counts only
- Cosmetic session-name greeting (no real accounts/passwords)
- Dark, responsive interface with a custom project logo

## Results

- **Text Detection & Redaction:** A sample prompt containing an email, a phone number, and an API key was scanned. All three were correctly detected, categorized, and redacted — with the sanitized version shown side-by-side with the original for review.
- **Chatbot & Leak Detection:** In a demo run, the mock chatbot's reply was seeded to include an original phone number. The leak checker correctly flagged the reply and identified the exact category and value that reappeared.
- **Audit Dashboard:** The dashboard aggregates scan, redaction, and leak-check counts across the session as live charts. No raw prompt, image, or sensitive value is ever written to this log — only counters.

## Testing Approach

| Test Case | Expected Outcome |
|---|---|
| Clean text (no sensitive data) | No findings returned |
| Text with multiple sensitive values | All categories detected & redacted |
| Image with a detectable face | Face(s) found and blurred |
| Image with no face | "No faces detected" shown |
| Chatbot reply seeded with a leak | Leak checker flags the value |
| Chatbot reply with no leak | Leak checker reports clean |

Precision, recall, and leak-detection rate are computed from the team's own test runs (true/false positives and negatives counted by hand) — not simulated in advance.

## Limitations & Future Scope

**Limitations**
- Regex can miss context-dependent data such as names or addresses.
- Haar-cascade face detection can miss angled or low-light faces.
- The chatbot is a fixed-rule mock, not a real language model.
- Reduces risk — does not guarantee complete privacy.

**Future Enhancements**
- Named-entity detection (e.g. Microsoft Presidio) for names & addresses
- Deep-learning face detection for angled / low-light images
- Optional connection to a real LLM API behind a user's own key
- Exportable audit reports for institutional use

## Software Requirements

- **Language:** Python 3.10+
- **Web Interface:** Streamlit (Python-based web framework)
- **Text Detection:** Regular Expressions (built-in `re` module)
- **Image Processing:** OpenCV (Haar Cascade face detection) + Pillow
- **Numerical Library:** NumPy
- **Chatbot:** Local rule-based mock — no external API or key
- **Data Storage:** None — session-only, in-memory audit counters
- **Development Tool:** Visual Studio Code + Python virtual environment (venv)
- **Hardware:** Intel i3 or higher, 4 GB RAM — no GPU or camera required

## Getting Started

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-memory-firewall

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Conclusion

AI Memory Firewall demonstrates that a lightweight, fully local privacy checkpoint can meaningfully reduce accidental exposure of personal data when using AI chatbots — without requiring any paid API, cloud service, or complex infrastructure.

By combining text pattern matching, local face detection, an offline mock chatbot, response leak checking, and a privacy-respecting audit trail, the project shows an end-to-end, explainable approach to a real and growing privacy concern.

## References

1. P. Viola and M. Jones, "Rapid Object Detection Using a Boosted Cascade of Simple Features," *Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR)*, vol. 1, pp. 511–518, 2001. doi:10.1109/CVPR.2001.990517
2. B. Yan, K. Li, M. Xu, Y. Dong, Y. Zhang, Z. Ren, and X. Cheng, "On Protecting the Data Privacy of Large Language Models (LLMs): A Survey," arXiv:2403.05156, 2024.
3. S. Cheng, Z. Li, S. Meng, M. Ren, H. Xu, C. Yue, and F. Zhang, "Understanding PII Leakage in Large Language Models: A Systematic Survey," *Proc. IJCAI 2025*, pp. 10409–10417. doi:10.24963/ijcai.2025/1156
4. Microsoft, "Presidio: Context-aware, pluggable and customizable data protection and de-identification SDK," GitHub repository, github.com/microsoft/presidio.
5. OpenCV Team, "Cascade Classifier — OpenCV Documentation," docs.opencv.org.
6. Streamlit Inc., "Streamlit Documentation," docs.streamlit.io.

## Team

- Manjushri V S
- Aashimathul Asmi H

**Under the guidance of:** Dr. B. Vijayakumar, Associate Professor

**Department of Information Technology**
