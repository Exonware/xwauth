#!/usr/bin/env python3
"""
``exonware.xwauth.connect`` — **multi-provider auth connector** (orchestrator).

xwauth-connect is a thin connector layer that integrates many auth providers
(Google, Apple, Microsoft, SAML IdPs, Keycloak, Auth0, xwauth-identity, …) over
HTTP. Each provider has a dedicated module under
``exonware.xwauth.connect.providers``; generic remote wiring lives in
``exonware.xwauth.connect.connectors.login_bridge``.

Independence rule (architectural invariant)
-------------------------------------------
- ``exonware.xwauth.connect`` **never imports** ``exonware.xwauth.identity``.
- ``exonware.xwauth.identity`` **never imports** ``exonware.xwauth.connect``.
- Shared contracts and primitives live in ``exonware.xwsystem.security``.
- Both distributions may be installed side by side; they share the
  ``exonware.xwauth`` namespace via :mod:`pkgutil`-extend namespace packages
  (see ``exonware/__init__.py`` and ``exonware/xwauth/__init__.py``).

Mutual discovery (coexistence)
------------------------------
To compose a host that runs both sides (e.g. ``xwbase-api``), the connect side
can *discover* whether identity is present at runtime — **without** importing
it at module load. Use :func:`discover_identity_package` /
:func:`identity_is_available` below; they are safe when identity is not
installed (they return ``None`` / ``False``).

Similarly ``exonware.xwauth.identity`` exposes a reciprocal
``discover_connect_package`` for symmetric composition. The two packages never
reach into each other's internals — discovery is how hosts compose them.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
"""

from __future__ import annotations

import importlib
import os
from types import ModuleType
from typing import Any

# =============================================================================
# XWLAZY — optional lazy-install hook (parity with every exonware package).
# =============================================================================
if os.environ.get("XWSTACK_SKIP_XWLAZY_INIT", "").lower() not in ("1", "true", "yes"):
    try:
        from exonware.xwlazy import config_package_lazy_install_enabled

        config_package_lazy_install_enabled(
            __package__ or "exonware.xwauth.connect",
            enabled=True,
            mode="smart",
        )
    except ImportError:
        # xwlazy not installed — omit [lazy] extra or install exonware-xwlazy for lazy mode.
        pass

from .version import __version__, __author__, __email__

# =============================================================================
# Mutual discovery — safe, lazy, no hard dependency on identity.
# =============================================================================
# Sentinel-based single-flight cache so repeat calls avoid redundant import attempts
# and do not treat a legitimate ``None`` return as "not yet resolved".
_DISCOVERY_UNSET: Any = object()
_identity_module_cache: Any = _DISCOVERY_UNSET

# Environment hook for integrators that deliberately mock or disable identity
# (e.g. connector-only test harnesses, security probes).
_IDENTITY_DISABLED_ENV = "XWAUTH_CONNECT_DISABLE_IDENTITY_DISCOVERY"


def discover_identity_package() -> ModuleType | None:
    """Return the ``exonware.xwauth.identity`` module if installed, else ``None``.

    Performs a one-time import attempt and caches the result. Safe when the
    identity distribution is not installed — returns ``None`` instead of
    raising ``ImportError``. Hosts that compose both sides (e.g. ``xwbase-api``)
    call this to detect whether in-process identity routes can be mounted;
    otherwise they fall back to HTTP-upstream mode.

    Set ``XWAUTH_CONNECT_DISABLE_IDENTITY_DISCOVERY=1`` to force-return
    ``None`` (useful for connector-only test harnesses).

    Returns:
        The imported identity module on success, or ``None`` when identity
        is not installed / explicitly disabled / failed to import cleanly.
    """
    global _identity_module_cache
    if _identity_module_cache is not _DISCOVERY_UNSET:
        return _identity_module_cache
    if os.environ.get(_IDENTITY_DISABLED_ENV, "").lower() in ("1", "true", "yes"):
        _identity_module_cache = None
        return None
    try:
        mod = importlib.import_module("exonware.xwauth.identity")
    except ModuleNotFoundError as exc:
        # Return ``None`` only when the target package is not installed.
        # Bubble up missing transitive deps from inside identity to avoid
        # masking real runtime defects.
        if exc.name != "exonware.xwauth.identity":
            raise
        _identity_module_cache = None
        return None
    except ImportError:
        _identity_module_cache = None
        return None
    _identity_module_cache = mod
    return mod


def identity_is_available() -> bool:
    """Return ``True`` if ``exonware.xwauth.identity`` can be imported.

    Thin predicate over :func:`discover_identity_package`. Use in control flow
    that branches on "is identity present in this process".
    """
    return discover_identity_package() is not None


def _reset_discovery_cache_for_tests() -> None:
    """Clear the discovery cache. Intended for unit tests only.

    Public helpers never reset the cache; tests that install / uninstall the
    identity distribution mid-process call this to re-exercise discovery.
    """
    global _identity_module_cache
    _identity_module_cache = _DISCOVERY_UNSET


__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "discover_identity_package",
    "identity_is_available",
]


def __getattr__(name: str) -> Any:
    # Intentionally minimal. Do NOT re-export identity-owned types here —
    # that would violate the independence rule (connect must not import
    # identity at module load, or as a side effect of attribute access on the
    # connect root namespace). Consumers that need identity types import them
    # from ``exonware.xwauth.identity`` directly, which requires the identity
    # distribution to be installed.
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
