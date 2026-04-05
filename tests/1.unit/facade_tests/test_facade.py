#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/facade_tests/test_facade.py
Unit tests for XWAuth facade.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import DEFAULT_TEST_CLIENTS, XWAuthConfig
from exonware.xwauth.errors import XWAuthError, XWOAuthError
from exonware.xwauth.storage.mock import MockStorageProvider
from exonware.xwauth.providers.base import ABaseProvider
from exonware.xwauth.defs import ProviderType
from exonware.xwauth.scim import ScimService
@pytest.mark.xwauth_unit

class TestXWAuthFacade:
    """Test XWAuth facade implementation."""

    def test_facade_initialization(self):
        """Test facade initialization."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert auth is not None
        assert auth.config is not None
        assert auth.storage is not None

    def test_facade_initialization_with_storage(self):
        """Test facade initialization with custom storage."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        storage = MockStorageProvider()
        auth = XWAuth(config=config, storage=storage)
        assert auth.storage == storage

    def test_facade_initialization_missing_config(self):
        """Test facade initialization without config."""
        with pytest.raises(XWAuthError):
            XWAuth()

    def test_facade_authorize_method(self):
        """Test facade authorize method."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert hasattr(auth, 'authorize')
        assert callable(auth.authorize)

    def test_facade_token_method(self):
        """Test facade token method."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert hasattr(auth, 'token')
        assert callable(auth.token)

    def test_facade_exposes_scim_services(self):
        """Facade should expose SCIM user/group service instances."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert isinstance(auth.scim_users, ScimService)
        assert isinstance(auth.scim_groups, ScimService)
        assert auth.scim_users.resource_type == "User"
        assert auth.scim_groups.resource_type == "Group"

    def test_facade_introspect_token_method(self):
        """Test facade introspect_token method."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert hasattr(auth, 'introspect_token')
        assert callable(auth.introspect_token)

    def test_facade_revoke_token_method(self):
        """Test facade revoke_token method."""
        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        assert hasattr(auth, 'revoke_token')
        assert callable(auth.revoke_token)
    @pytest.mark.asyncio

    async def test_facade_authorize_flow(self):
        """Test facade authorize flow."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=[
                {"client_id": "test_client", "redirect_uris": ["https://example.com/callback"]}
            ],
        )
        auth = XWAuth(config=config)
        from exonware.xwauth.core.pkce import PKCE
        verifier, challenge = PKCE.generate_code_pair('S256')
        request = {
            'client_id': 'test_client',
            'redirect_uri': 'https://example.com/callback',
            'response_type': 'code',
            'state': 'test_state',
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
        response = await auth.authorize(request)
        assert 'code' in response or 'redirect_uri' in response
    @pytest.mark.asyncio

    async def test_facade_token_flow(self):
        """Test facade token flow."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=[
                {"client_id": "test_client", "client_secret": "test_secret", "redirect_uris": ["https://example.com/cb"]}
            ],
        )
        auth = XWAuth(config=config)
        request = {
            'grant_type': 'client_credentials',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        }
        response = await auth.token(request)
        assert 'access_token' in response
    @pytest.mark.asyncio

    async def test_facade_token_introspection(self):
        """Test facade token introspection."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=[
                {"client_id": "test_client", "client_secret": "test_secret", "redirect_uris": ["https://example.com/cb"]}
            ],
        )
        auth = XWAuth(config=config)
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        }
        token_response = await auth.token(token_request)
        access_token = token_response['access_token']
        introspection = await auth.introspect_token(access_token)
        assert introspection is not None
    @pytest.mark.asyncio

    async def test_facade_token_revocation(self):
        """Test facade token revocation."""
        config = XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=[
                {"client_id": "test_client", "client_secret": "test_secret", "redirect_uris": ["https://example.com/cb"]}
            ],
        )
        auth = XWAuth(config=config)
        token_request = {
            'grant_type': 'client_credentials',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        }
        token_response = await auth.token(token_request)
        access_token = token_response['access_token']
        await auth.revoke_token(access_token)
        try:
            await auth.introspect_token(access_token)
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_facade_authz_decision_emits_audit_event(self):
        """check_permission_context should create an immutable authz audit record."""
        from exonware.xwauth.contracts import AuthContext

        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        context = AuthContext(
            subject_id="user-1",
            tenant_id="tenant-1",
            scopes=["storage:read"],
            roles=["member"],
        )
        allowed = await auth.check_permission_context(context, resource="bucket:x", action="read")
        assert allowed is True
        logs = await auth.storage.get_audit_logs({"action": "authz.decision"})
        assert len(logs) >= 1
        assert logs[-1].attributes.get("allowed") is True

    @pytest.mark.asyncio
    async def test_facade_federation_broker_flow(self):
        """Facade federation methods should normalize OAuth provider callback results."""

        class _FakeProvider(ABaseProvider):
            @property
            def provider_type(self) -> ProviderType:
                return ProviderType.OPENID_CONNECT

            async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
                return {"access_token": f"acc_{code}"}

            async def get_user_info(self, access_token: str) -> dict:
                return {"sub": "sub-1", "email": "user@example.com", "tid": "tenant-1"}

        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        auth.register_provider(
            _FakeProvider(
                client_id="cid",
                client_secret="sec",
                authorization_url="https://idp.example/authorize",
                token_url="https://idp.example/token",
                userinfo_url="https://idp.example/userinfo",
            )
        )

        identity = await auth.complete_federation_login(
            "openid_connect",
            code="abc",
            redirect_uri="https://app.example/callback",
        )
        assert identity.subject_id == "sub-1"
        assert identity.email == "user@example.com"
        assert identity.tenant_id == "tenant-1"

    @pytest.mark.asyncio
    async def test_facade_federation_saml_flow(self):
        """Facade SAML federation methods should normalize SAML callback results."""

        class _FakeSamlProvider:
            def get_login_url(self, return_url: str) -> str:
                return f"https://idp.example/saml/login?RelayState={return_url}"

            async def complete_login(self, saml_response: str, relay_state: str | None = None) -> dict:
                _ = saml_response
                return {"sub": "saml-sub-1", "email": "saml@example.com", "relay_state": relay_state}

        config = XWAuthConfig(jwt_secret="test-secret-key")
        auth = XWAuth(config=config)
        auth.register_saml_provider("saml", _FakeSamlProvider())

        login_url = await auth.start_federation_saml("saml", relay_state="https://app.example/after-login")
        assert "RelayState=https://app.example/after-login" in login_url
        identity = await auth.complete_federation_saml(
            "saml",
            saml_response="PHNhbWxSZXNwb25zZT4uLi48L3NhbWxSZXNwb25zZT4=",
            relay_state="https://app.example/after-login",
        )
        assert identity.subject_id == "saml-sub-1"
        assert identity.email == "saml@example.com"

    @pytest.mark.asyncio
    async def test_facade_get_userinfo_rejects_missing_and_invalid_tokens(self) -> None:
        auth = XWAuth(
            config=XWAuthConfig(
                jwt_secret="userinfo-facade-secret",
                registered_clients=DEFAULT_TEST_CLIENTS,
            ),
        )
        with pytest.raises(XWOAuthError) as exc_info:
            await auth.get_userinfo("")
        assert exc_info.value.error_code == "invalid_token"

        with pytest.raises(XWOAuthError) as exc_info2:
            await auth.get_userinfo("not.a.valid.jwt")
        assert exc_info2.value.error_code == "invalid_token"

    @pytest.mark.asyncio
    async def test_facade_get_userinfo_accepts_active_access_token(self) -> None:
        auth = XWAuth(
            config=XWAuthConfig(
                jwt_secret="userinfo-facade-cc-secret",
                registered_clients=DEFAULT_TEST_CLIENTS,
            ),
        )
        token_bundle = await auth.token(
            {
                "grant_type": "client_credentials",
                "client_id": "test",
                "client_secret": "secret",
            }
        )
        access = token_bundle.get("access_token")
        assert access
        claims = await auth.get_userinfo(access)
        assert claims.get("sub") == "test"
