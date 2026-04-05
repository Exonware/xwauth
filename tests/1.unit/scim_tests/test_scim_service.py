#!/usr/bin/env python3
"""
Unit tests for SCIM service foundation.
"""

from __future__ import annotations

import pytest

from exonware.xwauth.scim.models import SCIM_USER_SCHEMA
from exonware.xwauth.scim.patch import ScimPatchOperation
from exonware.xwauth.scim.service import ScimService


@pytest.mark.xwauth_unit
def test_scim_service_create_patch_and_list_response() -> None:
    service = ScimService(resource_type="User", default_schema=SCIM_USER_SCHEMA)
    created = service.create(
        resource_id="u-1",
        attributes={"userName": "alice", "displayName": "Alice Example"},
        external_id="ext-1",
    )
    assert created.meta is not None
    assert created.meta.version.startswith('W/"')

    updated = service.patch(
        "u-1",
        [
            ScimPatchOperation(op="replace", path="displayName", value="Alice Updated"),
            ScimPatchOperation(op="add", path="active", value=True),
        ],
    )
    assert updated.attributes["displayName"] == "Alice Updated"
    assert updated.attributes["active"] is True

    response = service.list_response(filter_expression='userName eq "alice"', start_index=1, count=10)
    assert response["totalResults"] == 1
    assert response["itemsPerPage"] == 1
    assert response["Resources"][0]["id"] == "u-1"


@pytest.mark.xwauth_unit
def test_scim_service_delete_returns_false_when_missing() -> None:
    service = ScimService(resource_type="User", default_schema=SCIM_USER_SCHEMA)
    assert service.delete("missing") is False

