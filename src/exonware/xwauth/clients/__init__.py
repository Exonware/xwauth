# exonware/xwauth/clients/__init__.py
"""Compatibility re-exports for ``exonware.xwauth.clients`` — implementation in ``exonware.xwlogin.clients``.

Attributes resolve on first access (PEP 562) so ``import exonware.xwauth.clients`` works without
xwlogin until you use a client class. Submodules (e.g. ``.oauth2_client``) remain thin shims that
import xwlogin when loaded.
"""

from __future__ import annotations

import importlib
from typing import Any

_LAZY: dict[str, tuple[str, str]] = {
    "OAuth2ClientManager": (
        "exonware.xwlogin.clients.oauth_client",
        "OAuth2ClientManager",
    ),
    "EntitySessionManager": (
        "exonware.xwlogin.clients.entity_session_manager",
        "EntitySessionManager",
    ),
    "OAuth2Session": (
        "exonware.xwlogin.clients.oauth2_client",
        "OAuth2Session",
    ),
    "AsyncOAuth2Session": (
        "exonware.xwlogin.clients.async_client",
        "AsyncOAuth2Session",
    ),
}

_INSTALL_HINT = (
    "Install exonware-xwlogin (e.g. pip install 'exonware-xwauth[xwlogin]') for OAuth RP / agent clients."
)


def __getattr__(name: str) -> Any:
    spec = _LAZY.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod_name, attr_name = spec
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as e:
        raise AttributeError(
            f"cannot import {name!r}: exonware-xwlogin is not installed. {_INSTALL_HINT}"
        ) from e
    value = getattr(mod, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({n for n in globals() if not n.startswith("_")} | set(_LAZY))


__all__ = [
    "OAuth2ClientManager",
    "EntitySessionManager",
    "OAuth2Session",
    "AsyncOAuth2Session",
]
