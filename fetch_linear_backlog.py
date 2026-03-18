#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch Linear backlog for a project."""
import os
import sys
import json
import requests


def fetch_project_backlog(project_id: str) -> dict:
    """Fetch all issues for a Linear project."""
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise ValueError("LINEAR_API_KEY environment variable not set")

    query = """
    query ProjectIssues($projectId: String!) {
        project(id: $projectId) {
            id
            name
            description
            state
            issues {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    priorityLabel
                    url
                    state {
                        name
                        type
                    }
                    assignee {
                        name
                        email
                    }
                    labels {
                        nodes {
                            name
                        }
                    }
                    createdAt
                    updatedAt
                }
            }
        }
    }
    """

    variables = {
        "projectId": project_id
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": variables},
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

    return data["data"]["project"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_linear_backlog.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]

    try:
        result = fetch_project_backlog(project_id)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error fetching backlog: {e}", file=sys.stderr)
        sys.exit(1)
