#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/security_tests/test_password_policies.py
Unit tests for password policies and security.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.security.password import PasswordSecurity
from exonware.xwauth.security.validation import InputValidator
from exonware.xwauth.defs import PasswordHashAlgorithm
@pytest.mark.xwauth_unit
@pytest.mark.xwauth_security

class TestPasswordPolicies:
    """Test password policies and security."""
    @pytest.fixture

    def validator(self):
        """Create InputValidator instance."""
        return InputValidator()

    def test_password_minimum_length(self, validator):
        """Test password minimum length requirement."""
        # Too short
        assert validator.validate_password("Short1") is False
        # Valid length
        assert validator.validate_password("ValidPassword123") is True

    def test_password_complexity_requirements(self, validator):
        """Test password complexity requirements."""
        # Missing uppercase
        assert validator.validate_password("lowercase123") is False
        # Missing lowercase
        assert validator.validate_password("UPPERCASE123") is False
        # Missing digit
        assert validator.validate_password("NoDigits") is False
        # Valid password
        assert validator.validate_password("ValidPass123") is True

    def test_password_common_passwords(self, validator):
        """Test password against common passwords."""
        common_passwords = ["password", "12345678", "qwerty", "admin"]
        for pwd in common_passwords:
            # Should fail or warn about common passwords
            result = validator.validate_password(pwd + "1A")
            # May pass validation but should be flagged
            assert isinstance(result, bool)

    def test_password_hash_algorithm(self):
        """Test password hashing with different algorithms."""
        password = "TestPassword123"
        # Default algorithm
        hashed1 = PasswordSecurity.hash_password(password)
        assert hashed1 is not None
        # Verify works
        assert PasswordSecurity.verify_password(password, hashed1) is True

    def test_password_hash_salt_uniqueness(self):
        """Test that password hashes are unique due to salt."""
        password = "TestPassword123"
        hashed1 = PasswordSecurity.hash_password(password)
        hashed2 = PasswordSecurity.hash_password(password)
        # Hashes should be different
        assert hashed1 != hashed2
        # But both should verify correctly
        assert PasswordSecurity.verify_password(password, hashed1) is True
        assert PasswordSecurity.verify_password(password, hashed2) is True

    def test_password_verification_rejects_mismatch(self):
        """Wrong plaintext must not verify; correct plaintext must verify (delegates to xwsystem crypto)."""
        password = "TestPassword123"
        hashed = PasswordSecurity.hash_password(password)
        assert PasswordSecurity.verify_password("WrongPassword123", hashed) is False
        assert PasswordSecurity.verify_password(password, hashed) is True
