# REF_32 — Multi-region authorization server

**Purpose:** REF_25 #18 — run OAuth/OIDC **across regions** without breaking validation, rotation, or logout.  
**Checklist API:** `exonware.xwauth.connector.ops.multi_region_auth.multi_region_auth_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_multi_region_auth.py`

---

## Core tensions

- **Issuer stability:** Clients embed issuer and discovery; per-region issuer drift breaks RPs unless designed for it.
- **Signing keys:** JWKS must converge across regions during rotation.
- **Refresh / revoke:** Server-side state must become **eventually** or **strongly** consistent per your SLA.

---

## Related

- Data location and subprocessors: [REF_31_DATA_RESIDENCY.md](REF_31_DATA_RESIDENCY.md)
- JWKS refetch behavior in code: `exonware.xwauth.connector.federation.oidc_id_token` (`jwks_refetch_on_verify_failure`)

---

*Last updated: 2026-04-03*
