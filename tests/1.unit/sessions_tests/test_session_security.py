#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/sessions_tests/test_session_security.py
Unit tests for session security features.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.sessions.security import SessionSecurity
from exonware.xwauth.identity.errors import XWSessionError, XWInvalidRequestError
@pytest.mark.xwauth_unit
@pytest.mark.xwauth_security

class TestSessionSecurity:
    """Test SessionSecurity implementation."""
    @pytest.fixture

    def security(self):
        """Create SessionSecurity instance."""
        return SessionSecurity()

    def test_generate_csrf_token(self, security):
        """Test CSRF token generation."""
        token = security.generate_csrf_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_csrf_token_unique(self, security):
        """Test that CSRF tokens are unique."""
        token1 = security.generate_csrf_token()
        token2 = security.generate_csrf_token()
        assert token1 != token2

    def test_validate_csrf_token(self, security):
        """Test CSRF token validation."""
        token = security.generate_csrf_token()
        # Should not raise
        assert security.validate_csrf_token(token, token) is True

    def test_validate_csrf_token_mismatch(self, security):
        """Test CSRF token validation with mismatch."""
        token1 = security.generate_csrf_token()
        token2 = security.generate_csrf_token()
        with pytest.raises(XWSessionError):
            security.validate_csrf_token(token1, token2)

    def test_validate_csrf_token_empty(self, security):
        """Test CSRF token validation with empty tokens."""
        with pytest.raises(XWInvalidRequestError):
            security.validate_csrf_token("", "valid_token")

    def test_validate_csrf_token_none(self, security):
        """Test CSRF token validation with None."""
        with pytest.raises((XWInvalidRequestError, TypeError)):
            security.validate_csrf_token(None, "valid_token")
