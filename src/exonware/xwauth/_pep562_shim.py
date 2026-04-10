"""Shared PEP 562 lazy re-exports (historical); ``exonware.xwlogin`` is not imported."""

from __future__ import annotations

import importlib
from typing import Any, Sequence

_DEFAULT_HINT = (
    "exonware-xwauth does not import login-provider packages. "
    "Integrate identity/login via OAuth 2.0 / OIDC (and related) HTTP APIs from your deployment."
)

_XWLOGIN_PREFIX = "exonware.xwlogin."


def bind_lazy_exports(
    ns: dict[str, Any],
    impl_module: str,
    export_names: Sequence[str],
    *,
    install_hint: str | None = None,
) -> None:
    """Define ``__getattr__`` / ``__dir__`` on *ns* (typically ``globals()`` of a shim module)."""
    names_f = frozenset(export_names)
    ns["__all__"] = list(export_names)
    mod_name = ns["__name__"]
    hint = install_hint or _DEFAULT_HINT

    def __getattr__(name: str) -> Any:
        if name not in names_f:
            raise AttributeError(f"module {mod_name!r} has no attribute {name!r}")
        if impl_module.startswith(_XWLOGIN_PREFIX):
            raise AttributeError(
                f"cannot resolve {name!r} from {mod_name!r}: {hint}"
            ) from None
        try:
            mod = importlib.import_module(impl_module)
        except ImportError as e:
            raise AttributeError(
                f"cannot import {name!r}: optional dependency missing. {hint}"
            ) from e
        val = getattr(mod, name)
        ns[name] = val
        return val

    def __dir__() -> list[str]:
        return sorted({n for n in ns if not n.startswith("_")} | set(names_f))

    ns["__getattr__"] = __getattr__
    ns["__dir__"] = __dir__
