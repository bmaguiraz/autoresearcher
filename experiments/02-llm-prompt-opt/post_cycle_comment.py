#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post cycle comments to Linear issue."""
import os
import sys
import requests


def post_comment(issue_id: str, body: str, api_key: str):
    """Post a comment to a Linear issue."""
    mutation = """
    mutation CreateComment($issueId: String!, $body: String!) {
        commentCreate(input: {
            issueId: $issueId
            body: $body
        }) {
            success
            comment {
                id
                createdAt
            }
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": {"issueId": issue_id, "body": body}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["commentCreate"]["success"]:
        raise ValueError("Comment creation failed")

    return data["data"]["commentCreate"]["comment"]


if __name__ == "__main__":
    issue_id = sys.argv[1]
    body = sys.stdin.read()
    api_key = os.getenv("LINEAR_API_KEY")

    if not api_key:
        print("Error: LINEAR_API_KEY not set")
        sys.exit(1)

    comment = post_comment(issue_id, body, api_key)
    print(f"Posted comment ID: {comment['id']}")
