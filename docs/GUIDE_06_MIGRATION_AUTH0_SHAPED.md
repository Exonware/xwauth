# GUIDE_06 — Migration playbook (Auth0-shaped deployments)

**Audience:** Teams moving off **Auth0** (tenant, applications, APIs, rules/actions, M2M).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#4**.  
**Companion:** [GUIDE_05_MIGRATION_KEYCLOAK_SHAPED.md](GUIDE_05_MIGRATION_KEYCLOAK_SHAPED.md) (shared OAuth/OIDC checklist patterns).

---

## 1. Inventory

| Auth0 concept | Plan in XW |
|---------------|------------|
| **Tenant / custom domain** | Public **issuer** URL + TLS at ingress (see xwauth-api Helm / [REF_33](REF_33_PARTNER_INTEGRATION_MATRIX.md)). |
| **Applications** (SPA, native, regular web, M2M) | `registered_clients` — map **grant types**, **PKCE** for public/SPA, **client_credentials** for M2M. |
| **APIs / scopes / RBAC** | `default_scopes`, custom scopes, claims in access tokens; B2B **org** claims if needed ([REF_37_MULTI_TENANT_REFERENCE_STACK.md](REF_37_MULTI_TENANT_REFERENCE_STACK.md)). |
| **Actions / Rules** | Re-implement as **hooks** / middleware in your BFF or connector-adjacent code — not 1:1 portable. |
| **Universal Login** | Replace with your hosted login UI + xwlogin handlers / IdP mixins. |

---

## 2. Clients

1. Export **callback URLs** and **allowed logout URLs** — collapse to **exact** redirect allow lists (OAuth 2.1-style strictness in profiles A/B).  
2. **Rotate** client secrets at cutover; store in Secret manager / K8s Secret.  
3. **M2M:** map to `client_credentials` with narrow scopes; rate-limit at gateway.

---

## 3. Tokens

1. Compare **access token** TTL and **refresh** behavior; set `access_token_lifetime` / env overrides on xwauth-api.  
2. If apps rely on **namespaced claims** (`https://.../roles`), map to flat or namespaced claims consistently in your token issuance path.  
3. **JWT custom claims** via Auth0 rules → implement in issuer pipeline or post-login step in XW.

---

## 4. Federation / social

- Re-register **social** and **enterprise** connections as upstream IdPs in xwauth **federation** config.  
- Test **linking** and **email verification** parity.

---

## 5. Cutover

1. Run **parallel issuer** (e.g. `auth-new.example.com`) and switch app config.  
2. **Do not** migrate refresh tokens — plan re-login.  
3. Validate with [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](REF_53_PROTOCOL_TRACEABILITY_MATRIX.md) / CI conformance jobs where applicable.

---

## Expand next

- **Field mapping:** [REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md](REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md) (Auth0 → `registered_clients`).
