#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.research_program (REF_25 #20)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import (
    RESEARCH_PROGRAM_SCHEMA_VERSION,
    fuzzing_recommendations,
    interop_bounty_policy,
)
from exonware.xwauth.ops.research_program import fuzzing_recommendations as raw_fuzz
from exonware.xwauth.ops.research_program import interop_bounty_policy as raw_bounty


@pytest.mark.xwauth_unit
def test_research_schema_version() -> None:
    assert RESEARCH_PROGRAM_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_interop_bounty_policy_shape() -> None:
    p = interop_bounty_policy()
    assert p["schema_version"] == RESEARCH_PROGRAM_SCHEMA_VERSION
    assert p["kind"] == "interop_bounty_policy"
    assert p["status"] == "draft"
    assert p["reporting"]["address"] == "connect@exonware.com"
    assert len(p["in_scope"]) >= 3
    assert len(p["out_of_scope"]) >= 3
    assert "reward_note" in p


@pytest.mark.xwauth_unit
def test_fuzzing_recommendations_shape() -> None:
    f = fuzzing_recommendations()
    assert f["schema_version"] == RESEARCH_PROGRAM_SCHEMA_VERSION
    assert f["kind"] == "fuzzing_recommendations"
    assert f["status"] == "draft"
    assert len(f["targets"]) >= 3
    assert "tooling_note" in f


@pytest.mark.xwauth_unit
def test_package_matches_module_exports() -> None:
    assert raw_bounty() == interop_bounty_policy()
    assert raw_fuzz() == fuzzing_recommendations()
