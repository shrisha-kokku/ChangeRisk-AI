from app.graph.state import ChangeRiskState
from app.graph.nodes import log_step
from app.llm.groq_client import get_llm

def supervisor_node(state: ChangeRiskState) -> ChangeRiskState:
    """Judge: looks at what's known so far and decides which specialist runs next."""
    if state.get("security_findings") and state.get("test_impact_findings") and state.get("code_findings"):
        state["next_agent"] = "report"     # all specialists are done, no need to ask the LLM
        log_step(state, "Supervisor (Judge)", "Decided next specialist: report")
        return state
    llm = get_llm()
    prompt = f"""You are a supervisor deciding which specialist to consult next.
Specialists: security, test_impact, code_search.
Pick ONE not yet consulted, or say "report" if enough is known.

Change: {state['change_request']}
Security so far: {state.get('security_findings') or 'none'}
Test impact so far: {state.get('test_impact_findings') or 'none'}
Code findings so far: {state.get('code_findings') or 'none'}

Reply with exactly one word: security, test_impact, code_search, or report."""
    state["next_agent"] = llm.invoke(prompt).content.strip().lower()
    log_step(state, "Supervisor (Judge)", f"Decided next specialist: {state['next_agent']}")
    return state