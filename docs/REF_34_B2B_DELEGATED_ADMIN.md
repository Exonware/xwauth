# REF_34 — B2B delegated administration

**Purpose:** REF_25 #15 — **customer org** admins manage their own users, roles, and IdPs without becoming platform operators.  
**Checklist:** `exonware.xwauth.ops.b2b_delegated_admin.b2b_delegated_admin_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_b2b_delegated_admin.py`

---

## Model sketch

- **Platform** staff ≠ **org_owner** / **org_admin** for a tenant.
- Invites are **org-scoped** with audit.
- Optional **per-org SSO** via tenant-scoped IdP registry (federation docs).

Implement persistence and APIs in your product layer (**xwentity**, custom admin routes); this REF is the **contract** checklist.

---

## Related

- Multi-tenant data boundaries: [REF_31_DATA_RESIDENCY.md](REF_31_DATA_RESIDENCY.md)  
- IdP quirks: [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md)

---

*Last updated: 2026-04-03*
