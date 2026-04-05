#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/core_tests/test_pkce.py
Unit tests for PKCE implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.core.pkce import PKCE
from exonware.xwauth.errors import XWInvalidRequestError
@pytest.mark.xwauth_unit

class TestPKCE:
    """Test PKCE implementation."""

    def test_generate_code_verifier(self):
        """Test code verifier generation."""
        verifier = PKCE.generate_code_verifier()
        assert verifier is not None
        assert len(verifier) >= PKCE.CODE_VERIFIER_MIN_LENGTH
        assert len(verifier) <= PKCE.CODE_VERIFIER_MAX_LENGTH

    def test_generate_code_challenge_s256(self):
        """Test code challenge generation with S256."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'S256')
        assert challenge is not None
        assert challenge != verifier  # Should be hashed
        assert len(challenge) > 0

    def test_generate_code_challenge_plain(self):
        """Test code challenge generation with plain method."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'plain')
        assert challenge == verifier  # Should be same for plain

    def test_generate_code_challenge_invalid_method(self):
        """Test code challenge generation with invalid method."""
        verifier = PKCE.generate_code_verifier()
        with pytest.raises(XWInvalidRequestError):
            PKCE.generate_code_challenge(verifier, 'invalid')

    def test_generate_code_pair(self):
        """Test code verifier and challenge pair generation."""
        verifier, challenge = PKCE.generate_code_pair('S256')
        assert verifier is not None
        assert challenge is not None
        assert len(verifier) >= PKCE.CODE_VERIFIER_MIN_LENGTH

    def test_validate_code_verifier(self):
        """Test code verifier validation."""
        verifier = PKCE.generate_code_verifier()
        # Should not raise
        assert PKCE.validate_code_verifier(verifier) is True

    def test_validate_code_verifier_too_short(self):
        """Test code verifier validation with too short verifier."""
        with pytest.raises(XWInvalidRequestError):
            PKCE.validate_code_verifier('short')

    def test_validate_code_verifier_too_long(self):
        """Test code verifier validation with too long verifier."""
        long_verifier = 'a' * (PKCE.CODE_VERIFIER_MAX_LENGTH + 1)
        with pytest.raises(XWInvalidRequestError):
            PKCE.validate_code_verifier(long_verifier)

    def test_validate_code_verifier_empty(self):
        """Test code verifier validation with empty string."""
        with pytest.raises(XWInvalidRequestError):
            PKCE.validate_code_verifier('')

    def test_verify_code_challenge(self):
        """Test code challenge verification."""
        verifier, challenge = PKCE.generate_code_pair('S256')
        # Should not raise
        assert PKCE.verify_code_challenge(verifier, challenge, 'S256') is True

    def test_verify_code_challenge_mismatch(self):
        """Test code challenge verification with mismatched verifier."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'S256')
        wrong_verifier = PKCE.generate_code_verifier()
        with pytest.raises(XWInvalidRequestError):
            PKCE.verify_code_challenge(wrong_verifier, challenge, 'S256')
