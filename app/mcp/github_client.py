import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


async def _call(tool_name: str, arguments: dict) -> str:
    client = MultiServerMCPClient({
        "github": {
            "transport": "streamable_http",
            "url": GITHUB_MCP_URL,
            "headers": {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"},
        }
    })
    tools = await client.get_tools()                       # ask the server which tools it offers
    tool = next((t for t in tools if t.name == tool_name), None)
    if tool is None:
        raise RuntimeError(f"GitHub MCP server has no tool named {tool_name}")
    result = await tool.ainvoke(arguments)
    if isinstance(result, list):   # MCP returns content blocks; keep only the text
        return "\n".join(block["text"] for block in result if isinstance(block, dict) and "text" in block)
    return str(result)


def call_github_tool(tool_name: str, arguments: dict) -> str:
    """Sync wrapper so normal (non-async) code can call a GitHub MCP tool."""
    return asyncio.run(_call(tool_name, arguments))