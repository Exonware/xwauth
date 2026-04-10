# exonware/xwauth/clients/__init__.py
"""OAuth 2.0 / OIDC **client** helpers (RP, agents, multi-entity configs).

These types live in ``exonware-xwauth`` and talk to **any** standards-compliant
authorization server over HTTP — they do not assume a specific login product.
"""

from __future__ import annotations

from .async_client import AsyncOAuth2Session
from .entity_session_manager import EntitySessionManager
from .oauth_client import OAuth2ClientManager
from .oauth2_client import OAuth2Session

__all__ = [
    "AsyncOAuth2Session",
    "EntitySessionManager",
    "OAuth2ClientManager",
    "OAuth2Session",
]
