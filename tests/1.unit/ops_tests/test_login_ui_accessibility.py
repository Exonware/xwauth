#!/usr/bin/env python3
"""Tests for exonware.xwauth.ops.login_ui_accessibility (REF_25 #10)."""

from __future__ import annotations

import pytest

from exonware.xwauth.ops import LOGIN_UI_A11Y_SCHEMA_VERSION, login_ui_accessibility_checklist
from exonware.xwauth.ops.login_ui_accessibility import login_ui_accessibility_checklist as raw


@pytest.mark.xwauth_unit
def test_login_ui_a11y_schema() -> None:
    assert LOGIN_UI_A11Y_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_login_ui_a11y_sections() -> None:
    doc = login_ui_accessibility_checklist()
    assert doc["kind"] == "login_ui_accessibility"
    assert doc["wcag_target"] == "2.2 AA"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "perceivable",
        "operable",
        "understandable",
        "robust",
        "vpat_style",
    }


@pytest.mark.xwauth_unit
def test_login_ui_a11y_export_parity() -> None:
    assert raw() == login_ui_accessibility_checklist()
