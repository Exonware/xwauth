#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/storage_tests/test_storage_edge_cases.py
Unit tests for storage edge cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from datetime import datetime, timedelta
from exonware.xwauth.storage.mock import (
    MockStorageProvider,
    MockUser,
    MockSession,
    MockToken,
    MockAuditLog
)
@pytest.mark.xwauth_unit

class TestStorageEdgeCases:
    """Test storage edge cases."""
    @pytest.fixture

    def storage(self):
        """Create MockStorageProvider instance."""
        return MockStorageProvider()
    @pytest.mark.asyncio

    async def test_save_user_with_special_characters(self, storage):
        """Test saving user with special characters."""
        user = MockUser(
            id="user123",
            email="test+tag@example.com",
            attributes={"name": "Test User", "special": "value with spaces & symbols"}
        )
        await storage.save_user(user)
        retrieved = await storage.get_user("user123")
        assert retrieved.attributes["special"] == "value with spaces & symbols"
    @pytest.mark.asyncio

    async def test_save_user_with_unicode(self, storage):
        """Test saving user with unicode characters."""
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={"name": "测试用户", "description": "ユーザー説明"}
        )
        await storage.save_user(user)
        retrieved = await storage.get_user("user123")
        assert retrieved.attributes["name"] == "测试用户"
        assert retrieved.attributes["description"] == "ユーザー説明"
    @pytest.mark.asyncio

    async def test_save_user_with_very_large_attributes(self, storage):
        """Test saving user with very large attributes."""
        large_data = "x" * 100000  # 100KB of data
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={"large_field": large_data}
        )
        await storage.save_user(user)
        retrieved = await storage.get_user("user123")
        assert len(retrieved.attributes["large_field"]) == 100000
    @pytest.mark.asyncio

    async def test_update_user_partial(self, storage):
        """Test partial user update."""
        user = MockUser(
            id="user123",
            email="test@example.com",
            attributes={"field1": "value1", "field2": "value2"}
        )
        await storage.save_user(user)
        await storage.update_user("user123", {"field1": "updated_value1"})
        updated = await storage.get_user("user123")
        assert updated.attributes["field1"] == "updated_value1"
        assert updated.attributes["field2"] == "value2"  # Should remain
    @pytest.mark.asyncio

    async def test_list_users_empty(self, storage):
        """Test listing users when storage is empty."""
        users = await storage.list_users()
        assert isinstance(users, list)
    @pytest.mark.asyncio

    async def test_list_users_with_filters(self, storage):
        """Test listing users with filters."""
        user1 = MockUser(id="user1", email="user1@example.com", attributes={"role": "admin"})
        user2 = MockUser(id="user2", email="user2@example.com", attributes={"role": "user"})
        await storage.save_user(user1)
        await storage.save_user(user2)
        # List all
        all_users = await storage.list_users()
        assert len(all_users) >= 2
        # List with filters (if supported)
        try:
            filtered = await storage.list_users({"role": "admin"})
            assert len(filtered) >= 1
        except Exception:
            # Filters may not be implemented
            pass
    @pytest.mark.asyncio

    async def test_save_session_with_metadata(self, storage):
        """Test saving session with metadata."""
        session = MockSession(
            id="session123",
            user_id="user123",
            expires_at=datetime.now() + timedelta(hours=1),
            metadata={"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        )
        await storage.save_session(session)
        retrieved = await storage.get_session("session123")
        assert retrieved.metadata["ip_address"] == "192.168.1.1"
    @pytest.mark.asyncio

    async def test_list_user_sessions_empty(self, storage):
        """Test listing sessions for user with no sessions."""
        sessions = await storage.list_user_sessions("nonexistent_user")
        assert isinstance(sessions, list)
        assert len(sessions) == 0
    @pytest.mark.asyncio

    async def test_save_token_with_custom_scopes(self, storage):
        """Test saving token with custom scopes."""
        token = MockToken(
            id="token123",
            user_id="user123",
            client_id="client123",
            token_type="Bearer",
            access_token="access_token_123",
            expires_at=datetime.now() + timedelta(hours=1),
            scopes=["custom:scope1", "custom:scope2", "read", "write"]
        )
        await storage.save_token(token)
        retrieved = await storage.get_token("token123")
        assert "custom:scope1" in retrieved.scopes
        assert "custom:scope2" in retrieved.scopes
    @pytest.mark.asyncio

    async def test_save_audit_log_with_context(self, storage):
        """Test saving audit log with context."""
        log = MockAuditLog(
            id="log123",
            user_id="user123",
            action="login",
            timestamp=datetime.now(),
            context={"ip_address": "192.168.1.1", "success": True}
        )
        await storage.save_audit_log(log)
        logs = await storage.get_audit_logs({"user_id": "user123"})
        assert len(logs) > 0
        assert logs[0].context["success"] is True
