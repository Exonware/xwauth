<!-- docs/GUIDE_01_USAGE.md (project usage, GUIDE_41_DOCS) -->
# xwauth — Usage Guide

**Last Updated:** 07-Feb-2026

How to use xwauth (output of GUIDE_41_DOCS; project-local guide).

---

## Quick start

See [REF_15_API.md](REF_15_API.md) for API and code examples. Installation and configuration: see repo README.md.

## Facade-first integration pattern

Use `XWAuth` as the only auth-domain entry point; avoid calling token/session/storage internals directly.

- `xwauth` owns identity/authentication/authorization decisions.
- `xwapi` should consume resolved auth context via provider adapters.
- `xwstorage` should consume policy context and remain persistence-focused.

Example flow:

1. API middleware resolves bearer token via `resolve_auth_context`.
2. Authorization checks route through `check_permission_context`.
3. Storage filters consume normalized tenant/user/role context.

## Federation broker usage

`XWAuth` exposes broker-backed federation methods for consistent OAuth/OIDC + LDAP normalization:

- `start_federation_login(...)`
- `complete_federation_login(...)`
- `authenticate_federated_ldap(...)`
- `start_federation_saml(...)`
- `complete_federation_saml(...)`

This keeps provider-specific claims mapping out of API handlers and centralizes identity normalization.

## Detailed guides (archived)

The following project-specific guides were consolidated per GUIDE_41_DOCS; originals are in `docs/_archive/guides/`:

- **Quickstart:** _archive/guides/GUIDE_QUICKSTART_XWAUTH.md  
- **Usage:** _archive/guides/GUIDE_USAGE_XWAUTH.md  
- **Security:** _archive/guides/GUIDE_SECURITY_XWAUTH.md  
- **Provider integration:** _archive/guides/GUIDE_PROVIDER_INTEGRATION_XWAUTH.md  

Endpoint reference and deployment (Docker, Kubernetes, production): _archive/api/, _archive/deployment/.

---

*Per GUIDE_00_MASTER and GUIDE_41_DOCS. API: REF_15_API.md. Requirements: REF_22_PROJECT.md.*
