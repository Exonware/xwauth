#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/providers/__init__.py
XWAuth provider **core**: registry, base class, and xwsystem bridge types.

Concrete OAuth/OIDC identity providers live in **exonware-xwlogin**
(``exonware.xwlogin.providers``). Submodule ``callback_providers`` is a **thin shim**
to ``exonware.xwlogin.providers.callback_providers``. For backwards compatibility,
``from exonware.xwauth.providers import SomeProvider`` resolves via
:data:`__getattr__` when xwlogin is installed.

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
    """Delegate IdP symbols to ``exonware.xwlogin.providers`` when installed."""
    try:
        import exonware.xwlogin.providers as _lp
    except ImportError as e:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}. "
            "Install optional dependency exonware-xwlogin (pip install exonware-xwauth[login]) "
            "for concrete identity providers, or import from exonware.xwlogin.providers."
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
