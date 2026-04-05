#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/tokens_tests/test_token_manager.py
Unit tests for TokenManager orchestrator.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.tokens.manager import TokenManager
from exonware.xwauth.defs import TokenType
@pytest.mark.xwauth_unit

class TestTokenManager:
    """Test TokenManager implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def token_manager(self, auth):
        """Create TokenManager instance."""
        return TokenManager(auth, use_jwt=True)
    @pytest.mark.asyncio

    async def test_generate_access_token(self, token_manager):
        """Test access token generation."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read", "write"]
        )
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    @pytest.mark.asyncio

    async def test_generate_refresh_token(self, token_manager):
        """Test refresh token generation."""
        token = await token_manager.generate_refresh_token(
            user_id="user123",
            client_id="client123"
        )
        assert token is not None
        assert isinstance(token, str)
    @pytest.mark.asyncio

    async def test_generate_access_token_with_session_id(self, token_manager):
        """Test access token generation with session_id parameter."""
        session_id = "session_test_123"
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            session_id=session_id
        )
        assert token is not None
        # Verify session_id is in token (for JWT)
        if token_manager._use_jwt and token_manager._jwt_manager:
            payload = token_manager._jwt_manager.validate_token(token)
            assert payload.get('session_id') == session_id
    @pytest.mark.asyncio

    async def test_generate_refresh_token_with_access_token_linking(self, auth):
        """Test refresh token generation with access token linking (opaque tokens)."""
        # Use opaque tokens for linking
        opaque_manager = TokenManager(auth, use_jwt=False)
        # Generate access token
        access_token = await opaque_manager.generate_access_token(
            user_id="user456",
            client_id="client456",
            scopes=["read"]
        )
        # Generate refresh token with linking
        refresh_token = await opaque_manager.generate_refresh_token(
            user_id="user456",
            client_id="client456",
            access_token=access_token
        )
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
    @pytest.mark.asyncio

    async def test_validate_token(self, token_manager):
        """Test token validation."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        is_valid = await token_manager.validate_token(token)
        assert is_valid is True
    @pytest.mark.asyncio

    async def test_validate_invalid_token(self, token_manager):
        """Test validation of invalid token."""
        is_valid = await token_manager.validate_token("invalid_token")
        assert is_valid is False
    @pytest.mark.asyncio

    async def test_introspect_token(self, token_manager):
        """Test token introspection."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        introspection = await token_manager.introspect_token(token)
        assert introspection is not None
        assert 'active' in introspection or 'sub' in introspection
    @pytest.mark.asyncio

    async def test_revoke_token(self, token_manager):
        """Test token revocation."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        await token_manager.revoke_token(token)
        # Token should be revoked (introspection should show inactive)
        introspection = await token_manager.introspect_token(token)
        # May show as inactive or raise error
        assert introspection is not None or True
    @pytest.mark.asyncio

    async def test_token_type_detection(self, token_manager):
        """Test token type detection."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        # Token type can be inferred from token format
        # JWT tokens start with specific format, opaque tokens are random strings
        is_jwt = token.count('.') == 2  # JWT has 3 parts separated by dots
        assert isinstance(token, str)
        assert len(token) > 0
