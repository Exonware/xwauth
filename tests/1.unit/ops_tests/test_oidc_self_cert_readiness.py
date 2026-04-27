#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.oidc_self_cert_readiness (REF_25 #2)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import (
    OIDC_SELF_CERT_READINESS_SCHEMA_VERSION,
    oidc_self_cert_readiness_checklist,
)
from exonware.xwauth.identity.ops.oidc_self_cert_readiness import oidc_self_cert_readiness_checklist as raw


@pytest.mark.xwauth_unit
def test_oidc_self_cert_schema_version() -> None:
    assert OIDC_SELF_CERT_READINESS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_oidc_self_cert_checklist_shape() -> None:
    doc = oidc_self_cert_readiness_checklist()
    assert doc["schema_version"] == OIDC_SELF_CERT_READINESS_SCHEMA_VERSION
    assert doc["kind"] == "oidc_self_cert_readiness"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "conformance_baseline",
        "certification_suites",
        "foundation_submission",
        "listing_and_marketing",
        "ongoing_maintenance",
    }


@pytest.mark.xwauth_unit
def test_oidc_self_cert_export_parity() -> None:
    assert raw() == oidc_self_cert_readiness_checklist()
