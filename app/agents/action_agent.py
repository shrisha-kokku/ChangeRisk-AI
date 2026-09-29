from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.types import interrupt

from app.llm.groq_client import get_llm
from app.agents.tools import READ_TOOLS, WRITE_TOOLS, TOOLS_BY_NAME

WRITE_NAMES = {t.name for t in WRITE_TOOLS}

SYSTEM_PROMPT = """You help a developer act on a risk report.
You have tools to search, create, and comment on GitHub issues.

Always search for existing issues before creating one.
Treat an existing issue as a duplicate if it is about the same underlying change request,
even if its conclusion or details differ. In that case, comment on the existing issue
with the new findings instead of creating a new issue. Only create a new issue if
search finds nothing related to this change request at all.
Call only one tool at a time.

Risk report:
{report}"""


def agent_node(state: MessagesState):
    """The LLM reads the conversation and either answers or asks for a tool."""
    llm = get_llm().bind_tools(READ_TOOLS + WRITE_TOOLS)
    return {"messages": [llm.invoke(state["messages"])]}


def tool_node(state: MessagesState):
    """Runs the requested tool. Write tools pause for human approval (with editable args) first."""
    calls = state["messages"][-1].tool_calls
    results = []
    for index, call in enumerate(calls):
        name, args = call["name"], call["args"]
        if index > 0:
            # one tool per turn, so a resumed approval can never repeat an earlier action
            output = "Skipped. Call only one tool at a time."
        elif name in WRITE_NAMES:
            decision = interrupt({"tool": name, "args": args})   # the UI shows editable fields
            if decision["approved"]:
                output = TOOLS_BY_NAME[name].invoke(decision["args"])   # runs with the user's edits
            else:
                output = "The user rejected this action."
        else:
            output = TOOLS_BY_NAME[name].invoke(args)
        results.append(ToolMessage(content=output, tool_call_id=call["id"], name=name))
    return {"messages": results}


def route_after_agent(state: MessagesState) -> str:
    """If the LLM asked for a tool, run it. Otherwise the turn is finished."""
    return "tools" if state["messages"][-1].tool_calls else END


def build_action_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")   # after a tool runs, the LLM sees the result
    return graph.compile(checkpointer=MemorySaver())