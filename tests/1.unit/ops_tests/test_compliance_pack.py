#!/usr/bin/env python3
"""Tests for exonware.xwauth.connector.ops.compliance_pack (REF_25 #11)."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.ops import (
    COMPLIANCE_PACK_SCHEMA_VERSION,
    compliance_evidence_template,
    compliance_pack_checklist,
)
from exonware.xwauth.identity.ops.compliance_pack import compliance_evidence_template as raw_tpl
from exonware.xwauth.identity.ops.compliance_pack import compliance_pack_checklist as raw_chk


@pytest.mark.xwauth_unit
def test_compliance_schema() -> None:
    assert COMPLIANCE_PACK_SCHEMA_VERSION == 1


@pytest.mark.xwauth_unit
def test_compliance_checklist_sections() -> None:
    doc = compliance_pack_checklist()
    assert doc["kind"] == "compliance_pack_checklist"
    ids = {s["id"] for s in doc["sections"]}
    assert ids == {
        "records_and_ropa",
        "subprocessors",
        "retention",
        "dpa_annex",
        "data_subject_rights",
        "incidents",
    }


@pytest.mark.xwauth_unit
def test_evidence_template_fields() -> None:
    tpl = compliance_evidence_template()
    assert tpl["kind"] == "compliance_evidence_template"
    fields = tpl["fields"]
    assert "data_controller_legal_name" in fields
    assert fields["product_name"]
    assert all(isinstance(v, str) for v in fields.values())


@pytest.mark.xwauth_unit
def test_export_parity() -> None:
    assert raw_chk() == compliance_pack_checklist()
    assert raw_tpl() == compliance_evidence_template()
