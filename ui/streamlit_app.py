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
DEFAULTS = {"trace": [], "risk_report": None, "chat": [], "chat_thread_id": None, "pending": None}
for key, default in DEFAULTS.items():
    st.session_state.setdefault(key, default)


def show_trace(steps):
    """One bordered card per analysis step."""
    for step in steps:
        with st.container(border=True):
            st.markdown(f"**{step['step']}**")
            st.caption(step["detail"])


def show_item(item):
    """Shows one chat entry: a user message, an agent message, or a tool call/result card."""
    if item["kind"] == "user":
        st.chat_message("user").write(item["text"])
    elif item["kind"] == "agent":
        st.chat_message("assistant").write(item["text"])
    else:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            st.caption(item["text"])


def to_item(event):
    """Converts a backend event into a chat entry."""
    if event["type"] == "message":
        return {"kind": "agent", "text": event["text"]}
    if event["type"] == "tool_call":
        return {"kind": "tool", "title": f"Tool call: {event['name']}", "text": json.dumps(event["args"], ensure_ascii=False)}
    if event["type"] == "tool_result":
        return {"kind": "tool", "title": f"Tool result: {event['name']}", "text": event["output"]}
    return None


def run_analysis(change_request):
    """Reads the live analysis stream and shows each agent as it works."""
    st.session_state.update(risk_report=None, trace=[], chat=[], chat_thread_id=None, pending=None)
    with st.status("Running: Extractor", expanded=True) as status:
        url = f"{API_URL}/analyze-change/stream"
        with requests.post(url, json={"change_request": change_request}, stream=True, timeout=300) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                if event["type"] == "step":
                    show_trace(event["entries"])
                    if event["next"]:
                        status.update(label=f"Running: {event['next']}")
                elif event["type"] == "done":
                    st.session_state.risk_report = event["risk_report"]
                    st.session_state.trace = event["execution_log"]
                    status.update(label="Analysis complete", state="complete")
    st.rerun()


def run_agent_stream(path, payload):
    """Reads the action agent's live stream: every tool call, result, and message."""
    with st.status("Agent is working...", expanded=True) as status:
        with requests.post(f"{API_URL}{path}", json=payload, stream=True, timeout=300) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                if event["type"] == "start":
                    st.session_state.chat_thread_id = event["thread_id"]
                elif event["type"] == "approval":
                    st.session_state.pending = {"tool": event["tool"], "args": event["args"]}
                else:
                    item = to_item(event)
                    if item:
                        st.session_state.chat.append(item)
                        show_item(item)
        status.update(label="Agent finished", state="complete")
    st.rerun()


def send_decision(approved, args):
    """Sends the human's decision (with any edits) back to the paused agent."""
    st.session_state.pending = None
    run_agent_stream("/decision", {
        "thread_id": st.session_state.chat_thread_id, "approved": approved, "args": args,
    })


def show_approval():
    """Editable form for the write action the agent wants to run."""
    pending = st.session_state.pending
    args = pending["args"]
    st.subheader("Approval Required")
    st.caption(f"The agent wants to run: {pending['tool']}. Edit anything below, then approve.")

    edited = {}
    if pending["tool"] == "create_issue":
        edited["title"] = st.text_input("Title", args.get("title", ""))
        edited["body"] = st.text_area("Body", args.get("body", ""), height=260)
        labels = st.text_input("Labels (comma separated)", ", ".join(args.get("labels") or []))
        edited["labels"] = [label.strip() for label in labels.split(",") if label.strip()]
    else:  # add_comment
        edited["issue_number"] = int(st.number_input("Issue number", min_value=1, value=int(args.get("issue_number", 1)), step=1))
        edited["body"] = st.text_area("Comment", args.get("body", ""), height=260)

    approve_col, reject_col, _ = st.columns([1, 1, 4])
    if approve_col.button("Approve", key="approve"):
        send_decision(True, edited)
    if reject_col.button("Reject", key="reject"):
        send_decision(False, args)


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

    st.subheader("Action Agent")
    st.caption("Tell the agent what to do with this report. Anything it wants to create or post is shown for your approval first.")
    for chat_item in st.session_state.chat:
        show_item(chat_item)

    if st.session_state.pending:
        show_approval()
    else:
        prompt = st.chat_input("e.g. File this as an issue")
        if prompt:
            user_item = {"kind": "user", "text": prompt}
            st.session_state.chat.append(user_item)
            show_item(user_item)
            run_agent_stream("/chat", {
                "message": prompt,
                "report": st.session_state.risk_report,
                "thread_id": st.session_state.chat_thread_id,
            })