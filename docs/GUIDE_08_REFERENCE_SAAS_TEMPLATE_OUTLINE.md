# GUIDE_08 — Reference SaaS template outline (self-host vs product shell)

**Audience:** Teams that want a **managed-style** or **copy-paste SaaS-shaped** deployment without re-deriving architecture from scratch.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#3**.  
**Scope:** **Outline only** — not a full multi-tenant product; billing, CRM, and arbitrary SLAs are **out of scope** here.

---

## 1. What the reference stack already gives you

| Layer | You get from XW repos |
|-------|------------------------|
| **OAuth/OIDC AS process** | `xwauth-connector-api` container / Helm chart, discovery, token endpoints (with correct deployment profile). |
| **Client registry** | `registered_clients` JSON, env-driven; optional Secret mount in Kubernetes. |
| **Login / IdP glue** | `exonware-xwauth-identity` handlers and federation when you opt into `[xwlogin]` / `[enterprise]`. |
| **Observability hooks** | See [REF_63_AUTH_OBSERVABILITY_CONTRACT.md](REF_63_AUTH_OBSERVABILITY_CONTRACT.md). |

---

## 2. Product shell you still own

| Concern | Typical approach |
|---------|------------------|
| **Tenant identity** | Subdomain (`tenant.app.com`) or path (`app.com/t/x`); map to org id in storage. |
| **Issuer strategy** | Single issuer + org claims in tokens **or** issuer per tenant — affects JWKS caching and mobile config. |
| **Provisioning** | Admin API or job that creates tenant row + seeds default OAuth clients + roles. |
| **Data isolation** | Storage namespaces / DB schemas; align with [REF_37_MULTI_TENANT_REFERENCE_STACK.md](REF_37_MULTI_TENANT_REFERENCE_STACK.md). |
| **Billing / metering** | External system; optional claim or org metadata only. |

---

## 3. Minimal “template” layout (fork-friendly)

1. **Fork** [xwauth-connector-api](../../xwauth-connector-api/) Helm chart values for your cluster naming and ingress.  
2. Add a **small “tenant provisioner”** service or CI job that writes **client JSON** into a Secret per tenant (or merges into a shared registry with unique `client_id` prefixes).  
3. Front **WAF / API gateway** with your rate limits and [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md) patterns.  
4. Document **one golden path** for engineering: same as [GOLDEN_PATH_DEPLOY.md](../../xwauth-connector-api/docs/GOLDEN_PATH_DEPLOY.md) but with your hostname and Secret naming.

---

## 4. Terraform stub (namespace + JWT Secret + Helm)

A minimal **IaC** starting point lives in the **xwauth-connector-api** repo:

- **[`deploy/terraform/stub/`](../../xwauth-connector-api/deploy/terraform/stub/)** — creates a namespace, a generated **JWT** `Secret`, and installs [`deploy/helm/xwauth-connector-api`](../../xwauth-connector-api/deploy/helm/xwauth-connector-api/). See that folder’s `README.md` for `terraform init` / `apply`.

Fork this stub into your product repo to add **per-tenant namespaces**, **clients JSON** Secrets, **Ingress**, and remote state.

---

## 5. When to prefer managed IdP instead

If you do **not** need an embedded AS, run **Okta / Entra / Keycloak** as IdP and use **xwauth** as connector/RAR only — this guide is for teams standardizing on **self-hosted XW AS** as the control plane.

---

## Expand next

- **Cell / shard** model for large SaaS (ties to [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md)).
