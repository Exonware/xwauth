#!/usr/bin/env python3
"""
# exonware/xwauth.connector/tests/1.unit/interop_lab_tests/test_interop_fixture_manifest.py
Validate interop_lab manifest and artifact paths (GUIDE_12 / ROADMAP #8).
"""

from __future__ import annotations

from pathlib import Path

from exonware.xwsystem.io.serialization.formats.text import json as xw_json

_MANIFEST = Path(__file__).resolve().parents[2] / "fixtures" / "interop_lab" / "manifest.json"


def test_interop_manifest_schema_and_artifacts() -> None:
    assert _MANIFEST.is_file(), f"Missing manifest: {_MANIFEST}"
    data = xw_json.loads(_MANIFEST.read_text(encoding="utf-8"))
    assert data.get("schema_version") == "1.0"
    contracts = data.get("contracts")
    assert isinstance(contracts, list)
    base = _MANIFEST.parent
    for i, entry in enumerate(contracts):
        assert isinstance(entry, dict), f"contracts[{i}] must be an object"
        for key in ("id", "protocol", "idp", "artifact"):
            assert key in entry, f"contracts[{i}] missing {key!r}"
            assert isinstance(entry[key], str) and entry[key].strip(), f"contracts[{i}].{key} non-empty string"
        rel = entry["artifact"]
        path = (base / rel).resolve()
        assert path.is_file(), f"contracts[{i}] artifact not found: {rel}"


def _load_contract_artifact(base: Path, rel: str) -> dict:
    path = (base / rel).resolve()
    return xw_json.loads(path.read_text(encoding="utf-8"))


def test_redacted_oidc_token_fixture_shape() -> None:
    """Regression on envelope + RFC 6749-style body (GUIDE_12 sample)."""
    base = _MANIFEST.parent
    data = _load_contract_artifact(base, "samples/oidc_token_response.redacted.json")
    meta = data.get("_interop_lab")
    assert isinstance(meta, dict)
    assert meta.get("id") == "oidc-token-response-shape-v1"
    assert meta.get("protocol") == "oidc"

    body = data.get("recorded_response_body")
    assert isinstance(body, dict)
    assert body.get("token_type") == "Bearer"
    assert isinstance(body.get("expires_in"), int) and body["expires_in"] > 0

    for key in ("access_token", "refresh_token", "id_token"):
        val = body.get(key)
        assert isinstance(val, str), key
        assert "REDACTED" in val, f"{key} must be redacted, got non-placeholder value"

    assert isinstance(body.get("scope"), str) and body["scope"].strip()


def test_redacted_scim_users_list_fixture_shape() -> None:
    """ListResponse envelope + Resources[] User shape (GUIDE_12 / GUIDE_11)."""
    from exonware.xwauth.identity.scim.models import SCIM_LIST_RESPONSE_SCHEMA, SCIM_USER_SCHEMA
    base = _MANIFEST.parent
    data = _load_contract_artifact(base, "samples/scim_users_list.redacted.json")
    meta = data.get("_interop_lab")
    assert isinstance(meta, dict)
    assert meta.get("id") == "scim-users-list-shape-v1"
    assert meta.get("protocol") == "scim"

    body = data.get("recorded_response_body")
    assert isinstance(body, dict)
    assert body.get("schemas") == [SCIM_LIST_RESPONSE_SCHEMA]
    assert isinstance(body.get("totalResults"), int)
    assert isinstance(body.get("startIndex"), int) and body["startIndex"] >= 1
    assert isinstance(body.get("itemsPerPage"), int) and body["itemsPerPage"] >= 0

    resources = body.get("Resources")
    assert isinstance(resources, list) and len(resources) >= 1
    user = resources[0]
    assert isinstance(user, dict)
    assert SCIM_USER_SCHEMA in user.get("schemas", [])
    assert "REDACTED" in str(user.get("id", ""))
    assert "REDACTED" in str(user.get("userName", ""))


def test_redacted_saml_idp_metadata_fixture_shape() -> None:
    """Minimal SAML 2.0 metadata XML markers (no XML parser required)."""
    base = _MANIFEST.parent
    path = (base / "samples" / "saml_idp_metadata.redacted.xml").resolve()
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "EntityDescriptor" in text
    assert "urn:oasis:names:tc:SAML:2.0:metadata" in text
    assert "REDACTED" in text
    assert "entityID=" in text and "REDACTED" in text.split("entityID=", 1)[1][:80]
    assert "X509Certificate" in text
    assert "SingleSignOnService" in text
    assert "https://REDACTED." in text
