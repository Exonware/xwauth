#!/usr/bin/env python3
"""Unit tests for PAR (RFC 9126) and authorize integration."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig, DEFAULT_TEST_CLIENTS
from exonware.xwauth.identity.core.oauth2 import OAuth2Server
from exonware.xwauth.identity.core.par import PARManager
from exonware.xwauth.identity.errors import XWInvalidRequestError, XWConfigError

pytestmark = pytest.mark.xwauth_unit


@pytest.fixture
def par_auth() -> XWAuth:
    return XWAuth(
        config=XWAuthConfig(
            jwt_secret="test-secret-key",
            registered_clients=DEFAULT_TEST_CLIENTS,
            require_state_in_authorize=False,
            allow_mock_storage_fallback=True,
        )
    )


@pytest.mark.asyncio
async def test_par_consume_single_use(par_auth: XWAuth) -> None:
    par = PARManager(par_auth)
    out = await par.push_request(
        {"response_type": "code", "client_id": "test", "redirect_uri": "https://example.com/cb"},
        "test",
    )
    uri = out["request_uri"]
    first = await par.consume_request(uri)
    assert first is not None
    params, cid = first
    assert cid == "test"
    assert params["response_type"] == "code"
    assert await par.consume_request(uri) is None


@pytest.mark.asyncio
async def test_fapi20_require_par_rejects_without_request_uri(par_auth: XWAuth) -> None:
    par_auth.config.fapi20_require_par = True
    oauth = OAuth2Server(par_auth)
    with pytest.raises(XWInvalidRequestError) as exc:
        await oauth.authorize(
            {
                "client_id": "test",
                "response_type": "code",
                "redirect_uri": "https://example.com/cb",
            }
        )
    text = (
        (exc.value.error_description or "")
        + " "
        + (exc.value.message or "")
    ).lower()
    assert "par" in text or "request_uri" in text


@pytest.mark.asyncio
async def test_par_strict_query_rejects_duplicate_params(par_auth: XWAuth) -> None:
    par = PARManager(par_auth)
    out = await par.push_request(
        {
            "response_type": "code",
            "client_id": "test",
            "redirect_uri": "https://example.com/cb",
            "scope": "openid",
        },
        "test",
    )
    oauth = OAuth2Server(par_auth)
    with pytest.raises(XWInvalidRequestError) as exc:
        await oauth.authorize(
            {
                "request_uri": out["request_uri"],
                "scope": "openid",
            }
        )
    assert "scope" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_par_client_id_mismatch(par_auth: XWAuth) -> None:
    par = PARManager(par_auth)
    out = await par.push_request(
        {"response_type": "code", "client_id": "test", "redirect_uri": "https://example.com/cb"},
        "test",
    )
    oauth = OAuth2Server(par_auth)
    with pytest.raises(XWInvalidRequestError) as exc:
        await oauth.authorize(
            {
                "request_uri": out["request_uri"],
                "client_id": "other",
            }
        )
    assert "client_id" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_par_second_authorize_fails_after_consume(par_auth: XWAuth) -> None:
    par = PARManager(par_auth)
    out = await par.push_request(
        {"response_type": "code", "client_id": "test", "redirect_uri": "https://example.com/cb"},
        "test",
    )
    uri = out["request_uri"]
    oauth = OAuth2Server(par_auth)
    try:
        await oauth.authorize({"request_uri": uri, "client_id": "test"})
    except Exception:
        pass
    with pytest.raises(XWInvalidRequestError) as exc:
        await oauth.authorize({"request_uri": uri, "client_id": "test"})
    assert exc.value.error_code == "invalid_request_uri"


def test_par_request_lifetime_validation() -> None:
    cfg = XWAuthConfig(jwt_secret="x", par_request_lifetime=5)
    with pytest.raises(XWConfigError):
        cfg.validate()
