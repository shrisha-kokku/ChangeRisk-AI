import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ChangeRisk AI", layout="centered")

st.markdown("""
<style>
.trace-step {
    padding: 10px 14px;
    border-left: 3px solid #4f8cff;
    margin-bottom: 8px;
    background-color: #161a23;
    border-radius: 4px;
}
.trace-step-name { font-weight: 600; color: #4f8cff; }
.trace-step-detail { color: #b0b8c4; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

st.title("ChangeRisk AI")
st.caption("Multi-agent system for software change impact and risk analysis")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
    st.session_state.risk_report = None
    st.session_state.execution_log = []
    st.session_state.resolved = False

change_request = st.text_area(
    "Describe the change you want to make", height=100,
    placeholder="e.g. I want to add UPI refund functionality to my payment system"
)

if st.button("Analyze Change", type="primary"):
    with st.spinner("Running analysis..."):
        response = requests.post(f"{API_URL}/analyze-change", json={"change_request": change_request})
        data = response.json()
        st.session_state.thread_id = data["thread_id"]
        st.session_state.risk_report = data["risk_report"]
        st.session_state.execution_log = data["execution_log"]
        st.session_state.resolved = False

if st.session_state.risk_report:
    st.subheader("Risk Report")
    st.write(st.session_state.risk_report)

    st.subheader("Agent Execution Trace")
    for step in st.session_state.execution_log:
        st.markdown(
            f'<div class="trace-step"><div class="trace-step-name">{step["step"]}</div>'
            f'<div class="trace-step-detail">{step["detail"]}</div></div>',
            unsafe_allow_html=True
        )

    if not st.session_state.resolved:
        st.subheader("Approval Required")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve — File GitHub Issue"):
                r = requests.post(f"{API_URL}/approve", json={"thread_id": st.session_state.thread_id, "approved": True})
                st.session_state.execution_log = r.json()["execution_log"]
                st.session_state.resolved = True
                st.success("Approved. GitHub issue filed.")
        with col2:
            if st.button("Reject"):
                r = requests.post(f"{API_URL}/approve", json={"thread_id": st.session_state.thread_id, "approved": False})
                st.session_state.execution_log = r.json()["execution_log"]
                st.session_state.resolved = True
                st.info("Rejected. No action taken.")