# REF_64 — Client registry field mapping (migration to `registered_clients`)

**Purpose:** Map **Keycloak**, **Auth0**, and **Supabase-shaped** sources into the **XW authorization server** client registry shape used by `xwauth` / `xwauth-api` (env `XWAUTH_API_REGISTERED_CLIENTS_JSON`, file mount, or in-process `registered_clients`).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#4**.  
**Related:** [GUIDE_05](GUIDE_05_MIGRATION_KEYCLOAK_SHAPED.md) · [GUIDE_06](GUIDE_06_MIGRATION_AUTH0_SHAPED.md) · [GUIDE_07](GUIDE_07_MIGRATION_SUPABASE_SHAPED.md).

---

## 1. Target shape (reference server / xwauth)

Each entry is one OAuth **client** the AS knows about. Minimal fields:

| Field | Type | Notes |
|-------|------|--------|
| `client_id` | string | Public identifier; must match `client_id` in token and authorize requests. |
| `client_secret` | string | **Confidential** clients only; omit or empty for **public** clients (use PKCE). |
| `redirect_uris` | list of strings | Exact-match redirect allow list (OAuth 2.1-style strictness in profile A/B). |

Example JSON array (suitable for `XWAUTH_API_REGISTERED_CLIENTS_JSON` or a mounted file):

```json
[
  {
    "client_id": "my-spa",
    "redirect_uris": ["https://app.example.com/oauth/callback"]
  },
  {
    "client_id": "my-backend-job",
    "client_secret": "<from secret manager>",
    "redirect_uris": ["https://api.example.com/oauth/callback"]
  }
]
```

**Not** mapped here: scopes, grant-type allow lists, token lifetimes, PKCE enforcement flags — those live in **AS config** and **protocol profile** settings, not in the per-client secret blob alone.

---

## 2. Keycloak → `registered_clients`

Sources: **Admin Console** (Clients → *client*), **`realm-export.json`** client objects, or **Admin REST** `GET /admin/realms/{realm}/clients/{id}`.

| Keycloak field / concept | `registered_clients` |
|--------------------------|----------------------|
| `clientId` | `client_id` |
| `redirectUris` | `redirect_uris` (copy list; trim and de-duplicate) |
| `secret` (Credentials tab / `credentials` in export) | `client_secret` if **confidential** |
| `publicClient: true` | Omit `client_secret`; require **PKCE S256** for code flow |
| `webOrigins` | **Not** `redirect_uris` — keep CORS/origin policy in **API gateway** / `XWAUTH_API_CORS_*`; only true redirect URLs go in `redirect_uris` |

**Multi-client export:** iterate each realm client with `standardFlowEnabled` or relevant grant usage; skip **service-account-only** clients if you register them under **client credentials** config elsewhere.

---

## 3. Auth0 → `registered_clients`

Sources: **Dashboard** (Application settings) or **Management API** `GET /api/v2/clients/{client_id}`.

| Auth0 field | `registered_clients` |
|-------------|----------------------|
| `client_id` | `client_id` |
| `client_secret` | `client_secret` (omit if application type is **Native** / public) |
| `callbacks` | `redirect_uris` |
| `initiate_login_uri` | **Not** a redirect URI for OAuth callback — do not merge into `redirect_uris` unless it is literally a registered redirect |
| Application type **Regular Web** | Typically confidential → include `client_secret` |
| Application type **SPA** / **Native** | Public → omit secret; PKCE |

**Rotations:** after importing, rotate Auth0-side secrets once if the export lived in ticketing/email; store final secret in **secret manager** and reference via env / K8s Secret.

---

## 4. Supabase → `registered_clients` (and what does *not* map)

Supabase **Auth** is primarily an **IdP / user JWT issuer** for your project. Its dashboard **OAuth providers** (Google, GitHub, …) are **upstream IdPs**, not the same thing as **first-party OAuth clients** of *your* authorization server.

| Scenario | Mapping |
|----------|---------|
| You run **XW as the AS** for your product | Define **`registered_clients`** on XW for each **first-party** web/mobile/backend client; Supabase does not supply this list. |
| You still validate **Supabase-issued JWTs** on APIs | Use Supabase **JWKS** / project JWT settings in your **resource server** — parallel to XW client registry; see [GUIDE_07](GUIDE_07_MIGRATION_SUPABASE_SHAPED.md) for cutover. |
| “Sign in with Supabase” as social on XW | Configure **federation / upstream OIDC** in xwlogin/xwauth stack — **not** a row in `registered_clients`. |

If you previously stored **custom OAuth client metadata** in Supabase (Edge Functions, tables), map those rows manually to the table in §1 using your own column names.

---

## 5. Validation checklist

1. **Exact redirect URIs** — no wildcards unless your AS explicitly supports them (default XW posture: exact match).  
2. **Public vs confidential** — wrong classification leaks secrets or breaks PKCE expectations.  
3. **One row per AS client** — duplicate `client_id` values must be resolved before load.  
4. **Secrets** — never commit real `client_secret` values; use K8s Secret + file mount or secret manager injection for `XWAUTH_API_REGISTERED_CLIENTS_JSON`.

---

*Per GUIDE_41_DOCS; extend with vendor-specific export samples as you harden migrations.*
