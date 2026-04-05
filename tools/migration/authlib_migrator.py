#!/usr/bin/env python3
"""
#exonware/xwauth/tools/migration/authlib_migrator.py
Migration Tool: From Authlib to xwauth
Format-agnostic migration tool for converting Authlib configurations and data to xwauth.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 25-Jan-2026
"""

from typing import Any, Optional
import json
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class AuthlibMigrator:
    """
    Migration tool from Authlib to xwauth.
    Format-agnostic - works with any storage backend.
    """

    def __init__(self, source_config: dict[str, Any], target_storage: Any):
        """
        Initialize Authlib migrator.
        Args:
            source_config: Authlib configuration dictionary
            target_storage: xwauth storage provider (format-agnostic)
        """
        self._source_config = source_config
        self._target_storage = target_storage
        logger.debug("AuthlibMigrator initialized")

    async def migrate_clients(self) -> dict[str, Any]:
        """
        Migrate OAuth clients from Authlib to xwauth format.
        Returns:
            Migration report
        """
        migrated = []
        errors = []
        # Extract clients from Authlib config
        clients = self._source_config.get('OAUTH_CLIENTS', {})
        for client_name, client_config in clients.items():
            try:
                # Convert Authlib client format to xwauth format
                xwauth_client = {
                    'client_id': client_config.get('client_id', client_name),
                    'client_secret': client_config.get('client_secret'),
                    'redirect_uris': client_config.get('redirect_uris', []),
                    'grant_types': client_config.get('grant_types', ['authorization_code']),
                    'scopes': client_config.get('scopes', []),
                }
                # Save to xwauth storage (format-agnostic)
                if hasattr(self._target_storage, 'write'):
                    await self._target_storage.write(
                        f"oauth_client:{xwauth_client['client_id']}",
                        xwauth_client
                    )
                migrated.append(client_name)
            except Exception as e:
                errors.append({
                    'client': client_name,
                    'error': str(e)
                })
        return {
            'migrated': migrated,
            'errors': errors,
            'total': len(clients)
        }

    async def migrate_users(self, source_users: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Migrate users from Authlib format to xwauth format.
        Args:
            source_users: List of users from Authlib
        Returns:
            Migration report
        """
        migrated = []
        errors = []
        for user in source_users:
            try:
                # Convert Authlib user format to xwauth format
                from exonware.xwauth.users.user import User
                xwauth_user = User(
                    id=user.get('id'),
                    email=user.get('email'),
                    password_hash=user.get('password_hash'),
                    attributes=user.get('attributes', {})
                )
                # Save to xwauth storage
                await self._target_storage.save_user(xwauth_user)
                migrated.append(user.get('id'))
            except Exception as e:
                errors.append({
                    'user': user.get('id'),
                    'error': str(e)
                })
        return {
            'migrated': migrated,
            'errors': errors,
            'total': len(source_users)
        }


class DjangoOAuthToolkitMigrator:
    """
    Migration tool from Django OAuth Toolkit to xwauth.
    Format-agnostic - works with any storage backend.
    """

    def __init__(self, source_data: dict[str, Any], target_storage: Any):
        """
        Initialize Django OAuth Toolkit migrator.
        Args:
            source_data: Django OAuth Toolkit data (from database export)
            target_storage: xwauth storage provider
        """
        self._source_data = source_data
        self._target_storage = target_storage
        logger.debug("DjangoOAuthToolkitMigrator initialized")

    async def migrate_applications(self) -> dict[str, Any]:
        """
        Migrate OAuth applications from Django OAuth Toolkit.
        Returns:
            Migration report
        """
        migrated = []
        errors = []
        applications = self._source_data.get('oauth2_provider_application', [])
        for app in applications:
            try:
                # Convert Django OAuth Toolkit format to xwauth format
                xwauth_client = {
                    'client_id': app.get('client_id'),
                    'client_secret': app.get('client_secret'),
                    'redirect_uris': app.get('redirect_uris', '').split(),
                    'grant_types': ['authorization_code', 'refresh_token'],
                    'scopes': [],
                }
                # Save to xwauth storage
                if hasattr(self._target_storage, 'write'):
                    await self._target_storage.write(
                        f"oauth_client:{xwauth_client['client_id']}",
                        xwauth_client
                    )
                migrated.append(app.get('client_id'))
            except Exception as e:
                errors.append({
                    'application': app.get('client_id'),
                    'error': str(e)
                })
        return {
            'migrated': migrated,
            'errors': errors,
            'total': len(applications)
        }
