#!/usr/bin/env python3
"""
RFC 6749 §2.3.1: HTTP Basic may carry client_id and client_secret for the token endpoint.
"""

from __future__ import annotations

import base64

from exonware.xwauth.handlers._common import merge_token_endpoint_client_auth


class _Hdr:
    def __init__(self, mapping: dict[str, str]) -> None:
        self._d = {k.lower(): v for k, v in mapping.items()}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._d.get(key.lower(), default)


class _FakeRequest:
    __slots__ = ("headers",)

    def __init__(self, authorization: str | None) -> None:
        h: dict[str, str] = {}
        if authorization is not None:
            h["authorization"] = authorization
        self.headers = _Hdr(h)


def test_merge_basic_fills_missing_client_id_and_secret() -> None:
    req: dict[str, str] = {"grant_type": "client_credentials"}
    enc = base64.b64encode(b"myid:mysecret").decode("ascii")
    merge_token_endpoint_client_auth(_FakeRequest(f"Basic {enc}"), req)
    assert req["client_id"] == "myid"
    assert req["client_secret"] == "mysecret"


def test_merge_does_not_override_non_empty_body_credentials() -> None:
    enc = base64.b64encode(b"other:othersec").decode("ascii")
    req: dict[str, str] = {
        "grant_type": "client_credentials",
        "client_id": "bodyid",
        "client_secret": "bodysec",
    }
    merge_token_endpoint_client_auth(_FakeRequest(f"Basic {enc}"), req)
    assert req["client_id"] == "bodyid"
    assert req["client_secret"] == "bodysec"


def test_merge_fills_secret_when_body_secret_empty_string() -> None:
    enc = base64.b64encode(b"bodyid:frombasic").decode("ascii")
    req: dict[str, str] = {
        "grant_type": "client_credentials",
        "client_id": "bodyid",
        "client_secret": "",
    }
    merge_token_endpoint_client_auth(_FakeRequest(f"Basic {enc}"), req)
    assert req["client_id"] == "bodyid"
    assert req["client_secret"] == "frombasic"


def test_merge_without_basic_leaves_request_unchanged() -> None:
    req: dict[str, str] = {"grant_type": "client_credentials"}
    merge_token_endpoint_client_auth(_FakeRequest(None), req)
    assert "client_id" not in req
    assert "client_secret" not in req
