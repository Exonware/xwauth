# Architecture Reference â€” xwauth (XWOAuth)

**Library:** exonware-xwauth-connector  
**Last Updated:** 08-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)  
**Producing guide:** GUIDE_13_ARCH. Per REF_35_REVIEW.

---

## Overview

**XWOAuth (xwauth)** is a **centralized, universal authorization system** in three parts: (1) **Backend library** (exonware-xwauth-connector) for OAuth 1, OAuth 2, OIDC, SAML, future standards (e.g. DCE), tokens, sessions, **100+ connectors**, RBAC/ABAC/ReBAC/FGA; (2) **Authorization system with APIs** â€” OAuth/OIDC endpoints, user/session APIs, discovery; (3) **User interfaces** for login and admin flows. The library follows contracts/base/facade and provider abstraction. **Performance:** Use everything available in Exonware libraries for highest efficiency; extremely fast, really small footprint, really powerful.

---

## Boundaries

- **Public API:** Auth facades (XWAuth), token/session APIs, provider adapters, connector registry (target **â‰¥100 connectors**).
- **API layer:** Routes and endpoints (see REF_15_API, _archive/api); authorization and token endpoints, userinfo, discovery, device authorization (RFC 8628).
- **Providers/connectors:** Pluggable implementations; consistent interface; **â‰¥100 connectors** (current ~64); social, enterprise, gaming, AI, payments, etc.
- **Sessions / tokens:** Encrypted storage, lifecycle, validation; JWT and opaque; introspection (RFC 7662), revocation (RFC 7009).
- **Integration:** xwentity (users/roles), xwstorage.connect (persistence), xwaction (workflow/security), xwbase; all future Exonware APIs. **Backward:** Extend auth provider for legacy systems.

---

## Layering

1. **Contracts:** Auth and provider interfaces.
2. **Base:** Abstract auth and provider implementations.
3. **Facade:** Public auth API and high-level flows (extremely short, seamless DX).
4. **API:** REST endpoints (when used as server); delegates to library.
5. **Providers:** Per-provider adapters (OAuth1/OAuth2/OIDC/SAML); registry; **â‰¥100 connectors**.

---

## Standards and Extensibility

- **Supported today:** OAuth 1 (RFC 5849), OAuth 2 (RFC 6749, PKCE, PAR, DCR), OIDC, SAML, device code (RFC 8628), token exchange (RFC 8693), RFC 7521/7662/7009/9068/9101/9207/9126.
- **Future:** New standards as they emerge (e.g. DCE); no cap on standards or connector count.
- **Pattern:** Pluggable connectors; registry; lazy/optional loading to keep footprint small while supporting 100+ connectors.

---

## Delegation and Dependencies

- **xwentity:** User, role, permission entities.
- **xwstorage.connect:** User/session persistence (optional; interface-based to avoid circular deps).
- **xwaction:** Security and workflow handlers in decorated operations.
- **xwbase / Exonware libs:** Use for performance and DX (extremely fast, highest efficiency).

---

## xwauth-server

The **xwauth-server** stub exposes OAuth 2.0/OIDC (and OAuth1/SAML where applicable) endpoints and delegates to exonware-xwauth-connector. Scope: authorization server, token endpoint, userinfo, discovery; see xwauth-server/docs/REF_22_PROJECT.md.

---

*See REF_15_API.md and deployment guides for API and deployment. Requirements: REF_01_REQ.md, REF_22_PROJECT.md.*


