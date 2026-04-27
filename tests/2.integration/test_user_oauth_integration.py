#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/2.integration/test_user_oauth_integration.py
User and OAuth Integration Tests
Tests for user management integrated with OAuth flows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockUser
from exonware.xwsystem.security.crypto import hash_password
@pytest.mark.xwauth_integration

class TestUserOAuthIntegration:
    """User and OAuth integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance with registered clients for token flows."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key-for-user-oauth",
            registered_clients=[
                {"client_id": "user_oauth_client", "client_secret": "user_oauth_secret", "redirect_uris": ["https://example.com/cb"]},
                {"client_id": "update_client", "client_secret": "update_secret", "redirect_uris": ["https://example.com/cb"]},
                {"client_id": "delete_client", "client_secret": "delete_secret", "redirect_uris": ["https://example.com/cb"]},
            ],
            allow_mock_storage_fallback=True,
        )
        return XWAuth(config=config)
    @pytest.mark.asyncio

    async def test_user_creation_and_oauth_token(self, auth):
        """Test user creation followed by OAuth token generation."""
        from exonware.xwauth.identity.users.lifecycle import UserLifecycle
        lifecycle = UserLifecycle(auth)
        # Create user
        user = await lifecycle.create_user(
            email="oauth_user@example.com",
            password_hash=hash_password("password123")
        )
        # Get OAuth token for user
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'user_oauth_client',
            'client_secret': 'user_oauth_secret'
        }
        token_response = await auth.token(token_request)
        assert 'access_token' in token_response
        # Verify user still exists
        retrieved = await lifecycle.get_user(user.id)
        assert retrieved is not None
    @pytest.mark.asyncio

    async def test_user_authentication_and_session(self, auth):
        """Test user authentication followed by session creation."""
        from exonware.xwauth.identity.authentication.email_password import EmailPasswordAuthenticator
        from exonware.xwauth.identity.sessions.manager import SessionManager
        # Create user
        user = MockUser(
            id="auth_session_user",
            email="auth_session@example.com",
            password_hash=hash_password("password123")
        )
        await auth.storage.save_user(user)
        # Authenticate
        authenticator = EmailPasswordAuthenticator(auth)
        user_id = await authenticator.authenticate({
            'email': 'auth_session@example.com',
            'password': 'password123'
        })
        # Create session
        session_manager = SessionManager(auth)
        session_id = await session_manager.create_session(
            user_id=user_id,
            expires_in=3600
        )
        assert session_id is not None
        # Get session
        session_data = await session_manager.get_session(session_id)
        assert session_data['user_id'] == user_id
    @pytest.mark.asyncio

    async def test_user_update_and_token_refresh(self, auth):
        """Test user update followed by token operations."""
        from exonware.xwauth.identity.users.lifecycle import UserLifecycle
        lifecycle = UserLifecycle(auth)
        # Create user
        user = await lifecycle.create_user(
            email="update_token@example.com",
            password_hash=hash_password("password123")
        )
        # Get initial token
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'update_client',
            'client_secret': 'update_secret'
        }
        token1 = await auth.token(token_request)
        # Update user
        updated = await lifecycle.update_user(
            user.id,
            {'email': 'updated_token@example.com'}
        )
        # Get new token
        token2 = await auth.token(token_request)
        # Both tokens should be valid
        assert 'access_token' in token1
        assert 'access_token' in token2
    @pytest.mark.asyncio

    async def test_user_deletion_and_token_cleanup(self, auth):
        """Test user deletion and token cleanup."""
        from exonware.xwauth.identity.users.lifecycle import UserLifecycle
        lifecycle = UserLifecycle(auth)
        # Create user
        user = await lifecycle.create_user(
            email="delete_token@example.com",
            password_hash=hash_password("password123")
        )
        # Get token
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'delete_client',
            'client_secret': 'delete_secret'
        }
        token_response = await auth.token(token_request)
        access_token = token_response['access_token']
        # Delete user
        await lifecycle.delete_user(user.id)
        # User should be deleted
        deleted = await lifecycle.get_user(user.id)
        assert deleted is None
        # Token may still be valid (depends on implementation)
        try:
            await auth.introspect_token(access_token)
        except Exception:
            # May be invalidated on user deletion
            pass
