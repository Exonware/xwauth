"""OAuth/token exception → HTTP response mapping for the connector side.

Maps ``exonware.xwauth.connect.errors.*`` exceptions into RFC 6749-shaped
response tuples (body + status code) suitable for FastAPI ``JSONResponse``.

Independent of ``exonware.xwauth.identity`` — each package ships its own
error-to-HTTP mapping so neither has to import the other.
"""

from __future__ import annotations

from typing import Any

from exonware.xwsystem.security.oauth_errors import oauth_error_response

from ..errors import (
    XWAccessDeniedError,
    XWAuthenticationError,
    XWAuthError,
    XWExpiredTokenError,
    XWInvalidRequestError,
    XWInvalidScopeError,
    XWInvalidTokenError,
    XWOAuthError,
    XWProviderConnectionError,
    XWProviderError,
    XWTokenError,
    XWUnauthorizedClientError,
    XWUnsupportedResponseTypeError,
)

__all__ = ["oauth_error_to_http"]


def oauth_error_to_http(exc: Exception) -> tuple[dict[str, Any], int]:
    """Map an auth/token exception to a ``(body, status_code)`` tuple.

    - ``XWOAuthError`` / subclasses → RFC 6749 error body + 400
    - ``XWInvalidTokenError`` / ``XWExpiredTokenError`` → 401 ``invalid_token``
    - ``XWAccessDeniedError`` → 403 ``access_denied``
    - ``XWAuthenticationError`` → 401 ``unauthorized``
    - ``XWProviderConnectionError`` → 502 ``upstream_provider_unreachable``
    - ``XWProviderError`` → 502 ``upstream_provider_error``
    - Other ``XWAuthError`` subclasses → 400 with the error_code from the exception
    - Everything else → 500 ``internal_error``
    """
    # Token-class first: 401 for invalid/expired token surfaces.
    if isinstance(exc, XWExpiredTokenError):
        return oauth_error_response("invalid_token", str(exc)), 401
    if isinstance(exc, XWInvalidTokenError):
        return oauth_error_response("invalid_token", str(exc)), 401
    if isinstance(exc, XWTokenError):
        return oauth_error_response("invalid_token", str(exc)), 401

    # OAuth2 error-class: 400 with the RFC 6749 code from the exception.
    if isinstance(exc, XWAccessDeniedError):
        return oauth_error_response("access_denied", str(exc)), 403
    if isinstance(exc, XWUnauthorizedClientError):
        return oauth_error_response("unauthorized_client", str(exc)), 401
    if isinstance(exc, XWUnsupportedResponseTypeError):
        return oauth_error_response("unsupported_response_type", str(exc)), 400
    if isinstance(exc, XWInvalidScopeError):
        return oauth_error_response("invalid_scope", str(exc)), 400
    if isinstance(exc, XWInvalidRequestError):
        return oauth_error_response("invalid_request", str(exc)), 400
    if isinstance(exc, XWOAuthError):
        code = getattr(exc, "error_code", "invalid_request") or "invalid_request"
        return oauth_error_response(code, str(exc)), 400

    # Provider-class: upstream IdP failures.
    if isinstance(exc, XWProviderConnectionError):
        return oauth_error_response("upstream_provider_unreachable", str(exc)), 502
    if isinstance(exc, XWProviderError):
        return oauth_error_response("upstream_provider_error", str(exc)), 502

    # Authentication failures (credentials/identity not confirmed).
    if isinstance(exc, XWAuthenticationError):
        return oauth_error_response("unauthorized", str(exc)), 401

    # Anything else in the xwauth family: 400 with class-derived code.
    if isinstance(exc, XWAuthError):
        code = getattr(exc, "error_code", None) or exc.__class__.__name__
        return oauth_error_response(code, str(exc)), 400

    # Unknown exception: generic 500.
    return oauth_error_response("internal_error", str(exc) or "internal server error"), 500
