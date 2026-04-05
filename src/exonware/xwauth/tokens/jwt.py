#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/tokens/jwt.py
JWT Token Management
JWT token generation and validation using xwsystem SecureHash.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 20-Dec-2025
"""

from typing import Any
from datetime import datetime, timedelta, timezone
import time
import uuid
import jwt
from exonware.xwsystem import get_logger
from ..errors import XWTokenError, XWInvalidTokenError, XWExpiredTokenError
from ..defs import TokenType
logger = get_logger(__name__)


def oidc_left_half_sha256_b64url(value: str) -> str:
    """
    OIDC ``at_hash`` / ``c_hash`` for JWS alg HS256 / RS256 (SHA-256 family).
    Delegates to federation helper so digest choice stays aligned with ``oidc_access_token_hash``.
    """
    from ..federation.oidc_access_token_hash import compute_at_hash

    return compute_at_hash(value, signing_alg="HS256")


class JWTTokenManager:
    """
    JWT token generation and validation.
    Uses PyJWT library with xwsystem SecureHash for signing.
    """

    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        issuer: str | None = None,
        audience: str | None = None,
        verify_secrets: list[str] | None = None,
        active_key_id: str | None = None,
    ):
        """
        Initialize JWT token manager.
        Args:
            secret: Secret key for signing tokens
            algorithm: JWT algorithm (HS256, RS256, etc.)
            issuer: Token issuer (optional)
            audience: Token audience (optional)
        """
        self._secret = secret
        self._verify_secrets = [secret] + [s for s in (verify_secrets or []) if s and s != secret]
        self._algorithm = algorithm
        self._issuer = issuer
        self._audience = audience
        self._active_key_id = active_key_id
        self._revoked_jtis: set[str] = set()
        logger.debug("JWTTokenManager initialized")

    def generate_token(
        self,
        user_id: str | None,
        client_id: str,
        scopes: list[str],
        expires_in: int = 3600,
        additional_claims: dict[str, Any] | None = None
    ) -> str:
        """
        Generate JWT access token.
        Args:
            user_id: User identifier (None for client credentials)
            client_id: Client identifier
            scopes: List of granted scopes
            expires_in: Token expiration in seconds
            additional_claims: Additional JWT claims
        Returns:
            JWT token string
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=expires_in)
        payload = {
            'sub': user_id or client_id,  # Subject
            'client_id': client_id,
            'scope': ' '.join(scopes),
            'iat': int(now.timestamp()),  # Issued at
            'exp': int(expires_at.timestamp()),  # Expiration
            'jti': str(uuid.uuid4()),
        }
        # Add issuer if configured
        if self._issuer:
            payload['iss'] = self._issuer
        # Add audience if configured
        if self._audience:
            payload['aud'] = self._audience
        # Add additional claims
        if additional_claims:
            payload.update(additional_claims)
        # Generate token
        headers = {}
        if self._active_key_id:
            headers["kid"] = self._active_key_id
        token = jwt.encode(payload, self._secret, algorithm=self._algorithm, headers=headers or None)
        logger.debug(f"Generated JWT token for client: {client_id}")
        return token

    def generate_id_token(
        self,
        *,
        sub: str,
        aud: str,
        issuer: str,
        nonce: str,
        expires_in: int = 3600,
        c_hash: str | None = None,
        at_hash: str | None = None,
    ) -> str:
        """Sign an OpenID Connect ID Token (JWT)."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=expires_in)
        payload: dict[str, Any] = {
            "sub": sub,
            "aud": aud,
            "nonce": nonce,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "jti": str(uuid.uuid4()),
        }
        if issuer:
            payload["iss"] = issuer
        if c_hash:
            payload["c_hash"] = c_hash
        if at_hash:
            payload["at_hash"] = at_hash
        headers: dict[str, str] = {"typ": "JWT"}
        if self._active_key_id:
            headers["kid"] = self._active_key_id
        token = jwt.encode(
            payload, self._secret, algorithm=self._algorithm, headers=headers
        )
        logger.debug("Generated OIDC id_token")
        return token

    def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate JWT token.
        Args:
            token: JWT token string
        Returns:
            Decoded token payload
        Raises:
            XWInvalidTokenError: If token is invalid
            XWExpiredTokenError: If token is expired
        """
        try:
            # Decode and verify token
            last_error: Exception | None = None
            payload: dict[str, Any] | None = None
            for candidate_secret in self._verify_secrets:
                try:
                    payload = jwt.decode(
                        token,
                        candidate_secret,
                        algorithms=[self._algorithm],
                        issuer=self._issuer,
                        audience=self._audience
                    )
                    break
                except jwt.InvalidTokenError as exc:
                    last_error = exc
                    continue
            if payload is None:
                raise last_error or jwt.InvalidTokenError("Token verification failed")
            jti = payload.get("jti")
            if jti and self.is_jti_revoked(str(jti)):
                raise XWInvalidTokenError(
                    "JWT token has been revoked",
                    error_code="token_revoked"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise XWExpiredTokenError(
                "JWT token has expired",
                error_code="token_expired"
            )
        except jwt.InvalidTokenError as e:
            raise XWInvalidTokenError(
                f"Invalid JWT token: {e}",
                error_code="invalid_token"
            )

    def revoke_jti(self, jti: str) -> None:
        """Mark JWT jti as revoked."""
        if jti:
            self._revoked_jtis.add(str(jti))

    def is_jti_revoked(self, jti: str) -> bool:
        """Check if JWT jti has been revoked."""
        return str(jti) in self._revoked_jtis

    def get_token_info(self, token: str) -> dict[str, Any]:
        """
        Get token information without validation (for introspection).
        Args:
            token: JWT token string
        Returns:
            Token information dictionary
        """
        try:
            # Decode without verification (for introspection)
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except jwt.InvalidTokenError as e:
            raise XWInvalidTokenError(
                f"Invalid JWT token: {e}",
                error_code="invalid_token"
            )

    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.
        Args:
            token: JWT token string
        Returns:
            True if expired, False otherwise
        """
        try:
            payload = self.get_token_info(token)
            exp = payload.get('exp')
            if exp:
                return datetime.now(timezone.utc).timestamp() > exp
            return False
        except XWInvalidTokenError:
            return True
