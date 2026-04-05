#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.multi_region_auth (REF_25 #18)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import MULTI_REGION_AUTH_OPS_SCHEMA_VERSION, multi_region_auth_checklist
from exonware.xwauth.ops.multi_region_auth import multi_region_auth_checklist as raw


@pytest.mark.xwauth_unit
def test_multi_region_schema() -> None:
    assert MULTI_REGION_AUTH_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_multi_region_sections() -> None:
    doc = multi_region_auth_checklist()
    assert doc["kind"] == "multi_region_auth"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "issuer_and_discovery",
        "jwks_rotation",
        "token_validation",
        "revocation_and_sessions",
        "redis_and_webauthn",
        "testing",
    }
    for s in doc["sections"]:
        assert len(s["items"]) >= 2


@pytest.mark.xwauth_unit
def test_multi_region_export_parity() -> None:
    assert raw() == multi_region_auth_checklist()
