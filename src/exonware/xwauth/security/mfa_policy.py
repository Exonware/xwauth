# exonware/xwauth/security/mfa_policy.py
"""Compatibility shim: implementation in ``exonware.xwlogin.security.mfa_policy``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.security.mfa_policy",
    (
        "MfaPolicyContext",
        "MfaSecurityProfile",
        "attestation_for_profile",
        "merge_amr_claims",
        "require_backup_codes",
        "step_up_required_aal2",
    ),
    install_hint=(
        "Install exonware-xwlogin (e.g. pip install 'exonware-xwauth[xwlogin]') for MFA / WebAuthn policy helpers."
    ),
)
