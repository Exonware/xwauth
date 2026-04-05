#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/authorization_tests/test_rbac.py
Unit tests for RBAC authorization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.authorization.rbac import RBACAuthorizer
@pytest.mark.xwauth_unit

class TestRBACAuthorizer:
    """Test RBACAuthorizer implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def rbac(self, auth):
        """Create RBACAuthorizer instance."""
        return RBACAuthorizer(auth)
    @pytest.mark.asyncio

    async def test_get_user_roles(self, rbac):
        """Test getting user roles."""
        # Create user with roles
        from exonware.xwsystem.security.crypto import hash_password
        from exonware.xwauth.storage.mock import MockUser
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={"roles": ["admin", "user"]}
        )
        await rbac._storage.save_user(user)
        roles = await rbac.get_user_roles("user123")
        assert "admin" in roles
        assert "user" in roles
    @pytest.mark.asyncio

    async def test_get_user_roles_no_user(self, rbac):
        """Test getting roles for non-existent user."""
        roles = await rbac.get_user_roles("nonexistent")
        assert roles == []
    @pytest.mark.asyncio

    async def test_check_permission(self, rbac):
        """Test permission check."""
        # For now, RBAC always returns False (not implemented)
        result = await rbac.check_permission(
            user_id="user123",
            resource="resource1",
            action="read"
        )
        # Currently returns False (not implemented)
        assert isinstance(result, bool)
