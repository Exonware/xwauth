# exonware/xwauth/src/exonware/xwauth/connectors/login_bridge.py
"""
Attach **exonware-xwauth** to a login or IdP surface over **HTTP**.

``exonware-xwauth`` stays decoupled from concrete login products: treat any
login or identity deployment as a separate service that exposes OAuth 2.0 /
OIDC (or similar) endpoints. Use ``LoginBridgeMode.REMOTE_API`` and an HTTP
client to that base URL.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(frozen=True, slots=True)
class LoginRemoteConfig:
    """HTTP client configuration for a remote login / IdP deployment."""

    base_url: str
    """Scheme + host (+ optional port), no trailing slash, e.g. ``https://login.example.com``."""

    timeout_s: float = 30.0


class LoginBridgeMode(str, Enum):
    """Where login primitives are resolved for this auth deployment."""

    REMOTE_API = "remote_api"


def load_login_package() -> Any:
    """
    .. deprecated::
        In-process login package coupling was removed. Use ``LoginRemoteConfig``
        and call your login / IdP service over HTTPS using standard OAuth 2.0 /
        OIDC endpoints.
    """
    raise ImportError(
        "In-process login packages are not loaded from exonware-xwauth. "
        "Use LoginBridgeMode.REMOTE_API with LoginRemoteConfig (base URL + HTTP client) "
        "against a standards-compliant login or IdP deployment."
    )
