# REF_61 — Ops Telemetry Schema

**Project:** `xwauth`  
**Last Updated:** 02-Apr-2026  
**Status:** Schema v1 (cross-package contract)

---

## 1) Purpose

Standardize telemetry vocabulary across:

- `xwauth`
- `xwauth-api`
- `xwsystem`

This schema defines required metric names, minimum labels, and correlation fields used by metrics, traces, logs, and audit events.

---

## 2) Naming and Stability

- Metric namespace prefix: `xwauth_`
- Schema version label/value: `telemetry_schema=v1`
- Rule: additive evolution only; breaking changes require `v2`

---

## 3) RED Metrics (HTTP/API)

### Required metrics

- `xwauth_requests_total` (counter)
- `xwauth_request_duration_seconds` (histogram)
- `xwauth_errors_total` (counter)

### Required dimensions

- `route_family` (for example `oauth_token`, `oauth_authorize`, `sessions`, `scim`, `saml`, `mfa`, `passkeys`, `admin`, `system`)
- `method`
- `status_class` (`2xx`, `3xx`, `4xx`, `5xx`)
- `tier` (`A`, `B`, `C`)

Optional dimensions should be low-cardinality only.

---

## 4) USE Metrics (Dependencies)

### Required metrics

- `xwauth_dependency_requests_total` (counter)
- `xwauth_dependency_errors_total` (counter)
- `xwauth_dependency_latency_seconds` (histogram)

### Required dimensions

- `dependency` (for example `storage`, `jwks`, `idp`, `email`, `cache`)
- `operation` (high-level action name)
- `result` (`success`, `failure`, `timeout`)
- `tier` (`A`, `B`, `C`)

---

## 5) Correlation Fields (Logs/Traces/Audit)

All critical-path events must include:

- `trace_id`
- `span_id` (if tracing is active)
- `correlation_id`
- `tenant_id` (when available)
- `request_id` (HTTP scope)
- `route_family`

Security/privacy handling:

- never log raw secrets/tokens,
- redact or hash high-sensitivity identifiers when required by policy.

---

## 6) Audit Event Envelope (Minimum)

```json
{
  "schema_version": "1.0",
  "event_type": "auth.decision",
  "timestamp": "2026-04-01T00:00:00Z",
  "trace_id": "abc",
  "correlation_id": "xyz",
  "tenant_id": "tenant-a",
  "route_family": "oauth_token",
  "result": "allow"
}
```

Required envelope keys:

- `schema_version`
- `event_type`
- `timestamp`
- `trace_id` or `correlation_id` (at least one; both preferred)
- `route_family`
- `result`

---

## 7) Validation Rules

- route-family coverage must include all critical auth flows in `REF_62`.
- missing required dimensions are schema violations.
- dashboards and alerts must reference only approved metric names from this schema.

---

## 8) Audit event type catalog (v1)

**Purpose:** Stable `event_type` strings for **SIEM / SOC** export (JSON lines). All types use prefix **`xwauth.`** and **past-tense** verbs where the event records a completed decision or mutation.

**Rules:**

- Reuse the **envelope** from §6; add type-specific keys only under `details` (object) unless listed below.
- **Never** place secrets, raw tokens, authorization codes, or passwords in `details`.
- Prefer **`sub`** (subject) hashes or opaque internal user ids when policy forbids raw PII; document your redaction tier in [REF_63_AUTH_OBSERVABILITY_CONTRACT.md](REF_63_AUTH_OBSERVABILITY_CONTRACT.md).

### 8.1 OAuth / OIDC (AS)

| `event_type` | Typical `route_family` | `result` | `details` (illustrative keys) |
|--------------|------------------------|----------|--------------------------------|
| `xwauth.oauth.authorize_succeeded` | `oauth_authorize` | `allow` | `client_id`, `response_type`, `scope` (space-delimited or list) |
| `xwauth.oauth.authorize_denied` | `oauth_authorize` | `deny` | `client_id`, `error` (OAuth error code), `error_description` (sanitized) |
| `xwauth.oauth.token_issued` | `oauth_token` | `allow` | `client_id`, `grant_type`, `token_type` (e.g. `Bearer`); **no** token material |
| `xwauth.oauth.token_denied` | `oauth_token` | `deny` | `client_id`, `grant_type`, `error` (OAuth error code) |
| `xwauth.oauth.introspection_succeeded` | `oauth_introspect` | `allow` | `client_id`, `active` (boolean) |
| `xwauth.oauth.revocation_succeeded` | `oauth_revoke` | `allow` | `client_id`, `token_type_hint` if present |

### 8.2 Sessions

| `event_type` | Typical `route_family` | `result` | `details` |
|--------------|------------------------|----------|-----------|
| `xwauth.session.created` | `sessions` | `allow` | `session_id` (opaque id), `auth_method` if known |
| `xwauth.session.revoked` | `sessions` | `allow` | `session_id`, `reason` (e.g. `logout`, `admin`, `idle_timeout`) |

### 8.3 Admin & RBAC

| `event_type` | Typical `route_family` | `result` | `details` |
|--------------|------------------------|----------|-----------|
| `xwauth.admin.user_role_changed` | `admin` | `allow` | `actor_sub`, `target_sub`, `old`, `new` (role names) |
| `xwauth.admin.client_redirect_uris_changed` | `admin` | `allow` | `actor_sub`, `client_id`, `added`, `removed` (URI lists, bounded length) |

### 8.4 SCIM / provisioning

| `event_type` | Typical `route_family` | `result` | `details` |
|--------------|------------------------|----------|-----------|
| `xwauth.scim.user_created` | `scim` | `allow` | `external_id`, `id` (resource id) |
| `xwauth.scim.user_updated` | `scim` | `allow` | `id`, `changed_attributes` (attribute names only, or hashed) |
| `xwauth.scim.user_deleted` | `scim` | `allow` | `id` |
| `xwauth.scim.group_membership_changed` | `scim` | `allow` | `group_id`, `user_id`, `operation` (`add` / `remove`) |

### 8.5 Federation / SAML

| `event_type` | Typical `route_family` | `result` | `details` |
|--------------|------------------------|----------|-----------|
| `xwauth.federation.account_linked` | `saml` or `oauth_token` | `allow` | `idp_entity_id` or `provider`, `sub` |
| `xwauth.federation.assertion_rejected` | `saml` | `deny` | `idp_entity_id`, `error` (short machine code, no assertion XML) |

### 8.6 MFA / passkeys (when enabled)

| `event_type` | Typical `route_family` | `result` | `details` |
|--------------|------------------------|----------|-----------|
| `xwauth.mfa.challenge_succeeded` | `mfa` | `allow` | `method` (e.g. `totp`, `webauthn`) |
| `xwauth.mfa.challenge_failed` | `mfa` | `deny` | `method`, `failure_reason` (coarse, e.g. `bad_code`) |
| `xwauth.passkey.registration_completed` | `passkeys` | `allow` | `credential_id` (opaque) |
| `xwauth.passkey.authentication_succeeded` | `passkeys` | `allow` | `credential_id` (opaque) |

### 8.7 Security signals (aggregated / sampled)

| `event_type` | Typical `route_family` | `result` | Notes |
|--------------|------------------------|----------|--------|
| `xwauth.security.rate_limited` | any | `deny` | Log **sampled** or aggregated counts; include `client_id` or `ip_hash` per policy, not raw client_secret attempts. |

### 8.8 Versioning

- New event types are **additive** within `v1` unless semantics collide; then bump `schema_version` in the envelope (§6) and document migration in [REF_63_AUTH_OBSERVABILITY_CONTRACT.md](REF_63_AUTH_OBSERVABILITY_CONTRACT.md).

