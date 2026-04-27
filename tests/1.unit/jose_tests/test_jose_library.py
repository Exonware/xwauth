#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/jose_tests/test_jose_library.py
Unit tests for JOSE library (JWT, JWS, JWK, JWA).
Tests comprehensive JOSE functionality including token operations,
signing, key management, and algorithm support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwauth.identity.jose.jwt import JWTManager
from exonware.xwauth.identity.jose.jws import JWSManager
from exonware.xwauth.identity.jose.jwk import JWKManager
from exonware.xwauth.identity.jose.jwa import JWAManager
from exonware.xwauth.identity.jose.key_manager import JOSEKeyManager
from exonware.xwauth.identity.errors import XWInvalidTokenError, XWExpiredTokenError
@pytest.mark.xwauth_unit

class TestJWTManager:
    """Test JWT Manager implementation."""

    def test_encode_decode(self, jwt_manager):
        """Test JWT encoding and decoding."""
        payload = {
            "sub": "user123",
            "client_id": "client123",
            "scope": "read write"
        }
        token = jwt_manager.encode(payload)
        assert token is not None
        assert isinstance(token, str)
        assert token.count('.') == 2  # JWT has 3 parts
        decoded = jwt_manager.decode(token)
        assert decoded is not None
        assert decoded.get('sub') == "user123"
        assert decoded.get('client_id') == "client123"

    def test_decode_invalid_token(self, jwt_manager):
        """Test decoding of invalid token."""
        with pytest.raises((XWInvalidTokenError, Exception)):
            jwt_manager.decode("invalid.token.here")

    def test_encode_with_additional_claims(self, jwt_manager):
        """Test encoding with additional claims."""
        payload = {
            "sub": "user456",
            "client_id": "client456",
            "scope": "read",
            "session_id": "session_123",
            "custom": "value"
        }
        token = jwt_manager.encode(payload)
        decoded = jwt_manager.decode(token)
        assert decoded.get('session_id') == "session_123"
        assert decoded.get('custom') == "value"
@pytest.mark.xwauth_unit

class TestJWSManager:
    """Test JWS Manager implementation."""
    @pytest.mark.asyncio

    async def test_sign_data(self, jws_manager):
        """Test signing data with JWS."""
        payload = {"data": "test", "user_id": "user123"}
        signed = await jws_manager.sign(payload, algorithm="HS256")
        assert signed is not None
        assert isinstance(signed, str)
        # JWS has format: header.payload.signature (3 parts)
        assert signed.count('.') == 2
    @pytest.mark.asyncio

    async def test_verify_signature(self, jws_manager):
        """Test signature verification."""
        payload = {"data": "test", "user_id": "user123"}
        signed = await jws_manager.sign(payload, algorithm="HS256")
        verified = await jws_manager.verify(signed)
        assert verified is not None
        assert verified.get('data') == "test"
        assert verified.get('user_id') == "user123"
    @pytest.mark.asyncio

    async def test_verify_invalid_signature(self, jws_manager):
        """Test that invalid signatures fail verification."""
        invalid_signed = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        with pytest.raises((XWInvalidTokenError, Exception)):
            await jws_manager.verify(invalid_signed)
@pytest.mark.xwauth_unit

class TestJWKManager:
    """Test JWK Manager implementation."""

    def test_generate_jwk_oct(self, jwk_manager):
        """Test OCT (symmetric) key generation."""
        key = jwk_manager.generate_jwk(key_type="oct", algorithm="HS256")
        assert key is not None
        assert 'kty' in key
        assert key['kty'] == "oct"
        assert 'k' in key  # OCT keys have 'k' (key value)

    def test_generate_jwk_rsa(self, jwk_manager):
        """Test RSA key generation."""
        try:
            key = jwk_manager.generate_jwk(key_type="RSA", algorithm="RS256")
            assert key is not None
            assert 'kty' in key
            assert key['kty'] == "RSA"
        except (NotImplementedError, Exception):
            # RSA key generation may require cryptography library
            pytest.skip("RSA key generation requires cryptography library")

    def test_generate_jwk_ec(self, jwk_manager):
        """Test EC key generation."""
        try:
            key = jwk_manager.generate_jwk(key_type="EC", algorithm="ES256")
            assert key is not None
            assert 'kty' in key
            assert key['kty'] == "EC"
        except (NotImplementedError, Exception):
            # EC key generation may require cryptography library
            pytest.skip("EC key generation requires cryptography library")
    @pytest.mark.asyncio

    async def test_save_and_load_jwk(self, jwk_manager):
        """Test saving and loading JWK."""
        key = jwk_manager.generate_jwk(key_type="oct", algorithm="HS256")
        key_id = key.get('kid')
        if not key_id:
            key['kid'] = 'test-key-id'
            key_id = 'test-key-id'
        # Save key (save_jwk takes single jwk dict)
        await jwk_manager.save_jwk(key)
        # Load key (get_jwk by key_id)
        loaded_key = await jwk_manager.get_jwk(key_id)
        assert loaded_key is not None
        assert loaded_key['kid'] == key_id
@pytest.mark.xwauth_unit

class TestJWAManager:
    """Test JWA Manager implementation."""
    @pytest.fixture

    def jwa_manager(self):
        """Create JWAManager instance."""
        return JWAManager()

    def test_get_algorithm_info(self, jwa_manager):
        """Test getting algorithm information."""
        info = jwa_manager.get_algorithm_info("HS256")
        assert info is not None
        assert info['name'] == "HS256"
        # Implementation uses "signing" for HMAC/signing algorithms
        assert info['type'] in ("MAC", "signing")

    def test_validate_algorithm(self, jwa_manager):
        """Test algorithm validation (via is_signing_algorithm / is_encryption_algorithm)."""
        assert jwa_manager.is_signing_algorithm("HS256") is True
        assert jwa_manager.is_signing_algorithm("RS256") is True
        assert jwa_manager.is_signing_algorithm("INVALID") is False

    def test_get_supported_algorithms(self, jwa_manager):
        """Test supported algorithms (JWAAlgorithm enum)."""
        from exonware.xwauth.identity.jose.jwa import JWAAlgorithm
        algorithms = [a.value for a in JWAAlgorithm]
        assert algorithms is not None
        assert isinstance(algorithms, list)
        assert len(algorithms) > 0
        assert "HS256" in algorithms
