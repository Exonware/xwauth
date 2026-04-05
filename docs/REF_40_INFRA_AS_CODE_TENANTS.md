# REF_40 — Terraform / Pulumi tenant and client IaC

**Purpose:** REF_25 #3 — **engineering checklist** for infrastructure-as-code that provisions tenants, OAuth clients, redirect URIs, signing keys, and scopes.  
**Checklist API:** `exonware.xwauth.ops.infra_as_code_tenants.infra_as_code_tenants_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_infra_as_code_tenants.py`

---

## Scope

- Applies to modules you maintain under `deploy/terraform`, `deploy/pulumi`, or a dedicated **exonware-deploy**-style repository.
- This document does **not** ship Terraform or Pulumi sources; it defines what “complete” automation should cover for enterprise buyers.

---

## Related

- Multi-region and JWKS themes: [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md)  
- B2B org patterns: [REF_34_B2B_DELEGATED_ADMIN.md](REF_34_B2B_DELEGATED_ADMIN.md)

---

*Last updated: 2026-04-03*
