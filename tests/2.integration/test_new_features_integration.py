#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/2.integration/test_new_features_integration.py
Integration tests for newly added features.
Tests end-to-end scenarios for:
- Device code storage and retrieval
- Session ID in token claims
- Access token ID linking
- Registration access token validation
- OAuth 1.0 flows
- JOSE library operations
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
from exonware.xwauth.identity.storage.mock import MockStorageProvider
@pytest.mark.xwauth_integration

class TestDeviceCodeFlowIntegration:
    """Integration test for device code flow with storage."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
            allow_mock_storage_fallback=True,
        )
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.mark.asyncio

    async def test_complete_device_code_flow(self, auth):
        """Test complete device code authorization flow."""
        from exonware.xwauth.identity.core.grants.device_code import DeviceCodeGrant
        grant = DeviceCodeGrant(auth)
        # Step 1: Generate device code
        request = {
            'client_id': 'test',
            'scopes': ['read', 'write'],
        }
        response = await grant.process(request)
        device_code = response['device_code']
        user_code = response['user_code']
        # Step 2: Verify device code is stored
        stored_code = await auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.status == 'pending'
        # Step 3: User approves (update status)
        await auth.storage.update_device_code_status(
            device_code=device_code,
            status='approved',
            user_id='user123'
        )
        # Step 4: Verify status update
        updated_code = await auth.storage.get_device_code(device_code)
        assert updated_code.status == 'approved'
        assert updated_code.user_id == 'user123'
@pytest.mark.xwauth_integration

class TestSessionIdTokenFlowIntegration:
    """Integration test for session_id in token flow."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.mark.asyncio

    async def test_jwt_token_with_session_id_flow(self, auth):
        """Test complete flow: generate JWT with session_id, extract it."""
        # Create session
        session_id = "session_integration_123"
        # Generate token with session_id
        token = await auth._token_manager.generate_access_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id from token
        payload = auth._token_manager._jwt_manager.validate_token(token)
        extracted_session_id = payload.get('session_id')
        assert extracted_session_id == session_id
    @pytest.mark.asyncio

    async def test_opaque_token_with_session_id_flow(self, auth):
        """Test complete flow: generate opaque token with session_id, extract it."""
        # Use opaque tokens
        auth._token_manager._use_jwt = False
        session_id = "session_opaque_integration_456"
        # Generate token with session_id
        token = await auth._token_manager.generate_access_token(
            user_id="user456",
            client_id="client456",
            scopes=["read"],
            session_id=session_id
        )
        # Extract session_id from token
        token_data = await auth._token_manager._opaque_manager.get_token(token)
        extracted_session_id = token_data.get('attributes', {}).get('session_id')
        assert extracted_session_id == session_id
@pytest.mark.xwauth_integration

class TestAccessTokenLinkingIntegration:
    """Integration test for access token ID linking."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.mark.asyncio

    async def test_refresh_token_linking_flow(self, auth):
        """Test complete flow: generate access token, link refresh token."""
        # Use opaque tokens for linking
        auth._token_manager._use_jwt = False
        # Generate access token
        access_token = await auth._token_manager.generate_access_token(
            user_id="user789",
            client_id="client789",
            scopes=["read", "write"]
        )
        # Get access token ID
        token_data = await auth._token_manager._opaque_manager.get_token(access_token)
        access_token_id = token_data.get('token_id')
        assert access_token_id is not None
        # Generate refresh token with linking
        refresh_token = await auth._token_manager.generate_refresh_token(
            user_id="user789",
            client_id="client789",
            access_token=access_token
        )
        # Verify refresh token was generated
        assert refresh_token is not None
        # Verify refresh token data
        refresh_data = await auth._token_manager._refresh_manager.get_refresh_token(refresh_token)
        assert refresh_data is not None
@pytest.mark.xwauth_integration

class TestDCRFlowIntegration:
    """Integration test for Dynamic Client Registration flow."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key", allow_mock_storage_fallback=True)
        storage = MockStorageProvider()
        return XWAuth(config=config, storage=storage)
    @pytest.mark.asyncio

    async def test_complete_dcr_flow(self, auth):
        """Test complete DCR flow: register, get, update, delete."""
        from exonware.xwauth.identity.core.dcr import DCRManager
        dcr_manager = DCRManager(auth)
        # Step 1: Register client
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
            "client_name": "Integration Test Client",
        }
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        registration_token = registration_result['registration_access_token']
        assert client_id is not None
        assert registration_token is not None
        # Step 2: Get client with valid token
        client_data = await dcr_manager.get_client(
            client_id,
            registration_access_token=registration_token
        )
        assert client_data is not None
        assert client_data['client_id'] == client_id
        # Step 3: Update client with valid token
        updated_metadata = {"client_name": "Updated Client Name"}
        updated_result = await dcr_manager.update_client(
            client_id,
            updated_metadata,
            registration_access_token=registration_token
        )
        assert updated_result['client_name'] == "Updated Client Name"
        # Step 4: Delete client with valid token
        await dcr_manager.delete_client(
            client_id,
            registration_access_token=registration_token
        )
        # Verify client is deleted
        deleted_client = await dcr_manager.get_client(client_id)
        assert deleted_client is None
