#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.infra_as_code_tenants (REF_25 #3)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import INFRA_AS_CODE_TENANTS_SCHEMA_VERSION, infra_as_code_tenants_checklist
from exonware.xwauth.identity.ops.infra_as_code_tenants import infra_as_code_tenants_checklist as raw


@pytest.mark.xwauth_unit
def test_infra_as_code_schema_version() -> None:
    assert INFRA_AS_CODE_TENANTS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_infra_as_code_checklist_shape() -> None:
    doc = infra_as_code_tenants_checklist()
    assert doc["schema_version"] == INFRA_AS_CODE_TENANTS_SCHEMA_VERSION
    assert doc["kind"] == "infra_as_code_tenants"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "resource_model",
        "scopes_and_grants",
        "secrets_and_keys",
        "state_and_drift",
        "environments",
    }


@pytest.mark.xwauth_unit
def test_infra_as_code_export_parity() -> None:
    assert raw() == infra_as_code_tenants_checklist()
