#!/usr/bin/env python3
"""
Core protocol conformance tests for xwauth contracts.
"""

import pytest

from exonware.xwauth.identity.config.config import XWAuthConfig

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwsystem.security.contracts import IAuthContextResolver
from exonware.xwauth.identity.contracts import IProvider
from exonware.xwauth.connect.providers.registry import ProviderRegistry
# ProviderRegistry is part of the connect package; it raises
# ``connect.errors.XWProviderError``, which is a separate class from
# ``identity.errors.XWProviderError`` (the two packages are independent and
# each owns its own error hierarchy -- NO shim, NO cross-import).
from exonware.xwauth.connect.errors import XWProviderError
from exonware.xwsystem.security.contracts import AuthContext as SharedAuthContext


class _ProviderConformanceFake:
    @property
    def provider_name(self) -> str:
        return "conformance_provider"

    @property
    def provider_type(self) -> str:
        return "openid_connect"

    async def get_authorization_url(self, client_id: str, redirect_uri: str, state: str, scopes=None) -> str:
        return "https://idp.example/authorize"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        return {"access_token": "tok"}

    async def get_user_info(self, access_token: str) -> dict:
        return {"sub": "user-1"}


class _ProviderMissingContract:
    @property
    def provider_name(self) -> str:
        return "missing_contract"

    @property
    def provider_type(self) -> str:
        return "openid_connect"


@pytest.mark.xwauth_core
def test_xwauth_facade_conforms_to_auth_context_resolver() -> None:
    auth = XWAuth(
        config=XWAuthConfig(
            jwt_secret="test-secret-conformance",
            allow_mock_storage_fallback=True,
        )
    )
    assert isinstance(auth, IAuthContextResolver)


@pytest.mark.xwauth_core
def test_provider_registry_accepts_protocol_conformant_provider() -> None:
    provider = _ProviderConformanceFake()
    assert isinstance(provider, IProvider)
    registry = ProviderRegistry()
    registry.register(provider)
    assert registry.has("conformance_provider") is True


@pytest.mark.xwauth_core
def test_provider_registry_rejects_invalid_provider_name() -> None:
    class _BadProvider(_ProviderConformanceFake):
        @property
        def provider_name(self) -> str:
            return "INVALID NAME"

    registry = ProviderRegistry()
    with pytest.raises(XWProviderError):
        registry.register(_BadProvider())


@pytest.mark.xwauth_core
@pytest.mark.parametrize(
    "provider_name",
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="whitespace"),
        pytest.param("A", id="too_short_uppercase"),
        pytest.param("INVALID NAME", id="contains_space"),
        pytest.param("a" * 65, id="too_long"),
    ],
)
def test_provider_registry_rejects_invalid_name_variants(provider_name: str) -> None:
    class _BadProvider(_ProviderConformanceFake):
        @property
        def provider_name(self) -> str:
            return provider_name

    registry = ProviderRegistry()
    with pytest.raises(XWProviderError):
        registry.register(_BadProvider())


@pytest.mark.xwauth_core
def test_provider_registry_rejects_missing_oauth_contract_methods() -> None:
    registry = ProviderRegistry()
    with pytest.raises(XWProviderError):
        registry.register(_ProviderMissingContract())


@pytest.mark.xwauth_core
def test_xwauth_auth_context_reuses_xwsystem_contract() -> None:
    from exonware.xwauth.identity.contracts import AuthContext
    assert AuthContext is SharedAuthContext
