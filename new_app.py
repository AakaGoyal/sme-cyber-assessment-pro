import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="SME Cyber Self-Assessment – Pro",
    page_icon="🛡️",
    layout="wide"
)

st.title("SME Cyber Self-Assessment – Pro")
st.caption("A separate deployment from your core SME app")

RESPONSES_FILE = "responses_pro.csv"  # distinct storage target

@st.cache_data(ttl=3600, show_spinner=False)
def load_questions():
    return [
        {"id": "biz_size", "q": "How many employees do you have?"},
        {"id": "it_owner", "q": "Do you manage IT in-house or via MSP?"},
        {"id": "asset_inv", "q": "Do you keep an asset inventory?"},
        {"id": "backups", "q": "Are verified backups performed at least weekly?"},
        {"id": "mfa", "q": "Is MFA enforced for email/admin access?"},
    ]

qs = load_questions()
answers = {}
cols = st.columns(2)
for i, item in enumerate(qs):
    with cols[i % 2]:
        if item["id"] == "biz_size":
            answers[item["id"]] = st.selectbox(item["q"], ["1–9","10–49","50–249","250+"])
        elif item["id"] in {"mfa","backups","asset_inv"}:
            answers[item["id"]] = st.selectbox(item["q"], ["Yes","No","Planned"])
        else:
            answers[item["id"]] = st.selectbox(item["q"], ["In-house","MSP","Hybrid"])

if st.button("Submit"):
    row = {"ts": datetime.utcnow().isoformat(timespec="seconds"), **answers}
    try:
        try:
            df = pd.read_csv(RESPONSES_FILE)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame([row])
        df.to_csv(RESPONSES_FILE, index=False)
        st.success("Submitted ✅")
    except Exception as e:
        st.error(f"Save failed: {e}")

with st.expander("Preview stored responses (demo)"):
    try:
        st.dataframe(pd.read_csv(RESPONSES_FILE).tail(50))
    except FileNotFoundError:
        st.info("No submissions yet.")
