# new_app.py — SME Cyber Risk Self-Assessment (clean light UI, fixed keys)
# Only dependency: streamlit

import streamlit as st

# ------------------ page config ------------------
st.set_page_config(page_title="SME Cyber Risk Self-Assessment", page_icon="🛡️", layout="centered")

# ------------------ light styles ------------------
st.markdown("""
<style>
:root{
  --bg:#FFFFFF; --surface:#F7F8FA; --surface2:#FFFFFF;
  --text:#0B1220; --muted:#6B7280; --primary:#2563EB; --border:#E6E7EB;
}
html, body { background: var(--bg) !important; color: var(--text); }
.block-container{ max-width: 960px; padding-top: 1.25rem !important; }
*{ font-size: 16px; }

/* header */
.hero{ background: var(--surface2); border:1px solid var(--border); border-radius: 20px; padding: 28px 22px; }
.kicker{ font-size:.85rem; letter-spacing:.14em; color: var(--muted); text-transform: uppercase; margin-bottom:.25rem; }
.hero h1{ margin:0; font-size: 2.2rem; line-height:1.25; font-weight: 900; }

/* pills */
.pills{ display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 10px; }
.pill{ background:#EEF1F6; color:#2E3138; border:1px solid var(--border); border-radius: 999px; padding:8px 12px; font-weight:700; font-size:.95rem; }
.pill.active{ background: var(--primary); color:#fff; border-color: var(--primary); }
.pill.done{ background:#E9F7EF; color:#106B35; border-color:#D5EFDF; }

/* progress bar */
.progress{ height:10px; background:#EEF1F6; border:1px solid var(--border); border-radius:999px; overflow:hidden; }
.progress > div{ height:100%; background: var(--primary); width:0%; transition: width .25s ease; }

/* question box */
.box{ background: var(--surface); border:1px solid var(--border); border-radius: 18px; padding: 18px; margin-top: 14px; }
.q{ font-size: 1.45rem; font-weight: 900; margin: 0 0 8px; }

/* radio as cards */
.stRadio [role="radiogroup"]{ display:grid; grid-template-columns:1fr; gap: 12px; }
@media(min-width:860px){ .stRadio [role="radiogroup"]{ grid-template-columns:1fr 1fr; } }
.stRadio label{ width:100%; }
.stRadio div[role="radio"]{
  width:100%; min-height: 82px; padding:16px 14px; border-radius:16px;
  border:1px solid var(--border); background: var(--surface2);
  display:flex; align-items:center; font-weight:800; color: var(--text);
  box-shadow:none;
}
.stRadio div[role="radio"][aria-checked="true"]{
  outline: 3px solid rgba(37,99,235,.25); border-color: var(--primary);
}

/* nav buttons */
.actions{ display:flex; gap:10px; margin-top: 14px; }
.btn{ border:1px solid var(--border); background:#fff; color:var(--text); padding:10px 16px; border-radius:999px; font-weight:900; }
.btn.primary{ background: var(--primary); color:#fff; border-color: var(--primary); }

/* results */
.tiles{ display:grid; grid-template-columns:1fr; gap:12px; margin-top: 12px; }
@media(min-width:860px){ .tiles{ grid-template-columns: repeat(3,1fr);} }
.tile{ background:#fff; border:1px solid var(--border); border-radius:16px; padding:16px; }
.badge{ display:inline-block; padding:6px 12px; border-radius:999px; font-weight:900; font-size:.9rem; }
.badge.red{ background:#FEE2E2; color:#991B1B; }
.badge.orange{ background:#FFEDD5; color:#9A3412; }
.badge.yellow{ background:#FEF9C3; color:#854D0E; }
.badge.green{ background:#DCFCE7; color:#166534; }
.small{ color: var(--muted); font-size:.98rem; }
.hr{ height:1px; background: linear-gradient(90deg,transparent,#ECEFF3,transparent); margin:16px 0; }
</style>
""", unsafe_allow_html=True)

# ------------------ state ------------------
if "page" not in st.session_state: st.session_state.page = "welcome"
if "answers" not in st.session_state: st.session_state.answers = {}   # {q_index: score}
if "idx" not in st.session_state: st.session_state.idx = 0
if "user_profile" not in st.session_state: st.session_state.user_profile = {}

DOMAINS = [
    ("Governance & Risk","GOV"), ("Identity & Access Management","IAM"),
    ("Data Protection & Privacy","DPP"), ("Network & Infrastructure","NET"),
    ("Incident Response & Recovery","IR"), ("Awareness & AI Risk","AIA"),
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
        [("Ad-hoc",2),("Basic",3),("Within 24h",4),("Automated",5)]),
    # IAM
    ("IAM","MFA enabled for email/admin tools?",
        [("No",1),("Some staff",3),("All accounts",4),("All + conditional access",5)]),
    ("IAM","Password manager in use?",
        [("No",1),("Optional",2),("Yes, adopted",4),("Yes + SSO",5)]),
    ("IAM","Unique accounts per staff/device?",
        [("Shared accounts",1),("Mixed",2),("Unique",3),("Unique + review",4)]),
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
        [("No",1),("Partially",2),("Separate SSID/VLAN",3),("Separated + ACLs",4)]),
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
    "GOV":{"good":"Governance foundations visible.","improve":"Add a simple risk register and quarterly access reviews."},
    "IAM":{"good":"MFA & password manager set the right baseline.","improve":"Ensure same-day leaver removals; extend MFA broadly."},
    "DPP":{"good":"Backups + data minimisation practices exist.","improve":"Test restores twice a year; review Wi-Fi/loyalty privacy notices."},
    "NET":{"good":"Basic segmentation and endpoint controls in place.","improve":"Separate guest Wi-Fi from POS; schedule monthly patching."},
    "IR":{"good":"Contacts and reporting route mostly defined.","improve":"Create a 1-page incident card and run a 15-minute tabletop drill."},
    "AIA":{"good":"General awareness exists.","improve":"Quarterly AI-aware micro-training and one phishing simulation."},
}

# ------------------ helpers ------------------
def current_domain(idx:int) -> str:
    return QUESTIONS[min(idx, len(QUESTIONS)-1)][0]

def make_pills(idx:int):
    code_now = current_domain(idx)
    html = ['<div class="pills">']
    for title, code in DOMAINS:
        cls = "pill"
        if code == code_now: cls += " active"
        done = all(i in st.session_state.answers for i,(c,_,_) in enumerate(QUESTIONS) if c==code)
        if done and code != code_now: cls += " done"
        html.append(f'<div class="{cls}">{title}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

def progress(idx:int):
    pct = int((idx / len(QUESTIONS)) * 100)
    st.markdown(f'<div class="progress"><div style="width:{pct}%"></div></div>', unsafe_allow_html=True)

def domain_scores(answers:dict):
    buckets = {code: [] for _, code in DOMAINS}
    for i, (code, _, _) in enumerate(QUESTIONS):
        if i in answers: buckets[code].append(answers[i])
    return {code: (sum(v)/len(v) if v else 0.0) for code, v in buckets.items()}

def label_for(score:float):
    if score < 2: return "red","🔴 Initial"
    if score < 3: return "orange","🟠 Developing"
    if score < 4: return "yellow","🟡 Defined"
    return "green","🟢 Managed/Optimised"

# ------------------ screens ------------------
def welcome():
    st.markdown("""
      <div class="hero">
        <div class="kicker">SME cybersecurity</div>
        <h1>Social-engineering risk self-assessment</h1>
        <p>Clean, fast, and human-centred. One question per screen.</p>
      </div>
    """, unsafe_allow_html=True)
    # IMPORTANT: form key MUST NOT equal any session_state key
    with st.form("frm_profile"):
        name = st.text_input("Business name", key="pf_name", placeholder="e.g., Café Aurora")
        colA, colB = st.columns(2)
        sector = colA.selectbox("Sector", ["Hospitality","Retail","Consulting","Healthcare","Other"], key="pf_sector")
        staff = colB.number_input("Employees", 1, 500, 12, key="pf_staff")
        if st.form_submit_button("Start"):
            st.session_state.user_profile = {"name": (name or "—").strip(), "sector": sector, "staff": staff}
            st.session_state.page = "quiz"
            st.session_state.idx = 0
            st.session_state.answers = {}

def quiz():
    idx = st.session_state.idx
    if idx >= len(QUESTIONS):
        st.session_state.page = "results"; return

    progress(idx)
    make_pills(idx)

    code, qtext, options = QUESTIONS[idx]
    st.markdown(f'<div class="box"><div class="q">{qtext}</div></div>', unsafe_allow_html=True)

    labels = [lbl for (lbl, _score) in options]
    chosen = st.radio(" ", labels, index=None, label_visibility="collapsed", key=f"radio_{idx}")
    if chosen is not None:
        score = next(s for (lbl, s) in options if lbl == chosen)
        st.session_state.answers[idx] = score

    col1, col2 = st.columns(2)
    if col1.button("← Back", use_container_width=True, key=f"back_{idx}", disabled=(idx==0)):
        st.session_state.idx = max(0, idx-1); st.experimental_rerun()
    if col2.button("Next →", use_container_width=True, key=f"next_{idx}"):
        if idx not in st.session_state.answers:
            st.warning("Please select an option to continue.")
        else:
            st.session_state.idx = idx + 1; st.experimental_rerun()

def results():
    scores = domain_scores(st.session_state.answers)
    overall = sum(scores.values())/len(DOMAINS)

    st.subheader("Results")
    st.caption("Traffic-light tiles — clear at a glance.")
    st.markdown('<div class="tiles">', unsafe_allow_html=True)
    for title, code in DOMAINS:
        s = scores[code]; color, tag = label_for(s)
        st.markdown(
            f'<div class="tile"><div class="badge {color}">{tag}</div>'
            f'<div style="height:8px"></div>'
            f'<div style="font-weight:900; font-size:18px">{title}</div>'
            f'<div class="small">Score: {s:.2f} / 5</div></div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.subheader(f"Overall maturity: {overall:.2f} / 5")

    st.markdown("**What you're doing well**")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['good']}")
    st.markdown("**What to improve next**")
    for title, code in DOMAINS:
        st.write(f"- **{title}:** {FEEDBACK[code]['improve']}")

    if st.button("↺ Restart", key="restart"):
        st.session_state.page = "welcome"; st.session_state.idx = 0; st.session_state.answers = {}; st.experimental_rerun()

# ------------------ router ------------------
if st.session_state.page == "welcome": welcome()
elif st.session_state.page == "quiz": quiz()
elif st.session_state.page == "results": results()
