#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/security_tests/test_password_security.py
Unit tests for password security.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.security.password import PasswordSecurity
from exonware.xwauth.defs import PasswordHashAlgorithm
@pytest.mark.xwauth_unit

class TestPasswordSecurity:
    """Test PasswordSecurity implementation."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = PasswordSecurity.hash_password(password)
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Should be hashed

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hashed1 = PasswordSecurity.hash_password(password)
        hashed2 = PasswordSecurity.hash_password(password)
        # Hashes should be different due to salt
        assert hashed1 != hashed2

    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = PasswordSecurity.hash_password(password)
        assert PasswordSecurity.verify_password(password, hashed) is True
        assert PasswordSecurity.verify_password("wrongpassword", hashed) is False
    @pytest.mark.asyncio

    async def test_check_password_breach(self):
        """Test password breach detection (async)."""
        result = await PasswordSecurity.check_password_breach("testpassword123")
        assert isinstance(result, bool)
