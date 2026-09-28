from mcp.server.fastmcp import FastMCP
from app.mcp.github_tool import create_github_issue

mcp = FastMCP("changerisk-tools")

@mcp.tool()
def file_github_issue(title: str, body: str) -> dict:
    """MCP tool: files a GitHub issue for an approved change."""
    return create_github_issue(title, body)