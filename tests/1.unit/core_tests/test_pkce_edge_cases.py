#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/core_tests/test_pkce_edge_cases.py
Unit tests for PKCE edge cases and boundary conditions.
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

class TestPKCEEdgeCases:
    """Test PKCE edge cases."""

    def test_code_verifier_minimum_length(self):
        """Test code verifier minimum length."""
        # Generate multiple verifiers and check they meet minimum
        for _ in range(10):
            verifier = PKCE.generate_code_verifier()
            assert len(verifier) >= PKCE.CODE_VERIFIER_MIN_LENGTH

    def test_code_verifier_maximum_length(self):
        """Test code verifier maximum length."""
        # Generate multiple verifiers and check they meet maximum
        for _ in range(10):
            verifier = PKCE.generate_code_verifier()
            assert len(verifier) <= PKCE.CODE_VERIFIER_MAX_LENGTH

    def test_code_verifier_characters(self):
        """Test code verifier character set."""
        verifier = PKCE.generate_code_verifier()
        # Should only contain URL-safe characters
        import string
        allowed_chars = string.ascii_letters + string.digits + '-._~'
        assert all(c in allowed_chars for c in verifier)

    def test_code_challenge_consistency(self):
        """Test code challenge generation consistency."""
        verifier = PKCE.generate_code_verifier()
        challenge1 = PKCE.generate_code_challenge(verifier, 'S256')
        challenge2 = PKCE.generate_code_challenge(verifier, 'S256')
        # Same verifier should produce same challenge
        assert challenge1 == challenge2

    def test_code_challenge_different_methods(self):
        """Test code challenge with different methods."""
        verifier = PKCE.generate_code_verifier()
        challenge_s256 = PKCE.generate_code_challenge(verifier, 'S256')
        challenge_plain = PKCE.generate_code_challenge(verifier, 'plain')
        # S256 should be different from plain
        assert challenge_s256 != challenge_plain
        assert challenge_plain == verifier

    def test_verify_code_challenge_case_sensitive(self):
        """Test code challenge verification is case sensitive."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'S256')
        # Should verify correctly
        assert PKCE.verify_code_challenge(verifier, challenge, 'S256') is True
        # Case change should fail
        try:
            PKCE.verify_code_challenge(verifier, challenge.lower(), 'S256')
            assert False, "Should fail with case change"
        except XWInvalidRequestError:
            pass

    def test_code_verifier_entropy(self):
        """Test code verifier has sufficient entropy."""
        verifiers = [PKCE.generate_code_verifier() for _ in range(100)]
        # All should be unique
        assert len(set(verifiers)) == 100

    def test_code_challenge_length(self):
        """Test code challenge length."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'S256')
        # S256 challenge should be base64url encoded (43 chars for 32 bytes)
        assert len(challenge) > 0
        assert len(challenge) <= 128  # Reasonable maximum
