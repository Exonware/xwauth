#!/usr/bin/env python3
"""
RFC 8414 (OAuth AS metadata) and OIDC Discovery 1.0 field contracts for discovery builders.
Pure unit tests — no HTTP stack.
"""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.oauth_http.discovery import (
    oauth_authorization_server_metadata,
    oauth_protected_resource_metadata,
    openid_configuration,
)
from exonware.xwauth.identity.tokens.oidc_id_token_signing import (
    infer_id_token_signing_algorithms_for_discovery,
)


def _under_issuer(url: str, issuer: str) -> bool:
    base = issuer.rstrip("/")
    return url.startswith(base + "/") or url == base


@pytest.mark.parametrize("allow_pw", [True, False])
def test_oauth_authorization_server_metadata_core_rfc8414(allow_pw: bool) -> None:
    issuer = "https://as.example.com"
    meta = oauth_authorization_server_metadata(
        issuer,
        allow_password_grant=allow_pw,
    )
    assert meta["issuer"] == issuer
    assert _under_issuer(meta["authorization_endpoint"], issuer)
    assert _under_issuer(meta["token_endpoint"], issuer)
    assert _under_issuer(meta["jwks_uri"], issuer)
    assert meta["response_types_supported"] == [
        "code",
        "code id_token",
        "code token",
        "code id_token token",
    ]
    assert "S256" in meta.get("code_challenge_methods_supported", [])
    assert meta.get("pushed_authorization_request_endpoint", "").endswith("/par")
    gts = meta["grant_types_supported"]
    if allow_pw:
        assert "password" in gts
    else:
        assert "password" not in gts


def test_oauth_metadata_normalizes_trailing_slash_issuer() -> None:
    meta = oauth_authorization_server_metadata(
        "https://as.example.com/",
        allow_password_grant=False,
    )
    assert meta["issuer"] == "https://as.example.com"
    assert meta["authorization_endpoint"].startswith("https://as.example.com/")


def test_oauth_authorization_server_metadata_fapi_flags() -> None:
    meta = oauth_authorization_server_metadata(
        "https://as.example.com",
        fapi20_compliant=True,
        fapi20_require_par=True,
        fapi20_require_jar=True,
        fapi20_require_dpop_or_mtls=True,
    )
    assert meta.get("fapi_security_profile") == "fapi-2.0"
    assert meta.get("require_pushed_authorization_requests") is True
    assert meta.get("require_jwt_secured_authorization_request") is True
    assert meta.get("require_dpop_or_mtls") is True
    assert meta.get("dpop_signing_alg_values_supported")
    assert meta.get("tls_client_certificate_bound_access_tokens") is True


def test_oauth_authorization_server_metadata_oauth21_response_types() -> None:
    meta = oauth_authorization_server_metadata(
        "https://as.example.com",
        oauth21_compliant=True,
        allow_password_grant=False,
    )
    assert meta["response_types_supported"] == ["code", "code id_token"]


def test_openid_configuration_oidc_discovery_required_fields() -> None:
    issuer = "https://as.example.com"
    doc = openid_configuration(issuer)
    # OpenID Connect Discovery 1.0 — registration response required parameters
    assert doc["issuer"] == issuer
    assert _under_issuer(doc["authorization_endpoint"], issuer)
    assert _under_issuer(doc["token_endpoint"], issuer)
    assert _under_issuer(doc["jwks_uri"], issuer)
    assert _under_issuer(doc["userinfo_endpoint"], issuer)
    assert doc.get("response_types_supported")
    assert doc.get("subject_types_supported")
    assert doc.get("id_token_signing_alg_values_supported")
    assert "openid" in doc.get("scopes_supported", [])
    assert doc.get("pushed_authorization_request_endpoint", "").endswith("/par")
    assert "S256" in doc.get("code_challenge_methods_supported", [])


def test_openid_configuration_fapi_par_oidc_registry() -> None:
    doc = openid_configuration(
        "https://as.example.com",
        fapi20_compliant=True,
        fapi20_require_par=True,
        fapi20_require_jar=True,
        fapi20_require_dpop_or_mtls=True,
    )
    assert doc.get("require_pushed_authorization_requests") is True
    assert doc.get("fapi_security_profile") == "fapi-2.0"
    assert doc.get("require_jwt_secured_authorization_request") is True
    assert doc.get("require_dpop_or_mtls") is True


def test_infer_id_token_signing_algorithms_symmetric_config() -> None:
    cfg = XWAuthConfig(jwt_secret="x", jwt_algorithm="HS256", allow_mock_storage_fallback=True)
    assert infer_id_token_signing_algorithms_for_discovery(cfg) == ["HS256"]


def test_openid_configuration_password_grant_toggle() -> None:
    with_pw = openid_configuration("https://as.example.com", allow_password_grant=True)
    without_pw = openid_configuration("https://as.example.com", allow_password_grant=False)
    assert "password" in with_pw["grant_types_supported"]
    assert "password" not in without_pw["grant_types_supported"]


def test_oauth_protected_resource_metadata_rfc9728_shape() -> None:
    meta = oauth_protected_resource_metadata(
        resource="https://api.example.com/",
        authorization_servers=["https://as.example.com"],
        issuer="https://as.example.com",
    )
    assert meta["resource"] == "https://api.example.com/"
    assert meta["authorization_servers"] == ["https://as.example.com"]
    assert meta.get("bearer_methods_supported") == ["header"]
    assert "jwks_uri" in meta
    assert meta["jwks_uri"].startswith("https://as.example.com")
