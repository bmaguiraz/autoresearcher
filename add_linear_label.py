#!/usr/bin/env python3
"""Add a label to a Linear issue."""
import os
import sys
import requests


def add_label_to_issue(issue_id: str, label_name: str) -> dict:
    """Add a label to a Linear issue."""
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise ValueError("LINEAR_API_KEY environment variable not set")

    # First, get or create the label
    query_label = """
    query GetLabel($name: String!) {
        issueLabels(filter: { name: { eq: $name } }) {
            nodes {
                id
                name
            }
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query_label, "variables": {"name": label_name}},
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

    labels = data["data"]["issueLabels"]["nodes"]

    if labels:
        label_id = labels[0]["id"]
        print(f"Found existing label: {label_name} (ID: {label_id})")
    else:
        # Create the label if it doesn't exist
        create_label_mutation = """
        mutation CreateLabel($name: String!) {
            issueLabelCreate(input: { name: $name }) {
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
            json={"query": create_label_mutation, "variables": {"name": label_name}},
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

        if not data["data"]["issueLabelCreate"]["success"]:
            raise ValueError("Label creation failed")

        label_id = data["data"]["issueLabelCreate"]["issueLabel"]["id"]
        print(f"Created new label: {label_name} (ID: {label_id})")

    # Now add the label to the issue
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

    if not data["data"]["issueAddLabel"]["success"]:
        raise ValueError("Adding label to issue failed")

    return data["data"]["issueAddLabel"]["issue"]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_linear_label.py <issue_id> <label_name>")
        sys.exit(1)

    issue_id = sys.argv[1]
    label_name = sys.argv[2]

    try:
        result = add_label_to_issue(issue_id, label_name)
        print(f"Label '{label_name}' added successfully to issue {issue_id}")
        print(f"Current labels: {[label['name'] for label in result['labels']['nodes']]}")
    except Exception as e:
        print(f"Error adding label: {e}", file=sys.stderr)
        sys.exit(1)
