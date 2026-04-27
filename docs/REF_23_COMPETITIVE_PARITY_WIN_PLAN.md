# REF_23 — Competitive Parity Win Plan

**Project:** `xwauth`  
**Objective:** Raise `xwauth` from current broad capability to top-tier competitive parity (and selective leadership) against:
- `hydra-master` for OAuth2/OIDC and sessions/tokens
- `keycloak-main` for protocol breadth, identity lifecycle, federation, MFA/passkeys, authorization, observability, and quality gates
- `zitadel-main` for multi-tenant architecture
- `logto-master` for DX/docs

This plan is intentionally execution-focused: every section includes architecture scope, implementation backlog, quality gates, and measurable exit criteria.

---

## 0) Reality Check and Win Definition

Winning does not mean "copy every feature." It means:
- Match or exceed reference behavior in critical enterprise adoption criteria
- Deliver predictable security and operations quality
- Provide better developer velocity and composability than monolith incumbents

### Win conditions

`xwauth` wins when all of the following are true:
1. **Protocol trustworthiness:** conformance and interop pass-rates at or near best-in-class
2. **Enterprise readiness:** tenancy, authz, federation, and audit are deployable without custom forks
3. **Operational confidence:** SLOs, incident diagnostics, and release quality become routine
4. **Adoption velocity:** onboarding and integration time is shorter than comparable products

### 0.1 Package responsibilities (non-negotiable)

This program assumes a 3-part product shape and hard ownership boundaries:

- **`xwauth` (core library):**
  - Source of truth for identity model, auth flows, token/session lifecycle, policy decisions, federation normalization, crypto/key lifecycle, and storage contracts.
  - Must not leak transport or UI concerns.
- **`xwauth-connector-api` (network surface over `xwapi`):**
  - Owns endpoint contracts, HTTP semantics, rate limiting, idempotency, and tenant-safe middleware orchestration.
  - Must not reimplement core auth logic.
- **`xwauth-web` (admin/end-user UX on `xwui-base`):**
  - Owns operator and self-service workflows only.
  - Must consume `xwauth`/`xwauth-connector-api` contracts, not fork policy logic.

### 0.2 Competitive scorecard matrix (current -> target -> owner -> milestone)

Scoring scale: `0-5` where `5` means parity-grade behavior with publishable evidence.

| Capability | Reference target | Current score | Target score | Primary owner | Milestone |
|---|---:|---:|---:|---|---|
| OAuth2/OIDC | `hydra-master` | 3.4 | 5.0 | `xwauth` + `xwauth-connector-api` | M1-M2 |
| Protocol breadth | `keycloak-main` | 2.6 | 5.0 | `xwauth` | M2-M3 |
| Identity lifecycle | `keycloak-main` | 3.0 | 5.0 | `xwauth` + `xwauth-web` | M2-M3 |
| Federation | `keycloak-main` | 2.8 | 5.0 | `xwauth` + `xwauth-web` | M2-M3 |
| MFA/passkeys | `keycloak-main` | 3.1 | 5.0 | `xwauth` + `xwauth-web` | M2-M3 |
| Sessions/tokens | `hydra-master` | 3.5 | 5.0 | `xwauth` | M1-M2 |
| Authorization | `keycloak-main` | 2.9 | 5.0 | `xwauth` + `xwauth-connector-api` | M2-M3 |
| Multi-tenant | `zitadel-main` | 2.5 | 5.0 | `xwauth` + `xwauth-connector-api` + `xwauth-web` | M2-M4 |
| Observability | `keycloak-main` | 2.4 | 5.0 | `xwauth` + `xwauth-connector-api` | M2-M4 |
| Quality gates | `keycloak-main` | 2.7 | 5.0 | cross-package | M1-M4 |
| DX/docs | `logto-master` | 3.0 | 5.0 | `xwauth-connector-api` + `xwauth-web` | M3-M4 |

Milestone shorthand:
- **M1:** Protocol correctness baseline
- **M2:** Enterprise protocol completion
- **M3:** Tenant/authz/federation maturity
- **M4:** Operational and adoption leadership

### 0.3 Hard success criteria for each match objective

The following are the exact parity checkpoints requested:

1. **`xwauth` matches `hydra-master` in OAuth2/OIDC**  
   - Required: OIDC conformance pass >= `98%`, strict RFC error behavior, deterministic discovery metadata.
2. **`xwauth` matches `keycloak-main` in Protocol breadth**  
   - Required: production-grade OIDC + SAML + SCIM + LDAP/AD federation, with interop evidence.
3. **`xwauth` matches `keycloak-main` in Identity lifecycle**  
   - Required: configurable lifecycle states/flows, recovery/verification/credential-event completeness.
4. **`xwauth` matches `keycloak-main` in Federation**  
   - Required: robust broker, first-login orchestration, tenant-scoped provider registries, mapping DSL.
5. **`xwauth` matches `keycloak-main` in MFA/passkeys**  
   - Required: AAL policies, hardened WebAuthn ceremonies, operational recovery model.
6. **`xwauth` matches `hydra-master` in Sessions/tokens**  
   - Required: rotation/revocation consistency and HA-safe invalidation semantics.
7. **`xwauth` matches `keycloak-main` in Authorization**  
   - Required: unified RBAC+ABAC+scopes+context decisions with explain API and traceability.
8. **`xwauth` matches `zitadel-main` in Multi-tenant**  
   - Required: strict isolation and delegated org/project administration with tenant-local controls.
9. **`xwauth` matches `keycloak-main` in Observability**  
   - Required: first-class tracing/metrics/audit with incident-grade diagnostics.
10. **`xwauth` matches `keycloak-main` in Quality gates**  
    - Required: non-bypassable CI/CD gates, migration tests, security scans, release provenance.
11. **`xwauth` matches `logto-master` in DX/docs**  
    - Required: <30m time-to-first-success and docs/examples validated continuously in CI.

---

## 1) Target: Match `hydra-master` in OAuth2/OIDC

Hydra benchmark is protocol correctness and reliability under edge cases.

### 1.1 Required architecture changes

- Split protocol engine into stricter layers:
  - Request validation and normalization
  - Grant flow execution
  - Token assembly and signing
  - Error mapping (RFC-compliant)
- Introduce explicit "conformance profile" mode:
  - Strict defaults for redirect URI matching, PKCE, client auth method handling
  - Deterministic error codes/messages per RFC behavior
- Build deterministic key management:
  - Rotating JWKS with active/next keys
  - KID pinning and rollover scheduling

### 1.2 Implementation backlog

1. Complete and harden:
   - Authorization Code + PKCE
   - Client Credentials
   - Device Authorization
   - PAR
   - Token Exchange
2. Upgrade OIDC endpoint semantics:
   - UserInfo claim filtering by scope
   - Correct `nonce`, `at_hash`, `c_hash`, `s_hash` where required
   - ID token claims profile and validation hooks
3. Expand client authentication support:
   - `client_secret_basic`, `client_secret_post`, `private_key_jwt`, `tls_client_auth` (if mTLS targeted)
4. Add discovery and metadata completeness:
   - Full issuer metadata consistency checks
5. Build interop test harness against:
   - Generic OIDC client suites
   - Regression scenarios from production incidents

### 1.3 Quality gates (must pass)

- OAuth2/OIDC conformance suite pass rate >= 98%
- No known high severity RFC-compliance bugs
- Backward compatibility matrix for client registration and token behavior

### 1.4 Exit criteria

- Drop-in compatibility for common OIDC client SDKs without custom patches
- Protocol error behavior stable across releases

### 1.5 Proof artifacts to publish

- OIDC conformance run logs and trendline by release
- Supported grants/auth methods matrix with pass/fail evidence
- RFC deviation register (must be empty or approved exception with sunset date)

---

## 2) Target: Match `keycloak-main` in Protocol Breadth

Keycloak benchmark is broad protocol support with enterprise interoperability.

### 2.1 Required protocol surface

- OAuth2/OIDC (already broad, improve depth)
- OAuth1 (keep if strategic)
- SAML 2.0 (full production-grade)
- SCIM 2.0 (HTTP API, provisioning lifecycle)
- LDAP/AD federation
- Optional: RADIUS / Kerberos bridge if enterprise roadmap requires

### 2.2 Critical gaps to close in current `xwauth`

- SAML implementation must move from simplified parsing to verified trust chain:
  - Signature validation
  - Audience, recipient, InResponseTo validation
  - Replay detection and clock skew windows
- SCIM must be promoted from in-memory service behavior to full API:
  - `/Users`, `/Groups`, `/Schemas`, `/ResourceTypes`, `/ServiceProviderConfig`
  - ETag, patch, filter, pagination, optimistic concurrency

### 2.3 Implementation backlog

1. SAML production module:
   - Metadata ingestion and certificate management
   - SP-initiated and IdP-initiated flows
   - SLO support (front/back channel strategy)
2. SCIM API module:
   - Multi-tenant SCIM endpoint partitioning
   - Provisioning webhooks and reconciliation
3. LDAP/AD connector:
   - Sync and just-in-time federation modes
   - Group/role mapping pipeline

### 2.4 Exit criteria

- Enterprise customers can run SSO + provisioning with no custom protocol code
- SCIM compatibility validated with at least 3 major IdPs

### 2.5 Protocol breadth minimum parity table

| Protocol area | Minimum parity behavior required in `xwauth` |
|---|---|
| OIDC/OAuth2 | strict endpoint semantics, PAR, token exchange, dynamic client registration depth |
| SAML 2.0 | signed/encrypted assertions, metadata rotation trust chain, replay and audience controls |
| SCIM 2.0 | Users/Groups/PATCH/filter/pagination/ETag/versioning and deprovision lifecycle |
| LDAP/AD | JIT + sync modes, group/role mapping, tenant-aware federation links |

---

## 3) Target: Match `keycloak-main` in Identity Lifecycle

### 3.1 Capability scope

- Registration flows (self-service and admin-created)
- Credential management (password/passkey/OTP/recovery codes)
- Recovery and account verification
- Account linking and profile management
- Session management and device history
- Deactivation, lockout, and retention workflows

### 3.2 Implementation backlog

1. Build flow engine for lifecycle policies:
   - Conditional steps (email verify, MFA required, risk checks)
2. Add identity states model:
   - pending, active, suspended, locked, deleted, archived
3. Credential event model:
   - every credential add/remove/rotate emits auditable events
4. Self-service portal API surfaces:
   - profile updates, security sessions, connected identities

### 3.3 Exit criteria

- Full lifecycle can be configured by policy, not hardcoded branching
- Admin and self-service flows share same domain rules

---

## 4) Target: Match `keycloak-main` in Federation

### 4.1 Required federation capabilities

- Broker model for external IdPs (OIDC/SAML/social)
- Account linking/unlinking
- Attribute and role mapping DSL
- Home realm discovery / domain discovery
- First-login flow orchestration

### 4.2 Implementation backlog

1. Provider abstraction v2:
   - Standard contract for claims, identity proofing strength, and errors
2. Mapping engine:
   - Declarative claim transforms
   - Role/group assignment rules
3. Federation reliability:
   - Retry and backoff for upstream failures
   - Circuit-breaker and fallback behaviors
4. Tenant-scoped provider registries:
   - Distinct IdP configs per org/tenant

### 4.3 Exit criteria

- Add new enterprise IdP with config-only onboarding for 80% of cases
- Predictable login behavior across mixed federation sources

### 4.4 Federation interoperability matrix (required)

At minimum, maintain continuously-tested interop rows for:
- OIDC enterprise IdPs (Azure AD/Entra, Okta, Auth0)
- SAML enterprise IdPs (ADFS, Azure AD, Okta, OneLogin)
- LDAP/AD backends (OpenLDAP, Active Directory)

Each row must include:
- login success/failure semantics
- claim/attribute mapping correctness
- group/role sync behavior
- account link and unlink lifecycle

---

## 5) Target: Match `keycloak-main` in MFA/Passkeys

### 5.1 Required MFA/passkeys scope

- TOTP with secure enrollment and backup codes
- WebAuthn passkeys:
  - Registration ceremony validation
  - Authentication ceremony validation
  - Resident/discoverable credentials support
  - Device-bound vs synced credential policy controls
- Step-up auth policies by action sensitivity and risk level

### 5.2 Implementation backlog

1. MFA policy engine:
   - AAL-level enforcement (`aal1/aal2/aal3` profile)
2. WebAuthn production hardening:
   - Attestation policy and authenticator metadata verification
   - Origin/rpId controls and replay-safe challenge lifecycle
3. Recovery architecture:
   - Secure fallback hierarchy with abuse controls
4. UX state machine:
   - Enrollment prompts, grace periods, and enforcement deadlines

### 5.3 Exit criteria

- Passkey and TOTP can be required by tenant policy
- Step-up integrates with authz decision points

---

## 6) Target: Match `hydra-master` in Sessions/Tokens

Hydra benchmark is token/session correctness at scale.

### 6.1 Required token/session capabilities

- Token issuance correctness across grants
- Introspection/revocation accuracy and latency
- Session lifecycle consistency:
  - create, rotate, revoke, revoke-all, exclude-current
- Refresh token rotation and reuse-detection controls
- Key rollover without downtime

### 6.2 Implementation backlog

1. Token store hardening:
   - Strong indexes, TTL semantics, and replay detection
2. Rotation strategy:
   - Access + refresh token family trees
3. Session store semantics:
   - Consistent invalidation across distributed nodes
4. Performance benchmarks:
   - p95 issuance and introspection latency targets

### 6.3 Exit criteria

- No token/session consistency bugs in HA deployment tests
- Revocation visible in bounded propagation window (documented SLO)

### 6.4 Session/token SLOs (mandatory)

- Access token issuance p95 < `150ms` (steady state baseline)
- Introspection p95 < `120ms`
- Revocation propagation SLO < `5s` in distributed mode
- Refresh token reuse-detection false negative rate: `0`

---

## 7) Target: Match `keycloak-main` in Authorization

### 7.1 Required authorization scope

- RBAC baseline
- Relationship/tuple-based authorization where needed (FGA)
- Policy engine with contextual conditions:
  - tenant, resource, action, environment, risk state
- Permission explainability and trace logs

### 7.2 Implementation backlog

1. Unified policy layer:
   - Merge RBAC + scopes + contextual claims into one decision graph
2. Resource server integration kit:
   - Cached policy decision SDK + async invalidation
3. Policy admin API:
   - Versioning, dry-run, simulation, rollback
4. Explain API:
   - Return why allow/deny with policy lineage

### 7.3 Exit criteria

- Authorization decisions are deterministic, explainable, and testable
- Permission model supports both coarse RBAC and fine-grained checks

### 7.4 Policy decision trace contract

`xwauth` policy decisions must return traceable metadata for audit and debugging:
- decision id
- effective scopes/roles/claims
- matched policy path
- deny reason classification
- tenant/org/project context used during evaluation

---

## 8) Target: Match `zitadel-main` in Multi-tenant

### 8.1 Required tenancy architecture

- Hierarchical tenancy:
  - instance -> organization -> project/app (or equivalent)
- Strict data isolation model
- Tenant-local branding, policy, keys, connectors
- Delegated tenant administration with scoped rights

### 8.2 Implementation backlog

1. Tenant domain model refactor:
   - Introduce immutable tenant IDs in all core entities
2. Isolation enforcement:
   - Storage-level and application-level guards
3. Tenant-scoped key management:
   - Per-tenant signing keys and rotation plans
4. Tenant migration framework:
   - Safe import/export and schema evolution

### 8.3 Exit criteria

- Tenant isolation validated via security tests and red-team scenarios
- Per-tenant config drift and blast radius are controllable

### 8.4 Multi-tenant risk controls

- Tenant boundary tests are mandatory in every release
- No cross-tenant read/write paths without explicit privileged override + audit event
- Tenant-scoped key lifecycle and rotation must be independently operable

---

## 9) Target: Match `keycloak-main` in Observability

### 9.1 Required observability stack

- Metrics:
  - protocol, auth success/failure, latency, token issuance, federation health
- Tracing:
  - distributed trace IDs across auth flows and provider calls
- Structured logs:
  - consistent event schema and correlation IDs
- Audit ledger:
  - immutable auth/audit events with retention controls

### 9.2 Implementation backlog

1. OpenTelemetry integration:
   - spans for each auth flow and external call
2. Prometheus metrics revamp:
   - replace placeholder counters with real instruments
3. Audit schema v2:
   - signed events or tamper-evident chain for high-trust deployments
4. Dashboards and alerting:
   - SLO dashboards, runbook-linked alerts

### 9.3 Exit criteria

- Operators can diagnose auth incidents in minutes, not hours
- SLOs and alerts map directly to business impact

---

## 10) Target: Match `keycloak-main` in Quality Gates

### 10.1 Required engineering gates

- Full CI pipeline:
  - lint, type-check, unit, integration, protocol conformance, security scans
- Release hardening:
  - signed artifacts, SBOM, provenance
- Compatibility testing:
  - upgrade tests, migration tests, API contract checks

### 10.2 Implementation backlog

1. CI redesign:
   - parallel jobs and mandatory checks for merge
2. Test layers formalization:
   - unit -> integration -> conformance -> chaos/load
3. Security gates:
   - SAST, dependency scanning, secret scanning, container scanning
4. Release process:
   - release train with canary and rollback policy

### 10.3 Exit criteria

- No release ships without complete gate pass
- Reproducible release artifacts with verifiable provenance

### 10.4 Required gate inventory (all blocking)

- static checks: lint + type + import graph safety
- tests: unit + integration + protocol conformance + migration regressions
- security: SAST + dependency + secret + container scanning
- release: SBOM + signed artifacts + provenance attestation

---

## 11) Target: Match `logto-master` in DX/Docs

### 11.1 Required DX outcomes

- Integration in < 30 minutes for common stacks
- Opinionated SDK examples with production-ready defaults
- Clear architecture docs and migration playbooks
- Self-service local dev + sandbox story

### 11.2 Implementation backlog

1. Docs information architecture overhaul:
   - "Get started", "Production deploy", "Security model", "Troubleshooting"
2. SDK and examples:
   - polished reference integrations (FastAPI, Node, Next.js, Django, Go)
3. Quickstart automation:
   - `docker compose up` + seeded demo tenant + test client app
4. Dev portal quality:
   - copy-paste snippets verified in CI

### 11.3 Exit criteria

- Time-to-first-success sharply reduced
- Support tickets on setup/integration drop release-over-release

---

## 12) Cross-Cutting Program Needed to "Win Everything"

You cannot achieve all targets by feature coding alone. You need a program layer:

### 12.1 Product and architecture governance

- Quarterly capability roadmap with explicit "parity" and "leadership" themes
- Architecture decision records for every major security/protocol change
- Compatibility policy and deprecation windows

### 12.2 Security program

- Threat modeling for each major flow and connector
- Annual external penetration testing
- Coordinated vulnerability disclosure and patch SLA

### 12.3 Performance and reliability program

- Load profile baselines (steady, burst, and degraded upstream provider)
- Capacity planning model
- Incident postmortem standard with corrective action tracking

### 12.4 Ecosystem strategy

- Prioritize connectors by enterprise demand
- Publish API stability guarantees
- Offer migration kits from incumbent IdPs

---

## 13) Suggested Phased Execution (24-month horizon)

### Phase 1 (0-6 months): Protocol and security foundation

- OAuth2/OIDC conformance push
- SAML production hardening
- Token/session consistency redesign
- CI quality gate baseline

### Phase 2 (6-12 months): Enterprise core

- SCIM HTTP API + provisioning
- Multi-tenant architecture v1
- Authorization engine v2
- Observability stack v1

### Phase 3 (12-18 months): Ecosystem and scale

- Federation expansion and mapping DSL
- Tenant admin and policy UX/API maturity
- Performance and HA hardening

### Phase 4 (18-24 months): Leadership polish

- Best-in-class DX and docs
- Benchmark publication and case studies
- External audits, certifications, and trust artifacts

---

## 14) Team and Capability Requirements

Minimum sustained team to execute this plan effectively:

- 2-3 protocol/security engineers (OAuth/OIDC/SAML/SCIM/WebAuthn)
- 2 platform engineers (storage, tenancy, HA, release)
- 2 product engineers (admin API, lifecycle, federation UX/API)
- 1 DevEx engineer (SDKs, docs, examples, developer tooling)
- 1 SRE/observability engineer
- 1 QA automation engineer (conformance + integration suites)

Without dedicated ownership in each area, progress will be uneven and parity goals will slip.

---

## 15) Executive Checklist (What you need to fund and commit)

To make `xwauth` win across all requested dimensions, you need:

1. **Protocol correctness investment** (conformance-first engineering)
2. **Enterprise protocol completion** (SAML + SCIM + LDAP done right)
3. **Tenant and authorization architecture refactor** (not patchwork)
4. **Production observability and release quality discipline**
5. **Developer adoption acceleration** through docs, SDKs, and examples
6. **Long-horizon execution discipline** across at least 4 phases

If these are all funded and enforced through hard quality gates, `xwauth` can move from "feature-rich" to "category-leading."

---

## 16) Recommended immediate next actions (next 30 days)

1. Establish parity scorecard dashboard with current baseline per criterion.
2. Freeze protocol behavior contract for OAuth2/OIDC and start conformance runbook.
3. Launch SAML production hardening initiative (replace simplified trust path).
4. Start SCIM HTTP API design and tenancy model RFC.
5. Stand up CI gate template (lint/type/test/security/conformance skeleton).
6. Draft DX v1 quickstart with end-to-end demo in CI.

These six actions create momentum and de-risk the largest structural gaps first.

---

## 17) 90-day concrete execution plan (owner-locked)

### Track A — Protocol and token core (`xwauth`)
- Harden OIDC/OAuth edge-case behavior and publish conformance baseline.
- Implement SCIM API-ready contracts and patch/filter semantics end-to-end.
- Complete token/session family rotation and reuse detection hardening.

### Track B — Transport parity (`xwauth-connector-api`)
- Freeze API error envelope and versioning strategy for auth endpoints.
- Add tenant-safe middleware and idempotency semantics for mutable routes.
- Add protocol-specific conformance endpoints and CI evidence export.

### Track C — Admin/operator usability (`xwauth-web`)
- Deliver federation setup wizard baseline with validation and dry-run checks.
- Add policy simulation UI and decision trace inspection.
- Add tenant/org/project delegation UX with scope-guarded actions.

### Track D — Program controls (cross-package)
- Launch parity scorecard release dashboard.
- Enforce blocking quality gates and compatibility matrix publication.
- Produce first external-facing deployment and upgrade runbook set.
