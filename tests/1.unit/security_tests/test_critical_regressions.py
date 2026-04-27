#!/usr/bin/env python3
"""
#exonware/xwauth.connect/tests/1.unit/security_tests/test_critical_regressions.py
Regression tests for previously identified critical auth flaws.
"""

import time

import jwt
import pytest

from exonware.xwsystem.security.errors import AuthenticationError, TokenExpiredError
from exonware.xwauth.connect.providers.xwsystem_providers import JWTProvider


# Minimal attestation that a test fixture has "verified" the subject. In
# production this field names the upstream authenticator (password backend,
# OIDC broker, …) that did the real verification. See the JWTProvider
# security contract.
_TEST_VERIFIED_BY = {"_verified_by": "test_fixture"}


@pytest.mark.xwauth_security
class TestJWTProviderCriticalRegressions:
    """Guard rails for claim injection and unsafe refresh behavior."""

    @pytest.mark.asyncio
    async def test_authenticate_rejects_reserved_claim_override(self):
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=300,
        )
        now = time.time()
        token_info = await provider.authenticate(
            {
                "user_id": "safe-user",
                "password": "ignored",
                "sub": "attacker-user",
                "exp": now + 999999,
                "iat": now - 5000,
                "roles": ["admin"],
                **_TEST_VERIFIED_BY,
            }
        )

        payload = jwt.decode(
            token_info.access_token,
            "critical-regression-secret",
            algorithms=["HS256"],
            issuer="https://issuer.example",
            audience="audience.example",
        )
        assert payload["sub"] == "safe-user"
        assert payload["roles"] == ["admin"]
        assert payload.get("token_use") == "access"
        assert payload["iat"] >= now
        assert payload["exp"] <= now + 400
        # The verification marker MUST NOT leak into the signed token.
        assert "_verified_by" not in payload

    @pytest.mark.asyncio
    async def test_authenticate_requires_verified_by_field_auth_bypass_regression(self):
        """Guard: JWTProvider must refuse token-minting for unverified subjects.

        Regression test for the 2026-04-20 critical security finding: prior
        code accepted ``{"user_id": <anything>}`` and immediately minted a
        signed JWT for that subject, turning any HTTP endpoint that invoked
        this method into a token-forgery primitive. The fix requires callers
        to pass ``_verified_by`` attesting to upstream verification.
        """
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=300,
        )

        # No _verified_by → must raise.
        with pytest.raises(AuthenticationError) as exc_info:
            await provider.authenticate({"user_id": "attacker"})
        assert "_verified_by" in str(exc_info.value)

        # Empty-string _verified_by → still raises (must be non-empty).
        with pytest.raises(AuthenticationError):
            await provider.authenticate(
                {"user_id": "attacker", "_verified_by": "   "}
            )

        # Non-string _verified_by (e.g. True) → raises.
        with pytest.raises(AuthenticationError):
            await provider.authenticate(
                {"user_id": "attacker", "_verified_by": True}
            )

        # Missing user_id still fails with the original error, independent of
        # the new gate.
        with pytest.raises(AuthenticationError):
            await provider.authenticate(
                {"_verified_by": "test_fixture"}
            )

        # Only the combination of user_id + non-empty string _verified_by
        # succeeds.
        token_info = await provider.authenticate(
            {"user_id": "verified-user", "_verified_by": "test_fixture"}
        )
        assert token_info.access_token
        payload = jwt.decode(
            token_info.access_token,
            "critical-regression-secret",
            algorithms=["HS256"],
            issuer="https://issuer.example",
            audience="audience.example",
        )
        assert payload["sub"] == "verified-user"
        assert payload.get("token_use") == "access"
        assert "_verified_by" not in payload

    @pytest.mark.asyncio
    async def test_refresh_rejects_minted_access_token(self):
        """Access tokens (token_use=access) must not be accepted by refresh_token."""
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=300,
        )
        minted = await provider.authenticate(
            {"user_id": "u1", "_verified_by": "test_fixture"},
        )
        with pytest.raises(AuthenticationError, match="not eligible"):
            await provider.refresh_token(minted.access_token)

    @pytest.mark.asyncio
    async def test_refresh_rejects_explicit_access_token_use(self):
        """JWTs with token_use=access are never refresh inputs."""
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=60,
        )
        access_like = jwt.encode(
            {
                "sub": "safe-user",
                "token_use": "access",
                "iss": "https://issuer.example",
                "aud": "audience.example",
                "iat": int(time.time()) - 10,
                "exp": int(time.time()) + 120,
            },
            "critical-regression-secret",
            algorithm="HS256",
        )
        with pytest.raises(AuthenticationError, match="not eligible"):
            await provider.refresh_token(access_like)

    @pytest.mark.asyncio
    async def test_refresh_rejects_expired_token(self):
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=60,
        )
        expired_refresh = jwt.encode(
            {
                "sub": "safe-user",
                "token_use": "refresh",
                "iss": "https://issuer.example",
                "aud": "audience.example",
                "iat": int(time.time()) - 120,
                "exp": int(time.time()) - 30,
            },
            "critical-regression-secret",
            algorithm="HS256",
        )

        with pytest.raises(TokenExpiredError):
            await provider.refresh_token(expired_refresh)

    @pytest.mark.asyncio
    async def test_refresh_drops_non_allowlisted_claims(self):
        provider = JWTProvider(
            secret_key="critical-regression-secret",
            issuer="https://issuer.example",
            audience="audience.example",
            expiration_time=60,
        )
        refresh_input = jwt.encode(
            {
                "sub": "safe-user",
                "username": "safe-user",
                "roles": ["reader"],
                "token_use": "refresh",
                "admin": True,
                "iss": "https://issuer.example",
                "aud": "audience.example",
                "iat": int(time.time()) - 10,
                "exp": int(time.time()) + 120,
            },
            "critical-regression-secret",
            algorithm="HS256",
        )

        refreshed = await provider.refresh_token(refresh_input)
        payload = jwt.decode(
            refreshed.access_token,
            "critical-regression-secret",
            algorithms=["HS256"],
            issuer="https://issuer.example",
            audience="audience.example",
        )
        assert payload["sub"] == "safe-user"
        assert payload["roles"] == ["reader"]
        assert "admin" not in payload
        assert "token_use" not in payload
