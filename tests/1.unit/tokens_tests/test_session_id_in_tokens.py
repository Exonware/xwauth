#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/tokens_tests/test_session_id_in_tokens.py
Unit tests for session_id in token claims functionality.
Tests that session_id is properly included in JWT and opaque tokens,
and can be extracted from tokens.
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
class TestSessionIdInJWTTokens:
    """Test session_id in JWT tokens."""
    @pytest.fixture
    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture
    def token_manager(self, auth):
        """Create TokenManager instance with JWT."""
        return TokenManager(auth, use_jwt=True)
    @pytest.mark.asyncio
    async def test_generate_jwt_token_with_session_id(self, token_manager):
        """Test that JWT tokens include session_id when provided."""
        session_id = "session_12345"
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read", "write"],
            session_id=session_id
        )
        # Verify token is generated
        assert token is not None
        assert isinstance(token, str)
        # Decode and verify session_id is in claims
        payload = token_manager._jwt_manager.validate_token(token)
        assert payload is not None
        assert payload.get('session_id') == session_id
    @pytest.mark.asyncio
    async def test_generate_jwt_token_without_session_id(self, token_manager):
        """Test that JWT tokens work without session_id."""
        token = await token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"]
        )
        # Verify token is generated
        assert token is not None
        # Decode and verify session_id is not present
        payload = token_manager._jwt_manager.validate_token(token)
        assert payload is not None
        assert 'session_id' not in payload or payload.get('session_id') is None
    @pytest.mark.asyncio
    async def test_extract_session_id_from_jwt(self, token_manager):
        """Test extracting session_id from JWT token."""
        session_id = "session_67890"
        token = await token_manager.generate_access_token(
            user_id="user456",
            client_id="client456",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id
        payload = token_manager._jwt_manager.validate_token(token)
        extracted_session_id = payload.get('session_id')
        assert extracted_session_id == session_id
@pytest.mark.xwauth_unit
class TestSessionIdInOpaqueTokens:
    """Test session_id in opaque tokens."""
    @pytest.fixture
    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture
    def token_manager(self, auth):
        """Create TokenManager instance with opaque tokens."""
        return TokenManager(auth, use_jwt=False)
    @pytest.mark.asyncio
    async def test_generate_opaque_token_with_session_id(self, token_manager):
        """Test that opaque tokens store session_id in attributes."""
        session_id = "session_opaque_123"
        token = await token_manager.generate_access_token(
            user_id="user789",
            client_id="client789",
            scopes=["read"],
            session_id=session_id
        )
        # Verify token is generated
        assert token is not None
        # Retrieve token data and verify session_id
        token_data = await token_manager._opaque_manager.get_token(token)
        assert token_data is not None
        assert token_data.get('attributes', {}).get('session_id') == session_id
    @pytest.mark.asyncio
    async def test_generate_opaque_token_without_session_id(self, token_manager):
        """Test that opaque tokens work without session_id."""
        token = await token_manager.generate_access_token(
            user_id="user999",
            client_id="client999",
            scopes=["read"]
        )
        # Verify token is generated
        assert token is not None
        # Retrieve token data
        token_data = await token_manager._opaque_manager.get_token(token)
        assert token_data is not None
        # session_id should not be present or be None
        assert 'session_id' not in token_data.get('attributes', {}) or \
               token_data.get('attributes', {}).get('session_id') is None
    @pytest.mark.asyncio
    async def test_extract_session_id_from_opaque(self, token_manager):
        """Test extracting session_id from opaque token."""
        session_id = "session_opaque_456"
        token = await token_manager.generate_access_token(
            user_id="user111",
            client_id="client111",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id
        token_data = await token_manager._opaque_manager.get_token(token)
        extracted_session_id = token_data.get('attributes', {}).get('session_id')
        assert extracted_session_id == session_id
