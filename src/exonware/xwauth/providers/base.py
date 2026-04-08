#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/providers/base.py
Base Provider Class
Abstract base class for OAuth providers using xwsystem HttpClient.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.3
Generation Date: 20-Dec-2025
"""

from typing import Any, Optional
from abc import abstractmethod
import base64
import hashlib
from urllib.parse import urlencode, urlparse, parse_qs
from exonware.xwsystem import get_logger
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.formats.text import json as xw_json
from exonware.xwsystem.http_client import HttpClient, AsyncHttpClient
HTTP_CLIENT_AVAILABLE = True
from ..defs import ProviderType
from ..errors import XWProviderError, XWProviderConnectionError
from ..base import ABaseProvider as _ABaseProvider
from ..contracts import IProvider
logger = get_logger(__name__)


class ABaseProvider(_ABaseProvider, IProvider):
    """
    Abstract base class for OAuth providers.
    Provides common OAuth flow functionality using xwsystem HttpClient.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        userinfo_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize provider.
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            authorization_url: Authorization endpoint URL
            token_url: Token endpoint URL
            userinfo_url: User info endpoint URL (optional)
            **kwargs: Provider-specific configuration
        """
        super().__init__(client_id, client_secret, **kwargs)
        self._authorization_url = authorization_url
        self._token_url = token_url
        self._userinfo_url = userinfo_url
        # Initialize HTTP clients lazily to avoid issues if httpx not available
        self._http_client = None
        self._async_http_client = None
        logger.debug(f"ABaseProvider initialized: {self.provider_name}")
    @property

    def provider_name(self) -> str:
        """Get provider name."""
        return self.provider_type.value
    @property

    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.CUSTOM

    @staticmethod
    def _pkce_s256_challenge(code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    @staticmethod
    def _token_error_summary(response: Any) -> str:
        """Best-effort OAuth 2.0 error JSON (*error*, *error_description*) for logs and exceptions."""
        raw = getattr(response, "text", None) or ""
        text = str(raw)
        snippet = (text[:500] + ("…" if len(text) > 500 else "")).strip()
        try:
            data = xw_json.loads(text)
        except (xw_json.JSONDecodeError, SerializationError, TypeError, ValueError):
            return snippet or ""
        if isinstance(data, dict) and data.get("error"):
            err = str(data.get("error", "")).strip()
            desc = str(data.get("error_description", "") or "").strip()
            if desc:
                return f"{err}: {desc}"
            return err
        return snippet or ""

    @property
    def oidc_issuer(self) -> str | None:
        """When set, the federation broker can validate id_tokens against JWKS."""
        return None

    @property
    def oidc_jwks_uri(self) -> str | None:
        return None

    async def get_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes: Optional[list[str]] = None,
        nonce: Optional[str] = None,
        code_verifier: Optional[str] = None,
    ) -> str:
        """
        Get authorization URL for OAuth flow.
        Args:
            client_id: OAuth client ID
            redirect_uri: Redirect URI
            state: State parameter for CSRF protection
            scopes: Optional list of scopes
        Returns:
            Authorization URL
        """
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
        }
        if scopes:
            params['scope'] = ' '.join(scopes)
        scope_str = params.get("scope") or ""
        if nonce and ("openid" in scope_str or "openid" in (scopes or [])):
            params["nonce"] = nonce
        if code_verifier:
            params["code_challenge"] = self._pkce_s256_challenge(code_verifier)
            params["code_challenge_method"] = "S256"
        # Add provider-specific parameters
        params.update(self._get_authorization_params())
        query_string = urlencode(params)
        return f"{self._authorization_url}?{query_string}"

    def _token_exchange_client_secret(self) -> str:
        """Secret sent as `client_secret` on the token endpoint (override for JWT secrets, e.g. Apple)."""
        return self._client_secret

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        *,
        code_verifier: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token.
        Args:
            code: Authorization code
            redirect_uri: Redirect URI
        Returns:
            Token response dictionary
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self._client_id,
            'client_secret': self._token_exchange_client_secret(),
        }
        if code_verifier:
            data["code_verifier"] = code_verifier
        # Lazy initialize async client
        if not HTTP_CLIENT_AVAILABLE:
            raise XWProviderConnectionError(
                "HTTP client not available",
                error_code="http_client_unavailable"
            )
        if self._async_http_client is None:
            self._async_http_client = AsyncHttpClient()
        try:
            response = await self._async_http_client.post(
                self._token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            if response.status_code != 200:
                detail = self._token_error_summary(response)
                raise XWProviderConnectionError(
                    f"Token exchange failed: {response.status_code} {detail}".strip(),
                    error_code="token_exchange_failed",
                    context={
                        "status_code": response.status_code,
                        "response": response.text,
                        "oauth_error": detail,
                    },
                )
            return response.json()
        except XWProviderConnectionError:
            raise
        except XWProviderError:
            raise
        except Exception as e:
            raise XWProviderConnectionError(
                f"Token exchange error: {e}",
                error_code="token_exchange_error",
                cause=e
            )

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from provider.
        Args:
            access_token: Access token
        Returns:
            User information dictionary
        """
        if not self._userinfo_url:
            raise XWProviderError(
                "User info endpoint not configured",
                error_code="userinfo_not_configured"
            )
        # Lazy initialize async client
        if not HTTP_CLIENT_AVAILABLE:
            raise XWProviderConnectionError(
                "HTTP client not available",
                error_code="http_client_unavailable"
            )
        if self._async_http_client is None:
            self._async_http_client = AsyncHttpClient()
        try:
            response = await self._async_http_client.get(
                self._userinfo_url,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            if response.status_code != 200:
                raise XWProviderConnectionError(
                    f"User info request failed: {response.status_code}",
                    error_code="userinfo_failed",
                    context={'status_code': response.status_code}
                )
            return response.json()
        except Exception as e:
            raise XWProviderConnectionError(
                f"User info error: {e}",
                error_code="userinfo_error",
                cause=e
            )

    def _get_authorization_params(self) -> dict[str, Any]:
        """
        Get provider-specific authorization parameters.
        Override in subclasses for provider-specific parameters.
        Returns:
            Dictionary of additional parameters
        """
        return {}
