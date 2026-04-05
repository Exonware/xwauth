#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/jose_tests/conftest.py
JOSE Tests Fixtures
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth import XWAuth
from exonware.xwauth.config.config import XWAuthConfig
from exonware.xwauth.storage.mock import MockStorageProvider
from exonware.xwauth.jose.jwt import JWTManager
from exonware.xwauth.jose.jws import JWSManager
from exonware.xwauth.jose.jwk import JWKManager
from exonware.xwauth.jose.jwa import JWAManager
from exonware.xwauth.jose.key_manager import JOSEKeyManager
@pytest.fixture

def mock_storage():
    """Create mock storage provider."""
    return MockStorageProvider()
@pytest.fixture

def auth():
    """Create XWAuth instance for JOSE tests."""
    config = XWAuthConfig(
        jwt_secret="test-secret-key-for-jwt-testing"
    )
    storage = MockStorageProvider()
    return XWAuth(config=config, storage=storage)
@pytest.fixture

def jwt_manager(auth):
    """Create JWTManager instance."""
    return JWTManager(auth)
@pytest.fixture

def jws_manager(auth):
    """Create JWSManager instance."""
    return JWSManager(auth)
@pytest.fixture

def jwk_manager(auth):
    """Create JWKManager instance."""
    return JWKManager(auth)
@pytest.fixture

def jwa_manager():
    """Create JWAManager instance."""
    return JWAManager()
@pytest.fixture

def jose_key_manager(auth):
    """Create JOSEKeyManager instance."""
    return JOSEKeyManager(auth)
