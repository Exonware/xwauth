from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from exonware.xwauth.storage.mock import MockToken, MockUser
from exonware.xwauth.storage.xwstorage_provider import XWStorageProvider


class _InMemoryBackend:
    def __init__(self) -> None:
        self._data: dict[str, object] = {}

    async def write(self, key: str, value: object) -> None:
        self._data[key] = value

    async def read(self, key: str) -> object:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_xwstorage_provider_persists_user_across_instances() -> None:
    backend = _InMemoryBackend()
    provider1 = XWStorageProvider(backend)
    await provider1.save_user(MockUser(id="u1", email="u1@example.com"))

    provider2 = XWStorageProvider(backend)
    loaded = await provider2.get_user("u1")
    assert loaded is not None
    assert loaded.id == "u1"
    assert loaded.email == "u1@example.com"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_xwstorage_provider_persists_token_lookup_indexes() -> None:
    backend = _InMemoryBackend()
    provider = XWStorageProvider(backend)

    token = MockToken(
        id="t1",
        user_id="u1",
        client_id="c1",
        token_type="Bearer",
        access_token="access-1",
        refresh_token="refresh-1",
        expires_at=datetime.now() + timedelta(minutes=10),
        scopes=["read"],
    )
    await provider.save_token(token)

    loaded_access = await provider.get_token_by_access_token("access-1")
    loaded_refresh = await provider.get_token_by_refresh_token("refresh-1")
    assert loaded_access is not None and loaded_access.id == "t1"
    assert loaded_refresh is not None and loaded_refresh.id == "t1"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_xwstorage_provider_supports_basic_provider_storage_contract() -> None:
    backend = _InMemoryBackend()
    provider = XWStorageProvider(backend)

    await provider.save("custom_entity", "e1", {"status": "active", "tenant_id": "t1"})
    found = await provider.get("custom_entity", "e1")
    by_field = await provider.get_by_field("custom_entity", "tenant_id", "t1")
    all_items = await provider.list("custom_entity", {"status": "active"})

    assert found == {"status": "active", "tenant_id": "t1"}
    assert by_field == {"status": "active", "tenant_id": "t1"}
    assert len(all_items) == 1
