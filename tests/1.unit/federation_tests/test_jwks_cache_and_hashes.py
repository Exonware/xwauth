#!/usr/bin/env python3
"""JWKS TTL cache and OIDC at_hash / c_hash broker integration."""

from __future__ import annotations

import base64
import time

import jwt
import pytest

from exonware.xwauth.identity.federation import FederationBroker, JwksDocumentCache
from exonware.xwauth.identity.federation.errors import XWFederationError
from exonware.xwauth.identity.federation.oidc_access_token_hash import (
    compute_at_hash,
    compute_c_hash,
    verify_at_hash,
)
from exonware.xwauth.identity.federation.oidc_id_token import OidcIdTokenValidationParams, validate_federated_id_token
from exonware.xwauth.connect.providers.registry import ProviderRegistry


class _Resp:
    def __init__(self, status: int, payload: dict) -> None:
        self.status_code = status
        self._payload = payload

    def json(self) -> dict:
        return self._payload


@pytest.mark.xwauth_unit
def test_compute_and_verify_at_hash() -> None:
    tok = "access-token-ascii"
    h = compute_at_hash(tok)
    assert verify_at_hash(tok, h, "HS256")
    assert not verify_at_hash("other", h, "HS256")


@pytest.mark.xwauth_unit
def test_at_hash_es384_uses_sha384_half() -> None:
    tok = "token-for-es384"
    h = compute_at_hash(tok, signing_alg="ES384")
    assert verify_at_hash(tok, h, "ES384")
    assert not verify_at_hash(tok, compute_at_hash(tok, "RS256"), "ES384")


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_jwks_cache_reuses_single_http_fetch() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks_body = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    calls: list[str] = []

    async def http_get(url: str) -> _Resp:
        calls.append(url)
        return _Resp(200, jwks_body)

    cache = JwksDocumentCache(ttl_seconds=3600.0)
    iss = "https://issuer.cache.test"
    aud = "client-z"

    def _tok(nonce: str) -> str:
        claims = {
            "sub": "u",
            "aud": aud,
            "iss": iss,
            "exp": int(time.time()) + 3600,
            "nonce": nonce,
        }
        return jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})

    params = OidcIdTokenValidationParams(issuer=iss, audience=aud, jwks_uri="https://idp.example/jwks")
    await validate_federated_id_token(
        _tok("a"),
        params,
        expected_nonce="a",
        http_get=http_get,
        jwks_document_cache=cache,
    )
    await validate_federated_id_token(
        _tok("b"),
        params,
        expected_nonce="b",
        http_get=http_get,
        jwks_document_cache=cache,
    )
    assert calls == ["https://idp.example/jwks"]


class _HashingOAuthProvider:
    """Returns id_token with at_hash/c_hash matching token response (HS256 + oct JWKS)."""

    @property
    def provider_name(self) -> str:
        return "hashoauth"

    @property
    def provider_type(self) -> str:
        return "openid_connect"

    async def get_authorization_url(self, client_id: str, redirect_uri: str, state: str, **_: object) -> str:
        return f"https://idp.example/authorize?client_id={client_id}&state={state}"

    async def exchange_code_for_token(self, code: str, redirect_uri: str, **_: object) -> dict:
        secret = b"unit-test-oct-key-32bytes-min!!"
        access_token = "acc-for-hash-test"
        at_h = compute_at_hash(access_token)
        c_h = compute_c_hash(code)
        claims = {
            "sub": "hash-user",
            "aud": "client-h1",
            "iss": "https://issuer.hash.test",
            "exp": int(time.time()) + 3600,
            "at_hash": at_h,
            "c_hash": c_h,
        }
        id_token = jwt.encode(claims, secret, algorithm="HS256", headers={"kid": "oct1"})
        return {"access_token": access_token, "id_token": id_token}

    async def get_user_info(self, access_token: str) -> dict:
        return {"sub": "hash-user", "email": "h@example.com"}


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_broker_oidc_hashes_verified_with_inline_jwks() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    vparams = OidcIdTokenValidationParams(
        issuer="https://issuer.hash.test",
        audience="client-h1",
        jwks=jwks,
    )
    reg = ProviderRegistry()
    reg.register(_HashingOAuthProvider())
    broker = FederationBroker(reg, jwks_cache_ttl_seconds=0)
    ident = await broker.complete_oauth2(
        "hashoauth",
        code="authorization-code-xyz",
        redirect_uri="https://app.example/cb",
        client_id="client-h1",
        id_token_validation=vparams,
    )
    assert ident.subject_id == "hash-user"
    assert ident.mapping_trace
    assert ident.mapping_trace.get("id_token_validation") == "jwks"
    oh = ident.mapping_trace.get("oidc_token_hashes")
    assert oh == {"at_hash": "verified", "c_hash": "verified"}


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_broker_oidc_at_hash_mismatch_raises() -> None:
    class _Bad(_HashingOAuthProvider):
        async def exchange_code_for_token(self, code: str, redirect_uri: str, **_: object) -> dict:
            out = await super().exchange_code_for_token(code, redirect_uri)
            out["access_token"] = "wrong-token"
            return out

    secret = b"unit-test-oct-key-32bytes-min!!"
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    vparams = OidcIdTokenValidationParams(
        issuer="https://issuer.hash.test",
        audience="client-h1",
        jwks=jwks,
    )
    reg = ProviderRegistry()
    reg.register(_Bad())
    broker = FederationBroker(reg, jwks_cache_ttl_seconds=0)
    with pytest.raises(XWFederationError, match="at_hash"):
        await broker.complete_oauth2(
            "hashoauth",
            code="authorization-code-xyz",
            redirect_uri="https://app.example/cb",
            client_id="client-h1",
            id_token_validation=vparams,
        )


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_broker_oidc_hashes_skipped_when_disabled() -> None:
    secret = b"unit-test-oct-key-32bytes-min!!"
    k = base64.urlsafe_b64encode(secret).decode("ascii").rstrip("=")
    jwks = {"keys": [{"kty": "oct", "k": k, "kid": "oct1", "alg": "HS256"}]}
    vparams = OidcIdTokenValidationParams(
        issuer="https://issuer.hash.test",
        audience="client-h1",
        jwks=jwks,
    )
    reg = ProviderRegistry()
    reg.register(_HashingOAuthProvider())
    broker = FederationBroker(reg, jwks_cache_ttl_seconds=0)
    ident = await broker.complete_oauth2(
        "hashoauth",
        code="authorization-code-xyz",
        redirect_uri="https://app.example/cb",
        client_id="client-h1",
        id_token_validation=vparams,
        verify_oidc_token_hashes=False,
    )
    oh = ident.mapping_trace.get("oidc_token_hashes")
    assert oh == {"at_hash": "skipped_disabled", "c_hash": "skipped_disabled"}
