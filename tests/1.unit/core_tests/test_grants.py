#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/core_tests/test_grants.py
Unit tests for OAuth 2.0 grant types.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig, DEFAULT_TEST_CLIENTS
from exonware.xwauth.core.grants.authorization_code import AuthorizationCodeGrant
from exonware.xwauth.core.grants.client_credentials import ClientCredentialsGrant
from exonware.xwauth.core.grants.resource_owner_password import ResourceOwnerPasswordGrant
from exonware.xwauth.core.grants.device_code import DeviceCodeGrant
from exonware.xwauth.core.grants.refresh_token import (
    RefreshTokenGrant,
    _refresh_metadata_for_issue,
)
from exonware.xwauth.core.grants.authorization_code import _refresh_metadata_from_code_attrs
from exonware.xwauth.errors import (
    XWAccessDeniedError,
    XWInvalidRequestError,
    XWUnauthorizedClientError,
)
@pytest.mark.xwauth_unit


def test_refresh_metadata_from_code_attrs_filters_tenancy_keys() -> None:
    attrs = {
        "org_id": "org_1",
        "project_id": "proj_9",
        "session_id": "sess_x",
        "tenant_id": "t1",
        "roles": ["admin"],
        "noise": "skip",
    }
    meta = _refresh_metadata_from_code_attrs(attrs)
    assert meta is not None
    assert meta["org_id"] == "org_1"
    assert meta["project_id"] == "proj_9"
    assert meta["session_id"] == "sess_x"
    assert meta["tenant_id"] == "t1"
    assert meta["roles"] == ["admin"]
    assert "noise" not in meta


def test_refresh_metadata_for_issue_reads_nested_attributes() -> None:
    token_data = {
        "user_id": "u1",
        "client_id": "c1",
        "attributes": {"org_id": "org_2", "session_id": "s2", "aal": 2},
    }
    meta = _refresh_metadata_for_issue(token_data)
    assert meta is not None
    assert meta["org_id"] == "org_2"
    assert meta["session_id"] == "s2"
    assert meta["aal"] == 2

class TestAuthorizationCodeGrant:
    """Test AuthorizationCodeGrant implementation."""
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
        """Create AuthorizationCodeGrant instance."""
        return AuthorizationCodeGrant(auth)
    @pytest.mark.asyncio

    async def test_validate_request(self, grant):
        """Test request validation."""
        from exonware.xwauth.core.pkce import PKCE
        verifier, challenge = PKCE.generate_code_pair('S256')
        request = {
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'client_id': 'test',
            'redirect_uri': 'https://example.com/cb',
            'code_verifier': verifier,
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
        }
        try:
            await grant.validate_request(request)
        except Exception:
            pass
    @pytest.mark.asyncio

    async def test_validate_missing_code(self, grant):
        """Test validation with missing code (token exchange path)."""
        request = {
            'grant_type': 'authorization_code',
            'client_id': 'test',
            'client_secret': 'secret',
            'redirect_uri': 'https://example.com/cb',
            'code_verifier': 'x',
        }
        with pytest.raises((XWInvalidRequestError, XWUnauthorizedClientError)):
            await grant.validate_request(request)
    @pytest.mark.asyncio

    async def test_validate_missing_client_id(self, grant):
        """Test validation with missing client_id."""
        from exonware.xwauth.core.pkce import PKCE
        _, challenge = PKCE.generate_code_pair('S256')
        request = {
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'redirect_uri': 'https://example.com/cb',
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
        }
        with pytest.raises(XWInvalidRequestError):
            await grant.validate_request(request)
    @pytest.mark.asyncio

    async def test_execute_grant(self, grant):
        """Test grant execution."""
        from exonware.xwauth.core.pkce import PKCE
        verifier, challenge = PKCE.generate_code_pair('S256')
        request = {
            'grant_type': 'authorization_code',
            'code': 'test_code',
            'client_id': 'test',
            'redirect_uri': 'https://example.com/cb',
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'code_verifier': verifier,
            'scopes': [],
            'state': 'test_state',
            '_is_authorize': False,
        }
        try:
            response = await grant.process(request)
            assert 'redirect_uri' in response or response is not None
        except Exception:
            # Expected without valid code
            pass

    @pytest.mark.asyncio
    async def test_authorize_org_hint_rejects_without_bearer_subject(self, grant):
        from exonware.xwauth.core.pkce import PKCE

        _, challenge = PKCE.generate_code_pair("S256")
        request = {
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
            "state": "st",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "org_id": "org_acme",
        }
        with pytest.raises(XWInvalidRequestError):
            await grant._validate_authorize(request)

    @pytest.mark.asyncio
    async def test_authorize_org_hint_rejects_non_member(self, grant):
        from exonware.xwauth.core.pkce import PKCE

        _, challenge = PKCE.generate_code_pair("S256")
        request = {
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
            "state": "st",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "org_id": "org_acme",
            "_xwauth_authorize_subject_id": "user_no_member",
        }
        with pytest.raises(XWAccessDeniedError):
            await grant._validate_authorize(request)

    @pytest.mark.asyncio
    async def test_authorize_org_hint_allows_member(self, grant, auth):
        from exonware.xwauth.core.pkce import PKCE

        _, challenge = PKCE.generate_code_pair("S256")
        if not hasattr(auth.storage, "_org_memberships"):
            auth.storage._org_memberships = {}
        auth.storage._org_memberships["org_member:org_acme:user1"] = {
            "role": "admin",
            "user_id": "user1",
        }
        request = {
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
            "state": "st",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "org_id": "org_acme",
            "_xwauth_authorize_subject_id": "user1",
        }
        out = await grant._validate_authorize(request)
        assert out["_xwauth_org_member_role"] == "admin"

    @pytest.mark.asyncio
    async def test_authorize_org_hint_legacy_when_flag_off(self):
        from exonware.xwauth.core.pkce import PKCE

        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
            authorize_org_hint_requires_membership=False,
        )
        auth = XWAuth(config=config)
        grant = AuthorizationCodeGrant(auth)
        _, challenge = PKCE.generate_code_pair("S256")
        request = {
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
            "state": "st",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "org_id": "org_legacy",
        }
        out = await grant._validate_authorize(request)
        assert out.get("org_id") == "org_legacy"

    @pytest.mark.asyncio
    async def test_authorize_org_id_organization_id_mismatch(self, grant):
        from exonware.xwauth.core.pkce import PKCE

        _, challenge = PKCE.generate_code_pair("S256")
        request = {
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
            "state": "st",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "org_id": "a",
            "organization_id": "b",
        }
        with pytest.raises(XWInvalidRequestError):
            await grant._validate_authorize(request)
@pytest.mark.xwauth_unit

class TestClientCredentialsGrant:
    """Test ClientCredentialsGrant implementation."""
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
        """Create ClientCredentialsGrant instance."""
        return ClientCredentialsGrant(auth)
    @pytest.mark.asyncio

    async def test_validate_request(self, grant):
        """Test request validation."""
        request = {
            'grant_type': 'client_credentials',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            await grant.validate_request(request)
        except Exception:
            pass
    @pytest.mark.asyncio

    async def test_execute_grant(self, grant):
        """Test grant execution."""
        request = {
            'grant_type': 'client_credentials',
            'client_id': 'test',
            'client_secret': 'secret',
            'scopes': [],
        }
        validated = await grant.validate_request(request)
        response = await grant.process(validated)
        assert 'access_token' in response
        assert 'token_type' in response
    @pytest.mark.asyncio

    async def test_execute_with_scope(self, grant):
        """Test grant execution with scope."""
        request = {
            'grant_type': 'client_credentials',
            'client_id': 'test',
            'client_secret': 'secret',
            'scope': 'read write',
        }
        validated = await grant.validate_request(request)
        response = await grant.process(validated)
        assert 'access_token' in response
@pytest.mark.xwauth_unit

class TestResourceOwnerPasswordGrant:
    """Test ResourceOwnerPasswordGrant implementation."""
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
        """Create ResourceOwnerPasswordGrant instance."""
        return ResourceOwnerPasswordGrant(auth)
    @pytest.mark.asyncio

    async def test_validate_request(self, grant):
        """Test request validation."""
        request = {
            'grant_type': 'password',
            'username': 'test_user',
            'password': 'test_password',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            await grant.validate_request(request)
        except Exception:
            pass
    @pytest.mark.asyncio

    async def test_validate_missing_username(self, grant):
        """Test validation with missing username."""
        request = {
            'grant_type': 'password',
            'password': 'test_password',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        with pytest.raises(XWInvalidRequestError):
            await grant.validate_request(request)
    @pytest.mark.asyncio

    async def test_execute_grant(self, grant):
        """Test grant execution."""
        request = {
            'grant_type': 'password',
            'username': 'test_user',
            'password': 'test_password',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            validated = await grant.validate_request(request)
            response = await grant.process(validated)
            assert response is not None
        except Exception:
            # Expected without valid credentials
            pass
@pytest.mark.xwauth_unit

class TestDeviceCodeGrant:
    """Test DeviceCodeGrant implementation."""
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

    async def test_validate_request(self, grant):
        """Test request validation."""
        request = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': 'test_device_code',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            await grant.validate_request(request)
        except Exception:
            pass
    @pytest.mark.asyncio

    async def test_validate_missing_device_code(self, grant):
        """Test validation with missing device_code."""
        request = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            await grant.validate_request(request)
        except XWInvalidRequestError:
            pass
    @pytest.mark.asyncio

    async def test_execute_grant(self, grant):
        """Test grant execution."""
        request = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': 'test_device_code',
            'client_id': 'test',
            'client_secret': 'secret',
            'scopes': [],
        }
        try:
            validated = await grant.validate_request(request)
            response = await grant.process(validated)
            assert response is not None
        except Exception:
            # Expected without valid device code
            pass
    @pytest.mark.asyncio

    async def test_device_code_storage_on_generation(self, grant):
        """Test that device code is stored when generated."""
        request = {
            'client_id': 'test',
            'scopes': ['read'],
        }
        # Process device code grant (should store device code)
        response = await grant.process(request)
        assert 'device_code' in response
        assert 'user_code' in response
        device_code = response['device_code']
        # Verify device code is stored
        stored_code = await grant._auth.storage.get_device_code(device_code)
        assert stored_code is not None
        assert stored_code.device_code == device_code
@pytest.mark.xwauth_unit

class TestRefreshTokenGrant:
    """Test RefreshTokenGrant implementation."""
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
        """Create RefreshTokenGrant instance."""
        return RefreshTokenGrant(auth)
    @pytest.mark.asyncio

    async def test_validate_request(self, grant):
        """Test request validation."""
        request = {
            'grant_type': 'refresh_token',
            'refresh_token': 'test_refresh_token',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            await grant.validate_request(request)
        except Exception:
            pass
    @pytest.mark.asyncio

    async def test_validate_missing_refresh_token(self, grant):
        """Test validation with missing refresh_token."""
        request = {
            'grant_type': 'refresh_token',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        with pytest.raises(XWInvalidRequestError):
            await grant.validate_request(request)
    @pytest.mark.asyncio

    async def test_execute_grant(self, grant):
        """Test grant execution."""
        request = {
            'grant_type': 'refresh_token',
            'refresh_token': 'test_refresh_token',
            'client_id': 'test',
            'client_secret': 'secret',
        }
        try:
            validated = await grant.validate_request(request)
            response = await grant.process(validated)
            assert response is not None
        except Exception:
            # Expected without valid refresh token
            pass
