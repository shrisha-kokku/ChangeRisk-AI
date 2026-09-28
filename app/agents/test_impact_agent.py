from app.graph.state import ChangeRiskState
from app.graph.nodes import log_step
from app.llm.groq_client import get_llm

def test_impact_agent(state: ChangeRiskState) -> ChangeRiskState:
    """Identifies what tests are needed/affected by this change."""
    llm = get_llm()
    context = "\n".join(state["retrieved_context"])
    prompt = f"""You are a QA engineer. Given this change request and context,
list what tests are required or affected. Be concise.

Change: {state['change_request']}
Context: {context}"""
    response = llm.invoke(prompt)
    state["test_impact_findings"] = response.content
    log_step(state, "Test Impact Agent", "Completed test impact review")
    return state