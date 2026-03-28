#!/usr/bin/env python3
"""
Post experiment 03-data-cleaning results to Linear issue.
"""
import json
import os
import sys
import requests
from pathlib import Path


def get_or_create_label(label_name: str, api_key: str, team_id: str) -> str:
    """Get existing label ID or create new label."""
    # First, try to find existing label
    query = """
    query FindLabel($teamId: String!) {
        team(id: $teamId) {
            labels {
                nodes {
                    id
                    name
                }
            }
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": {"teamId": team_id}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    # Check if label exists
    labels = data["data"]["team"]["labels"]["nodes"]
    for label in labels:
        if label["name"] == label_name:
            return label["id"]

    # Create new label if it doesn't exist
    mutation = """
    mutation CreateLabel($teamId: String!, $name: String!) {
        issueLabelCreate(input: {
            teamId: $teamId
            name: $name
        }) {
            success
            issueLabel {
                id
                name
            }
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": {"teamId": team_id, "name": label_name}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["issueLabelCreate"]["success"]:
        raise ValueError("Label creation failed")

    return data["data"]["issueLabelCreate"]["issueLabel"]["id"]


def add_label_to_issue(issue_id: str, label_id: str, api_key: str) -> bool:
    """Add a label to an issue."""
    mutation = """
    mutation AddLabel($issueId: String!, $labelId: String!) {
        issueAddLabel(id: $issueId, labelId: $labelId) {
            success
            issue {
                id
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
    }
    """

    variables = {
        "issueId": issue_id,
        "labelId": label_id
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": variables},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    return data["data"]["issueAddLabel"]["success"]


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
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["commentCreate"]["success"]:
        raise ValueError("Comment creation failed")

    return data["data"]["commentCreate"]["comment"]


def format_results_comment(data: dict, pr_url: str) -> str:
    """Format experiment results as a markdown comment."""
    session_id = data["session_id"]
    cycles = data["cycles_completed"]
    summary = data["summary"]
    results = data["results"]

    # Build results table
    table_rows = []
    for result in results:
        cycle = result["cycle"]
        score = result["aggregate_score"]
        strategy = result["strategy"]
        completeness = result["metrics"]["completeness"]
        consistency = result["metrics"]["consistency"]
        accuracy = result["metrics"]["accuracy"]
        dedup = result["metrics"]["deduplication_rate"]

        table_rows.append(
            f"| {cycle} | {strategy} | {score:.4f} | "
            f"{completeness:.4f} | {consistency:.4f} | {accuracy:.4f} | {dedup:.4f} |"
        )

    comment = f"""## ✅ Experiment Complete: 03-data-cleaning

**Session ID:** `{session_id}`
**Cycles:** {cycles}
**Pull Request:** {pr_url}

### 📊 Results Summary

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| **Aggregate Score** | {summary['initial_score']:.4f} | {summary['final_score']:.4f} | **+{summary['improvement']:.4f} ({summary['improvement_percentage']:+.2f}%)** |

### 🔄 Cycle Details

| Cycle | Strategy | Aggregate | Completeness | Consistency | Accuracy | Deduplication |
|-------|----------|-----------|--------------|-------------|----------|---------------|
{chr(10).join(table_rows)}

### 🎯 Key Findings

The optimization achieved a **{summary['improvement_percentage']:.2f}% improvement** in aggregate data quality score by:

- **Data Preservation**: Shifted from removing incomplete records to intelligent imputation
- **Completeness Gain**: Improved from {results[0]['metrics']['completeness']:.1%} to {results[-1]['metrics']['completeness']:.1%} (+{(results[-1]['metrics']['completeness'] - results[0]['metrics']['completeness']):.1%})
- **Quality Balance**: Maintained high accuracy and deduplication while maximizing data retention

### 📁 Artifacts

- Configuration: `experiments/03-data-cleaning/config.json`
- Results: `experiments/03-data-cleaning/results/results_latest.json`
- Summary: `experiments/03-data-cleaning/EXPERIMENT_SUMMARY_MOR64_{session_id}.md`

---
*Automated autoresearch experiment · Session `{session_id}`*
"""
    return comment


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    # Issue details from webhook
    issue_id = "86470c49-41d4-48a8-bccd-c006451fca3a"
    team_id = "ba745c5b-3dee-421d-9d31-fe5707aff2ca"
    session_id = "7d3a42be"
    pr_url = "https://github.com/bmaguiraz/autoresearcher/pull/1163"

    # Load results
    results_file = Path(__file__).parent / "results" / "results_latest.json"
    if not results_file.exists():
        print(f"Error: Results file not found at {results_file}")
        return 1

    with open(results_file, 'r') as f:
        data = json.load(f)

    print(f"Posting results to Linear issue {issue_id}...")

    # Format and post results comment
    comment_body = format_results_comment(data, pr_url)
    try:
        comment = post_comment_to_issue(issue_id, comment_body, api_key)
        print(f"✓ Posted results comment (ID: {comment['id']})")
    except Exception as e:
        print(f"✗ Failed to post comment: {e}")
        return 1

    # Add session label
    label_name = f"ac:sid:{session_id}"
    try:
        label_id = get_or_create_label(label_name, api_key, team_id)
        print(f"✓ Label '{label_name}' ready (ID: {label_id})")

        success = add_label_to_issue(issue_id, label_id, api_key)
        if success:
            print(f"✓ Added label '{label_name}' to issue")
        else:
            print(f"✗ Failed to add label to issue")
            return 1
    except Exception as e:
        print(f"✗ Failed to add label: {e}")
        return 1

    print("\n✅ Results posted successfully!")
    print(f"   - Comment with results table")
    print(f"   - Label: {label_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
