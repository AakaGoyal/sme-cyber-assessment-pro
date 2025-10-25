import streamlit as st
from typing import Dict, Any, List, Tuple

# =========================================================
# Page & styles
# =========================================================
st.set_page_config(page_title="SME Self-Assessment Wizard", page_icon="🧭", layout="wide")

CSS = """
<style>
.card{border:1px solid #eaeaea;border-radius:14px;padding:16px;background:#fff}
.qtitle{font-size:1.1rem;font-weight:600;margin:0 0 8px 0}
.qtip{font-size:.95rem;color:#444;margin-top:6px}
.small{font-size:.9rem;color:#666}
.footer{display:flex;gap:8px}
.footer .stButton>button{width:100%;border-radius:10px}
.header-phase{color:#334; font-weight:600; font-size:1.05rem; margin:2px 0 6px 0}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;font-weight:600}
.red{background:#ffe7e7;border:1px solid #ffd0d0;color:#b10000}
.amber{background:#fff3cd;border:1px solid #ffe59a;color:#7a5b00}
.green{background:#e6f7e6;border:1px solid #c9efc9;color:#0d6b0d}
.kpi{border-radius:12px;border:1px solid #eee;padding:14px;background:#fafafa}
.kpi h4{margin:.1rem 0 .4rem 0}
ul.tight>li{margin-bottom:.3rem}
.progress-head{font-size:1rem; font-weight:600; color:#223;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================================================
# Session init
# =========================================================
def ss_init():
    if "stage" not in st.session_state:
        # intake -> qa (Initial) -> done_initial -> cyber_qa -> cyber_results
        st.session_state.stage = "intake"
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "contact_name": "",
            "business_name": "",
            "industry": {"value":"", "other":""},  # value + custom
            "years": "",
            "headcount": "",
            "turnover": "",
            "work_mode": "",
        }
    if "answers" not in st.session_state:
        st.session_state.answers: Dict[str, Any] = {}
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    if "cyber_answers" not in st.session_state:
        st.session_state.cyber_answers: Dict[str, Any] = {}
    if "cyber_idx" not in st.session_state:
        st.session_state.cyber_idx = 0

ss_init()

# =========================================================
# Helpers (shared)
# =========================================================
def digital_dependency_score(ans: Dict[str, Any]) -> int:
    s = 0
    if ans.get("sell_online","").startswith("Yes"): s += 2
    if ans.get("data_types") == "Yes": s += 1
    s += min(len(ans.get("tools_regular", [])), 4)
    return s

def dd_text(v:int) -> str:
    return "Low" if v <= 2 else ("Medium" if v <= 5 else "High")

def reset_all():
    for k in ["stage","profile","answers","idx","cyber_answers","cyber_idx"]:
        if k in st.session_state: del st.session_state[k]
    ss_init()

def traffic_light(pct: float) -> Tuple[str, str]:
    if pct >= 75: return ("green","Good")
    if pct >= 40: return ("amber","Needs work")
    return ("red","At risk")

# =========================================================
# Initial Assessment — Question Bank (+ branching)
# =========================================================

INDUSTRY_OPTIONS = [
    "Retail",
    "Food & Beverage (Café/Restaurant)",
    "Professional Services (Consulting/Legal/Accounting)",
    "Creative/Marketing/Design",
    "Healthcare",
    "Education",
    "Manufacturing",
    "Logistics / Transportation",
    "Construction / Trades",
    "Real Estate",
    "Hospitality / Travel",
    "Non-profit",
    "IT / Software",
    "Finance / Insurance",
    "Personal Services",
    "e-Commerce only",
    "Marketplace seller",
    "Government / Public sector",
    "Agriculture",
    "Automotive",
    "Fitness / Wellness",
    "Beauty / Salon",
    "Event services",
    "Other (please specify)"
]

TOOLS_EXPANDED = [
    "Email",
    "Office/Docs (e.g., Microsoft 365, Google Workspace Docs)",
    "Cloud storage (Google Drive/OneDrive etc.)",
    "Accounting/Finance software",
    "CRM or client list",
    "POS / Till or Booking system",
    "Website or webshop",
    "Online payment system",
    "Messaging (Teams/Slack/WhatsApp Business)",
    "Project tool (Trello/Asana/Jira)",
    "HR/Payroll",
    "Inventory/ERP",
    "Marketing tool (Mailchimp/HubSpot)",
]

BASE_QUESTIONS: List[Dict[str, Any]] = [
    # Digital Footprint
    {
        "id": "sell_online",
        "phase": "Digital Footprint",
        "text": "Do you sell products or deliver services online?",
        "type": "choice",
        "choices": ["Yes – on my own website","Yes – via marketplaces (Amazon/Etsy)","No – mostly offline"],
        "tip": "This helps us understand your online exposure and dependencies.",
        "allow_other": False
    },
    {
        "id": "marketplaces_detail",
        "phase": "Digital Footprint",
        "text": "Which marketplace(s) do you use? (e.g., Amazon, Etsy, eBay) — type a short list",
        "type": "text",
        "show_if": lambda a: a.get("sell_online") == "Yes – via marketplaces (Amazon/Etsy)"
    },
    {
        "id": "data_types",
        "phase": "Digital Footprint",
        "text": "Do you store customer or employee information (e.g., emails, invoices, payment info)?",
        "type": "choice",
        "choices": ["Yes","No"],
        "tip": "You **store data** if you keep any of these: customer emails or order history/invoices; newsletter lists; employee records (contracts/payroll); support tickets/chat logs; CCTV with identifiable faces; payment records (even if payments go through Stripe/PayPal, you likely still store related customer info).",
        "allow_other": False
    },
    {
        "id": "tools_regular",
        "phase": "Digital Footprint",
        "text": "Which of these do you rely on daily?",
        "type": "multi",
        "choices": TOOLS_EXPANDED,
        "tip": "This identifies where your critical information and daily operations live."
    },

    # IT Ownership
    {
        "id": "website_owner",
        "phase": "IT Ownership",
        "text": "Who looks after your website and online systems?",
        "type": "choice",
        "choices": ["I do it myself","Someone on my team","An external company or freelancer"],
        "allow_other": True
    },
    {
        "id": "it_support",
        "phase": "IT Ownership",
        "text": "Who takes care of your computers, email and systems when something needs setup/fixing?",
        "type": "choice",
        "choices": ["I do","A friend/freelancer","An IT company","In-house IT team"],
        "allow_other": True
    },
    {
        "id": "setup_by",
        "phase": "IT Ownership",
        "text": "Did you personally set up your main systems (email, website, backups)?",
        "type": "choice",
        "choices": ["Yes, mostly me","Shared effort","Someone else handled it"],
        "allow_other": True
    },
    {
        "id": "asset_list",
        "phase": "IT Ownership",
        "text": "Do you have a clear list of systems, accounts and devices you use?",
        "type": "choice",
        "choices": ["Yes, documented","Rough idea","Not really"],
        "allow_other": True
    },

    # Partners (branch)
    {
        "id": "third_parties",
        "phase": "Partners",
        "text": "Do you work with external partners who handle your data or systems (host, accountant, logistics, marketing tools)?",
        "type": "choice",
        "choices": ["Yes","No"],
        "allow_other": False
    },
    {
        "id": "partner_count",
        "phase": "Partners",
        "text": "How many key partners or providers do you rely on?",
        "type": "choice",
        "choices": ["0–2","3–5","6+"],
        "show_if": lambda a: a.get("third_parties") == "Yes",
        "allow_other": False
    },
    {
        "id": "main_partners",
        "phase": "Partners",
        "text": "Who are your main partners? (select all that apply)",
        "type": "multi",
        "choices": [
            "Hosting provider", "Domain/DNS", "Email provider", "Payment processor",
            "Accountant/Payroll", "Logistics/Courier", "Marketing tool",
            "Managed IT", "Website developer/agency", "Cloud storage",
            "Other (add details in summary)"
        ],
        "show_if": lambda a: a.get("third_parties") == "Yes"
    },
    {
        "id": "breach_contact",
        "phase": "Partners",
        "text": "If one of these partners had a breach, would you know what to do and who to contact?",
        "type": "choice",
        "choices": ["Yes – I know who to reach","Not really sure"],
        "show_if": lambda a: a.get("third_parties") == "Yes",
        "allow_other": False
    },

    # Confidence
    {
        "id": "confidence",
        "phase": "Confidence",
        "text": "How prepared would you feel if a cyberattack or data loss hit tomorrow?",
        "type": "choice",
        "choices": ["Not at all","Somewhat","Fairly confident","Very confident"],
        "allow_other": False
    },
    {
        "id": "past_incidents",
        "phase": "Confidence",
        "text": "Have you experienced a cybersecurity issue before — like a phishing email, data loss, or a locked computer?",
        "type": "choice",
        "choices": ["Yes","No","Not sure"],
        "allow_other": False
    },
    {
        "id": "know_who_to_call",
        "phase": "Confidence",
        "text": "Do you know who to call or where to get help if something happened?",
        "type": "choice",
        "choices": ["Yes","No"],
        "allow_other": False
    },
]

def visible_questions(answers: Dict[str, Any]) -> List[Dict[str, Any]]:
    qs = []
    for q in BASE_QUESTIONS:
        cond = q.get("show_if")
        if cond is None or cond(answers):
            qs.append(q)
    return qs

# =========================================================
# Cybersecurity Posture — Question Bank (plain-language)
# =========================================================
CYBER_QUESTIONS: List[Dict[str, Any]] = [
    # Access & Accounts
    {
        "id":"mfa_all",
        "domain":"Access & Accounts",
        "text":"Do all important accounts use **Multi-Factor Authentication (MFA)**?",
        "type":"choice",
        "choices":["— Select one —","Yes, for all important accounts","Yes, for some","No / not sure"],
        "weights":[0,2,1,0],
        "tip":"MFA = password **plus** a second step (e.g., code from an app like Google Authenticator, SMS, or email). It blocks most account-takeover attempts."
    },
    {
        "id":"shared_accounts",
        "domain":"Access & Accounts",
        "text":"Does each person have their **own** login for work systems, or are logins shared?",
        "type":"choice",
        "choices":["— Select one —","Everyone has their own","Some shared accounts","Mostly shared accounts"],
        "weights":[0,2,1,0],
        "tip":"Personal logins let you remove access when someone leaves and see who did what."
    },
    {
        "id":"admin_rights",
        "domain":"Access & Accounts",
        "text":"Are **administrator rights** kept to a **few people** and used **only when needed**?",
        "type":"choice",
        "choices":["— Select one —","Yes, limited & reviewed","Partly","No / not sure"],
        "weights":[0,2,1,0],
        "tip":"Admins can change settings/install software. Limit who has admin, use a separate admin account, and review every 3–6 months."
    },

    # Devices
    {
        "id":"device_lock",
        "domain":"Devices",
        "text":"Are all laptops/phones protected with password/biometrics **and** auto-lock?",
        "type":"choice",
        "choices":["— Select one —","Yes, all","Most","No / not sure"],
        "weights":[0,2,1,0]
    },
    {
        "id":"disk_encryption",
        "domain":"Devices",
        "text":"If a **laptop is lost or stolen**, would the data on it be **locked/encrypted** so others can’t read it?",
        "type":"choice",
        "choices":["— Select one —","Yes, on all","Some / in progress","No / not sure"],
        "weights":[0,2,1,0],
        "tip":"Encryption protects files on a lost device. Windows = **BitLocker**, Mac = **FileVault**."
    },

    # Data & Backups
    {
        "id":"backup_frequency",
        "domain":"Data & Backups",
        "text":"How often are business-critical files **backed up automatically**?",
        "type":"choice",
        "choices":["— Select one —","Daily or continuous","Weekly","Rarely / never / not sure"],
        "weights":[0,2,1,0],
        "tip":"Follow **3-2-1**: 3 copies, 2 different places, 1 offsite/immutable."
    },
    {
        "id":"backup_restore_test",
        "domain":"Data & Backups",
        "text":"Have you **tested restoring** from backups recently?",
        "type":"choice",
        "choices":["— Select one —","Yes, in last 6 months","Longer than 6 months","Never / not sure"],
        "weights":[0,2,1,0]
    },

    # Email & Awareness
    {
        "id":"phishing_training",
        "domain":"Email & Awareness",
        "text":"Do staff get **phishing/security awareness training**?",
        "type":"choice",
        "choices":["— Select one —","Yes, at least yearly","Ad-hoc / once","No / not sure"],
        "weights":[0,2,1,0]
    },
    {
        "id":"email_filters",
        "domain":"Email & Awareness",
        "text":"Do you have **spam/malware filtering** and **link protection** on email?",
        "type":"choice",
        "choices":["— Select one —","Yes, managed controls","Basic filtering only","No / not sure"],
        "weights":[0,2,1,0]
    },

    # Updates & AV
    {
        "id":"patching",
        "domain":"Updates & AV",
        "text":"Are computers and apps set to **install updates automatically** (within ~14 days)?",
        "type":"choice",
        "choices":["— Select one —","Yes, automated","Partly manual","No / not sure"],
        "weights":[0,2,1,0],
        "tip":"Updates (‘patches’) fix security holes used by attackers."
    },
    {
        "id":"av_edr",
        "domain":"Updates & AV",
        "text":"Is **antivirus** (or **EDR – Endpoint Detection & Response**) installed on work devices and **checked centrally**?",
        "type":"choice",
        "choices":["— Select one —","Yes, on all devices","Some devices","No / not sure"],
        "weights":[0,2,1,0],
        "tip":"‘Centrally checked’ = someone can see if all devices are protected."
    },

    # Response & Continuity
    {
        "id":"ir_contacts",
        "domain":"Response & Continuity",
        "text":"If something goes wrong, do you have a **one-page incident checklist** and **key contacts**?",
        "type":"choice",
        "choices":["— Select one —","Yes, documented","Partial / informal","No / not sure"],
        "weights":[0,2,1,0]
    },
    {
        "id":"vendor_breach_flow",
        "domain":"Response & Continuity",
        "text":"If a **vendor/partner** is breached, do you know **their contact** and the **steps to take**?",
        "type":"choice",
        "choices":["— Select one —","Yes, clear contacts","Some idea","No / not sure"],
        "weights":[0,2,1,0]
    },
]
CYBER_TOTAL = len(CYBER_QUESTIONS)

def compute_domain_scores(cyber_ans: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    domain_max: Dict[str,int] = {}
    domain_sum: Dict[str,int] = {}
    for q in CYBER_QUESTIONS:
        dom = q["domain"]
        domain_max[dom] = domain_max.get(dom, 0) + max(q["weights"])
        if q["id"] in cyber_ans:
            sel = cyber_ans[q["id"]]
            idx = q["choices"].index(sel) if sel in q["choices"] else 0
            w = q["weights"][idx]
        else:
            w = 0
        domain_sum[dom] = domain_sum.get(dom, 0) + w
    results: Dict[str, Dict[str, Any]] = {}
    for dom in domain_max:
        pct = (domain_sum[dom] / domain_max[dom]) * 100 if domain_max[dom] else 0
        colour, label = traffic_light(pct)
        results[dom] = {"score": round(pct), "colour": colour, "label": label}
    return results

def overall_score(domain_scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not domain_scores: return {"score":0,"colour":"red","label":"At risk"}
    avg = sum(v["score"] for v in domain_scores.values()) / len(domain_scores)
    colour, label = traffic_light(avg)
    return {"score": round(avg), "colour": colour, "label": label}

def add_action_cards(initial: Dict[str, Any], cyber: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    good, fixes = [], []
    def chose(id_, i):
        q = next(q for q in CYBER_QUESTIONS if q["id"] == id_)
        sel = cyber.get(id_, "")
        return q["choices"].index(sel) == i if sel in q["choices"] else False

    # Goods
    if chose("mfa_all", 1): good.append("MFA enabled on important accounts.")
    if chose("disk_encryption", 1): good.append("Full-disk encryption on devices.")
    if chose("backup_frequency", 1): good.append("Frequent (daily/continuous) backups.")
    if chose("backup_restore_test", 1): good.append("Backups are restore-tested.")
    if chose("patching", 1): good.append("Automatic updates are in place.")
    if chose("av_edr", 1): good.append("AV/EDR deployed across devices.")
    if chose("phishing_training", 1): good.append("Regular phishing/security training.")
    if chose("ir_contacts", 1): good.append("Incident contacts/checklist documented.")

    # Fixes
    if not chose("mfa_all", 1):
        fixes.append("Turn on **MFA** for email, cloud storage, accounting, and admin portals (today).")
    if not chose("backup_frequency", 1):
        fixes.append("Implement **3-2-1 backups** with at least one **immutable/offsite** copy.")
    if not chose("disk_encryption", 1):
        fixes.append("Enable **full-disk encryption** (BitLocker/FileVault) on all laptops/desktops.")
    if not chose("patching", 1):
        fixes.append("Enable **automatic updates** for OS and key apps; patch within ~14 days.")
    if not chose("av_edr", 1):
        fixes.append("Deploy **reputable AV/EDR** on all devices and ensure it’s updating.")
    if not chose("ir_contacts", 1):
        fixes.append("Create a **one-page incident checklist** with internal & vendor contacts.")
    if not chose("phishing_training", 1):
        fixes.append("Schedule **annual phishing/awareness training** (15–30 minutes).")
    if not chose("email_filters", 1):
        fixes.append("Enable **advanced email filtering** (malware/link protection) in your mail suite.")
    if not chose("shared_accounts", 1):
        fixes.append("Stop using **shared accounts**; give each person their own login.")
    if not chose("admin_rights", 1):
        fixes.append("Restrict **admin rights**; use separate admin accounts and review quarterly.")

    if initial.get("third_parties") == "Yes" and initial.get("breach_contact") == "Not really sure":
        if "Create a **one-page incident checklist** with internal & vendor contacts." not in fixes:
            fixes.insert(0, "Add **vendor breach contacts** to your incident checklist (host, payments, accountant).")

    return good[:8], fixes[:10]

# =========================================================
# Sidebar snapshot
# =========================================================
with st.sidebar:
    st.markdown("### Snapshot")
    p = st.session_state.profile
    industry_disp = p.get("industry", {}).get("value") or "—"
    if industry_disp.startswith("Other") and p.get("industry", {}).get("other"):
        industry_disp = f"Other — {p['industry']['other']}"
    st.markdown(
f"""**Business:** {p.get('business_name') or '—'}  
**Industry:** {industry_disp}  
**People:** {p.get('headcount') or '—'}  
**Years:** {p.get('years') or '—'}  
**Turnover:** {p.get('turnover') or '—'}  
**Work mode:** {p.get('work_mode') or '—'}  
"""
    )
    st.markdown("---")
    dd = dd_text(digital_dependency_score(st.session_state.answers))
    st.markdown(f"**Digital dependency (derived):** {dd}")
    st.caption("Derived from online sales, data handling, and daily tools.")
    if st.button("🔁 Restart"):
        reset_all(); st.rerun()

# =========================================================
# Header
# =========================================================
st.title("🧭 SME Self-Assessment Wizard")

# =========================================================
# Stage 1: Intake
# =========================================================
if st.session_state.stage == "intake":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("First, tell us a bit about the business (≈2 minutes)")
    col1, col2 = st.columns(2)
    with col1:
        contact = st.text_input("Your name", value=st.session_state.profile.get("contact_name",""))
        bname   = st.text_input("Business name", value=st.session_state.profile.get("business_name",""))
        # Industry typeahead + other
        current_val = st.session_state.profile["industry"]["value"]
        init_index = INDUSTRY_OPTIONS.index(current_val) if current_val in INDUSTRY_OPTIONS else len(INDUSTRY_OPTIONS)-1
        industry_sel = st.selectbox("Industry / core service", options=INDUSTRY_OPTIONS, index=init_index)
        industry_other = ""
        if industry_sel == "Other (please specify)":
            industry_other = st.text_input("Type your industry / service", value=st.session_state.profile["industry"].get("other",""))
    with col2:
        years    = st.selectbox("How long in business?", ["<1 year","1–3 years","3–10 years","10+ years"])
        headcount= st.selectbox("How many people (incl. contractors)?", ["Just me","2–5","6–20","21–100","100+"])
        turnover = st.selectbox("Approx. annual turnover", ["<€100k","€100k–500k","€500k–2M",">€2M"])
    work_mode = st.radio("Would you describe your business as mostly…", ["Local & in-person","Online/remote","A mix of both"], horizontal=True)

    c1, c2 = st.columns([1,2])
    with c1:
        proceed = st.button("Start Initial Assessment", type="primary", use_container_width=True)
    with c2:
        st.caption("We’ll tailor the next questions based on this.")

    st.markdown('</div>', unsafe_allow_html=True)

    if proceed:
        st.session_state.profile.update({
            "contact_name": contact.strip(),
            "business_name": bname.strip(),
            "industry": {"value": industry_sel, "other": industry_other.strip()},
            "years": years,
            "headcount": headcount,
            "turnover": turnover,
            "work_mode": work_mode
        })
        st.session_state.stage = "qa"
        st.session_state.idx = 0
        st.rerun()

# =========================================================
# Utilities for rendering QA pages
# =========================================================
PLACEHOLDER = "— Select one —"

def render_choice_with_other(qid: str, options: List[str], allow_other: bool, current: Any):
    """
    Safe radio renderer with placeholder and optional 'Other (please specify)'.
    - Keeps indices in range.
    - Prefills comment if returning to a previously saved 'Other'.
    """
    base = options[:]
    if allow_other and "Other (please specify)" not in base:
        base.append("Other (please specify)")
    opts = [PLACEHOLDER] + base

    # compute safe pre-selected index
    pre_idx = 0
    if isinstance(current, dict) and current.get("value") in opts:
        pre_idx = opts.index(current["value"])
    elif isinstance(current, str) and current in opts:
        pre_idx = opts.index(current)

    selected = st.radio("Select one:", opts, index=pre_idx, key=f"radio_{qid}")

    other_text = ""
    if allow_other and selected == "Other (please specify)":
        preset = current.get("comment", "") if isinstance(current, dict) else ""
        other_text = st.text_input("Please specify", value=preset)

    return selected, other_text

# =========================================================
# Stage 1: One-question-per-page (Initial Assessment)
# =========================================================
if st.session_state.stage == "qa":
    answers = st.session_state.answers
    Q = visible_questions(answers)
    idx = st.session_state.idx
    q = Q[idx]

    # Progress
    st.markdown(f'<div class="progress-head">Initial Assessment • {q["phase"]} • Step {idx+1} of {len(Q)}</div>', unsafe_allow_html=True)
    st.progress((idx)/max(len(Q),1))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="qtitle">{q["text"]}</div>', unsafe_allow_html=True)
    if q.get("tip"):
        with st.expander("Why this matters"):
            st.markdown(q["tip"])

    curr_val = answers.get(q["id"])

    if q["type"] == "choice":
        sel, other_text = render_choice_with_other(q["id"], q["choices"], q.get("allow_other", False), curr_val)
        if sel == "Other (please specify)":
            answers[q["id"]] = {"value": sel, "comment": other_text}
        elif sel == PLACEHOLDER:
            answers.pop(q["id"], None)  # don't store placeholder
        else:
            answers[q["id"]] = sel

    elif q["type"] == "multi":
        selset = set(curr_val or [])
        cols = st.columns(2)
        updated = []
        for i, opt in enumerate(q["choices"]):
            with cols[i % 2]:
                if st.checkbox(opt, value=(opt in selset), key=f"chk_{q['id']}_{i}"):
                    updated.append(opt)
        answers[q["id"]] = updated

    elif q["type"] == "text":
        t = st.text_input("Your answer", value=curr_val or "")
        answers[q["id"]] = t

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    col_prev, col_skip, col_next = st.columns([1,1,1])
    with col_prev:
        st.button("← Back", use_container_width=True, disabled=(idx==0),
                  on_click=lambda: st.session_state.update(idx=max(idx-1,0)))
    with col_skip:
        if st.button("Skip", use_container_width=True):
            st.session_state.idx = min(idx + 1, len(Q) - 1)
            st.rerun()
    with col_next:
        if st.button("Next →", type="primary", use_container_width=True):
            new_Q = visible_questions(st.session_state.answers)
            current_id = q["id"]
            ids = [qq["id"] for qq in new_Q]
            pos = ids.index(current_id) + 1 if current_id in ids else min(idx + 1, len(new_Q))
            if pos >= len(new_Q):
                st.session_state.stage = "done_initial"
            else:
                st.session_state.idx = pos
            st.rerun()

# =========================================================
# Stage 1: Summary + Continue
# =========================================================
if st.session_state.stage == "done_initial":
    st.success("Initial Assessment complete.")
    p, a = st.session_state.profile, st.session_state.answers
    dd = dd_text(digital_dependency_score(a))

    st.markdown("### Quick Summary")
    industry_disp = p["industry"]["value"]
    if industry_disp.startswith("Other") and p["industry"]["other"]:
        industry_disp = f"Other — {p['industry']['other']}"
    st.markdown(
f"""**Business:** {p.get('business_name') or '—'}  
**Industry:** {industry_disp}  
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
        if a.get("third_parties") == "Yes" and a.get("breach_contact") == "Not really sure":
            blindspots.append("No partner-breach playbook — clarify contacts and escalation.")
        if a.get("confidence") in ["Not at all","Somewhat"]:
            blindspots.append("Low confidence — training and basic controls will lift resilience quickly.")
        if not blindspots:
            blindspots.append("Solid baseline. Next, validate backups, MFA, and incident basics.")
        for b in blindspots: st.markdown(f"- {b}")

    st.info("Next: Cybersecurity Posture (controls like MFA, backups, patching, awareness, incident response).")
    if st.button("→ Continue to Cybersecurity Posture", type="primary"):
        st.session_state.stage = "cyber_qa"; st.session_state.cyber_idx = 0; st.rerun()

# =========================================================
# Stage 2: Cybersecurity Posture – Wizard
# =========================================================
if st.session_state.stage == "cyber_qa":
    i = st.session_state.cyber_idx
    q = CYBER_QUESTIONS[i]
    st.markdown(f'<div class="progress-head">Cybersecurity Posture • {q["domain"]} • Step {i+1} of {CYBER_TOTAL}</div>', unsafe_allow_html=True)
    st.progress(i/CYBER_TOTAL)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="qtitle">{q["text"]}</div>', unsafe_allow_html=True)
    if q.get("tip"):
        with st.expander("Why this matters"):
            st.markdown(q["tip"])

    curr = st.session_state.cyber_answers.get(q["id"], "— Select one —")
    answer = st.radio("Select one:", q["choices"], index=q["choices"].index(curr) if curr in q["choices"] else 0, key=f"cy_radio_{q['id']}")
    st.session_state.cyber_answers[q["id"]] = answer
    st.markdown('</div>', unsafe_allow_html=True)

    col_prev, col_skip, col_next = st.columns([1,1,1])
    with col_prev:
        st.button("← Back", use_container_width=True, disabled=(i==0),
                  on_click=lambda: st.session_state.update(cyber_idx=max(i-1,0)))
    with col_skip:
        if st.button("Skip", use_container_width=True):
            st.session_state.cyber_idx = min(i+1, CYBER_TOTAL-1)
            if st.session_state.cyber_idx == CYBER_TOTAL-1 and i == CYBER_TOTAL-1:
                st.session_state.stage = "cyber_results"
            st.rerun()
    with col_next:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state.cyber_idx = i + 1
            if st.session_state.cyber_idx >= CYBER_TOTAL:
                st.session_state.stage = "cyber_results"
            st.rerun()

# =========================================================
# Stage 2: Results – Traffic Lights + Action Cards
# =========================================================
if st.session_state.stage == "cyber_results":
    st.success("Cybersecurity Posture assessment complete.")
    scores = compute_domain_scores(st.session_state.cyber_answers)
    overall = overall_score(scores)

    def badge(colour, text):
        return f'<span class="badge {colour}">{text}</span>'

    st.markdown('<div class="kpi">', unsafe_allow_html=True)
    st.markdown(f"#### Overall posture: {badge(overall['colour'], overall['label'])}  •  **{overall['score']}%**", unsafe_allow_html=True)
    st.caption("Scores reflect practical control coverage and are intended to guide priorities, not replace audits.")
    st.markdown('</div>', unsafe_allow_html=True)

    dcols = st.columns(3)
    doms = list(scores.items())
    for idx, (dom, data) in enumerate(doms):
        with dcols[idx % 3]:
            st.markdown('<div class="kpi">', unsafe_allow_html=True)
            st.markdown(f"**{dom}**")
            st.markdown(f"{badge(data['colour'], data['label'])} • **{data['score']}%**", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    good, fixes = add_action_cards(st.session_state.answers, st.session_state.cyber_answers)
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### ✅ What you’re doing well")
        if good:
            st.markdown("<ul class='tight'>" + "".join([f"<li>{g}</li>" for g in good]) + "</ul>", unsafe_allow_html=True)
        else:
            st.write("We didn’t detect specific strengths yet — once you implement the fixes below, this list will grow.")
    with colB:
        st.markdown("### 🛠 Top recommended fixes")
        if fixes:
            st.markdown("<ul class='tight'>" + "".join([f"<li>{f}</li>" for f in fixes]) + "</ul>", unsafe_allow_html=True)
        else:
            st.write("Great baseline! Keep policies current and review quarterly.")

    st.markdown("---")
    st.info("Tip: capture this page as PDF for your records (export coming soon).")

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("← Review answers"):
            st.session_state.stage = "cyber_qa"; st.session_state.cyber_idx = 0; st.rerun()
    with c2:
        if st.button("Restart whole assessment"):
            reset_all(); st.rerun()
