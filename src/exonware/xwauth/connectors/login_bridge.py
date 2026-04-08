# exonware/xwauth/src/exonware/xwauth/connectors/login_bridge.py
"""
How **exonware-xwauth** attaches to **exonware-xwlogin** (REF_41 §6).

- **IN_PROCESS:** import ``exonware.xwlogin`` when both packages are installed (same interpreter).
- **REMOTE_API:** HTTP client to a host running **exonware-xwlogin-api** on **XWApiServer** (base URL + routes).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(frozen=True, slots=True)
class LoginRemoteConfig:
    """HTTP attachment to a **xwlogin-api** host (**XWApiServer**). Use with ``LoginBridgeMode.REMOTE_API``."""

    base_url: str
    """Scheme + host (+ optional port), no trailing slash, e.g. ``https://login.example.com``."""

    timeout_s: float = 30.0


class LoginBridgeMode(str, Enum):
    """Where login primitives are resolved for this auth deployment."""

    IN_PROCESS = "in_process"
    REMOTE_API = "remote_api"


def load_login_package() -> Any:
    """
    Return the ``exonware.xwlogin`` module (in-process attachment).

    Raises ``ImportError`` with guidance if ``exonware-xwlogin`` is not installed —
    install the login product or use ``LoginBridgeMode.REMOTE_API``.
    """
    try:
        import exonware.xwlogin as xwlogin
    except ImportError as e:
        raise ImportError(
            "exonware-xwlogin is not installed. For in-process login wiring install "
            "'exonware-xwlogin' (e.g. pip install exonware-xwauth[xwlogin]). "
            "For remote login, use LoginBridgeMode.REMOTE_API with an HTTP client to "
            "exonware-xwlogin-api."
        ) from e
    return xwlogin
