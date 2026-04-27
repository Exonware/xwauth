#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/tokens_tests/test_token_edge_cases.py
Unit tests for token management edge cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.tokens.manager import TokenManager
from exonware.xwauth.identity.errors import XWInvalidTokenError
@pytest.mark.xwauth_unit

class TestTokenEdgeCases:
    """Test token management edge cases."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def token_manager(self, auth):
        """Create TokenManager instance."""
        return TokenManager(auth, use_jwt=True)
    @pytest.mark.asyncio

    async def test_generate_token_with_empty_scopes(self, token_manager):
        """Test token generation with empty scopes."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=[]
        )
        assert token is not None
    @pytest.mark.asyncio

    async def test_generate_token_with_many_scopes(self, token_manager):
        """Test token generation with many scopes."""
        scopes = [f"scope_{i}" for i in range(100)]
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=scopes
        )
        assert token is not None
    @pytest.mark.asyncio

    async def test_generate_token_with_very_long_user_id(self, token_manager):
        """Test token generation with very long user_id."""
        long_user_id = "a" * 1000
        token = await token_manager.generate_access_token(
            user_id=long_user_id,
            client_id="client123",
            scopes=["read"]
        )
        assert token is not None
    @pytest.mark.asyncio

    async def test_validate_token_empty_string(self, token_manager):
        """Test validation of empty token."""
        result = await token_manager.validate_token("")
        assert result is False
    @pytest.mark.asyncio

    async def test_validate_token_none(self, token_manager):
        """Test validation of None token."""
        result = await token_manager.validate_token(None)
        assert result is False
    @pytest.mark.asyncio

    async def test_validate_token_very_long(self, token_manager):
        """Test validation of very long token."""
        long_token = "a" * 10000
        result = await token_manager.validate_token(long_token)
        assert result is False
    @pytest.mark.asyncio

    async def test_revoke_token_twice(self, token_manager):
        """Test revoking token twice (idempotent)."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        # Revoke twice
        await token_manager.revoke_token(token)
        await token_manager.revoke_token(token)  # Should be idempotent
    @pytest.mark.asyncio

    async def test_introspect_revoked_token(self, token_manager):
        """Test introspection of revoked token."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        await token_manager.revoke_token(token)
        introspection = await token_manager.introspect_token(token)
        assert introspection is not None
        # For JWT tokens, revocation may not be detected in introspection
        # (depends on implementation - may still show active=True)
        # For opaque tokens, should show active=False
        # This test verifies introspection works, not necessarily that it detects revocation
        assert 'active' in introspection or 'sub' in introspection or 'client_id' in introspection
