#!/usr/bin/env python3
"""
#exonware/xwauth.connector/src/exonware/xwauth.connector/providers/__init__.py
XWAuth provider **core**: registry, base class, and xwsystem bridge types.

Concrete OAuth/OIDC identity provider implementations may be supplied by separate packages
on ``PYTHONPATH``. Optional symbols from the **login connector** are exposed via ``__getattr__``
when that distribution is installed; ``exonware-xwauth-connector`` does not declare it as a required
dependency. Submodule ``callback_providers`` documents the callback discovery surface. Integrate
IdPs primarily via OAuth 2.0 / OIDC HTTP APIs.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from __future__ import annotations

from typing import Any

from exonware.xwauth.connect.base import ABaseProvider
from .registry import ProviderRegistry
from .xwsystem_providers import EnterpriseAuth, JWTProvider, OAuth2Provider, SAMLProvider

__all__ = [
    "ABaseProvider",
    "ProviderRegistry",
    "OAuth2Provider",
    "JWTProvider",
    "SAMLProvider",
    "EnterpriseAuth",
]


def __getattr__(name: str) -> Any:
    """Resolve provider classes lazily from local sibling modules.

    Two resolution attempts (no shim — real canonical lookup):

    1. Exact submodule name: ``providers.<name>`` (covers ``callback_providers``
       and any manager-ish helper modules whose attribute name IS the module
       name).
    2. Class-name convention: a provider class ``XyzProvider`` is expected to
       live in submodule ``xyz``. Strip a trailing ``Provider``, lowercase the
       remainder, and try that submodule. If present and the class is defined
       there, return it.
    """
    import importlib

    # (1) exact submodule name.
    try:
        mod = importlib.import_module(f"{__name__}.{name}")
    except ImportError:
        mod = None
    if mod is not None and hasattr(mod, name):
        return getattr(mod, name)

    # (2) class-name → submodule convention.
    if name.endswith("Provider"):
        stem = name[: -len("Provider")].lower()
        if stem:
            try:
                mod = importlib.import_module(f"{__name__}.{stem}")
            except ImportError:
                mod = None
            if mod is not None and hasattr(mod, name):
                return getattr(mod, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
