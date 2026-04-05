#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/users_tests/test_user_model.py
Unit tests for User model.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import pytest
from datetime import datetime
from exonware.xwauth.users.user import User
from exonware.xwauth.defs import UserStatus
@pytest.mark.xwauth_unit

class TestUserModel:
    """Test User model implementation."""

    def test_create_user(self):
        """Test user creation."""
        user = User(
            id="user123",
            email="test@example.com",
            status=UserStatus.ACTIVE,
            created_at=datetime.now()
        )
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.status == UserStatus.ACTIVE

    def test_user_with_attributes(self):
        """Test user with custom attributes."""
        user = User(
            id="user123",
            email="test@example.com",
            attributes={
                "name": "Test User",
                "age": 30,
                "department": "engineering"
            }
        )
        assert user.attributes["name"] == "Test User"
        assert user.attributes["age"] == 30

    def test_user_with_roles(self):
        """Test user with roles."""
        user = User(
            id="user123",
            email="test@example.com",
            attributes={"roles": ["admin", "user"]}
        )
        assert "admin" in user.attributes.get("roles", [])
        assert "user" in user.attributes.get("roles", [])

    def test_user_status_transitions(self):
        """Test user status transitions."""
        user = User(
            id="user123",
            email="test@example.com",
            status=UserStatus.ACTIVE
        )
        assert user.status == UserStatus.ACTIVE
        user.status = UserStatus.SUSPENDED
        assert user.status == UserStatus.SUSPENDED
        user.status = UserStatus.DELETED
        assert user.status == UserStatus.DELETED

    def test_user_metadata(self):
        """Test user metadata."""
        user = User(
            id="user123",
            email="test@example.com",
            attributes={
                "last_login": datetime.now().isoformat(),
                "login_count": 5
            }
        )
        assert "last_login" in user.attributes
        assert user.attributes["login_count"] == 5
