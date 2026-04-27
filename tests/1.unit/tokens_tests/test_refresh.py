#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/tokens_tests/test_refresh.py
Unit tests for refresh token management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.tokens.refresh import RefreshTokenManager
from exonware.xwauth.identity.storage.mock import MockStorageProvider
from exonware.xwauth.identity.errors import XWInvalidTokenError, XWExpiredTokenError
@pytest.mark.xwauth_unit

class TestRefreshTokenManager:
    """Test RefreshTokenManager implementation."""
    @pytest.fixture

    def storage(self):
        """Create mock storage."""
        return MockStorageProvider()
    @pytest.fixture

    def refresh_manager(self, storage):
        """Create RefreshTokenManager instance."""
        return RefreshTokenManager(storage, enable_rotation=True)
    @pytest.mark.asyncio

    async def test_generate_refresh_token(self, refresh_manager):
        """Test refresh token generation."""
        token = refresh_manager.generate_refresh_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    @pytest.mark.asyncio

    async def test_save_and_get_refresh_token(self, refresh_manager):
        """Test saving and retrieving refresh token."""
        token = refresh_manager.generate_refresh_token()
        await refresh_manager.save_refresh_token(
            refresh_token=token,
            access_token_id="access123",
            user_id="user123",
            client_id="client123",
            expires_in=86400 * 7
        )
        token_data = await refresh_manager.get_refresh_token(token)
        assert token_data is not None
        assert token_data['user_id'] == 'user123'
        assert token_data['client_id'] == 'client123'
        assert token_data['access_token_id'] == 'access123'
    @pytest.mark.asyncio

    async def test_validate_refresh_token(self, refresh_manager):
        """Test refresh token validation."""
        token = refresh_manager.generate_refresh_token()
        await refresh_manager.save_refresh_token(
            refresh_token=token,
            access_token_id="access123",
            user_id="user123",
            client_id="client123",
            expires_in=86400 * 7
        )
        token_data = await refresh_manager.validate_refresh_token(token)
        assert token_data is not None
        assert token_data['user_id'] == 'user123'
    @pytest.mark.asyncio

    async def test_validate_refresh_token_invalid(self, refresh_manager):
        """Test refresh token validation with invalid token."""
        with pytest.raises(XWInvalidTokenError):
            await refresh_manager.validate_refresh_token("invalid_token")
    @pytest.mark.asyncio

    async def test_revoke_refresh_token(self, refresh_manager):
        """Test refresh token revocation."""
        token = refresh_manager.generate_refresh_token()
        await refresh_manager.save_refresh_token(
            refresh_token=token,
            access_token_id="access123",
            user_id="user123",
            client_id="client123",
            expires_in=86400 * 7
        )
        # Revoke token
        await refresh_manager.revoke_refresh_token(token)
        # Token should no longer be retrievable
        token_data = await refresh_manager.get_refresh_token(token)
        assert token_data is None
    @pytest.mark.asyncio

    async def test_rotate_refresh_token(self, refresh_manager):
        """Test refresh token rotation."""
        old_token = refresh_manager.generate_refresh_token()
        await refresh_manager.save_refresh_token(
            refresh_token=old_token,
            access_token_id="access123",
            user_id="user123",
            client_id="client123",
            expires_in=86400 * 7
        )
        # Rotate token
        new_token = await refresh_manager.rotate_refresh_token(old_token)
        assert new_token is not None
        assert new_token != old_token
        # Old token should be revoked
        old_token_data = await refresh_manager.get_refresh_token(old_token)
        assert old_token_data is None
        # New token should be valid
        new_token_data = await refresh_manager.get_refresh_token(new_token)
        assert new_token_data is not None
