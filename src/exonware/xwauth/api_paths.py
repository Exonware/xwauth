# exonware/xwauth/api_paths.py
"""HTTP API path prefix constants (shared by handlers, xwauth-api, discovery)."""

API_VERSION = "v1"
OAUTH2_PREFIX = f"/{API_VERSION}/oauth2"
OIDC_PREFIX = f"/{API_VERSION}/oidc"
OAUTH1_PREFIX = f"/{API_VERSION}/oauth1"
AUTH_PREFIX = f"/{API_VERSION}/auth"
USERS_PREFIX = f"/{API_VERSION}/users"
ADMIN_PREFIX = f"/{API_VERSION}/admin"
ORGANIZATIONS_PREFIX = f"/{API_VERSION}/organizations"
WEBHOOKS_PREFIX = f"/{API_VERSION}/webhooks"
SCIM_PREFIX = f"/{API_VERSION}/scim/v2"
SYSTEM_PREFIX = f"/{API_VERSION}/system"
PATH_HEALTH = "/health"
PATH_METRICS = "/metrics"

__all__ = [
    "API_VERSION",
    "OAUTH2_PREFIX",
    "OIDC_PREFIX",
    "OAUTH1_PREFIX",
    "AUTH_PREFIX",
    "USERS_PREFIX",
    "ADMIN_PREFIX",
    "ORGANIZATIONS_PREFIX",
    "WEBHOOKS_PREFIX",
    "SCIM_PREFIX",
    "SYSTEM_PREFIX",
    "PATH_HEALTH",
    "PATH_METRICS",
]
