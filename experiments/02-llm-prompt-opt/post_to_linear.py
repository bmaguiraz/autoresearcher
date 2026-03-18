#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post experiment results to Linear issue as comments.
"""
import json
import os
import sys
import requests
from pathlib import Path


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


def format_cycle_comment(cycle_data: dict) -> str:
    """Format a single cycle's results as a markdown comment."""
    cycle_num = cycle_data["cycle"]
    metrics = cycle_data["metrics"]
    score = cycle_data["aggregate_score"]

    comment = f"""## 🔄 Cycle {cycle_num} Complete

**Aggregate Score:** `{score:.3f}`

### Metrics
- **Clarity:** {metrics['clarity']:.3f}
- **Specificity:** {metrics['specificity']:.3f}
- **Response Quality:** {metrics['response_quality']:.3f}
- **Task Completion:** {metrics['task_completion']:.3f}

**Timestamp:** {cycle_data['timestamp']}
"""
    return comment


def format_summary_comment(summary: dict, cycles_completed: int) -> str:
    """Format the final summary as a markdown comment."""
    comment = f"""## ✅ Experiment Complete - {cycles_completed} Cycles

### Summary Statistics
- **Total Cycles:** {summary['total_cycles']}
- **Initial Score:** {summary['initial_score']:.3f}
- **Final Score:** {summary['final_score']:.3f}
- **Improvement:** +{summary['improvement']:.3f} ({summary['improvement_percentage']:.1f}%)
- **Best Score:** {summary['best_score']:.3f}
- **Average Score:** {summary['average_score']:.3f}

### Results
The experiment has completed successfully with a {summary['improvement_percentage']:.1f}% improvement in aggregate score across {summary['total_cycles']} optimization cycles.

Results are available in `experiments/02-llm-prompt-opt/results/results_latest.json`
"""
    return comment


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    issue_id = os.getenv("LINEAR_ISSUE_ID", "db5defca-2c4b-48cd-8528-945777c1158c")

    # Load results
    results_file = Path(__file__).parent / "results" / "results_latest.json"
    if not results_file.exists():
        print(f"Error: Results file not found at {results_file}")
        return 1

    with open(results_file, 'r') as f:
        data = json.load(f)

    print(f"Posting results to Linear issue {issue_id}...")

    # Post cycle comments
    for cycle_result in data["results"]:
        comment_body = format_cycle_comment(cycle_result)
        try:
            comment = post_comment_to_issue(issue_id, comment_body, api_key)
            print(f"✓ Posted cycle {cycle_result['cycle']} comment (ID: {comment['id']})")
        except Exception as e:
            print(f"✗ Failed to post cycle {cycle_result['cycle']} comment: {e}")
            return 1

    # Post summary comment
    summary_body = format_summary_comment(data["summary"], data["cycles_completed"])
    try:
        comment = post_comment_to_issue(issue_id, summary_body, api_key)
        print(f"✓ Posted summary comment (ID: {comment['id']})")
    except Exception as e:
        print(f"✗ Failed to post summary comment: {e}")
        return 1

    print("\n✅ All comments posted successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
