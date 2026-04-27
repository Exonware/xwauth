#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/0.core/test_core_installation.py
Core Installation Tests
Fast tests to verify basic installation and imports.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.defs import GrantType, TokenType, SessionStatus, UserStatus
from exonware.xwauth.identity.errors import XWAuthError, XWOAuthError, XWTokenError, XWProviderError
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.storage.interface import IStorageProvider
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockStorageProvider
@pytest.mark.xwauth_core

def test_imports():
    """Test that all core imports work."""
    assert XWAuth is not None
    assert XWAuthError is not None
    assert XWOAuthError is not None
    assert XWTokenError is not None
    assert XWProviderError is not None
    assert IStorageProvider is not None
@pytest.mark.xwauth_core

def test_enums():
    """Test that enums are defined."""
    assert GrantType.AUTHORIZATION_CODE == "authorization_code"
    assert TokenType.BEARER == "Bearer"
    assert SessionStatus.ACTIVE == "active"
    assert UserStatus.ACTIVE == "active"
@pytest.mark.xwauth_core

def test_config_creation():
    """Test configuration creation."""
    config = XWAuthConfig(jwt_secret="test-secret", allow_mock_storage_fallback=True)
    assert config.jwt_secret == "test-secret"
    assert config.jwt_algorithm == "HS256"
    assert config.enable_pkce is True
@pytest.mark.xwauth_core

def test_mock_storage():
    """Test mock storage provider."""
    storage = MockStorageProvider()
    assert storage is not None
@pytest.mark.xwauth_core

def test_xwauth_initialization():
    """Test XWAuth initialization."""
    config = XWAuthConfig(jwt_secret="test-secret", allow_mock_storage_fallback=True)
    auth = XWAuth(config=config)
    assert auth is not None
    assert auth.config is not None
    assert auth.storage is not None
@pytest.mark.xwauth_core

def test_xwauth_requires_config():
    """XWAuth() with no configuration must refuse to start (fail closed)."""
    with pytest.raises(XWAuthError) as exc_info:
        XWAuth()
    # No compat shim: the real facade raises XWConfigError from the
    # storage-provider gate. The message mentions "storage" or "config"; we
    # only assert the fail-closed contract, not the wording.
    msg = str(exc_info.value).lower()
    assert any(tok in msg for tok in ("storage", "config")), (
        f"expected fail-closed storage/config gate, got: {exc_info.value!r}"
    )
