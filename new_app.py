import streamlit as st
from typing import Dict, Any, List

# -----------------------------
# Page & Styles
# -----------------------------
st.set_page_config(page_title="SME Initial Assessment (Wizard)", page_icon="🧭", layout="wide")

CSS = """
<style>
.card{border:1px solid #eaeaea;border-radius:14px;padding:16px;background:#fff}
.qtitle{font-size:1.1rem;font-weight:600;margin:0 0 6px 0}
.qtip{font-size:.9rem;color:#666;margin-top:4px}
.small{font-size:.9rem;color:#666}
.footer{display:flex;gap:8px}
.footer .stButton>button{width:100%;border-radius:10px}
.header-phase{color:#555;font-weight:500}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
def ss_init():
    if "stage" not in st.session_state:
        st.session_state.stage = "intake"  # intake -> qa -> done
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "contact_name": "",
            "business_name": "",
            "industry": "",
            "years": "",
            "headcount": "",
            "turnover": "",
            "work_mode": "",
        }
    if "answers" not in st.session_state:
        st.session_state.answers: Dict[str, Any] = {}
    if "idx" not in st.session_state:
        st.session_state.idx = 0

ss_init()

# -----------------------------
# Question Bank
# -----------------------------
QUESTIONS: List[Dict[str, Any]] = [
    # Digital Footprint
    {
        "id": "sell_online",
        "phase": "Digital Footprint",
        "text": "Do you sell products or deliver services online?",
        "type": "choice",
        "choices": ["Yes – on my own website","Yes – via marketplaces (Amazon/Etsy)","No – mostly offline"],
        "tip": "This helps us understand your online exposure and dependencies."
    },
    {
        "id": "data_types",
        "phase": "Digital Footprint",
        "text": "Do you store customer or employee information (e.g., emails, invoices, payment info)?",
        "type": "choice",
        "choices": ["Yes","No"],
        "tip": "Handling personal data increases your duty of care and regulatory exposure."
    },
    {
        "id": "tools_regular",
        "phase": "Digital Footprint",
        "text": "Which of these do you rely on daily?",
        "type": "multi",
        "choices": [
            "Email","Accounting/finance software","CRM or client database",
            "Cloud storage (Google Drive/OneDrive etc.)","Online payment system","Website or webshop"
        ],
        "tip": "This identifies where your critical information and daily operations live."
    },
    # IT Ownership
    {
        "id": "website_owner",
        "phase": "IT Ownership",
        "text": "Who looks after your website and online systems?",
        "type": "choice",
        "choices": ["I do it myself","Someone on my team","An external company or freelancer"]
    },
    {
        "id": "it_support",
        "phase": "IT Ownership",
        "text": "Who takes care of your computers, email and systems when something needs setup/fixing?",
        "type": "choice",
        "choices": ["I do","A friend/freelancer","An IT company","In-house IT team"]
    },
    {
        "id": "setup_by",
        "phase": "IT Ownership",
        "text": "Did you personally set up your main systems (email, website, backups)?",
        "type": "choice",
        "choices": ["Yes, mostly me","Shared effort","Someone else handled it"]
    },
    {
        "id": "asset_list",
        "phase": "IT Ownership",
        "text": "Do you have a clear list of systems, accounts and devices you use?",
        "type": "choice",
        "choices": ["Yes, documented","Rough idea","Not really"]
    },
    # Partners
    {
        "id": "third_parties",
        "phase": "Partners",
        "text": "Do you work with external partners who handle your data or systems (host, accountant, logistics, marketing tools)?",
        "type": "choice",
        "choices": ["Yes","No"]
    },
    {
        "id": "partner_count",
        "phase": "Partners",
        "text": "How many key partners or providers do you rely on?",
        "type": "choice",
        "choices": ["0–2","3–5","6+"]
    },
    {
        "id": "breach_contact",
        "phase": "Partners",
        "text": "If a main partner had a breach, would you know who to contact and what to do?",
        "type": "choice",
        "choices": ["Yes – I know who to reach","Not really sure"]
    },
    # Confidence
    {
        "id": "confidence",
        "phase": "Confidence",
        "text": "How prepared would you feel if a cyberattack or data loss hit tomorrow?",
        "type": "choice",
        "choices": ["Not at all","Somewhat","Fairly confident","Very confident"]
    },
    {
        "id": "past_incidents",
        "phase": "Confidence",
        "text": "Have you experienced a cybersecurity issue before (e.g., phishing, data loss, locked computer)?",
        "type": "choice",
        "choices": ["Yes","No","Not sure"]
    },
    {
        "id": "know_who_to_call",
        "phase": "Confidence",
        "text": "Do you know who to call or where to get help if something happened?",
        "type": "choice",
        "choices": ["Yes","No"]
    },
]
TOTAL = len(QUESTIONS)

# -----------------------------
# Helpers
# -----------------------------
def digital_dependency_score(ans: Dict[str, Any]) -> int:
    s = 0
    if ans.get("sell_online","").startswith("Yes"): s += 2
    if ans.get("data_types") == "Yes": s += 1
    s += min(len(ans.get("tools_regular", [])), 4)
    return s

def dd_text(v:int) -> str:
    return "Low" if v <= 2 else ("Medium" if v <= 5 else "High")

def reset_all():
    for k in ["stage","profile","answers","idx"]:
        if k in st.session_state: del st.session_state[k]
    ss_init()

# -----------------------------
# Sidebar snapshot
# -----------------------------
with st.sidebar:
    st.markdown("### Snapshot")
    p = st.session_state.profile
    st.markdown(
f"""**Business:** {p.get('business_name') or '—'}  
**Industry:** {p.get('industry') or '—'}  
**People:** {p.get('headcount') or '—'}  
**Years:** {p.get('years') or '—'}  
**Turnover:** {p.get('turnover') or '—'}  
**Work mode:** {p.get('work_mode') or '—'}  
"""
    )
    st.markdown("---")
    dd = dd_text(digital_dependency_score(st.session_state.answers))
    st.markdown(f"**Digital dependency (live):** {dd}")
    st.caption("Derived from online sales, data handling, and daily tools.")
    if st.button("🔁 Restart"):
        reset_all()
        st.rerun()

# -----------------------------
# Header
# -----------------------------
st.title("🧭 Initial Assessment")
st.caption("A short intake followed by a clean, one-question-per-page flow.")

# -----------------------------
# Stage: Intake
# -----------------------------
if st.session_state.stage == "intake":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("First, tell us a bit about the business (≈2 minutes)")
    col1, col2 = st.columns(2)
    with col1:
        contact = st.text_input("Your name", value=st.session_state.profile.get("contact_name",""))
        bname   = st.text_input("Business name", value=st.session_state.profile.get("business_name",""))
        industry= st.text_input("Industry / core service (e.g., retail, consulting)")
    with col2:
        years    = st.selectbox("How long in business?", ["<1 year","1–3 years","3–10 years","10+ years"])
        headcount= st.selectbox("How many people (incl. contractors)?", ["Just me","2–5","6–20","21–100","100+"])
        turnover = st.selectbox("Approx. annual turnover", ["<€100k","€100k–500k","€500k–2M",">€2M"])
    work_mode = st.radio("Would you describe your business as mostly…", ["Local & in-person","Online/remote","A mix of both"], horizontal=True)

    c1, c2 = st.columns([1,2])
    with c1:
        proceed = st.button("Start", type="primary", use_container_width=True)
    with c2:
        st.caption("We’ll tailor the next questions based on this.")

    st.markdown('</div>', unsafe_allow_html=True)

    if proceed:
        st.session_state.profile.update({
            "contact_name": contact.strip(),
            "business_name": bname.strip(),
            "industry": industry.strip(),
            "years": years,
            "headcount": headcount,
            "turnover": turnover,
            "work_mode": work_mode
        })
        st.session_state.stage = "qa"
        st.session_state.idx = 0
        st.rerun()

# -----------------------------
# Stage: One-question-per-page (QA)
# -----------------------------
if st.session_state.stage == "qa":
    idx = st.session_state.idx
    q = QUESTIONS[idx]

    # Progress
    st.progress((idx)/TOTAL, text=f"Now: {q['phase']}  •  Question {idx+1} of {TOTAL}")

    # Question Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="qtitle">{q["text"]}</div>', unsafe_allow_html=True)

    # Optional tip (collapsible)
    if q.get("tip"):
        with st.expander("Why this matters"):
            st.markdown(q["tip"])

    # Input control
    curr_val = st.session_state.answers.get(q["id"])

    if q["type"] == "choice":
        # Render radio with current selection (if any)
        answer = st.radio("Select one:", q["choices"], index=q["choices"].index(curr_val) if curr_val in q["choices"] else 0, key=f"radio_{q['id']}")
        st.session_state.answers[q["id"]] = answer

    elif q["type"] == "multi":
        sel = set(curr_val or [])
        cols = st.columns(2)
        updated = []
        for i, opt in enumerate(q["choices"]):
            with cols[i % 2]:
                if st.checkbox(opt, value=(opt in sel), key=f"chk_{q['id']}_{i}"):
                    updated.append(opt)
        st.session_state.answers[q["id"]] = updated

    else:
        txt = st.text_input("Your answer", value=curr_val or "")
        st.session_state.answers[q["id"]] = txt

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    col_prev, col_skip, col_next = st.columns([1,1,1])
    with col_prev:
        disabled_prev = idx == 0
        if st.button("← Back", use_container_width=True, disabled=disabled_prev):
            st.session_state.idx = max(idx - 1, 0)
            st.rerun()
    with col_skip:
        if st.button("Skip", use_container_width=True):
            # keep whatever current state is; mark as skipped if empty
            if q["type"] == "multi" and not st.session_state.answers.get(q["id"]):
                st.session_state.answers[q["id"]] = []
            st.session_state.idx = min(idx + 1, TOTAL - 1)
            if st.session_state.idx == TOTAL - 1 and idx == TOTAL - 1:
                st.session_state.stage = "done"
            st.rerun()
    with col_next:
        if st.button("Save & Next →", type="primary", use_container_width=True):
            st.session_state.idx = idx + 1
            if st.session_state.idx >= TOTAL:
                st.session_state.stage = "done"
            st.rerun()

# -----------------------------
# Stage: Done (Summary)
# -----------------------------
if st.session_state.stage == "done":
    st.success("Initial Assessment complete.")
    p, a = st.session_state.profile, st.session_state.answers
    dd = dd_text(digital_dependency_score(a))

    st.markdown("### Quick Summary")
    st.markdown(
f"""**Business:** {p.get('business_name') or '—'}  
**Industry:** {p.get('industry') or '—'}  
**People:** {p.get('headcount') or '—'} • **Years:** {p.get('years') or '—'} • **Turnover:** {p.get('turnover') or '—'}  
**Work mode:** {p.get('work_mode') or '—'}  

**Digital dependency (derived):** {dd}
"""
    )

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Highlights**")
        highlights = []
        if a.get("sell_online","").startswith("Yes"):
            highlights.append("Online sales increase reliance on website uptime and payment security.")
        if "Cloud storage (Google Drive/OneDrive etc.)" in a.get("tools_regular", []):
            highlights.append("Cloud storage is central — access controls and backups matter.")
        if a.get("data_types") == "Yes":
            highlights.append("You handle personal data — consider privacy and retention basics.")
        if not highlights:
            highlights.append("Operational footprint looks light; next step focuses on essential hygiene.")
        for h in highlights: st.markdown(f"- {h}")

    with colB:
        st.markdown("**Potential blind spots**")
        blindspots = []
        if a.get("asset_list") in ["Rough idea","Not really"]:
            blindspots.append("No clear list of systems/accounts — hard to secure what you can’t see.")
        if a.get("breach_contact") == "Not really sure":
            blindspots.append("No partner-breach playbook — clarify contacts and escalation.")
        if a.get("confidence") in ["Not at all","Somewhat"]:
            blindspots.append("Low confidence — training and basic controls will lift resilience quickly.")
        if not blindspots:
            blindspots.append("Solid baseline. Next, validate backups, MFA, and incident basics.")
        for b in blindspots: st.markdown(f"- {b}")

    st.info("Next: Continue to the Cybersecurity Posture assessment (traffic-light results + action cards).")
    if st.button("→ Continue to Cybersecurity Posture", type="primary"):
        st.success("This will route to Stage 2 in your app.")
