# REF_60 — Ops Tier Profile Contract

**Project:** `xwauth`  
**Last Updated:** 01-Apr-2026  
**Status:** Contract v1 (documentation baseline)

---

## 1) Purpose

Define one machine-readable contract for runtime operations policy consumed by `xwauth-api` startup and middleware bootstrap.

This contract standardizes three profile blocks:

- `slo_profile`
- `alert_profile`
- `deployment_profile`

---

## 2) Top-Level Contract

```yaml
schema_version: "1.0"
tier: "A"            # A | B | C
deployment_overlay: "k8s"   # k8s | vm | saas
slo_profile: {}
alert_profile: {}
deployment_profile: {}
```

### Required fields

- `schema_version` (`string`)
- `tier` (`A | B | C`)
- `slo_profile` (`object`)
- `alert_profile` (`object`)
- `deployment_profile` (`object`)

### Optional fields

- `deployment_overlay` (`k8s | vm | saas`)

---

## 3) `slo_profile`

```yaml
slo_profile:
  availability_target: 0.9995
  rolling_window_days: 30
  latency_budgets:
    oauth_authorize:
      p95_ms: 200
      p99_ms: 500
    oauth_token:
      p95_ms: 180
      p99_ms: 450
  error_budget_policy: "standard"   # standard | strict
```

Field contract:

- `availability_target` (`float`, 0..1)
- `rolling_window_days` (`int`, >= 7)
- `latency_budgets` (`map[route_family] -> {p95_ms, p99_ms}`)
- `error_budget_policy` (`standard | strict`)

---

## 4) `alert_profile`

```yaml
alert_profile:
  burn_rate_preset: "balanced"      # conservative | balanced | aggressive
  page_on_call: true
  create_ticket: true
  runbook_required: true
```

Field contract:

- `burn_rate_preset` (`conservative | balanced | aggressive`)
- `page_on_call` (`bool`)
- `create_ticket` (`bool`)
- `runbook_required` (`bool`) - alerts without a runbook link are invalid policy.

---

## 5) `deployment_profile`

```yaml
deployment_profile:
  max_unavailable_percent: 25
  min_ready_replicas: 2
  canary_steps: 3
  auto_rollback_enabled: true
```

Field contract:

- `max_unavailable_percent` (`int`, 0..100)
- `min_ready_replicas` (`int`, >= 1)
- `canary_steps` (`int`, >= 1)
- `auto_rollback_enabled` (`bool`)

---

## 6) Tier Defaults (v1)

| Tier | Availability target | Error budget policy | Alert preset |
|------|---------------------|---------------------|--------------|
| A | 0.9995 | standard | balanced |
| B | 0.9999 | strict | aggressive |
| C | 0.9999+ | strict | aggressive |

`Tier C` requires explicit deployment assumptions (multi-region or equivalent) outside this v1 contract.

---

## 7) Startup Loading Contract

Environment transport for v1:

- `XWAUTH_OPS_TIER` -> `A | B | C`
- `XWAUTH_OPS_PROFILE_PATH` -> optional JSON/YAML file path matching this contract

Resolution order:

1. load defaults from `XWAUTH_OPS_TIER`,
2. merge `XWAUTH_OPS_PROFILE_PATH` overrides,
3. fail startup if required keys are missing or invalid.

---

## 8) Compatibility Rules

- Additive changes only within `schema_version: 1.x`.
- Renaming/removing keys requires `schema_version` major bump.
- Unknown keys are allowed but must be ignored safely in v1 readers.

