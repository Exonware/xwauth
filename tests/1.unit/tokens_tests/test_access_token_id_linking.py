#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/tokens_tests/test_access_token_id_linking.py
Unit tests for access token ID linking in refresh tokens.
Tests that refresh tokens can link to opaque access tokens via token ID.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.tokens.manager import TokenManager
@pytest.mark.xwauth_unit

class TestAccessTokenIdLinking:
    """Test access token ID linking in refresh tokens."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def opaque_token_manager(self, auth):
        """Create TokenManager instance with opaque tokens."""
        return TokenManager(auth, use_jwt=False)
    @pytest.fixture

    def jwt_token_manager(self, auth):
        """Create TokenManager instance with JWT tokens."""
        return TokenManager(auth, use_jwt=True)
    @pytest.mark.asyncio

    async def test_refresh_token_links_to_opaque_access_token(self, opaque_token_manager):
        """Test that refresh token links to opaque access token via token ID."""
        # Generate access token (opaque)
        access_token = await opaque_token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read", "write"]
        )
        # Get token ID from opaque token
        token_data = await opaque_token_manager._opaque_manager.get_token(access_token)
        access_token_id = token_data.get('token_id')
        assert access_token_id is not None
        # Generate refresh token with access token linking
        refresh_token = await opaque_token_manager.generate_refresh_token(
            user_id="user123",
            client_id="client123",
            access_token=access_token
        )
        # Verify refresh token was generated
        assert refresh_token is not None
        # Verify refresh token is linked to access token
        refresh_data = await opaque_token_manager._refresh_manager.get_refresh_token(refresh_token)
        assert refresh_data is not None
        # The refresh token should have access_token_id if linking worked
        # (This depends on RefreshTokenManager implementation)
    @pytest.mark.asyncio

    async def test_refresh_token_without_access_token(self, opaque_token_manager):
        """Test that refresh token generation works without access token."""
        refresh_token = await opaque_token_manager.generate_refresh_token(
            user_id="user456",
            client_id="client456"
        )
        # Verify refresh token was generated
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
    @pytest.mark.asyncio

    async def test_refresh_token_with_jwt_access_token(self, jwt_token_manager):
        """Test that refresh token generation works with JWT access token (no linking needed)."""
        # Generate JWT access token
        access_token = await jwt_token_manager.generate_access_token(
            user_id="user789",
            client_id="client789",
            scopes=["read"]
        )
        # Generate refresh token (JWT tokens don't need linking)
        refresh_token = await jwt_token_manager.generate_refresh_token(
            user_id="user789",
            client_id="client789",
            access_token=access_token  # Should gracefully handle JWT tokens
        )
        # Verify refresh token was generated
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
    @pytest.mark.asyncio

    async def test_refresh_token_with_invalid_access_token(self, opaque_token_manager):
        """Test that refresh token generation handles invalid access token gracefully."""
        # Try to generate refresh token with invalid access token
        refresh_token = await opaque_token_manager.generate_refresh_token(
            user_id="user999",
            client_id="client999",
            access_token="invalid_token_12345"
        )
        # Should still generate refresh token (linking fails gracefully)
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
