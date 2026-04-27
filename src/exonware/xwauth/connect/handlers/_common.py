"""HTTP handler primitives owned by ``exonware.xwauth.connect``.

This module ships the minimal set of OpenAPI tag constants, request-scoped
getters, and auth-instance resolvers that the connector's HTTP handlers need.
It is **NOT** a shim — each of the two packages (``xwauth-connect`` and
``xwauth-identity``) owns its own copy of these primitives so neither has to
import the other.

If you find yourself importing from ``exonware.xwauth.identity.*`` here to
"share" a symbol, stop: those two packages must stay independent.
"""

from __future__ import annotations

from typing import Any

from exonware.xwapi.http import Request

# -----------------------------------------------------------------------------
# OpenAPI tag lists (used by connector callback handlers for docs grouping).
# -----------------------------------------------------------------------------
AUTH_TAGS: list[str] = ["Auth"]
USER_TAGS: list[str] = ["Users"]
PROVIDERS_TAGS: list[str] = ["Providers"]
SSO_TAGS: list[str] = ["SSO"]
MFA_TAGS: list[str] = ["MFA"]
ADMIN_TAGS: list[str] = ["Admin"]
SYSTEM_TAGS: list[str] = ["System"]
AUTHZ_TAGS: list[str] = ["Authorization"]

__all__ = [
    "AUTH_TAGS",
    "USER_TAGS",
    "PROVIDERS_TAGS",
    "SSO_TAGS",
    "MFA_TAGS",
    "ADMIN_TAGS",
    "SYSTEM_TAGS",
    "AUTHZ_TAGS",
    "get_auth",
    "get_user_lifecycle",
]


def get_auth(request: Request) -> Any:
    """Return the connector-side auth instance from ``request.app.state``.

    Hosts that mount ``xwauth.connect`` routes attach the auth/broker instance
    as ``app.state.xwauth_connect``. Callback handlers retrieve it via this
    getter so handler code never hardcodes the attribute name.
    """
    return request.app.state.xwauth_connect


def get_user_lifecycle(auth: Any) -> Any:
    """Return the UserLifecycle bound to the given auth instance.

    The concrete ``UserLifecycle`` class lives on whatever identity backend the
    connector is composed with. In-process composition reads it off the auth
    instance directly; remote-HTTP composition resolves it via the connector's
    own client surface.
    """
    return auth.user_lifecycle
