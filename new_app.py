import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(
    page_title="SME Cyber Self-Assessment – Pro",
    page_icon="🛡️",
    layout="wide"
)

TITLE = "SME Cyber Self-Assessment – Pro"
SUBTITLE = "Before we talk about cybersecurity, let’s get to know your business a little better. No tech jargon—just what really matters."

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "started_at" not in st.session_state:
    st.session_state.started_at = datetime.utcnow().isoformat(timespec="seconds")

def save(k, v):
    st.session_state.answers[k] = v

# ---------------------------------------------------
# HEADER & NAVIGATION
# ---------------------------------------------------
def header():
    st.title(TITLE)
    st.caption("A separate deployment from your core SME app")
    st.markdown(f"### Getting to Know Your Business")
    st.write(SUBTITLE)
    st.progress((st.session_state.step - 1) / 5)

def nav(prev=True, next=True, validate_ok=True):
    cols = st.columns([1, 1, 6])
    with cols[0]:
        if prev and st.button("← Back"):
            st.session_state.step = max(1, st.session_state.step - 1)
            st.rerun()
    with cols[1]:
        if next and st.button("Next →", type="primary", disabled=not validate_ok):
            st.session_state.step = min(6, st.session_state.step + 1)
            st.rerun()

# ---------------------------------------------------
# SECTION 1 — BUSINESS AT A GLANCE
# ---------------------------------------------------
def section_1():
    st.markdown("#### 🧱 Your Business at a Glance")

    save("business_type", st.text_input(
        "What kind of business do you run?",
        placeholder="e.g., local café, consulting firm, online shop, creative agency"
    ))

    save("years_in_business", st.radio(
        "How long have you been in business?",
        ["Less than a year", "1–3 years", "3–10 years", "Over 10 years"],
        index=None
    ))

    save("team_size", st.radio(
        "Roughly how many people are involved in your business right now?",
        ["Just me", "2–5", "6–20", "More than 20"],
        index=None
    ))

    save("business_mode", st.radio(
        "Would you describe your business as mostly...",
        ["Local and in-person", "Online or remote", "A mix of both"],
        index=None
    ))

    save("turnover", st.radio(
        "Which range fits your yearly turnover best?",
        ["Under €100k", "€100k–500k", "€500k–2M", "Over €2M"],
        index=None
    ))

    required = ["business_type", "years_in_business", "team_size", "business_mode", "turnover"]
    ok = all(st.session_state.answers.get(k) not in [None, "", []] for k in required)
    nav(prev=False, next=True, validate_ok=ok)

# ---------------------------------------------------
# SECTION 2 — TECHNOLOGY USE
# ---------------------------------------------------
def section_2():
    st.markdown("#### 💻 How You Use Technology")

    save("online_sales", st.radio(
        "Do you sell or deliver services online?",
        ["Yes – own website", "Yes – via marketplaces", "No – mostly offline"],
        index=None
    ))

    save("stores_data", st.radio(
        "Do you keep any customer or employee data (emails, invoices, payment info)?",
        ["Yes", "No"],
        index=None
    ))

    save("daily_tools", st.multiselect(
        "Which of these tools do you rely on daily?",
        ["Email", "Accounting software", "CRM or client list",
         "Cloud storage", "Online payment system", "Website or webshop"]
    ))

    save("website_manager", st.radio(
        "Who looks after your website and online systems?",
        ["I do", "Someone on my team", "External freelancer/company"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["online_sales", "stores_data", "website_manager"])
    nav(prev=True, next=True, validate_ok=ok)

# ---------------------------------------------------
# SECTION 3 — IT MANAGEMENT
# ---------------------------------------------------
def section_3():
    st.markdown("#### 🧰 Who Manages Your IT and Accounts")

    save("it_support", st.radio(
        "Who handles computers, email, and systems when something breaks?",
        ["I do", "Freelancer", "IT company", "In-house IT team"],
        index=None
    ))

    save("system_setup", st.radio(
        "Did you personally set up your main systems and accounts?",
        ["Yes, mostly me", "Shared effort", "Someone else handled it"],
        index=None
    ))

    save("asset_list", st.radio(
        "Do you have a clear list of systems, accounts, and devices you use?",
        ["Yes, documented", "Rough idea", "Not really"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["it_support", "system_setup", "asset_list"])
    nav(prev=True, next=True, validate_ok=ok)

# ---------------------------------------------------
# SECTION 4 — PARTNERS
# ---------------------------------------------------
def section_4():
    st.markdown("#### 🤝 Partners and Ecosystem")

    save("partners", st.radio(
        "Do you work with external partners who handle your data or systems?",
        ["Yes", "No"],
        index=None
    ))

    save("num_partners", st.radio(
        "Roughly how many key partners do you rely on?",
        ["0–2", "3–5", "6+"],
        index=None
    ))

    save("breach_response", st.radio(
        "If one had a data breach, would you know what to do?",
        ["Yes, I know who to contact", "Not really sure"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["partners", "num_partners", "breach_response"])
    nav(prev=True, next=True, validate_ok=ok)

# ---------------------------------------------------
# SECTION 5 — CONFIDENCE
# ---------------------------------------------------
def section_5():
    st.markdown("#### 🧭 Confidence & Experience")

    save("preparedness", st.radio(
        "If hit by a cyberattack tomorrow, how prepared would you feel?",
        ["Not at all", "Somewhat", "Fairly confident", "Very confident"],
        index=None
    ))

    save("past_incident", st.radio(
        "Have you experienced a cybersecurity issue before?",
        ["Yes", "No", "Not sure"],
        index=None
    ))

    save("knows_help", st.radio(
        "Do you know who to call if that happened?",
        ["Yes", "No"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["preparedness", "past_incident", "knows_help"])
    nav(prev=True, next=True, validate_ok=ok)

# ---------------------------------------------------
# SCORING, MATURITY, ACTIONS
# ---------------------------------------------------
def compute_scores(a: dict) -> dict:
    scores = {}
    scores["Governance & Visibility"] = 70 if a.get("asset_list") == "Yes, documented" else 50 if a.get("asset_list") == "Rough idea" else 30
    scores["Data Protection"] = 80 if a.get("stores_data") == "Yes" and "Cloud storage" in (a.get("daily_tools") or []) else 50
    scores["Access Control"] = 70 if a.get("it_support") in ["IT company", "In-house IT team"] else 50
    scores["Vendor Risk"] = 70 if a.get("partners") == "Yes" else 50
    scores["Incident Readiness"] = 80 if a.get("knows_help") == "Yes" else 40
    avg = int(sum(scores.values()) / len(scores))
    return scores, avg

def generate_actions(scores: dict) -> list[dict]:
    actions = []
    for area, val in scores.items():
        if val < 60:
            actions.append({
                "area": area,
                "action": "Improve controls in " + area,
                "why": "This domain shows below-average maturity.",
                "how": "Review related practices and implement improvements."
            })
    return actions

# ---------------------------------------------------
# PDF GENERATOR
# ---------------------------------------------------
class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "SME Cybersecurity Self-Assessment Report", ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_pdf(profile, scores, actions, avg):
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Business Context Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for k, v in profile.items():
        pdf.multi_cell(0, 6, f"{k}: {v}")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Readiness Overview", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, f"Overall Readiness: {avg}/100")
    for k, v in scores.items():
        pdf.multi_cell(0, 6, f"- {k}: {v}/100")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Priority Action Register", ln=True)
    pdf.set_font("Helvetica", "", 11)
    if not actions:
        pdf.multi_cell(0, 6, "No immediate actions required.")
    else:
        for i, a in enumerate(actions, 1):
            pdf.multi_cell(0, 6, f"{i}. {a['area']} — {a['action']}")
            pdf.multi_cell(0, 5, f"Why: {a['why']}")
            pdf.multi_cell(0, 5, f"How: {a['how']}")
            pdf.ln(2)

    return pdf.output(dest="S").encode("latin-1")

# ---------------------------------------------------
# SUMMARY / DASHBOARD
# ---------------------------------------------------
def section_summary():
    a = st.session_state.answers
    st.success("✅ Conversation saved. Here’s your **Business Context**.")

    profile = {k.replace("_", " ").title(): v for k, v in a.items()}
    scores, avg = compute_scores(a)
    actions = generate_actions(scores)

    st.markdown("### 🧾 Business Snapshot")
    for k, v in profile.items():
        st.markdown(f"**{k}:** {v}")

    st.divider()
    st.markdown("### 🧩 Readiness Overview")
    for k, v in scores.items():
        st.markdown(f"**{k}:** {v}/100")
    st.info(f"**Overall Readiness:** {avg}/100")

    st.divider()
    st.markdown("### ✅ Priority Actions")
    if actions:
        for a in actions:
            st.markdown(f"- **{a['area']}** — {a['action']}  \n  _Why:_ {a['why']}  \n  _How:_ {a['how']}")
    else:
        st.success("No critical areas found.")

    st.divider()
    st.markdown("### 📄 Export")
    pdf_bytes = generate_pdf(profile, scores, actions, avg)
    st.download_button(
        "⬇️ Generate PDF Report",
        data=pdf_bytes,
        file_name="SME_Cyber_Assessment_Report.pdf",
        mime="application/pdf"
    )

    cols = st.columns([1, 1, 6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 5
            st.rerun()

# ---------------------------------------------------
# MAIN FLOW
# ---------------------------------------------------
header()
step = st.session_state.step
if step == 1:
    section_1()
elif step == 2:
    section_2()
elif step == 3:
    section_3()
elif step == 4:
    section_4()
elif step == 5:
    section_5()
else:
    section_summary()
