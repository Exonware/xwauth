#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.pen_test_engagement (REF_25 #1)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import PENTEST_ENGAGEMENT_SCHEMA_VERSION, pen_test_engagement_checklist
from exonware.xwauth.ops.pen_test_engagement import pen_test_engagement_checklist as raw


@pytest.mark.xwauth_unit
def test_pentest_schema_version() -> None:
    assert PENTEST_ENGAGEMENT_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_pentest_checklist_shape() -> None:
    doc = pen_test_engagement_checklist()
    assert doc["schema_version"] == PENTEST_ENGAGEMENT_SCHEMA_VERSION
    assert doc["kind"] == "pen_test_engagement"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "scope",
        "environment",
        "rules_of_engagement",
        "deliverables",
        "executive_summary_publication",
        "remediation_follow_up",
    }


@pytest.mark.xwauth_unit
def test_pentest_export_parity() -> None:
    assert raw() == pen_test_engagement_checklist()
