# -*- coding: utf-8 -*-
"""
Tests for Linear integration utilities.
"""
import pytest
from tests.integration.linear_utils import (
    parse_telegram_create_issue_command,
    get_linear_config,
    verify_linear_connection,
    create_test_issue
)
import os


class TestTelegramMessageParsing:
    """Test Telegram message parsing utilities."""

    def test_parse_basic_create_issue_command(self):
        """Test parsing a basic /create_issue command."""
        text = "/create_issue Fix authentication bug"
        result = parse_telegram_create_issue_command(text)

        assert result["title"] == "Fix authentication bug"
        assert result["description"] == ""

    def test_parse_create_issue_with_description(self):
        """Test parsing /create_issue with description."""
        text = """/create_issue Bug in authentication flow
Description: Users are unable to login after password reset."""

        result = parse_telegram_create_issue_command(text)

        assert result["title"] == "Bug in authentication flow"
        assert result["description"] == "Users are unable to login after password reset."

    def test_parse_create_issue_with_multiline_description(self):
        """Test parsing /create_issue with multiline description."""
        text = """/create_issue Improve documentation
Description: The API documentation needs improvement.
It should include more examples.
Especially for the authentication flow."""

        result = parse_telegram_create_issue_command(text)

        assert result["title"] == "Improve documentation"
        assert "API documentation" in result["description"]
        assert "more examples" in result["description"]

    def test_parse_invalid_command_raises_error(self):
        """Test that invalid commands raise ValueError."""
        text = "This is not a command"

        with pytest.raises(ValueError, match="must start with /create_issue"):
            parse_telegram_create_issue_command(text)

    def test_parse_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        text = "/create_issue"

        with pytest.raises(ValueError, match="title cannot be empty"):
            parse_telegram_create_issue_command(text)


class TestLinearConfig:
    """Test Linear configuration utilities."""

    def test_get_config_with_env_vars(self, monkeypatch):
        """Test getting config from environment variables."""
        monkeypatch.setenv("LINEAR_API_KEY", "test_key")
        monkeypatch.setenv("LINEAR_TEAM_ID", "test_team_id")

        config = get_linear_config()

        assert config["api_key"] == "test_key"
        assert config["team_id"] == "test_team_id"

    def test_get_config_uses_default_team_id(self, monkeypatch):
        """Test that default team ID is used when not set."""
        monkeypatch.setenv("LINEAR_API_KEY", "test_key")
        monkeypatch.delenv("LINEAR_TEAM_ID", raising=False)

        config = get_linear_config()

        assert config["api_key"] == "test_key"
        assert config["team_id"] == "ba745c5b-3dee-421d-9d31-fe5707aff2ca"

    def test_get_config_missing_api_key_raises_error(self, monkeypatch):
        """Test that missing API key raises ValueError."""
        monkeypatch.delenv("LINEAR_API_KEY", raising=False)

        with pytest.raises(ValueError, match="LINEAR_API_KEY"):
            get_linear_config()


class TestLinearAPIIntegration:
    """Integration tests for Linear API (requires credentials)."""

    @pytest.fixture
    def linear_api_key(self):
        """Get Linear API key from environment."""
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            pytest.skip("LINEAR_API_KEY not set")
        return api_key

    @pytest.fixture
    def team_id(self):
        """Get team ID from environment or use default."""
        return os.getenv("LINEAR_TEAM_ID", "ba745c5b-3dee-421d-9d31-fe5707aff2ca")

    def test_verify_connection(self, linear_api_key):
        """Test verifying Linear API connection."""
        viewer = verify_linear_connection(linear_api_key)

        assert "id" in viewer
        assert "name" in viewer
        assert "email" in viewer
        print(f"✓ Connected as: {viewer['name']} ({viewer['email']})")

    def test_create_test_issue_utility(self, linear_api_key, team_id):
        """Test creating an issue using the utility function."""
        issue = create_test_issue(
            title="Test Issue from Utility",
            description="This issue was created using the linear_utils helper function.",
            api_key=linear_api_key,
            team_id=team_id
        )

        assert "id" in issue
        assert "identifier" in issue
        assert issue["title"] == "Test Issue from Utility"
        assert "url" in issue

        print(f"✓ Created issue: {issue['identifier']}")
        print(f"  URL: {issue['url']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
