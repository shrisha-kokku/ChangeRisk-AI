import json
import os
from pathlib import Path

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
ROBOT_ICON = Path(__file__).parent / "static" / "robot.svg"

st.set_page_config(page_title="ChangeRisk AI", layout="centered")

# button colors: green for Approve, red for Reject
st.markdown("""
<style>
.st-key-approve button {background-color: #238636; border-color: #238636; width: 100%;}
.st-key-reject button {background-color: #da3633; border-color: #da3633; width: 100%;}
.st-key-approve button *, .st-key-reject button * {color: #ffffff !important;}
</style>
""", unsafe_allow_html=True)

# values that must survive button clicks
if "trace" not in st.session_state:
    st.session_state.update(thread_id=None, risk_report=None, trace=[], resolved=False, outcome=None)


def show_trace(steps):
    """One bordered card per agent step."""
    for step in steps:
        with st.container(border=True):
            st.markdown(f"**{step['step']}**")
            st.caption(step["detail"])


def run_analysis(change_request):
    """Reads the live stream from the backend and shows each agent as it works."""
    st.session_state.update(risk_report=None, trace=[], resolved=False, outcome=None)
    with st.status("Running: Extractor", expanded=True) as status:
        url = f"{API_URL}/analyze-change/stream"
        with requests.post(url, json={"change_request": change_request}, stream=True, timeout=300) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                if event["type"] == "start":
                    st.session_state.thread_id = event["thread_id"]
                elif event["type"] == "step":
                    show_trace(event["entries"])
                    status.update(label=f"Running: {event['next']}")   # the agent working right now
                elif event["type"] == "done":
                    st.session_state.risk_report = event["risk_report"]
                    st.session_state.trace = event["execution_log"]
                    status.update(label="Analysis complete", state="complete")
    st.rerun()   # redraw the page from saved state


def send_decision(approved):
    """Sends the human's approve/reject to the backend."""
    response = requests.post(
        f"{API_URL}/approve",
        json={"thread_id": st.session_state.thread_id, "approved": approved},
        timeout=120,
    )
    response.raise_for_status()
    st.session_state.trace.append(response.json()["execution_log"][-1])
    st.session_state.resolved = True
    st.session_state.outcome = "approved" if approved else "rejected"
    st.rerun()


# ---------- page ----------
icon_col, title_col = st.columns([1, 8], vertical_alignment="center")
icon_col.image(str(ROBOT_ICON), width=64)
title_col.title("ChangeRisk AI")
st.caption("Multi-agent system for software change impact and risk analysis")

change_request = st.text_area(
    "Describe the change you want to make", height=110,
    placeholder="e.g. I want to add UPI refund functionality to my payment system",
)

if st.button("Analyze Change", type="primary"):
    if change_request.strip():
        try:
            run_analysis(change_request)
        except requests.exceptions.RequestException:
            st.error("Cannot reach the backend. Make sure the FastAPI server is running.")
    else:
        st.warning("Please describe the change first.")

if st.session_state.trace:
    st.subheader("Agent Activity")
    show_trace(st.session_state.trace)

if st.session_state.risk_report:
    st.subheader("Risk Report")
    with st.container(border=True):
        st.markdown(st.session_state.risk_report)

    if st.session_state.resolved:
        if st.session_state.outcome == "approved":
            st.success("Approved. GitHub issue filed.")
        else:
            st.info("Rejected. No action was taken.")
    else:
        st.subheader("Approval Required")
        st.caption("Nothing is filed on GitHub until you approve.")
        approve_col, reject_col, _ = st.columns([1, 1, 4])
        if approve_col.button("Approve", key="approve"):
            send_decision(True)
        if reject_col.button("Reject", key="reject"):
            send_decision(False)