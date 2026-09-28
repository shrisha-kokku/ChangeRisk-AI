import uuid
from langgraph.types import Command
from app.graph.build_graph import build_graph, route_from_supervisor

graph = build_graph()

NAMES = {
    "extractor": "Extractor", "rag": "RAG Retriever", "supervisor": "Supervisor (Judge)",
    "security": "Security Agent", "test_impact": "Test Impact Agent",
    "code_search": "Code Search Agent", "report": "Report Builder", "hitl": "Human Approval",
}
NEXT_AFTER = {
    "extractor": "rag", "rag": "supervisor", "security": "supervisor",
    "test_impact": "supervisor", "code_search": "supervisor", "report": "hitl",
}

def start_analysis(change_request: str) -> dict:
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"change_request": change_request, "retrieved_context": [], "next_agent": "", "execution_log": []},
        config=config
    )
    interrupt_data = result["__interrupt__"][0].value
    return {
        "thread_id": thread_id,
        "risk_report": interrupt_data["report"],
        "question": interrupt_data["question"],
        "execution_log": result.get("execution_log", [])
    }

def submit_approval(thread_id: str, approved: bool) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(Command(resume=approved), config=config)   # FIXED
    return {
        "status": "approved" if approved else "rejected",
        "execution_log": result.get("execution_log", [])
    }


def stream_analysis(change_request: str):
    """Yields an event after every finished step, saying which step runs next."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    state = {"change_request": change_request, "retrieved_context": [], "next_agent": "", "execution_log": []}
    yield {"type": "start", "thread_id": thread_id}

    log = []
    for chunk in graph.stream(state, config=config, stream_mode="updates"):
        for node, update in chunk.items():
            if node == "__interrupt__":          # graph paused for human approval
                data = update[0].value
                log.append({"step": "Human Approval", "detail": "Paused - waiting for developer decision"})
                yield {"type": "done", "risk_report": data["report"], "execution_log": log}
            else:
                new_entries = update["execution_log"][len(log):]
                log.extend(new_entries)
                next_node = route_from_supervisor(update) if node == "supervisor" else NEXT_AFTER.get(node)
                yield {"type": "step", "entries": new_entries, "next": NAMES.get(next_node)}