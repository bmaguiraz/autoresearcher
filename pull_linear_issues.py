#!/usr/bin/env python3
"""
Pull open issues from Linear for the autoresearcher project.
"""
import os
import json
import requests


def get_open_issues(api_key: str, project_id: str) -> list:
    """Fetch all open issues from Linear for a specific project."""
    query = """
    query GetProjectIssues($projectId: String!) {
        project(id: $projectId) {
            id
            name
            issues(filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
                nodes {
                    id
                    identifier
                    title
                    description
                    url
                    priority
                    state {
                        name
                        type
                    }
                    labels {
                        nodes {
                            id
                            name
                        }
                    }
                    assignee {
                        id
                        name
                    }
                }
            }
        }
    }
    """

    variables = {"projectId": project_id}

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    return data["data"]["project"]["issues"]["nodes"]


def main():
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    # Load project config
    with open(".linear-worker.json", "r") as f:
        config = json.load(f)

    project_id = config["projectId"]

    print(f"Fetching open issues for project {config['projectName']}...")
    issues = get_open_issues(api_key, project_id)

    print(f"\n✅ Found {len(issues)} open issues:\n")

    for issue in issues:
        labels = [label["name"] for label in issue["labels"]["nodes"]]
        assignee = issue["assignee"]["name"] if issue["assignee"] else "Unassigned"

        print(f"**{issue['identifier']}**: {issue['title']}")
        print(f"  State: {issue['state']['name']} | Priority: {issue['priority']} | Assignee: {assignee}")
        if labels:
            print(f"  Labels: {', '.join(labels)}")
        print(f"  URL: {issue['url']}")
        print()

    # Save to JSON for processing
    with open("linear_issues.json", "w") as f:
        json.dump(issues, f, indent=2)

    print(f"Issues saved to linear_issues.json")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
