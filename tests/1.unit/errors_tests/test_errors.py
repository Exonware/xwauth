#!/usr/bin/env python3
"""
#exonware/xwauth.connector/tests/1.unit/errors_tests/test_errors.py
Unit tests for error handling.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from exonware.xwauth.identity.errors import (
    XWAuthError,
    XWOAuthError,
    XWTokenError,
    XWInvalidTokenError,
    XWExpiredTokenError,
    XWAuthenticationError,
    XWInvalidCredentialsError,
    XWAuthorizationError,
    XWSessionError,
    XWSessionExpiredError,
    XWUserError,
    XWUserNotFoundError,
    XWUserAlreadyExistsError,
    XWProviderError,
    XWProviderNotFoundError,
    XWProviderConnectionError,
    XWInvalidRequestError,
    XWUnauthorizedClientError,
    XWUnsupportedResponseTypeError
)
@pytest.mark.xwauth_unit

class TestErrorHierarchy:
    """Test error hierarchy and inheritance."""

    def test_xwauth_error_base(self):
        """Test XWAuthError base class."""
        error = XWAuthError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code is not None
        assert isinstance(error.context, dict)
        assert isinstance(error.suggestions, list)

    def test_xwauth_error_with_context(self):
        """Test XWAuthError with context."""
        error = XWAuthError(
            "Test error",
            error_code="TEST_ERROR",
            context={"key": "value"},
            suggestions=["Fix this", "Try that"]
        )
        assert error.error_code == "TEST_ERROR"
        assert error.context["key"] == "value"
        assert len(error.suggestions) == 2

    def test_xwauth_error_chaining(self):
        """Test error context chaining."""
        error = XWAuthError("Test error")
        error.add_context(key1="value1").add_context(key2="value2")
        error.suggest("Suggestion 1").suggest("Suggestion 2")
        assert error.context["key1"] == "value1"
        assert error.context["key2"] == "value2"
        assert len(error.suggestions) == 2

    def test_xwoauth_error(self):
        """Test XWOAuthError."""
        error = XWOAuthError(
            "OAuth error",
            error_code="invalid_request",
            error_description="Invalid request parameter"
        )
        assert error.error_code == "invalid_request"
        assert error.error_description == "Invalid request parameter"
        assert isinstance(error, XWAuthError)

    def test_xwtoken_error(self):
        """Test XWTokenError."""
        error = XWTokenError("Token error")
        assert isinstance(error, XWAuthError)
        assert "Token" in error.error_code or "token" in error.error_code.lower()

    def test_xwinvalid_token_error(self):
        """Test XWInvalidTokenError."""
        error = XWInvalidTokenError("Invalid token")
        assert isinstance(error, XWTokenError)
        assert isinstance(error, XWAuthError)

    def test_xwexpired_token_error(self):
        """Test XWExpiredTokenError."""
        error = XWExpiredTokenError("Expired token")
        assert isinstance(error, XWTokenError)
        assert isinstance(error, XWAuthError)

    def test_xwauthentication_error(self):
        """Test XWAuthenticationError."""
        error = XWAuthenticationError("Authentication failed")
        assert isinstance(error, XWAuthError)

    def test_xwinvalid_credentials_error(self):
        """Test XWInvalidCredentialsError."""
        error = XWInvalidCredentialsError("Invalid credentials")
        assert isinstance(error, XWAuthenticationError)
        assert isinstance(error, XWAuthError)

    def test_xwauthorization_error(self):
        """Test XWAuthorizationError."""
        error = XWAuthorizationError("Authorization failed")
        assert isinstance(error, XWAuthError)

    def test_xwsession_error(self):
        """Test XWSessionError."""
        error = XWSessionError("Session error")
        assert isinstance(error, XWAuthError)

    def test_xwsession_expired_error(self):
        """Test XWSessionExpiredError."""
        error = XWSessionExpiredError("Session expired")
        assert isinstance(error, XWSessionError)
        assert isinstance(error, XWAuthError)

    def test_xwuser_error(self):
        """Test XWUserError."""
        error = XWUserError("User error")
        assert isinstance(error, XWAuthError)

    def test_xwuser_not_found_error(self):
        """Test XWUserNotFoundError."""
        error = XWUserNotFoundError("User not found", user_id="user123")
        assert isinstance(error, XWUserError)
        assert isinstance(error, XWAuthError)

    def test_xwuser_already_exists_error(self):
        """Test XWUserAlreadyExistsError."""
        error = XWUserAlreadyExistsError("User exists", email="test@example.com")
        assert isinstance(error, XWUserError)
        assert isinstance(error, XWAuthError)

    def test_xwprovider_error(self):
        """Test XWProviderError."""
        error = XWProviderError("Provider error")
        assert isinstance(error, XWAuthError)

    def test_xwprovider_not_found_error(self):
        """Test XWProviderNotFoundError."""
        error = XWProviderNotFoundError("Provider not found", provider_name="google")
        assert isinstance(error, XWProviderError)
        assert isinstance(error, XWAuthError)

    def test_xwprovider_connection_error(self):
        """Test XWProviderConnectionError."""
        error = XWProviderConnectionError("Connection failed")
        assert isinstance(error, XWProviderError)
        assert isinstance(error, XWAuthError)

    def test_xwinvalid_request_error(self):
        """Test XWInvalidRequestError."""
        error = XWInvalidRequestError("Invalid request")
        assert isinstance(error, XWOAuthError)
        assert isinstance(error, XWAuthError)

    def test_xwunauthorized_client_error(self):
        """Test XWUnauthorizedClientError."""
        error = XWUnauthorizedClientError("Unauthorized client")
        assert isinstance(error, XWOAuthError)
        assert isinstance(error, XWAuthError)

    def test_xwunsupported_response_type_error(self):
        """Test XWUnsupportedResponseTypeError."""
        error = XWUnsupportedResponseTypeError("Unsupported response type")
        assert isinstance(error, XWOAuthError)
        assert isinstance(error, XWAuthError)

    def test_error_with_cause(self):
        """Test error with cause."""
        cause = ValueError("Original error")
        error = XWAuthError("Wrapper error", cause=cause)
        assert error.cause == cause
        assert isinstance(error.cause, ValueError)
