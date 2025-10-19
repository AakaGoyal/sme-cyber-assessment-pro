# new_app.py
# SME Cyber Risk Self-Assessment — clean build with key fixes
# Stack: Streamlit + FPDF (no DB, no external services)

import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ------------- Page config -------------
st.set_page_config(page_title="SME Cyber Risk Self-Assessment", page_icon="🛡️", layout="centered")

# ------------- Styles -------------
st.markdown("""
<style>
html, body, [class^="css"]  { font-family: Inter, -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
:root { --bg:#0a0a0a; --fg:#ffffff; --muted:#9AA0A6; --accent:#007AFF; }
.block-container { padding-top: 2rem !important; }

.hero { background: #0a0a0a; color: #fff; padding: 72px 36px; border-radius: 20px;
        border: 1px solid #111; box-shadow: 0 10px 30px rgba(0,0,0,.35);}
.hero h1 { font-size: 44px; line-height: 1.06; margin: 0 0 10px; letter-spacing: -0.02em; }
.hero p { font-size: 18px; color: #c8c8c8; margin: 0; }

.step { font-size: 12px; letter-spacing:.14em; color:#9AA0A6; text-transform:uppercase; margin: 6px 0 2px; }
.q { font-size: 22px; font-weight: 700; margin: 4px 0 10px; }

.grid { display:grid; grid-template-columns: repeat(2, minmax(200px,1fr)); gap:12px; margin: 10px 0 12px; }
@media (min-width: 900px) { .grid { grid-template-columns: repeat(4, 1fr);} }

/* Make Streamlit buttons behave like blocks */
.stButton > button {
  width: 100%; height: 80px; border-radius: 16px; border: 1px solid #17191c;
  background: #101214; color: #ECEDEE; font-weight: 600;
}
.stButton > button:hover { transform: translateY(-1px); border-color:#2a2f36; box-shadow:0 6px 16px rgba(0,0,0,.35); }

.nav { display:flex; gap:8px; justify-content: space-between; margin-top: 4px; }
.nav .next, .nav .back {
  border-radius: 999px; padding: 10px 16px; font-weight: 700; border: none;
}
.nav .next { background: #fff; color: #000; }
.nav .back { background: #1b1f24; color: #fff; }

.tiles { display:grid; grid-template-columns: repeat(2, minmax(230px,1fr)); gap:12px; margin-top: 12px; }
@media (min-width: 900px) { .tiles { grid-template-columns: repeat(3, 1fr);} }
.tile { border-radius:16px; padding:16px; color:#0a0a0a; background:#f6f7f8; border:1px solid #e6e6e6; }
.badge { font-weight:700; padding:4px 10px; border-radius:999px; font-size:12px; display:inline-block; }
.badge.red { background:#ffe6ea; color:#b00020; }
.badge.orange { background:#fff0e0; color:#b24a00; }
.badge.yellow { background:#fff9db; color:#8a6d00; }
.badge.green { background:#e8f9ef; color:#0f7a3a; }

.hr { height:1px; background: linear-gradient(90deg, transparent, #1c1f24, transparent); margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ------------- Session state -------------
if "page" not in st.session_state: st.session_state.page = "landing"
if "profile_data" not in st.session_state: st.session_state.profile_data = {}
if "answers" not in st.session_state: st.session_state.answers = {}   # {q_index: score}
if "q_index" not in st.session_state: st.session_state.q_index = 0

# ------------- Domains & Questions -------------
DOMAINS = [
    ("Governance & Risk", "GOV"),
    ("Identity & Access Management", "IAM"),
    ("Data Protection & Privacy", "DPP"),
    ("Network & Infrastructure", "NET"),
    ("Incident Response & Recovery", "IR"),
    ("Awareness & AI Risk", "AIA"),
]

QUESTIONS = [
    # GOV
    ("GOV","Do you have documented security responsibilities?",
        [("No / not sure",1),("Some notes exist",2),("Yes, basic doc",3),("Yes, reviewed annually",4)]),
    ("GOV","Do you assess risks at least annually?",
        [("Never",1),("Informal only",2),("Annual checklist",3),("Formal register + actions",4)]),
    ("GOV","Are suppliers (POS/loyalty/app) risk-checked?",
        [("No",1),("Basic check",2),("Contract clauses",3),("Checklist + review cycle",4)]),
    ("GOV","Joiner/leaver access managed?",
        [("Ad-hoc",2),("Basic",3),("Formal within 24h",4),("Automated",5)]),

    # IAM
    ("IAM","MFA enabled for email/admin tools?",
        [("No",1),("Some staff",3),("All accounts",4),("All + conditional access",5)]),
    ("IAM","Password manager in use?",
        [("No",1),("Optional",2),("Yes, adopted",4),("Yes + SSO",5)]),
    ("IAM","Unique accounts per staff/device?",
        [("Shared accounts",1),("Mixed",2),("Unique",3),("Unique + periodic review",4)]),
    ("IAM","Leaver access removed within 24h?",
        [("Days/weeks",1),("72h",2),("24–48h",3),("Same day",4)]),

    # DPP
    ("DPP","Backups exist & tested?",
        [("None",1),("Ad-hoc",2),("Regular backups",3),("Tested restores",4)]),
    ("DPP","Minimal personal data collected?",
        [("Don’t know",1),("Some minimisation",2),("Yes, defined",3),("Yes + DPIA if needed",4)]),
    ("DPP","Cardholder data stored locally?",
        [("Yes",1),("Unsure",2),("No, processor only",4),("Tokenised controls",5)]),
    ("DPP","Privacy notice & consent on Wi-Fi/loyalty?",
        [("No",1),("Basic",2),("Yes",3),("Yes + reviewed",4)]),

    # NET
    ("NET","Router/POS firmware & patches?",
        [("Rarely",1),("Sometimes",2),("Monthly",3),("Automated/managed",4)]),
    ("NET","Guest Wi-Fi isolated from POS?",
        [("No",1),("Partially",2),("Yes (separate SSID/VLAN)",3),("Yes + ACLs",4)]),
    ("NET","Endpoint protection on devices?",
        [("No",1),("Basic AV",2),("AV + auto updates",3),("EDR + alerts",4)]),
    ("NET","Default creds removed everywhere?",
        [("Not sure",1),("Mostly",2),("Yes",3),("Yes + periodic audit",4)]),

    # IR
    ("IR","Incident playbook exists?",
        [("No",1),("Draft",2),("Yes",3),("Yes + drills",4)]),
    ("IR","Contacts list (bank/IT/processor)?",
        [("No",1),("Partial",2),("Yes",3),("Yes + wallet card",4)]),
    ("IR","Restore test in last 6 months?",
        [("Never",1),("Over a year",2),("Yes",3),("Yes + recorded",4)]),
    ("IR","Phishing/reporting channel defined?",
        [("No",1),("Email to IT",2),("Button/alias",3),("Button + triage SOP",4)]),

    # AIA
    ("AIA","Staff training (incl. AI-aware) frequency?",
        [("Never",1),("Annual",2),("Quarterly micro",3),("Quarterly + role-based",4)]),
    ("AIA","Phishing simulations in last 12m?",
        [("No",1),("Once",2),("Quarterly",3),("Quarterly + targeted",4)]),
    ("AIA","Guidance on deepfakes/voice scams?",
        [("No",1),("Basic tips",2),("Playbook",3),("Playbook + drills",4)]),
    ("AIA","Cashier/shift fraud checks (refunds/cards)?",
        [("No",1),("Some checks",2),("Checklist",3),("Checklist + approvals",4)]),
]

FEEDBACK = {
    "GOV":{"good":"Governance foundations visible.","improve":"Introduce a simple risk register and quarterly access reviews."},
    "IAM":{"good":"MFA and password manager adoption is a strong base.","improve":"Tighten leaver process to same-day removals; extend MFA to all admin apps."},
    "DPP":{"good":"Backups and minimal data collection are in place.","improve":"Test restores twice a year and review Wi-Fi/loyalty privacy notices."},
    "NET":{"good":"Basic segmentation and endpoint controls exist.","improve":"Ensure guest Wi-Fi isolation and monthly patching for router/POS/OS."},
    "IR":{"good":"Contacts and reporting route are mostly defined.","improve":"Create a 1-page incident card and run a 15-minute tabletop drill."},
    "AIA":{"good":"Some awareness exists across staff.","improve":"Add quarterly AI-aware micro-training and one phishing simulation."},
}

# ------------- Helpers -------------
def domain_scores(answer_map: dict):
    """Return average score per domain code."""
    buckets = {code: [] for _, code in DOMAINS}
    for i, (code, _, _) in enumerate(QUESTIONS):
        if i in answer_map:
            buckets[code].append(answer_map[i])
    return {code: (sum(v)/len(v) if v else 0.0) for code, v in buckets.items()}

def label_for(score: float):
    if score < 2: return "red", "🔴 Initial"
    if score < 3: return "orange", "🟠 Developing"
    if score < 4: return "yellow", "🟡 Defined"
    return "green", "🟢 Managed/Optimised"

def export_pdf(profile: dict, scores: dict, overall: float) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Cyber Risk Self-Assessment Report", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Organisation: {profile.get('name','')}", ln=1)
    pdf.cell(0, 8, f"Sector: {profile.get('sector','')}", ln=1)
    pdf.cell(0, 8, f"Employees: {profile.get('staff','')}", ln=1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Overall Maturity: {overall:.2f} / 5", ln=1)
    pdf.ln(2)
    pdf.set_font("Arial", "", 12)
    for title, code in DOMAINS:
        s = scores[code]
        _, tag = label_for(s)
        pdf.cell(0, 7, f"- {title}: {s:.2f}  ({tag})", ln=1)
    pdf.ln(2)
    pdf.set_font("Arial","B",12); pdf.cell(0,8,"Quick Recommendations", ln=1)
    pdf.set_font("Arial","",12)
    for title, code in DOMAINS:
        pdf.multi_cell(0,6, f"{title}: {FEEDBACK[code]['improve']}")
    filename = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# ------------- Screens -------------
def screen_landing():
    st.markdown("""
    <div class="hero">
      <div class="step">SME Cybersecurity</div>
      <h1>Social-engineering risk self-assessment</h1>
      <p>Clean, fast, and human-centred. One question at a time — no clutter, no charts.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("frm_profile"):
        st.write("")  # spacing
        name = st.text_input("Business name", key="pf_name", placeholder="e.g., Café Aurora")
        sector = st.selectbox("Sector", ["Hospitality","Retail","Consulting","Healthcare","Other"], key="pf_sector")
        staff = st.number_input("Employees", min_value=1, max_value=500, value=12, key="pf_staff")
        colA, colB = st.columns(2)
        it_provider = colA.selectbox("External IT provider", ["No","Yes, ad-hoc","Yes, managed"], key="pf_it")
        incident = colB.selectbox("Any incidents in last 12 months?", ["No","Yes (unsure impact)","Yes (reported)"], key="pf_inc")
        submitted = st.form_submit_button("Start Assessment")
    if submitted:
        st.session_state.profile_data = {
            "name": name.strip() if name else "—",
            "sector": sector, "staff": staff,
            "it_provider": it_provider, "incident": incident
        }
        st.session_state.page = "assessment"
        st.session_state.q_index = 0
        st.session_state.answers = {}

def screen_question():
    idx = st.session_state.q_index
    if idx >= len(QUESTIONS):
        st.session_state.page = "results"
        return

    code, qtext, options = QUESTIONS[idx]
    domain_title = next(title for title, c in DOMAINS if c == code)

    st.markdown(f"<div class='step'>{domain_title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='q'>{qtext}</div>", unsafe_allow_html=True)

    # Block-style options (buttons in a grid)
    st.markdown("<div class='grid'>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (label, score) in enumerate(options):
        with cols[i % 4]:
            if st.button(label, key=f"opt_{idx}_{i}", use_container_width=True):
                st.session_state.answers[idx] = score
    st.markdown("</div>", unsafe_allow_html=True)

    # Nav
    colL, colR = st.columns(2)
    if colL.button("← Back", key=f"back_{idx}", use_container_width=True, help="Previous question", disabled=(idx == 0)):
        st.session_state.q_index = max(0, idx - 1)
        st.experimental_rerun()

    if colR.button("Next →", key=f"next_{idx}", use_container_width=True, help="Next question"):
        if idx not in st.session_state.answers:
            st.warning("Please select an option to continue.")
        else:
            st.session_state.q_index = idx + 1
            st.experimental_rerun()

def screen_results():
    scores = domain_scores(st.session_state.answers)
    overall = sum(scores.values()) / len(DOMAINS)

    st.markdown("## Results")
    st.caption("Traffic-light tiles — concise and readable.")
    st.markdown("<div class='tiles'>", unsafe_allow_html=True)
    for title, code in DOMAINS:
        s = scores[code]
        color, tag = label_for(s)
        st.markdown(
            f"<div class='tile'><div class='badge {color}'>{tag}</div>"
            f"<div style='height:8px'></div>"
            f"<div style='font-weight:700; font-size:18px'>{title}</div>"
            f"<div style='color:#4a4f55; margin-top:6px'>Score: {s:.2f} / 5</div>"
            f"</div>", unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader(f"Overall maturity: {overall:.2f} / 5")

    st.markdown("### What you're doing well")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['good']}")

    st.markdown("### What to improve next")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['improve']}")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    if st.button("📄 Export PDF report", key="export_pdf"):
        filename = export_pdf(st.session_state.profile_data, scores, overall)
        with open(filename, "rb") as f:
            st.download_button("Download report", f, file_name=filename, mime="application/pdf")

    if st.button("↺ Restart", key="restart"):
        st.session_state.page = "landing"
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.experimental_rerun()

# ------------- Router -------------
if st.session_state.page == "landing":
    screen_landing()
elif st.session_state.page == "assessment":
    screen_question()
elif st.session_state.page == "results":
    screen_results()
