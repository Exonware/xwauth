# REF_24 — Ops/Observability/Reliability Perfect-Score Execution Plan

**Project:** `xwauth`  
**Scope:** `xwauth` core with explicit integration anchors in `xwauth-connector-api` and `xwsystem`  
**Last Updated:** 01-Apr-2026

---

## 1) Outcome Target

Achieve and sustain a **10/10 operational score** for `xwauth` across:

- reliability (tiered SLOs + hard error budgets),
- observability (complete RED + USE + trace + audit correlation),
- operations (safe delivery + rollback + incident repeatability),
- evidence (publishable scorecard artifacts from CI and runtime telemetry).

This target is measured against enterprise identity-system operators, not only local test pass rates.

---

## 2) Ownership Boundaries

- **`xwauth` (core):** auth domain logic, token/session lifecycle, policy and security primitives.
- **`xwauth-connector-api` (transport):** endpoint surface, middleware, telemetry propagation, startup profile loading.
- **`xwsystem` (shared foundation):** shared contracts, normalization, OAuth error shape, monitoring primitives.

This plan keeps one policy model and telemetry vocabulary across all three packages.

---

## 3) Tier Profiles and Runtime Intent

Three runtime tiers are required from one codebase:

- **Tier A (Enterprise Core):** 99.95% availability target
- **Tier B (Regulated):** 99.99% availability target
- **Tier C (Mission Critical):** 99.99%+ with multi-region active-active assumptions

Tier profiles are defined as machine-readable contracts in:

- `REF_60_OPS_TIER_PROFILE_CONTRACT.md`

Telemetry and correlation schema are defined in:

- `REF_61_OPS_TELEMETRY_SCHEMA.md`

Endpoint-family SLI inventory starts in:

- `REF_62_OPS_SLI_REGISTRY_V1.md`

---

## 4) Current Anchors and Gaps

Primary implementation anchors:

- `xwauth-connector-api/src/exonware/xwauth_connector_api/services/__init__.py` (route registry)
- `xwauth-connector-api/src/exonware/xwauth_connector_api/server.py` (startup wiring)
- `xwauth/src/exonware/xwauth.connector/handlers/mixins/system.py` (`/health`, `/metrics`)
- `xwauth/src/exonware/xwauth.connector/handlers/mixins/auth_core.py` (critical auth paths)
- `xwauth/src/exonware/xwauth.connector/sessions/manager.py` and `security.py` (session lifecycle)
- `xwsystem/src/exonware/xwsystem/security/contracts.py` and `oauth_errors.py` (shared schema/error primitives)

Known gap summary:

- no endpoint-to-SLI contract from the route registry,
- no tier profile contract consumed by startup,
- partial metrics endpoint but not full RED/USE coverage,
- no strict cross-package correlation schema as a first-class contract,
- no signed weekly ops scorecard process.

---

## 5) Workstreams (xwauth-targeted)

### W1. Reliability Foundation

- Build route-family SLI mapping from `AUTH_SERVICES`.
- Define tier SLO/error-budget profile contracts.
- Apply resilience primitives to critical dependency paths (timeouts, retry with jitter, breaker).

### W2. Observability Standardization

- Standardize metrics/traces/logs/audit field names and required dimensions.
- Require correlation linkage (`trace_id`, `span_id`, `correlation_id`) for critical flows.
- Move `/metrics` from placeholder output to route-family RED coverage.

### W3. Operational Safety

- Introduce release gates tied to SLO impact and health checks.
- Define canary + rollback policy contracts per tier.
- Create runbooks for top incidents and recurring game-day validation.

### W4. Evidence Program

- Produce weekly benchmark and scorecard artifacts.
- Enforce "no evidence, no claim" rule for reliability/observability statements.

---

## 6) Phased Delivery

### Phase 0 (Baseline)

- Publish this execution plan and the `REF_60+` contracts.
- Create initial SLI registry table and ownership map.
- Establish first scorecard template with red/yellow/green grading.

### Phase 1 (Tier + Telemetry Core)

- Load tier/runtime profile at startup in `xwauth-connector-api`.
- Add correlation-id propagation middleware contract.
- Instrument token/authorize/introspect/revoke/session and federation paths.

### Phase 2 (Resilience + Safe Delivery)

- Apply breaker/retry/timeouts to hot dependency paths.
- Enforce release gate checks and auto-rollback criteria.
- Run recurring game days with measurable objectives.

### Phase 3 (Isolation + Leadership Operations)

- Validate tier C failure-domain objectives and isolation controls.
- Continuously publish scorecards and benchmark deltas.
- Maintain 90-day rolling SLO conformance by tier.

---

## 7) Success Criteria

- Tier SLO targets met on rolling windows with explicit error budgets.
- 100% critical route-family telemetry coverage (metrics + traces + audit correlation).
- MTTD and MTTR tracked with objectives and trend direction.
- Zero ungated production releases.
- Signed scorecard artifact for each release and weekly ops report.

---

## 8) Immediate Build Checklist

1. Establish SLI families from route registry (`REF_62`).
2. Lock tier contract and startup env contract (`REF_60`).
3. Lock telemetry schema and required dimensions (`REF_61`).
4. Use `GUIDE_02_OPS_ROLLOUT_V1.md` for first controlled rollout.

These documents are the minimum baseline required before implementing runtime enforcement logic.

---

## 9) Implemented Baseline (01-Apr-2026)

The following runtime capabilities are now implemented in code:

- `xwauth-connector-api` loads ops tier/profile from env at startup (`XWAUTH_OPS_TIER`, `XWAUTH_OPS_PROFILE_PATH`) and stores resolved state on `app.state`.
- `xwauth-connector-api` installs correlation middleware emitting:
  - `X-Request-Id`
  - `X-Correlation-Id`
  - `X-Trace-Id`
  - `X-Route-Family`
  - `X-XWAUTH-Ops-Tier`
- route-family registry is generated from `AUTH_SERVICES` and attached on `app.state`.
- runtime scorecard and release-gate endpoint is exposed at `GET /v1/system/ops/scorecard`.
- dedicated release gate and runbook/game-day endpoints are exposed at:
  - `GET /v1/system/ops/release-gate`
  - `GET /v1/system/ops/runbooks`
- deployment overlay contract endpoint is exposed at:
  - `GET /v1/system/ops/deployment-overlays`
- anomaly and benchmark evidence endpoints are exposed at:
  - `GET /v1/system/ops/anomalies`
  - `GET /v1/system/ops/benchmark`
- in-memory burn-rate policy now activates automatic non-critical load shedding when thresholds are exceeded.
- canary policy controls are available via env (`XWAUTH_OPS_CANARY_*`) with optional mutating-request enforcement.
- tenant noisy-neighbor throttling controls are available via `XWAUTH_OPS_TENANT_REQUEST_LIMIT`.
- scorecard endpoint now returns signed artifacts (`HMAC-SHA256`) for evidence workflows.
- `xwauth` system conformance endpoint now reports:
  - ops profile summary (`schema_version`, `tier`, `deployment_overlay`)
  - route-family coverage gates and missing required families
- `xwauth` metrics endpoint now exports an ops tier info metric line when tier is present.

These changes establish executable ops contracts and observability wiring, not only documentation.

