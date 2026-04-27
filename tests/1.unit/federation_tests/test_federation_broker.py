#!/usr/bin/env python3
"""
Unit tests for federation broker normalization.
"""

from __future__ import annotations
import pytest
import jwt

from exonware.xwauth.identity.federation import FederationBroker
from exonware.xwauth.identity.federation.errors import XWFederationError
from exonware.xwauth.connect.providers.registry import ProviderRegistry


class _FakeOAuthProvider:
    @property
    def provider_name(self) -> str:
        return "fakeoauth"

    @property
    def provider_type(self) -> str:
        return "openid_connect"

    async def get_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes=None,
        nonce=None,
        code_verifier=None,
    ) -> str:
        q = f"https://idp.example/authorize?client_id={client_id}&state={state}"
        if nonce:
            q += f"&nonce={nonce}"
        if code_verifier:
            q += "&code_challenge=present"
        return q

    async def exchange_code_for_token(self, code: str, redirect_uri: str, *, code_verifier=None) -> dict:
        id_token = jwt.encode({"nonce": "n1"}, "secret", algorithm="HS256")
        return {"access_token": f"acc_{code}", "id_token": id_token}

    async def get_user_info(self, access_token: str) -> dict:
        return {"sub": "user-sub-1", "email": "user@example.com", "tid": "tenant-1"}


class _FakeLdapProvider:
    async def authenticate(self, credentials: dict) -> dict:
        return {"id": credentials["username"], "email": f'{credentials["username"]}@example.com'}


class _FakeLdapBindProvider:
    async def bind(self, username: str, password: str) -> bool:
        _ = password
        return bool(username)


class _FakeSamlProvider:
    def get_login_url(self, return_url: str) -> str:
        return f"https://idp.example/saml/login?RelayState={return_url}"

    async def complete_login(self, saml_response: str, relay_state: str | None = None) -> dict:
        _ = saml_response
        return {"sub": "saml-user-1", "email": "saml@example.com", "relay_state": relay_state}


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_oauth_normalization() -> None:
    registry = ProviderRegistry()
    registry.register(_FakeOAuthProvider())
    broker = FederationBroker(registry)

    url = await broker.start_oauth2(
        "fakeoauth",
        client_id="client-1",
        redirect_uri="https://app.example/cb",
        state="state123",
        scopes=["openid", "email"],
    )
    assert "state=state123" in url

    identity = await broker.complete_oauth2(
        "fakeoauth",
        code="abc",
        redirect_uri="https://app.example/cb",
    )
    assert identity.provider == "fakeoauth"
    assert identity.subject_id == "user-sub-1"
    assert identity.tenant_id == "tenant-1"
    assert identity.claims.get("access_token") == "acc_abc"
    assert identity.mapping_trace is not None
    assert identity.mapping_trace["subject_id"]["selected_key"] == "sub"
    assert identity.mapping_trace["tenant_id"]["selected_key"] == "tid"
    assert identity.mapping_trace.get("id_token_validation") == "unverified"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_ldap_normalization() -> None:
    broker = FederationBroker(ProviderRegistry())
    broker.register_ldap_provider("ldap_main", _FakeLdapProvider())
    identity = await broker.authenticate_ldap(
        "ldap_main",
        username="alice",
        password="pw",
    )
    assert identity.provider == "ldap_main"
    assert identity.subject_id == "alice"
    assert identity.mapping_trace is not None
    assert identity.mapping_trace["subject_id"]["selected_key"] == "id"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_ldap_bind_adapter_path() -> None:
    broker = FederationBroker(ProviderRegistry())
    broker.register_ldap_provider("ldap_bind", _FakeLdapBindProvider())
    identity = await broker.authenticate_ldap(
        "ldap_bind",
        username="bob",
        password="pw",
    )
    assert identity.provider == "ldap_bind"
    assert identity.subject_id == "bob"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_saml_normalization() -> None:
    broker = FederationBroker(ProviderRegistry())
    broker.register_saml_provider("saml", _FakeSamlProvider())
    login_url = await broker.start_saml("saml", relay_state="https://app.example/after-login")
    assert "RelayState=https://app.example/after-login" in login_url
    identity = await broker.complete_saml(
        "saml",
        saml_response="PHNhbWxSZXNwb25zZT4uLi48L3NhbWxSZXNwb25zZT4=",
        relay_state="https://app.example/after-login",
    )
    assert identity.provider == "saml"
    assert identity.subject_id == "saml-user-1"
    assert identity.email == "saml@example.com"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_oidc_nonce_validated() -> None:
    registry = ProviderRegistry()
    registry.register(_FakeOAuthProvider())
    broker = FederationBroker(registry)
    identity = await broker.complete_oauth2(
        "fakeoauth",
        code="abc",
        redirect_uri="https://app.example/cb",
        expected_nonce="n1",
    )
    assert identity.subject_id == "user-sub-1"
    assert identity.mapping_trace.get("id_token_validation") == "nonce_only"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_oidc_nonce_mismatch() -> None:
    registry = ProviderRegistry()
    registry.register(_FakeOAuthProvider())
    broker = FederationBroker(registry)
    with pytest.raises(XWFederationError):
        await broker.complete_oauth2(
            "fakeoauth",
            code="abc",
            redirect_uri="https://app.example/cb",
            expected_nonce="wrong",
        )


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_claim_mapping_v1() -> None:
    registry = ProviderRegistry()
    registry.register(_FakeOAuthProvider())
    broker = FederationBroker(registry)
    rules = [{"target": "email", "from": ["mail", "email"], "required": False}]
    identity = await broker.complete_oauth2(
        "fakeoauth",
        code="abc",
        redirect_uri="https://app.example/cb",
        claim_mapping_rules=rules,
    )
    assert identity.email == "user@example.com"
    assert identity.mapping_trace and "dsl_v1" in identity.mapping_trace


class _SparseUserInfoOAuthProvider(_FakeOAuthProvider):
    """Userinfo without email (e.g. Apple stub); extras come from callback *user* JSON."""

    async def get_user_info(self, access_token: str) -> dict:
        return {"sub": "user-sub-1", "tid": "tenant-1"}


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_federation_broker_extra_user_claims_fill_email() -> None:
    registry = ProviderRegistry()
    registry.register(_SparseUserInfoOAuthProvider())
    broker = FederationBroker(registry)
    identity = await broker.complete_oauth2(
        "fakeoauth",
        code="abc",
        redirect_uri="https://app.example/cb",
        extra_user_claims={
            "email": "from-form-post@example.com",
            "given_name": "Pat",
        },
    )
    assert identity.email == "from-form-post@example.com"
    assert identity.claims.get("given_name") == "Pat"
