#!/usr/bin/env python3
"""Buffer GraphQL API CLI using the stored custom.buffer credential.

Usage:
    buffer.py account
    buffer.py channels --org <organizationId>

Auth goes through the authd surrogate exchange (never touches a raw key).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
)

ENDPOINT = "https://api.buffer.com"
ALLOWED_HOSTS = ["api.buffer.com"]
CREDENTIAL = "custom.buffer"


def graphql(query: str, variables: dict | None = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(
        req, CREDENTIAL, entry_name="access_token", allowed_hosts=ALLOWED_HOSTS
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return read_json_response(resp)
    except urllib.error.HTTPError as exc:  # noqa: F821
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = "<unreadable>"
        raise SystemExit(f"HTTP {exc.code}: {body[:2000]}")


ACCOUNT_QUERY = """query {
  account {
    id
    email
    organizations {
      id
      name
    }
  }
}"""

CHANNELS_QUERY = """query($orgId: OrganizationId!) {
  channels(input: { organizationId: $orgId }) {
    id
    name
    displayName
    service
    serviceId
    type
    isDisconnected
  }
}"""

CREATE_POST_MUTATION = """mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess {
      post { id status dueAt channelService text }
    }
    ... on InvalidInputError { message }
    ... on LimitReachedError { message }
    ... on UnexpectedError { message }
    ... on UnauthorizedError { message }
    ... on NotFoundError { message }
  }
}"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Buffer GraphQL API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("account", help="Show account and organizations")
    p = sub.add_parser("channels", help="List connected channels for an org")
    p.add_argument("--org", required=True, help="Organization ID")
    p = sub.add_parser("create-post", help="Create/schedule a post")
    p.add_argument("--channel", required=True, help="Channel ID")
    p.add_argument("--text", required=True, help="Post caption text")
    p.add_argument("--video-url", required=True, help="Public video URL")
    p.add_argument("--due-at", required=True, help="ISO-8601 UTC, e.g. 2026-10-08T12:00:00Z")
    p.add_argument("--service", required=True, choices=["facebook", "instagram", "tiktok"],
                   help="Platform, used to set the reel type metadata")
    args = parser.parse_args()

    if args.cmd == "account":
        result = graphql(ACCOUNT_QUERY)
    elif args.cmd == "channels":
        result = graphql(CHANNELS_QUERY, {"orgId": args.org})
    elif args.cmd == "create-post":
        metadata: dict = {}
        if args.service == "facebook":
            metadata = {"facebook": {"type": "reel"}}
        elif args.service == "instagram":
            metadata = {"instagram": {"type": "reel", "isAiGenerated": True,
                                      "shouldShareToFeed": True}}
        elif args.service == "tiktok":
            metadata = {"tiktok": {"isAiGenerated": True}}
        result = graphql(CREATE_POST_MUTATION, {"input": {
            "channelId": args.channel,
            "text": args.text,
            "assets": [{"video": {"url": args.video_url}}],
            "mode": "customScheduled",
            "dueAt": args.due_at,
            "schedulingType": "automatic",
            "needsApproval": False,
            "metadata": metadata,
        }})

    if result.get("errors"):
        print(json.dumps(result["errors"], indent=2, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(result.get("data"), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
