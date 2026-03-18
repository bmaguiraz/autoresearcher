# -*- coding: utf-8 -*-
"""Tests for authentication module.

Key test: verify sessions are invalidated after password reset (bug fix).
"""

import pytest
import time
from autoresearcher.auth import (
    AuthManager,
    AuthenticationError,
    PasswordResetError,
)


@pytest.fixture
def auth_manager():
    """Create a fresh auth manager for each test."""
    return AuthManager()


@pytest.fixture
def test_user(auth_manager):
    """Create a test user."""
    auth_manager.create_user("testuser", "password123")
    return "testuser"


class TestUserCreation:
    """Test user account creation."""

    def test_create_user_success(self, auth_manager):
        user = auth_manager.create_user("alice", "secret")
        assert user.username == "alice"
        assert user.password_hash != "secret"  # Should be hashed
        assert user.password_version == 0

    def test_create_duplicate_user_fails(self, auth_manager):
        auth_manager.create_user("bob", "pass1")
        with pytest.raises(ValueError, match="already exists"):
            auth_manager.create_user("bob", "pass2")


class TestLogin:
    """Test login functionality."""

    def test_login_success(self, auth_manager, test_user):
        session_id = auth_manager.login("testuser", "password123")
        assert session_id is not None
        assert len(session_id) > 20  # Should be a long random token
        assert auth_manager.validate_session(session_id) is True

    def test_login_wrong_password(self, auth_manager, test_user):
        with pytest.raises(AuthenticationError, match="Invalid username or password"):
            auth_manager.login("testuser", "wrongpassword")

    def test_login_nonexistent_user(self, auth_manager):
        with pytest.raises(AuthenticationError, match="Invalid username or password"):
            auth_manager.login("nobody", "password")


class TestLogout:
    """Test logout functionality."""

    def test_logout_invalidates_session(self, auth_manager, test_user):
        session_id = auth_manager.login("testuser", "password123")
        assert auth_manager.validate_session(session_id) is True

        auth_manager.logout(session_id)
        assert auth_manager.validate_session(session_id) is False

    def test_logout_nonexistent_session(self, auth_manager):
        # Should not raise error
        auth_manager.logout("fake-session-id")


class TestPasswordReset:
    """Test password reset functionality."""

    def test_request_reset_token(self, auth_manager, test_user):
        reset_token = auth_manager.request_password_reset("testuser")
        assert reset_token is not None
        assert len(reset_token) > 20

        user = auth_manager.users["testuser"]
        assert user.reset_token == reset_token
        assert user.reset_token_expires is not None
        assert user.reset_token_expires > time.time()

    def test_reset_password_success(self, auth_manager, test_user):
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpassword456")

        # Should be able to login with new password
        session_id = auth_manager.login("testuser", "newpassword456")
        assert auth_manager.validate_session(session_id) is True

    def test_reset_password_old_password_fails(self, auth_manager, test_user):
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpassword456")

        # Old password should not work
        with pytest.raises(AuthenticationError):
            auth_manager.login("testuser", "password123")

    def test_reset_with_invalid_token_fails(self, auth_manager, test_user):
        with pytest.raises(PasswordResetError, match="Invalid reset token"):
            auth_manager.reset_password("testuser", "wrong-token", "newpass")

    def test_reset_token_expires(self, auth_manager, test_user):
        reset_token = auth_manager.request_password_reset("testuser")

        # Manually expire the token
        user = auth_manager.users["testuser"]
        user.reset_token_expires = time.time() - 1

        with pytest.raises(PasswordResetError, match="expired"):
            auth_manager.reset_password("testuser", reset_token, "newpass")

    def test_reset_token_cleared_after_use(self, auth_manager, test_user):
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpass")

        # Same token should not work twice
        with pytest.raises(PasswordResetError):
            auth_manager.reset_password("testuser", reset_token, "anotherpass")


class TestPasswordResetBugFix:
    """CRITICAL: Test that sessions are invalidated after password reset.

    This is the bug fix - users were able to login with old sessions
    after password reset, which is a security issue.
    """

    def test_sessions_invalidated_after_password_reset(self, auth_manager, test_user):
        """Bug fix: Old sessions must be invalidated when password is reset."""
        # User logs in and gets a session
        session1 = auth_manager.login("testuser", "password123")
        session2 = auth_manager.login("testuser", "password123")

        # Both sessions are valid
        assert auth_manager.validate_session(session1) is True
        assert auth_manager.validate_session(session2) is True

        # User resets password
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpassword456")

        # BUG FIX: Old sessions must be INVALID after password reset
        assert auth_manager.validate_session(session1) is False
        assert auth_manager.validate_session(session2) is False

        # New login with new password should work
        new_session = auth_manager.login("testuser", "newpassword456")
        assert auth_manager.validate_session(new_session) is True

    def test_password_version_increments_on_reset(self, auth_manager, test_user):
        """Verify password_version mechanism works correctly."""
        user = auth_manager.users["testuser"]
        initial_version = user.password_version
        assert initial_version == 0

        # Reset password
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpass")

        # Password version should increment
        assert user.password_version == initial_version + 1

    def test_session_tied_to_password_version(self, auth_manager, test_user):
        """Verify sessions store and check password version."""
        session_id = auth_manager.login("testuser", "password123")
        session = auth_manager.sessions[session_id]

        # Session should have current password version
        user = auth_manager.users["testuser"]
        assert session.password_version == user.password_version

        # After password reset, versions should mismatch
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "newpass")

        assert session.password_version < user.password_version
        # This mismatch causes session validation to fail
        assert auth_manager.validate_session(session_id) is False

    def test_multiple_password_resets(self, auth_manager, test_user):
        """Test multiple password resets in sequence."""
        # Create initial session
        session1 = auth_manager.login("testuser", "password123")

        # First reset
        token1 = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", token1, "password_v2")
        assert auth_manager.validate_session(session1) is False

        # Login with new password
        session2 = auth_manager.login("testuser", "password_v2")
        assert auth_manager.validate_session(session2) is True

        # Second reset
        token2 = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", token2, "password_v3")

        # Both old sessions should be invalid
        assert auth_manager.validate_session(session1) is False
        assert auth_manager.validate_session(session2) is False

        # New session with latest password works
        session3 = auth_manager.login("testuser", "password_v3")
        assert auth_manager.validate_session(session3) is True


class TestSessionValidation:
    """Test session validation edge cases."""

    def test_validate_nonexistent_session(self, auth_manager):
        assert auth_manager.validate_session("fake-id") is False

    def test_validate_session_after_user_deleted(self, auth_manager, test_user):
        session_id = auth_manager.login("testuser", "password123")
        assert auth_manager.validate_session(session_id) is True

        # Simulate user deletion
        del auth_manager.users["testuser"]

        assert auth_manager.validate_session(session_id) is False


class TestMOR26Verification:
    """MOR-26: Verification that authentication bug is fixed.

    Issue: Users are unable to login after password reset
    Root cause: Sessions were not invalidated after password reset
    Fix: password_version tracking ensures old sessions become invalid

    This test class explicitly verifies MOR-26 is resolved.
    """

    def test_mor26_login_after_password_reset_works(self, auth_manager, test_user):
        """MOR-26: Verify users CAN login with new password after reset.

        The bug description says "Users are unable to login after password reset."
        This test confirms users CAN login after reset with the NEW password.
        """
        # Initial login works
        session1 = auth_manager.login("testuser", "password123")
        assert auth_manager.validate_session(session1) is True

        # Reset password
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "new_secure_password")

        # CRITICAL: User SHOULD be able to login with new password
        # This was the bug - if this fails, MOR-26 is not fixed
        new_session = auth_manager.login("testuser", "new_secure_password")
        assert new_session is not None
        assert auth_manager.validate_session(new_session) is True

    def test_mor26_old_sessions_invalidated_after_reset(self, auth_manager, test_user):
        """MOR-26: Verify old sessions are invalidated (security requirement).

        After password reset, all previous sessions must be invalid.
        This prevents unauthorized access with stolen session tokens.
        """
        # Create multiple sessions before reset
        session1 = auth_manager.login("testuser", "password123")
        session2 = auth_manager.login("testuser", "password123")

        assert auth_manager.validate_session(session1) is True
        assert auth_manager.validate_session(session2) is True

        # Reset password
        reset_token = auth_manager.request_password_reset("testuser")
        auth_manager.reset_password("testuser", reset_token, "new_password")

        # Old sessions MUST be invalid
        assert auth_manager.validate_session(session1) is False
        assert auth_manager.validate_session(session2) is False

    def test_mor26_complete_password_reset_flow(self, auth_manager, test_user):
        """MOR-26: End-to-end test of password reset flow.

        Simulates complete user experience:
        1. User logs in and uses the system
        2. User forgets password and requests reset
        3. User resets password with token
        4. User can login with new password
        5. Old sessions are no longer valid
        """
        # Step 1: User logs in normally
        old_session = auth_manager.login("testuser", "password123")
        assert auth_manager.validate_session(old_session) is True

        # Step 2: User requests password reset
        reset_token = auth_manager.request_password_reset("testuser")
        assert reset_token is not None

        # Step 3: User receives token via email and resets password
        auth_manager.reset_password("testuser", reset_token, "MyNewPassword123!")

        # Step 4: User can login with NEW password
        new_session = auth_manager.login("testuser", "MyNewPassword123!")
        assert new_session is not None
        assert auth_manager.validate_session(new_session) is True

        # Step 5: Old session is invalid (security requirement)
        assert auth_manager.validate_session(old_session) is False

        # Step 6: Old password no longer works
        with pytest.raises(AuthenticationError):
            auth_manager.login("testuser", "password123")
