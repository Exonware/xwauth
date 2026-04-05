#!/usr/bin/env python3
"""
#exonware/xwauth/tests/2.integration/test_error_recovery.py
Error Recovery Integration Tests
Integration tests for error recovery and resilience.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import sys
from pathlib import Path
# Add src to path for testing
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.errors import (
    XWInvalidRequestError,
    XWInvalidTokenError,
    XWInvalidCredentialsError,
    XWUserNotFoundError
)
@pytest.mark.xwauth_integration

class TestErrorRecovery:
    """Error recovery integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance with registered client for token flow."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=[
                {"client_id": "test_client", "client_secret": "test_secret", "redirect_uris": ["https://example.com/cb"]}
            ],
        )
        return XWAuth(config=config)
    @pytest.mark.asyncio

    async def test_recover_from_invalid_token(self, auth):
        """Test recovery from invalid token."""
        # Try to introspect invalid token
        try:
            await auth.introspect_token("invalid_token")
        except XWInvalidTokenError:
            # Should handle gracefully
            pass
        # System should still work
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        }
        response = await auth.token(token_request)
        assert 'access_token' in response
    @pytest.mark.asyncio

    async def test_recover_from_expired_session(self, auth):
        """Test recovery from expired session."""
        from exonware.xwauth.sessions.manager import SessionManager
        from exonware.xwauth.errors import XWSessionExpiredError
        session_manager = SessionManager(auth)
        # Create expired session
        session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=-1  # Already expired
        )
        import time
        time.sleep(0.1)
        # Try to get expired session
        try:
            session_data = await session_manager.get_session(session_id)
            assert session_data['status'] == 'expired'
        except XWSessionExpiredError:
            pass
        # Should be able to create new session
        new_session_id = await session_manager.create_session(
            user_id="user123",
            expires_in=3600
        )
        assert new_session_id is not None
    @pytest.mark.asyncio

    async def test_recover_from_invalid_credentials(self, auth):
        """Test recovery from invalid credentials."""
        from exonware.xwlogin.authentication.email_password import EmailPasswordAuthenticator
        from exonware.xwauth.storage.mock import MockUser
        from exonware.xwsystem.security.crypto import hash_password
        authenticator = EmailPasswordAuthenticator(auth)
        # Create user
        user = MockUser(
            id="recovery_user",
            email="recovery@example.com",
            password_hash=hash_password("correct_password")
        )
        await auth.storage.save_user(user)
        # Try wrong password
        try:
            await authenticator.authenticate({
                'email': 'recovery@example.com',
                'password': 'wrong_password'
            })
            assert False, "Should raise error"
        except XWInvalidCredentialsError:
            pass
        # Should still work with correct password
        user_id = await authenticator.authenticate({
            'email': 'recovery@example.com',
            'password': 'correct_password'
        })
        assert user_id == "recovery_user"
    @pytest.mark.asyncio

    async def test_recover_from_missing_user(self, auth):
        """Test recovery from missing user operations."""
        from exonware.xwauth.users.lifecycle import UserLifecycle
        from exonware.xwsystem.security.crypto import hash_password
        lifecycle = UserLifecycle(auth)
        # Try to get nonexistent user
        user = await lifecycle.get_user("nonexistent")
        assert user is None
        # Should still be able to create new user
        new_user = await lifecycle.create_user(
            email="new@example.com",
            password_hash=hash_password("password123")
        )
        assert new_user is not None
    @pytest.mark.asyncio

    async def test_recover_from_rate_limit(self, auth):
        """Test recovery from rate limiting."""
        from exonware.xwauth.security.rate_limit import RateLimiter
        rate_limiter = RateLimiter(requests_per_minute=3)
        identifier = "rate_limit_recovery"
        # Exceed limit
        for i in range(3):
            rate_limiter.check_rate_limit(identifier)
        # Should be rate limited
        assert rate_limiter.check_rate_limit(identifier) is False
        # Different identifier should still work
        assert rate_limiter.check_rate_limit("different_client") is True
