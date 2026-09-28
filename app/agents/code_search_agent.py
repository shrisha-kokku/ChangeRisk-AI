from app.graph.state import ChangeRiskState
from app.graph.nodes import log_step
from app.llm.groq_client import get_llm

def code_search_agent(state: ChangeRiskState) -> ChangeRiskState:
    """Identifies which files/APIs would need to change."""
    llm = get_llm()
    context = "\n".join(state["retrieved_context"])
    prompt = f"""You are a senior engineer. Given this change request and context,
list which files/APIs likely need modification. Only name files that appear in the context. Mark files that don't exist yet as NEW. `Be concise.

Change: {state['change_request']}
Context: {context}"""
    response = llm.invoke(prompt)
    state["code_findings"] = response.content
    log_step(state, "Code Search Agent", "Identified affected files/APIs")
    return state