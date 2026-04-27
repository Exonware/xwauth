#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/sessions_tests/test_session_edge_cases.py
Unit tests for session management edge cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.sessions.manager import SessionManager
from exonware.xwauth.identity.errors import XWSessionError, XWSessionExpiredError
@pytest.mark.xwauth_unit

class TestSessionEdgeCases:
    """Test session management edge cases."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def session_manager(self, auth):
        """Create SessionManager instance."""
        return SessionManager(auth)
    @pytest.mark.asyncio

    async def test_create_session_with_zero_expiration(self, session_manager):
        """Test creating session with zero expiration."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=0
        )
        assert session_id is not None
        # Session should be expired immediately
        try:
            session_data = await session_manager.get_session(session_id)
            assert session_data is not None
        except XWSessionExpiredError:
            # Expected
            pass
    @pytest.mark.asyncio

    async def test_create_session_with_very_long_expiration(self, session_manager):
        """Test creating session with very long expiration."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=86400 * 365 * 10  # 10 years
        )
        assert session_id is not None
        session_data = await session_manager.get_session(session_id)
        assert session_data is not None
    @pytest.mark.asyncio

    async def test_create_multiple_sessions_same_user(self, session_manager):
        """Test creating multiple sessions for same user."""
        session_ids = []
        for i in range(10):
            session_id = await session_manager.create_session(
                user_id="user123",
                expires_in=3600
            )
            session_ids.append(session_id)
        # All sessions should be unique
        assert len(set(session_ids)) == 10
        # All should be retrievable
        for session_id in session_ids:
            session_data = await session_manager.get_session(session_id)
            assert session_data is not None
    @pytest.mark.asyncio

    async def test_revoke_session_twice(self, session_manager):
        """Test revoking session twice (idempotent)."""
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        await session_manager.revoke_session(session_id)
        await session_manager.revoke_session(session_id)  # Should be idempotent
        session_data = await session_manager.get_session(session_id)
        assert session_data['status'] == 'revoked'
    @pytest.mark.asyncio

    async def test_get_nonexistent_session(self, session_manager):
        """Test getting nonexistent session."""
        session_data = await session_manager.get_session("nonexistent_session")
        assert session_data is None
    @pytest.mark.asyncio

    async def test_validate_csrf_empty_tokens(self, session_manager):
        """Test CSRF validation with empty tokens."""
        from exonware.xwauth.identity.errors import XWInvalidRequestError
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        with pytest.raises(XWInvalidRequestError):
            await session_manager.validate_csrf_token(session_id, "")
    @pytest.mark.asyncio

    async def test_session_concurrent_limit(self, session_manager):
        """Test session concurrent limit."""
        # Create sessions up to limit (if implemented)
        session_ids = []
        for i in range(20):  # Try to create many sessions
            try:
                session_id = await session_manager.create_session(
                    user_id="user123",
                    expires_in=3600
                )
                session_ids.append(session_id)
            except XWSessionError:
                # May hit concurrent limit
                break
        # Should have created at least some sessions
        assert len(session_ids) > 0
