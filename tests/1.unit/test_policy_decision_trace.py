#!/usr/bin/env python3
"""
Unit tests for explainable policy decision traces.
"""

from __future__ import annotations

import pytest

from exonware.xwsystem.security.contracts import AuthContext
from exonware.xwauth.identity.policy_decision import PolicyDecisionService


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_policy_decision_evaluate_keeps_legacy_storage_scope_behavior() -> None:
    service = PolicyDecisionService()
    context = AuthContext(subject_id="user-1", scopes=["storage:read"])
    allowed = await service.evaluate(context, resource="documents", action="read")
    assert allowed is True


@pytest.mark.xwauth_unit
def test_policy_decision_explain_returns_trace_with_reasons() -> None:
    service = PolicyDecisionService()
    context = AuthContext(subject_id="user-1", scopes=["documents:read"], claims={"org_id": "org-a"})
    decision = service.explain(context, resource="documents", action="read", org_id="org-a")
    assert decision.allowed is True
    assert decision.trace.decision_id
    assert "documents:read" in decision.trace.required_scopes
    assert decision.trace.matched_scopes == ["documents:read"]
    assert any("matched scopes:" in reason for reason in decision.trace.reasons)


@pytest.mark.xwauth_unit
def test_policy_decision_explain_enforces_org_scope_when_present() -> None:
    service = PolicyDecisionService()
    context = AuthContext(subject_id="user-1", scopes=["documents:read"], claims={"org_id": "org-a"})
    decision = service.explain(context, resource="documents", action="read", org_id="org-b")
    assert decision.allowed is False
    assert any("org scope mismatch" in reason for reason in decision.trace.reasons)

