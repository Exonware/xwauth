# REF_41 — Kubernetes operator readiness (beyond Helm)

**Purpose:** REF_25 #4 — checklist for **day-2** automation: coordinated upgrades, health integration, and signing-key rotation hooks.  
**Checklist API:** `exonware.xwauth.ops.kubernetes_operator_readiness.kubernetes_operator_readiness_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_kubernetes_operator_readiness.py`

---

## Scope

- Complements golden-path **Compose / Helm**; users who only want charts should remain supported.
- An operator is optional product surface; this file captures **readiness criteria** before claiming parity with Keycloak-style operators.

---

## Related

- Ops contracts: [REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md](REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md), `REF_60+` telemetry/SLO docs  
- Multi-region keys: [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md)

---

*Last updated: 2026-04-03*
