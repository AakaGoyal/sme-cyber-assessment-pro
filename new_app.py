# new_app.py – SME Cyber Risk Self-Assessment (Light UI version)
# Streamlit + FPDF

import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="SME Cyber Risk Self-Assessment", page_icon="🛡️", layout="centered")

# ---------------- LIGHT THEME & STYLES ----------------
st.markdown("""
<style>
:root{
  --bg:#ffffff; --surface:#f8f9fa; --surface2:#ffffff;
  --text:#0b1220; --muted:#586072; --primary:#2563EB; --border:#e6e7eb;
  --ring: rgba(37,99,235,.35);
}
.block-container{padding-top:1.4rem!important; max-width:960px;}
body{background:#fff !important; color:var(--text);}
*{font-size:16px;}
/* Hero */
.hero{background:var(--surface2); border:1px solid var(--border); border-radius:24px; padding:28px 22px;}
.kicker{font-size:.85rem; letter-spacing:.14em; color:var(--muted); text-transform:uppercase; margin-bottom:.25rem;}
.hero h1{font-size:2.3rem; line-height:1.25; margin:0; color:var(--text);}
.hero p{margin:.5rem 0 0; color:#505460; font-size:1rem;}
/* Pills */
.pills{display:flex; flex-wrap:wrap; gap:8px; margin:18px 0 10px;}
.pill{background:#eef0f5; color:#2e3138; border:1px solid #e6e7eb; border-radius:999px; padding:8px 14px; font-weight:700; font-size:.95rem;}
.pill.active{background:var(--primary); color:#fff; border-color:var(--primary);}
.pill.done{background:#e9f7ef; color:#106b35; border-color:#d5efdf;}
/* Question */
.qwrap{background:var(--surface); border:1px solid var(--border); border-radius:22px; padding:24px 18px; margin-top:10px;}
.qtitle{font-size:1.6rem; line-height:1.35; color:var(--text); font-weight:800;}
/* Options grid -> rounded cards */
.grid{display:grid; grid-template-columns:1fr; gap:14px; margin-top:16px;}
@media(min-width:860px){ .grid{grid-template-columns:1fr 1fr;} }
.stButton > button{
  width:100%; min-height:88px; border-radius:18px; border:1px solid var(--border);
  background:var(--surface2); color:var(--text); font-weight:800; text-align:left; padding:18px 16px;
  box-shadow:none; transition:.15s ease;
}
.stButton > button:hover{transform:translateY(-1px); border-color:#d0d3da;}
.stButton > button:focus{outline:4px solid var(--ring); border-color:var(--primary);}
.nav{display:flex; gap:10px; justify-content:space-between; margin-top:20px;}
.nav .btn{border:1px solid var(--border); background:#fff; color:var(--text); padding:12px 18px; border-radius:999px; font-weight:800; font-size:1rem;}
.nav .btn.primary{background:var(--primary); color:#fff; border-color:var(--primary);}
.nav .btn.primary:hover{filter:brightness(0.95);}
/* Results */
.tiles{display:grid; grid-template-columns:1fr; gap:14px; margin-top:12px;}
@media(min-width:860px){ .tiles{grid-template-columns:repeat(3,1fr);} }
.tile{background:#fff; border:1px solid var(--border); border-radius:18px; padding:18px;}
.badge{font-weight:800; font-size:.9rem; padding:6px 12px; border-radius:999px; display:inline-block;}
.badge.red{background:#fee2e2; color:#991b1b;}
.badge.orange{background:#ffedd5; color:#9a3412;}
.badge.yellow{background:#fef9c3; color:#854d0e;}
.badge.green{background:#dcfce7; color:#166534;}
.hr{height:1px; background:linear-gradient(90deg,transparent,#eceff3,transparent); margin:18px 0;}
.small{color:var(--muted); font-size:1rem;}
label, .stTextInput input, .stSelectbox div, .stNumberInput input { font-size:1rem !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state: st.session_state.page = "landing"
if "profile" not in st.session_state: st.session_state.profile = {}
if "answers" not in st.session_state: st.session_state.answers = {}
if "idx" not in st.session_state: st.session_state.idx = 0

DOMAINS = [
    ("Governance & Risk","GOV"),
    ("Identity & Access Management","IAM"),
    ("Data Protection & Privacy","DPP"),
    ("Network & Infrastructure","NET"),
    ("Incident Response & Recovery","IR"),
    ("Awareness & AI Risk","AIA"),
]

QUESTIONS = [
    ("GOV","Do you have documented security responsibilities?",
        [("No / not sure",1),("Some notes exist",2),("Yes, basic doc",3),("Yes, reviewed annually",4)]),
    ("GOV","Do you assess risks at least annually?",
        [("Never",1),("Informal only",2),("Annual checklist",3),("Formal register + actions",4)]),
    ("GOV","Are suppliers (POS/loyalty/app) risk-checked?",
        [("No",1),("Basic check",2),("Contract clauses",3),("Checklist + review cycle",4)]),
    ("GOV","Joiner/leaver access managed?",
        [("Ad-hoc",2),("Basic",3),("Formal within 24h",4),("Automated",5)]),

    ("IAM","MFA enabled for email/admin tools?",
        [("No",1),("Some staff",3),("All accounts",4),("All + conditional access",5)]),
    ("IAM","Password manager in use?",
        [("No",1),("Optional",2),("Yes, adopted",4),("Yes + SSO",5)]),
    ("IAM","Unique accounts per staff/device?",
        [("Shared accounts",1),("Mixed",2),("Unique",3),("Unique + periodic review",4)]),
    ("IAM","Leaver access removed within 24h?",
        [("Days/weeks",1),("72h",2),("24–48h",3),("Same day",4)]),

    ("DPP","Backups exist & tested?",
        [("None",1),("Ad-hoc",2),("Regular backups",3),("Tested restores",4)]),
    ("DPP","Minimal personal data collected?",
        [("Don’t know",1),("Some minimisation",2),("Yes, defined",3),("Yes + DPIA if needed",4)]),
    ("DPP","Cardholder data stored locally?",
        [("Yes",1),("Unsure",2),("No, processor only",4),("Tokenised controls",5)]),
    ("DPP","Privacy notice & consent on Wi-Fi/loyalty?",
        [("No",1),("Basic",2),("Yes",3),("Yes + reviewed",4)]),

    ("NET","Router/POS firmware & patches?",
        [("Rarely",1),("Sometimes",2),("Monthly",3),("Automated/managed",4)]),
    ("NET","Guest Wi-Fi isolated from POS?",
        [("No",1),("Partially",2),("Yes (separate SSID/VLAN)",3),("Yes + ACLs",4)]),
    ("NET","Endpoint protection on devices?",
        [("No",1),("Basic AV",2),("AV + auto updates",3),("EDR + alerts",4)]),
    ("NET","Default creds removed everywhere?",
        [("Not sure",1),("Mostly",2),("Yes",3),("Yes + periodic audit",4)]),

    ("IR","Incident playbook exists?",
        [("No",1),("Draft",2),("Yes",3),("Yes + drills",4)]),
    ("IR","Contacts list (bank/IT/processor)?",
        [("No",1),("Partial",2),("Yes",3),("Yes + wallet card",4)]),
    ("IR","Restore test in last 6 months?",
        [("Never",1),("Over a year",2),("Yes",3),("Yes + recorded",4)]),
    ("IR","Phishing/reporting channel defined?",
        [("No",1),("Email to IT",2),("Button/alias",3),("Button + triage SOP",4)]),

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

def domain_scores(answers):
    buckets = {code: [] for _, code in DOMAINS}
    for i, (code,_,_) in enumerate(QUESTIONS):
        if i in answers: buckets[code].append(answers[i])
    return {code: (sum(v)/len(v) if v else 0.0) for code,v in buckets.items()}

def label_for(score):
    if score < 2: return "red","🔴 Initial"
    if score < 3: return "orange","🟠 Developing"
    if score < 4: return "yellow","🟡 Defined"
    return "green","🟢 Managed/Optimised"

# ------------- UI SCREENS -------------
def landing():
    st.markdown("""
    <div class="hero">
      <div class="kicker">SME cybersecurity</div>
      <h1>Social-engineering risk self-assessment</h1>
      <p>Simple, human-centred, and fast. One question per screen.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("frm_profile"):
        name = st.text_input("Business name", placeholder="e.g., Café Aurora")
        colA, colB = st.columns(2)
        sector = colA.selectbox("Sector", ["Hospitality","Retail","Consulting","Healthcare","Other"])
        staff = colB.number_input("Employees", 1, 500, 12)
        submitted = st.form_submit_button("Start")
    if submitted:
        st.session_state.profile = {"name": name or "—", "sector": sector, "staff": staff}
        st.session_state.page = "q"

def pills(current_idx):
    code_now = QUESTIONS[min(current_idx, len(QUESTIONS)-1)][0]
    html = ['<div class="pills">']
    for title, code in DOMAINS:
        cls = "pill"
        if code == code_now: cls += " active"
        done = all(i in st.session_state.answers for i,(c,_,_) in enumerate(QUESTIONS) if c==code)
        if done and code != code_now: cls += " done"
        html.append(f'<div class="{cls}">{title}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

def question():
    idx = st.session_state.idx
    if idx >= len(QUESTIONS):
        st.session_state.page = "results"; return
    code, qtext, options = QUESTIONS[idx]
    pills(idx)
    st.markdown(f'<div class="qwrap"><div class="qtitle">{qtext}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="grid">', unsafe_allow_html=True)
    for i,(label,score) in enumerate(options):
        if st.button(label, key=f"opt_{idx}_{i}", use_container_width=True):
            st.session_state.answers[idx] = score
    st.markdown('</div>', unsafe_allow_html=True)
    colL, colR = st.columns(2)
    if colL.button("← Back", use_container_width=True, disabled=(idx==0)):
        st.session_state.idx = max(0, idx-1); st.experimental_rerun()
    if colR.button("Next →", use_container_width=True):
        if idx not in st.session_state.answers:
            st.warning("Please select an option to continue.")
        else:
            st.session_state.idx = idx+1; st.experimental_rerun()

def results():
    scores = domain_scores(st.session_state.answers)
    overall = sum(scores.values())/len(DOMAINS)
    st.markdown("### Results")
    st.caption("Traffic-light tiles — clear at a glance.")
    st.markdown('<div class="tiles">', unsafe_allow_html=True)
    for title, code in DOMAINS:
        s = scores[code]; color, tag = label_for(s)
        st.markdown(
            f'<div class="tile"><div class="badge {color}">{tag}</div>'
            f'<div style="height:8px"></div>'
            f'<div style="font-weight:800; font-size:18px">{title}</div>'
            f'<div class="small">Score: {s:.2f} / 5</div></div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader(f"Overall maturity: {overall:.2f} / 5")
    st.markdown("**What you're doing well**")
    for title,code in DOMAINS: st.write(f"- **{title}:** {FEEDBACK[code]['good']}")
    st.markdown("**What to improve next**")
    for title,code in DOMAINS: st.write(f"- **{title}:** {FEEDBACK[code]['improve']}")
    if st.button("↺ Restart"):
        st.session_state.page="landing"; st.session_state.idx=0; st.session_state.answers={}; st.experimental_rerun()

# ------------- ROUTER -------------
if st.session_state.page=="landing": landing()
elif st.session_state.page=="q": question()
elif st.session_state.page=="results": results()
