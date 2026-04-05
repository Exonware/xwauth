# xwauth

**OAuth 2.0 / OIDC connector** — authorization server primitives, tokens, sessions, federation core, and storage contracts. **Concrete IdPs, WebAuthn/MFA, OAuth RP clients, and FastAPI login route mixins** ship in sibling package **exonware-xwlogin** (`pip install exonware-xwauth[login]` pulls `exonware-xwlogin[handlers]`). Ties to xwentity, xwstorage, xwaction where you wire them. Docs in `docs/`; competitive notes in `.references/`.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwauth
pip install exonware-xwauth[lazy]
pip install exonware-xwauth[full]
pip install exonware-xwauth[login]   # exonware-xwlogin (IdPs, clients, FastAPI login mixins)
pip install "exonware-xwauth[enterprise]"   # SAML + storage + login handlers (self-hosted AS embedding)
```

SKUs and extras: [docs/REF_39_EDITION_AND_SKUS.md](docs/REF_39_EDITION_AND_SKUS.md).

Optional: `xwauth-server` for OAuth endpoints; see [docs/](docs/) when present.

---

## Quick start

```python
from exonware.xwauth import *

# OAuth 2.0 flows, grant types, provider integration; entity-aware user/role persistence
# See docs/ and REF_* for full API and server setup
```

See [docs/](docs/) for usage, `REF_*`, and GUIDE_01_USAGE when present.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Backend** | OAuth 2.0 / OpenID Connect; authorization code, client credentials, refresh; custom providers. |
| **Integration** | xwentity (user/role), xwstorage, xwaction. |
| **Server** | xwauth-server - OAuth endpoints, multi-tenant. |
| **Security** | Token encryption, sessions, CSRF, rate limiting. |

---

## Exonware ecosystem advantage

XW-Auth is not only a standalone auth package. It is backed by the broader XW stack, so security, transport, storage, and API behavior stay consistent across services.
You can still use `xwauth` standalone with its core install and your existing stack.
Adopting more XW libraries is optional and primarily valuable when you need enterprise and mission-critical patterns with self-managed infrastructure control.

| XW library behind XW-Auth | Exact added value | Competitive edge vs typical auth stacks |
|------|----------------|----------------|
| **XWSystem** | Shared security contracts, principal normalization, OAuth error payload/status mapping, and codec/serialization plumbing. | You avoid framework-locked auth glue and inconsistent claim/error handling across services. |
| **XWStorage** | Pluggable auth persistence through one provider model (file/local today, extensible backends). | You can switch storage strategy without rewriting auth logic around a single ORM or IdP store. |
| **XWJSON** | Native structured serialization used with XWStorage-backed auth state. | Safer, more consistent state handling than ad-hoc JSON blobs spread across handlers. |
| **XWAction** | Declarative action/route integration for auth handlers and API endpoints. | Cleaner endpoint composition than scattering manual route wiring in each framework module. |
| **XWSchema** | Schema-level validation for security and authorization rule shapes. | Stronger policy correctness than relying only on runtime checks and hand-written guards. |
| **XWAPI** | Error-envelope parity between auth endpoints and the rest of your APIs. | Clients get one predictable failure contract instead of separate auth-vs-app error formats. |
| **XWEntity** | Domain-aligned user/role integration point for identity and authorization models. | Your auth layer matches your business entity model instead of living in an isolated user silo. |

This ecosystem alignment is the core differentiator: XW-Auth gives OAuth 2.0 features plus platform-level consistency from security primitives to storage and API contracts.

---

## Docs and tests

- **Security:** [SECURITY.md](SECURITY.md) (report vulnerabilities); [docs/SECURITY_ADVISORIES.md](docs/SECURITY_ADVISORIES.md) (advisory process); [docs/REF_26_INTEGRATOR_SECURITY_CHECKLIST.md](docs/REF_26_INTEGRATOR_SECURITY_CHECKLIST.md) (integrator checklist); MFA/WebAuthn: [docs/REF_MFA_WEBAUTHN_THREAT_MODEL.md](docs/REF_MFA_WEBAUTHN_THREAT_MODEL.md).
- **Competitive backlog:** [docs/REF_25_COMPETITIVE_ADVANCE_BACKLOG.md](docs/REF_25_COMPETITIVE_ADVANCE_BACKLOG.md) (20 extended ideas + TCO appendix).
- **Microbench (REF_25 #6):** `python -m exonware.xwauth.bench --iterations 2000` (after install or `PYTHONPATH=src`); see [benchmarks/README.md](benchmarks/README.md).
- **Score improvement roadmap:** [.references/ROADMAP_SCORE_20.md](.references/ROADMAP_SCORE_20.md) (20 competitive-rubric work items).
- **HA / upgrade runbook (starter):** [docs/GUIDE_03_HA_UPGRADE_RUNBOOK.md](docs/GUIDE_03_HA_UPGRADE_RUNBOOK.md) (ROADMAP #12).
- **Partner / edge matrix:** [docs/REF_33_PARTNER_INTEGRATION_MATRIX.md](docs/REF_33_PARTNER_INTEGRATION_MATRIX.md) (ROADMAP #19).
- **RFC / design process:** [docs/rfc/README.md](docs/rfc/README.md) (ROADMAP #18).
- **Multi-tenant reference story:** [docs/REF_37_MULTI_TENANT_REFERENCE_STACK.md](docs/REF_37_MULTI_TENANT_REFERENCE_STACK.md) (ROADMAP #13).
- **Observability (ROADMAP #14 — done):** [REF_63 landing](docs/REF_63_AUTH_OBSERVABILITY_CONTRACT.md); metrics/audit + **event catalog §8:** [REF_61](docs/REF_61_OPS_TELEMETRY_SCHEMA.md); SLI registry + **CI parity:** [REF_62](docs/REF_62_OPS_SLI_REGISTRY_V1.md) · `xwauth-api` workflow `core-tests` (`test_sli_registry_parity.py`).
- **Architecture diagrams:** [docs/GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md](docs/GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md) (ROADMAP #20).
- **Edition / pip SKUs:** [docs/REF_39_EDITION_AND_SKUS.md](docs/REF_39_EDITION_AND_SKUS.md) (ROADMAP #2).
- **Migration playbooks (ROADMAP #4):** [GUIDE_05 Keycloak](docs/GUIDE_05_MIGRATION_KEYCLOAK_SHAPED.md) · [GUIDE_06 Auth0](docs/GUIDE_06_MIGRATION_AUTH0_SHAPED.md) · [GUIDE_07 Supabase](docs/GUIDE_07_MIGRATION_SUPABASE_SHAPED.md); **client registry mapping:** [REF_64](docs/REF_64_CLIENT_REGISTRY_MIGRATION_MAPPING.md).
- **Reference SaaS outline (ROADMAP #3):** [GUIDE_08](docs/GUIDE_08_REFERENCE_SAAS_TEMPLATE_OUTLINE.md); **Terraform stub:** `xwauth-api/deploy/terraform/stub/`.
- **Thin OIDC client patterns (ROADMAP #16):** [GUIDE_09](docs/GUIDE_09_OIDC_THIN_CLIENT_PATTERNS.md) (PKCE, refresh §5).
- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Ops program:** [docs/REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md](docs/REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md) and `REF_60+` contracts.
- **Protocol rigor (ROADMAP #5):** [REF_53](docs/REF_53_PROTOCOL_TRACEABILITY_MATRIX.md), [REF_54](docs/REF_54_PROTOCOL_DEVIATION_REGISTER.md), [REF_55](docs/REF_55_PROTOCOL_PROFILE_SCHEMA_NOTES.md); **CI:** `xwauth-api` `.github/workflows/protocol-conformance.yml` (A/B/C); `xwauth` `.github/workflows/protocol-governance.yml` (deviation gate).
- **Federation / IdP quirks (Entra, Okta, Google):** [docs/REF_27_IDP_OIDC_QUIRKS.md](docs/REF_27_IDP_OIDC_QUIRKS.md), module `exonware.xwauth.federation.idp_quirks`.
- **SAML enterprise kit (ROADMAP #6):** [GUIDE_10](docs/GUIDE_10_SAML_ENTERPRISE_KIT.md) (`pip install "exonware-xwauth[saml]"` or `[enterprise]`).
- **SCIM hardening (ROADMAP #7):** [GUIDE_11](docs/GUIDE_11_SCIM_HARDENING.md) (`/v1/scim/v2/*`, pagination, errors, ETags).
- **Federation interop lab (ROADMAP #8):** [GUIDE_12](docs/GUIDE_12_FEDERATION_INTEROP_LAB.md); matrix: [docs/federation/INTEROP_MATRIX.md](docs/federation/INTEROP_MATRIX.md).
- **Email / magic-link ops (SPF/DKIM/DMARC):** [docs/REF_28_EMAIL_MAGIC_LINK_OPS.md](docs/REF_28_EMAIL_MAGIC_LINK_OPS.md), `exonware.xwauth.ops`.
- **Interop disclosure & fuzzing (draft):** [docs/REF_29_INTEROP_BOUNTY_AND_FUZZING.md](docs/REF_29_INTEROP_BOUNTY_AND_FUZZING.md), `exonware.xwauth.ops.research_program`.
- **Air-gapped / offline deploy:** [docs/REF_30_AIRGAP_DEPLOYMENT.md](docs/REF_30_AIRGAP_DEPLOYMENT.md), `exonware.xwauth.ops.airgap_deployment`.
- **Data residency:** [docs/REF_31_DATA_RESIDENCY.md](docs/REF_31_DATA_RESIDENCY.md), `exonware.xwauth.ops.data_residency`.
- **Multi-region AS:** [docs/REF_32_MULTI_REGION_AUTH.md](docs/REF_32_MULTI_REGION_AUTH.md), `exonware.xwauth.ops.multi_region_auth`.
- **Abuse resistance:** [docs/REF_33_ABUSE_RESISTANCE.md](docs/REF_33_ABUSE_RESISTANCE.md), `exonware.xwauth.ops.abuse_resistance`.
- **B2B delegated admin:** [docs/REF_34_B2B_DELEGATED_ADMIN.md](docs/REF_34_B2B_DELEGATED_ADMIN.md), `exonware.xwauth.ops.b2b_delegated_admin`.
- **Compliance pack (ROPA / DPA / subprocessors):** [docs/REF_35_COMPLIANCE_PACK.md](docs/REF_35_COMPLIANCE_PACK.md), `exonware.xwauth.ops.compliance_pack`.
- **Login UI accessibility (WCAG-oriented checklist):** [docs/REF_36_LOGIN_UI_ACCESSIBILITY.md](docs/REF_36_LOGIN_UI_ACCESSIBILITY.md), `exonware.xwauth.ops.login_ui_accessibility`.
- **TCO benchmark evidence:** [docs/REF_37_TCO_BENCHMARK_EVIDENCE.md](docs/REF_37_TCO_BENCHMARK_EVIDENCE.md), `exonware.xwauth.ops.tco_evidence` (`validate_microbench_output`, publish checklist).
- **Pen test engagement (executive summary path):** [docs/REF_38_PENETRATION_TEST_ENGAGEMENT.md](docs/REF_38_PENETRATION_TEST_ENGAGEMENT.md), `exonware.xwauth.ops.pen_test_engagement`.
- **OIDC self-cert readiness:** [docs/REF_39_OIDC_SELF_CERT_READINESS.md](docs/REF_39_OIDC_SELF_CERT_READINESS.md), `exonware.xwauth.ops.oidc_self_cert_readiness`.
- **IaC (Terraform/Pulumi) for tenants & clients:** [docs/REF_40_INFRA_AS_CODE_TENANTS.md](docs/REF_40_INFRA_AS_CODE_TENANTS.md), `exonware.xwauth.ops.infra_as_code_tenants`.
- **Kubernetes operator readiness:** [docs/REF_41_KUBERNETES_OPERATOR_READINESS.md](docs/REF_41_KUBERNETES_OPERATOR_READINESS.md), `exonware.xwauth.ops.kubernetes_operator_readiness`.
- **Admin API + OpenAPI parity:** [docs/REF_42_ADMIN_API_OPENAPI_PARITY.md](docs/REF_42_ADMIN_API_OPENAPI_PARITY.md), `exonware.xwauth.ops.admin_api_openapi_parity`.
- **Extension model readiness:** [docs/REF_43_EXTENSION_MODEL_READINESS.md](docs/REF_43_EXTENSION_MODEL_READINESS.md), `exonware.xwauth.ops.extension_model_readiness`.
- **Session / device reference UI:** [docs/REF_44_SESSION_DEVICE_REFERENCE_UI.md](docs/REF_44_SESSION_DEVICE_REFERENCE_UI.md), `exonware.xwauth.ops.session_device_reference_ui`; HTTP mixins: `exonware.xwauth.handlers.mixins.sessions` (`GET /auth/sessions` JSON + Bearer revoke; `GET /auth/sessions/view` HTML — Bearer or documented cookie `xwauth_reference_access_token`).
- **Tests:** From repo root, follow the project's test layout.

---

## License and links

MIT - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwauth  


## Async Support

<!-- async-support:start -->
- xwauth includes asynchronous execution paths in production code.
- Source validation: 560 async def definitions and 643 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.0.1.1 | Updated: 05-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
