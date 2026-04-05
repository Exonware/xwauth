"""Compatibility shim: OAuth callback discovery lives in ``exonware.xwlogin.providers.callback_providers``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.providers.callback_providers",
    (
        "discover_oauth2_callback_provider_names",
        "get_oauth2_callback_provider_names",
        "verify_provider_names_match_modules",
    ),
)
