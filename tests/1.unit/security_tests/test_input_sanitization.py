#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/security_tests/test_input_sanitization.py
Unit tests for input sanitization and validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.security.validation import InputValidator
from exonware.xwauth.errors import XWInvalidUserDataError
@pytest.mark.xwauth_unit
@pytest.mark.xwauth_security

class TestInputSanitization:
    """Test input sanitization and validation."""
    @pytest.fixture

    def validator(self):
        """Create InputValidator instance."""
        return InputValidator()

    def test_sanitize_email(self, validator):
        """Test email sanitization."""
        email = validator.sanitize_email("  TEST@EXAMPLE.COM  ")
        assert email == "test@example.com"

    def test_sanitize_email_invalid(self, validator):
        """Test email sanitization with invalid email."""
        # sanitize_email just sanitizes, doesn't validate
        result = validator.sanitize_email("invalid-email")
        assert result == "invalid-email"  # Just lowercased and trimmed

    def test_sanitize_string(self, validator):
        """Test string sanitization."""
        result = validator.sanitize_string("  Test String  ")
        assert result == "Test String"

    def test_sanitize_string_remove_html(self, validator):
        """Test string sanitization removes HTML."""
        result = validator.sanitize_string("<script>alert('xss')</script>Test")
        assert "<script>" not in result
        assert "Test" in result

    def test_sanitize_string_max_length(self, validator):
        """Test string sanitization with max length."""
        long_string = "a" * 1000
        result = validator.sanitize_string(long_string, max_length=100)
        assert len(result) <= 100

    def test_validate_redirect_uri_whitelist(self, validator):
        """Test redirect URI whitelist validation."""
        # Valid URIs
        assert validator.validate_redirect_uri("https://example.com/callback") is True
        assert validator.validate_redirect_uri("http://localhost:3000/callback") is True
        # Invalid URIs
        assert validator.validate_redirect_uri("javascript:alert('xss')") is False
        assert validator.validate_redirect_uri("data:text/html,<script>") is False

    def test_validate_scope(self, validator):
        """Test scope validation."""
        # Valid scopes
        assert validator.validate_scope("read") is True
        assert validator.validate_scope("read write") is True
        # Invalid scopes
        assert validator.validate_scope("") is False
        assert validator.validate_scope("read<script>") is False

    def test_validate_state_parameter(self, validator):
        """Test state parameter validation."""
        # Valid state
        assert validator.validate_state("abc123") is True
        assert validator.validate_state("state_123") is True
        # Invalid state
        assert validator.validate_state("") is False
        assert validator.validate_state("state<script>") is False
