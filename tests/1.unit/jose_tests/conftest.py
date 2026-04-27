#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/jose_tests/conftest.py
JOSE Tests Fixtures
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.storage.mock import MockStorageProvider
from exonware.xwauth.identity.jose.jwt import JWTManager
from exonware.xwauth.identity.jose.jws import JWSManager
from exonware.xwauth.identity.jose.jwk import JWKManager
from exonware.xwauth.identity.jose.jwa import JWAManager
from exonware.xwauth.identity.jose.key_manager import JOSEKeyManager
@pytest.fixture

def mock_storage():
    """Create mock storage provider."""
    return MockStorageProvider()
@pytest.fixture

def auth():
    """Create XWAuth instance for JOSE tests."""
    config = XWAuthConfig(
        jwt_secret="test-secret-key-for-jwt-testing",
        allow_mock_storage_fallback=True,
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
