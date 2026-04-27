#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/tokens_tests/test_introspection.py
Unit tests for token introspection (RFC 7662).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.tokens.introspection import TokenIntrospection
from exonware.xwauth.identity.tokens.jwt import JWTTokenManager
from exonware.xwauth.identity.tokens.opaque import OpaqueTokenManager
from exonware.xwauth.identity.storage.mock import MockStorageProvider
@pytest.mark.xwauth_unit

class TestTokenIntrospection:
    """Test TokenIntrospection implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def introspection(self, auth):
        """Create TokenIntrospection instance."""
        try:
            jwt_manager = JWTTokenManager(
                secret="test-secret-key",
                algorithm="HS256"
            )
        except Exception:
            jwt_manager = None
        storage = MockStorageProvider()
        opaque_manager = OpaqueTokenManager(storage)
        return TokenIntrospection(
            jwt_manager=jwt_manager,
            opaque_manager=opaque_manager
        )
    @pytest.mark.asyncio

    async def test_introspect_jwt_token(self, introspection):
        """Test introspection of JWT token."""
        jwt_manager = JWTTokenManager(
            secret="test-secret-key",
            algorithm="HS256"
        )
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        result = await introspection.introspect(token)
        assert result is not None
        assert 'active' in result or 'sub' in result
        assert result.get("token_id") == result.get("jti")
    @pytest.mark.asyncio

    async def test_introspect_jwt_includes_org_and_project_claims(self, introspection):
        """B2B tokens surface org_id / project_id through RFC 7662-style introspection."""
        jwt_manager = JWTTokenManager(secret="test-secret-key", algorithm="HS256")
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600,
            additional_claims={"org_id": "org-9", "project_id": "proj-2"},
        )
        result = await introspection.introspect(token)
        assert result.get("org_id") == "org-9"
        assert result.get("project_id") == "proj-2"
    @pytest.mark.asyncio

    async def test_introspect_opaque_token(self, introspection):
        """Test introspection of opaque token."""
        storage = MockStorageProvider()
        opaque_manager = OpaqueTokenManager(storage)
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600,
            additional_data={"session_id": "sess_1", "tenant_id": "tenant_1", "roles": ["member"]},
        )
        introspection_obj = TokenIntrospection(
            jwt_manager=None,
            opaque_manager=opaque_manager
        )
        result = await introspection_obj.introspect(token)
        assert result is not None
        assert result.get("session_id") == "sess_1"
        assert result.get("tenant_id") == "tenant_1"
        assert result.get("roles") == ["member"]
    @pytest.mark.asyncio

    async def test_introspect_invalid_token(self, introspection):
        """Test introspection of invalid token."""
        result = await introspection.introspect("invalid_token")
        assert result is not None
        assert result.get('active', False) is False
    @pytest.mark.asyncio

    async def test_introspect_expired_token(self, introspection):
        """Test introspection of expired token."""
        jwt_manager = JWTTokenManager(
            secret="test-secret-key",
            algorithm="HS256"
        )
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=-1  # Expired
        )
        import time
        time.sleep(0.1)
        result = await introspection.introspect(token)
        assert result is not None
        assert result.get('active', True) is False
