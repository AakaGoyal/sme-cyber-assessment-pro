import streamlit as st
from fpdf import FPDF
from datetime import datetime

# ---------- Page config ----------
st.set_page_config(page_title="SME Cyber Risk Self-Assessment", page_icon="🛡️", layout="centered")

# ---------- Styles ----------
CUSTOM_CSS = """
<style>
/* Base */
html, body, [class^="css"]  { font-family: Inter, -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
:root { --bg:#0a0a0a; --fg:#ffffff; --muted:#9AA0A6; --accent:#17C964; --accent2:#007AFF; --danger:#F31260; --warn:#FFB300; --amber:#FF7A00; }

.block-container { padding-top: 2rem !important; }

/* Landing */
.hero { background: var(--bg); color: var(--fg); padding: 72px 36px; border-radius: 20px;
        border: 1px solid #111; box-shadow: 0 10px 30px rgba(0,0,0,.35);}
.hero h1 { font-size: 48px; line-height: 1.05; margin: 0 0 12px; letter-spacing: -0.02em; }
.hero p { font-size: 18px; color: #c8c8c8; margin: 0 0 24px; }

/* Step header */
.step { font-size: 14px; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; margin: 8px 0 6px; }

/* Cards grid */
.card-grid { display: grid; grid-template-columns: repeat(2, minmax(200px, 1fr)); gap: 12px; margin: 12px 0 6px; }
@media (min-width: 900px) { .card-grid { grid-template-columns: repeat(4, 1fr);} }

.card {
  background: #101214; color: #ECEDEE; border: 1px solid #17191c; border-radius: 16px; padding: 18px 16px;
  min-height: 88px; display: flex; align-items: center; justify-content: center; text-align: center;
  transition: .18s ease; cursor: pointer; user-select: none;
}
.card:hover { transform: translateY(-2px); border-color: #2a2f36; box-shadow: 0 8px 20px rgba(0,0,0,.35); }
.card.selected { outline: 2px solid var(--accent2); box-shadow: 0 0 0 4px rgba(0,122,255,.12); }

/* Next button (Framer-style) */
.next-wrap { display:flex; align-items:center; justify-content:flex-end; margin-top: 10px; }
.next {
  background: var(--fg); color: #000; border: none; border-radius: 999px; padding: 12px 18px; font-weight: 600;
  display:inline-flex; align-items:center; gap:10px; cursor:pointer; transition:.18s;
}
.next:hover { transform: translateX(2px); }
.next .arrow { width: 22px; height:22px; border-radius:50%; background:#000; color:#fff; display:grid; place-items:center; }

/* Result tiles */
.tiles { display:grid; grid-template-columns: repeat(2, minmax(220px,1fr)); gap:12px; }
@media (min-width: 900px) { .tiles { grid-template-columns: repeat(3, 1fr);} }
.tile { border-radius:16px; padding:16px; color:#0a0a0a; background:#f5f5f5; border:1px solid #e6e6e6; }
.badge { font-weight:700; padding:4px 10px; border-radius:999px; font-size:12px; display:inline-block; }
.badge.red { background:#ffe6ea; color:#b00020; }
.badge.orange { background:#fff0e0; color:#b24a00; }
.badge.yellow { background:#fff9db; color:#8a6d00; }
.badge.green { background:#e8f9ef; color:#0f7a3a; }

/* Subtle divider */
.hr { height:1px; background: linear-gradient(90deg, transparent, #1c1f24, transparent); margin: 18px 0; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- Session state ----------
if "page" not in st.session_state: st.session_state.page = "landing"
if "profile" not in st.session_state: st.session_state.profile = {}
if "answers" not in st.session_state: st.session_state.answers = {}
if "q_index" not in st.session_state: st.session_state.q_index = 0

# ---------- Questionnaire (one question per screen, 6 domains, 4 Qs each) ----------
DOMAINS = [
    ("Governance & Risk", "GOV"),
    ("Identity & Access Management", "IAM"),
    ("Data Protection & Privacy", "DPP"),
    ("Network & Infrastructure", "NET"),
    ("Incident Response & Recovery", "IR"),
    ("Awareness & AI Risk", "AIA"),
]

QUESTIONS = [
    # domain_code, question, [(label, score)]
    ("GOV", "Do you have documented security responsibilities?", [("No / not sure",1),("Some notes exist",2),("Yes, basic doc",3),("Yes, reviewed annually",4)]),
    ("GOV", "Do you assess risks at least annually?", [("Never",1),("Informal only",2),("Annual checklist",3),("Formal register+actions",4)]),
    ("GOV", "Are suppliers (POS/loyalty/app) risk-checked?", [("No",1),("Basic check",2),("Contract clauses",3),("Checklist + review cycle",4)]),
    ("GOV", "Joiner/leaver access managed?", [("Ad-hoc",2),("Basic",3),("Formal within 24h",4),("Automated",5)]),

    ("IAM", "MFA enabled for email/admin tools?", [("No",1),("Some staff",3),("All accounts",4),("All + conditional access",5)]),
    ("IAM", "Password manager in use?", [("No",1),("Optional",2),("Yes, adopted",4),("Yes + SSO",5)]),
    ("IAM", "Unique accounts per staff/device?", [("Shared accounts",1),("Mixed",2),("Unique",3),("Unique + periodic review",4)]),
    ("IAM", "Leaver access removed within 24h?", [("Days/weeks",1),("72h",2),("24–48h",3),("Same day",4)]),

    ("DPP", "Backups exist & tested?", [("None",1),("Ad-hoc",2),("Regular backups",3),("Tested restores",4)]),
    ("DPP", "Minimal personal data collected?", [("Don’t know",1),("Some minimisation",2),("Yes, defined",3),("Yes + DPIA if needed",4)]),
    ("DPP", "Cardholder data stored locally?", [("Yes",1),("Unsure",2),("No, processor only",4),("Tokenised controls",5)]),
    ("DPP", "Privacy notice & consent on Wi-Fi/loyalty?", [("No",1),("Basic",2),("Yes",3),("Yes + reviewed",4)]),

    ("NET", "Router/POS firmware & patches?", [("Rarely",1),("Sometimes",2),("Monthly",3),("Automated/managed",4)]),
    ("NET", "Guest Wi-Fi isolated from POS?", [("No",1),("Partially",2),("Yes (separate SSID/VLAN)",3),("Yes + ACLs",4)]),
    ("NET", "Endpoint protection (AV/EDR) present?", [("No",1),("Basic AV",2),("AV + auto updates",3),("EDR + alerts",4)]),
    ("NET", "Default creds removed everywhere?", [("Not sure",1),("Mostly",2),("Yes",3),("Yes + periodic audit",4)]),

    ("IR", "Incident playbook exists?", [("No",1),("Draft",2),("Yes",3),("Yes + drills",4)]),
    ("IR", "Contacts list (bank/IT/processor)?", [("No",1),("Partial",2),("Yes",3),("Yes + wallet card",4)]),
    ("IR", "Restore test in last 6 months?", [("Never",1),("Over a year",2),("Yes",3),("Yes + recorded",4)]),
    ("IR", "Phishing/reporting channel defined?", [("No",1),("Email to IT",2),("Button/alias",3),("Button + triage SOP",4)]),

    ("AIA", "Staff training (incl. AI-aware) frequency?", [("Never",1),("Annual",2),("Quarterly micro",3),("Quarterly + role-based",4)]),
    ("AIA", "Phishing simulations in last 12m?", [("No",1),("Once",2),("Quarterly",3),("Quarterly + targeted",4)]),
    ("AIA", "Guidance on deepfakes/voice scams?", [("No",1),("Basic tips",2),("Playbook",3),("Playbook + drills",4)]),
    ("AIA", "Cashier/shift fraud checks (refunds/cards)?", [("No",1),("Some checks",2),("Checklist",3),("Checklist + approvals",4)]),
]

FEEDBACK = {
    "GOV": {
        "good": "Governance foundations visible. Keep documenting responsibilities and supplier checks.",
        "improve": "Introduce a simple risk register and quarterly access reviews."
    },
    "IAM": {
        "good": "MFA and password manager adoption is a strong base.",
        "improve": "Tighten leaver process to same-day removals; extend MFA to all admin apps."
    },
    "DPP": {
        "good": "Backups and minimal data collection are in place.",
        "improve": "Test restores twice a year and review Wi-Fi/loyalty privacy notices."
    },
    "NET": {
        "good": "Basic segmentation and endpoint controls exist.",
        "improve": "Ensure guest Wi-Fi isolation and monthly patching for router/POS/OS."
    },
    "IR": {
        "good": "Contacts and reporting route are mostly defined.",
        "improve": "Create a 1-page incident card and run a 15-minute tabletop drill."
    },
    "AIA": {
        "good": "Some awareness exists across staff.",
        "improve": "Add quarterly AI-aware micro-training and one phishing simulation."
    }
}

# ---------- Helpers ----------
def domain_scores(answers):
    scores = {code: [] for _, code in DOMAINS}
    for i, q in enumerate(QUESTIONS):
        code, _, options = q
        if i in answers:
            scores[code].append(answers[i])
    return {d: (sum(vals)/len(vals) if vals else 0) for d, vals in scores.items()}

def label_for(score):
    if score < 2: return "red", "🔴 Initial"
    if score < 3: return "orange", "🟠 Developing"
    if score < 4: return "yellow", "🟡 Defined"
    return "green", "🟢 Managed/Optimised"

def next_question_index(idx):
    return min(idx + 1, len(QUESTIONS))

def prev_question_index(idx):
    return max(idx - 1, 0)

def export_pdf(profile, scores, overall):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Cyber Risk Self-Assessment Report", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Organisation: {profile.get('name','')}", ln=1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Overall Maturity: {overall:.2f}/5", ln=1)
    pdf.ln(2)
    pdf.set_font("Arial", "", 12)
    for title, code in DOMAINS:
        s = scores[code]
        _, tag = label_for(s)
        pdf.cell(0, 7, f"- {title}: {s:.2f}  ({tag})", ln=1)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12); pdf.cell(0,8,"Quick Recommendations", ln=1)
    pdf.set_font("Arial","",12)
    for title, code in DOMAINS:
        pdf.multi_cell(0,6, f"{title} – {FEEDBACK[code]['improve']}")
    filename = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# ---------- UI Components ----------
def hero():
    st.markdown(
        f"""
        <div class="hero">
          <div class="step">SME Cybersecurity</div>
          <h1>Social-engineering risk self-assessment</h1>
          <p>Clean, fast, and human-centred. One question at a time — no clutter, no charts.</p>
        </div>
        """, unsafe_allow_html=True
    )
    with st.form("profile"):
        st.write("")
        name = st.text_input("Business name", placeholder="e.g., Café Aurora")
        sector = st.selectbox("Sector", ["Hospitality", "Retail", "Consulting", "Healthcare", "Other"])
        staff = st.number_input("Employees", 1, 500, 12)
        colA, colB = st.columns(2)
        it_provider = colA.selectbox("External IT provider", ["No", "Yes, ad-hoc", "Yes, managed"])
        prior_incident = colB.selectbox("Any suspicious incidents in the last 12m?", ["No", "Yes (unsure impact)", "Yes (reported)"])
        submitted = st.form_submit_button("Start Assessment")
    if submitted:
        st.session_state.profile = {
            "name": name, "sector": sector, "staff": staff,
            "it": it_provider, "incident": prior_incident
        }
        st.session_state.page = "assessment"

def question_screen():
    idx = st.session_state.q_index
    if idx >= len(QUESTIONS):
        st.session_state.page = "results"
        return

    code, qtext, options = QUESTIONS[idx]
    domain_name = [d for d in DOMAINS if d[1] == code][0][0]

    st.markdown(f"<div class='step'>{domain_name}</div>", unsafe_allow_html=True)
    st.markdown(f"### {qtext}")

    # Render options as cards
    cols = st.container()
    cols.markdown("<div class='card-grid'>", unsafe_allow_html=True)
    selected_idx = None
    for opt_i, (label, score) in enumerate(options):
        is_selected = (st.session_state.answers.get(idx, None) == score)
        selected_class = " selected" if is_selected else ""
        if st.button(label, key=f"q{idx}_opt{opt_i}", help=str(score)):
            st.session_state.answers[idx] = score
            selected_idx = opt_i
        # Mark selection visually by re-rendering HTML
        cols.markdown(f"<div class='card{selected_class}'>{label}</div>", unsafe_allow_html=True)
    cols.markdown("</div>", unsafe_allow_html=True)

    # Nav
    left, right = st.columns([1,1])
    if left.button("← Back", disabled=(idx==0)):
        st.session_state.q_index = prev_question_index(idx)
        st.experimental_rerun()

    st.markdown("<div class='next-wrap'>", unsafe_allow_html=True)
    if st.button("Next  ", key=f"next_{idx}", help="Go to next question"):
        st.session_state.q_index = next_question_index(idx)
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def results_screen():
    scores = domain_scores(st.session_state.answers)
    overall = sum(scores.values()) / len(DOMAINS)

    st.markdown("## Results")
    st.caption("Traffic-light tiles — no charts.")
    st.markdown("<div class='tiles'>", unsafe_allow_html=True)
    for title, code in DOMAINS:
        s = scores[code]
        color, tag = label_for(s)
        st.markdown(
            f"<div class='tile'><div class='badge {color}'>{tag}</div><div style='height:8px'></div>"
            f"<div style='font-weight:700; font-size:18px'>{title}</div>"
            f"<div style='color:#4a4f55; margin-top:6px'>Score: {s:.2f} / 5</div>"
            f"</div>", unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader(f"Overall maturity: {overall:.2f} / 5")

    # Feedback
    st.markdown("### What you're doing well")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['good']}")

    st.markdown("### What to improve next")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['improve']}")

    # Export
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    if st.button("📄 Export PDF report"):
        filename = export_pdf(st.session_state.profile, scores, overall)
        with open(filename, "rb") as f:
            st.download_button("Download report", f, file_name=filename, mime="application/pdf")

    if st.button("↺ Restart"):
        st.session_state.page = "landing"
        st.session_state.q_index = 0
        st.session_state.answers = {}
        st.experimental_rerun()

# ---------- Router ----------
if st.session_state.page == "landing":
    hero()
elif st.session_state.page == "assessment":
    question_screen()
elif st.session_state.page == "results":
    results_screen()
