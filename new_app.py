import streamlit as st
from datetime import datetime
from fpdf import FPDF

# =========================
# Page setup
# =========================
st.set_page_config(
    page_title="SME Cyber Self-Assessment – Pro",
    page_icon="🛡️",
    layout="wide"
)

APP_TITLE = "SME Cyber Self-Assessment – Pro"
APP_SUBTITLE = (
    "Before we talk about cybersecurity, let’s get to know your business a little better. "
    "No tech jargon—just what really matters."
)

# =========================
# Session state
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1            # 1..6 (5 sections + summary)
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "started_at" not in st.session_state:
    st.session_state.started_at = datetime.utcnow().isoformat(timespec="seconds")

def save(k, v):
    st.session_state.answers[k] = v

# =========================
# Header & navigation
# =========================
def header():
    st.title(APP_TITLE)
    st.caption("A separate deployment from your core SME app")
    st.markdown("### Getting to Know Your Business")
    st.write(APP_SUBTITLE)
    st.progress((st.session_state.step - 1) / 5)

def nav(prev=True, nxt=True, validate_ok=True):
    cols = st.columns([1, 1, 6])
    with cols[0]:
        if prev and st.button("← Back"):
            st.session_state.step = max(1, st.session_state.step - 1)
            st.rerun()
    with cols[1]:
        if nxt and st.button("Next →", type="primary", disabled=not validate_ok):
            st.session_state.step = min(6, st.session_state.step + 1)
            st.rerun()

# =========================
# Sections (conversation)
# =========================
def section_1():
    st.markdown("#### Your Business at a Glance")

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
        ["Under EUR 100k", "EUR 100k–500k", "EUR 500k–2M", "Over EUR 2M"],
        index=None
    ))

    required = ["business_type", "years_in_business", "team_size", "business_mode", "turnover"]
    ok = all(st.session_state.answers.get(k) not in [None, "", []] for k in required)
    nav(prev=False, nxt=True, validate_ok=ok)

def section_2():
    st.markdown("#### How You Use Technology")

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
    nav(prev=True, nxt=True, validate_ok=ok)

def section_3():
    st.markdown("#### Who Manages Your IT and Accounts")

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
    nav(prev=True, nxt=True, validate_ok=ok)

def section_4():
    st.markdown("#### Partners and Ecosystem")

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
    nav(prev=True, nxt=True, validate_ok=ok)

def section_5():
    st.markdown("#### Confidence & Experience")

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
    nav(prev=True, nxt=True, validate_ok=ok)

# =========================
# Scoring & actions
# =========================
def compute_scores(a: dict) -> dict:
    scores = {}

    # Governance & Visibility
    scores["Governance & Visibility"] = (
        85 if a.get("asset_list") == "Yes, documented"
        else 60 if a.get("asset_list") == "Rough idea"
        else 35
    )

    # Data Protection
    holds_data = a.get("stores_data") == "Yes"
    uses_cloud = "Cloud storage" in (a.get("daily_tools") or [])
    scores["Data Protection"] = 80 if holds_data and uses_cloud else 55 if holds_data else 45

    # Access Control
    pro_it = a.get("it_support") in ["IT company", "In-house IT team"]
    scores["Access Control"] = 75 if pro_it else 55

    # Vendor Risk
    has_partners = a.get("partners") == "Yes"
    scores["Vendor Risk"] = 70 if has_partners else 50

    # Incident Readiness
    knows_help = a.get("knows_help") == "Yes"
    confident = a.get("preparedness") in ["Fairly confident", "Very confident"]
    scores["Incident Readiness"] = 80 if knows_help and confident else 60 if knows_help else 40

    return scores

def overall_readiness(scores: dict) -> tuple[int, str]:
    avg = int(sum(scores.values()) / max(1, len(scores)))
    label = "Strong" if avg >= 75 else "Moderate" if avg >= 50 else "Needs Attention"
    return avg, label

def generate_actions(a: dict, scores: dict) -> list[dict]:
    actions = []

    if scores["Governance & Visibility"] < 70:
        actions.append({
            "area": "Governance & Visibility",
            "action": "Create a simple asset & account inventory",
            "why": "Know what to protect and who has access.",
            "how": "List devices, cloud apps, admin emails, and owners; review quarterly."
        })
    if scores["Data Protection"] < 70 or a.get("stores_data") == "Yes":
        actions.append({
            "area": "Data Protection",
            "action": "Enable automated cloud backups + monthly restore test",
            "why": "Backups that restore are critical against ransomware and mistakes.",
            "how": "Use versioned backups (e.g., OneDrive/Google Drive/Backblaze) and test on a spare device."
        })
    if scores["Access Control"] < 70:
        actions.append({
            "area": "Access Control",
            "action": "Enforce MFA for email/admin and deploy a password manager",
            "why": "Stops most account-takeover attacks.",
            "how": "Turn on MFA in Microsoft/Google; use Bitwarden/1Password for the team."
        })
    if scores["Vendor Risk"] < 70 and a.get("partners") == "Yes":
        actions.append({
            "area": "Vendor Risk",
            "action": "Maintain a vendor list with incident contact",
            "why": "Respond faster if partners are compromised.",
            "how": "Track vendor, service, data shared, and breach contact; review yearly."
        })
    if scores["Incident Readiness"] < 70:
        actions.append({
            "area": "Incident Readiness",
            "action": "Create a 1-page incident plan and contact tree",
            "why": "Reduces downtime and panic during incidents.",
            "how": "Define who to call, steps to isolate devices, and where backups are."
        })

    # Prioritize by lowest domain scores
    actions.sort(key=lambda x: scores.get(x["area"], 0))
    return actions[:5]

# =========================
# PDF utilities (Unicode-safe for FPDF 1.x)
# =========================
def clean_text(x) -> str:
    """Sanitize to latin-1 for FPDF 1.x."""
    if x is None:
        return ""
    s = str(x)
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-",
        "•": "*", "→": "->",
        "€": "EUR", "…": "...",
        "✅": "", "⚠️": "", "🛡️": "", "📄": "", "🧾": ""
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, clean_text("SME Cybersecurity Self-Assessment Report"), ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_pdf(profile: dict, scores: dict, actions: list[dict], overall: tuple[int, str]) -> bytes:
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, clean_text("Business Context Summary"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, clean_text(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"), ln=True)
    pdf.ln(2)
    for k, v in profile.items():
        pdf.multi_cell(0, 6, clean_text(f"{k}: {v}"))
    pdf.ln(4)

    # Readiness
    avg, label = overall
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Readiness Overview"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, clean_text(f"Overall Readiness: {avg}/100 ({label})"))
    for k, v in scores.items():
        band = "Strong" if v >= 75 else "Moderate" if v >= 50 else "Weak"
        pdf.multi_cell(0, 6, clean_text(f"- {k}: {v}/100 ({band})"))
    pdf.ln(4)

    # Actions
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Priority Action Register"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    if not actions:
        pdf.multi_cell(0, 6, clean_text("No immediate high-priority actions identified."))
    else:
        for i, a in enumerate(actions, 1):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, clean_text(f"{i}. {a['area']} — {a['action']}"))
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, clean_text(f"Why: {a['why']}"))
            pdf.multi_cell(0, 5, clean_text(f"How: {a['how']}"))
            pdf.ln(1)

    # Return bytes (latin-1 safe)
    return pdf.output(dest="S").encode("latin-1", "ignore")

# =========================
# Summary / dashboard
# =========================
def section_summary():
    a = st.session_state.answers
    st.success("Conversation saved. Here’s your Business Context.")

    # Profile (make lists readable)
    profile = {
        "Type": a.get("business_type", "—"),
        "Size": a.get("team_size", "—"),
        "Mode": a.get("business_mode", "—"),
        "Years": a.get("years_in_business", "—"),
        "Turnover": a.get("turnover", "—"),
        "Online sales": a.get("online_sales", "—"),
        "Data handled": a.get("stores_data", "—"),
        "Digital tools": ", ".join(a.get("daily_tools", [])) or "—",
        "Website ownership": a.get("website_manager", "—"),
        "IT support": a.get("it_support", "—"),
        "System setup": a.get("system_setup", "—"),
        "Asset inventory": a.get("asset_list", "—"),
        "Partners": a.get("partners", "—"),
        "Partner count": a.get("num_partners", "—"),
        "Third-party breach plan": a.get("breach_response", "—"),
        "Confidence": a.get("preparedness", "—"),
        "Past incident": a.get("past_incident", "—"),
        "Knows who to call": a.get("knows_help", "—"),
    }

    scores = compute_scores(a)
    avg, label = overall_readiness(scores)
    actions = generate_actions(a, scores)

    # Snapshot (left) + KPIs (right)
    st.subheader("Business Snapshot")
    c1, c2 = st.columns([1.3, 1])
    with c1:
        for k, v in profile.items():
            st.markdown(f"**{k}:** {v}")
    with c2:
        st.subheader("Key KPIs")
        st.markdown(f"**Overall readiness:** {avg}/100 ({label})")
        st.markdown(f"**Third-party exposure:** {'Yes' if a.get('partners')=='Yes' else 'No'}")
        st.markdown(f"**Knows who to call:** {profile['Knows who to call']}")

    st.divider()

    st.subheader("Control Health (by domain)")
    for dom, sc in scores.items():
        st.markdown(f"**{dom}:** {sc}/100")
        st.progress(sc/100)

    st.divider()

    st.subheader("Priority Action Register")
    if actions:
        for i, it in enumerate(actions, 1):
            st.markdown(
                f"**{i}. {it['area']} — {it['action']}**  \n"
                f"*Why:* {it['why']}  \n"
                f"*How:* {it['how']}"
            )
            st.write("")
    else:
        st.success("No immediate high-priority actions identified.")

    st.divider()
    st.subheader("Export")
    pdf_bytes = generate_pdf(profile, scores, actions, (avg, label))
    st.download_button(
        "Generate PDF Report",
        data=pdf_bytes,
        file_name="SME_Cyber_Assessment_Report.pdf",
        mime="application/pdf"
    )

    cols = st.columns([1, 1, 6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 5
            st.rerun()

# =========================
# Main flow
# =========================
header()
if st.session_state.step == 1:
    section_1()
elif st.session_state.step == 2:
    section_2()
elif st.session_state.step == 3:
    section_3()
elif st.session_state.step == 4:
    section_4()
elif st.session_state.step == 5:
    section_5()
else:
    section_summary()
