#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post autoresearch cycle results to Linear issue as comments."""
import os
import sys
import requests


def post_comment_to_issue(issue_id: str, comment_body: str, api_key: str) -> dict:
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


def format_cycle_comment(
    cycle: int,
    commit: str,
    accuracy: float,
    correct: int,
    total: int,
    cost_cents: float,
    eval_seconds: float,
    prompt_config: str,
    status: str,
    description: str
) -> str:
    """Format cycle results as markdown comment with collapsible prompt config."""

    # Determine emoji based on status
    emoji = "✅" if status == "keep" else "🔄"
    if cycle == 0:
        emoji = "📊"  # baseline

    comment = f"""## {emoji} Cycle {cycle} Complete

### Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | `{accuracy:.3f}` ({correct}/{total}) |
| **Cost** | `{cost_cents:.1f}¢` |
| **Eval Time** | `{eval_seconds:.1f}s` |
| **Commit** | `{commit}` |
| **Status** | `{status}` |

**Description:** {description}

<details>
<summary>📝 <code>prompt.py</code> Configuration</summary>

```python
{prompt_config}
```

</details>
"""
    return comment


def main():
    if len(sys.argv) < 9:
        print("Usage: post_cycle_to_linear.py <cycle> <commit> <accuracy> <correct> <total> <cost_cents> <eval_seconds> <status> <description>")
        return 1

    cycle = int(sys.argv[1])
    commit = sys.argv[2]
    accuracy = float(sys.argv[3])
    correct = int(sys.argv[4])
    total = int(sys.argv[5])
    cost_cents = float(sys.argv[6])
    eval_seconds = float(sys.argv[7])
    status = sys.argv[8]
    description = " ".join(sys.argv[9:]) if len(sys.argv) > 9 else ""

    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    issue_id = os.getenv("LINEAR_ISSUE_ID")
    if not issue_id:
        print("Error: LINEAR_ISSUE_ID environment variable not set")
        return 1

    # Read current prompt.py
    try:
        with open("prompt.py", "r") as f:
            prompt_config = f.read()
    except FileNotFoundError:
        print("Error: prompt.py not found")
        return 1

    # Format and post comment
    comment_body = format_cycle_comment(
        cycle, commit, accuracy, correct, total,
        cost_cents, eval_seconds, prompt_config,
        status, description
    )

    try:
        comment = post_comment_to_issue(issue_id, comment_body, api_key)
        print(f"✓ Posted cycle {cycle} comment (ID: {comment['id']})")
        return 0
    except Exception as e:
        print(f"✗ Failed to post cycle {cycle} comment: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
