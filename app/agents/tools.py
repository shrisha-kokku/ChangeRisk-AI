import os
from langchain_core.tools import tool
from app.mcp.github_client import call_github_tool


def _owner_repo() -> tuple[str, str]:
    owner, repo = os.getenv("GITHUB_REPO").split("/")
    return owner, repo


@tool
def search_issues(query: str) -> str:
    """Search existing GitHub issues. Use this before creating an issue, to check for duplicates."""
    owner, repo = _owner_repo()
    return call_github_tool("search_issues", {"query": query, "owner": owner, "repo": repo})


@tool
def create_issue(title: str, body: str, labels: list[str]) -> str:
    """Create a new GitHub issue. Only use it when no similar issue exists. Labels example: ["security"]."""
    owner, repo = _owner_repo()
    return call_github_tool("issue_write", {
        "method": "create", "owner": owner, "repo": repo,
        "title": title, "body": body, "labels": labels,
    })


@tool
def add_comment(issue_number: int, body: str) -> str:
    """Add a comment to an existing GitHub issue, for example to add new findings."""
    owner, repo = _owner_repo()
    return call_github_tool("add_issue_comment", {
        "owner": owner, "repo": repo, "issue_number": issue_number, "body": body,
    })


READ_TOOLS = [search_issues]
WRITE_TOOLS = [create_issue, add_comment]
TOOLS_BY_NAME = {t.name: t for t in READ_TOOLS + WRITE_TOOLS}