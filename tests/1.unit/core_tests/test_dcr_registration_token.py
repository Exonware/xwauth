#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/core_tests/test_dcr_registration_token.py
Unit tests for Dynamic Client Registration (DCR) registration_access_token validation.
Tests that DCR endpoints properly validate registration_access_token from Authorization header.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.core.dcr import DCRManager
from exonware.xwauth.errors import XWInvalidRequestError
@pytest.mark.xwauth_unit

class TestDCRRegistrationTokenValidation:
    """Test registration_access_token validation in DCR."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        return XWAuth(config=config)
    @pytest.fixture

    def dcr_manager(self, auth):
        """Create DCRManager instance."""
        return DCRManager(auth)
    @pytest.mark.asyncio

    async def test_register_client_returns_registration_token(self, dcr_manager):
        """Test that client registration returns registration_access_token."""
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
            "token_endpoint_auth_method": "client_secret_basic",
            "grant_types": ["authorization_code"],
        }
        result = await dcr_manager.register_client(client_metadata)
        # Verify registration_access_token is returned
        assert 'registration_access_token' in result
        assert result['registration_access_token'] is not None
        assert len(result['registration_access_token']) > 0
    @pytest.mark.asyncio

    async def test_validate_registration_token_succeeds(self, dcr_manager):
        """Test that valid registration_access_token passes validation."""
        # Register a client
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
        }
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        registration_token = registration_result['registration_access_token']
        # Validate the token
        await dcr_manager.validate_registration_access_token(client_id, registration_token)
        # Should not raise exception
    @pytest.mark.asyncio

    async def test_validate_registration_token_fails_with_invalid_token(self, dcr_manager):
        """Test that invalid registration_access_token fails validation."""
        # Register a client
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
        }
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        # Try to validate with wrong token
        with pytest.raises(XWInvalidRequestError):
            await dcr_manager.validate_registration_access_token(
                client_id,
                "invalid_token_12345"
            )
    @pytest.mark.asyncio

    async def test_validate_registration_token_fails_with_wrong_client(self, dcr_manager):
        """Test that registration_access_token fails for wrong client_id."""
        # Register two clients
        client1_metadata = {"redirect_uris": ["https://client1.example.com/callback"]}
        client2_metadata = {"redirect_uris": ["https://client2.example.com/callback"]}
        result1 = await dcr_manager.register_client(client1_metadata)
        result2 = await dcr_manager.register_client(client2_metadata)
        client1_id = result1['client_id']
        client2_token = result2['registration_access_token']
        # Try to use client2's token for client1
        with pytest.raises(XWInvalidRequestError):
            await dcr_manager.validate_registration_access_token(
                client1_id,
                client2_token
            )
    @pytest.mark.asyncio

    async def test_get_client_with_valid_token(self, dcr_manager):
        """Test that get_client works with valid registration_access_token."""
        # Register a client
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
            "client_name": "Test Client",
        }
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        registration_token = registration_result['registration_access_token']
        # Get client with valid token
        client_data = await dcr_manager.get_client(
            client_id,
            registration_access_token=registration_token
        )
        assert client_data is not None
        assert client_data['client_id'] == client_id
        assert client_data['client_name'] == "Test Client"
        # registration_access_token should not be in response
        assert 'registration_access_token' not in client_data
    @pytest.mark.asyncio

    async def test_get_client_with_invalid_token(self, dcr_manager):
        """Test that get_client fails with invalid registration_access_token."""
        # Register a client
        client_metadata = {"redirect_uris": ["https://client.example.com/callback"]}
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        # Try to get client with invalid token
        with pytest.raises(XWInvalidRequestError):
            await dcr_manager.get_client(
                client_id,
                registration_access_token="invalid_token"
            )
    @pytest.mark.asyncio

    async def test_update_client_with_valid_token(self, dcr_manager):
        """Test that update_client works with valid registration_access_token."""
        # Register a client
        client_metadata = {
            "redirect_uris": ["https://client.example.com/callback"],
            "client_name": "Original Name",
        }
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        registration_token = registration_result['registration_access_token']
        # Update client with valid token
        updated_metadata = {"client_name": "Updated Name"}
        result = await dcr_manager.update_client(
            client_id,
            updated_metadata,
            registration_access_token=registration_token
        )
        assert result is not None
        assert result['client_name'] == "Updated Name"
    @pytest.mark.asyncio

    async def test_delete_client_with_valid_token(self, dcr_manager):
        """Test that delete_client works with valid registration_access_token."""
        # Register a client
        client_metadata = {"redirect_uris": ["https://client.example.com/callback"]}
        registration_result = await dcr_manager.register_client(client_metadata)
        client_id = registration_result['client_id']
        registration_token = registration_result['registration_access_token']
        # Delete client with valid token
        await dcr_manager.delete_client(
            client_id,
            registration_access_token=registration_token
        )
        # Verify client is deleted
        client_data = await dcr_manager.get_client(client_id)
        assert client_data is None
