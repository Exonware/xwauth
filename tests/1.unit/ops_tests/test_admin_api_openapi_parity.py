#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.admin_api_openapi_parity (REF_25 #7)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import (
    ADMIN_API_OPENAPI_PARITY_SCHEMA_VERSION,
    admin_api_openapi_parity_checklist,
)
from exonware.xwauth.ops.admin_api_openapi_parity import admin_api_openapi_parity_checklist as raw


@pytest.mark.xwauth_unit
def test_admin_api_openapi_schema_version() -> None:
    assert ADMIN_API_OPENAPI_PARITY_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_admin_api_openapi_checklist_shape() -> None:
    doc = admin_api_openapi_parity_checklist()
    assert doc["schema_version"] == ADMIN_API_OPENAPI_PARITY_SCHEMA_VERSION
    assert doc["kind"] == "admin_api_openapi_parity"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "inventory",
        "api_coverage",
        "openapi_fidelity",
        "authorization",
        "parity_gates",
    }


@pytest.mark.xwauth_unit
def test_admin_api_openapi_export_parity() -> None:
    assert raw() == admin_api_openapi_parity_checklist()
