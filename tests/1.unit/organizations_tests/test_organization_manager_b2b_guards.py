#!/usr/bin/env python3
"""Delegated-admin and horizontal-privilege guards on organization roles."""

from __future__ import annotations

import pytest

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.errors import XWAuthError
from exonware.xwauth.identity.organizations.lifecycle import OrganizationLifecycle
from exonware.xwauth.identity.organizations.manager import OrganizationManager


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_admin_cannot_assign_owner_role() -> None:
    auth = XWAuth(
        jwt_secret="unit-test-secret-key-for-org-tests",
        allow_mock_storage_fallback=True,
    )
    life = OrganizationLifecycle(auth)
    org = await life.create_organization(name="Acme Corp", owner_id="u_owner")
    await life._add_member(org.id, "u_admin", "admin")
    await life._add_member(org.id, "u_member", "member")
    mgr = OrganizationManager(auth)
    with pytest.raises(XWAuthError) as exc:
        await mgr.update_member_role(
            org.id, "u_member", "owner", actor_user_id="u_admin"
        )
    assert exc.value.error_code == "forbidden_owner_promotion"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_owner_can_promote_to_owner_when_second_owner_allowed() -> None:
    auth = XWAuth(
        jwt_secret="unit-test-secret-key-for-org-tests",
        allow_mock_storage_fallback=True,
    )
    life = OrganizationLifecycle(auth)
    org = await life.create_organization(name="Beta Inc", owner_id="u_owner")
    await life._add_member(org.id, "u_member", "member")
    mgr = OrganizationManager(auth)
    out = await mgr.update_member_role(
        org.id, "u_member", "owner", actor_user_id="u_owner"
    )
    assert out["role"] == "owner"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_cannot_demote_last_owner() -> None:
    auth = XWAuth(
        jwt_secret="unit-test-secret-key-for-org-tests",
        allow_mock_storage_fallback=True,
    )
    life = OrganizationLifecycle(auth)
    org = await life.create_organization(name="Gamma LLC", owner_id="u_owner")
    mgr = OrganizationManager(auth)
    with pytest.raises(XWAuthError) as exc:
        await mgr.update_member_role(
            org.id, "u_owner", "admin", actor_user_id="u_owner"
        )
    assert exc.value.error_code == "last_owner"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_admin_cannot_demote_owner() -> None:
    auth = XWAuth(
        jwt_secret="unit-test-secret-key-for-org-tests",
        allow_mock_storage_fallback=True,
    )
    life = OrganizationLifecycle(auth)
    org = await life.create_organization(name="Epsilon Co", owner_id="u_owner")
    await life._add_member(org.id, "u_admin", "admin")
    await life._add_member(org.id, "u_co", "owner")
    mgr = OrganizationManager(auth)
    with pytest.raises(XWAuthError) as exc:
        await mgr.update_member_role(
            org.id, "u_co", "member", actor_user_id="u_admin"
        )
    assert exc.value.error_code == "forbidden_owner_demotion"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_admin_cannot_invite_owner() -> None:
    auth = XWAuth(
        jwt_secret="unit-test-secret-key-for-org-tests",
        allow_mock_storage_fallback=True,
    )
    life = OrganizationLifecycle(auth)
    org = await life.create_organization(name="Delta Ltd", owner_id="u_owner")
    await life._add_member(org.id, "u_admin", "admin")
    mgr = OrganizationManager(auth)
    with pytest.raises(XWAuthError) as exc:
        await mgr.invite_member(
            org.id, "new@example.com", role="owner", inviter_id="u_admin"
        )
    assert exc.value.error_code == "forbidden_owner_invite"
