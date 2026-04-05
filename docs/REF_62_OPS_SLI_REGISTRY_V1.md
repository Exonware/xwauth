# REF_62 — Ops SLI Registry (v1)

**Project:** `xwauth`  
**Last Updated:** 02-Apr-2026  
**Status:** Baseline seed for Phase 0/1; **CI parity** with `xwauth-api` (see §5)

---

## 1) Purpose

Provide a stable endpoint-family to SLI map that can be populated from `xwauth-api` route registration and used by dashboards, alerting, and scorecards.

This is a contract-first baseline. Metric wiring follows in implementation phases.

---

## 2) SLI Families

**CI:** `exonware-xwauth-api` runs `tests/0.core/test_sli_registry_parity.py`; every `route_family` produced for `AUTH_SERVICES` must appear in this table. Canonical set in code: `exonware.xwauth_api.sli_catalog.SLI_REGISTRY_V1_ROUTE_FAMILIES`.

| Route family | Primary SLI | Secondary SLI | Owner | Status |
|-------------|-------------|---------------|-------|--------|
| `oauth_authorize` | Availability | p95/p99 latency | auth-core | planned |
| `oauth_token` | Availability | p95/p99 latency, error rate | auth-core | planned |
| `oauth_introspect` | Availability | p95 latency | auth-core | planned |
| `oauth_revoke` | Availability | p95 latency | auth-core | planned |
| `oidc_logout` | Availability | p95 latency | auth-core | planned |
| `oauth1` | Availability | p95 latency | auth-core | planned |
| `dcr` | Availability | latency | auth-core | planned |
| `fga` | Availability | latency | authz | planned |
| `sessions` | Success rate | latency, revoke propagation | sessions | planned |
| `scim` | Availability | sync latency, error rate | provisioning | planned |
| `saml` | Availability | assertion-processing latency | federation | planned |
| `mfa` | Success rate | ceremony latency | security | planned |
| `passkeys` | Success rate | ceremony latency | security | planned |
| `organizations` | Availability | latency | platform | planned |
| `webhooks` | Availability | latency | platform | planned |
| `users` | Availability | latency | platform | planned |
| `admin` | Availability | latency | platform | planned |
| `system` | Availability | health endpoint latency | platform | planned |
| `auth_general` | Availability | p95 latency | auth-core | planned |

---

## 3) Critical User Journeys

Each journey should be measured by composed SLI objectives:

1. **Sign-in interactive journey**  
   route families: `oauth_authorize` -> `oauth_token`
2. **Service-to-service token journey**  
   route families: `oauth_token` (client credentials)
3. **Session continuity journey**  
   route families: `sessions` + `oauth_introspect`
4. **Provisioning journey**  
   route families: `scim`
5. **Federation sign-in journey**  
   route families: `saml` or external provider callback paths

---

## 4) Coverage Rules

- Every route registered by `AUTH_SERVICES` must map to one `route_family`.
- Every `route_family` must have at least one primary availability SLI.
- No route can remain `unclassified` at release time.

---

## 5) CI and generated evidence

- **Enforced:** `xwauth-api` workflow **core-tests** runs `pytest tests/0.core -m xwauth_api_core` (includes `test_sli_registry_parity.py`).
- **Next:** optional job to diff this markdown table against `SLI_REGISTRY_V1_ROUTE_FAMILIES`; export `/system/ops/sli-catalog` JSON as scorecard artifact.

