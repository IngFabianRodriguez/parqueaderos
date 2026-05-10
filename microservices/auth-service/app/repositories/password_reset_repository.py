"""Password reset token repository for database operations."""

from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base
from app.db.session import AsyncSessionLocal


class PasswordResetTokenRepository:
    """Repository for PasswordResetToken database operations.

    Note: Uses a separate table for password reset tokens to support
    email-based password reset flow. In this implementation, we use
    an in-memory approach for simplicity since the models.py doesn't
    define a PasswordResetToken model. If a real table is needed,
    add a PasswordResetToken model to models.py.
    """

    # In-memory store for password reset tokens (for testing/dev)
    # In production, this would be a database table
    _tokens: dict = {}

    @classmethod
    async def create_token(
        cls,
        user_id: str,
        email: str,
        token: str,
        expires_in_hours: int = 24,
    ) -> dict:
        """Create a password reset token."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        token_data = {
            "id": token,
            "user_id": user_id,
            "email": email,
            "token": token,
            "expires_at": expires_at,
            "is_used": False,
            "created_at": datetime.utcnow(),
        }
        cls._tokens[token] = token_data
        return token_data

    @classmethod
    async def get_valid_token(cls, token: str) -> Optional[dict]:
        """Get a valid (non-expired, non-used) token."""
        token_data = cls._tokens.get(token)
        if not token_data:
            return None
        if token_data["is_used"]:
            return None
        if token_data["expires_at"] < datetime.utcnow():
            return None
        return token_data

    @classmethod
    async def mark_token_used(cls, token: str) -> bool:
        """Mark a token as used."""
        if token in cls._tokens:
            cls._tokens[token]["is_used"] = True
            return True
        return False

    @classmethod
    async def get_token_by_user(cls, user_id: str) -> Optional[dict]:
        """Get the most recent valid token for a user."""
        valid_tokens = [
            t for t in cls._tokens.values()
            if t["user_id"] == user_id
            and not t["is_used"]
            and t["expires_at"] > datetime.utcnow()
        ]
        if not valid_tokens:
            return None
        return max(valid_tokens, key=lambda t: t["created_at"])

    @classmethod
    async def delete_token(cls, token: str) -> bool:
        """Delete a token."""
        if token in cls._tokens:
            del cls._tokens[token]
            return True
        return False

    @classmethod
    async def delete_user_tokens(cls, user_id: str) -> int:
        """Delete all tokens for a user. Returns count of deleted tokens."""
        tokens_to_delete = [
            token for token, data in cls._tokens.items()
            if data["user_id"] == user_id
        ]
        for token in tokens_to_delete:
            del cls._tokens[token]
        return len(tokens_to_delete)

    @classmethod
    def clear_all(cls) -> None:
        """Clear all tokens (for testing)."""
        cls._tokens.clear()


password_reset_token_repository = PasswordResetTokenRepository()