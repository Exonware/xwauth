# REF_26 — Integrator security checklist

**Audience:** Teams embedding `xwauth` / `xwlogin` / `xwauth-connector-api` in production.  
**Goal:** Reduce auth incidents from **integration mistakes** (not library defects alone).

Use this as a release gate for your environment. It does not replace a full threat model or pen test.

## Tokens and sessions

- [ ] Access tokens are **short-lived**; refresh rotation policy is defined and tested.
- [ ] Refresh tokens are **bound** to client + user context as appropriate; reuse detection is defined.
- [ ] Token storage in browsers follows your threat model (**HttpOnly** cookies vs memory; avoid localStorage for bearer tokens in XSS-prone apps unless justified).
- [ ] **Clock skew** budget documented for JWT `exp`/`nbf` and federation assertions.

## OAuth / OIDC client hygiene

- [ ] **Redirect URI** allowlist is exact-match (no open prefixes); native app loopback documented if used.
- [ ] **PKCE** required for public clients; confidential clients use approved auth methods only.
- [ ] **State** parameter validated on every authorization code return; CSRF on login forms if cookie-based.

## Federation and outbound HTTP

- [ ] Outbound calls to IdPs use **pinned TLS** or corporate proxy policy; **SSRF** controls on any “fetch URL” features.
- [ ] JWKS fetch caching and **key rollover** tested (old kid still valid until cutover).
- [ ] Issuer / audience checks enforced for inbound and outbound tokens.

## WebAuthn / MFA

- [ ] `rp_id` and **origin allowlist** match deployed hostnames; no wildcard origins in production.
- [ ] Step-up / AAL policy matches asset sensitivity (see [REF_MFA_WEBAUTHN_THREAT_MODEL.md](REF_MFA_WEBAUTHN_THREAT_MODEL.md)).

## Operations

- [ ] **Secrets** (signing keys, client secrets) in a secret manager; rotation runbook exists.
- [ ] **Structured logs** do not include raw tokens or passwords; PII minimization applied.
- [ ] **Rate limits** and lockouts enabled at the edge and/or AS (credential stuffing).

## Supply chain

- [ ] Dependency pins or lockfile reviewed for auth-related packages (`cryptography`, `authlib`, `PyJWT`, etc.).
- [ ] Upgrade path for security releases understood (see [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md)).

---

*Extend with tenant-specific controls when multi-tenant SaaS is in scope.*
