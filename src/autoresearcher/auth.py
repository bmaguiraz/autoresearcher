# -*- coding: utf-8 -*-
"""Authentication module for autoresearcher.

Provides user authentication and password reset functionality.
Fixes: Properly invalidates sessions after password reset.
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """User account."""
    username: str
    password_hash: str
    created_at: float = field(default_factory=time.time)
    reset_token: Optional[str] = None
    reset_token_expires: Optional[float] = None
    # CRITICAL FIX: Track password version to invalidate old sessions
    password_version: int = 0


@dataclass
class Session:
    """User session."""
    session_id: str
    username: str
    created_at: float
    # CRITICAL FIX: Store password version with session
    password_version: int


class AuthenticationError(Exception):
    """Authentication failed."""
    pass


class PasswordResetError(Exception):
    """Password reset failed."""
    pass


class AuthManager:
    """Manages user authentication and password resets.

    Key fix: Sessions are tied to password_version. When password is reset,
    the version increments, automatically invalidating all old sessions.
    """

    def __init__(self):
        self.users: dict[str, User] = {}
        self.sessions: dict[str, Session] = {}

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str) -> User:
        """Create a new user account."""
        if username in self.users:
            raise ValueError(f"User {username} already exists")

        user = User(
            username=username,
            password_hash=self._hash_password(password),
            password_version=0
        )
        self.users[username] = user
        return user

    def login(self, username: str, password: str) -> str:
        """Authenticate user and create session.

        Returns:
            session_id for the authenticated session
        """
        if username not in self.users:
            raise AuthenticationError("Invalid username or password")

        user = self.users[username]
        password_hash = self._hash_password(password)

        if user.password_hash != password_hash:
            raise AuthenticationError("Invalid username or password")

        # Create new session tied to current password version
        session_id = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            username=username,
            created_at=time.time(),
            password_version=user.password_version
        )
        self.sessions[session_id] = session
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """Validate a session.

        CRITICAL FIX: Sessions are invalidated if password_version doesn't match.
        This automatically logs out all sessions when password is reset.
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        user = self.users.get(session.username)

        if not user:
            return False

        # FIX: Check password version match
        if session.password_version != user.password_version:
            # Password was reset - this session is invalid
            del self.sessions[session_id]
            return False

        return True

    def logout(self, session_id: str) -> None:
        """Log out a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def request_password_reset(self, username: str) -> str:
        """Request a password reset token.

        Returns:
            reset_token to be sent to user (e.g., via email)
        """
        if username not in self.users:
            # Don't reveal if user exists
            raise PasswordResetError("If the user exists, a reset email will be sent")

        user = self.users[username]
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        # Token valid for 1 hour
        user.reset_token_expires = time.time() + 3600

        return reset_token

    def reset_password(self, username: str, reset_token: str, new_password: str) -> None:
        """Reset user password using reset token.

        CRITICAL FIX: Increments password_version to invalidate all sessions.
        This ensures users must re-login after password reset.
        """
        if username not in self.users:
            raise PasswordResetError("Invalid reset token")

        user = self.users[username]

        # Validate reset token
        if not user.reset_token or user.reset_token != reset_token:
            raise PasswordResetError("Invalid reset token")

        if not user.reset_token_expires or time.time() > user.reset_token_expires:
            raise PasswordResetError("Reset token has expired")

        # Update password
        user.password_hash = self._hash_password(new_password)

        # FIX: Increment password version to invalidate all existing sessions
        user.password_version += 1

        # Clear reset token
        user.reset_token = None
        user.reset_token_expires = None

        # FIX: Explicitly clean up old sessions for this user
        # (They'll be rejected on next validate_session call anyway)
        sessions_to_remove = [
            sid for sid, session in self.sessions.items()
            if session.username == username and session.password_version < user.password_version
        ]
        for sid in sessions_to_remove:
            del self.sessions[sid]
