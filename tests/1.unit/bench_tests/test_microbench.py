#!/usr/bin/env python3
"""Unit tests for exonware.xwauth.bench.microbench (REF_25 #6)."""

from __future__ import annotations

import pytest

from exonware.xwauth.bench import run_microbench_suite


def test_run_microbench_suite_structure():
    out = run_microbench_suite(iterations=20)
    assert out["iterations"] == 20
    assert "jwt_generate_seconds" in out
    assert "jwt_validate_seconds" in out
    assert "oidc_at_hash_seconds" in out
    cases = out["cases"]
    assert set(cases.keys()) == {"jwt_generate", "jwt_validate", "oidc_at_hash"}
    for name in cases:
        assert cases[name]["total_seconds"] >= 0.0
        assert cases[name]["per_op_seconds"] >= 0.0


def test_run_microbench_suite_round_trip_uses_validate():
    """One generate + validate ensures manager is consistent (not timing assertion)."""
    out = run_microbench_suite(iterations=2)
    assert out["cases"]["jwt_validate"]["total_seconds"] > 0.0


def test_run_microbench_suite_invalid_iterations():
    with pytest.raises(ValueError, match="iterations"):
        run_microbench_suite(iterations=0)
    with pytest.raises(ValueError, match="iterations"):
        run_microbench_suite(iterations=-1)
