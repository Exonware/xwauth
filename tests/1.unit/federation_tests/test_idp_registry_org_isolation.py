#!/usr/bin/env python3
"""Org-scoped IdP registry: no cross-org domain resolution."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.federation.idp_registry import TenantIdpRecord, TenantScopedIdpRegistry, idp_isolation_namespace


@pytest.mark.xwauth_unit
def test_idp_isolation_namespace_prefers_org() -> None:
    r = TenantIdpRecord(
        tenant_id="t1",
        idp_key="k1",
        protocol="saml",
        org_id="org-a",
    )
    assert idp_isolation_namespace(r) == "org:org-a"


@pytest.mark.xwauth_unit
def test_resolve_domain_for_org_does_not_leak_across_orgs() -> None:
    auth = XWAuth(
        jwt_secret="idp-registry-test-secret",
        allow_mock_storage_fallback=True,
    )
    reg = TenantScopedIdpRegistry(auth, persist=False)
    reg.register(
        TenantIdpRecord(
            tenant_id="t1",
            idp_key="corp",
            protocol="saml",
            org_id="org-1",
            entity_id="https://idp1.example.com",
            metadata_url="https://idp1.example.com/sso",
            domains=("org1.example.com",),
        )
    )
    assert reg.resolve_domain_for_org("org-1", "org1.example.com") is not None
    assert reg.resolve_domain_for_org("org-2", "org1.example.com") is None


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_discover_sso_org_scoped_without_legacy_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XWAUTH_SSO_DISCOVERY_ORG_LEGACY_FALLBACK", raising=False)
    auth = XWAuth(
        jwt_secret="saml-discovery-test-secret",
        allow_mock_storage_fallback=True,
    )
    auth.tenant_idp_registry.register(
        TenantIdpRecord(
            tenant_id="t",
            idp_key="okta",
            protocol="saml",
            org_id="acme",
            metadata_url="https://acme.idp/login",
            entity_id="urn:acme:idp",
            domains=("acme.com",),
        )
    )
    from exonware.xwauth.identity.core.saml import SAMLManager
    mgr = SAMLManager(auth)
    found = await mgr.discover_sso_provider("u@acme.com", org_id="acme")
    assert found is not None
    assert found.get("idp_url") == "https://acme.idp/login"
    missing = await mgr.discover_sso_provider("u@acme.com", org_id="other-org")
    assert missing is None
