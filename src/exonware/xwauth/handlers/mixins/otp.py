"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.otp``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.otp",
    ("otp_send", "otp_verify"),
)
