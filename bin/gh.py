#!/usr/bin/env python3
"""GitHub REST API CLI using the stored custom.github credential.

Usage:
    gh.py user
    gh.py create-repo --name <name> [--private]
    gh.py upload --repo <owner/repo> --path <repo-path> --file <local-file> [--message <msg>]

Auth goes through the authd surrogate exchange (never touches a raw key).
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
)

API = "https://api.github.com"
ALLOWED_HOSTS = ["api.github.com"]
CREDENTIAL = "custom.github"


def api(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(
        req, CREDENTIAL, entry_name="access_token", allowed_hosts=ALLOWED_HOSTS
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = "<unreadable>"
        raise SystemExit(f"GitHub HTTP {exc.code}: {detail[:2000]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("user", help="Show authenticated user")

    p = sub.add_parser("create-repo", help="Create a new repository")
    p.add_argument("--name", required=True)
    p.add_argument("--private", action="store_true")
    p.add_argument("--description", default="Media hosting for @volumarc social posts")

    p = sub.add_parser("upload", help="Upload a file to a repo")
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--path", required=True, help="path inside the repo")
    p.add_argument("--file", required=True, help="local file to upload")
    p.add_argument("--message", default="Add media file")

    args = parser.parse_args()

    if args.cmd == "user":
        result = api("GET", "/user")
        print(json.dumps(
            {"login": result.get("login"), "id": result.get("id")},
            indent=2,
        ))
    elif args.cmd == "create-repo":
        result = api("POST", "/user/repos", {
            "name": args.name,
            "private": args.private,
            "description": args.description,
            "auto_init": True,
        })
        print(json.dumps(
            {"full_name": result.get("full_name"),
             "html_url": result.get("html_url"),
             "default_branch": result.get("default_branch")},
            indent=2,
        ))
    elif args.cmd == "upload":
        with open(args.file, "rb") as fh:
            content = base64.b64encode(fh.read()).decode("ascii")
        result = api("PUT", f"/repos/{args.repo}/contents/{args.path}", {
            "message": args.message,
            "content": content,
        })
        dl = (result.get("content") or {}).get("download_url")
        print(json.dumps({"download_url": dl}, indent=2))


if __name__ == "__main__":
    main()
