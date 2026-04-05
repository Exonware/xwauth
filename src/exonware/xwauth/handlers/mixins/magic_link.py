"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.magic_link``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.magic_link",
    ("magic_link_send", "magic_link_verify"),
)
