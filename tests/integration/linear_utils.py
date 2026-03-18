# -*- coding: utf-8 -*-
"""
Utility functions for Linear integration testing.

This module provides helper functions for creating and managing
Linear issues during integration tests.
"""
import os
from typing import Dict, Any, Optional
import requests


def get_linear_config() -> Dict[str, str]:
    """
    Get Linear configuration from environment variables.

    Returns:
        Dictionary with api_key and team_id

    Raises:
        ValueError: If required environment variables are not set
    """
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise ValueError("LINEAR_API_KEY environment variable not set")

    team_id = os.getenv("LINEAR_TEAM_ID", "ba745c5b-3dee-421d-9d31-fe5707aff2ca")

    return {
        "api_key": api_key,
        "team_id": team_id
    }


def create_test_issue(
    title: str,
    description: str,
    api_key: Optional[str] = None,
    team_id: Optional[str] = None,
    labels: Optional[list] = None
) -> Dict[str, Any]:
    """
    Create a test issue in Linear.

    Args:
        title: Issue title
        description: Issue description
        api_key: Linear API key (defaults to env var)
        team_id: Linear team ID (defaults to env var)
        labels: Optional list of label IDs

    Returns:
        Dictionary with issue data including id, identifier, and url

    Raises:
        requests.HTTPError: If the API request fails
        ValueError: If required config is missing
    """
    if not api_key or not team_id:
        config = get_linear_config()
        api_key = api_key or config["api_key"]
        team_id = team_id or config["team_id"]

    mutation = """
    mutation CreateIssue($teamId: String!, $title: String!, $description: String, $labelIds: [String!]) {
        issueCreate(input: {
            teamId: $teamId
            title: $title
            description: $description
            labelIds: $labelIds
        }) {
            success
            issue {
                id
                identifier
                title
                url
                state {
                    name
                }
            }
        }
    }
    """

    variables = {
        "teamId": team_id,
        "title": title,
        "description": description,
        "labelIds": labels or []
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

    if not data["data"]["issueCreate"]["success"]:
        raise ValueError("Issue creation failed")

    return data["data"]["issueCreate"]["issue"]


def verify_linear_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify connection to Linear API and return viewer information.

    Args:
        api_key: Linear API key (defaults to env var)

    Returns:
        Dictionary with viewer data (id, name, email, organization)

    Raises:
        requests.HTTPError: If the API request fails
        ValueError: If API key is missing
    """
    if not api_key:
        config = get_linear_config()
        api_key = config["api_key"]

    query = """
    query {
        viewer {
            id
            name
            email
            organization {
                name
            }
        }
    }
    """

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query},
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

    return data["data"]["viewer"]


def parse_telegram_create_issue_command(text: str) -> Dict[str, str]:
    """
    Parse a Telegram /create_issue command message.

    Expected format:
        /create_issue Issue title here
        Description: Detailed description

    Args:
        text: The message text from Telegram

    Returns:
        Dictionary with 'title' and 'description' keys

    Raises:
        ValueError: If message format is invalid
    """
    if not text.startswith("/create_issue"):
        raise ValueError("Message must start with /create_issue")

    lines = text.split("\n")
    title = lines[0].replace("/create_issue", "").strip()

    if not title:
        raise ValueError("Issue title cannot be empty")

    # Extract description (everything after first line)
    description = "\n".join(lines[1:])
    if description.startswith("Description:"):
        description = description.replace("Description:", "", 1).strip()

    return {
        "title": title,
        "description": description
    }
