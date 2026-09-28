from app.graph.state import ChangeRiskState
from app.graph.nodes import log_step
from app.llm.groq_client import get_llm

def security_agent(state: ChangeRiskState) -> ChangeRiskState:
    """Checks the change request + retrieved context for security concerns."""
    llm = get_llm()
    context = "\n".join(state["retrieved_context"])
    prompt = f"""You are a security reviewer. Given this change request and context,
list concrete security risks only. Be concise.

Change: {state['change_request']}
Context: {context}"""
    response = llm.invoke(prompt)
    state["security_findings"] = response.content
    log_step(state, "Security Agent", "Completed security review")
    return state