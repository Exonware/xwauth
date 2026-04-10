"""Legacy OAuth callback discovery shim (blocked — use OAuth 2.0 / OIDC HTTP integration)."""

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
