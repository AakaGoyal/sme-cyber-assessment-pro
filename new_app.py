import streamlit as st
from typing import List, Dict, Any

# -----------------------------
# Page & Styles
# -----------------------------
st.set_page_config(
    page_title="SME Initial Assessment (Conversational)",
    page_icon="💬",
    layout="wide"
)

CUSTOM_CSS = """
<style>
/* Chat bubbles */
.stChatMessage[data-testid="stChatMessage"] .stMarkdown p {
  margin-bottom: 0.3rem;
}
.assistant-bubble {
  background: #f7f7fb;
  border: 1px solid #ececf5;
  padding: 12px 14px;
  border-radius: 14px;
}
.user-bubble {
  background: #e9f7ff;
  border: 1px solid #d7eefc;
  padding: 12px 14px;
  border-radius: 14px;
}
/* Cards */
.card {
  border: 1px solid #eaeaea;
  border-radius: 14px;
  padding: 16px;
  background: white;
}
.small {
  font-size: 0.9rem;
  color: #666;
}
/* Quick reply buttons */
.quick-btn > button {
  width: 100%;
  border-radius: 12px !important;
}
/* Progress label */
.progress-label {
  font-size: 0.9rem;
  color: #555;
  margin-top: 4px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
def ss_init():
    if "stage" not in st.session_state:
        # stage: "intake" -> "chat" -> (later) "done"
        st.session_state.stage = "intake"
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, Any]] = []
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "contact_name": "",
            "business_name": "",
            "industry": "",
            "years": "",
            "headcount": "",
            "turnover": "",
            "work_mode": ""
        }
    if "answers" not in st.session_state:
        st.session_state.answers: Dict[str, Any] = {}
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "asked_ids" not in st.session_state:
        st.session_state.asked_ids = set()

ss_init()

# -----------------------------
# Question Bank (Phase-driven)
# (Derived from the uploaded "Initial Assessment" phases)
# -----------------------------
QUESTIONS = [
    # Phase 1 – Understanding the Business
    {
        "id": "sell_online",
        "phase": "Digital Footprint",
        "text": "Do you sell products or deliver services online?",
        "type": "choice",
        "choices": [
            "Yes – on my own website",
            "Yes – via marketplaces (Amazon/Etsy)",
            "No – mostly offline"
        ],
        "tip": "This helps us understand your online exposure and dependencies."
    },
    {
        "id": "data_types",
        "phase": "Digital Footprint",
        "text": "Do you store customer or employee information (e.g., emails, invoices, payment info)?",
        "type": "choice",
        "choices": ["Yes", "No"],
        "tip": "Handling personal data increases your duty of care and regulatory exposure."
    },
    {
        "id": "tools_regular",
        "phase": "Digital Footprint",
        "text": "Which of these do you rely on daily? (pick all that apply in sequence)",
        "type": "multi",
        "choices": [
            "Email",
            "Accounting/finance software",
            "CRM or client database",
            "Cloud storage (Google Drive/OneDrive etc.)",
            "Online payment system",
            "Website or webshop"
        ],
        "tip": "This identifies where your critical information and daily operations live."
    },
    # Phase 3 – IT Ownership and Responsibility
    {
        "id": "website_owner",
        "phase": "IT Ownership",
        "text": "Who looks after your website and online systems?",
        "type": "choice",
        "choices": [
            "I do it myself",
            "Someone on my team",
            "An external company or freelancer"
        ]
    },
    {
        "id": "it_support",
        "phase": "IT Ownership",
        "text": "Who takes care of your computers, email and systems when something needs setup/fixing?",
        "type": "choice",
        "choices": [
            "I do",
            "A friend/freelancer",
            "An IT company",
            "In-house IT team"
        ]
    },
    {
        "id": "setup_by",
        "phase": "IT Ownership",
        "text": "Did you personally set up your main systems (email, website, backups)?",
        "type": "choice",
        "choices": [
            "Yes, mostly me",
            "Shared effort",
            "Someone else handled it"
        ]
    },
    {
        "id": "asset_list",
        "phase": "IT Ownership",
        "text": "Do you have a clear list of systems, accounts and devices you use?",
        "type": "choice",
        "choices": [
            "Yes, documented",
            "Rough idea",
            "Not really"
        ]
    },
    # Phase 4 – Partners & Ecosystem
    {
        "id": "third_parties",
        "phase": "Partners",
        "text": "Do you work with external partners who handle your data or systems (host, accountant, logistics, marketing tools)?",
        "type": "choice",
        "choices": ["Yes", "No"]
    },
    {
        "id": "partner_count",
        "phase": "Partners",
        "text": "How many key partners or providers do you rely on?",
        "type": "choice",
        "choices": ["0–2", "3–5", "6+"]
    },
    {
        "id": "breach_contact",
        "phase": "Partners",
        "text": "If a main partner had a breach, would you know who to contact and what to do?",
        "type": "choice",
        "choices": ["Yes – I know who to reach", "Not really sure"]
    },
    # Phase 5 – Confidence & Experience
    {
        "id": "confidence",
        "phase": "Confidence",
        "text": "How prepared would you feel if a cyberattack or data loss hit tomorrow?",
        "type": "choice",
        "choices": ["Not at all", "Somewhat", "Fairly confident", "Very confident"]
    },
    {
        "id": "past_incidents",
        "phase": "Confidence",
        "text": "Have you experienced a cybersecurity issue before (e.g., phishing, data loss, locked computer)?",
        "type": "choice",
        "choices": ["Yes", "No", "Not sure"]
    },
    {
        "id": "know_who_to_call",
        "phase": "Confidence",
        "text": "Do you know who to call or where to get help if something happened?",
        "type": "choice",
        "choices": ["Yes", "No"]
    },
]

TOTAL_Q = len(QUESTIONS)

# -----------------------------
# Helpers
# -----------------------------
def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def next_question_index(current: int) -> int:
    # Simple sequential flow with a bit of light branching:
    # - If user answered "No – mostly offline" to sell_online, we still continue normally.
    # - You can extend with deeper branching as needed.
    return min(current + 1, TOTAL_Q)

def friendly_intro(profile: Dict[str, str]) -> str:
    parts = []
    if profile.get("business_name"):
        parts.append(f"{profile['business_name']}")
    if profile.get("industry"):
        parts.append(profile["industry"])
    if profile.get("headcount"):
        parts.append(f"{profile['headcount']} people")
    base = " • ".join(parts) if parts else "your business"
    return (
        f"Great, thanks! I’ll tailor the questions to **{base}**. "
        f"We’ll keep it simple and practical—one step at a time."
    )

def phase_progress_label(idx: int) -> str:
    if idx >= TOTAL_Q:
        return "All questions completed"
    phase = QUESTIONS[idx]["phase"]
    return f"Now: {phase}"

def digital_dependency_score(ans: Dict[str, Any]) -> int:
    score = 0
    if ans.get("sell_online", "").startswith("Yes"):
        score += 2
    if ans.get("data_types") == "Yes":
        score += 1
    tools = ans.get("tools_regular", [])
    score += min(len(tools), 4)  # cap contribution
    return score  # 0–7 (rough guide)

# -----------------------------
# Sidebar Summary (live)
# -----------------------------
with st.sidebar:
    st.markdown("### Snapshot")
    st.caption("Auto-fills while you chat.")
    p = st.session_state.profile
    st.markdown(
        f"""
**Business:** {p.get('business_name') or '—'}  
**Industry:** {p.get('industry') or '—'}  
**People:** {p.get('headcount') or '—'}  
**Years:** {p.get('years') or '—'}  
**Turnover:** {p.get('turnover') or '—'}  
**Work mode:** {p.get('work_mode') or '—'}  
"""
    )
    dd = digital_dependency_score(st.session_state.answers)
    dd_text = "Low" if dd <= 2 else ("Medium" if dd <= 5 else "High")
    st.markdown("---")
    st.markdown("**Digital dependency (live):** " + dd_text)
    st.caption("Based on online sales, data handling, and daily tools.")

    if st.button("🔁 Restart", use_container_width=True):
        for k in ["stage", "messages", "profile", "answers", "q_index", "asked_ids"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

# -----------------------------
# Header
# -----------------------------
st.title("💬 Initial Assessment (Conversational)")
st.write(
    "We’ll start with a few basics, then move into a short, guided conversation. "
    "No jargon—just what matters."
)

# -----------------------------
# Stage 1 – Quick Intake Card
# -----------------------------
if st.session_state.stage == "intake":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("First, the basics (≈2 minutes)")
        col1, col2 = st.columns(2)
        with col1:
            contact_name = st.text_input("Your name", value=st.session_state.profile.get("contact_name", ""))
            business_name = st.text_input("Business name", value=st.session_state.profile.get("business_name", ""))
            industry = st.text_input("Industry / core service (e.g., retail, consulting, healthcare)")
        with col2:
            years = st.selectbox("How long in business?", ["<1 year","1–3 years","3–10 years","10+ years"])
            headcount = st.selectbox("How many people (incl. contractors)?", ["Just me","2–5","6–20","21–100","100+"])
            turnover = st.selectbox("Approx. annual turnover", ["<€100k","€100k–500k","€500k–2M",">€2M"])

        work_mode = st.radio("Would you describe your business as mostly…", ["Local & in-person","Online/remote","A mix of both"], horizontal=True)

        c1, c2 = st.columns([1, 2])
        with c1:
            proceed = st.button("Start the conversation →", use_container_width=True, type="primary")
        with c2:
            st.caption("We’ll use this to tailor the tone and next questions.")

        st.markdown('</div>', unsafe_allow_html=True)

        if proceed:
            st.session_state.profile.update({
                "contact_name": contact_name.strip(),
                "business_name": business_name.strip(),
                "industry": industry.strip(),
                "years": years,
                "headcount": headcount,
                "turnover": turnover,
                "work_mode": work_mode
            })
            # Seed assistant welcome & first question
            add_message("assistant", f"Hi {contact_name or 'there'} 👋")
            add_message("assistant", friendly_intro(st.session_state.profile))
            st.session_state.stage = "chat"
            st.session_state.q_index = 0
            st.rerun()

# -----------------------------
# Stage 2 – Conversational Chat
# -----------------------------
if st.session_state.stage == "chat":
    # Progress
    done_count = len(st.session_state.asked_ids)
    progress_val = done_count / TOTAL_Q
    st.progress(progress_val, text=phase_progress_label(st.session_state.q_index))
    st.markdown(f'<div class="progress-label">{done_count} / {TOTAL_Q} answered</div>', unsafe_allow_html=True)
    st.divider()

    # Render history
    for m in st.session_state.messages:
        with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
            st.markdown(
                f'<div class="{ "assistant-bubble" if m["role"]=="assistant" else "user-bubble"}">{m["content"]}</div>',
                unsafe_allow_html=True
            )

    # Ask current question if not asked
    if st.session_state.q_index < TOTAL_Q:
        q = QUESTIONS[st.session_state.q_index]

        # Only show the prompt once
        if q["id"] not in st.session_state.asked_ids:
            # Personalize the copy a bit
            prefix = ""
            if q["phase"] == "Digital Footprint" and st.session_state.profile.get("industry"):
                prefix = f"Given you’re in **{st.session_state.profile['industry']}**, "
            add_message("assistant", f"{prefix}{q['text']}")
            if q.get("tip"):
                add_message("assistant", f"_Tip: {q['tip']}_")
            st.session_state.asked_ids.add(q["id"])
            st.rerun()

        # Render input controls under the latest assistant message
        # Choices as quick buttons
        if q["type"] == "choice":
            cols = st.columns(3) if len(q["choices"]) <= 3 else st.columns(2)
            chosen = None
            # generate deterministic keys
            for i, choice in enumerate(q["choices"]):
                col = cols[i % len(cols)]
                with col:
                    if st.button(choice, key=f"{q['id']}_{i}", use_container_width=True):
                        chosen = choice
            if chosen:
                add_message("user", chosen)
                st.session_state.answers[q["id"]] = chosen
                st.session_state.q_index = next_question_index(st.session_state.q_index)
                st.rerun()

        elif q["type"] == "multi":
            # Sequential quick-pick experience
            st.caption("Click the options you use. Click “Done” when finished.")
            selected_list = st.session_state.answers.get(q["id"], [])
            # Lay out choices as buttons that toggle
            cols = st.columns(2)
            for i, choice in enumerate(q["choices"]):
                with cols[i % 2]:
                    key = f"{q['id']}_toggle_{i}"
                    active = choice in selected_list
                    label = ("✓ " if active else "") + choice
                    if st.button(label, key=key, use_container_width=True):
                        if active:
                            selected_list = [c for c in selected_list if c != choice]
                        else:
                            selected_list.append(choice)
                        st.session_state.answers[q["id"]] = selected_list
                        st.rerun()

            c_done, c_skip = st.columns([1,1])
            with c_done:
                if st.button("Done ✅", use_container_width=True, type="primary"):
                    user_msg = ", ".join(selected_list) if selected_list else "None selected"
                    add_message("user", user_msg)
                    st.session_state.q_index = next_question_index(st.session_state.q_index)
                    st.rerun()
            with c_skip:
                if st.button("Skip", use_container_width=True):
                    add_message("user", "Skipped")
                    st.session_state.answers[q["id"]] = []
                    st.session_state.q_index = next_question_index(st.session_state.q_index)
                    st.rerun()

        else:
            # Fallback: free text via chat_input
            prompt = st.chat_input("Type your answer…")
            if prompt:
                add_message("user", prompt)
                st.session_state.answers[q["id"]] = prompt
                st.session_state.q_index = next_question_index(st.session_state.q_index)
                st.rerun()

    else:
        # Completed
        st.success("Nice! You’ve completed the Initial Assessment.")
        # Friendly, contextual mini-summary
        p = st.session_state.profile
        a = st.session_state.answers
        dd = digital_dependency_score(a)
        dd_text = "Low" if dd <= 2 else ("Medium" if dd <= 5 else "High")

        st.markdown("#### Quick Summary")
        st.markdown(
            f"""
**Business:** {p.get('business_name') or '—'}  
**Industry:** {p.get('industry') or '—'}  
**People:** {p.get('headcount') or '—'} • **Years:** {p.get('years') or '—'} • **Turnover:** {p.get('turnover') or '—'}  
**Work mode:** {p.get('work_mode') or '—'}  

**Digital dependency (derived):** {dd_text}  
"""
        )

        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Highlights**")
            hl = []
            if a.get("sell_online","").startswith("Yes"):
                hl.append("Online sales increase reliance on website uptime and payment security.")
            if "Cloud storage (Google Drive/OneDrive etc.)" in a.get("tools_regular", []):
                hl.append("Cloud storage is central — access controls and backups matter.")
            if a.get("data_types") == "Yes":
                hl.append("You handle personal data — consider privacy and retention basics.")
            if not hl:
                hl.append("Operational footprint looks light; next step focuses on essential hygiene.")
            for h in hl:
                st.markdown(f"- {h}")

        with colB:
            st.markdown("**Potential blind spots**")
            bs = []
            if a.get("asset_list") in ["Rough idea", "Not really"]:
                bs.append("No clear list of systems/accounts — hard to secure what you can’t see.")
            if a.get("breach_contact") == "Not really sure":
                bs.append("No partner-breach playbook — clarify points of contact and escalation.")
            if a.get("confidence") in ["Not at all", "Somewhat"]:
                bs.append("Low confidence — training and basic controls will lift resilience quickly.")
            if not bs:
                bs.append("Solid baseline. Next, validate backups, MFA, and incident basics.")
            for b in bs:
                st.markdown(f"- {b}")

        st.info("Next: move to the Cybersecurity Posture questions (backups, MFA, device locks, training, response).")
        if st.button("→ Continue to Cybersecurity Posture", type="primary"):
            st.success("Great—this button would route to Stage 2 in your app.")
