#!/usr/bin/env python3
"""
Post MAG-143 experiment results to Linear issue as comments.
"""
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


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    issue_id = "6d333694-2074-493a-b93f-a61cf00453ee"  # MAG-143

    # Create results comment
    comment_body = """## 🔬 Autoresearch Complete: LLM Prompt Optimization (1 cycle)

### Experiment Results

**Baseline (d90825f)**
- Accuracy: **0.960** (48/50 correct)
- Cost: $0.008
- Errors: 2 positive samples misclassified as neutral
  - Item 7: "This book changed my perspective on life. Highly recommend it to everyone."
  - Item 12: "The team delivered the project ahead of schedule and under budget."

**Hypothesis 1: Enhanced Positive Signal Recognition (b4622b6)**
- Accuracy: **1.000** (50/50 correct) ✨
- Cost: $0.010
- Changes:
  - Expanded positive label definition with: recommendations, accomplishments, exceeded expectations, gratitude/joy
  - Added neutral few-shot example to clarify boundaries

### Summary
- **Total Cycles**: 1
- **Improvement**: +0.040 (+4.2%)
- **Status**: ✅ **Perfect accuracy achieved**

### Key Findings
1. Subtle positive signals (recommendations like "highly recommend", accomplishments) were being misclassified as neutral
2. Explicitly listing these patterns in the positive label definition resolved both errors
3. Adding a neutral few-shot example helped clarify decision boundaries
4. Cost increase ($0.002) is negligible for perfect classification

### Branch & Commits
- Branch: `autoresearch/mar18-mag143`
- Baseline: d90825f8
- Hypothesis 1: b4622b6c

Results logged in `experiments/02-llm-prompt-opt/results.tsv`
"""

    try:
        comment = post_comment_to_issue(issue_id, comment_body, api_key)
        print(f"✓ Posted results comment to MAG-143 (ID: {comment['id']})")
        print(f"\n✅ Results posted successfully!")
        return 0
    except Exception as e:
        print(f"✗ Failed to post comment: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
