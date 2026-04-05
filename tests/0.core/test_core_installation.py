#!/usr/bin/env python3
"""
#exonware/xwauth/tests/0.core/test_core_installation.py
Core Installation Tests
Fast tests to verify basic installation and imports.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

from __future__ import annotations
import sys
from pathlib import Path
# Add src to path for testing
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
import pytest
from exonware.xwauth import (
    XWAuth,
    XWAuthError,
    XWOAuthError,
    XWTokenError,
    XWProviderError,
    IStorageProvider,
    GrantType,
    TokenType,
    SessionStatus,
    UserStatus,
)
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.storage.mock import MockStorageProvider
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
    config = XWAuthConfig(jwt_secret="test-secret")
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
    config = XWAuthConfig(jwt_secret="test-secret")
    auth = XWAuth(config=config)
    assert auth is not None
    assert auth.config is not None
    assert auth.storage is not None
@pytest.mark.xwauth_core

def test_xwauth_requires_config():
    """Test that XWAuth requires configuration."""
    with pytest.raises(XWAuthError) as exc_info:
        XWAuth()
    assert "CONFIG_REQUIRED" in str(exc_info.value.error_code or "")
