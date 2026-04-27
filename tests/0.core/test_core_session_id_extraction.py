#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/0.core/test_core_session_id_extraction.py
Core test for session_id extraction from tokens.
Fast, high-value test covering critical session management functionality.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockStorageProvider
@pytest.mark.xwauth_core

class TestSessionIdExtraction:
    """Core test for session_id extraction from tokens."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.mark.asyncio

    async def test_extract_session_id_from_jwt_token(self, auth):
        """Test extracting session_id from JWT token (critical path)."""
        session_id = "session_core_test_123"
        # Generate JWT token with session_id
        token = await auth._token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id
        token_manager = auth._token_manager
        if hasattr(token_manager, '_jwt_manager') and token_manager._jwt_manager:
            payload = token_manager._jwt_manager.validate_token(token)
            extracted_session_id = payload.get('session_id')
            assert extracted_session_id == session_id
    @pytest.mark.asyncio

    async def test_extract_session_id_from_opaque_token(self, auth):
        """Test extracting session_id from opaque token (critical path)."""
        # Use opaque tokens
        auth._token_manager._use_jwt = False
        session_id = "session_opaque_core_456"
        # Generate opaque token with session_id
        token = await auth._token_manager.generate_access_token(
            user_id="user456",
            client_id="client456",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id
        token_data = await auth._token_manager._opaque_manager.get_token(token)
        extracted_session_id = token_data.get('attributes', {}).get('session_id')
        assert extracted_session_id == session_id
