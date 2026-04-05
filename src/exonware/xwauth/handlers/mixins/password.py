"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.password``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.password",
    ("password_change", "password_reset"),
)
