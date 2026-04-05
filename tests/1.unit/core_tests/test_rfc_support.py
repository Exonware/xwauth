#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/core_tests/test_rfc_support.py
Unit tests for advanced RFC support (RFC 9101, 9207, 9068, 7521/7523).
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
from exonware.xwauth.storage.mock import MockStorageProvider
from exonware.xwauth.core.rfc.rfc9101 import RFC9101BrowserBasedApps
from exonware.xwauth.core.rfc.rfc9207 import RFC9207IssuerIdentification
from exonware.xwauth.core.rfc.rfc9068 import RFC9068JWTProfile
from exonware.xwauth.core.rfc.rfc7521 import RFC7521JWTBearerToken
from exonware.xwauth.errors import XWInvalidRequestError
@pytest.mark.xwauth_unit

class TestRFC9101:
    """Test RFC 9101: OAuth 2.0 for Browser-Based Apps."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret",
            registered_clients=[{
                "client_id": "public_client",
                "redirect_uris": ["https://example.com/callback"],
            }]
        )
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.fixture

    def rfc9101(self, auth):
        """Create RFC9101BrowserBasedApps instance."""
        return RFC9101BrowserBasedApps(auth)
    @pytest.mark.asyncio

    async def test_validate_browser_based_client(self, rfc9101):
        """Test browser-based client validation."""
        from exonware.xwauth.core.pkce import PKCE
        code_verifier = PKCE.generate_code_verifier()
        code_challenge = PKCE.generate_code_challenge(code_verifier)
        # Should pass with PKCE
        rfc9101.validate_browser_based_client(
            client_id="public_client",
            redirect_uri="https://example.com/callback",
            code_challenge=code_challenge,
            code_challenge_method="S256"
        )
    @pytest.mark.asyncio

    async def test_validate_browser_based_client_no_pkce(self, rfc9101):
        """Test that PKCE is required for public clients."""
        with pytest.raises(XWInvalidRequestError):
            rfc9101.validate_browser_based_client(
                client_id="public_client",
                redirect_uri="https://example.com/callback",
                code_challenge=None,
                code_challenge_method=None
            )
@pytest.mark.xwauth_unit

class TestRFC9207:
    """Test RFC 9207: OAuth 2.0 Authorization Server Issuer Identification."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret"
        )
        # Set issuer attribute if RFC9207 expects it
        # RFC9207 uses getattr(self._config, "issuer", None), so we can set it as an attribute
        config.issuer = "https://auth.example.com"
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.fixture

    def rfc9207(self, auth):
        """Create RFC9207IssuerIdentification instance."""
        return RFC9207IssuerIdentification(auth)

    def test_get_issuer(self, rfc9207):
        """Test issuer retrieval."""
        issuer = rfc9207.get_issuer()
        # RFC9207 returns issuer from config.issuer if set, otherwise falls back to "xwauth"
        assert issuer is not None
        assert isinstance(issuer, str)
        assert len(issuer) > 0

    def test_validate_issuer(self, rfc9207):
        """Test issuer validation."""
        expected_issuer = rfc9207.get_issuer()
        assert rfc9207.validate_issuer(expected_issuer) is True
        assert rfc9207.validate_issuer("https://wrong.example.com") is False
@pytest.mark.xwauth_unit

class TestRFC9068:
    """Test RFC 9068: JWT Profile for OAuth 2.0 Access Tokens."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret"
        )
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.fixture

    def rfc9068(self, auth):
        """Create RFC9068JWTProfile instance."""
        return RFC9068JWTProfile(auth)
    @pytest.mark.asyncio

    async def test_generate_jwt_access_token(self, rfc9068):
        """Test JWT access token generation with RFC 9068 profile."""
        from datetime import datetime, timezone
        token = rfc9068.generate_jwt_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["openid", "profile"],
            auth_time=datetime.now(timezone.utc),
            acr="urn:mace:incommon:iap:silver",
            amr=["password", "mfa"]
        )
        assert token is not None
        assert len(token) > 0
@pytest.mark.xwauth_unit

class TestRFC7521:
    """Test RFC 7521/7523: JWT Bearer Token Profiles."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret"
        )
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.fixture

    def rfc7521(self, auth):
        """Create RFC7521JWTBearerToken instance."""
        return RFC7521JWTBearerToken(auth)
    @pytest.mark.asyncio

    async def test_generate_client_assertion(self, rfc7521):
        """Test client assertion generation."""
        assertion = rfc7521.generate_client_assertion(
            client_id="client123",
            audience="https://auth.example.com/oauth/token"
        )
        assert assertion is not None
        assert len(assertion) > 0
