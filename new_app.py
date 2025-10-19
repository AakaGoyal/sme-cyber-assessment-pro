import streamlit as st
import pandas as pd
from datetime import datetime

from fpdf import FPDF
import io

class ReportPDF(FPDF):
    def header(self):
        # Optional header with title
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "SME Cybersecurity Self-Assessment Report", ln=True, align="C")
        self.ln(4)

    def footer(self):
        # Add page numbers
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_pdf(profile: dict, scores: dict, actions: list[dict], overall: tuple[int, str]) -> bytes:
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Section 1: Summary ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Business Context Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
    pdf.ln(4)

    for k, v in profile.items():
        pdf.multi_cell(0, 6, f"{k}: {v}")
    pdf.ln(6)

    # --- Section 2: Readiness Overview ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Readiness Overview", ln=True)
    pdf.set_font("Helvetica", "", 11)
    avg, label = overall
    pdf.multi_cell(0, 6, f"Overall Readiness: {avg}/100 ({label})")
    pdf.ln(2)
    for k, v in scores.items():
        pdf.multi_cell(0, 6, f"- {k}: {v}/100 ({'Strong' if v>=75 else 'Moderate' if v>=50 else 'Weak'})")
    pdf.ln(6)

    # --- Section 3: Action Register ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Priority Action Register", ln=True)
    pdf.set_font("Helvetica", "", 11)
    if not actions:
        pdf.multi_cell(0, 6, "No immediate high-priority actions identified.")
    else:
        for i, a in enumerate(actions, 1):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, f"{i}. {a['area']} — {a['action']}")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, f"Why: {a['why']}")
            pdf.multi_cell(0, 5, f"How: {a['how']}")
            pdf.ln(2)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Next Steps & Notes", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6,
        "This report summarises the current business context and cybersecurity posture.\n"
        "Recommended next steps:\n"
        "  • Address the Priority 1 actions first (within 2 weeks).\n"
        "  • Reassess quarterly or after major IT/partner changes.\n"
        "  • Train staff on phishing and password management.\n"
        "  • Review vendor security agreements yearly."
    )

    # Convert to bytes
    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    return pdf_bytes.getvalue()


# ---------- Page setup ----------
st.set_page_config(
    page_title="SME Cyber Self-Assessment – Pro",
    page_icon="🛡️",
    layout="wide"
)

TITLE = "SME Cyber Self-Assessment – Pro"
SUBTITLE = "Before we talk about cybersecurity, let’s get to know your business a little better. No tech jargon—just what really matters."

# ---------- Session state ----------
if "step" not in st.session_state:
    st.session_state.step = 1  # 1..6 (5 sections + summary)
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "started_at" not in st.session_state:
    st.session_state.started_at = datetime.utcnow().isoformat(timespec="seconds")

def save(k, v):
    st.session_state.answers[k] = v

# ---------- Helper UI ----------
def header():
    st.title(TITLE)
    st.caption("A separate deployment from your core SME app")
    st.markdown(f"### Getting to Know Your Business")
    st.write(SUBTITLE)
    st.progress((st.session_state.step-1)/5)

def nav(prev=True, next=True, validate_ok=True):
    cols = st.columns([1,1,6])
    with cols[0]:
        if prev and st.button("← Back"):
            st.session_state.step = max(1, st.session_state.step - 1)
            st.rerun()
    with cols[1]:
        if next and st.button("Next →", type="primary", disabled=not validate_ok):
            st.session_state.step = min(6, st.session_state.step + 1)
            st.rerun()

# ---------- Sections ----------
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

    required = ["business_type","years_in_business","team_size","business_mode","turnover"]
    ok = all(st.session_state.answers.get(k) not in [None, "", []] for k in required)
    nav(prev=False, next=True, validate_ok=ok)

def section_2():
    st.markdown("#### 💻 How You Use Technology")

    save("online_sales", st.radio(
        "Do you sell or deliver services online?",
        ["Yes – through my own website", "Yes – through marketplaces (e.g., Etsy, Amazon)", "No – it’s mostly offline"],
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
         "Cloud storage (Google Drive, OneDrive, etc.)",
         "Online payment system", "Website or webshop"]
    ))

    save("website_manager", st.radio(
        "Who looks after your website and online systems?",
        ["I do it myself", "Someone on my team", "An external company or freelancer"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["online_sales","stores_data","website_manager"])
    nav(prev=True, next=True, validate_ok=ok)

def section_3():
    st.markdown("#### 🧰 Who Manages Your IT and Accounts")

    save("it_support", st.radio(
        "Who takes care of your computers, emails, and systems when something breaks or needs setting up?",
        ["I do", "A friend/freelancer", "An IT company", "In-house IT team"],
        index=None
    ))

    save("system_setup", st.radio(
        "Did you personally set up your main systems and accounts (email, website, backups)?",
        ["Yes, mostly me", "Shared effort", "Someone else handled it"],
        index=None
    ))

    save("asset_list", st.radio(
        "Do you have a clear list of what systems, accounts, and devices your business uses?",
        ["Yes, written down or documented", "I have a rough idea", "Not really"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["it_support","system_setup","asset_list"])
    nav(prev=True, next=True, validate_ok=ok)

def section_4():
    st.markdown("#### 🤝 Partners and Ecosystem")

    save("partners", st.radio(
        "Do you work with external partners who handle your data or systems (web host, accountant, logistics, marketing tools)?",
        ["Yes", "No"],
        index=None
    ))

    save("num_partners", st.radio(
        "Roughly how many key partners or service providers do you rely on?",
        ["0–2", "3–5", "6+"],
        index=None
    ))

    save("breach_response", st.radio(
        "If one of them had a data breach, would you know what to do or who to contact?",
        ["Yes, I know who to reach", "Not really sure"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["partners","num_partners","breach_response"])
    nav(prev=True, next=True, validate_ok=ok)

def section_5():
    st.markdown("#### 🧭 Confidence & Experience")

    save("preparedness", st.radio(
        "If your business was hit by a cyberattack or data loss tomorrow, how prepared would you feel?",
        ["Not at all", "Somewhat", "Fairly confident", "Very confident"],
        index=None
    ))

    save("past_incident", st.radio(
        "Have you ever experienced a cybersecurity issue before (phishing, data loss, locked computer)?",
        ["Yes", "No", "Not sure"],
        index=None
    ))

    save("knows_help", st.radio(
        "Do you know who to call or where to get help if something like that happened?",
        ["Yes", "No"],
        index=None
    ))

    ok = all(st.session_state.answers.get(k) not in [None, ""] for k in ["preparedness","past_incident","knows_help"])
    nav(prev=True, next=True, validate_ok=ok)

# ---------- Summary / Context Profile ----------
def derive_context(a: dict) -> dict:
    """Create a concise profile for the next stage."""
    profile = {
        "Type": a.get("business_type") or "—",
        "Size": a.get("team_size") or "—",
        "Mode": a.get("business_mode") or "—",
        "Years": a.get("years_in_business") or "—",
        "Turnover": a.get("turnover") or "—",
        "Digital setup": f"{a.get('website_manager','—')}; tools: {', '.join(a.get('daily_tools', [])) or '—'}",
        "Data handled": a.get("stores_data") or "—",
        "Online sales": a.get("online_sales") or "—",
        "IT ownership": f"{a.get('it_support','—')}; setup: {a.get('system_setup','—')}",
        "Asset inventory": a.get("asset_list") or "—",
        "Partners": f"{a.get('partners','—')} ({a.get('num_partners','—')})",
        "Third-party breach plan": a.get("breach_response") or "—",
        "Confidence": a.get("preparedness") or "—",
        "Past incident": a.get("past_incident") or "—",
        "Knows where to get help": a.get("knows_help") or "—",
    }
    return profile

def section_summary():
    st.success("✅ Conversation saved. Here’s your **Business Context**.")
    a = st.session_state.answers
    profile = derive_context(a)

    # Nicely formatted profile
    st.markdown("### 🧾 Business Snapshot")
    cols = st.columns(2)
    keys = list(profile.keys())
    left_keys, right_keys = keys[:len(keys)//2], keys[len(keys)//2:]
    with cols[0]:
        for k in left_keys:
            st.markdown(f"**{k}:** {profile[k]}")
    with cols[1]:
        for k in right_keys:
            st.markdown(f"**{k}:** {profile[k]}")

    st.divider()
    st.markdown("### 🎯 Suggested Next Step")
    st.info(
        "Start the cybersecurity self-assessment tailored for your context. "
        "We’ll focus on practical controls first (backups, MFA, device protection, awareness, vendor risk)."
    )

    # Download
    export = {
        "meta_started_at": st.session_state.started_at,
        "meta_completed_at": datetime.utcnow().isoformat(timespec="seconds"),
        **a
    }
    df = pd.DataFrame([export])
    st.download_button(
        "⬇️ Download Conversation Summary (CSV)",
        data=df.to_csv(index=False),
        file_name="business_context_summary.csv",
        mime="text/csv"
    )

    # Nav
    cols = st.columns([1,1,6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 5
            st.experimental_rerun()
    with cols[1]:
        st.button("Proceed to Cyber Assessment →", type="primary", disabled=True)  # placeholder

# ---------- Render ----------
header()
step = st.session_state.step
with st.container():
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

