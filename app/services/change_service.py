import uuid
from app.graph.build_graph import build_graph, route_from_supervisor

graph = build_graph()

NAMES = {
    "extractor": "Extractor", "rag": "RAG Retriever", "supervisor": "Supervisor (Judge)",
    "security": "Security Agent", "test_impact": "Test Impact Agent",
    "code_search": "Code Search Agent", "report": "Report Builder",
}
NEXT_AFTER = {
    "extractor": "rag", "rag": "supervisor", "security": "supervisor",
    "test_impact": "supervisor", "code_search": "supervisor",
}


def stream_analysis(change_request: str):
    """Yields an event after every finished step, saying which step runs next."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    state = {"change_request": change_request, "retrieved_context": [], "next_agent": "", "execution_log": []}

    log, report = [], ""
    for chunk in graph.stream(state, config=config, stream_mode="updates"):
        for node, update in chunk.items():
            new_entries = update["execution_log"][len(log):]
            log.extend(new_entries)
            if node == "report":
                report = update["risk_report"]
            next_node = route_from_supervisor(update) if node == "supervisor" else NEXT_AFTER.get(node)
            yield {"type": "step", "entries": new_entries, "next": NAMES.get(next_node)}
    yield {"type": "done", "risk_report": report, "execution_log": log}