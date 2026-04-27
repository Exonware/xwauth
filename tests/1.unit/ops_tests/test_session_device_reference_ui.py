#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.session_device_reference_ui (REF_25 #14)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import (
    SESSION_DEVICE_REFERENCE_UI_SCHEMA_VERSION,
    session_device_reference_ui_checklist,
)
from exonware.xwauth.identity.ops.session_device_reference_ui import session_device_reference_ui_checklist as raw


@pytest.mark.xwauth_unit
def test_session_device_ui_schema_version() -> None:
    assert SESSION_DEVICE_REFERENCE_UI_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_session_device_ui_checklist_shape() -> None:
    doc = session_device_reference_ui_checklist()
    assert doc["schema_version"] == SESSION_DEVICE_REFERENCE_UI_SCHEMA_VERSION
    assert doc["kind"] == "session_device_reference_ui"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "surfaces",
        "revocation",
        "security_copy",
        "api_alignment",
        "privacy",
    }


@pytest.mark.xwauth_unit
def test_session_device_ui_export_parity() -> None:
    assert raw() == session_device_reference_ui_checklist()
