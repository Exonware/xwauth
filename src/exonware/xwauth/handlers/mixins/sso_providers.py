"""Compatibility shim: implementation in ``exonware.xwlogin.handlers.mixins.sso_providers``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.sso_providers",
    (
        "EXPLICIT_SSO_PROVIDERS",
        "apple_callback",
        "build_dynamic_callback_handlers",
        "discord_callback",
        "get_provider_callback_routes",
        "github_callback",
        "google_callback",
        "microsoft_callback",
        "saml_callback",
        "slack_callback",
    ),
)
