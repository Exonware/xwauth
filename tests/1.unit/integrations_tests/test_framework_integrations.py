#!/usr/bin/env python3
"""
#exonware/xwauth/tests/1.unit/integrations_tests/test_framework_integrations.py
Unit tests for framework integrations (FastAPI, Flask, Django).
Tests framework-specific helpers and integrations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from __future__ import annotations
import pytest
@pytest.mark.xwauth_unit

class TestFastAPIIntegration:
    """Test FastAPI integration helpers."""

    def test_fastapi_dependencies_import(self):
        """Test that FastAPI dependencies can be imported."""
        try:
            from exonware.xwauth.integrations.fastapi import get_current_user, require_auth
            assert get_current_user is not None
            assert require_auth is not None
        except ImportError:
            pytest.skip("FastAPI integration not available")

    def test_fastapi_integration_structure(self):
        """Test FastAPI integration module structure."""
        try:
            from exonware.xwauth.integrations import fastapi
            assert hasattr(fastapi, 'get_current_user') or hasattr(fastapi, '__all__')
        except ImportError:
            pytest.skip("FastAPI integration not available")
@pytest.mark.xwauth_unit

class TestFlaskIntegration:
    """Test Flask integration helpers."""

    def test_flask_middleware_import(self):
        """Test that Flask middleware can be imported."""
        try:
            from exonware.xwauth.integrations.flask import require_auth, get_current_user
            assert require_auth is not None
            assert get_current_user is not None
        except ImportError:
            pytest.skip("Flask integration not available")

    def test_flask_integration_structure(self):
        """Test Flask integration module structure."""
        try:
            from exonware.xwauth.integrations import flask
            assert hasattr(flask, 'require_auth') or hasattr(flask, '__all__')
        except ImportError:
            pytest.skip("Flask integration not available")
@pytest.mark.xwauth_unit

class TestDjangoIntegration:
    """Test Django integration helpers."""

    def test_django_auth_backend_import(self):
        """Test that Django auth backend can be imported."""
        try:
            from exonware.xwauth.integrations.django import auth_backend
            assert auth_backend is not None
        except ImportError:
            pytest.skip("Django integration not available")

    def test_django_drf_integration_import(self):
        """Test that Django REST Framework integration can be imported."""
        try:
            from exonware.xwauth.integrations.django import drf
            assert drf is not None
        except ImportError:
            pytest.skip("Django DRF integration not available")
@pytest.mark.xwauth_unit

class TestORMHelpers:
    """Test ORM helper integrations."""

    def test_sqlalchemy_mixins_import(self):
        """Test that SQLAlchemy mixins can be imported."""
        try:
            from exonware.xwauth.integrations.sqlalchemy import mixins
            assert mixins is not None
            # Check for common mixins
            assert hasattr(mixins, 'OAuth2ClientMixin') or hasattr(mixins, '__all__')
        except ImportError:
            pytest.skip("SQLAlchemy integration not available")

    def test_django_orm_models_import(self):
        """Test that Django ORM models can be imported."""
        try:
            from exonware.xwauth.integrations.django_orm import models
            assert models is not None
        except ImportError:
            pytest.skip("Django ORM integration not available")
