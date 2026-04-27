# GUIDE_11 — SCIM 2.0 hardening (pagination, errors, idempotency)

**Audience:** Operators and integrators exposing **SCIM 2.0** (`/v1/scim/v2/*`) from **xwauth** + **xwauth-connector-api** to IdPs (Entra provisioning, Okta, etc.).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#7**.  
**Traceability:** [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](REF_53_PROTOCOL_TRACEABILITY_MATRIX.md) (SCIM row).

---

## 1. Surface and code anchors

| Area | Location |
|------|-----------|
| **HTTP routes** | `xwauth-connector-api` `AUTH_SERVICES` — `GET/POST .../scim/v2/Users`, `Groups`, `ServiceProviderConfig`, etc. (`route_family`: **`scim`** — [REF_62](REF_62_OPS_SLI_REGISTRY_V1.md)). |
| **Handlers** | `src/exonware/xwauth.connector/handlers/mixins/scim.py` — auth, paging query parsing, `If-Match`, org query guard (`org_id` vs token org). |
| **Service semantics** | `src/exonware/xwauth.connector/scim/service.py` — `list_response` (`startIndex`, `count`, `filter`), create/patch/delete. |
| **Filter / patch** | `scim/filtering.py`, `scim/patch.py` |
| **Tests** | `xwauth/tests/1.unit/scim_tests/`, `xwauth-connector-api/tests/2.integration/test_scim_policy_api.py` |

---

## 2. Pagination (`startIndex`, `count`)

| Rule | Notes |
|------|--------|
| **`startIndex`** | SCIM uses **1-based** index. Values `< 1` should yield **`400`** with SCIM Error body (validate at service layer — see `ScimService.list_response`). |
| **`count`** | **`0`** is valid (metadata-only list in some profiles); negative values are invalid. Malformed query integers fall back to defaults in HTTP layer — **confirm** your product policy: strict `400` vs safe defaults (`src/exonware/xwauth.connector/handlers/mixins/scim.py` uses `try/except` → `1` / `100`). |
| **`totalResults` / `itemsPerPage`** | List responses must set **`totalResults`** to full filtered set size, **`itemsPerPage`** to returned page length — required for IdP sync loops. |
| **IdP quirks** | **Microsoft Entra** often uses default page sizes; it **retries** with `startIndex` advances — any off-by-one bug shows up as missing or duplicate users. **Okta** may send large `count`; cap server-side if needed and document `maxResults` in `ServiceProviderConfig` when you implement it. |

---

## 3. Filter syntax

- SCIM **`filter`** is parsed/validated via **`validate_scim_filter`** before listing; unsupported expressions should return **`400`** with a clear **`detail`** (not a generic stack trace).  
- **Case sensitivity** and **attribute paths** differ slightly by IdP — regression-test filters your provisioning app actually sends (often `eq` on `userName` or `externalId`).

---

## 4. Error mapping

Standard error envelope (see handlers):

```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
  "status": "401",
  "detail": "Authentication required"
}
```

| HTTP | When |
|------|------|
| **401** | Missing/invalid Bearer for SCIM (treat as SCIM Error JSON for consistency). |
| **403** | Authenticated but not authorized (e.g. org mismatch). |
| **404** | Unknown resource id on GET/PATCH/DELETE. |
| **409** | Create conflict (e.g. duplicate `userName` / id) — many IdPs retry with PATCH; return stable **`detail`**. |
| **412** | **`If-Match`** precondition failed (ETag mismatch) — required for safe concurrent PATCH from IdPs. |
| **400** | Invalid filter, bad JSON patch, invalid `startIndex` / `count`. |

Map **internal exceptions** to the above; never leak stack traces in production ([INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md)).

---

## 5. Idempotency and concurrency

| Operation | Guidance |
|-----------|----------|
| **POST /Users** | Prefer **`externalId`** (or stable `userName`) as IdP’s correlation key; duplicate create should be **`409`** or **return existing** only if your policy explicitly defines upsert — document behavior. |
| **PUT** | Full replace; idempotent when body is identical — still bump **`meta.lastModified`** / **ETag** only when content changes if you want to reduce churn. |
| **PATCH** | Use **`If-Match`** with **`ETag`** from `meta.version` when the IdP supports it; handlers compare via `_matches_if_match`. |
| **DELETE** | **Idempotent delete:** second DELETE should be **`404`** or **`204`** per your chosen strictness; pick one and test the IdP (some expect 404, some 204). |

---

## 6. Tenancy and auth

- Query param **`org_id`** must align with **token org** when the token is org-bound (`_scim_org_query_matches_token`) — prevents cross-tenant SCIM in multi-org deployments.  
- Use **Bearer tokens** scoped to provisioning; rotate on the same cadence as other admin credentials.  
- Emit audit lines per [REF_61](REF_61_OPS_TELEMETRY_SCHEMA.md) §8 (`xwauth.scim.*`).

---

## 7. Related

- SAML / federation (parallel IdP work): [GUIDE_10_SAML_ENTERPRISE_KIT.md](GUIDE_10_SAML_ENTERPRISE_KIT.md)  
- Partner / gateway: [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md)

---

## Expand next

- **`ServiceProviderConfig`** JSON: advertise **`filter`**, **`patch`**, **`changePassword`**, **`sort`**, **`etag`**, **`authenticationSchemes`** consistently with actual behavior.  
- **Contract tests** per IdP (recorded HTTP fixtures) — [GUIDE_12_FEDERATION_INTEROP_LAB.md](GUIDE_12_FEDERATION_INTEROP_LAB.md) (roadmap **#8**).
