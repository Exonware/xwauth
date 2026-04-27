#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/users_tests/test_user_lifecycle.py
Unit tests for user lifecycle management.
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
from exonware.xwauth.identity.errors import XWUserNotFoundError, XWUserAlreadyExistsError
@pytest.mark.xwauth_unit

class TestUserLifecycle:
    """Test UserLifecycle implementation."""
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

    async def test_create_user(self, lifecycle):
        """Test user creation."""
        from exonware.xwsystem.security.crypto import hash_password
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        assert user is not None
        assert user.email == "test@example.com"
        assert user.id is not None
    @pytest.mark.asyncio

    async def test_create_user_duplicate_email(self, lifecycle):
        """Test creating user with duplicate email."""
        from exonware.xwsystem.security.crypto import hash_password
        await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        with pytest.raises(XWUserAlreadyExistsError):
            await lifecycle.create_user(
                email="test@example.com",
                password_hash=hash_password("anotherpassword")
            )
    @pytest.mark.asyncio

    async def test_get_user(self, lifecycle):
        """Test getting user."""
        from exonware.xwsystem.security.crypto import hash_password
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        retrieved = await lifecycle.get_user(user.id)
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email
    @pytest.mark.asyncio

    async def test_get_user_not_found(self, lifecycle):
        """Test getting non-existent user."""
        user = await lifecycle.get_user("nonexistent_id")
        assert user is None
    @pytest.mark.asyncio

    async def test_get_user_by_email(self, lifecycle):
        """Test getting user by email."""
        from exonware.xwsystem.security.crypto import hash_password
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        retrieved = await lifecycle.get_user_by_email("test@example.com")
        assert retrieved is not None
        assert retrieved.id == user.id
    @pytest.mark.asyncio

    async def test_update_user(self, lifecycle):
        """Test updating user."""
        from exonware.xwsystem.security.crypto import hash_password
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        updated = await lifecycle.update_user(
            user.id,
            {"email": "updated@example.com"}
        )
        assert updated.email == "updated@example.com"
    @pytest.mark.asyncio

    async def test_update_user_not_found(self, lifecycle):
        """Test updating non-existent user."""
        with pytest.raises(XWUserNotFoundError):
            await lifecycle.update_user(
                "nonexistent_id",
                {"email": "updated@example.com"}
            )
    @pytest.mark.asyncio

    async def test_delete_user(self, lifecycle):
        """Test deleting user."""
        from exonware.xwsystem.security.crypto import hash_password
        user = await lifecycle.create_user(
            email="test@example.com",
            password_hash=hash_password("testpassword123")
        )
        await lifecycle.delete_user(user.id)
        deleted = await lifecycle.get_user(user.id)
        assert deleted is None
    @pytest.mark.asyncio

    async def test_delete_user_not_found(self, lifecycle):
        """Test deleting non-existent user."""
        with pytest.raises(XWUserNotFoundError):
            await lifecycle.delete_user("nonexistent_id")
    @pytest.mark.asyncio

    async def test_list_users(self, lifecycle):
        """Test listing users."""
        from exonware.xwsystem.security.crypto import hash_password
        await lifecycle.create_user(
            email="user1@example.com",
            password_hash=hash_password("password1")
        )
        await lifecycle.create_user(
            email="user2@example.com",
            password_hash=hash_password("password2")
        )
        users = await lifecycle.list_users()
        assert len(users) >= 2
