#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.abuse_resistance (REF_25 #13)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import (
    ABUSE_RESISTANCE_OPS_SCHEMA_VERSION,
    abuse_resistance_checklist,
    exponential_backoff_delay_ms,
)
from exonware.xwauth.identity.ops.abuse_resistance import abuse_resistance_checklist as raw


@pytest.mark.xwauth_unit
def test_abuse_schema() -> None:
    assert ABUSE_RESISTANCE_OPS_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_exponential_backoff_monotonic_until_cap() -> None:
    assert exponential_backoff_delay_ms(0, base_ms=100, cap_ms=10_000, multiplier=2.0) == 100
    assert exponential_backoff_delay_ms(1, base_ms=100, cap_ms=10_000, multiplier=2.0) == 200
    assert exponential_backoff_delay_ms(2, base_ms=100, cap_ms=10_000, multiplier=2.0) == 400
    assert exponential_backoff_delay_ms(20, base_ms=100, cap_ms=500, multiplier=2.0) == 500


@pytest.mark.xwauth_unit
def test_exponential_backoff_invalid() -> None:
    with pytest.raises(ValueError, match="attempt"):
        exponential_backoff_delay_ms(-1)
    with pytest.raises(ValueError, match="base_ms"):
        exponential_backoff_delay_ms(0, base_ms=-1)
    with pytest.raises(ValueError, match="multiplier"):
        exponential_backoff_delay_ms(0, multiplier=0.5)


@pytest.mark.xwauth_unit
def test_abuse_checklist_sections() -> None:
    doc = abuse_resistance_checklist()
    assert doc["kind"] == "abuse_resistance"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "credential_stuffing",
        "magic_link_and_otp",
        "registration_and_clients",
        "edge_and_signals",
        "observability",
    }


@pytest.mark.xwauth_unit
def test_abuse_export_parity() -> None:
    assert raw() == abuse_resistance_checklist()
