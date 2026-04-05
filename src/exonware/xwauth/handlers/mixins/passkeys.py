"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.passkeys``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.passkeys",
    (
        "passkeys_login_options",
        "passkeys_login_verify",
        "passkeys_register_options",
        "passkeys_register_verify",
    ),
)
