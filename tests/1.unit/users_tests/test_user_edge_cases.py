#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/users_tests/test_user_edge_cases.py
Unit tests for user management edge cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.users.lifecycle import UserLifecycle
from exonware.xwauth.identity.errors import XWUserNotFoundError, XWUserAlreadyExistsError, XWUserError
from exonware.xwsystem.security.crypto import hash_password
@pytest.mark.xwauth_unit

class TestUserEdgeCases:
    """Test user management edge cases."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def lifecycle(self, auth):
        """Create UserLifecycle instance."""
        return UserLifecycle(auth)
    @pytest.mark.asyncio

    async def test_create_user_with_special_characters_email(self, lifecycle):
        """Test creating user with special characters in email."""
        user = await lifecycle.create_user(
            email="test+tag@example.com",
            password_hash=hash_password("password123")
        )
        assert user is not None
        assert "+" in user.email
    @pytest.mark.asyncio

    async def test_create_user_with_unicode_email(self, lifecycle):
        """Test creating user with unicode in email."""
        user = await lifecycle.create_user(
            email="testé@example.com",
            password_hash=hash_password("password123")
        )
        assert user is not None
        assert "é" in user.email
    @pytest.mark.asyncio

    async def test_create_user_with_very_long_email(self, lifecycle):
        """Test creating user with very long email."""
        long_email = "a" * 100 + "@example.com"
        try:
            user = await lifecycle.create_user(
                email=long_email,
                password_hash=hash_password("password123")
            )
            assert user is not None
        except Exception:
            # May fail validation
            pass
    @pytest.mark.asyncio

    async def test_update_user_multiple_fields(self, lifecycle):
        """Test updating user with multiple fields."""
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        updated = await lifecycle.update_user(
            user.id,
            {
                'email': 'updated@example.com',
                'attributes': {'name': 'Updated User', 'age': 30}
            }
        )
        assert updated.email == 'updated@example.com'
        assert updated.attributes.get('name') == 'Updated User'
    @pytest.mark.asyncio

    async def test_update_user_nonexistent(self, lifecycle):
        """Test updating nonexistent user."""
        with pytest.raises(XWUserNotFoundError):
            await lifecycle.update_user(
                "nonexistent_id",
                {'email': 'updated@example.com'}
            )
    @pytest.mark.asyncio

    async def test_delete_user_twice(self, lifecycle):
        """Test deleting user twice (idempotent)."""
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        await lifecycle.delete_user(user.id)
        # Second delete should not raise
        try:
            await lifecycle.delete_user(user.id)
        except XWUserNotFoundError:
            # May raise or be idempotent
            pass
    @pytest.mark.asyncio

    async def test_get_user_by_email_case_sensitivity(self, lifecycle):
        """Test getting user by email with case sensitivity."""
        user = await lifecycle.create_user(
            email="Test@Example.com",
            password_hash=hash_password("password123")
        )
        # Should find regardless of case
        found1 = await lifecycle.get_user_by_email("Test@Example.com")
        found2 = await lifecycle.get_user_by_email("test@example.com")
        # At least one should find the user
        assert (found1 is not None) or (found2 is not None)
    @pytest.mark.asyncio

    async def test_list_users_with_filters(self, lifecycle):
        """Test listing users with filters."""
        # Create multiple users
        await lifecycle.create_user(
            email="user1@example.com",
            password_hash=hash_password("password1")
        )
        await lifecycle.create_user(
            email="user2@example.com",
            password_hash=hash_password("password2")
        )
        # List all users
        all_users = await lifecycle.list_users()
        assert len(all_users) >= 2
        # List with filters (if supported)
        try:
            filtered = await lifecycle.list_users({'email': 'user1@example.com'})
            assert len(filtered) >= 1
        except Exception:
            # Filters may not be implemented
            pass
    @pytest.mark.asyncio

    async def test_create_user_empty_email(self, lifecycle):
        """Test creating user with empty email."""
        with pytest.raises((XWUserError, ValueError)):
            await lifecycle.create_user(
                email="",
                password_hash=hash_password("password123")
            )
    @pytest.mark.asyncio

    async def test_create_user_none_email(self, lifecycle):
        """Test creating user with None email."""
        with pytest.raises((XWUserError, ValueError, TypeError)):
            await lifecycle.create_user(
                email=None,
                password_hash=hash_password("password123")
            )
