#!/usr/bin/env python3
"""
Unit tests for SCIM patch helpers.
"""

from __future__ import annotations

import pytest

from exonware.xwauth.scim.patch import (
    ScimPatchOperation,
    apply_scim_patch,
    enforce_scim_if_match,
)


@pytest.mark.xwauth_unit
def test_apply_scim_patch_supports_add_replace_remove() -> None:
    base = {"userName": "alice", "name": {"givenName": "Alice", "familyName": "Liddell"}}
    patched = apply_scim_patch(
        base,
        [
            ScimPatchOperation(op="replace", path="name.familyName", value="Example"),
            ScimPatchOperation(op="add", path="active", value=True),
            ScimPatchOperation(op="remove", path="userName"),
        ],
    )
    assert patched["name"]["familyName"] == "Example"
    assert patched["active"] is True
    assert "userName" not in patched


@pytest.mark.xwauth_unit
def test_apply_scim_patch_without_path_requires_object_value() -> None:
    with pytest.raises(ValueError):
        apply_scim_patch({"a": 1}, [ScimPatchOperation(op="add", value="bad")])


@pytest.mark.xwauth_unit
def test_apply_scim_patch_requires_non_empty_operations() -> None:
    with pytest.raises(ValueError):
        apply_scim_patch({"a": 1}, [])


@pytest.mark.xwauth_unit
def test_apply_scim_patch_replace_requires_value() -> None:
    with pytest.raises(ValueError):
        apply_scim_patch({"name": {"familyName": "A"}}, [ScimPatchOperation(op="replace", path="name.familyName", value=None)])


@pytest.mark.xwauth_unit
def test_apply_scim_patch_rejects_array_selector_paths() -> None:
    with pytest.raises(ValueError, match="array path selectors"):
        apply_scim_patch(
            {"emails": [{"value": "a@example.com"}]},
            [ScimPatchOperation(op="replace", path="emails[0].value", value="b@example.com")],
        )


@pytest.mark.xwauth_unit
def test_enforce_scim_if_match_rejects_mismatch() -> None:
    with pytest.raises(ValueError, match="precondition failed"):
        enforce_scim_if_match('"v2"', '"v1"')

