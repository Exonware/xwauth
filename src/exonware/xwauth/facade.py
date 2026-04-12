#!/usr/bin/env python3
"""
#exonware/xwauth/src/exonware/xwauth/facade.py
XWAuth Main Facade
Main public API for xwauth library.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.10
Generation Date: 20-Dec-2025
"""

from typing import Any
from exonware.xwsystem import get_logger
from .config.config import XWAuthConfig
from .contracts import AuthContext
from .policy_decision import PolicyDecisionService
from .audit.manager import AuditLogManager
from .audit.context import get_audit_correlation_id
from .extensions import AuthHookRegistry, IAuthHook
from .contracts import IProvider
from .federation import FederationBroker, FederatedIdentity
from .federation.oidc_id_token import OidcIdTokenValidationParams
from .storage.interface import IStorageProvider
from .storage.mock import MockStorageProvider
from .errors import XWAuthError, XWOAuthError
from .base import ABaseAuth
from .scim import SCIM_GROUP_SCHEMA, SCIM_USER_SCHEMA, ScimService
logger = get_logger(__name__)


def create_webauthn_challenge_store(_config: XWAuthConfig) -> Any:
    """
    WebAuthn challenge persistence is not bundled in ``exonware-xwauth``.

    Integrate passkeys/WebAuthn via a separate deployment or library that follows
    W3C WebAuthn and exposes it to your stack over HTTPS.
    """
    raise NotImplementedError(
        "create_webauthn_challenge_store is not provided by exonware-xwauth. "
        "Use a WebAuthn-capable service or in-app store in your deployment."
    )


def create_webauthn_credential_index_redis(_config: XWAuthConfig) -> Any:
    """See :func:`create_webauthn_challenge_store`."""
    raise NotImplementedError(
        "create_webauthn_credential_index_redis is not provided by exonware-xwauth. "
        "Use a WebAuthn-capable service or in-app index in your deployment."
    )


class XWAuth(ABaseAuth):
    """
    Main xwauth facade.
    Provides OAuth 2.0 authentication and authorization capabilities
    with comprehensive provider support and security features.
    Convenience initialization:
        >>> # Option 1: Direct convenience API (DX-friendly)
        >>> auth = XWAuth(
        ...     backend="local",
        ...     format="xwjson",
        ...     address="data/xwauth.xwjson",
        ...     jwt_secret="your-secret-key"
        ... )
        >>> # Option 2: Storage as XWStorage instance
        >>> storage = XWStorage(backend="local", format="xwjson", address="data/xwauth.xwjson")
        >>> auth = XWAuth(storage=storage, jwt_secret="your-secret-key")
        >>> # Option 3: Storage as dictionary
        >>> auth = XWAuth(
        ...     storage={"backend": "local", "format": "xwjson", "address": "data/xwauth.xwjson"},
        ...     jwt_secret="your-secret-key"
        ... )
        >>> # Advanced API (full control)
        >>> config = XWAuthConfig(jwt_secret="your-secret-key")
        >>> storage = MyStorageProvider()
        >>> auth = XWAuth(config=config, storage=storage)
    """

    def __init__(
        self,
        config: XWAuthConfig | None = None,
        storage: IStorageProvider | None = None,
        # Convenience parameters (DX-friendly API)
        backend: str | None = None,
        format: str | None = None,  # noqa: A002
        address: str | None = None,
        jwt_secret: str | None = None,
        jwt_algorithm: str = "HS256",
        **kwargs
    ):
        """
        Initialize xwauth.
        Args:
            config: Optional configuration object (advanced API)
            storage: Optional storage provider (advanced API). Can be:
                - IStorageProvider instance
                - XWStorage instance (will be converted)
                - dict with {"backend", "format", "address"} keys (convenience API)
            # Convenience parameters (simple API)
            backend: Storage backend type ("local", "file", etc.) - creates storage automatically
            format: Storage format ("xwjson", "json", etc.)
            address: Storage address/path (file path, URL, etc.)
            jwt_secret: JWT secret key (required if config not provided)
            jwt_algorithm: JWT algorithm (default: "HS256")
            **kwargs: Additional configuration options
        """
        # Handle convenience API (backend/format/address)
        if backend is not None or format is not None or address is not None:
            # Convenience API detected - create storage and config automatically
            if jwt_secret is None:
                raise XWAuthError(
                    "jwt_secret is required when using convenience API (backend/format/address)",
                    error_code="JWT_SECRET_REQUIRED",
                    suggestions=["Provide jwt_secret parameter"]
                )
            # Create storage provider from convenience parameters
            storage = self._create_storage_from_params(backend, format, address)
            # Create config from convenience parameters
            config = XWAuthConfig(
                jwt_secret=jwt_secret,
                jwt_algorithm=jwt_algorithm,
                storage_provider=storage,
                **kwargs
            )
        # Handle storage parameter - accept XWStorage and convert to IStorageProvider
        if storage:
            # Check if storage is XWStorage instance and convert to IStorageProvider
            storage = self._normalize_storage(storage)
            self._storage = storage
            # If config not provided but jwt_secret is, create config
            if config is None and jwt_secret:
                config = XWAuthConfig(
                    jwt_secret=jwt_secret,
                    jwt_algorithm=jwt_algorithm,
                    storage_provider=storage,
                    **kwargs
                )
        elif config and config.storage_provider:
            self._storage = config.storage_provider
        else:
            self._storage = MockStorageProvider()
            logger.info("Using MockStorageProvider (independent development mode)")
        # Use provided config or create default
        if config:
            self._config = config
        else:
            # Create default config (requires jwt_secret)
            if jwt_secret:
                # Create config from jwt_secret if provided
                config = XWAuthConfig(
                    jwt_secret=jwt_secret,
                    jwt_algorithm=jwt_algorithm,
                    storage_provider=self._storage,
                    **kwargs
                )
                self._config = config
            else:
                raise XWAuthError(
                    "Configuration required. Provide XWAuthConfig with jwt_secret or jwt_secret parameter.",
                    error_code="CONFIG_REQUIRED",
                    suggestions=["Create XWAuthConfig with jwt_secret parameter or provide jwt_secret directly"]
                )
        # Initialize components
        from .core.oauth2 import OAuth2Server
        from .core.oidc import OIDCProvider
        from .tokens.manager import TokenManager
        self._oauth2_server = OAuth2Server(self)
        self._oidc_provider = OIDCProvider(self)
        self._token_manager = TokenManager(self, use_jwt=True)
        self._policy_decision = PolicyDecisionService()
        self._audit_manager = AuditLogManager(self)
        self._hook_registry = AuthHookRegistry()
        from .federation.idp_registry import TenantScopedIdpRegistry

        self.tenant_idp_registry = TenantScopedIdpRegistry(self, persist=False)
        from .sessions.manager import SessionManager
        self._session_manager = SessionManager(self)
        self._webauthn_challenge_store = create_webauthn_challenge_store(self._config)
        self._webauthn_credential_index_redis = create_webauthn_credential_index_redis(self._config)
        from .providers.registry import ProviderRegistry
        self._provider_registry = ProviderRegistry()
        _jwks_ttl = int(getattr(self._config, "federation_jwks_cache_ttl_seconds", 3600) or 0)
        _jwks_neg = int(getattr(self._config, "federation_jwks_negative_cache_seconds", 20) or 0)
        self._federation_broker = FederationBroker(
            self._provider_registry,
            jwks_cache_ttl_seconds=_jwks_ttl,
            jwks_negative_cache_ttl_seconds=_jwks_neg,
        )
        self._scim_users = ScimService(resource_type="User", default_schema=SCIM_USER_SCHEMA)
        self._scim_groups = ScimService(resource_type="Group", default_schema=SCIM_GROUP_SCHEMA)
        logger.info("XWAuth initialized")
    @staticmethod

    def _normalize_storage(storage: Any) -> IStorageProvider:
        """
        Normalize storage to IStorageProvider.
        Converts XWStorage instances, dictionaries, or other types to IStorageProvider if needed.
        Args:
            storage: Storage instance (XWStorage, IStorageProvider, dict, etc.)
        Returns:
            IStorageProvider instance
        """
        # If already IStorageProvider, return as-is
        if isinstance(storage, IStorageProvider):
            return storage
        # Handle dictionary (convenience API)
        if isinstance(storage, dict):
            # Extract parameters from dict
            backend = storage.get("backend") or storage.get("connector")
            format_param = storage.get("format")
            address = storage.get("address")
            # Create storage from dict parameters
            return XWAuth._create_storage_from_params(backend, format_param, address)
        # Try to convert XWStorage to IStorageProvider
        try:
            from exonware.xwstorage import XWStorage as XWStorageClass
            if isinstance(storage, XWStorageClass):
                # Try to use XWStorageProvider adapter if available
                try:
                    from exonware.xwauth.storage.xwstorage_provider import XWStorageProvider
                    return XWStorageProvider(storage)
                except (ImportError, AttributeError):
                    # XWStorageProvider not available - create a simple adapter
                    logger.warning(
                        "XWStorageProvider not found. Creating temporary adapter. "
                        "For production use, implement XWStorageProvider or use IStorageProvider directly."
                    )
                    # Return a mock for now - user should implement proper adapter
                    return MockStorageProvider()
        except ImportError:
            pass
        # If we can't convert, check if it's already compatible
        # (duck typing - if it has the right methods, use it)
        if hasattr(storage, 'save_user') and hasattr(storage, 'get_user'):
            logger.info("Using storage with duck typing (not a formal IStorageProvider)")
            return storage  # type: ignore
        # Fallback to mock
        logger.warning(
            f"Storage type {type(storage)} is not compatible with IStorageProvider. "
            "Falling back to MockStorageProvider."
        )
        return MockStorageProvider()
    @staticmethod

    def _create_storage_from_params(
        backend: str | None,
        format: str | None,  # noqa: A002
        address: str | None
    ) -> IStorageProvider:
        """
        Create storage provider from convenience parameters.
        Args:
            backend: Storage backend type
            format: Storage format
            address: Storage address/path
        Returns:
            Storage provider instance
        """
        # Default to mock storage if no backend specified
        if backend is None or backend == "mock":
            logger.debug("Using MockStorageProvider (no backend specified)")
            return MockStorageProvider()
        # Try to create storage provider using xwstorage integration
        try:
            from exonware.xwstorage import XWStorage
            storage_connection = XWStorage(
                backend=backend or "local",
                format=format or "xwjson",
                address=address or "data/xwauth.xwjson",
                auth=None,
            )
            # Try to use XWStorageProvider if available
            try:
                from exonware.xwauth.storage.xwstorage_provider import XWStorageProvider
                return XWStorageProvider(storage_connection)
            except (ImportError, AttributeError):
                # XWStorageProvider not available - this is expected for now
                # The storage connection is created but we'll use MockStorageProvider
                # Users can implement XWStorageProvider or use the advanced API
                logger.info(
                    "XWStorageProvider not found. Using MockStorageProvider for now. "
                    "To enable persistent storage, implement XWStorageProvider or use "
                    "the advanced API with a custom storage provider."
                )
                return MockStorageProvider()
        except ImportError:
            logger.warning(
                "xwstorage not available, falling back to MockStorageProvider. "
                "Install exonware-xwstorage for persistent storage."
            )
            return MockStorageProvider()
        except Exception as e:
            logger.warning(
                f"Failed to create storage provider from params: {e}. "
                "Falling back to MockStorageProvider."
            )
            return MockStorageProvider()
    @property

    def storage(self) -> IStorageProvider:
        """Get storage provider."""
        return self._storage
    @property

    def config(self) -> XWAuthConfig:
        """Get configuration."""
        return self._config

    @property
    def scim_users(self) -> ScimService:
        """Get SCIM users service."""
        return self._scim_users

    @property
    def scim_groups(self) -> ScimService:
        """Get SCIM groups service."""
        return self._scim_groups

    @property
    def policy_decision_service(self) -> PolicyDecisionService:
        """Get policy decision service for explainable decisions."""
        return self._policy_decision
    # OAuth 2.0 methods

    async def authorize(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Handle authorization endpoint.
        Args:
            request: Authorization request parameters
        Returns:
            Authorization response
        """
        return await self._oauth2_server.authorize(request)

    async def token(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Handle token endpoint.
        Args:
            request: Token request parameters
        Returns:
            Token response
        """
        return await self._oauth2_server.token(request)
    # Token introspection and revocation

    async def introspect_token(self, token: str) -> dict[str, Any]:
        """
        Introspect token (RFC 7662).
        Args:
            token: Token to introspect
        Returns:
            Introspection response
        """
        return await self._token_manager.introspect_token(token)

    async def resolve_auth_context(self, token: str) -> AuthContext | None:
        """
        Resolve a bearer token into a normalized auth context.
        """
        try:
            introspection = await self._token_manager.introspect_token(token)
        except Exception:
            return None
        if not isinstance(introspection, dict) or not introspection.get("active", False):
            return None
        claims = dict(introspection)
        scope_value = claims.get("scope")
        scopes: list[str]
        if isinstance(scope_value, str):
            scopes = [scope for scope in scope_value.split(" ") if scope]
        else:
            scopes = list(claims.get("scopes") or [])
        subject_id = str(
            claims.get("subject_id")
            or claims.get("sub")
            or claims.get("user_id")
            or claims.get("client_id")
            or ""
        )
        org_claim = claims.get("org_id") or claims.get("organization_id")
        proj_claim = claims.get("project_id") or claims.get("application_id")
        if org_claim is not None:
            org_claim = str(org_claim).strip() or None
        if proj_claim is not None:
            proj_claim = str(proj_claim).strip() or None
        context = AuthContext(
            subject_id=subject_id,
            tenant_id=claims.get("tenant_id") or claims.get("tid"),
            org_id=org_claim,
            project_id=proj_claim,
            scopes=scopes,
            roles=list(claims.get("roles") or []),
            session_id=claims.get("session_id"),
            aal=claims.get("aal"),
            claims=claims,
            token_id=claims.get("token_id"),
            token_type=claims.get("token_type"),
        )
        await self._emit_extension_event(
            "auth.context_resolved",
            {
                "subject_id": context.subject_id,
                "tenant_id": context.tenant_id,
                "org_id": context.org_id,
                "project_id": context.project_id,
            },
        )
        return context

    async def revoke_token(self, token: str, token_type_hint: str | None = None) -> None:
        """
        Revoke token (RFC 7009).
        Args:
            token: Token to revoke
            token_type_hint: Optional "access_token" or "refresh_token"
        """
        await self._token_manager.revoke_token(token, token_type_hint=token_type_hint)
        await self._safe_audit_log(
            event_type="token.revoked",
            user_id=None,
            attributes={"token_type_hint": token_type_hint or "unknown"},
        )
        await self._emit_extension_event("token.revoked", {"token_type_hint": token_type_hint or "unknown"})

    def register_auth_hook(self, hook: IAuthHook) -> None:
        """Register extension hook for auth lifecycle events."""
        self._hook_registry.register(hook)

    def register_provider(self, provider: IProvider) -> None:
        """Register OAuth/OIDC provider in the canonical provider registry."""
        self._provider_registry.register(provider)

    def register_ldap_provider(self, provider_name: str, provider: Any) -> None:
        """Register LDAP provider adapter for federation broker."""
        self._federation_broker.register_ldap_provider(provider_name, provider)

    def register_saml_provider(self, provider_name: str, provider: Any) -> None:
        """Register SAML provider adapter for federation broker."""
        self._federation_broker.register_saml_provider(provider_name, provider)

    async def start_federation_login(
        self,
        provider_name: str,
        *,
        client_id: str,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
        nonce: str | None = None,
        code_verifier: str | None = None,
    ) -> str:
        """Start federation login for OAuth/OIDC providers."""
        return await self._federation_broker.start_oauth2(
            provider_name,
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            scopes=scopes or [],
            nonce=nonce,
            code_verifier=code_verifier,
        )

    async def complete_federation_login(
        self,
        provider_name: str,
        *,
        code: str,
        redirect_uri: str,
        client_id: str | None = None,
        code_verifier: str | None = None,
        expected_nonce: str | None = None,
        claim_mapping_rules: list[dict[str, Any]] | None = None,
        id_token_validation: OidcIdTokenValidationParams | None = None,
        validate_id_token: bool | None = None,
        userinfo_fallback_from_id_token: bool = True,
        verify_oidc_token_hashes: bool | None = None,
        extra_user_claims: dict[str, Any] | None = None,
    ) -> FederatedIdentity:
        """
        Complete OAuth/OIDC callback exchange and return normalized federated identity.

        *extra_user_claims*: optional claims from the authorization callback (e.g. Apple's
        OIDC-style form_post ``user`` payload from your integration layer)
        merged after userinfo and id_token fallback so signed claims stay authoritative.
        """
        v_hashes = verify_oidc_token_hashes
        if v_hashes is None:
            v_hashes = bool(getattr(self._config, "federation_verify_oidc_token_hashes", True))
        return await self._federation_broker.complete_oauth2(
            provider_name,
            code=code,
            redirect_uri=redirect_uri,
            client_id=client_id,
            code_verifier=code_verifier,
            expected_nonce=expected_nonce,
            claim_mapping_rules=claim_mapping_rules,
            id_token_validation=id_token_validation,
            validate_id_token=validate_id_token,
            userinfo_fallback_from_id_token=userinfo_fallback_from_id_token,
            verify_oidc_token_hashes=v_hashes,
            extra_user_claims=extra_user_claims,
        )

    async def issue_federated_user_tokens(
        self,
        *,
        user_id: str,
        client_id: str | None = None,
        scopes: list[str] | None = None,
        tenant_id: str | None = None,
        auth_method: str = "federated_sso",
    ) -> dict[str, Any]:
        """
        Issue access and refresh tokens bound to a user session after external IdP success
        (SAML ACS, LDAP bind, OIDC userinfo), without using the client_credentials grant.
        """
        cid = client_id or getattr(self._config, "federated_sso_client_id", "saml_sso")
        scopes = scopes or list(self._config.default_scopes or ["openid", "profile", "email"])
        session_id = await self._session_manager.create_session(user_id)
        extra: dict[str, Any] = {"auth_method": auth_method, "amr": [auth_method]}
        if tenant_id:
            extra["tenant_id"] = tenant_id
        access = await self._token_manager.generate_access_token(
            user_id=user_id,
            client_id=cid,
            scopes=scopes,
            session_id=session_id,
            additional_claims=extra,
        )
        refresh = await self._token_manager.generate_refresh_token(
            user_id=user_id,
            client_id=cid,
            access_token=access,
        )
        return {
            "token_type": "Bearer",
            "access_token": access,
            "refresh_token": refresh,
            "expires_in": self._config.access_token_lifetime,
            "scope": " ".join(scopes),
            "session_id": session_id,
        }

    async def authenticate_federated_ldap(
        self,
        provider_name: str,
        *,
        username: str,
        password: str,
    ) -> FederatedIdentity:
        """Authenticate against LDAP provider and return normalized federated identity."""
        return await self._federation_broker.authenticate_ldap(
            provider_name,
            username=username,
            password=password,
        )

    async def start_federation_saml(self, provider_name: str, *, relay_state: str) -> str:
        """Start SAML login by creating an IdP redirect URL."""
        return await self._federation_broker.start_saml(provider_name, relay_state=relay_state)

    async def complete_federation_saml(
        self,
        provider_name: str,
        *,
        saml_response: str,
        relay_state: str | None = None,
    ) -> FederatedIdentity:
        """Complete SAML callback and return normalized federated identity."""
        return await self._federation_broker.complete_saml(
            provider_name,
            saml_response=saml_response,
            relay_state=relay_state,
        )

    async def check_permission_context(self, context: AuthContext, resource: str, action: str) -> bool:
        """
        Centralized runtime authorization decision based on resolved AuthContext.
        """
        allowed = await self._policy_decision.evaluate(context, resource=resource, action=action)
        await self._safe_audit_log(
            event_type="authz.decision",
            user_id=context.subject_id or None,
            attributes={
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "tenant_id": context.tenant_id,
            },
        )
        await self._emit_extension_event(
            "authz.decision",
            {
                "subject_id": context.subject_id,
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "tenant_id": context.tenant_id,
            },
        )
        return allowed

    async def device_authorization(
        self, request: dict[str, Any], verification_uri_base: str | None = None
    ) -> dict[str, Any]:
        """
        Handle device authorization endpoint (RFC 8628).
        Args:
            request: client_id, optional scope
            verification_uri_base: Base URL for verification_uri
        Returns:
            device_code, user_code, verification_uri, expires_in, interval
        """
        return await self._oauth2_server.device_authorization(
            request, verification_uri_base=verification_uri_base
        )

    async def get_userinfo(self, access_token: str) -> dict[str, Any]:
        """OIDC UserInfo: requires an active access token (same validity as RFC 7662 introspection)."""
        token = (access_token or "").strip()
        if not token:
            raise XWOAuthError(
                "Missing access token",
                "invalid_token",
                error_description="The access token is missing or empty",
            )
        info = await self._token_manager.introspect_token(token)
        if not isinstance(info, dict) or not info.get("active"):
            raise XWOAuthError(
                "Invalid or expired access token",
                "invalid_token",
                error_description="The access token is invalid, expired, or revoked",
            )
        sub = info.get("sub") or info.get("username") or info.get("client_id")
        if sub is None or str(sub).strip() == "":
            raise XWOAuthError(
                "Access token has no subject",
                "invalid_token",
                error_description="The access token cannot be mapped to an end-user or client subject",
            )
        claims: dict[str, Any] = {"sub": str(sub)}
        email = info.get("email")
        if email:
            claims["email"] = email
            if "email_verified" in info:
                claims["email_verified"] = bool(info["email_verified"])
        name = info.get("name")
        if name:
            claims["name"] = name
        picture = info.get("picture")
        if picture:
            claims["picture"] = picture
        return claims
    
    async def _safe_audit_log(
        self,
        event_type: str,
        user_id: str | None = None,
        attributes: dict[str, Any] | None = None,
        *,
        tenant_id: str | None = None,
        org_id: str | None = None,
        project_id: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        try:
            await self._audit_manager.log_event(
                event_type=event_type,
                user_id=user_id,
                attributes=attributes or {},
                tenant_id=tenant_id,
                org_id=org_id,
                project_id=project_id,
                correlation_id=correlation_id or get_audit_correlation_id(),
            )
        except Exception:
            # Audit must not break auth flow.
            pass

    async def _emit_extension_event(self, event: str, payload: dict[str, Any]) -> None:
        try:
            await self._hook_registry.emit(event=event, payload=payload)
        except Exception:
            # Extension failures are isolated from core auth.
            pass
    # Authentication methods (to be implemented in Phase 0.6)
    # async def authenticate_email_password(self, email: str, password: str) -> User: ...
    # async def authenticate_magic_link(self, token: str) -> User: ...
    # Authorization methods (to be implemented in Phase 0.7)
    # async def check_permission(self, user_id: str, resource: str, action: str) -> bool: ...
    # async def get_user_roles(self, user_id: str) -> list[Role]: ...
