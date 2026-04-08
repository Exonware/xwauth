# exonware/xwauth/src/exonware/xwauth/connectors/__init__.py
"""Bridge contracts for attaching xwauth to login (in-process lib vs remote API). See REF_41 §6."""

from __future__ import annotations

from .login_bridge import LoginBridgeMode, LoginRemoteConfig, load_login_package

__all__ = ["LoginBridgeMode", "LoginRemoteConfig", "load_login_package"]
