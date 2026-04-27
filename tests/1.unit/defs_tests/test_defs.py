#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/defs_tests/test_defs.py
Unit tests for definitions and enums.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.defs import (
    GrantType,
    ResponseType,
    TokenType,
    SessionStatus,
    UserStatus,
    ProviderType,
    PasswordHashAlgorithm
)
@pytest.mark.xwauth_unit

class TestDefinitions:
    """Test definitions and enums."""

    def test_grant_type_enum(self):
        """Test GrantType enum."""
        assert GrantType.AUTHORIZATION_CODE is not None
        assert GrantType.CLIENT_CREDENTIALS is not None
        assert GrantType.RESOURCE_OWNER_PASSWORD is not None
        assert GrantType.DEVICE_CODE is not None
        assert GrantType.REFRESH_TOKEN is not None

    def test_grant_type_values(self):
        """Test GrantType values."""
        assert GrantType.AUTHORIZATION_CODE == "authorization_code"
        assert GrantType.CLIENT_CREDENTIALS == "client_credentials"
        assert GrantType.RESOURCE_OWNER_PASSWORD == "password"
        assert GrantType.DEVICE_CODE == "urn:ietf:params:oauth:grant-type:device_code"
        assert GrantType.REFRESH_TOKEN == "refresh_token"

    def test_response_type_enum(self):
        """Test ResponseType enum."""
        assert ResponseType.CODE is not None
        assert ResponseType.TOKEN is not None

    def test_response_type_values(self):
        """Test ResponseType values."""
        assert ResponseType.CODE == "code"
        assert ResponseType.TOKEN == "token"

    def test_token_type_enum(self):
        """Test TokenType enum."""
        assert TokenType.JWT is not None
        assert TokenType.OPAQUE is not None

    def test_token_type_values(self):
        """Test TokenType values."""
        assert TokenType.JWT == "JWT"
        assert TokenType.OPAQUE == "opaque"

    def test_session_status_enum(self):
        """Test SessionStatus enum."""
        assert SessionStatus.ACTIVE is not None
        assert SessionStatus.EXPIRED is not None
        assert SessionStatus.REVOKED is not None

    def test_session_status_values(self):
        """Test SessionStatus values."""
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.EXPIRED == "expired"
        assert SessionStatus.REVOKED == "revoked"

    def test_user_status_enum(self):
        """Test UserStatus enum."""
        assert UserStatus.ACTIVE is not None
        assert UserStatus.SUSPENDED is not None
        assert UserStatus.DELETED is not None

    def test_user_status_values(self):
        """Test UserStatus values."""
        assert UserStatus.ACTIVE == "active"
        assert UserStatus.SUSPENDED == "suspended"
        assert UserStatus.DELETED == "deleted"

    def test_provider_type_enum(self):
        """Test ProviderType enum."""
        assert ProviderType.SOCIAL is not None
        assert ProviderType.ENTERPRISE is not None
        assert ProviderType.CHINESE is not None

    def test_provider_type_values(self):
        """Test ProviderType values."""
        assert ProviderType.SOCIAL == "social"
        assert ProviderType.ENTERPRISE == "enterprise"
        assert ProviderType.CHINESE == "chinese"

    def test_stripe_connect_slug_is_stripe(self):
        """Stripe provider uses slug ``stripe``; enum member remains STRIPE_CONNECT."""
        assert ProviderType.STRIPE_CONNECT == "stripe"

    def test_password_hash_algorithm_enum(self):
        """Test PasswordHashAlgorithm enum."""
        assert PasswordHashAlgorithm.BCRYPT is not None
        assert PasswordHashAlgorithm.ARGON2 is not None
        assert PasswordHashAlgorithm.SCRYPT is not None

    def test_password_hash_algorithm_values(self):
        """Test PasswordHashAlgorithm values."""
        assert PasswordHashAlgorithm.BCRYPT == "bcrypt"
        assert PasswordHashAlgorithm.ARGON2 == "argon2"
        assert PasswordHashAlgorithm.SCRYPT == "scrypt"
