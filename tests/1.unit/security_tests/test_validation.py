#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/security_tests/test_validation.py
Unit tests for input validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.security.validation import InputValidator
@pytest.mark.xwauth_unit

class TestInputValidator:
    """Test InputValidator implementation."""
    @pytest.fixture

    def validator(self):
        """Create InputValidator instance."""
        return InputValidator()

    def test_validate_email_valid(self, validator):
        """Test email validation with valid emails."""
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("user.name@example.co.uk") is True

    def test_validate_email_invalid(self, validator):
        """Test email validation with invalid emails."""
        assert validator.validate_email("invalid") is False
        assert validator.validate_email("@example.com") is False
        assert validator.validate_email("test@") is False
        assert validator.validate_email("") is False

    def test_validate_password_valid(self, validator):
        """Test password validation with valid passwords."""
        assert validator.validate_password("Test1234") is True
        assert validator.validate_password("StrongP@ssw0rd") is True

    def test_validate_password_invalid(self, validator):
        """Test password validation with invalid passwords."""
        assert validator.validate_password("short") is False  # Too short
        assert validator.validate_password("nouppercase123") is False  # No uppercase
        assert validator.validate_password("NOLOWERCASE123") is False  # No lowercase
        assert validator.validate_password("NoDigits") is False  # No digits
        assert validator.validate_password("") is False

    def test_validate_redirect_uri_valid(self, validator):
        """Test redirect URI validation with valid URIs."""
        assert validator.validate_redirect_uri("https://example.com/callback") is True
        assert validator.validate_redirect_uri("http://localhost:3000/callback") is True

    def test_validate_redirect_uri_invalid(self, validator):
        """Test redirect URI validation with invalid URIs."""
        assert validator.validate_redirect_uri("not-a-url") is False
        assert validator.validate_redirect_uri("") is False
        assert validator.validate_redirect_uri("//example.com") is False
