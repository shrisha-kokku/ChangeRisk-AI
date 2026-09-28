import uuid
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from app.agents.action_agent import build_action_graph, SYSTEM_PROMPT

action_graph = build_action_graph()


def _events(stream):
    """Converts raw graph updates into simple events for the UI."""
    for chunk in stream:
        for node, update in chunk.items():
            if node == "__interrupt__":                       # a write tool is waiting for approval
                yield {"type": "approval", **update[0].value}
            elif node == "agent":
                message = update["messages"][-1]
                if message.content:
                    yield {"type": "message", "text": message.content}
                for call in message.tool_calls:
                    yield {"type": "tool_call", "name": call["name"], "args": call["args"]}
            elif node == "tools":
                for message in update["messages"]:
                    yield {"type": "tool_result", "name": message.name, "output": message.content[:500]}


def stream_chat(user_message: str, report: str, thread_id: str | None = None):
    """Starts a new chat (first message) or continues one (same thread_id)."""
    is_new = thread_id is None
    thread_id = thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    messages = [HumanMessage(user_message)]
    if is_new:
        messages.insert(0, SystemMessage(SYSTEM_PROMPT.format(report=report)))
    yield {"type": "start", "thread_id": thread_id}
    yield from _events(action_graph.stream({"messages": messages}, config=config, stream_mode="updates"))


def stream_decision(thread_id: str, approved: bool, args: dict):
    """Resumes the paused agent with the human's decision and their edited arguments."""
    config = {"configurable": {"thread_id": thread_id}}
    resume = Command(resume={"approved": approved, "args": args})
    yield from _events(action_graph.stream(resume, config=config, stream_mode="updates"))