#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/__init__.py
XWAuth — **OAuth 2.0 / OIDC connector** for the Exonware stack: authorization server surface,
token and session contracts, federation core, storage hooks, and policy integration.

OAuth **client** helpers (RP-style sessions, token manager, entity sessions) ship **in this
package** under ``exonware.xwauth.clients`` and talk to **any** OAuth 2.0 / OIDC authorization
server over HTTP.

Login, IdP catalogs, WebAuthn stores, and first-party authenticator **implementations** are
**not** declared dependencies of ``exonware-xwauth``. Treat them as separate products or
services that follow OAuth 2.0, OIDC, WebAuthn, or your chosen API contracts at the HTTP
boundary. See ``xwauth/.references/`` for positioning notes.
"""
from __future__ import annotations

import importlib
import os
from typing import Any

# =============================================================================
# XWLAZY INTEGRATION — GUIDE_00_MASTER: config_package_lazy_install_enabled (EARLY)
# =============================================================================
# Dependency: exonware-xwlazy (optional; install exonware-xwauth[lazy] or [dev]).
# Under pytest / stack tests, skip auto-registration: the global import hook can break native
# stacks (lxml/signxml/SAML). Set XWSTACK_SKIP_XWLAZY_INIT=0 to force-enable in tests if needed.
if os.environ.get("XWSTACK_SKIP_XWLAZY_INIT", "").lower() not in ("1", "true", "yes"):
    try:
        from exonware.xwlazy import config_package_lazy_install_enabled

        config_package_lazy_install_enabled(
            __package__ or "exonware.xwauth",
            enabled=True,
            mode="smart",
        )
    except ImportError:
        # xwlazy not installed — omit [lazy] extra or install exonware-xwlazy for lazy mode.
        pass
from .version import __version__, __author__, __email__
# Core exports (OAuth client symbols lazy-import from exonware.xwauth.clients)
from .facade import XWAuth, create_webauthn_challenge_store, create_webauthn_credential_index_redis
from .config.config import XWAuthConfig
from .contracts import AuthContext, IAuthContextResolver, IStorageProvider, IRateLimiter, IAuditLogger
from .base import ABaseAuth
from .errors import (
    XWAuthError,
    XWOAuthError,
    XWTokenError,
    XWProviderError,
    XWConfigError,
    XWValidationError,
    XWMFAError,
    XWMFAInvalidCodeError,
    XWMFARequiredError,
    XWWebAuthnError,
    XWWebAuthnChallengeError,
    XWWebAuthnCredentialError,
    XWCSRFError,
    XWRateLimitError,
)
from .defs import GrantType, TokenType, SessionStatus, UserStatus
# Extended from xwsystem (xwauth extends xwsystem)
from .providers.xwsystem_providers import OAuth2Provider, JWTProvider, SAMLProvider, EnterpriseAuth
# OAuth 1.0 support
from .core.oauth1 import OAuth1Server, OAuth1Client, OAuth1Signature, OAuth1RequestValidator
# JOSE library
from .jose import JWTManager, JWSManager, JWEManager, JWKManager, JWAManager, JOSEKeyManager
# Advanced RFC support
from .core.rfc import RFC9101BrowserBasedApps, RFC9207IssuerIdentification, RFC9068JWTProfile, RFC7521JWTBearerToken
from .extensions import IAuthHook, AuthHookRegistry
from .federation import FederationBroker, FederatedIdentity
from .oauth_http.resource_owner_session import ensure_resource_owner_session

_LAZY_CLIENT_EXPORTS: dict[str, tuple[str, str]] = {
    "OAuth2ClientManager": (
        "exonware.xwauth.clients.oauth_client",
        "OAuth2ClientManager",
    ),
    "EntitySessionManager": (
        "exonware.xwauth.clients.entity_session_manager",
        "EntitySessionManager",
    ),
    "OAuth2Session": (
        "exonware.xwauth.clients.oauth2_client",
        "OAuth2Session",
    ),
    "AsyncOAuth2Session": (
        "exonware.xwauth.clients.async_client",
        "AsyncOAuth2Session",
    ),
}

_LEGACY_WEBAUTHN_EXPORTS = frozenset(
    {
        "WebAuthnManager",
        "build_pem_root_certs_bytes_by_fmt",
        "audit_mfa_event",
        "audit_webauthn_event",
        "register_webauthn_credential_mapping",
        "unregister_webauthn_credential_mapping",
        "rebuild_webauthn_credential_index",
        "resolve_user_for_webauthn_credential",
    }
)

_WEBAUTHN_ATTR_ERR = (
    "not exported from exonware.xwauth: integrate WebAuthn, MFA attestation, or credential "
    "indexing via a separate component or HTTPS API — not as a coupled Python dependency."
)


def __getattr__(name: str) -> Any:
    if name in _LEGACY_WEBAUTHN_EXPORTS:
        raise AttributeError(f"{name!r} {_WEBAUTHN_ATTR_ERR}")
    spec = _LAZY_CLIENT_EXPORTS.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod_name, attr_name = spec
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as e:
        raise AttributeError(f"cannot import {name!r} from {mod_name!r}") from e
    value = getattr(mod, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(
        {n for n in globals() if not n.startswith("_")}
        | set(_LAZY_CLIENT_EXPORTS)
        | set(_LEGACY_WEBAUTHN_EXPORTS)
    )


__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Main classes
    "XWAuth",
    "create_webauthn_challenge_store",
    "create_webauthn_credential_index_redis",
    "WebAuthnManager",
    "build_pem_root_certs_bytes_by_fmt",
    "audit_mfa_event",
    "audit_webauthn_event",
    "register_webauthn_credential_mapping",
    "unregister_webauthn_credential_mapping",
    "rebuild_webauthn_credential_index",
    "resolve_user_for_webauthn_credential",
    "XWAuthConfig",
    # Interfaces
    "IStorageProvider",
    "AuthContext",
    "IAuthContextResolver",
    "IRateLimiter",
    "IAuditLogger",
    # Base classes
    "ABaseAuth",
    # Errors
    "XWAuthError",
    "XWOAuthError",
    "XWTokenError",
    "XWProviderError",
    "XWConfigError",
    "XWValidationError",
    "XWMFAError",
    "XWMFAInvalidCodeError",
    "XWMFARequiredError",
    "XWWebAuthnError",
    "XWWebAuthnChallengeError",
    "XWWebAuthnCredentialError",
    "XWCSRFError",
    "XWRateLimitError",
    # Enums
    "GrantType",
    "TokenType",
    "SessionStatus",
    "UserStatus",
    # Extended from xwsystem (xwauth extends xwsystem)
    "OAuth2Provider",
    "JWTProvider",
    "SAMLProvider",
    "EnterpriseAuth",
    # Client-side OAuth and session management
    "OAuth2ClientManager",
    "EntitySessionManager",
    "OAuth2Session",
    "AsyncOAuth2Session",
    # OAuth 1.0 support
    "OAuth1Server",
    "OAuth1Client",
    "OAuth1Signature",
    "OAuth1RequestValidator",
    # JOSE library
    "JWTManager",
    "JWSManager",
    "JWEManager",
    "JWKManager",
    "JWAManager",
    "JOSEKeyManager",
    # Advanced RFC support
    "RFC9101BrowserBasedApps",
    "RFC9207IssuerIdentification",
    "RFC9068JWTProfile",
    "RFC7521JWTBearerToken",
    "IAuthHook",
    "AuthHookRegistry",
    "FederationBroker",
    "FederatedIdentity",
    # Resource-owner probe + password grant (Cookie/Authorization reuse)
    "ensure_resource_owner_session",
]
