# REF_25 — Competitive advance backlog (extended ideas)

**Project:** `xwauth` ecosystem (`xwauth`, `xwlogin`, `xwauth-api`)  
**Purpose:** Track the **20 extended competitive ideas** (beyond REF_23) with explicit status. Update this file as work lands; link evidence (PRs, docs, CI jobs) in **Notes**. As of the ops/doc pass, each row has **Done\*** engineering groundwork (checklists, tests, or harnesses) where applicable; external commitments (vendors, Foundation, full UI) remain noted per row.

**Status values:** `Pending` | `In progress` | `Done` | `N/A`

| # | Idea | Status | Primary target | Notes |
|---|------|--------|----------------|-------|
| 1 | Third-party penetration test + publishable executive summary | Done* | Trust / scrutiny | *`ops/pen_test_engagement.py`, `test_pen_test_engagement.py`, [REF_38_PENETRATION_TEST_ENGAGEMENT.md](REF_38_PENETRATION_TEST_ENGAGEMENT.md); vendor engagement + published summary still required* |
| 2 | Formal OIDC self-certification / OpenID Foundation listing | Done* | Protocol trust | *`ops/oidc_self_cert_readiness.py`, `test_oidc_self_cert_readiness.py`, [REF_39_OIDC_SELF_CERT_READINESS.md](REF_39_OIDC_SELF_CERT_READINESS.md); Foundation submission + listing still required* |
| 3 | Terraform + Pulumi coverage (tenants, clients, URIs, keys, scopes) | Done* | Enterprise automation | *`ops/infra_as_code_tenants.py`, `test_infra_as_code_tenants.py`, [REF_40_INFRA_AS_CODE_TENANTS.md](REF_40_INFRA_AS_CODE_TENANTS.md); shipped Terraform/Pulumi modules still optional* |
| 4 | Kubernetes operator (beyond Helm): upgrades, health, key rotation hooks | Done* | Day-2 ops | *`ops/kubernetes_operator_readiness.py`, `test_kubernetes_operator_readiness.py`, [REF_41_KUBERNETES_OPERATOR_READINESS.md](REF_41_KUBERNETES_OPERATOR_READINESS.md); operator implementation still optional* |
| 5 | LTS release train + documented breaking-change policy | Done* | Lifecycle risk | *Draft in **Appendix B**; promote to GUIDE when ratified* |
| 6 | Reproducible performance benchmark harness + published results | Done* | Ops credibility | *Scope:* library microbench (`exonware.xwauth.bench`) + **HTTP TestClient** bench (`exonware.xwauth_api.bench`) + unit tests + [xwauth benchmarks/README.md](../benchmarks/README.md) + xwauth-api `benchmarks/README.md` + workflow `http-bench.yml`. *Optional:* socket load (`oha`/`wrk`) + checked-in result JSON for TCO. |
| 7 | Full admin parity: every console action has an API + OpenAPI | Done* | Keycloak-class ops | *`ops/admin_api_openapi_parity.py`, `test_admin_api_openapi_parity.py`, [REF_42_ADMIN_API_OPENAPI_PARITY.md](REF_42_ADMIN_API_OPENAPI_PARITY.md); route inventory + 100% parity in `xwauth-api` still required* |
| 8 | Stable extension model (MFA, risk, step-up, custom claims) | Done* | Ecosystem | *`ops/extension_model_readiness.py`, `test_extension_model_readiness.py`, [REF_43_EXTENSION_MODEL_READINESS.md](REF_43_EXTENSION_MODEL_READINESS.md); shipped extension SDK still required* |
| 9 | “IdP quirk” contract tests (Azure AD / Okta / Google-shaped behaviors) | Done* | Interop | *`federation/idp_quirks.py`, tests `test_idp_quirk_contracts.py`, [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md); live IdP samples still optional |
| 10 | Reference login UI: WCAG 2.2 AA + VPAT-style checklist | Done* | Procurement | *`ops/login_ui_accessibility.py`, `test_login_ui_accessibility.py`, [REF_36_LOGIN_UI_ACCESSIBILITY.md](REF_36_LOGIN_UI_ACCESSIBILITY.md); axe/Playwright on xwlogin templates still recommended* |
| 11 | Compliance packaging (data map, retention, subprocessors, DPA template) | Done* | Regulated buyers | *`ops/compliance_pack.py`, `test_compliance_pack.py`, [REF_35](REF_35_COMPLIANCE_PACK.md); legal sign-off still required* |
| 12 | Data residency / regional deployment patterns | Done* | EU / sovereign | *`ops/data_residency.py`, `test_data_residency.py`, [REF_31_DATA_RESIDENCY.md](REF_31_DATA_RESIDENCY.md) |
| 13 | Abuse resistance as a product module (rate limits, bot signals) | Done* | Security | *`ops/abuse_resistance.py`, `test_abuse_resistance.py`, [REF_33](REF_33_ABUSE_RESISTANCE.md); wire backoff at transport* |
| 14 | End-user session & device management in reference app | Done* | IdP UX bar | *`ops/session_device_reference_ui.py`, `test_session_device_reference_ui.py`, [REF_44_SESSION_DEVICE_REFERENCE_UI.md](REF_44_SESSION_DEVICE_REFERENCE_UI.md); Bearer session list/revoke mixins in `xwauth.handlers.mixins.sessions`; **account HTML** in `xwlogin` still optional* |
| 15 | B2B delegated admin pattern (org owners, invites, role templates) | Done* | SaaS IAM | *`ops/b2b_delegated_admin.py`, `test_b2b_delegated_admin.py`, [REF_34](REF_34_B2B_DELEGATED_ADMIN.md)* |
| 16 | Email / magic-link operational playbook (SPF/DKIM/DMARC, bounces) | Done* | Reliability | *`exonware.xwauth.ops.email_magic_link_ops`, tests `ops_tests/test_email_magic_link_ops.py`, [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md) |
| 17 | Air-gapped / offline install story | Done* | Gov / regulated | *`ops/airgap_deployment.py`, tests `test_airgap_deployment.py`, [REF_30_AIRGAP_DEPLOYMENT.md](REF_30_AIRGAP_DEPLOYMENT.md) |
| 18 | Multi-region auth: JWKS rotation, validation, revocation semantics | Done* | Scale | *`ops/multi_region_auth.py`, `test_multi_region_auth.py`, [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md) |
| 19 | TCO one-pager vs Keycloak / Ory stack | Done* | Sales / adoption | *Appendix A narrative + [REF_37_TCO_BENCHMARK_EVIDENCE.md](REF_37_TCO_BENCHMARK_EVIDENCE.md): `validate_microbench_output`, `tco_benchmark_publish_checklist`; commit measured JSON under `docs/logs/benchmarks/` when publishing* |
| 20 | Public interop bounty + fuzzing budget for OAuth parsers/endpoints | Done* | Scrutiny | *Draft policy:* `ops/research_program.py`, tests `test_research_program.py`, [REF_29](REF_29_INTEROP_BOUNTY_AND_FUZZING.md), [SECURITY.md](../SECURITY.md); **paid** bounty TBD |

### Groundwork shipped (this iteration)

- [SECURITY.md](../SECURITY.md) — private reporting channel (GitHub-standard).
- [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md) — triage levels, EXONWARE-SA id scheme, advisory log scaffold.
- [REF_26_INTEGRATOR_SECURITY_CHECKLIST.md](REF_26_INTEGRATOR_SECURITY_CHECKLIST.md) — integrator release gate (tokens, OAuth, federation, MFA, ops).
- **Benchmark harness (REF_25 #6):** `exonware.xwauth.bench` (JWT microbench) + `exonware.xwauth_api.bench` (token `TestClient` loop) + `xwauth-api/scripts/http_bench.py` (monorepo path bootstrap); tests under each repo’s `tests/1.unit/bench_tests/`; CI: `xwauth-api/.github/workflows/http-bench.yml`.
- **IdP quirks (REF_25 #9):** `federation/idp_quirks.py`, `tests/1.unit/federation_tests/test_idp_quirk_contracts.py`, [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md).
- **Email / magic-link ops (REF_25 #16):** `ops/email_magic_link_ops.py`, `tests/1.unit/ops_tests/test_email_magic_link_ops.py`, [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md).
- **Interop / fuzzing policy (REF_25 #20):** `ops/research_program.py`, `tests/1.unit/ops_tests/test_research_program.py`, [REF_29_INTEROP_BOUNTY_AND_FUZZING.md](REF_29_INTEROP_BOUNTY_AND_FUZZING.md).
- **Airgap deploy (REF_25 #17):** `ops/airgap_deployment.py`, `tests/1.unit/ops_tests/test_airgap_deployment.py`, [REF_30_AIRGAP_DEPLOYMENT.md](REF_30_AIRGAP_DEPLOYMENT.md).
- **Data residency (REF_25 #12):** `ops/data_residency.py`, `test_data_residency.py`, [REF_31_DATA_RESIDENCY.md](REF_31_DATA_RESIDENCY.md).
- **Multi-region AS (REF_25 #18):** `ops/multi_region_auth.py`, `test_multi_region_auth.py`, [REF_32_MULTI_REGION_AUTH.md](REF_32_MULTI_REGION_AUTH.md).
- **Abuse resistance (REF_25 #13):** `ops/abuse_resistance.py`, `test_abuse_resistance.py`, [REF_33_ABUSE_RESISTANCE.md](REF_33_ABUSE_RESISTANCE.md).
- **B2B delegated admin (REF_25 #15):** `ops/b2b_delegated_admin.py`, `test_b2b_delegated_admin.py`, [REF_34_B2B_DELEGATED_ADMIN.md](REF_34_B2B_DELEGATED_ADMIN.md).
- **Compliance pack (REF_25 #11):** `ops/compliance_pack.py`, `test_compliance_pack.py`, [REF_35_COMPLIANCE_PACK.md](REF_35_COMPLIANCE_PACK.md).
- **Login UI a11y (REF_25 #10):** `ops/login_ui_accessibility.py`, `tests/1.unit/ops_tests/test_login_ui_accessibility.py`, [REF_36_LOGIN_UI_ACCESSIBILITY.md](REF_36_LOGIN_UI_ACCESSIBILITY.md).
- **TCO benchmark evidence (REF_25 #19):** `ops/tco_evidence.py`, `tests/1.unit/ops_tests/test_tco_evidence.py`, [REF_37_TCO_BENCHMARK_EVIDENCE.md](REF_37_TCO_BENCHMARK_EVIDENCE.md).
- **Pen test engagement (REF_25 #1):** `ops/pen_test_engagement.py`, `tests/1.unit/ops_tests/test_pen_test_engagement.py`, [REF_38_PENETRATION_TEST_ENGAGEMENT.md](REF_38_PENETRATION_TEST_ENGAGEMENT.md).
- **OIDC self-cert readiness (REF_25 #2):** `ops/oidc_self_cert_readiness.py`, `tests/1.unit/ops_tests/test_oidc_self_cert_readiness.py`, [REF_39_OIDC_SELF_CERT_READINESS.md](REF_39_OIDC_SELF_CERT_READINESS.md).
- **IaC tenants/clients (REF_25 #3):** `ops/infra_as_code_tenants.py`, `tests/1.unit/ops_tests/test_infra_as_code_tenants.py`, [REF_40_INFRA_AS_CODE_TENANTS.md](REF_40_INFRA_AS_CODE_TENANTS.md).
- **Kubernetes operator readiness (REF_25 #4):** `ops/kubernetes_operator_readiness.py`, `tests/1.unit/ops_tests/test_kubernetes_operator_readiness.py`, [REF_41_KUBERNETES_OPERATOR_READINESS.md](REF_41_KUBERNETES_OPERATOR_READINESS.md).
- **Admin API + OpenAPI parity (REF_25 #7):** `ops/admin_api_openapi_parity.py`, `tests/1.unit/ops_tests/test_admin_api_openapi_parity.py`, [REF_42_ADMIN_API_OPENAPI_PARITY.md](REF_42_ADMIN_API_OPENAPI_PARITY.md).
- **Extension model readiness (REF_25 #8):** `ops/extension_model_readiness.py`, `tests/1.unit/ops_tests/test_extension_model_readiness.py`, [REF_43_EXTENSION_MODEL_READINESS.md](REF_43_EXTENSION_MODEL_READINESS.md).
- **Session/device reference UI (REF_25 #14):** `ops/session_device_reference_ui.py`, `tests/1.unit/ops_tests/test_session_device_reference_ui.py`, [REF_44_SESSION_DEVICE_REFERENCE_UI.md](REF_44_SESSION_DEVICE_REFERENCE_UI.md).

**Related:** [REF_23_COMPETITIVE_PARITY_WIN_PLAN.md](REF_23_COMPETITIVE_PARITY_WIN_PLAN.md), [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md), [REF_26_INTEGRATOR_SECURITY_CHECKLIST.md](REF_26_INTEGRATOR_SECURITY_CHECKLIST.md).

---

## Appendix A — TCO snapshot (stub)

One-page narrative for buyers comparing **self-hosted** stacks. Refine with measured numbers after **#6** exists.

| Dimension | XW stack (library + reference API) | Keycloak (typical) | Ory (Hydra + Kratos + UI glue) |
|-----------|--------------------------------------|--------------------|--------------------------------|
| Moving parts | `xwauth` + `xwlogin` + `xwauth-api` + storage + your app | Single product, heavy JVM process | Multiple services + custom login |
| Memory / CPU | Python + ASGI; scale with workers | JVM footprint often higher baseline | Go services; ops complexity |
| Upgrade cadence | You own semver across repos | Infamous upgrade/testing cycles | Multiple components to align |
| Staff skills | Python, OAuth details, XW patterns | Java, Keycloak domain | Go/K8s + OAuth + composition |
| Time to “boring” prod | Golden path + LTS still in flight | Mature but painful | Flexible but assembly-heavy |

*This appendix is intentionally short until benchmark and golden-path evidence exists.*

**Measured numbers:** capture methodology and validate microbench JSON per [REF_37_TCO_BENCHMARK_EVIDENCE.md](REF_37_TCO_BENCHMARK_EVIDENCE.md); optional checked-in artifacts under `docs/logs/benchmarks/`.

---

## Appendix B — LTS and breaking-change policy (draft)

Not ratified until published under `docs/GUIDE_*` or release process; use for planning only.

1. **Semantic versioning** for `exonware-xwauth`, `exonware-xwlogin`, `exonware-xwauth-api`: MAJOR for incompatible public API or wire-format changes; MINOR for backward-compatible features; PATCH for fixes.
2. **Security patches** backported to the **latest release line** at minimum; define `N-1` minor support window when LTS is declared.
3. **Migration notes** required for every MAJOR: link from release notes and `docs/REF_52_MIGRATION.md` (or successor).
4. **Deprecation:** two-minor warning period for removals where feasible; emit runtime warnings in reference API when configured.
5. **Pre-release** (`a`, `b`, `rc`) tags allowed; production guidance: pin to stable only.

---

*Last updated: 2026-04-03*
