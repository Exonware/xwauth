#!/usr/bin/env python3
"""JWKS refetch on verify failure, multi-issuer, JWKS negative cache."""

from __future__ import annotations

import asyncio
import base64
import time

import jwt
import pytest

from exonware.xwauth.identity.federation.errors import XWFederationError
from exonware.xwauth.identity.federation.jwks_cache import JwksDocumentCache
from exonware.xwauth.identity.federation.oidc_id_token import (
    OidcIdTokenValidationParams,
    fetch_jwks,
    validate_federated_id_token,
)


class _Resp:
    def __init__(self, status: int, payload: dict) -> None:
        self.status_code = status
        self._payload = payload

    def json(self) -> dict:
        return self._payload


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_validate_id_token_accepts_additional_issuer() -> None:
    """Tenant-specific *iss* while primary *issuer* is the common/metadata issuer."""
    secret = b"unit-test-oct-key-32bytes-min!!"
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    tenant_iss = "https://login.example.com/11111111-1111-1111-1111-111111111111/v2.0"
    common_iss = "https://login.example.com/common/v2.0"
    claims = {
        "sub": "u-ms",
        "aud": "client-ms",
        "iss": tenant_iss,
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
    params = OidcIdTokenValidationParams(
        issuer=common_iss,
        audience="client-ms",
        jwks=jwks,
        additional_allowed_issuers=(tenant_iss,),
    )
    out = await validate_federated_id_token(
        id_token, params, expected_nonce=None, http_get=None
    )
    assert out["sub"] == "u-ms"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_jwks_refetch_after_signature_failure() -> None:
    """Stale cached JWKS: first verify fails, invalidate + refetch succeeds (rotation)."""
    secret_old = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    secret_new = b"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    k_old = base64.urlsafe_b64encode(secret_old).decode("ascii").rstrip("=")
    k_new = base64.urlsafe_b64encode(secret_new).decode("ascii").rstrip("=")
    jwks_old = {
        "keys": [{"kty": "oct", "k": k_old, "kid": "kid-old", "alg": "HS256"}]
    }
    jwks_new = {
        "keys": [
            {"kty": "oct", "k": k_old, "kid": "kid-old", "alg": "HS256"},
            {"kty": "oct", "k": k_new, "kid": "kid-new", "alg": "HS256"},
        ]
    }
    iss = "https://issuer.rotate.test"
    aud = "client-r"
    claims = {
        "sub": "u-rot",
        "aud": aud,
        "iss": iss,
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(
        claims, secret_new, algorithm="HS256", headers={"kid": "kid-new"}
    )

    urls: list[str] = []

    async def http_get(url: str) -> _Resp:
        urls.append(url)
        if len(urls) == 1:
            return _Resp(200, jwks_old)
        return _Resp(200, jwks_new)

    cache = JwksDocumentCache(ttl_seconds=3600.0, negative_cache_ttl_seconds=0.0)
    params = OidcIdTokenValidationParams(issuer=iss, audience=aud, jwks_uri="https://idp/jwks")
    out = await validate_federated_id_token(
        id_token,
        params,
        expected_nonce=None,
        http_get=http_get,
        jwks_document_cache=cache,
    )
    assert out["sub"] == "u-rot"
    assert len(urls) == 2


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_jwks_refetch_disabled_single_fetch_fails() -> None:
    secret_old = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    secret_new = b"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    k_old = base64.urlsafe_b64encode(secret_old).decode("ascii").rstrip("=")
    k_new = base64.urlsafe_b64encode(secret_new).decode("ascii").rstrip("=")
    jwks_old = {
        "keys": [{"kty": "oct", "k": k_old, "kid": "kid-old", "alg": "HS256"}]
    }
    jwks_new = {
        "keys": [
            {"kty": "oct", "k": k_old, "kid": "kid-old", "alg": "HS256"},
            {"kty": "oct", "k": k_new, "kid": "kid-new", "alg": "HS256"},
        ]
    }
    iss = "https://issuer.noref.test"
    aud = "client-nr"
    claims = {
        "sub": "u",
        "aud": aud,
        "iss": iss,
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(
        claims, secret_new, algorithm="HS256", headers={"kid": "kid-new"}
    )
    urls: list[str] = []

    async def http_get(url: str) -> _Resp:
        urls.append(url)
        if len(urls) == 1:
            return _Resp(200, jwks_old)
        return _Resp(200, jwks_new)

    cache = JwksDocumentCache(ttl_seconds=3600.0, negative_cache_ttl_seconds=0.0)
    params = OidcIdTokenValidationParams(
        issuer=iss,
        audience=aud,
        jwks_uri="https://idp/jwks",
        jwks_refetch_on_verify_failure=False,
    )
    with pytest.raises(XWFederationError):
        await validate_federated_id_token(
            id_token,
            params,
            expected_nonce=None,
            http_get=http_get,
            jwks_document_cache=cache,
        )
    assert len(urls) == 1


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_multi_jwk_try_succeeds_when_header_kid_wrong_key() -> None:
    """IdP advertised *kid* does not match signing key: try remaining JWKS entries."""
    s1 = b"11111111111111111111111111111111"
    s2 = b"22222222222222222222222222222222"
    k1 = base64.urlsafe_b64encode(s1).decode("ascii").rstrip("=")
    k2 = base64.urlsafe_b64encode(s2).decode("ascii").rstrip("=")
    jwks = {
        "keys": [
            {"kty": "oct", "k": k1, "kid": "kid-1", "alg": "HS256"},
            {"kty": "oct", "k": k2, "kid": "kid-2", "alg": "HS256"},
        ]
    }
    iss = "https://issuer.multi.test"
    aud = "client-m"
    claims = {
        "sub": "u-multi",
        "aud": aud,
        "iss": iss,
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(
        claims, s2, algorithm="HS256", headers={"kid": "kid-1"}
    )
    params = OidcIdTokenValidationParams(issuer=iss, audience=aud, jwks=jwks)
    out = await validate_federated_id_token(
        id_token, params, expected_nonce=None, http_get=None
    )
    assert out["sub"] == "u-multi"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_max_jwks_verify_attempts_limits_tries() -> None:
    s1 = b"11111111111111111111111111111111"
    s2 = b"22222222222222222222222222222222"
    k1 = base64.urlsafe_b64encode(s1).decode("ascii").rstrip("=")
    k2 = base64.urlsafe_b64encode(s2).decode("ascii").rstrip("=")
    jwks = {
        "keys": [
            {"kty": "oct", "k": k1, "kid": "kid-1", "alg": "HS256"},
            {"kty": "oct", "k": k2, "kid": "kid-2", "alg": "HS256"},
        ]
    }
    claims = {
        "sub": "u",
        "aud": "c",
        "iss": "https://issuer.cap.test",
        "exp": int(time.time()) + 3600,
    }
    id_token = jwt.encode(
        claims, s2, algorithm="HS256", headers={"kid": "kid-1"}
    )
    params = OidcIdTokenValidationParams(
        issuer="https://issuer.cap.test",
        audience="c",
        jwks=jwks,
        max_jwks_verify_attempts=1,
    )
    with pytest.raises(XWFederationError):
        await validate_federated_id_token(
            id_token, params, expected_nonce=None, http_get=None
        )


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_jwks_negative_cache_suppresses_repeat_fetch() -> None:
    calls = 0

    async def http_get(url: str) -> _Resp:
        nonlocal calls
        calls += 1
        raise RuntimeError("idp down")

    cache = JwksDocumentCache(
        ttl_seconds=3600.0,
        negative_cache_ttl_seconds=0.08,
    )
    uri = "https://idp/jwks"

    with pytest.raises(RuntimeError):
        await cache.get_or_fetch(uri, http_get, fetch_jwks)
    assert calls == 1

    with pytest.raises(XWFederationError, match="recent fetch failure"):
        await cache.get_or_fetch(uri, http_get, fetch_jwks)
    assert calls == 1

    await asyncio.sleep(0.12)
    with pytest.raises(RuntimeError):
        await cache.get_or_fetch(uri, http_get, fetch_jwks)
    assert calls == 2
