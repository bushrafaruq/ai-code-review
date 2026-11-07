"""Post or update the review comment on a GitHub pull request (standard library only).

One comment per PR, identified by a hidden marker, is updated on every push instead of adding
a new comment each time.
"""

from __future__ import annotations

import json
import os
import urllib.request

from .render import MARKER

API = os.getenv("GITHUB_API_URL", "https://api.github.com")


def _req(method: str, url: str, token: str, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def upsert_comment(repo: str, pr: int, body: str, token: str | None = None) -> str:
    token = token or os.environ["GITHUB_TOKEN"]
    comments = _req("GET", f"{API}/repos/{repo}/issues/{pr}/comments?per_page=100", token)
    existing = next((c for c in comments if MARKER in (c.get("body") or "")), None)
    if existing:
        _req("PATCH", f"{API}/repos/{repo}/issues/comments/{existing['id']}", token, {"body": body})
        return f"updated comment {existing['id']}"
    c = _req("POST", f"{API}/repos/{repo}/issues/{pr}/comments", token, {"body": body})
    return f"created comment {c['id']}"
