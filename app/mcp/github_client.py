import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"

def _build_client() -> MultiServerMCPClient:
    """MCP client pointed at GitHub's official hosted MCP server."""
    return MultiServerMCPClient({
        "github": {
            "transport": "streamable_http",
            "url": GITHUB_MCP_URL,
            "headers": {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"},
        }
    })

async def _create_issue(title: str, body: str):
    client = _build_client()
    tools = await client.get_tools()                      # asks the server which tools it offers
    issue_tool = next((t for t in tools if t.name == "issue_write"), None)
    if issue_tool is None:
        raise RuntimeError("GitHub MCP server did not offer the issue_write tool")
    owner, repo = os.getenv("GITHUB_REPO").split("/")
    return await issue_tool.ainvoke({
        "method": "create", "owner": owner, "repo": repo, "title": title, "body": body,
    })

def create_issue_via_mcp(title: str, body: str):
    """Sync wrapper so our normal (non-async) graph node can call the MCP tool."""
    return asyncio.run(_create_issue(title, body))