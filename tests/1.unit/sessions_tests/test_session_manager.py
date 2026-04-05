#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/sessions_tests/test_session_manager.py
Unit tests for session management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.storage.mock import MockStorageProvider
from exonware.xwauth.sessions.manager import SessionManager
from exonware.xwauth.errors import XWSessionExpiredError, XWSessionError, XWInvalidRequestError
@pytest.mark.xwauth_unit

class TestSessionManager:
    """Test SessionManager implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def session_manager(self, auth):
        """Create SessionManager instance."""
        return SessionManager(auth)
    @pytest.mark.asyncio

    async def test_create_session(self, session_manager):
        """Test session creation."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    @pytest.mark.asyncio

    async def test_get_session(self, session_manager):
        """Test getting session."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        session_data = await session_manager.get_session(session_id)
        assert session_data is not None
        assert session_data['user_id'] == 'user123'
        assert session_data['status'] == 'active'
    @pytest.mark.asyncio

    async def test_revoke_session(self, session_manager):
        """Test session revocation."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        await session_manager.revoke_session(session_id)
        # Session should still exist but be revoked
        session_data = await session_manager.get_session(session_id)
        assert session_data['status'] == 'revoked'
    @pytest.mark.asyncio

    async def test_validate_csrf_token(self, session_manager):
        """Test CSRF token validation."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        session_data = await session_manager.get_session(session_id)
        csrf_token = session_data.get('csrf_token')
        if csrf_token:
            # Should not raise
            assert await session_manager.validate_csrf_token(session_id, csrf_token) is True
    @pytest.mark.asyncio

    async def test_validate_csrf_token_invalid(self, session_manager):
        """Test CSRF token validation with invalid token."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        # Should raise XWSessionError or XWInvalidRequestError
        with pytest.raises((XWSessionError, XWInvalidRequestError)):
            await session_manager.validate_csrf_token(session_id, "invalid_csrf_token")
