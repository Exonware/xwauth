#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/storage_tests/test_mock_storage.py
Unit tests for mock storage provider.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from datetime import datetime, timedelta
from exonware.xwauth.identity.storage.mock import (
    MockStorageProvider,
    MockUser,
    MockSession,
    MockToken,
    MockAuditLog
)
@pytest.mark.xwauth_unit

class TestMockStorageProvider:
    """Test MockStorageProvider implementation."""
    @pytest.fixture

    def storage(self):
        """Create MockStorageProvider instance."""
        return MockStorageProvider()
    @pytest.mark.asyncio

    async def test_save_and_get_user(self, storage):
        """Test saving and retrieving user."""
        user = MockUser(
            id="user123",
            email="test@example.com",
            password_hash="hashed_password"
        )
        await storage.save_user(user)
        retrieved = await storage.get_user("user123")
        assert retrieved is not None
        assert retrieved.id == "user123"
        assert retrieved.email == "test@example.com"
    @pytest.mark.asyncio

    async def test_get_user_by_email(self, storage):
        """Test getting user by email."""
        user = MockUser(
            id="user123",
            email="test@example.com"
        )
        await storage.save_user(user)
        retrieved = await storage.get_user_by_email("test@example.com")
        assert retrieved is not None
        assert retrieved.id == "user123"
    @pytest.mark.asyncio

    async def test_update_user(self, storage):
        """Test updating user."""
        user = MockUser(
            id="user123",
            email="test@example.com"
        )
        await storage.save_user(user)
        await storage.update_user("user123", {"email": "updated@example.com"})
        updated = await storage.get_user("user123")
        assert updated.email == "updated@example.com"
    @pytest.mark.asyncio

    async def test_delete_user(self, storage):
        """Test deleting user."""
        user = MockUser(id="user123", email="test@example.com")
        await storage.save_user(user)
        await storage.delete_user("user123")
        deleted = await storage.get_user("user123")
        assert deleted is None
    @pytest.mark.asyncio

    async def test_save_and_get_session(self, storage):
        """Test saving and retrieving session."""
        session = MockSession(
            id="session123",
            user_id="user123",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await storage.save_session(session)
        retrieved = await storage.get_session("session123")
        assert retrieved is not None
        assert retrieved.id == "session123"
        assert retrieved.user_id == "user123"
    @pytest.mark.asyncio

    async def test_save_and_get_token(self, storage):
        """Test saving and retrieving token."""
        token = MockToken(
            id="token123",
            user_id="user123",
            client_id="client123",
            token_type="Bearer",
            access_token="access_token_123",
            expires_at=datetime.now() + timedelta(hours=1),
            scopes=["read", "write"]
        )
        await storage.save_token(token)
        retrieved = await storage.get_token("token123")
        assert retrieved is not None
        assert retrieved.id == "token123"
        assert retrieved.user_id == "user123"
    @pytest.mark.asyncio

    async def test_get_token_by_access_token(self, storage):
        """Test getting token by access token."""
        token = MockToken(
            id="token123",
            user_id="user123",
            client_id="client123",
            token_type="Bearer",
            access_token="access_token_123",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await storage.save_token(token)
        retrieved = await storage.get_token_by_access_token("access_token_123")
        assert retrieved is not None
        assert retrieved.id == "token123"
    @pytest.mark.asyncio

    async def test_save_audit_log(self, storage):
        """Test saving audit log."""
        log = MockAuditLog(
            id="log123",
            user_id="user123",
            action="login",
            timestamp=datetime.now()
        )
        await storage.save_audit_log(log)
        logs = await storage.get_audit_logs({"user_id": "user123"})
        assert len(logs) > 0
        assert logs[0].action == "login"

    @pytest.mark.asyncio
    async def test_save_audit_log_rejects_duplicate_id(self, storage):
        """Audit log IDs are append-only and must be unique."""
        log = MockAuditLog(
            id="dup-log",
            user_id="user123",
            action="login",
            timestamp=datetime.now(),
            attributes={"k": "v"},
            context={"ip": "1.2.3.4"},
        )
        await storage.save_audit_log(log)
        with pytest.raises(ValueError):
            await storage.save_audit_log(log)

    @pytest.mark.asyncio
    async def test_save_audit_log_defensive_copy(self, storage):
        """Stored audit logs must not mutate when caller object mutates."""
        log = MockAuditLog(
            id="copy-log",
            user_id="user123",
            action="login",
            timestamp=datetime.now(),
            attributes={"k": "v"},
            context={"ip": "1.2.3.4"},
        )
        await storage.save_audit_log(log)
        log.attributes["k"] = "changed"
        logs = await storage.get_audit_logs({"id": "copy-log"})
        assert logs[0].attributes["k"] == "v"

    @pytest.mark.asyncio
    async def test_get_audit_logs_filter_by_action_and_missing_key(self, storage):
        """Filtering should match known fields and reject unknown filter keys."""
        log = MockAuditLog(
            id="filter-log",
            user_id="user123",
            action="authz.decision",
            timestamp=datetime.now(),
            attributes={"resource": "bucket:a"},
        )
        await storage.save_audit_log(log)
        by_action = await storage.get_audit_logs({"action": "authz.decision"})
        assert len(by_action) == 1
        missing = await storage.get_audit_logs({"does_not_exist": "x"})
        assert missing == []
