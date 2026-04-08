# exonware/xwauth/security/backup_codes.py
"""Compatibility shim: implementation in ``exonware.xwlogin.security.backup_codes``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.security.backup_codes",
    ("generate_backup_codes", "hash_backup_code", "verify_backup_code"),
    install_hint=(
        "Install exonware-xwlogin (e.g. pip install 'exonware-xwauth[xwlogin]') for MFA backup-code helpers."
    ),
)
