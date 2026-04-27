#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/core_tests/test_device_code_storage.py
Unit tests for Device Code Grant storage functionality.
Tests the format-agnostic storage implementation for device codes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig, DEFAULT_TEST_CLIENTS
from exonware.xwauth.identity.core.grants.device_code import DeviceCodeGrant
from exonware.xwauth.identity.errors import XWInvalidRequestError
@pytest.mark.xwauth_unit

class TestDeviceCodeStorage:
    """Test Device Code storage implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
            allow_mock_storage_fallback=True,
        )
        return XWAuth(config=config)
    @pytest.fixture

    def grant(self, auth):
        """Create DeviceCodeGrant instance."""
        return DeviceCodeGrant(auth)
    @pytest.mark.asyncio

    async def test_device_code_is_stored(self, grant):
        """Test that device code is stored in storage when generated."""
        request = {
            'client_id': 'test',
            'scopes': ['read', 'write'],
        }
        # Process device code grant (generates and stores device code)
        response = await grant.process(request)
        # Verify response contains device code
        assert 'device_code' in response
        assert 'user_code' in response
        assert 'verification_uri' in response
        assert 'expires_in' in response
        device_code = response['device_code']
        user_code = response['user_code']
        # Verify device code is stored and can be retrieved
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.device_code == device_code
        assert stored_code.user_code == user_code
        assert stored_code.client_id == 'test'
        assert stored_code.status == 'pending'
    @pytest.mark.asyncio

    async def test_device_code_retrieval_by_user_code(self, grant):
        """Test that device code can be retrieved by user_code."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        response = await grant.process(request)
        user_code = response['user_code']
        device_code = response['device_code']
        # Retrieve by user_code
        stored_code = await grant._auth.storage.get_device_code_by_user_code(user_code)
        assert stored_code is not None
        assert stored_code.device_code == device_code
        assert stored_code.user_code == user_code
    @pytest.mark.asyncio

    async def test_device_code_expiration(self, grant):
        """Test that device codes have expiration timestamps."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        response = await grant.process(request)
        device_code = response['device_code']
        # Verify expiration is set
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.expires_at is not None
        assert stored_code.created_at is not None
    @pytest.mark.asyncio

    async def test_device_code_status_update(self, grant):
        """Test that device code status can be updated."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        response = await grant.process(request)
        device_code = response['device_code']
        # Update status to approved
        await grant._auth.storage.update_device_code_status(
            device_code=device_code,
            status='approved',
            user_id='user123'
        )
        # Verify status was updated
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.status == 'approved'
        assert stored_code.user_id == 'user123'
    @pytest.mark.asyncio

    async def test_device_code_deletion(self, grant):
        """Test that device codes can be deleted."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        response = await grant.process(request)
        device_code = response['device_code']
        # Verify it exists
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        # Delete it
        await grant._auth.storage.delete_device_code(device_code)
        # Verify it's deleted
        deleted_code = await grant._auth.storage.get_device_code(device_code)
        assert deleted_code is None
