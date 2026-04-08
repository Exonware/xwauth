# exonware/xwauth/security/mfa_secrets.py
"""Compatibility shim: implementation in ``exonware.xwlogin.security.mfa_secrets``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.security.mfa_secrets",
    ("decrypt_totp_secret", "derive_mfa_encryption_key", "encrypt_totp_secret"),
    install_hint=(
        "Install exonware-xwlogin (e.g. pip install 'exonware-xwauth[xwlogin]') for TOTP envelope encryption."
    ),
)
