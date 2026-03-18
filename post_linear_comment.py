#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post experiment results comment to Linear issue."""
import os
import sys
import requests


def post_comment(issue_id: str, comment_body: str) -> dict:
    """Post a comment to a Linear issue."""
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise ValueError("LINEAR_API_KEY environment variable not set")

    mutation = """
    mutation CommentCreate($issueId: String!, $body: String!) {
        commentCreate(input: {
            issueId: $issueId
            body: $body
        }) {
            success
            comment {
                id
                body
                createdAt
            }
        }
    }
    """

    variables = {
        "issueId": issue_id,
        "body": comment_body
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json"
        },
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["commentCreate"]["success"]:
        raise ValueError("Comment creation failed")

    return data["data"]["commentCreate"]["comment"]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python post_linear_comment.py <issue_id> <comment_body>")
        sys.exit(1)

    issue_id = sys.argv[1]
    comment_body = sys.argv[2]

    try:
        result = post_comment(issue_id, comment_body)
        print(f"Comment posted successfully: {result['id']}")
    except Exception as e:
        print(f"Error posting comment: {e}", file=sys.stderr)
        sys.exit(1)
