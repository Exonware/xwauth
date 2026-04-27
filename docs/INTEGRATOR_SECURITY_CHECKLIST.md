# Integrator security checklist

**Audience:** Teams deploying **xwauth** (connector), **xwlogin** (login provider), and **xwauth-connector-api** (reference AS).  
**Companion:** [SECURITY.md](SECURITY.md) (reporting policy) Â· [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md).

Use this before production. It does not replace your own threat modeling.

---

## Before production

1. **Secrets** â€” Replace any demo `jwt_secret`; load from a secrets manager. Reference server defaults are **not** production-safe (see `XWAUTH_API_JWT_SECRET` in xwauth-connector-api `.env.example`). Set `XWAUTH_API_DEPLOYMENT_PROFILE=production` so the runner **refuses** the demo secret and the in-process **`DEFAULT_TEST_CLIENTS`** list; use **`XWAUTH_API_REGISTERED_CLIENTS_JSON`** (JSON array file path) for real OAuth clients. Optionally cap token lifetimes via `XWAUTH_API_ACCESS_TOKEN_LIFETIME_SECONDS` / `XWAUTH_API_REFRESH_TOKEN_LIFETIME_SECONDS` (bounded; invalid values are ignored with a log warning).
2. **Clients** â€” Replace harness `DEFAULT_TEST_CLIENTS` with a real client registry; enforce `client_secret` / PKCE / mTLS per client type.
3. **Redirect URIs** â€” Exact-match allow lists; no open wildcards on untrusted hosts.
4. **TLS** â€” Terminate TLS in front of the AS; no token endpoints on plain HTTP except local dev.
5. **Storage** â€” Use durable persistence (**xwstorage.connect** or equivalent) with backup/restore runbooks.
6. **Browser / CORS / cookies** â€” Prefer **BFF** or same-site patterns so tokens are not exposed to arbitrary web origins. If SPAs call the AS cross-origin, set an **explicit** allow-list (see xwauth-connector-api `XWAUTH_API_CORS_ORIGINS`); avoid `*` with `Access-Control-Allow-Credentials`. Stock **xwauth** handlers do **not** emit `Set-Cookie` today; if you extend flows to use session cookies, set `Secure`, `HttpOnly`, and `SameSite` appropriately (see [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md) for edge context).
7. **Federation** â€” Validate `iss`, JWKS, `nonce`, clock skew; allow-list upstream IdPs.
8. **Logging** â€” Never log access tokens, refresh tokens, or passwords; use correlation IDs (xwauth-connector-api ops headers).
9. **Dependencies** â€” Pin and audit (`pip audit`, OSV); keep `cryptography`, `PyJWT`, SAML stack updated.
10. **Abuse** â€” Rate-limit `authorize`, `token`, and password grants at gateway or application layer.

---

## Threat model (sketch)

| Asset | Risks |
|-------|--------|
| Tokens / codes | Theft via XSS, logs, misconfigured storage |
| Signing keys | Forgery if leaked â€” rotation and short-lived keys |
| Client registry | Impersonation â€” strict registration and secrets |
| Federation URLs | SSRF / metadata poisoning â€” validate URLs and TLS |

Expand per deployment (B2B SaaS, on-prem AD bridge, mobile, etc.).

**Roadmap:** [../.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item 9.


