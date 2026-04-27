# REF_31 — Data residency and regional boundaries

**Purpose:** REF_25 #12 — align **technical deployment** with data-location and subprocessors commitments.  
**Checklist API:** `exonware.xwauth.connector.ops.data_residency.data_residency_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_data_residency.py`

---

## Scope

This is **not** legal advice. Use the checklist with privacy/legal teams to ensure:

- Auth stores and backups stay in approved regions.
- Federation egress to IdPs is disclosed in DPIA / DPA.
- Logs and SIEM routing respect residency.
- Multi-tenant SaaS can pin **per-tenant** regions when required.

---

## Related

- Air-gapped installs: [REF_30_AIRGAP_DEPLOYMENT.md](REF_30_AIRGAP_DEPLOYMENT.md)
- Multi-region AS topology: [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md)

---

*Last updated: 2026-04-03*
