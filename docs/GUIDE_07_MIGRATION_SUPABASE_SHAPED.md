# GUIDE_07 — Migration playbook (Supabase Auth–shaped deployments)

**Audience:** Teams using **Supabase Auth (GoTrue)** for JWT-based API access and social/email login, considering a **self-hosted** OAuth/OIDC AS (xwauth stack).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#4**.

---

## 1. Mental model shift

| Supabase | XW stack |
|----------|----------|
| **JWT** from GoTrue with `anon` / `service_role` for PostgREST | **OAuth/OIDC AS** issues tokens for **clients**; your **API** validates JWT or introspects — wire explicitly. |
| **RLS** in Postgres | Still in **Postgres**; AS does not replace RLS — map `sub` / `role` claims consistently. |
| **Hosted Auth UI** | You provide UI + xwlogin / BFF patterns ([GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md](GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md)). |

---

## 2. Clients

1. Map **Supabase “URL config”** (site URL, redirect URLs) to **registered** `redirect_uris` on the AS.  
2. **Public** mobile/SPA clients → **PKCE**; avoid embedding long-lived secrets in apps.  
3. **Service role** usage → **confidential** server clients with `client_credentials` or server-side code with stored secret — never ship service-role equivalent to browsers.

---

## 3. Claims and users

1. List every **JWT claim** your RLS policies and APIs depend on (`sub`, `email`, `role`, `app_metadata`, etc.).  
2. Recreate **custom claims** in XW token / introspection path; test **one** representative policy in staging.  
3. **User IDs:** `sub` should be stable across migration or plan a **mapping table** for foreign keys.

---

## 4. Storage

- Supabase stores users in **PostgREST-accessible** tables; XW often uses **xwentity** / your DB. Plan **ETL** or **lazy migration** on first login.

---

## 5. Social / magic link

- Reconfigure **OAuth** upstreams and **email** delivery (see [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md)) to match production SPF/DKIM/DMARC.

---

## 6. Cutover

1. **Dual-run** issuers; switch API **JWKS** / validation to the new issuer when ready.  
2. Invalidate old Supabase sessions by shortening TTL before cutover if possible.

---

## Expand next

- **Client registry:** [REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md](REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md) (what maps vs what stays on Supabase as IdP).  
- Example **claim mapping** table: Supabase JWT → XW access token claims.
