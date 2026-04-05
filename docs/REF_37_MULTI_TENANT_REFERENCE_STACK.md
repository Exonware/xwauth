# REF_37 — Multi-tenant model (reference stack story)

**Purpose:** Describe how **B2B / multi-tenant** concerns map onto **xwauth + xwlogin + xwauth-api** and **xwsystem** helpers today, and what integrators must still own.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#13**.

---

## What the libraries provide

| Layer | Mechanism | Notes |
|-------|-----------|--------|
| **Connector config** | `authorize_org_hint_requires_membership` on `XWAuthConfig` | When `True`, org hints on `/authorize` expect a member relationship (see connector docs / GUIDE_01). |
| **xwsystem tenancy** | `exonware.xwsystem.security.tenancy` | `TenancyContext`, `build_tenancy_context`, `tenancy_violation_for_path_org`, `effective_isolation_key` — path org vs token org alignment, optional **trusted gateway headers** when `XWAUTH_TRUST_GATEWAY_TENANT_HEADERS` is enabled. |
| **Claims / introspection** | `org_id_from_claims_mapping`, `project_id_from_claims_mapping` | Normalize org/project from JWT or RFC 7662-style maps. |
| **Break-glass** | `is_instance_operator_introspection` | Narrow operator bypass; **must be audited** at call sites. |

---

## What you own in production

1. **Storage partition** — Tenant or org id as part of keys/paths in your persistence (xwstorage providers, DB schemas). The reference **JSON** layout is single-directory unless you shard by tenant.  
2. **Issuer per tenant?** — Usually **one issuer** + org claims; multiple issuers is a product decision (not required by the default stack).  
3. **Admin & SCIM** — Scope APIs (`/v1/admin/*`, SCIM) with the same org-bound rules as your API gateway.  
4. **Rate limits** — Use `effective_isolation_key(...)` (or equivalent) so throttles are per-tenant, not global-only.

---

## Reference server (`xwauth-api`)

The golden-path **Dockerfile / Compose** image is a **single-tenant-shaped** convenience. For multi-tenant production, plan:

- Shared or sharded **storage** backing all tenants.  
- **Client registry** (`XWAUTH_API_REGISTERED_CLIENTS_JSON` or DB) that encodes per-tenant or per-app clients as your model requires.  
- Ingress rules that preserve **tenant context** (subdomain, path prefix, or gateway headers — only trust headers when `XWAUTH_TRUST_GATEWAY_TENANT_HEADERS` is justified and the edge is yours).

---

## Reference Compose recipe (lab / demo)

Production multi-tenant shape is usually **Kubernetes** (see **xwauth-api** [`deploy/terraform/stub/`](../../xwauth-api/deploy/terraform/stub/) + Helm). For **local Compose** only:

1. **Single AS, logical tenants** — One `docker compose up` from **xwauth-api**; shared storage volume; distinguish tenants via **org claims** and gateway routing in front — matches the default golden-path image (not strong isolation).
2. **Parallel stacks (isolation simulation)** — Two checkouts or two `COMPOSE_PROJECT_NAME` values, different **host ports** and **`XWAUTH_API_STORAGE_PATH`** (or bind mounts) so two AS processes do not share disk; useful for integration tests, not a tenancy SLA.
3. **Kubernetes-shaped** — Use the Terraform stub or your own Helm values per environment; mount **per-env or per-tenant** `registered_clients` JSON via Secrets as in [GOLDEN_PATH_DEPLOY.md](../../xwauth-api/docs/GOLDEN_PATH_DEPLOY.md).

---

## Related

- Partner / edge: [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md)  
- Ops telemetry: [REF_63_AUTH_OBSERVABILITY_CONTRACT.md](REF_63_AUTH_OBSERVABILITY_CONTRACT.md)  
- HA / upgrade: [GUIDE_03_HA_UPGRADE_RUNBOOK.md](GUIDE_03_HA_UPGRADE_RUNBOOK.md)
