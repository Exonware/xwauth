#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/__init__.py
XWAuth — **OAuth 2.0 / OIDC connector** for the Exonware stack: authorization server surface,
token and session contracts, federation core, storage hooks, and policy integration.

**Identity providers**, WebAuthn/MFA, and OAuth **RP clients** live in **exonware-xwlogin**
(`exonware.xwlogin`). Install `exonware-xwauth[login]` or `exonware-xwlogin` for the full
login + connector story. Those symbols are also re-exported from this package via **lazy**
imports (PEP 562) so `import exonware.xwauth` works without xwlogin until you access a
login-only name. See `xwauth/.references/` for competitive positioning notes. When **exonware-xwlogin**
is installed, prefer its ``*_connector`` and ``handlers.connector_*`` modules over deep
``exonware.xwauth.*`` imports for IdPs, login HTTP glue, and MFA helpers — summarized in
``.references/COMPETITIVE_STACK.md``.
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
# Core exports (facade factories lazy-import xwlogin only when called)
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

_LAZY_XWLOGIN: dict[str, tuple[str, str]] = {
    "build_pem_root_certs_bytes_by_fmt": (
        "exonware.xwlogin.authentication.attestation_trust",
        "build_pem_root_certs_bytes_by_fmt",
    ),
    "audit_mfa_event": (
        "exonware.xwlogin.authentication.mfa_webauthn_audit",
        "audit_mfa_event",
    ),
    "audit_webauthn_event": (
        "exonware.xwlogin.authentication.mfa_webauthn_audit",
        "audit_webauthn_event",
    ),
    "WebAuthnManager": (
        "exonware.xwlogin.authentication.webauthn",
        "WebAuthnManager",
    ),
    "register_webauthn_credential_mapping": (
        "exonware.xwlogin.authentication.webauthn_credential_index",
        "register_webauthn_credential_mapping",
    ),
    "unregister_webauthn_credential_mapping": (
        "exonware.xwlogin.authentication.webauthn_credential_index",
        "unregister_webauthn_credential_mapping",
    ),
    "rebuild_webauthn_credential_index": (
        "exonware.xwlogin.authentication.webauthn_credential_index",
        "rebuild_webauthn_credential_index",
    ),
    "resolve_user_for_webauthn_credential": (
        "exonware.xwlogin.authentication.webauthn_credential_index",
        "resolve_user_for_webauthn_credential",
    ),
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

_LOGIN_INSTALL_HINT = (
    "Install exonware-xwlogin (e.g. pip install 'exonware-xwauth[login]') for WebAuthn/MFA helpers "
    "and OAuth RP clients."
)


def __getattr__(name: str) -> Any:
    spec = _LAZY_XWLOGIN.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod_name, attr_name = spec
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as e:
        raise AttributeError(
            f"cannot import {name!r}: optional package exonware-xwlogin is not installed. "
            f"{_LOGIN_INSTALL_HINT}"
        ) from e
    value = getattr(mod, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(
        {n for n in globals() if not n.startswith("_")} | set(_LAZY_XWLOGIN)
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
]
