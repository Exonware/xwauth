#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.airgap_deployment (REF_25 #17)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import AIRGAP_OPS_SCHEMA_VERSION, airgap_deployment_checklist
from exonware.xwauth.identity.ops.airgap_deployment import airgap_deployment_checklist as raw_checklist


@pytest.mark.xwauth_unit
def test_airgap_schema_version() -> None:
    assert AIRGAP_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_airgap_checklist_structure() -> None:
    doc = airgap_deployment_checklist()
    assert doc["schema_version"] == AIRGAP_OPS_SCHEMA_VERSION
    assert doc["kind"] == "airgap_deployment"
    sections = doc["sections"]
    ids = {s["id"] for s in sections}
    assert ids == {
        "python_artifacts",
        "federation_and_jwks",
        "time_and_tokens",
        "tls_and_trust",
        "optional_extras",
        "validation",
    }
    for s in sections:
        assert s["title"]
        assert len(s["items"]) >= 2


@pytest.mark.xwauth_unit
def test_airgap_package_matches_module() -> None:
    assert raw_checklist() == airgap_deployment_checklist()
