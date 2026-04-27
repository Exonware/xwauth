#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/core_tests/test_oauth2.py
Unit tests for OAuth 2.0 core implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockStorageProvider
from exonware.xwauth.identity.core.oauth2 import OAuth2Server
from exonware.xwauth.identity.defs import GrantType
from exonware.xwauth.identity.errors import XWInvalidRequestError, XWUnsupportedResponseTypeError
@pytest.mark.xwauth_unit

class TestOAuth2Server:
    """Test OAuth2Server implementation."""
    @pytest.fixture

    def auth(self):
        """Create XWAuth instance."""
        from exonware.xwauth.identity.config.config import DEFAULT_TEST_CLIENTS
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
            allow_mock_storage_fallback=True,
        )
        return XWAuth(config=config)
    @pytest.fixture

    def oauth2_server(self, auth):
        """Create OAuth2Server instance."""
        return OAuth2Server(auth)
    @pytest.mark.asyncio

    async def test_authorize_with_code(self, oauth2_server):
        """Test authorization with code response type."""
        request = {
            'client_id': 'test',  # Use DEFAULT_TEST_CLIENTS client_id
            'redirect_uri': 'https://example.com/cb',  # Use DEFAULT_TEST_CLIENTS redirect_uri
            'response_type': 'code',
            'state': 'test_state',
            'code_challenge': 'test_challenge',
            'code_challenge_method': 'S256'
        }
        response = await oauth2_server.authorize(request)
        assert 'redirect_uri' in response
        assert 'code' in response
        assert 'state' in response
        assert response['state'] == 'test_state'
    @pytest.mark.asyncio

    async def test_authorize_invalid_response_type(self, oauth2_server):
        """Test authorization with invalid response type."""
        request = {
            'client_id': 'test',  # Use DEFAULT_TEST_CLIENTS client_id
            'redirect_uri': 'https://example.com/cb',  # Use DEFAULT_TEST_CLIENTS redirect_uri
            'response_type': 'invalid_type'
        }
        with pytest.raises(XWUnsupportedResponseTypeError):
            await oauth2_server.authorize(request)
    @pytest.mark.asyncio

    async def test_token_authorization_code(self, oauth2_server):
        """Test token endpoint with authorization code grant."""
        request = {
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'client_id': 'test',  # Use DEFAULT_TEST_CLIENTS client_id
            'redirect_uri': 'https://example.com/cb'  # Use DEFAULT_TEST_CLIENTS redirect_uri
        }
        # This will fail validation but tests the flow
        with pytest.raises(Exception):  # Will fail at validation
            await oauth2_server.token(request)
    @pytest.mark.asyncio

    async def test_token_client_credentials(self, oauth2_server):
        """Test token endpoint with client credentials grant."""
        request = {
            'grant_type': 'client_credentials',
            'client_id': 'test',  # Use DEFAULT_TEST_CLIENTS client_id
            'client_secret': 'secret'  # Use DEFAULT_TEST_CLIENTS client_secret
        }
        response = await oauth2_server.token(request)
        assert 'access_token' in response
        assert 'token_type' in response
        assert response['token_type'] == 'Bearer'
    @pytest.mark.asyncio

    async def test_token_invalid_grant_type(self, oauth2_server):
        """Test token endpoint with invalid grant type."""
        request = {
            'grant_type': 'invalid_grant',
            'client_id': 'test'  # Use DEFAULT_TEST_CLIENTS client_id
        }
        with pytest.raises(XWInvalidRequestError):
            await oauth2_server.token(request)
    @pytest.mark.asyncio

    async def test_token_missing_grant_type(self, oauth2_server):
        """Test token endpoint without grant_type."""
        request = {
            'client_id': 'test'  # Use DEFAULT_TEST_CLIENTS client_id
        }
        with pytest.raises(XWInvalidRequestError):
            await oauth2_server.token(request)
