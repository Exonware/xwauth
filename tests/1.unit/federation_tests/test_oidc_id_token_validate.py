#!/usr/bin/env python3
"""JWKS-backed id_token validation (OIDC-style)."""

from __future__ import annotations

import base64
import time

import jwt
import pytest

from exonware.xwauth.federation.errors import XWFederationError
from exonware.xwauth.federation.oidc_id_token import OidcIdTokenValidationParams, validate_federated_id_token


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_federated_id_token_hs256_inline_jwks() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    claims = {
        "sub": "user-oidc-1",
        "aud": "client-99",
        "iss": "https://issuer.example.test",
        "exp": int(time.time()) + 3600,
        "nonce": "abc123",
        "email": "u@issuer.example.test",
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.example.test",
        audience="client-99",
        jwks=jwks,
    )
    out = await validate_federated_id_token(
        id_token,
        params,
        expected_nonce="abc123",
        http_get=None,
    )
    assert out["sub"] == "user-oidc-1"
    assert out["email"] == "u@issuer.example.test"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_federated_id_token_nonce_mismatch() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    claims = {
        "sub": "u",
        "aud": "c",
        "iss": "https://issuer.example.test",
        "exp": int(time.time()) + 3600,
        "nonce": "good",
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.example.test",
        audience="c",
        jwks=jwks,
    )
    with pytest.raises(XWFederationError):
        await validate_federated_id_token(
            id_token,
            params,
            expected_nonce="wrong",
            http_get=None,
        )


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_federated_id_token_multi_aud_pyjwt() -> None:
    """PyJWT accepts *aud* as a list when our expected client id is one of the audiences."""
    secret = b"unit-test-oct-key-32bytes-min!!"
    now = int(time.time())
    claims = {
        "sub": "u1",
        "aud": ["https://api.example", "client-99"],
        "iss": "https://issuer.example.test",
        "exp": now + 3600,
        "iat": now,
        "azp": "client-99",
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.example.test",
        audience="client-99",
        jwks=jwks,
        expected_azp="client-99",
    )
    out = await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)
    assert out["sub"] == "u1"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_federated_id_token_azp_mismatch() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    now = int(time.time())
    claims = {
        "sub": "u1",
        "aud": ["a", "client-99"],
        "iss": "https://issuer.example.test",
        "exp": now + 3600,
        "iat": now,
        "azp": "other-client",
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.example.test",
        audience="client-99",
        jwks=jwks,
        expected_azp="client-99",
    )
    with pytest.raises(XWFederationError, match="azp"):
        await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_federated_id_token_require_iat() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    claims = {
        "sub": "u",
        "aud": "c",
        "iss": "https://issuer.example.test",
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.example.test",
        audience="c",
        jwks=jwks,
        require_iat=True,
    )
    with pytest.raises(XWFederationError):
        await validate_federated_id_token(id_token, params, expected_nonce=None, http_get=None)


@pytest.mark.xwauth_unit
def test_generate_pkce_round_trip() -> None:
    from exonware.xwauth.federation.pkce import generate_pkce_pair
    from exonware.xwauth.providers.base import ABaseProvider

    verifier, challenge = generate_pkce_pair()
    assert len(verifier) >= 43
    assert ABaseProvider._pkce_s256_challenge(verifier) == challenge
