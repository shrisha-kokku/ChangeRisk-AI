from app.graph.state import ChangeRiskState
from app.rag.retriever import retrieve_context
from app.guardrails.validators import validate_report, enforce_policy_compliance

def log_step(state: ChangeRiskState, step_name: str, detail: str) -> None:
    """Records which step ran and what it did — this is what the UI displays."""
    state.setdefault("execution_log", []).append({"step": step_name, "detail": detail})

def extractor_node(state: ChangeRiskState) -> ChangeRiskState:
    state["change_request"] = state["change_request"].strip()
    log_step(state, "Extractor", "Cleaned and normalized the change request")
    return state

def rag_node(state: ChangeRiskState) -> ChangeRiskState:
    state["retrieved_context"] = retrieve_context(state["change_request"])
    log_step(state, "RAG Retriever", f"Retrieved {len(state['retrieved_context'])} relevant chunks")
    return state

def report_node(state: ChangeRiskState) -> ChangeRiskState:
    parts = []
    if state.get("security_findings"):
        parts.append(f"Security:\n{state['security_findings']}")
    if state.get("test_impact_findings"):
        parts.append(f"Tests:\n{state['test_impact_findings']}")
    if state.get("code_findings"):
        parts.append(f"Code/API changes:\n{state['code_findings']}")
    report = "\n\n".join(parts).replace("<br>", " ")

    if not validate_report(report, state["retrieved_context"]):
        report = "Report failed grounding check — insufficient evidence. Manual review required."
        log_step(state, "Guardrail", "Report failed grounding check")
    else:
        report = enforce_policy_compliance(report, state["retrieved_context"])
        log_step(state, "Guardrail", "Report checked against policies, no visible changes needed")

    state["risk_report"] = report
    log_step(state, "Report Builder", "Combined specialist findings into final report")
    return state

