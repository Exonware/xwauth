#!/usr/bin/env python3
"""Mapping DSL v1 and tenant IdP registry unit tests."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.federation import (
    TenantIdpRecord,
    TenantScopedIdpRegistry,
    apply_claim_mapping_v1,
)


@pytest.mark.xwauth_unit
def test_apply_claim_mapping_v1_selects_first_hit() -> None:
    claims = {"mail": "a@b.com", "sub": "x"}
    rules = [{"target": "email", "from": ["email", "mail"]}]
    out, trace = apply_claim_mapping_v1(claims, rules)
    assert out["email"] == "a@b.com"
    assert trace["rules_applied"] == 1
    assert trace["steps"][0]["selected_from"] == "mail"


@pytest.mark.xwauth_unit
def test_apply_claim_mapping_v1_nested_path() -> None:
    claims = {"profile": {"upn": "u@corp.com"}}
    rules = [{"target": "email", "from": ["profile.upn"]}]
    out, _trace = apply_claim_mapping_v1(claims, rules)
    assert out["email"] == "u@corp.com"


@pytest.mark.xwauth_unit
def test_tenant_idp_registry_health_unknown() -> None:
    auth = XWAuth(
        config=XWAuthConfig(jwt_secret="s", allow_mock_storage_fallback=True)
    )
    reg = TenantScopedIdpRegistry(auth)
    snap = reg.health_snapshot("t1", "missing")
    assert "idp_not_registered" in snap.warnings


@pytest.mark.xwauth_unit
def test_tenant_idp_registry_dry_run_metadata() -> None:
    auth = XWAuth(
        config=XWAuthConfig(jwt_secret="s", allow_mock_storage_fallback=True)
    )
    reg = TenantScopedIdpRegistry(auth)
    xml = """<?xml version="1.0"?>
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://idp.example.com">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor use="signing">
      <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
        <ds:X509Data><ds:X509Certificate>QUJD</ds:X509Certificate></ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
  </IDPSSODescriptor>
</EntityDescriptor>
"""
    snap = reg.validate_metadata_dry_run(xml, source_url="https://idp.example/metadata")
    assert snap.entity_id == "https://idp.example.com"


@pytest.mark.xwauth_unit
def test_tenant_idp_registry_domain_resolve() -> None:
    auth = XWAuth(
        config=XWAuthConfig(jwt_secret="s", allow_mock_storage_fallback=True)
    )
    reg = TenantScopedIdpRegistry(auth)
    rec = TenantIdpRecord(
        tenant_id="acme",
        idp_key="okta1",
        protocol="saml",
        domains=("users.acme.test",),
    )
    reg.register(rec)
    assert reg.resolve_domain("acme", "users.acme.test") == rec
    assert reg.resolve_domain("other", "users.acme.test") is None
