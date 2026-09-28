import requests
import os

def create_github_issue(title: str, body: str) -> dict:
    """Creates a GitHub issue using a free personal access token."""
    repo = os.getenv("GITHUB_REPO")  # e.g. "username/repo-name"
    token = os.getenv("GITHUB_TOKEN")  # free personal access token
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    response = requests.post(url, json={"title": title, "body": body}, headers=headers)
    return response.json()