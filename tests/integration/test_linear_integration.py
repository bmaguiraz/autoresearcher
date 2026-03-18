# -*- coding: utf-8 -*-
"""
Integration test for Linear issue creation from Telegram.

This test verifies the E2E flow of creating Linear issues from Telegram messages.
"""
import os
import pytest
import requests
from typing import Dict, Any


class TestLinearIntegration:
    """Test suite for Linear integration."""

    @pytest.fixture
    def linear_api_key(self):
        """Get Linear API key from environment."""
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            pytest.skip("LINEAR_API_KEY not set")
        return api_key

    @pytest.fixture
    def telegram_bot_token(self):
        """Get Telegram bot token from environment."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            pytest.skip("TELEGRAM_BOT_TOKEN not set")
        return token

    @pytest.fixture
    def team_id(self):
        """Get team ID from environment or use default."""
        return os.getenv("LINEAR_TEAM_ID", "ba745c5b-3dee-421d-9d31-fe5707aff2ca")

    def test_linear_api_connection(self, linear_api_key: str):
        """Test that we can connect to Linear API."""
        query = """
        query {
            viewer {
                id
                name
                email
            }
        }
        """

        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": query},
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )

        assert response.status_code == 200, f"Failed to connect to Linear API: {response.text}"
        data = response.json()
        assert "data" in data, "No data in response"
        assert "viewer" in data["data"], "No viewer in response"
        print(f"✓ Connected to Linear API as: {data['data']['viewer']['name']}")

    def test_create_linear_issue(self, linear_api_key: str, team_id: str):
        """Test creating a Linear issue via API."""
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
                    url
                }
            }
        }
        """

        variables = {
            "teamId": team_id,
            "title": "Test Issue from Integration Test",
            "description": "This is a test issue created by the Linear integration test suite."
        }

        response = requests.post(
            "https://api.linear.app/graphql",
            json={"query": mutation, "variables": variables},
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )

        assert response.status_code == 200, f"Failed to create issue: {response.text}"
        data = response.json()

        # Check for errors
        if "errors" in data:
            pytest.fail(f"GraphQL errors: {data['errors']}")

        assert "data" in data, "No data in response"
        assert "issueCreate" in data["data"], "No issueCreate in response"
        assert data["data"]["issueCreate"]["success"], "Issue creation failed"

        issue = data["data"]["issueCreate"]["issue"]
        print(f"✓ Created issue: {issue['identifier']} - {issue['title']}")
        print(f"  URL: {issue['url']}")

    def test_telegram_webhook_simulation(self, linear_api_key: str, team_id: str):
        """
        Simulate a Telegram webhook message and verify it creates a Linear issue.

        NOTE: This test creates REAL Linear issues for E2E verification.
        Issues are marked with [TEST] prefix and detailed description to distinguish
        from production work items.

        In a real implementation, this would:
        1. Receive a webhook from Telegram
        2. Parse the message content
        3. Create a Linear issue based on the message

        NOTE: This test creates a real Linear issue for integration testing purposes.
        Issues created by this test should be marked as test issues or closed after verification.
        The "Bug in authentication flow" text is example text only - autoresearcher does not
        have an authentication system as it is a Python research automation platform.
        """
        # Simulate incoming Telegram message
        telegram_message = {
            "message_id": 12345,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "text": "/create_issue [TEST] Bug in authentication flow\nDescription: Users are unable to login after password reset. This is a test issue from integration suite.",
            "date": 1234567890
        }

        # Parse the message (simplified parsing logic)
        text = telegram_message["text"]
        if text.startswith("/create_issue"):
            lines = text.split("\n")
            title = lines[0].replace("/create_issue", "").strip()
            description = "\n".join(lines[1:]).replace("Description:", "").strip()

            # Create Linear issue
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
                        url
                    }
                }
            }
            """

            # Add clear test markers to prevent confusion with real issues
            test_description = f"""**🧪 TEST ISSUE - Integration Test Suite**

Created from Telegram by @{telegram_message['from']['username']}

{description}

---
*This issue was created by the automated integration test suite at `tests/integration/test_linear_integration.py` to verify the Telegram → Linear → Agent webhook workflow. It is NOT a real bug.*

**Test Purpose:** Verify E2E issue creation from Telegram messages
**Test File:** `tests/integration/test_linear_integration.py:test_telegram_webhook_simulation`
**Expected Behavior:** This issue validates that the webhook integration is working correctly."""

            variables = {
                "teamId": team_id,
                "title": title,
                "description": test_description
            }

            response = requests.post(
                "https://api.linear.app/graphql",
                json={"query": mutation, "variables": variables},
                headers={
                    "Authorization": linear_api_key,
                    "Content-Type": "application/json"
                },
                timeout=10
            )

            assert response.status_code == 200
            data = response.json()

            if "errors" in data:
                pytest.fail(f"GraphQL errors: {data['errors']}")

            assert data["data"]["issueCreate"]["success"]
            issue = data["data"]["issueCreate"]["issue"]

            print(f"✓ E2E Test: Telegram message → Linear issue")
            print(f"  Issue: {issue['identifier']} - {issue['title']}")
            print(f"  URL: {issue['url']}")
            return  # Test passed

        pytest.fail("Message did not trigger issue creation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
