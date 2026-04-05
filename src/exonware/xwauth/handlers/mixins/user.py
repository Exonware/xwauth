"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.user``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.user",
    ("get_current_user", "register_user", "update_current_user"),
)
