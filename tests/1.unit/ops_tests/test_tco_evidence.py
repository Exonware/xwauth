#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.tco_evidence (REF_25 #19)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.bench import run_microbench_suite
from exonware.xwauth.identity.ops import (
    TCO_EVIDENCE_SCHEMA_VERSION,
    tco_benchmark_publish_checklist,
    validate_microbench_output,
)
from exonware.xwauth.identity.ops.tco_evidence import tco_benchmark_publish_checklist as raw_chk


@pytest.mark.xwauth_unit
def test_tco_evidence_schema() -> None:
    assert TCO_EVIDENCE_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_validate_microbench_accepts_real_run() -> None:
    out = run_microbench_suite(iterations=4)
    validate_microbench_output(out)


@pytest.mark.xwauth_unit
def test_validate_microbench_rejects_missing() -> None:
    with pytest.raises(ValueError, match="missing"):
        validate_microbench_output({})
    with pytest.raises(ValueError, match="cases"):
        validate_microbench_output({"iterations": 1, "jwt_generate_seconds": 0, "jwt_validate_seconds": 0, "oidc_at_hash_seconds": 0, "cases": []})


@pytest.mark.xwauth_unit
def test_validate_microbench_rejects_bad_case_entry() -> None:
    bad = {
        "iterations": 1,
        "jwt_generate_seconds": 0.0,
        "jwt_validate_seconds": 0.0,
        "oidc_at_hash_seconds": 0.0,
        "cases": {
            "jwt_generate": {},
            "jwt_validate": {"total_seconds": 0, "per_op_seconds": 0},
            "oidc_at_hash": {"total_seconds": 0, "per_op_seconds": 0},
        },
    }
    with pytest.raises(ValueError, match="total_seconds"):
        validate_microbench_output(bad)


@pytest.mark.xwauth_unit
def test_tco_publish_checklist_shape() -> None:
    doc = tco_benchmark_publish_checklist()
    assert doc["kind"] == "tco_benchmark_publish"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {"environment", "xwauth_microbench", "xwauth_connector_api_http", "tco_narrative"}


@pytest.mark.xwauth_unit
def test_tco_publish_export_parity() -> None:
    assert raw_chk() == tco_benchmark_publish_checklist()
