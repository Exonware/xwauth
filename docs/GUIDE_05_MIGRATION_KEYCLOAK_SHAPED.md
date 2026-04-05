# GUIDE_05 — Migration playbook (Keycloak-shaped deployments)

**Audience:** Teams replacing or complementing a **Keycloak-style** realm (OIDC/OAuth2, clients, users, optional SAML).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#4**.  
**Not** a one-click migrator — a **checklist** to avoid silent security regressions.  
**Other IdPs:** [GUIDE_06_MIGRATION_AUTH0_SHAPED.md](GUIDE_06_MIGRATION_AUTH0_SHAPED.md) · [GUIDE_07_MIGRATION_SUPABASE_SHAPED.md](GUIDE_07_MIGRATION_SUPABASE_SHAPED.md).

---

## 1. Inventory (before cutover)

| Area | Keycloak concept | XW mapping |
|------|------------------|------------|
| **Issuer / realm** | Realm URL | Single issuer URL + `XWAuthConfig` / discovery |
| **Clients** | Confidential / public, redirect URIs, PKCE | `registered_clients` or `XWAUTH_API_REGISTERED_CLIENTS_JSON` |
| **Scopes / roles** | Realm / client scopes | `default_scopes`, custom scopes, B2B org claims |
| **Users** | User federation / LDAP | Your user store + xwentity / custom adapters |
| **Sessions** | SSO session length | `session_timeout`, token lifetimes |
| **Admin** | Admin API | xwauth admin routes + your RBAC |

---

## 2. Clients and redirects

1. Export **exact** redirect URI allow lists — Keycloak often accumulates dev URIs; **re-validate** against OAuth 2.1 exact match.  
2. Map **public** clients → PKCE **S256** (connector defaults align with OAuth 2.1-style strictness in profile A/B).  
3. Map **confidential** clients → `client_secret` in secure storage; rotate before go-live.

---

## 3. Tokens and claims

1. Document **access token** lifetime and **refresh** rotation behavior today vs target (`access_token_lifetime`, `refresh_token_lifetime`, env overrides on xwauth-api).  
2. List **custom claims** apps depend on (`org_id`, `tenant_id`, etc.) and add them to your token / introspection path in XW.  
3. Align **clock skew** and `iss` / `aud` expectations (see [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md) for IdP-side quirks; your AS is now “local”).

---

## 4. Federation (if Keycloak brokered upstream IdPs)

1. Re-register **SAML** or **OIDC** upstream metadata in xwauth federation config.  
2. Re-test **logout**, **nonce**, and **account linking** flows.  
3. Run a **parallel issuer** (different subdomain) during pilot so clients can switch `issuer`/`authority` with config only.

---

## 5. Data migration

- **Authorization codes / refresh tokens** do not portable-migrate — plan a **session re-login** window.  
- **Password hashes** — import only if algorithms match your `PasswordHashAlgorithm` configuration; otherwise force password reset or email magic link.

---

## 6. Validation

1. **Conformance:** run your existing OIDC tests against the new issuer (see `REF_53` / CI protocol workflows in repo).  
2. **Load:** exercise `/authorize` and `/token` at expected QPS with WAF/proxy in path.  
3. **Rollback:** keep Keycloak read-only until burn-in completes; document issuer URL rollback in [GUIDE_03_HA_UPGRADE_RUNBOOK.md](GUIDE_03_HA_UPGRADE_RUNBOOK.md).

---

## Expand next

- **Field mapping:** [REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md](REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md) (Keycloak → `registered_clients`).  
- **Auth0 / Supabase:** [GUIDE_06](GUIDE_06_MIGRATION_AUTH0_SHAPED.md) · [GUIDE_07](GUIDE_07_MIGRATION_SUPABASE_SHAPED.md).
