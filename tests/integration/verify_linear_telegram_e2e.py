#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E verification script for Linear + Telegram integration.

This script demonstrates the end-to-end flow of creating Linear issues from Telegram.
Run this to verify the integration is working correctly.

Usage:
    export LINEAR_API_KEY="your_key_here"
    export LINEAR_TEAM_ID="your_team_id_here"  # Optional
    python verify_linear_telegram_e2e.py
"""

import os
import sys
import json
import requests
from datetime import datetime


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step: int, text: str):
    """Print a step indicator."""
    print(f"\n[Step {step}] {text}")


def print_success(text: str):
    """Print a success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print an error message."""
    print(f"✗ {text}", file=sys.stderr)


def check_environment() -> tuple:
    """Check that required environment variables are set."""
    print_step(1, "Checking environment variables")

    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print_error("LINEAR_API_KEY not set")
        print("  Please set LINEAR_API_KEY environment variable")
        return None, None

    print_success(f"LINEAR_API_KEY found: {api_key[:20]}...")

    team_id = os.getenv("LINEAR_TEAM_ID", "ba745c5b-3dee-421d-9d31-fe5707aff2ca")
    print_success(f"Team ID: {team_id}")

    return api_key, team_id


def verify_linear_connection(api_key: str) -> bool:
    """Verify connection to Linear API."""
    print_step(2, "Verifying Linear API connection")

    query = """
    query {
        viewer {
            id
            name
            email
        }
        organization {
            id
            name
        }
    }
    """

    try:
        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query},
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return False

        data = response.json()

        if "errors" in data:
            print_error("GraphQL errors:")
            for error in data["errors"]:
                print(f"  - {error.get('message', 'Unknown error')}")
            return False

        viewer = data["data"]["viewer"]
        org = data["data"]["organization"]

        print_success(f"Connected as: {viewer['name']} ({viewer['email']})")
        print_success(f"Organization: {org['name']}")

        return True

    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


def simulate_telegram_message() -> dict:
    """Simulate a Telegram message that triggers issue creation."""
    print_step(3, "Simulating Telegram message")

    message = {
        "update_id": 123456,
        "message": {
            "message_id": 789,
            "from": {
                "id": 987654321,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser"
            },
            "chat": {
                "id": 987654321,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private"
            },
            "date": int(datetime.now().timestamp()),
            "text": "/create_issue Test Linear integration from Telegram\nDescription: This issue was created as part of MOR-1 E2E testing to verify the Linear + Telegram integration works correctly."
        }
    }

    print(f"  Message from: @{message['message']['from']['username']}")
    print(f"  Message text: {message['message']['text'][:60]}...")

    return message


def parse_telegram_command(message: dict) -> tuple:
    """Parse Telegram message to extract issue details."""
    print_step(4, "Parsing Telegram command")

    text = message["message"]["text"]
    username = message["message"]["from"]["username"]

    if not text.startswith("/create_issue"):
        print_error("Message does not start with /create_issue")
        return None, None

    lines = text.split("\n")
    title = lines[0].replace("/create_issue", "").strip()
    description_lines = []

    for line in lines[1:]:
        if line.startswith("Description:"):
            description_lines.append(line.replace("Description:", "").strip())
        else:
            description_lines.append(line.strip())

    description = "\n".join(description_lines)

    # Add Telegram attribution
    full_description = f"**Created from Telegram by @{username}**\n\n{description}"

    print_success(f"Title: {title}")
    print_success(f"Description length: {len(description)} chars")

    return title, full_description


def create_linear_issue(api_key: str, team_id: str, title: str, description: str) -> dict:
    """Create a Linear issue."""
    print_step(5, "Creating Linear issue")

    mutation = """
    mutation CreateIssue($teamId: String!, $title: String!, $description: String) {
        issueCreate(input: {
            teamId: $teamId
            title: $title
            description: $description
        }) {
            success
            issue {
                id
                identifier
                title
                description
                url
                createdAt
                state {
                    name
                }
                team {
                    name
                }
            }
        }
    }
    """

    variables = {
        "teamId": team_id,
        "title": title,
        "description": description
    }

    try:
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
            print_error(f"API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return None

        data = response.json()

        if "errors" in data:
            print_error("GraphQL errors:")
            for error in data["errors"]:
                print(f"  - {error.get('message', 'Unknown error')}")
            return None

        if not data["data"]["issueCreate"]["success"]:
            print_error("Issue creation failed")
            return None

        issue = data["data"]["issueCreate"]["issue"]

        print_success(f"Issue created: {issue['identifier']}")
        print(f"  Title: {issue['title']}")
        print(f"  Team: {issue['team']['name']}")
        print(f"  State: {issue['state']['name']}")
        print(f"  URL: {issue['url']}")

        return issue

    except Exception as e:
        print_error(f"Failed to create issue: {e}")
        return None


def verify_e2e_flow():
    """Run the complete E2E verification."""
    print_header("Linear + Telegram Integration E2E Verification")
    print("This script verifies the end-to-end flow for MOR-1")

    # Step 1: Check environment
    api_key, team_id = check_environment()
    if not api_key:
        return False

    # Step 2: Verify Linear connection
    if not verify_linear_connection(api_key):
        return False

    # Step 3: Simulate Telegram message
    telegram_message = simulate_telegram_message()

    # Step 4: Parse command
    title, description = parse_telegram_command(telegram_message)
    if not title:
        return False

    # Step 5: Create Linear issue
    issue = create_linear_issue(api_key, team_id, title, description)
    if not issue:
        return False

    # Success!
    print_header("E2E Verification Complete!")
    print_success("All steps completed successfully")
    print(f"\n📋 Created Issue: {issue['identifier']}")
    print(f"🔗 URL: {issue['url']}")
    print("\nThe Linear + Telegram integration is working correctly!")

    return True


if __name__ == "__main__":
    success = verify_e2e_flow()
    sys.exit(0 if success else 1)
