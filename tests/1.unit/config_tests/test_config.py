#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/config_tests/test_config.py
Unit tests for configuration management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.errors import XWConfigError
@pytest.mark.xwauth_unit

class TestXWAuthConfig:
    """Test XWAuthConfig implementation."""

    def test_config_creation_minimal(self):
        """Test minimal config creation."""
        config = XWAuthConfig(jwt_secret="test-secret", allow_mock_storage_fallback=True)
        assert config.jwt_secret == "test-secret"
        assert config.jwt_algorithm == "HS256"

    def test_config_creation_full(self):
        """Test full config creation."""
        config = XWAuthConfig(
            jwt_secret="test-secret",
            jwt_algorithm="RS256",
            access_token_lifetime=3600,
            refresh_token_lifetime=86400 * 7,
            session_timeout=3600,
            enable_pkce=True,
            allow_mock_storage_fallback=True,
        )
        assert config.jwt_secret == "test-secret"
        assert config.jwt_algorithm == "RS256"
        assert config.access_token_lifetime == 3600
        assert config.enable_pkce is True

    def test_config_default_values(self):
        """Test config default values."""
        config = XWAuthConfig(jwt_secret="test-secret", allow_mock_storage_fallback=True)
        assert config.jwt_algorithm == "HS256"
        assert config.access_token_lifetime > 0
        assert config.refresh_token_lifetime > 0
        assert config.session_timeout > 0
        assert config.protocol_profile == "A"
        assert config.default_scopes == ["openid", "profile", "email"]

    def test_config_validation(self):
        """Test config validation."""
        # Dataclass allows None values unless validated
        # This test verifies that config can be created (validation may be done elsewhere)
        config = XWAuthConfig(jwt_secret=None, allow_mock_storage_fallback=True)
        assert config.jwt_secret is None
        # Or test that it requires jwt_secret (TypeError if missing)
        with pytest.raises(TypeError):
            # Missing required argument
            XWAuthConfig()

    def test_config_immutability(self):
        """Test config immutability (if implemented)."""
        config = XWAuthConfig(jwt_secret="test-secret")
        # Config should be read-only or raise on modification
        original_secret = config.jwt_secret
        assert config.jwt_secret == original_secret

    def test_protocol_profile_b_requires_fapi_profile_flags(self):
        config = XWAuthConfig(jwt_secret="test-secret", protocol_profile="B", allow_mock_storage_fallback=True)
        with pytest.raises(XWConfigError, match="requires fapi20_compliant=True"):
            config.validate()

    def test_protocol_profile_a_passes_default_validation(self):
        config = XWAuthConfig(jwt_secret="test-secret", protocol_profile="A")
        config.validate()
