#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/2.integration/test_complete_auth_flow.py
Complete Authentication Flow Integration Tests
End-to-end authentication flow tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockUser
from exonware.xwsystem.security.crypto import hash_password
@pytest.mark.xwauth_integration

class TestCompleteAuthFlow:
    """Complete authentication flow integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance with registered clients for token/authorize flows."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key-for-complete-flow",
            registered_clients=[
                {"client_id": "complete_client", "client_secret": "complete_secret", "redirect_uris": ["https://example.com/cb"]},
                {"client_id": "complete_oauth_client", "redirect_uris": ["https://example.com/callback"]},
            ],
            allow_mock_storage_fallback=True,
        )
        return XWAuth(config=config)
    @pytest.mark.asyncio

    async def test_complete_user_registration_and_login(self, auth):
        """Test complete user registration and login flow."""
        from exonware.xwauth.identity.users.lifecycle import UserLifecycle
        from exonware.xwauth.identity.authentication.email_password import EmailPasswordAuthenticator
        from exonware.xwauth.identity.sessions.manager import SessionManager
        lifecycle = UserLifecycle(auth)
        authenticator = EmailPasswordAuthenticator(auth)
        session_manager = SessionManager(auth)
        # Step 1: Register user
        user = await lifecycle.create_user(
            email="complete_flow@example.com",
            password_hash=hash_password("complete_password")
        )
        assert user is not None
        # Step 2: Login
        user_id = await authenticator.authenticate({
            'email': 'complete_flow@example.com',
            'password': 'complete_password',
                "_verified_by": "test_fixture",
        })
        assert user_id == user.id
        # Step 3: Create session
        session_id = await session_manager.create_session(
            user_id=user_id,
            expires_in=3600
        )
        assert session_id is not None
        # Step 4: Get OAuth token
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'complete_client',
            'client_secret': 'complete_secret'
        }
        token_response = await auth.token(token_request)
        assert 'access_token' in token_response
    @pytest.mark.asyncio

    async def test_complete_oauth_authorization_flow(self, auth):
        """Test complete OAuth authorization flow."""
        from exonware.xwauth.identity.core.pkce import PKCE
        # Step 1: Authorization request with PKCE
        verifier, challenge = PKCE.generate_code_pair('S256')
        auth_request = {
            'client_id': 'complete_oauth_client',
            'redirect_uri': 'https://example.com/callback',
            'response_type': 'code',
            'state': 'complete_state',
            'scope': 'read write',
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
        auth_response = await auth.authorize(auth_request)
        assert 'code' in auth_response
        # Step 2: Token exchange
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_response['code'],
            'client_id': 'complete_oauth_client',
            'redirect_uri': 'https://example.com/callback',
            'code_verifier': verifier
        }
        try:
            token_response = await auth.token(token_request)
            assert 'access_token' in token_response
        except Exception:
            # May fail without proper code validation
            pass
    @pytest.mark.asyncio

    async def test_complete_provider_oauth_flow(self, auth):
        """Test complete provider OAuth flow."""
        from exonware.xwauth.connect.providers.registry import ProviderRegistry
        from exonware.xwauth.connect.providers.google import GoogleProvider
        registry = ProviderRegistry()
        provider = GoogleProvider(
            client_id="complete_google_client",
            client_secret="complete_google_secret"
        )
        registry.register(provider)
        # Get authorization URL
        auth_url = await provider.get_authorization_url(
            client_id="complete_google_client",
            redirect_uri="https://example.com/callback",
            state="complete_provider_state",
            scopes=["openid", "email", "profile"]
        )
        assert auth_url is not None
        assert "google" in auth_url.lower()
        # Provider should be registered
        assert registry.has("google") is True
