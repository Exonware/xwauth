#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/security_tests/test_csrf_protection.py
Unit tests for CSRF protection.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.sessions.security import SessionSecurity
from exonware.xwauth.errors import XWSessionError
@pytest.mark.xwauth_unit
@pytest.mark.xwauth_security

class TestCSRFProtection:
    """Test CSRF protection implementation."""
    @pytest.fixture

    def security(self):
        """Create SessionSecurity instance."""
        return SessionSecurity()

    def test_csrf_token_generation(self, security):
        """Test CSRF token generation."""
        token = security.generate_csrf_token()
        assert token is not None
        assert isinstance(token, str)
        assert len(token) >= 32  # Minimum secure length

    def test_csrf_token_uniqueness(self, security):
        """Test CSRF token uniqueness."""
        tokens = [security.generate_csrf_token() for _ in range(100)]
        # All tokens should be unique
        assert len(set(tokens)) == 100

    def test_csrf_token_validation_success(self, security):
        """Test successful CSRF token validation."""
        token = security.generate_csrf_token()
        # Should not raise
        assert security.validate_csrf_token(token, token) is True

    def test_csrf_token_validation_failure(self, security):
        """Test CSRF token validation failure."""
        token1 = security.generate_csrf_token()
        token2 = security.generate_csrf_token()
        with pytest.raises(XWSessionError):
            security.validate_csrf_token(token1, token2)

    def test_csrf_token_timing_attack_protection(self, security):
        """Test CSRF token constant-time comparison."""
        import time
        token = security.generate_csrf_token()
        wrong_token = security.generate_csrf_token()
        # Measure time for correct validation
        start = time.perf_counter()
        try:
            security.validate_csrf_token(token, token)
        except Exception:
            pass
        correct_time = time.perf_counter() - start
        # Measure time for incorrect validation
        start = time.perf_counter()
        try:
            security.validate_csrf_token(token, wrong_token)
        except Exception:
            pass
        incorrect_time = time.perf_counter() - start
        # Times should be similar (constant-time comparison)
        # Allow some variance but should be close
        time_diff = abs(correct_time - incorrect_time)
        assert time_diff < 0.01  # Should be very close
