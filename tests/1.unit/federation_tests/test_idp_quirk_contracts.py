#!/usr/bin/env python3
"""Contract-style tests for major IdP OIDC quirks (REF_25 #9)."""

from __future__ import annotations

import base64
import time

import jwt
import pytest

from exonware.xwauth.federation.errors import XWFederationError
from exonware.xwauth.federation.idp_quirks import (
    GOOGLE_OIDC_ISSUER,
    normalize_oidc_issuer_url,
    okta_authorization_server_base,
    suggested_entra_multitenant_additional_issuers,
)
from exonware.xwauth.federation.oidc_id_token import (
    OidcIdTokenValidationParams,
    fetch_openid_configuration,
    validate_federated_id_token,
)


@pytest.mark.xwauth_unit
def test_normalize_oidc_issuer_url_strips_slash_and_space() -> None:
    assert normalize_oidc_issuer_url("  https://issuer.example/  ") == "https://issuer.example"


@pytest.mark.xwauth_unit
def test_suggested_entra_multitenant_when_common_discovery() -> None:
    discovery = "https://login.microsoftonline.com/common/v2.0"
    token_iss = "https://login.microsoftonline.com/11111111-1111-1111-1111-111111111111/v2.0"
    assert suggested_entra_multitenant_additional_issuers(discovery, token_iss) == (token_iss,)


@pytest.mark.xwauth_unit
def test_suggested_entra_empty_when_issuers_match() -> None:
    iss = "https://login.microsoftonline.com/11111111-1111-1111-1111-111111111111/v2.0"
    assert suggested_entra_multitenant_additional_issuers(iss, iss) == ()


@pytest.mark.xwauth_unit
def test_suggested_entra_organizations_entrypoint() -> None:
    discovery = "https://login.microsoftonline.com/organizations/v2.0"
    token_iss = "https://login.microsoftonline.com/22222222-2222-2222-2222-222222222222/v2.0"
    assert suggested_entra_multitenant_additional_issuers(discovery, token_iss) == (token_iss,)


@pytest.mark.xwauth_unit
def test_suggested_entra_non_entra_returns_empty() -> None:
    assert suggested_entra_multitenant_additional_issuers(
        "https://corp.idp.example/",
        "https://corp.idp.example",
    ) == ()


@pytest.mark.xwauth_unit
def test_okta_authorization_server_base_normalizes() -> None:
    assert (
        okta_authorization_server_base("https://dev-12345.okta.com/oauth2/default/")
        == "https://dev-12345.okta.com/oauth2/default"
    )


@pytest.mark.xwauth_unit
def test_google_constant_normalized() -> None:
    assert normalize_oidc_issuer_url(GOOGLE_OIDC_ISSUER + "/") == GOOGLE_OIDC_ISSUER


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_fetch_openid_configuration_uses_normalized_issuer() -> None:
    urls: list[str] = []

    async def http_get(url: str):
        urls.append(url)

        class Resp:
            status_code = 200

            def json(self):
                return {"issuer": "https://example.idp"}

        return Resp()

    await fetch_openid_configuration("https://example.idp///", http_get)
    assert urls == ["https://example.idp/.well-known/openid-configuration"]


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_entra_common_discovery_accepts_tenant_token_iss() -> None:
    """id_token iss is tenant-specific; discovery used /common/ — use additional_allowed_issuers."""
    secret = b"unit-test-oct-key-32bytes-min!!"
    discovery_iss = "https://login.microsoftonline.com/common/v2.0"
    token_iss = "https://login.microsoftonline.com/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/v2.0"
    now = int(time.time())
    claims = {
        "sub": "entra-user-1",
        "aud": "azure-client-id",
        "iss": token_iss,
        "exp": now + 3600,
        "iat": now,
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    extra = suggested_entra_multitenant_additional_issuers(discovery_iss, token_iss)
    assert extra == (token_iss,)
    params = OidcIdTokenValidationParams(
        issuer=discovery_iss,
        additional_allowed_issuers=extra,
        audience="azure-client-id",
        jwks=jwks,
    )
    out = await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)
    assert out["sub"] == "entra-user-1"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_entra_common_discovery_fails_without_additional_issuer() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    discovery_iss = "https://login.microsoftonline.com/common/v2.0"
    token_iss = "https://login.microsoftonline.com/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/v2.0"
    now = int(time.time())
    claims = {
        "sub": "u",
        "aud": "c",
        "iss": token_iss,
        "exp": now + 3600,
        "iat": now,
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer=discovery_iss,
        audience="c",
        jwks=jwks,
    )
    with pytest.raises(XWFederationError):
        await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_google_shaped_string_audience_accepted() -> None:
    """Google id_tokens typically use a single string *aud* (OAuth client id)."""
    secret = b"unit-test-oct-key-32bytes-min!!"
    now = int(time.time())
    client_id = "123456789.apps.googleusercontent.com"
    claims = {
        "sub": "google-subject",
        "aud": client_id,
        "iss": GOOGLE_OIDC_ISSUER,
        "exp": now + 3600,
        "iat": now,
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer=GOOGLE_OIDC_ISSUER,
        audience=client_id,
        jwks=jwks,
    )
    out = await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)
    assert out["sub"] == "google-subject"
