#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.email_magic_link_ops (REF_25 #16)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import (
    EMAIL_MAGIC_LINK_OPS_SCHEMA_VERSION,
    magic_link_email_ops_checklist,
    recommended_magic_link_ttl_seconds_bounds,
)
from exonware.xwauth.ops.email_magic_link_ops import magic_link_email_ops_checklist as raw_checklist


@pytest.mark.xwauth_unit
def test_schema_version_stable() -> None:
    assert EMAIL_MAGIC_LINK_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_ttl_bounds_ordered() -> None:
    lo, hi = recommended_magic_link_ttl_seconds_bounds()
    assert lo < hi
    assert lo >= 60


@pytest.mark.xwauth_unit
def test_checklist_structure() -> None:
    doc = magic_link_email_ops_checklist()
    assert doc["schema_version"] == EMAIL_MAGIC_LINK_OPS_SCHEMA_VERSION
    assert doc["kind"] == "magic_link_email_ops"
    bounds = doc["recommended_magic_link_ttl_bounds_seconds"]
    assert bounds["min"] == 60
    assert bounds["max"] == 86_400
    sections = doc["sections"]
    ids = {s["id"] for s in sections}
    assert ids == {
        "dns_authentication",
        "sending_infrastructure",
        "magic_link_security",
        "content_and_ux",
    }
    for s in sections:
        assert isinstance(s["title"], str) and s["title"]
        assert isinstance(s["items"], list) and len(s["items"]) >= 2


@pytest.mark.xwauth_unit
def test_package_and_module_export_same_payload() -> None:
    assert raw_checklist() == magic_link_email_ops_checklist()
