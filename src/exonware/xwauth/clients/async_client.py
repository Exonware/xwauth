"""Shim: use ``exonware.xwlogin.clients.async_client`` for new code."""

from __future__ import annotations

from exonware.xwauth._pep562_shim import bind_lazy_exports

bind_lazy_exports(globals(), "exonware.xwlogin.clients.async_client", ("AsyncOAuth2Session",))
