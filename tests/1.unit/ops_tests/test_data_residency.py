#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.data_residency (REF_25 #12)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import DATA_RESIDENCY_OPS_SCHEMA_VERSION, data_residency_checklist
from exonware.xwauth.ops.data_residency import data_residency_checklist as raw


@pytest.mark.xwauth_unit
def test_data_residency_schema() -> None:
    assert DATA_RESIDENCY_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_data_residency_sections() -> None:
    doc = data_residency_checklist()
    assert doc["kind"] == "data_residency"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "data_inventory",
        "storage_and_backups",
        "federation_and_egress",
        "observability",
        "tenant_isolation",
    }
    for s in doc["sections"]:
        assert len(s["items"]) >= 2


@pytest.mark.xwauth_unit
def test_data_residency_export_parity() -> None:
    assert raw() == data_residency_checklist()
