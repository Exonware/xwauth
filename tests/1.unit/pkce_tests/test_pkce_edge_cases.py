#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/pkce_tests/test_pkce_edge_cases.py
Unit tests for PKCE edge cases.
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

    def test_generate_code_verifier_uniqueness(self):
        """Test code verifier uniqueness."""
        verifiers = [PKCE.generate_code_verifier() for _ in range(100)]
        # All verifiers should be unique
        assert len(set(verifiers)) == 100

    def test_generate_code_verifier_length_variation(self):
        """Test code verifier length variation."""
        verifiers = [PKCE.generate_code_verifier() for _ in range(50)]
        # All should be within valid length range
        for verifier in verifiers:
            assert PKCE.CODE_VERIFIER_MIN_LENGTH <= len(verifier) <= PKCE.CODE_VERIFIER_MAX_LENGTH

    def test_generate_code_challenge_consistency(self):
        """Test code challenge generation consistency."""
        verifier = PKCE.generate_code_verifier()
        challenge1 = PKCE.generate_code_challenge(verifier, 'S256')
        challenge2 = PKCE.generate_code_challenge(verifier, 'S256')
        # Same verifier should produce same challenge
        assert challenge1 == challenge2

    def test_generate_code_challenge_different_verifiers(self):
        """Test code challenge with different verifiers."""
        verifier1 = PKCE.generate_code_verifier()
        verifier2 = PKCE.generate_code_verifier()
        challenge1 = PKCE.generate_code_challenge(verifier1, 'S256')
        challenge2 = PKCE.generate_code_challenge(verifier2, 'S256')
        # Different verifiers should produce different challenges
        assert challenge1 != challenge2

    def test_verify_code_challenge_case_sensitivity(self):
        """Test code challenge verification case sensitivity."""
        verifier, challenge = PKCE.generate_code_pair('S256')
        # Should verify correctly
        assert PKCE.verify_code_challenge(verifier, challenge, 'S256') is True
        # Method is normalized to uppercase, so lowercase should also work
        assert PKCE.verify_code_challenge(verifier, challenge, 's256') is True

    def test_verify_code_challenge_plain_method(self):
        """Test code challenge verification with plain method."""
        verifier = PKCE.generate_code_verifier()
        challenge = PKCE.generate_code_challenge(verifier, 'plain')
        assert PKCE.verify_code_challenge(verifier, challenge, 'plain') is True

    def test_validate_code_verifier_boundary_min(self):
        """Test code verifier validation at minimum length."""
        min_length_verifier = "a" * PKCE.CODE_VERIFIER_MIN_LENGTH
        # Should pass validation
        assert PKCE.validate_code_verifier(min_length_verifier) is True

    def test_validate_code_verifier_boundary_max(self):
        """Test code verifier validation at maximum length."""
        max_length_verifier = "a" * PKCE.CODE_VERIFIER_MAX_LENGTH
        # Should pass validation
        assert PKCE.validate_code_verifier(max_length_verifier) is True

    def test_validate_code_verifier_one_below_min(self):
        """Test code verifier validation one below minimum."""
        too_short = "a" * (PKCE.CODE_VERIFIER_MIN_LENGTH - 1)
        with pytest.raises(XWInvalidRequestError):
            PKCE.validate_code_verifier(too_short)

    def test_validate_code_verifier_one_above_max(self):
        """Test code verifier validation one above maximum."""
        too_long = "a" * (PKCE.CODE_VERIFIER_MAX_LENGTH + 1)
        with pytest.raises(XWInvalidRequestError):
            PKCE.validate_code_verifier(too_long)

    def test_generate_code_pair_multiple_times(self):
        """Test generating multiple code pairs."""
        pairs = [PKCE.generate_code_pair('S256') for _ in range(10)]
        # All should be unique
        verifiers = [pair[0] for pair in pairs]
        challenges = [pair[1] for pair in pairs]
        assert len(set(verifiers)) == 10
        assert len(set(challenges)) == 10

    def test_verify_code_challenge_with_wrong_method(self):
        """Test code challenge verification with wrong method."""
        verifier, challenge = PKCE.generate_code_pair('S256')
        # Should fail with wrong method
        with pytest.raises(XWInvalidRequestError):
            PKCE.verify_code_challenge(verifier, challenge, 'plain')
