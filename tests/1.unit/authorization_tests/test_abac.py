#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/authorization_tests/test_abac.py
Unit tests for ABAC authorization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.authorization.abac import ABACAuthorizer
from exonware.xwauth.identity.storage.mock import MockUser
@pytest.mark.xwauth_unit

class TestABACAuthorizer:
    """Test ABACAuthorizer implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        return XWAuth(config=config)
    @pytest.fixture

    def abac(self, auth):
        """Create ABACAuthorizer instance."""
        return ABACAuthorizer(auth)
    @pytest.mark.asyncio

    async def test_check_permission_with_attributes(self, abac):
        """Test permission check with attributes."""
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={
                "department": "engineering",
                "level": "senior"
            }
        )
        await abac._storage.save_user(user)
        result = await abac.check_permission(
            user_id="user123",
            resource="project",
            action="read"
        )
        assert isinstance(result, bool)
    @pytest.mark.asyncio

    async def test_check_permission_with_policy(self, abac):
        """Test permission check with policy."""
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={"role": "admin"}
        )
        await abac._storage.save_user(user)
        result = await abac.check_permission(
            user_id="user123",
            resource="admin_panel",
            action="access"
        )
        assert isinstance(result, bool)
    @pytest.mark.asyncio

    async def test_check_permission_no_user(self, abac):
        """Test permission check for non-existent user."""
        result = await abac.check_permission(
            user_id="nonexistent",
            resource="resource1",
            action="read"
        )
        assert result is False
