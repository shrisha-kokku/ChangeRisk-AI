import uuid
from langgraph.types import Command
from app.graph.build_graph import build_graph

graph = build_graph()

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