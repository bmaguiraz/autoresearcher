#!/usr/bin/env python3
"""
Cleanup script for test issues created by integration tests.

This script identifies and closes Linear issues created by the test suite
(marked with [TEST] prefix or created from integration tests).

Usage:
    export LINEAR_API_KEY="your_key_here"
    python cleanup_test_issues.py [--dry-run]
"""

import os
import sys
import argparse
import requests
from typing import List, Dict, Any


def get_test_issues(api_key: str, team_id: str) -> List[Dict[str, Any]]:
    """Fetch all test issues from Linear."""
    query = """
    query GetTestIssues($teamId: String!) {
        team(id: $teamId) {
            issues(
                filter: {
                    title: { containsIgnoreCase: "[TEST]" }
                }
            ) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        id
                        name
                        type
                    }
                    url
                    createdAt
                }
            }
        }
    }
    """

    variables = {"teamId": team_id}

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json"
        },
        timeout=10
    )

    if response.status_code != 200:
        print(f"❌ Error fetching issues: {response.status_code}")
        print(response.text)
        return []

    data = response.json()

    if "errors" in data:
        print("❌ GraphQL errors:")
        for error in data["errors"]:
            print(f"  - {error.get('message', 'Unknown error')}")
        return []

    return data["data"]["team"]["issues"]["nodes"]


def get_canceled_state_id(api_key: str, team_id: str) -> str:
    """Get the 'Canceled' state ID for the team."""
    query = """
    query GetWorkflowStates($teamId: String!) {
        team(id: $teamId) {
            states {
                nodes {
                    id
                    name
                    type
                }
            }
        }
    }
    """

    variables = {"teamId": team_id}

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json"
        },
        timeout=10
    )

    if response.status_code != 200:
        return None

    data = response.json()

    if "errors" in data:
        return None

    states = data["data"]["team"]["states"]["nodes"]

    # Find the canceled state
    for state in states:
        if state["type"] == "canceled":
            return state["id"]

    return None


def close_issue(api_key: str, issue_id: str, state_id: str) -> bool:
    """Close a Linear issue by updating its state."""
    mutation = """
    mutation UpdateIssue($issueId: String!, $stateId: String!) {
        issueUpdate(
            id: $issueId
            input: { stateId: $stateId }
        ) {
            success
            issue {
                id
                identifier
                state {
                    name
                }
            }
        }
    }
    """

    variables = {
        "issueId": issue_id,
        "stateId": state_id
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

    if response.status_code != 200:
        return False

    data = response.json()

    if "errors" in data:
        return False

    return data["data"]["issueUpdate"]["success"]


def main():
    parser = argparse.ArgumentParser(
        description="Cleanup test issues from Linear"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--team-id",
        default="ba745c5b-3dee-421d-9d31-fe5707aff2ca",
        help="Linear team ID (defaults to autoresearcher team)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("❌ LINEAR_API_KEY environment variable not set")
        print("   Please set it with: export LINEAR_API_KEY='your_key_here'")
        return 1

    print("🔍 Searching for test issues...")
    print(f"   Team ID: {args.team_id}")

    # Fetch test issues
    issues = get_test_issues(api_key, args.team_id)

    if not issues:
        print("✅ No test issues found!")
        return 0

    print(f"\n📋 Found {len(issues)} test issue(s):\n")

    for issue in issues:
        print(f"  {issue['identifier']}: {issue['title']}")
        print(f"    State: {issue['state']['name']}")
        print(f"    URL: {issue['url']}")
        print()

    if args.dry_run:
        print("🔒 DRY RUN - No changes made")
        print(f"   Would close {len(issues)} issue(s)")
        return 0

    # Get canceled state
    print("🔍 Finding 'Canceled' state...")
    canceled_state_id = get_canceled_state_id(api_key, args.team_id)

    if not canceled_state_id:
        print("❌ Could not find 'Canceled' state for team")
        return 1

    print(f"✓ Found state ID: {canceled_state_id}\n")

    # Close issues
    print("🗑️  Closing test issues...")

    closed_count = 0
    for issue in issues:
        # Skip already closed/canceled issues
        if issue["state"]["type"] in ["canceled", "completed"]:
            print(f"  ⏭️  {issue['identifier']} - Already closed")
            continue

        success = close_issue(api_key, issue["id"], canceled_state_id)

        if success:
            print(f"  ✓ {issue['identifier']} - Closed")
            closed_count += 1
        else:
            print(f"  ✗ {issue['identifier']} - Failed to close")

    print(f"\n✅ Cleanup complete! Closed {closed_count}/{len(issues)} issue(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
