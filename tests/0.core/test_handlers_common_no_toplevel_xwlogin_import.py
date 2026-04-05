#!/usr/bin/env python3
# exonware/xwauth/tests/0.core/test_handlers_common_no_toplevel_xwlogin_import.py
"""Connector import hygiene: no module-level ``exonware.xwlogin`` in xwauth src; lazy factory smoke (GUIDE_32/51)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


def _module_level_xwlogin_imports(py_path: Path) -> list[tuple[int, str]]:
    text = py_path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(py_path))
    bad: list[tuple[int, str]] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
            if mod == "exonware.xwlogin" or mod.startswith("exonware.xwlogin."):
                bad.append((node.lineno, mod))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name == "exonware.xwlogin" or name.startswith("exonware.xwlogin."):
                    bad.append((node.lineno, name))
    return bad


@pytest.mark.xwauth_core
def test_handlers_common_lazy_authenticator_factories_resolve_with_xwlogin() -> None:
    """Monorepo / [login] env: first call loads xwlogin and returns real authenticator types (GUIDE_51)."""
    from types import SimpleNamespace

    from exonware.xwauth.handlers import _common as handler_common

    # Factories require ``auth.config`` (and optional ``storage``) like real ``XWAuth``.
    auth = SimpleNamespace(storage=None, config=SimpleNamespace())
    for getter in (
        handler_common.get_email_password_authenticator,
        handler_common.get_magic_link_authenticator,
        handler_common.get_phone_otp_authenticator,
    ):
        inst = getter(auth)
        assert inst is not None
        assert callable(getattr(inst, "authenticate", None))


@pytest.mark.xwauth_core
def test_xwauth_src_has_no_module_level_exonware_xwlogin_import() -> None:
    """Connector package must not bind xwlogin at import time anywhere under ``src`` (GUIDE_32)."""
    root = Path(__file__).resolve().parents[2]
    pkg = root / "src" / "exonware" / "xwauth"
    assert pkg.is_dir(), f"missing {pkg}"
    failures: list[str] = []
    for path in sorted(pkg.rglob("*.py")):
        rel = path.relative_to(pkg).as_posix()
        for ln, mod in _module_level_xwlogin_imports(path):
            failures.append(f"  {rel}:{ln} {mod}")
    assert not failures, (
        "exonware.xwauth src must not import exonware.xwlogin at module level "
        "(use lazy imports inside functions or PEP 562 shims). Offenders:\n"
        + "\n".join(failures)
    )
