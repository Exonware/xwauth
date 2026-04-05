#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/sessions_tests/test_session_storage.py
Unit tests for session storage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from datetime import datetime, timedelta
from exonware.xwauth.sessions.storage import SessionStorage
from exonware.xwauth.sessions.session import Session
from exonware.xwauth.storage.mock import MockStorageProvider
from exonware.xwauth.defs import SessionStatus
@pytest.mark.xwauth_unit

class TestSessionStorage:
    """Test SessionStorage implementation."""
    @pytest.fixture

    def storage(self):
        """Create MockStorageProvider."""
        return MockStorageProvider()
    @pytest.fixture

    def session_storage(self, storage):
        """Create SessionStorage instance."""
        return SessionStorage(storage)
    @pytest.mark.asyncio

    async def test_save_session(self, session_storage):
        """Test saving session."""
        session = Session(
            id="session123",
            user_id="user123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await session_storage.save_session(session)
        # Verify saved
        saved = await session_storage.get_session("session123")
        assert saved is not None
        assert saved.id == "session123"
    @pytest.mark.asyncio

    async def test_get_session(self, session_storage):
        """Test getting session."""
        session = Session(
            id="session123",
            user_id="user123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await session_storage.save_session(session)
        retrieved = await session_storage.get_session("session123")
        assert retrieved is not None
        assert retrieved.user_id == "user123"
    @pytest.mark.asyncio

    async def test_get_nonexistent_session(self, session_storage):
        """Test getting nonexistent session."""
        session = await session_storage.get_session("nonexistent")
        assert session is None
    @pytest.mark.asyncio

    async def test_delete_session(self, session_storage):
        """Test deleting session."""
        session = Session(
            id="session123",
            user_id="user123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await session_storage.save_session(session)
        await session_storage.delete_session("session123")
        deleted = await session_storage.get_session("session123")
        assert deleted is None
    @pytest.mark.asyncio

    async def test_list_user_sessions(self, session_storage):
        """Test listing user sessions."""
        session1 = Session(
            id="session1",
            user_id="user123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        session2 = Session(
            id="session2",
            user_id="user123",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)
        )
        await session_storage.save_session(session1)
        await session_storage.save_session(session2)
        sessions = await session_storage.list_user_sessions("user123")
        assert len(sessions) >= 2
