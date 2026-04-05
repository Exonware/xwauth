#!/usr/bin/env python3
"""
Unit tests for SCIM filtering helpers.
"""

from __future__ import annotations

import pytest

from exonware.xwauth.scim.filtering import match_scim_filter, parse_scim_term


@pytest.mark.xwauth_unit
def test_parse_scim_term_parses_eq_expression() -> None:
    term = parse_scim_term('userName eq "alice"')
    assert term.attribute == "userName"
    assert term.operator == "eq"
    assert term.value == "alice"


@pytest.mark.xwauth_unit
def test_parse_scim_term_rejects_unsupported_expression() -> None:
    with pytest.raises(ValueError):
        parse_scim_term("userName xx \"alice\"")


@pytest.mark.xwauth_unit
def test_match_scim_filter_supports_and_or_subset() -> None:
    resource = {
        "userName": "alice",
        "emails": {"work": "alice@example.com"},
        "displayName": "Alice Example",
    }
    assert match_scim_filter(resource, 'userName eq "alice" and displayName co "Example"')
    assert match_scim_filter(resource, 'userName eq "bob" or emails.work ew "@example.com"')
    assert not match_scim_filter(resource, 'userName eq "bob" and displayName co "Example"')


@pytest.mark.xwauth_unit
def test_match_scim_filter_rejects_parenthesis_expressions() -> None:
    resource = {"userName": "alice"}
    with pytest.raises(ValueError):
        match_scim_filter(resource, '(userName eq "alice")')


@pytest.mark.xwauth_unit
def test_match_scim_filter_supports_presence_and_numeric_comparisons() -> None:
    resource = {"userName": "alice", "active": True, "meta": {"version": 3}}
    assert match_scim_filter(resource, "userName pr")
    assert match_scim_filter(resource, "meta.version ge 2")
    assert match_scim_filter(resource, "meta.version lt 4")
    assert not match_scim_filter(resource, "meta.version gt 10")

