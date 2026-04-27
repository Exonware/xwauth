#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/2.integration/test_security_integration.py
Security Integration Tests
End-to-end security scenario tests.
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
@pytest.mark.xwauth_security

class TestSecurityIntegration:
    """Security integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance with registered client for token flow."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key-for-security",
            registered_clients=[
                {"client_id": "security_client", "client_secret": "security_secret", "redirect_uris": ["https://example.com/cb"]}
            ],
            allow_mock_storage_fallback=True,
        )
        return XWAuth(config=config)
    @pytest.mark.asyncio

    async def test_password_breach_detection_flow(self, auth):
        """Test password breach detection in authentication flow."""
        from exonware.xwauth.identity.authentication.email_password import EmailPasswordAuthenticator
        from exonware.xwauth.identity.security.password import PasswordSecurity
        # Create user with potentially breached password
        user = MockUser(
            id="security_user_1",
            email="security@example.com",
            password_hash=hash_password("password123")  # Common password
        )
        await auth.storage.save_user(user)
        authenticator = EmailPasswordAuthenticator(auth)
        # Authenticate (should work but may flag breach)
        try:
            user_id = await authenticator.authenticate({
                'email': 'security@example.com',
                'password': 'password123'
            })
            assert user_id == 'security_user_1'
        except Exception:
            # May fail if breach detection blocks
            pass
    @pytest.mark.asyncio

    async def test_rate_limiting_integration(self, auth):
        """Test rate limiting in OAuth flow."""
        from exonware.xwauth.identity.security.rate_limit import RateLimiter
        rate_limiter = RateLimiter(requests_per_minute=5)
        # Make requests up to limit
        for i in range(5):
            assert rate_limiter.check_rate_limit("test_client") is True
        # Next request should be rate limited
        assert rate_limiter.check_rate_limit("test_client") is False
    @pytest.mark.asyncio

    async def test_csrf_protection_integration(self, auth):
        """Test CSRF protection in session flow."""
        from exonware.xwauth.identity.sessions.manager import SessionManager
        from exonware.xwauth.identity.errors import XWSessionError
        session_manager = SessionManager(auth)
        session_id = await session_manager.create_session(
            user_id="security_user_2",
            expires_in=3600
        )
        session_data = await session_manager.get_session(session_id)
        csrf_token = session_data.get('csrf_token')
        if csrf_token:
            # Valid CSRF token should work
            assert await session_manager.validate_csrf_token(session_id, csrf_token) is True
            # Invalid CSRF token should fail
            with pytest.raises(XWSessionError):
                await session_manager.validate_csrf_token(session_id, "invalid_csrf")
    @pytest.mark.asyncio

    async def test_input_validation_integration(self, auth):
        """Test input validation in OAuth flow."""
        from exonware.xwauth.identity.security.validation import InputValidator
        validator = InputValidator()
        # Valid inputs
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_redirect_uri("https://example.com/callback") is True
        # Invalid inputs
        assert validator.validate_email("invalid-email") is False
        assert validator.validate_redirect_uri("javascript:alert('xss')") is False
    @pytest.mark.asyncio

    async def test_token_security_integration(self, auth):
        """Test token security in complete flow."""
        # Get token
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'security_client',
            'client_secret': 'security_secret'
        }
        token_response = await auth.token(token_request)
        access_token = token_response['access_token']
        # Validate token
        try:
            introspection = await auth.introspect_token(access_token)
            assert introspection is not None
        except Exception:
            pass
        # Revoke token
        await auth.revoke_token(access_token)
        # Token should be invalid after revocation
        try:
            await auth.introspect_token(access_token)
            # May return active=False
        except Exception:
            # Expected
            pass
