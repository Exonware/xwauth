# REF_63 — Auth stack observability contract (landing)

**Purpose:** Single entry point for **logs, traces, metrics, and audit** expectations across **xwauth-connector-api** (transport) and **xwauth** (connector).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#14**.  
**Normative detail:** [REF_61_OPS_TELEMETRY_SCHEMA.md](REF_61_OPS_TELEMETRY_SCHEMA.md), [REF_62_OPS_SLI_REGISTRY_V1.md](REF_62_OPS_SLI_REGISTRY_V1.md), [REF_60_OPS_TIER_PROFILE_CONTRACT.md](REF_60_OPS_TIER_PROFILE_CONTRACT.md).

---

## 1. Correlation (HTTP)

The **xwauth-connector-api** reference server attaches stable identifiers for cross-service joins (see package README):

- **`X-Request-Id`**, **`X-Correlation-Id`**, **`X-Trace-Id`** (when tracing is active)  
- **`X-Route-Family`**, **`X-XWAUTH-Ops-Tier`**

**Integrator rule:** Forward or preserve these headers at proxies; log them on every auth error path.

---

## 2. Structured logs

- Emit **JSON** or key=value lines in production.  
- **Never** log access tokens, refresh tokens, authorization codes, passwords, or `client_secret`.  
- Include **`correlation_id`** / **`request_id`** fields matching HTTP headers.  
- For **tenant-aware** deployments, include a safe tenant/org dimension (see [REF_37_MULTI_TENANT_REFERENCE_STACK.md](REF_37_MULTI_TENANT_REFERENCE_STACK.md)).

---

## 3. Traces

- When OpenTelemetry is active, set **`XWAUTH_OPS_OTEL=true`** on the reference server (see xwauth-connector-api README) so spans receive `xwauth.*` attributes where implemented.  
- Sample **authorize** and **token** journeys at a higher rate during rollouts; reduce in steady state per cost.

---

## 4. Metrics & SLOs

- Use **REF_62** route-family registry as the menu of critical endpoints (`/token`, `/authorize`, introspection, etc.).  
- Tier profiles (**REF_60**) define burn-rate style gates for release — align dashboards with the same labels.

---

## 5. Audit export (product boundary)

- **Security-relevant events** (admin grants, SCIM mutations, federation linking) should be append-only and **exportable** to SIEM (see [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md)).  
- Contract shape: prefer **JSON lines** with stable event types; map fields to your SOC schema (CEF/OTel/etc.) in the integration layer.

**Example line (illustrative — align `event_type` with [REF_61](REF_61_OPS_TELEMETRY_SCHEMA.md) §8):**

```json
{"schema_version":"1.0","event_type":"xwauth.admin.user_role_changed","timestamp":"2026-04-02T12:00:00Z","trace_id":"","correlation_id":"req-abc","tenant_id":"org-789","route_family":"admin","result":"allow","details":{"actor_sub":"admin-123","target_sub":"user-456","old":"viewer","new":"editor"}}
```

**Normative catalog:** [REF_61_OPS_TELEMETRY_SCHEMA.md](REF_61_OPS_TELEMETRY_SCHEMA.md) §8 (audit event types).

---

## Expand next

- Optional: markdown diff check that REF_62 §2 rows match `SLI_REGISTRY_V1_ROUTE_FAMILIES` exactly (human table vs code).
