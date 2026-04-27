#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.b2b_delegated_admin (REF_25 #15)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import B2B_DELEGATED_ADMIN_OPS_SCHEMA_VERSION, b2b_delegated_admin_checklist
from exonware.xwauth.identity.ops.b2b_delegated_admin import b2b_delegated_admin_checklist as raw


@pytest.mark.xwauth_unit
def test_b2b_schema() -> None:
    assert B2B_DELEGATED_ADMIN_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_b2b_checklist_sections() -> None:
    doc = b2b_delegated_admin_checklist()
    assert doc["kind"] == "b2b_delegated_admin"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "org_model",
        "delegated_roles",
        "invites",
        "sso_per_org",
        "audit",
    }
    for s in doc["sections"]:
        assert len(s["items"]) >= 2


@pytest.mark.xwauth_unit
def test_b2b_export_parity() -> None:
    assert raw() == b2b_delegated_admin_checklist()
