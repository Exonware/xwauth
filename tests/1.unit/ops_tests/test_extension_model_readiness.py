#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.extension_model_readiness (REF_25 #8)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import (
    EXTENSION_MODEL_READINESS_SCHEMA_VERSION,
    extension_model_readiness_checklist,
)
from exonware.xwauth.ops.extension_model_readiness import extension_model_readiness_checklist as raw


@pytest.mark.xwauth_unit
def test_extension_model_schema_version() -> None:
    assert EXTENSION_MODEL_READINESS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_extension_model_checklist_shape() -> None:
    doc = extension_model_readiness_checklist()
    assert doc["schema_version"] == EXTENSION_MODEL_READINESS_SCHEMA_VERSION
    assert doc["kind"] == "extension_model_readiness"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "surface_choice",
        "versioning",
        "mfa_risk_stepup",
        "custom_claims",
        "security_boundary",
    }


@pytest.mark.xwauth_unit
def test_extension_model_export_parity() -> None:
    assert raw() == extension_model_readiness_checklist()
