#!/usr/bin/env python3
"""
# exonware/xwauth.connector/tests/conftest.py
Shared Test Fixtures
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import os
import sys
from pathlib import Path

# xwsystem/xwauth import exonware.xwlazy by default, which installs a global __import__ hook and
# breaks native stacks (lxml/signxml/SAML). Skip lazy auto-registration for this pytest process.
os.environ.setdefault("XWSTACK_SKIP_XWLAZY_INIT", "1")

_TESTS_ROOT = Path(__file__).resolve().parent
_XWAUTH_ROOT = _TESTS_ROOT.parent
_XWAUTH_CONNECT_SRC = _XWAUTH_ROOT / "src"
_XWAUTH_IDENTITY_SRC = _XWAUTH_ROOT.parent / "xwauth-identity" / "src"
if _XWAUTH_CONNECT_SRC.is_dir():
    sys.path.insert(0, str(_XWAUTH_CONNECT_SRC))
if _XWAUTH_IDENTITY_SRC.is_dir():
    sys.path.insert(0, str(_XWAUTH_IDENTITY_SRC))

def _patch_fastapi_middleware_stack_for_starlette() -> None:
    """FastAPI 0.104 unpacks Middleware as (cls, opts); Starlette 0.52+ uses (cls, args, kwargs)."""
    try:
        import fastapi.applications as fa
        from starlette.middleware import Middleware
        from starlette.middleware.errors import ServerErrorMiddleware
        from starlette.middleware.exceptions import ExceptionMiddleware
        from starlette.types import ASGIApp
        from fastapi.middleware.asyncexitstack import AsyncExitStackMiddleware
    except ImportError:
        return

    probe = Middleware(type("_Probe", (), {}), only_kw=True)  # type: ignore[misc]
    if len(list(probe)) != 3:
        return

    def build_middleware_stack(self: fa.FastAPI) -> ASGIApp:
        debug = self.debug
        error_handler = None
        exception_handlers = {}
        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = (
            [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
            + self.user_middleware
            + [
                Middleware(
                    ExceptionMiddleware, handlers=exception_handlers, debug=debug
                ),
                Middleware(AsyncExitStackMiddleware),
            ]
        )

        app: ASGIApp = self.router
        for m in reversed(middleware):
            app = m.cls(app, *m.args, **m.kwargs)
        return app

    fa.FastAPI.build_middleware_stack = build_middleware_stack  # type: ignore[method-assign]


_patch_fastapi_middleware_stack_for_starlette()

import pytest


def _xwauth_quiesce_xwlazy_for_native_imports() -> None:
    """Best-effort: global hook + meta_path finder + async worker confuse lxml/signxml (C ext)."""
    import sys

    try:
        from exonware.xwlazy import (
            XWLazy,
            is_global_import_hook_installed,
            uninstall_global_import_hook,
        )

        if is_global_import_hook_installed():
            uninstall_global_import_hook()
        sys.meta_path[:] = [p for p in sys.meta_path if not isinstance(p, XWLazy)]
    except Exception:
        pass
    try:
        _mod = sys.modules.get("exonware._xwlazy_module")
        if _mod is not None:
            flush = getattr(_mod, "_flush_async_io", None)
            if callable(flush):
                flush(timeout_s=3.0)
    except Exception:
        pass


def pytest_configure(config):
    """Third-party pytest plugins may import exonware.xwlazy before conftest env is applied."""
    _xwauth_quiesce_xwlazy_for_native_imports()


@pytest.fixture(autouse=True)
def _xwauth_ensure_no_xwlazy_builtin_hook():
    """Plugins may re-arm xwlazy between tests; native XML stacks need a quiet import surface."""
    _xwauth_quiesce_xwlazy_for_native_imports()
    yield


# Legacy test modules import from ``exonware.xwauth.connector``.
# The connector package is now provided as a compatibility shim.
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockStorageProvider


@pytest.fixture
def mock_storage():
    """Create mock storage provider for testing."""
    return MockStorageProvider()


@pytest.fixture
def auth_config(mock_storage):
    """Create auth configuration for testing."""
    return XWAuthConfig(
        jwt_secret="test-secret-key-for-testing-only",
        storage_provider=mock_storage,
        allow_mock_storage_fallback=True,
    )


@pytest.fixture
def auth(auth_config):
    """Create XWAuth instance for testing."""
    return XWAuth(config=auth_config)
