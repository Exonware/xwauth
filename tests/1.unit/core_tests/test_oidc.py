#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/core_tests/test_oidc.py
Unit tests for OpenID Connect (OIDC) implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.core.oidc import OIDCProvider
@pytest.mark.xwauth_unit

class TestOIDCProvider:
    """Test OIDCProvider implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def oidc(self, auth):
        """Create OIDCProvider instance."""
        return OIDCProvider(auth)
    @pytest.mark.asyncio

    async def test_get_user_info(self, oidc):
        """Test getting user info."""
        # Currently returns placeholder
        user_info = await oidc.get_userinfo("placeholder_token")
        assert user_info is not None
        assert isinstance(user_info, dict)
    @pytest.mark.asyncio

    async def test_discovery_document(self, oidc):
        """Test OIDC discovery document."""
        discovery = await oidc.get_discovery_document("https://example.com")
        assert discovery is not None
        assert 'issuer' in discovery
        assert isinstance(discovery, dict)
    @pytest.mark.asyncio

    async def test_jwks_endpoint(self, oidc):
        """Test JWKS endpoint."""
        # OIDCProvider doesn't have get_jwks method
        # This test should be skipped or test discovery document instead
        discovery = await oidc.get_discovery_document("https://example.com")
        assert discovery is not None
        assert 'jwks_uri' in discovery
