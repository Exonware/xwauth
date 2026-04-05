#exonware/xwauth/tests/0.core/test_import.py
"""
Core import and REF_14 key-code sanity tests for xwauth (XWOAuth).
Verifies public API (REF_15_API) and key code (REF_14_DX) are importable.
Per REF_51_TEST layer 0: fast, high-value checks; import sanity.
"""

import pytest
@pytest.mark.xwauth_core


class TestImportSanity:
    """Import sanity: REF_15 main entry points and REF_14 key code."""

    def test_facade_and_config_import(self):
        """REF_14: XWAuth(config=XWAuthConfig(...))."""
        from exonware.xwauth import XWAuth, XWAuthConfig
        config = XWAuthConfig(jwt_secret="test-secret-for-ref14")
        auth = XWAuth(config=config)
        assert auth is not None

    def test_facade_methods_exist(self):
        """REF_15: authorize, token, introspect_token, revoke_token."""
        from exonware.xwauth import XWAuth, XWAuthConfig
        config = XWAuthConfig(jwt_secret="test-secret")
        auth = XWAuth(config=config)
        assert hasattr(auth, "authorize")
        assert hasattr(auth, "token")
        assert hasattr(auth, "introspect_token")
        assert hasattr(auth, "revoke_token")
