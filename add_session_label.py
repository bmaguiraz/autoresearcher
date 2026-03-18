#!/usr/bin/env python3
"""Add session label to Linear issue."""
import os
import sys
import requests


def create_or_get_label(team_id: str, label_name: str, api_key: str) -> str:
    """Create a label if it doesn't exist, or get existing label ID."""
    # First try to find existing label
    query = """
    query GetLabels($teamId: String!) {
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

    # Create label if it doesn't exist
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


def add_label_to_issue(issue_id: str, label_id: str, api_key: str) -> None:
    """Add a label to an issue."""
    mutation = """
    mutation AddLabelToIssue($issueId: String!, $labelId: String!) {
        issueAddLabel(id: $issueId, labelId: $labelId) {
            success
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": {"issueId": issue_id, "labelId": label_id}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["issueAddLabel"]["success"]:
        raise ValueError("Failed to add label to issue")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python add_session_label.py <issue_id> <team_id> <session_id>")
        sys.exit(1)

    issue_id = sys.argv[1]
    team_id = sys.argv[2]
    session_id = sys.argv[3]

    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("LINEAR_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    label_name = f"ac:sid:{session_id}"

    try:
        label_id = create_or_get_label(team_id, label_name, api_key)
        print(f"Label ID: {label_id}")
        add_label_to_issue(issue_id, label_id, api_key)
        print(f"Successfully added label '{label_name}' to issue {issue_id}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
