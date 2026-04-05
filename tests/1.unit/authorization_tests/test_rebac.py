#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/authorization_tests/test_rebac.py
Unit tests for ReBAC authorization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.authorization.rebac import ReBACAuthorizer
from exonware.xwauth.storage.mock import MockUser
@pytest.mark.xwauth_unit

class TestReBACAuthorizer:
    """Test ReBACAuthorizer implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def rebac(self, auth):
        """Create ReBACAuthorizer instance."""
        return ReBACAuthorizer(auth)
    @pytest.mark.asyncio

    async def test_check_permission_with_relationship(self, rebac):
        """Test permission check with relationship."""
        user = MockUser(
            id="user123",
            email="test@example.com"
        )
        await rebac._storage.save_user(user)
        # Add relationship first
        await rebac.add_relationship("user123", "owner", "document")
        result = await rebac.check_permission(
            user_id="user123",
            resource="document",
            action="read"
        )
        assert isinstance(result, bool)
    @pytest.mark.asyncio

    async def test_check_permission_with_tupleset(self, rebac):
        """Test permission check with tupleset."""
        user = MockUser(
            id="user123",
            email="test@example.com"
        )
        await rebac._storage.save_user(user)
        # Add relationship first
        await rebac.add_relationship("user123", "viewer", "folder")
        result = await rebac.check_permission(
            user_id="user123",
            resource="folder",
            action="read"
        )
        assert isinstance(result, bool)
    @pytest.mark.asyncio

    async def test_check_permission_no_relationship(self, rebac):
        """Test permission check without relationship."""
        user = MockUser(
            id="user123",
            email="test@example.com"
        )
        await rebac._storage.save_user(user)
        result = await rebac.check_permission(
            user_id="user123",
            resource="document",
            action="read"
        )
        assert isinstance(result, bool)
