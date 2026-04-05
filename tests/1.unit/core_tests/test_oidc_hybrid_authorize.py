#!/usr/bin/env python3
"""OIDC hybrid authorize (code id_token, code token, form_post) — unit tests."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlparse

import jwt
import pytest

from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import DEFAULT_TEST_CLIENTS, XWAuthConfig
from exonware.xwauth.core.pkce import PKCE
from exonware.xwauth.errors import (
    XWConfigError,
    XWInvalidRequestError,
    XWUnsupportedResponseTypeError,
)
from exonware.xwauth.tokens.jwt import oidc_left_half_sha256_b64url
from exonware.xwauth.tokens.oidc_id_token_signing import resolve_id_token_signing

pytestmark = pytest.mark.xwauth_unit


def _base_authorize_req(**overrides):
    _v, challenge = PKCE.generate_code_pair("S256")
    req = {
        "client_id": "test",
        "redirect_uri": "https://example.com/cb",
        "scope": "openid",
        "state": "st-1",
        "nonce": "nonce-1",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "_xwauth_authorize_subject_id": "user-42",
        "response_type": "code id_token",
    }
    req.update(overrides)
    return req


@pytest.mark.asyncio
async def test_implicit_only_response_type_rejected() -> None:
    cfg = XWAuthConfig(
        jwt_secret="secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    with pytest.raises(XWUnsupportedResponseTypeError):
        await auth.authorize(
            {
                "client_id": "test",
                "redirect_uri": "https://example.com/cb",
                "response_type": "id_token",
                "scope": "openid",
                "state": "s",
                "nonce": "n",
            }
        )


@pytest.mark.asyncio
async def test_code_id_token_default_fragment_c_hash() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(_base_authorize_req())
    url = urlparse(out["redirect_uri"])
    assert url.fragment
    frag = dict(parse_qsl(url.fragment))
    assert frag.get("state") == "st-1"
    code = frag["code"]
    payload = jwt.decode(
        frag["id_token"],
        "unit-test-secret",
        algorithms=["HS256"],
        audience="test",
    )
    assert payload["sub"] == "user-42"
    assert payload["nonce"] == "nonce-1"
    assert payload["iss"] == "https://as.example"
    assert payload["c_hash"] == oidc_left_half_sha256_b64url(code)
    assert "at_hash" not in payload


@pytest.mark.asyncio
async def test_code_id_token_token_includes_at_hash() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
        oauth21_compliant=False,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(_base_authorize_req(response_type="code id_token token"))
    url = urlparse(out["redirect_uri"])
    frag = dict(parse_qsl(url.fragment))
    at = frag["access_token"]
    payload = jwt.decode(
        frag["id_token"],
        "unit-test-secret",
        algorithms=["HS256"],
        audience="test",
    )
    assert payload["at_hash"] == oidc_left_half_sha256_b64url(at)
    assert payload["c_hash"] == oidc_left_half_sha256_b64url(frag["code"])


@pytest.mark.asyncio
async def test_oauth21_rejects_access_token_in_authorize_response() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
        oauth21_compliant=True,
    )
    auth = XWAuth(config=cfg)
    with pytest.raises(XWInvalidRequestError):
        await auth.authorize(_base_authorize_req(response_type="code id_token token"))


@pytest.mark.asyncio
async def test_response_mode_query() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(
        _base_authorize_req(
            response_mode="query",
            redirect_uri="https://example.com/cb",
        )
    )
    url = urlparse(out["redirect_uri"])
    assert url.query
    q = dict(parse_qsl(url.query))
    assert "code" in q and "id_token" in q


@pytest.mark.asyncio
async def test_id_token_requires_openid_scope() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    with pytest.raises(XWInvalidRequestError):
        await auth.authorize(_base_authorize_req(scope="profile"))


@pytest.mark.asyncio
async def test_id_token_requires_nonce() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    req = _base_authorize_req()
    del req["nonce"]
    with pytest.raises(XWInvalidRequestError):
        await auth.authorize(req)


@pytest.mark.asyncio
async def test_id_token_requires_oidc_issuer_config() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    with pytest.raises(XWInvalidRequestError):
        await auth.authorize(_base_authorize_req())


@pytest.mark.asyncio
async def test_oidc_id_token_lifetime_override() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        oidc_id_token_lifetime_seconds=90,
        access_token_lifetime=3600,
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(_base_authorize_req())
    from urllib.parse import parse_qsl, urlparse

    frag = dict(parse_qsl(urlparse(out["redirect_uri"]).fragment))
    payload = jwt.decode(
        frag["id_token"],
        options={"verify_signature": False, "verify_exp": False},
    )
    assert int(payload["exp"]) - int(payload["iat"]) == 90


@pytest.mark.asyncio
async def test_code_id_token_rs256_pem_kid() -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        jwt_algorithm="HS256",
        oidc_issuer="https://as.example",
        oidc_id_token_signing_pem=pem,
        oidc_id_token_signing_kid="rsa-unit-kid",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(_base_authorize_req())
    from urllib.parse import parse_qsl, urlparse

    frag = dict(parse_qsl(urlparse(out["redirect_uri"]).fragment))
    tok = frag["id_token"]
    unverified = jwt.get_unverified_header(tok)
    assert unverified.get("alg") == "RS256"
    assert unverified.get("kid") == "rsa-unit-kid"
    payload = jwt.decode(
        tok,
        private_key.public_key(),
        algorithms=["RS256"],
        audience="test",
        issuer="https://as.example",
    )
    assert payload["sub"] == "user-42"
    assert payload["c_hash"] == oidc_left_half_sha256_b64url(frag["code"])


def test_resolve_pem_without_kid_or_jwks_raises() -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    cfg = XWAuthConfig(
        jwt_secret="s",
        oidc_id_token_signing_pem=pem,
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    with pytest.raises(XWConfigError):
        resolve_id_token_signing(cfg)


@pytest.mark.asyncio
async def test_form_post_returns_fields() -> None:
    cfg = XWAuthConfig(
        jwt_secret="unit-test-secret",
        oidc_issuer="https://as.example",
        registered_clients=DEFAULT_TEST_CLIENTS,
    )
    auth = XWAuth(config=cfg)
    out = await auth.authorize(_base_authorize_req(response_mode="form_post"))
    assert out.get("response_mode") == "form_post"
    assert out["redirect_uri"] == "https://example.com/cb"
    fields = out["form_fields"]
    assert "id_token" in fields and "code" in fields and fields["state"] == "st-1"
