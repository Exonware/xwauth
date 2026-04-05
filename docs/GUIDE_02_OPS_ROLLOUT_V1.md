# GUIDE_02 — Ops Rollout (v1)

**Project:** `xwauth`  
**Last Updated:** 01-Apr-2026

---

## 1) Purpose

Define a repeatable first rollout procedure for the ops profile contracts in:

- `REF_60_OPS_TIER_PROFILE_CONTRACT.md`
- `REF_61_OPS_TELEMETRY_SCHEMA.md`
- `REF_62_OPS_SLI_REGISTRY_V1.md`

This guide is intentionally low-risk and documentation-first.

---

## 2) Preconditions

- Tier selected: `A`, `B`, or `C`.
- Operators reviewed contract fields and defaults.
- Alert entries include runbook references before enabling paging behavior.

---

## 3) Runtime Inputs

Required environment values:

- `XWAUTH_OPS_TIER`

Optional:

- `XWAUTH_OPS_PROFILE_PATH`

If profile path is provided, file must conform to `REF_60` contract.

---

## 4) Rollout Steps

1. **Select tier baseline**  
   set `XWAUTH_OPS_TIER` to target tier.
2. **Apply optional profile overrides**  
   set `XWAUTH_OPS_PROFILE_PATH` for environment-specific values.
3. **Deploy and verify health**  
   confirm service startup and health endpoints are normal.
4. **Check observability naming readiness**  
   ensure dashboards/queries use `REF_61` metric names and dimensions.
5. **Publish scorecard seed**  
   create first scorecard entry with route-family coverage from `REF_62`.

---

## 5) Rollback Procedure

1. remove `XWAUTH_OPS_PROFILE_PATH` override,
2. fallback to tier-only defaults,
3. if needed, revert `XWAUTH_OPS_TIER` to previous value,
4. republish scorecard with rollback event details.

No data migration is required for this v1 rollout.

---

## 6) Validation Checklist

- [ ] tier value resolved correctly (`A/B/C`)
- [ ] profile file validated (if used)
- [ ] route-family classification exists for critical flows
- [ ] alert/runbook linkage reviewed
- [ ] scorecard artifact updated for the release

