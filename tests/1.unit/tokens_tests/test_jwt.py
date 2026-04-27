#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/tokens_tests/test_jwt.py
Unit tests for JWT token management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
import time
from datetime import datetime, timedelta
from exonware.xwauth.identity.tokens.jwt import JWTTokenManager
from exonware.xwauth.identity.errors import XWInvalidTokenError, XWExpiredTokenError
@pytest.mark.xwauth_unit

class TestJWTTokenManager:
    """Test JWTTokenManager implementation."""
    @pytest.fixture

    def jwt_manager(self):
        """Create JWTTokenManager instance."""
        return JWTTokenManager(
            secret="test-secret-key-for-testing",
            algorithm="HS256"
        )

    def test_generate_token(self, jwt_manager):
        """Test token generation."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read", "write"],
            expires_in=3600
        )
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_client_credentials(self, jwt_manager):
        """Test token generation for client credentials."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        token = jwt_manager.generate_token(
            user_id=None,
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        assert token is not None

    def test_validate_token(self, jwt_manager):
        """Test token validation."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        payload = jwt_manager.validate_token(token)
        assert payload is not None
        assert payload['sub'] == 'user123'
        assert payload['client_id'] == 'client123'
        assert 'exp' in payload
        assert 'iat' in payload

    def test_validate_token_invalid(self, jwt_manager):
        """Test token validation with invalid token."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        with pytest.raises(XWInvalidTokenError):
            jwt_manager.validate_token("invalid.token.here")

    def test_validate_token_expired(self, jwt_manager):
        """Test token validation with expired token."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        # Generate token with very short expiration
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=-1  # Already expired
        )
        # Wait a moment to ensure expiration
        time.sleep(0.1)
        with pytest.raises(XWExpiredTokenError):
            jwt_manager.validate_token(token)

    def test_get_token_info(self, jwt_manager):
        """Test getting token info without validation."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        info = jwt_manager.get_token_info(token)
        assert info is not None
        assert 'sub' in info
        assert 'client_id' in info

    def test_is_token_expired(self, jwt_manager):
        """Test checking if token is expired."""
        if jwt_manager is None:
            pytest.skip("PyJWT not available")
        # Valid token
        valid_token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=3600
        )
        assert jwt_manager.is_token_expired(valid_token) is False
        # Expired token
        expired_token = jwt_manager.generate_token(
            user_id="user123",
            client_id="client123",
            scopes=["read"],
            expires_in=-1
        )
        time.sleep(0.1)
        assert jwt_manager.is_token_expired(expired_token) is True
