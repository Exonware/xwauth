#!/usr/bin/env python3
"""
#exonware/xwauth/tests/2.integration/test_multi_provider_flow.py
Multi-Provider Integration Tests
Tests for multiple providers working together.
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
from exonware.xwlogin.providers.github import GitHubProvider
from exonware.xwlogin.providers.microsoft import MicrosoftProvider
from exonware.xwlogin.providers.apple import AppleProvider
from exonware.xwlogin.providers.samsung import SamsungProvider
@pytest.mark.xwauth_integration

class TestMultiProviderFlow:
    """Multi-provider integration tests."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key-for-multi-provider")
        return XWAuth(config=config)
    @pytest.fixture

    def registry(self):
        """Create provider registry."""
        return ProviderRegistry()
    @pytest.mark.asyncio

    async def test_register_all_core_providers(self, registry):
        """Test registering all core providers."""
        providers = [
            GoogleProvider(client_id="google_client", client_secret="google_secret"),
            GitHubProvider(client_id="github_client", client_secret="github_secret"),
            MicrosoftProvider(client_id="microsoft_client", client_secret="microsoft_secret"),
            AppleProvider(
                client_id="apple_client",
                client_secret="apple_secret",
                team_id="test_team_id",
                key_id="test_key_id",
                private_key="test_private_key"
            ),
            SamsungProvider(client_id="samsung_client", client_secret="samsung_secret")
        ]
        for provider in providers:
            registry.register(provider)
        # Verify all registered
        assert registry.has("google") is True
        assert registry.has("github") is True
        assert registry.has("microsoft") is True
        assert registry.has("apple") is True
        assert registry.has("samsung") is True
        # List all providers
        provider_list = registry.list_providers()
        assert len(provider_list) >= 5
    @pytest.mark.asyncio

    async def test_provider_authorization_urls(self, registry):
        """Test authorization URLs for all providers."""
        providers_config = {
            "google": GoogleProvider(client_id="google_client", client_secret="google_secret"),
            "github": GitHubProvider(client_id="github_client", client_secret="github_secret"),
            "microsoft": MicrosoftProvider(client_id="microsoft_client", client_secret="microsoft_secret"),
            "apple": AppleProvider(
                client_id="apple_client",
                client_secret="apple_secret",
                team_id="test_team_id",
                key_id="test_key_id",
                private_key="test_private_key"
            ),
            "samsung": SamsungProvider(client_id="samsung_client", client_secret="samsung_secret")
        }
        for name, provider in providers_config.items():
            registry.register(provider)
            url = await provider.get_authorization_url(
                client_id=f"{name}_client",
                redirect_uri="https://example.com/callback",
                state=f"{name}_state",
                scopes=["openid", "profile"]
            )
            assert url is not None
            assert name in url.lower() or f"{name}_client" in url
    @pytest.mark.asyncio

    async def test_provider_switching(self, registry):
        """Test switching between providers."""
        google = GoogleProvider(client_id="google_client", client_secret="google_secret")
        github = GitHubProvider(client_id="github_client", client_secret="github_secret")
        registry.register(google)
        registry.register(github)
        # Switch between providers
        provider1 = registry.get("google")
        provider2 = registry.get("github")
        assert provider1.provider_name == "google"
        assert provider2.provider_name == "github"
        # Both should work independently
        url1 = await provider1.get_authorization_url(
            client_id="google_client",
            redirect_uri="https://example.com/callback",
            state="state1"
        )
        url2 = await provider2.get_authorization_url(
            client_id="github_client",
            redirect_uri="https://example.com/callback",
            state="state2"
        )
        assert url1 != url2
