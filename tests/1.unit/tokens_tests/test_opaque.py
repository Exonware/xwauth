#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/tokens_tests/test_opaque.py
Unit tests for opaque token management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.tokens.opaque import OpaqueTokenManager
from exonware.xwauth.identity.storage.mock import MockStorageProvider
from exonware.xwauth.identity.errors import XWExpiredTokenError, XWInvalidTokenError
@pytest.mark.xwauth_unit

class TestOpaqueTokenManager:
    """Test OpaqueTokenManager implementation."""
    @pytest.fixture

    def storage(self):
        """Create mock storage."""
        return MockStorageProvider()
    @pytest.fixture

    def opaque_manager(self, storage):
        """Create OpaqueTokenManager instance."""
        return OpaqueTokenManager(storage)
    @pytest.mark.asyncio

    async def test_generate_token(self, opaque_manager):
        """Test token generation."""
        token = opaque_manager.generate_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    @pytest.mark.asyncio

    async def test_save_and_get_token(self, opaque_manager):
        """Test saving and retrieving token."""
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read", "write"],
            expires_in=3600
        )
        token_data = await opaque_manager.get_token(token)
        assert token_data is not None
        assert token_data['user_id'] == 'user123'
        assert token_data['client_id'] == 'client123'
        assert 'read' in token_data['scopes']
        assert 'write' in token_data['scopes']
    @pytest.mark.asyncio

    async def test_validate_token(self, opaque_manager):
        """Test token validation."""
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        token_data = await opaque_manager.validate_token(token)
        assert token_data is not None
        assert token_data['user_id'] == 'user123'
    @pytest.mark.asyncio

    async def test_validate_token_invalid(self, opaque_manager):
        """Test token validation with invalid token."""
        with pytest.raises(XWInvalidTokenError):
            await opaque_manager.validate_token("invalid_token")
    @pytest.mark.asyncio

    async def test_revoke_token(self, opaque_manager):
        """Test token revocation."""
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        # Revoke token
        await opaque_manager.revoke_token(token)
        # Token should no longer be retrievable
        token_data = await opaque_manager.get_token(token)
        assert token_data is None
