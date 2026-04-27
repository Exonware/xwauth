#!/usr/bin/env python3
"""Split _legacy.py into service-grouped mixin modules. Run from xwauth root."""

from pathlib import Path
LEGACY = Path("src/exonware/xwauth.connector/api/services/_legacy.py")
MIXINS = Path("src/exonware/xwauth.connector/api/services/mixins")
MIXINS.mkdir(parents=True, exist_ok=True)
# (start_1based, end_1based_inclusive) slices in _legacy. Skip header (1-44) and userinfo/logout (396-557).
SLICES = {
    "client_registration": (46, 343),      # DCR: register, register_get, register_put, register_delete
    "user": (565, 798),                    # register_user, get_current_user, update_current_user
    "password": (800, 961),                # password_reset, password_change
    "otp": (963, 1102),                    # otp_send, otp_verify
    "magic_link": (1104, 1224),            # magic_link_send, magic_link_verify
    "mfa": (1226, 1442),                   # mfa_setup_totp, mfa_verify_totp
    "passkeys": (1444, 1949),              # passkeys register/login options/verify
    "sessions": (1951, 2130),              # sessions_list, revoke, revoke_others
    "organizations": (2132, 2843),         # org helpers + list, create, get, update, users_me_organizations, invite, members, etc.
    "sso_providers": (2846, 3470),         # google, microsoft, apple, github, discord, slack callbacks
    "saml": (3471, 3739),                  # _get_saml_manager, saml_metadata, saml_acs, sso_discovery
    "fga": (3741, 4024),                   # _get_fga_manager, fga check, write_tuples, expand, permissions_me
    "webhooks": (4051, 4330),              # _get_webhook_manager, register, list, delete, test
    "admin": (4331, 5172),                 # _get_audit_log_manager, audit_logs, impersonate, users CRUD, list_users
    "system": (5174, 5292),                # health, metrics, oauth_protected_resource
}
IMPORTS_BY_MIXIN = {
    "client_registration": "AUTH_TAGS, AUTH_PREFIX, get_auth",  # DCR uses AUTH_PREFIX for registration_endpoint_base
    "user": "USER_TAGS, get_auth, get_user_lifecycle, get_email_password_authenticator, get_current_user_id",
    "password": "USER_TAGS, get_auth, get_user_lifecycle, get_email_password_authenticator, get_current_user_id",
    "otp": "AUTH_TAGS, get_auth, get_phone_otp_authenticator, get_current_user_id",
    "magic_link": "AUTH_TAGS, get_auth, get_magic_link_authenticator, AUTH_PREFIX, API_VERSION",
    "mfa": "MFA_TAGS, get_auth, get_current_user_id",
    "passkeys": "MFA_TAGS, get_auth, get_current_user_id",
    "sessions": "AUTH_TAGS, get_auth, get_bearer_token, get_current_user_id",
    "organizations": "ORG_TAGS, get_auth, get_current_user_id, get_organization_lifecycle, get_organization_manager",
    "sso_providers": "AUTH_TAGS, SSO_TAGS, get_auth, AUTH_PREFIX",
    "saml": "SSO_TAGS, get_auth, get_saml_manager",
    "fga": "AUTHZ_TAGS, get_auth, get_current_user_id, get_fga_manager",
    "webhooks": "WEBHOOK_TAGS, get_auth, get_current_user_id, get_webhook_manager",
    "admin": "ADMIN_TAGS, get_auth, introspect_and_check_admin, get_audit_log_manager",
    "system": "SYSTEM_TAGS, get_auth, PATH_HEALTH, PATH_METRICS",
}
DESCRIPTIONS = {
    "client_registration": "DCR (RFC 7591/7592): register, register_get, register_put, register_delete",
    "user": "User: register_user, get_current_user, update_current_user",
    "password": "Password: reset, change",
    "otp": "OTP: send, verify",
    "magic_link": "Magic link: send, verify",
    "mfa": "MFA TOTP: setup, verify",
    "passkeys": "WebAuthn/Passkeys: register/login options and verify",
    "sessions": "Sessions: list, revoke, revoke_others",
    "organizations": "Organizations: CRUD, members, invite, users_me_organizations",
    "sso_providers": "SSO OAuth callbacks: Google, Microsoft, Apple, GitHub, Discord, Slack",
    "saml": "SAML SSO: metadata, ACS, discovery",
    "fga": "FGA/ReBAC: check, tuples, expand, permissions_me",
    "webhooks": "Webhooks: register, list, delete, test",
    "admin": "Admin: audit logs, impersonate, users CRUD",
    "system": "System: health, metrics, oauth_protected_resource",
}
# Extra symbols from _common (only where handler code uses them)
EXTRA_FROM_COMMON = {
    "magic_link": ", AUTH_PREFIX, API_VERSION",
}


def main():
    root = Path(__file__).resolve().parents[1]
    legacy_path = root / LEGACY
    text = legacy_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for name, (start, end) in SLICES.items():
        chunk = "".join(lines[start - 1 : end])
        # Replace legacy helpers with _common helpers
        chunk = chunk.replace("_get_organization_lifecycle(", "get_organization_lifecycle(")
        chunk = chunk.replace("_get_organization_manager(", "get_organization_manager(")
        chunk = chunk.replace("_get_saml_manager(", "get_saml_manager(")
        chunk = chunk.replace("_get_fga_manager(", "get_fga_manager(")
        chunk = chunk.replace("_get_webhook_manager(", "get_webhook_manager(")
        chunk = chunk.replace("_get_audit_log_manager(", "get_audit_log_manager(")
        imports = IMPORTS_BY_MIXIN[name] + EXTRA_FROM_COMMON.get(name, "")
        header = f'''# exonware/xwauth.connector/api/services/mixins/{name}.py
"""{DESCRIPTIONS[name]}."""
from __future__ import annotations
from typing import Any, Optional
from fastapi import Request, Depends, Header
from fastapi.responses import JSONResponse, RedirectResponse, Response
from exonware.xwaction import XWAction
from exonware.xwaction.defs import ActionProfile
from ...errors import oauth_error_to_http
from .._common import (
    {imports}
)
'''
        out_path = root / MIXINS / f"{name}.py"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(header + chunk, encoding="utf-8")
        print(f"Wrote {out_path.relative_to(root)}")
    print("Done. Update mixins/__init__.py and services/__init__.py, then delete _legacy.py.")
if __name__ == "__main__":
    main()
