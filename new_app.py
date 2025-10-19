# new_app.py
# ------------------------------------------------------------
# SME Cyber Self-Assessment – Pro
# Conversational business intake  → Summary → Assessment → Results
# Exports a clean PDF report (no external storage required)
# Requires: streamlit==1.37+, fpdf==1.7.2
# ------------------------------------------------------------

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
    "No tech jargon — just what really matters."
)

# =========================
# Session state
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1            # 1..8 (5 intake sections, summary, assessment, results)
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
    # Progress for the intake part only (steps 1..5)
    prog = min(max(st.session_state.step - 1, 0), 5) / 5
    st.progress(prog)

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
# Intake Sections (conversation)
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
# Summary helpers & scoring (intake summary view)
# =========================
def compute_scores_from_intake(a: dict) -> dict:
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

# =========================
# Intake Summary View (Step 6)
# =========================
def section_summary():
    a = st.session_state.answers
    st.success("Conversation saved. Here’s your Business Context.")

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

    scores = compute_scores_from_intake(a)
    avg, label = overall_readiness(scores)

    # Snapshot (left) + KPIs (right)
    st.subheader("Business Snapshot")
    c1, c2 = st.columns([1.3, 1])
    with c1:
        for k, v in profile.items():
            st.markdown(f"**{k}:** {v}")
    with c2:
        st.subheader("Key KPIs")
        st.markdown(f"**Overall readiness (intake):** {avg}/100 ({label})")
        st.markdown(f"**Third-party exposure:** {'Yes' if a.get('partners')=='Yes' else 'No'}")
        st.markdown(f"**Knows who to call:** {profile['Knows who to call']}")

    st.divider()

    st.subheader("Control Health (from intake)")
    for dom, sc in scores.items():
        st.markdown(f"**{dom}:** {sc}/100")
        st.progress(sc/100)

    # PDF export button added later (after assessment code, reusing same generator)
    st.divider()
    st.subheader("Next")
    cols = st.columns([1,1,6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 5
            st.rerun()
    with cols[1]:
        if st.button("Proceed to Cyber Assessment →", type="primary"):
            st.session_state.step = 7
            st.rerun()

# =========================
# Assessment Question Bank (domain → list of Qs)
# =========================
QUESTION_BANK = {
    # 1) Governance & Asset Visibility
    "Governance & Asset Visibility": [
        {"id":"GV01","q":"Do you maintain a written inventory of key systems, devices and SaaS apps?","opts":["Yes","No"]},
        {"id":"GV02","q":"Is there a list of admin/owner accounts for each system?","opts":["Yes","No"]},
        {"id":"GV03","q":"Do you review who has access at least quarterly?","opts":["Yes","No"]},
        {"id":"GV04","q":"Is there a named person responsible for IT/security decisions?","opts":["Me","Named staff","External MSP","No owner"]},
        {"id":"GV05","q":"Do you have basic IT rules/policies (passwords, device use, data handling)?","opts":["Yes","No","In draft"]},
        {"id":"GV06","q":"Do you use a joiner/mover/leaver checklist for accounts?","opts":["Yes","No"]},
    ],

    # 2) Access & Identity
    "Access & Identity": [
        {"id":"AI01","q":"Is MFA enforced for company email accounts?","opts":["Yes","No","Partially"]},
        {"id":"AI02","q":"Is MFA enforced for admin/owner accounts on critical systems?","opts":["Yes","No","Partially"]},
        {"id":"AI03","q":"Do staff use a business-issued password manager?","opts":["Yes","No","Personal","Not sure"]},
        {"id":"AI04","q":"Are shared accounts avoided or tightly controlled and documented?","opts":["Yes","No","N/A"]},
        {"id":"AI05","q":"Do you require unique accounts per person for all systems?","opts":["Yes","No","Partially"]},
        {"id":"AI06","q":"Are default/admin passwords changed on all devices/services?","opts":["Yes","No","N/A"]},
    ],

    # 3) Data Protection & Backup
    "Data Protection & Backup": [
        {"id":"DP01","q":"Do you store customer/employee data (names, emails, invoices, payment refs)?","opts":["Yes","No"]},
        {"id":"DP02","q":"Where are files stored?","opts":["Managed cloud (Google/OneDrive)","Own server","Local only"]},
        {"id":"DP03","q":"Are automated backups enabled at least daily?","opts":["Yes","No","Not needed"]},
        {"id":"DP04","q":"Do you test a restore at least monthly?","opts":["Yes","No"]},
        {"id":"DP05","q":"Are backups versioned / immutable / offsite?","opts":["Yes","No","Not sure"]},
        {"id":"DP06","q":"Do you have a simple data retention approach (keep/delete)?","opts":["Yes","No","In draft"]},
    ],

    # 4) Device Security
    "Device Security": [
        {"id":"DV01","q":"Is full-disk encryption enabled on laptops?","opts":["Yes","No","Some"]},
        {"id":"DV02","q":"Do all devices auto-lock (≤10 min) and require PIN/password/biometric?","opts":["Yes","No","Some"]},
        {"id":"DV03","q":"Are automatic OS and browser updates enabled?","opts":["Yes","No","Some"]},
        {"id":"DV04","q":"Is built-in anti-malware/AV active (e.g., Defender) or EDR deployed?","opts":["Yes","No","Some devices"]},
        {"id":"DV05","q":"Can you wipe a lost/stolen device (MDM/Find My/Intune)?","opts":["Yes","No","Not sure"]},
    ],

    # 5) Email & Collaboration
    "Email & Collaboration": [
        {"id":"EM01","q":"Is a spam/phishing filter active on your email platform?","opts":["Yes","No","Not sure"]},
        {"id":"EM02","q":"Do staff know how to report phishing (button or address)?","opts":["Yes","No","Some"]},
        {"id":"EM03","q":"Is external mail forwarding restricted/monitored?","opts":["Yes","No","Not sure"]},
        {"id":"EM04","q":"Are risky file types warned/blocked (e.g., .exe, macros)?","opts":["Yes","No","Not sure"]},
    ],

    # 6) Network & Remote Access
    "Network & Remote Access": [
        {"id":"NW01","q":"Do staff connect remotely using secured methods (VPN/zero trust)?","opts":["Yes","No","N/A"]},
        {"id":"NW02","q":"Is your router/firewall set to auto-update firmware?","opts":["Yes","No","Not sure","N/A"]},
        {"id":"NW03","q":"Is remote admin (RDP/SSH/panels) closed to the internet or gated by MFA/VPN?","opts":["Yes","No","Not sure"]},
        {"id":"NW04","q":"Is guest Wi-Fi segmented from business devices?","opts":["Yes","No","N/A"]},
    ],

    # 7) Incident Readiness & Logging
    "Incident Readiness & Logging": [
        {"id":"IR01","q":"Do you have a 1-page incident plan (who to call, first steps, backups)?","opts":["Yes","No","In draft"]},
        {"id":"IR02","q":"Are key contacts (IT/MSP/bank/legal) written and accessible offline?","opts":["Yes","No","Partial"]},
        {"id":"IR03","q":"Do you know how to isolate a device during an incident?","opts":["Yes","No","Not sure"]},
        {"id":"IR04","q":"Can you reset all user passwords quickly if needed?","opts":["Yes","No","Not sure"]},
        {"id":"IR05","q":"Do you keep basic logs (sign-ins/admin changes/website errors) ≥30 days?","opts":["Yes","No","Not sure"]},
        {"id":"IR06","q":"Have you done a table-top exercise (talk-through of a fake incident)?","opts":["Yes","No","Planned"]},
    ],

    # 8) People & Training
    "People & Training": [
        {"id":"PT01","q":"Have staff had security awareness in the last 12 months?","opts":["Yes","No","Only onboarding"]},
        {"id":"PT02","q":"Do contractors/temps get the same security guidance?","opts":["Yes","No","N/A"]},
        {"id":"PT03","q":"Do you have a short Acceptable Use / IT rules document?","opts":["Yes","No","In draft"]},
        {"id":"PT04","q":"Are admin/staff roles clear (who can change settings / approve access)?","opts":["Yes","No","Partial"]},
    ],

    # Conditional: Website / Online
    "Website / Online": [
        {"id":"WB01","q":"Is the site/shop always served over HTTPS?","opts":["Yes","No","Not sure"]},
        {"id":"WB02","q":"Are security/plugin updates applied automatically or on a schedule?","opts":["Auto","Scheduled","Manual","Not sure"]},
        {"id":"WB03","q":"Do you have uptime/security alerts configured?","opts":["Yes","No","Not sure"]},
        {"id":"WB04","q":"Are admin logins protected with MFA (CMS/payment gateway)?","opts":["Yes","No","N/A"]},
        {"id":"WB05","q":"You never store card data yourself (use PSPs like Stripe/PayPal only).","opts":["Yes","No","N/A"]},
    ],

    # Conditional: Vendor / Third-Party
    "Vendor / Third-Party": [
        {"id":"VR01","q":"Do you keep a list of key vendors with what data they handle?","opts":["Yes","No","Partial"]},
        {"id":"VR02","q":"Do vendors with access to your data use MFA on their side?","opts":["Yes","No","Unknown"]},
        {"id":"VR03","q":"Do you know the breach/security contact for each key vendor?","opts":["Yes","No","Some"]},
        {"id":"VR04","q":"Do you off-board vendors (remove access, revoke tokens/keys)?","opts":["Yes","No","Not sure"]},
        {"id":"VR05","q":"Are transfers to/from vendors encrypted (SFTP/HTTPS/TLS email)?","opts":["Yes","No","Unknown"]},
    ],
}

def build_assessment_plan(context: dict) -> list[tuple[str, list[dict]]]:
    """Pick relevant domains based on intake answers."""
    plan = [
        ("Governance & Asset Visibility", QUESTION_BANK["Governance & Asset Visibility"]),
        ("Access & Identity", QUESTION_BANK["Access & Identity"]),
        ("Data Protection & Backup", QUESTION_BANK["Data Protection & Backup"]),
        ("Device Security", QUESTION_BANK["Device Security"]),
        ("Email & Collaboration", QUESTION_BANK["Email & Collaboration"]),
        ("Network & Remote Access", QUESTION_BANK["Network & Remote Access"]),
        ("Incident Readiness & Logging", QUESTION_BANK["Incident Readiness & Logging"]),
        ("People & Training", QUESTION_BANK["People & Training"]),
    ]
    if context.get("online_sales","").startswith("Yes") or "Website or webshop" in (context.get("daily_tools") or []):
        plan.append(("Website / Online", QUESTION_BANK["Website / Online"]))
    if context.get("partners") == "Yes":
        plan.append(("Vendor / Third-Party", QUESTION_BANK["Vendor / Third-Party"]))
    return plan

# =========================
# Assessment Scoring
# =========================
YES_VALUES = {"Yes","Me","Named staff","External MSP","Managed cloud (Google/OneDrive)","Own server","Auto","Scheduled"}
IGNORE_VALUES = {"N/A","Not sure","Unknown","Some","Partial","In draft","Planned","Only onboarding"}

def normalize_to_bool(val: str) -> int | None:
    """
    Map option -> 1 (yes), 0 (no), None (ignore).
    Neutral responses don't penalize.
    """
    if val in YES_VALUES:
        return 1
    if val in IGNORE_VALUES:
        return None
    if val in {"Manual", "Local only", "No", "Personal"}:
        return 0
    return None

def domain_score(answers: dict, controls: list[dict]) -> int:
    yes = 0; total = 0
    for c in controls:
        v = answers.get(c["id"])
        b = normalize_to_bool(v) if v is not None else None
        if b is None:
            continue
        total += 1
        if b == 1:
            yes += 1
    return int(100 * yes / total) if total else 0

# =========================
# Assessment UI (Step 7) & Results (Step 8)
# =========================
def section_assessment():
    st.subheader("Cyber Posture Assessment")
    st.caption("Answer the checklist below. N/A and Not sure are ignored for fair scoring.")

    context = st.session_state.answers
    plan = build_assessment_plan(context)

    ac = st.session_state.get("assessment_answers", {})

    for domain, controls in plan:
        with st.expander(domain, expanded=True):
            for c in controls:
                key = c["id"]
                default = ac.get(key)
                ac[key] = st.radio(
                    c["q"],
                    c["opts"],
                    index=(c["opts"].index(default) if default in c["opts"] else (c["opts"].index("No") if "No" in c["opts"] else 0)),
                    key=key
                )

    st.session_state.assessment_answers = ac

    st.divider()
    cols = st.columns([1,1,6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 6
            st.rerun()
    with cols[1]:
        if st.button("Calculate results", type="primary"):
            ds = {dom: domain_score(ac, ctrls) for dom, ctrls in plan}
            st.session_state.domain_scores = ds
            st.session_state.step = 8
            st.rerun()

def section_assessment_results():
    st.subheader("Assessment Results")
    ds = st.session_state.get("domain_scores", {})
    if not ds:
        st.info("No results yet. Please complete the checklist.")
        if st.button("← Back to checklist"):
            st.session_state.step = 7
            st.rerun()
        return

    overall = int(sum(ds.values()) / max(1, len(ds)))
    label = "Strong" if overall >= 75 else "Moderate" if overall >= 50 else "Needs Attention"

    st.markdown(f"**Overall coverage:** {overall}/100 ({label})")
    st.divider()
    st.markdown("#### Domain coverage")
    for k, v in ds.items():
        st.markdown(f"**{k}:** {v}/100")
        st.progress(v/100)

    st.divider()
    cols = st.columns([1,1,6])
    with cols[0]:
        if st.button("← Back"):
            st.session_state.step = 7
            st.rerun()
    with cols[1]:
        if st.button("Finish"):
            st.session_state.step = 6  # back to intake summary
            st.rerun()

# =========================
# PDF utilities (Unicode-safe for FPDF 1.x)
# =========================
def clean_text(x) -> str:
    """Sanitize to latin-1 for FPDF 1.x."""
    if x is None:
        return ""
    s = str(x)
    repl = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-",
        "•": "*", "→": "->",
        "€": "EUR", "…": "...",
        "✅": "", "⚠️": "", "🛡️": "", "📄": "", "🧾": ""
    }
    for k, v in repl.items():
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

def generate_pdf(profile: dict, intake_scores: dict, intake_overall: tuple[int,str],
                 ds: dict | None = None, assessment_overall: tuple[int,str] | None = None) -> bytes:
    """
    Create a concise, text-first PDF.
    If ds/assessment_overall provided, include assessment results as well.
    """
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

    # Intake readiness
    avg_i, label_i = intake_overall
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_text("Readiness Overview (from intake)"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, clean_text(f"Overall (intake): {avg_i}/100 ({label_i})"))
    for k, v in intake_scores.items():
        band = "Strong" if v >= 75 else "Moderate" if v >= 50 else "Weak"
        pdf.multi_cell(0, 6, clean_text(f"- {k}: {v}/100 ({band})"))
    pdf.ln(4)

    # Assessment results (optional)
    if ds is not None and assessment_overall is not None:
        avg_a, label_a = assessment_overall
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, clean_text("Assessment Results"), ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, clean_text(f"Overall (assessment): {avg_a}/100 ({label_a})"))
        for k, v in ds.items():
            band = "Strong" if v >= 75 else "Moderate" if v >= 50 else "Weak"
            pdf.multi_cell(0, 6, clean_text(f"- {k}: {v}/100 ({band})"))

    return pdf.output(dest="S").encode("latin-1", "ignore")

# =========================
# MAIN ROUTER
# =========================
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
elif step == 6:
    # Show summary and export
    section_summary()

    # Offer PDF export (includes intake metrics; also includes assessment if already done)
    a = st.session_state.answers
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
    intake_scores = compute_scores_from_intake(a)
    intake_overall = overall_readiness(intake_scores)

    ds = st.session_state.get("domain_scores")
    assessment_overall = None
    if ds:
        assessment_overall = (
            int(sum(ds.values()) / max(1, len(ds))),
            "Strong" if int(sum(ds.values()) / max(1, len(ds))) >= 75
            else "Moderate" if int(sum(ds.values()) / max(1, len(ds))) >= 50
            else "Needs Attention"
        )

    st.subheader("Export")
    pdf_bytes = generate_pdf(profile, intake_scores, intake_overall, ds, assessment_overall)
    st.download_button(
        "Generate PDF Report",
        data=pdf_bytes,
        file_name="SME_Cyber_Assessment_Report.pdf",
        mime="application/pdf"
    )

elif step == 7:
    section_assessment()
elif step == 8:
    section_assessment_results()
