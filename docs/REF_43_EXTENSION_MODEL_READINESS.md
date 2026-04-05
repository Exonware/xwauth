# REF_43 — Extension model readiness (MFA, risk, claims)

**Purpose:** REF_25 #8 — a **versioned** extension story for MFA, risk signals, step-up, and custom claims (in-process hooks or HTTP plugins).  
**Checklist API:** `exonware.xwauth.ops.extension_model_readiness.extension_model_readiness_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_extension_model_readiness.py`

---

## Scope

- Product and security must agree on **one primary** extension model per major release line.
- Implementations may live in `xwauth` core, `xwlogin`, or sidecars; this doc is the **contract checklist**.

---

*Last updated: 2026-04-03*
