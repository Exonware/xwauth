#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.kubernetes_operator_readiness (REF_25 #4)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import (
    K8S_OPERATOR_READINESS_SCHEMA_VERSION,
    kubernetes_operator_readiness_checklist,
)
from exonware.xwauth.identity.ops.kubernetes_operator_readiness import kubernetes_operator_readiness_checklist as raw


@pytest.mark.xwauth_unit
def test_k8s_operator_schema_version() -> None:
    assert K8S_OPERATOR_READINESS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_k8s_operator_checklist_shape() -> None:
    doc = kubernetes_operator_readiness_checklist()
    assert doc["schema_version"] == K8S_OPERATOR_READINESS_SCHEMA_VERSION
    assert doc["kind"] == "kubernetes_operator_readiness"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "value_over_helm",
        "crd_and_api",
        "rollout_and_health",
        "key_rotation",
        "observability",
    }


@pytest.mark.xwauth_unit
def test_k8s_operator_export_parity() -> None:
    assert raw() == kubernetes_operator_readiness_checklist()
