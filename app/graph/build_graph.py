from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import ChangeRiskState
from app.graph.nodes import extractor_node, rag_node, report_node, hitl_node
from app.agents.supervisor import supervisor_node
from app.agents.security_agent import security_agent
from app.agents.test_impact_agent import test_impact_agent
from app.agents.code_search_agent import code_search_agent

def route_from_supervisor(state: ChangeRiskState) -> str:
    """Reads the judge's decision and sends the state to that node next."""
    ran_all = all([state.get("security_findings"), state.get("test_impact_findings"), state.get("code_findings")])
    if ran_all:
        return "report"  # safety net: never loop forever
    return state["next_agent"] if state["next_agent"] in ("security", "test_impact", "code_search") else "report"

def build_graph():
    graph = StateGraph(ChangeRiskState)

    graph.add_node("extractor", extractor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("security", security_agent)
    graph.add_node("test_impact", test_impact_agent)
    graph.add_node("code_search", code_search_agent)
    graph.add_node("report", report_node)
    graph.add_node("hitl", hitl_node)

    graph.set_entry_point("extractor")
    graph.add_edge("extractor", "rag")
    graph.add_edge("rag", "supervisor")

    graph.add_conditional_edges("supervisor", route_from_supervisor, {
        "security": "security", "test_impact": "test_impact",
        "code_search": "code_search", "report": "report"
    })
    # each agent loops back to the supervisor so it can pick the next one
    graph.add_edge("security", "supervisor")
    graph.add_edge("test_impact", "supervisor")
    graph.add_edge("code_search", "supervisor")

    graph.add_edge("report", "hitl")
    graph.add_edge("hitl", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)