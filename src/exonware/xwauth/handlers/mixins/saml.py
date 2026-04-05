"""Compatibility shim: SAML SSO routes live in ``exonware.xwlogin.handlers.mixins.saml``."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(
    globals(),
    "exonware.xwlogin.handlers.mixins.saml",
    ("saml_metadata", "saml_acs", "sso_discovery"),
)
