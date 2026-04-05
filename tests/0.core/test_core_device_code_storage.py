#!/usr/bin/env python3
"""
#exonware/xwauth/tests/0.core/test_core_device_code_storage.py
Core test for device code storage functionality.
Fast, high-value test covering critical device code grant storage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig, DEFAULT_TEST_CLIENTS
from exonware.xwauth.core.grants.device_code import DeviceCodeGrant
@pytest.mark.xwauth_core

class TestDeviceCodeStorageCore:
    """Core test for device code storage (critical path)."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
        )
        return XWAuth(config=config)
    @pytest.fixture

    def grant(self, auth):
        """Create DeviceCodeGrant instance."""
        return DeviceCodeGrant(auth)
    @pytest.mark.asyncio

    async def test_device_code_is_stored_when_generated(self, grant):
        """Test that device codes are stored when generated (critical functionality)."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        # Generate device code
        response = await grant.process(request)
        device_code = response['device_code']
        # Verify it's stored and can be retrieved
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.device_code == device_code
        assert stored_code.status == 'pending'
