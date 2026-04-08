#!/usr/bin/env python3
"""
#exonware/xwauth/tests/2.integration/test_provider_integration.py
Provider Integration Tests
Integration tests for OAuth provider flows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.providers.registry import ProviderRegistry
from exonware.xwlogin.providers.google import GoogleProvider
@pytest.mark.xwauth_integration

class TestProviderIntegration:
    """Provider integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key-for-provider-integration")
        return XWAuth(config=config)
    @pytest.fixture

    def registry(self):
        """Create provider registry."""
        return ProviderRegistry()
    @pytest.mark.asyncio

    async def test_provider_registration_and_flow(self, auth, registry):
        """Test provider registration and OAuth flow."""
        # Register provider
        provider = GoogleProvider(
            client_id="integration_google_client",
            client_secret="integration_google_secret"
        )
        registry.register(provider)
        assert registry.has("google") is True
        # Get provider
        retrieved = registry.get("google")
        assert retrieved is not None
        assert retrieved.provider_name == "google"
        # Test provider authorization URL generation
        auth_url = await provider.get_authorization_url(
            client_id="integration_google_client",
            redirect_uri="https://example.com/callback",
            state="integration_state",
            scopes=["openid", "email", "profile"]
        )
        assert auth_url is not None
        auth_url_str = str(auth_url)
        assert "google" in auth_url_str.lower() or "accounts.google.com" in auth_url_str.lower()
        assert "integration_google_client" in auth_url_str
        assert "integration_state" in auth_url_str
    @pytest.mark.asyncio

    async def test_multiple_providers_integration(self, registry):
        """Test multiple providers working together."""
        from exonware.xwlogin.providers.github import GitHubProvider
        from exonware.xwlogin.providers.microsoft import MicrosoftProvider
        # Register multiple providers
        google = GoogleProvider(
            client_id="google_client",
            client_secret="google_secret"
        )
        github = GitHubProvider(
            client_id="github_client",
            client_secret="github_secret"
        )
        microsoft = MicrosoftProvider(
            client_id="microsoft_client",
            client_secret="microsoft_secret"
        )
        registry.register(google)
        registry.register(github)
        registry.register(microsoft)
        # Verify all registered
        providers = registry.list_providers()
        assert "google" in providers
        assert "github" in providers
        assert "microsoft" in providers
        # Test each provider
        assert registry.get("google").provider_name == "google"
        assert registry.get("github").provider_name == "github"
        assert registry.get("microsoft").provider_name == "microsoft"
