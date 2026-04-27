#!/usr/bin/env python3
"""
#exonware/xwauth.connect/tests/1.unit/core_tests/test_connect_identity_discovery.py
Regression tests for connect<->identity coexistence discovery helpers.
"""

import importlib
from types import ModuleType

import pytest

import exonware.xwauth.connect as connect_pkg


@pytest.mark.xwauth_core
class TestConnectIdentityDiscovery:
    """Ensure discovery semantics stay safe and deterministic."""

    def test_discovery_returns_none_when_identity_not_installed(self, monkeypatch):
        connect_pkg._reset_discovery_cache_for_tests()
        monkeypatch.delenv("XWAUTH_CONNECT_DISABLE_IDENTITY_DISCOVERY", raising=False)

        def _import_module(name: str):
            raise ModuleNotFoundError("No module named 'exonware.xwauth.identity'", name="exonware.xwauth.identity")

        monkeypatch.setattr(importlib, "import_module", _import_module)
        assert connect_pkg.discover_identity_package() is None
        assert connect_pkg.identity_is_available() is False

    def test_discovery_does_not_mask_identity_internal_dependency_errors(self, monkeypatch):
        connect_pkg._reset_discovery_cache_for_tests()
        monkeypatch.delenv("XWAUTH_CONNECT_DISABLE_IDENTITY_DISCOVERY", raising=False)

        def _import_module(name: str):
            raise ModuleNotFoundError("No module named 'missing_transitive_dep'", name="missing_transitive_dep")

        monkeypatch.setattr(importlib, "import_module", _import_module)
        with pytest.raises(ModuleNotFoundError):
            connect_pkg.discover_identity_package()

    def test_discovery_success_is_cached(self, monkeypatch):
        connect_pkg._reset_discovery_cache_for_tests()
        monkeypatch.delenv("XWAUTH_CONNECT_DISABLE_IDENTITY_DISCOVERY", raising=False)
        mod = ModuleType("exonware.xwauth.identity")
        calls = {"count": 0}

        def _import_module(name: str):
            calls["count"] += 1
            return mod

        monkeypatch.setattr(importlib, "import_module", _import_module)
        first = connect_pkg.discover_identity_package()
        second = connect_pkg.discover_identity_package()
        assert first is mod
        assert second is mod
        assert connect_pkg.identity_is_available() is True
        assert calls["count"] == 1
