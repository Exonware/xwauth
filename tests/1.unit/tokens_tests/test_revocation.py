#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/tokens_tests/test_revocation.py
Unit tests for token revocation (RFC 7009).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.tokens.revocation import TokenRevocation
from exonware.xwauth.tokens.opaque import OpaqueTokenManager
from exonware.xwauth.tokens.refresh import RefreshTokenManager
from exonware.xwauth.tokens.jwt import JWTTokenManager
from exonware.xwauth.storage.mock import MockStorageProvider
@pytest.mark.xwauth_unit

class TestTokenRevocation:
    """Test TokenRevocation implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def revocation(self, auth):
        """Create TokenRevocation instance."""
        storage = MockStorageProvider()
        opaque_manager = OpaqueTokenManager(storage)
        refresh_manager = RefreshTokenManager(storage)
        return TokenRevocation(
            opaque_manager=opaque_manager,
            refresh_manager=refresh_manager
        )
    @pytest.mark.asyncio

    async def test_revoke_access_token(self, revocation):
        """Test access token revocation."""
        storage = MockStorageProvider()
        opaque_manager = OpaqueTokenManager(storage)
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        revocation_obj = TokenRevocation(
            opaque_manager=opaque_manager,
            refresh_manager=None
        )
        await revocation_obj.revoke(token)
        # Token should be revoked
        token_data = await opaque_manager.get_token(token)
        assert token_data is None
    @pytest.mark.asyncio

    async def test_revoke_refresh_token(self, revocation):
        """Test refresh token revocation."""
        storage = MockStorageProvider()
        refresh_manager = RefreshTokenManager(storage)
        token = refresh_manager.generate_refresh_token()
        await refresh_manager.save_refresh_token(
            refresh_token=token,
            access_token_id="access123",
            user_id="user123",
            client_id="client123",
            expires_in=86400 * 7
        )
        revocation_obj = TokenRevocation(
            opaque_manager=None,
            refresh_manager=refresh_manager
        )
        await revocation_obj.revoke(token, token_type_hint="refresh_token")
        # Token should be revoked
        token_data = await refresh_manager.get_refresh_token(token)
        assert token_data is None
    @pytest.mark.asyncio

    async def test_revoke_nonexistent_token(self, revocation):
        """Test revocation of nonexistent token."""
        # Should not raise, just return
        await revocation.revoke("nonexistent_token")
    @pytest.mark.asyncio

    async def test_revoke_token_twice(self, revocation):
        """Test revoking token twice (idempotent)."""
        storage = MockStorageProvider()
        opaque_manager = OpaqueTokenManager(storage)
        token = opaque_manager.generate_token()
        await opaque_manager.save_token(
            token=token,
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        revocation_obj = TokenRevocation(
            opaque_manager=opaque_manager,
            refresh_manager=None
        )
        # Revoke twice
        await revocation_obj.revoke(token)
        await revocation_obj.revoke(token)  # Should be idempotent
        # Token should still be revoked
        token_data = await opaque_manager.get_token(token)
        assert token_data is None

    @pytest.mark.asyncio
    async def test_revoke_jwt_token_by_jti(self):
        """Test JWT revocation through jti denylist."""
        jwt_manager = JWTTokenManager(secret="test-secret-key", algorithm="HS256")
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600,
        )
        revocation_obj = TokenRevocation(
            opaque_manager=None,
            refresh_manager=None,
            jwt_manager=jwt_manager,
        )
        await revocation_obj.revoke(token, token_type_hint="access_token")
        payload = jwt_manager.get_token_info(token)
        assert jwt_manager.is_jti_revoked(str(payload.get("jti"))) is True
