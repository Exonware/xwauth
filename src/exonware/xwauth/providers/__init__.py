#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/providers/__init__.py
XWAuth provider **core**: registry, base class, and xwsystem bridge types.

Concrete OAuth/OIDC identity provider implementations may be supplied by separate packages
on ``PYTHONPATH``. Submodule ``callback_providers`` documents the expected callback
discovery surface; ``exonware-xwauth`` does not declare those packages as pip dependencies.
Integrate IdPs primarily via OAuth 2.0 / OIDC HTTP APIs.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from __future__ import annotations

from typing import Any

from .base import ABaseProvider
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
    """Delegate IdP symbols to an optional providers package on ``PYTHONPATH``, if present."""
    try:
        import exonware.xwlogin.providers as _lp
    except ImportError as e:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}. "
            "No optional IdP provider package was found. Use OAuth 2.0 / OIDC HTTP integration, "
            "or add a compatible provider package to the environment."
        ) from e
    if hasattr(_lp, name):
        return getattr(_lp, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    try:
        import exonware.xwlogin.providers as _lp

        extra = [x for x in dir(_lp) if not x.startswith("_")]
    except ImportError:
        extra = []
    return sorted(set(__all__) | set(extra))
