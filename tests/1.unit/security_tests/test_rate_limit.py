#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/security_tests/test_rate_limit.py
Unit tests for rate limiting.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
import time
from exonware.xwauth.identity.security.rate_limit import RateLimiter
@pytest.mark.xwauth_unit

class TestRateLimiter:
    """Test RateLimiter implementation."""
    @pytest.fixture

    def rate_limiter(self):
        """Create RateLimiter instance."""
        return RateLimiter(
            requests_per_minute=5,
            requests_per_hour=10
        )

    def test_check_rate_limit_within_limits(self, rate_limiter):
        """Test rate limit check within limits."""
        identifier = "test_client"
        # Make 5 requests (within limit)
        for i in range(5):
            result = rate_limiter.check_rate_limit(identifier)
            assert result is True

    def test_check_rate_limit_exceeded(self, rate_limiter):
        """Test rate limit check when exceeded."""
        identifier = "test_client"
        # Make requests up to limit
        for i in range(5):
            rate_limiter.check_rate_limit(identifier)
        # Next request should be rate limited
        result = rate_limiter.check_rate_limit(identifier)
        assert result is False

    def test_check_rate_limit_different_identifiers(self, rate_limiter):
        """Test rate limit with different identifiers."""
        # Each identifier should have separate limits
        result1 = rate_limiter.check_rate_limit("client1")
        result2 = rate_limiter.check_rate_limit("client2")
        assert result1 is True
        assert result2 is True
