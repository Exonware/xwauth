# Project Reference — xwauth (XWOAuth)

**Library:** exonware-xwauth  
**Last Updated:** 01-Apr-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)  
**Producing guide:** GUIDE_22_PROJECT. Per REF_35_REVIEW.

---

## Vision

**XWOAuth (xwauth)** is the **centralized, universal authorization system** for eXonware: not only a library but a full authorization system with APIs and user interfaces. It supports almost any authorization standard (OAuth 1, OAuth 2, OIDC, future standards, DCE), **more connectors than any other system** (target **≥100**; current ~64), seamless Exonware integration (xwstorage, xwbase, all future APIs), backward compatibility with legacy systems, and the power to **replace Firebase Auth and more**. Success = universal standards + maximum connectivity + extremely short, seamless developer experience + extremely fast performance using all Exonware libraries.

---

## Goals (from REF_01_REQ, ordered)

1. **Universal standards:** OAuth 1, OAuth 2, OIDC, future standards (e.g. DCE) — extend as new ones emerge.
2. **Maximum connectors:** At least 100 connectors; connect to more things than anything else online.
3. **Exonware integration:** Used in xwstorage, xwbase, all future APIs; easy, seamless integration.
4. **Backward compatibility:** Work with systems developed before xwauth by extending the authorization provider.
5. **Firebase Auth replacement and beyond.**
6. **Developer experience:** Extremely short and seamless code for auth; really small, really powerful, highest efficiency.
7. **Performance:** Extremely fast, using everything available in Exonware libraries.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | OAuth 1, OAuth 2, OIDC, SAML; grant types, PKCE, PAR, DCR, device code, token exchange | High | Done |
| FR-002 | Provider integrations — **≥100 connectors** (current ~64; add ~36+) | High | In progress |
| FR-003 | Token and session management; introspection, revocation | High | Done |
| FR-004 | RBAC, ABAC, ReBAC; FGA | High | Done |
| FR-005 | xwentity, xwstorage, xwaction, xwbase integration | High | Done |
| FR-006 | API layer (REF_15_API) + authorization system APIs and UIs | High | Done |
| FR-007 | 4-layer tests | High | Done |
| FR-008 | Backward compatibility (extend auth provider for legacy systems) | High | In scope |
| FR-009 | New standards support (e.g. DCE) as they emerge | High | Future |

---

## Non-Functional Requirements (5 Priorities)

1. **Security:** OWASP Top 10; credential handling; token storage; input validation; secure sessions; CSRF; rate limiting (ongoing review).
2. **Usability (top priority):** **Developer experience** — extremely short and seamless code; really small surface; really powerful; highest efficiency. Clear API, REF_15_API, guides (GUIDE_01_USAGE, _archive/guides), deployment (_archive/deployment).
3. **Maintainability:** Contracts/base/facade; REF_*; logs; pluggable provider modules.
4. **Performance (top priority):** **Extremely fast;** use everything available in Exonware libraries; highest efficiency; really small, really powerful.
5. **Extensibility:** Pluggable providers (100+ connectors); new standards as they emerge; custom grant types; backward compatibility.

---

## Project Status Overview

- **Current phase:** Alpha (Medium–High). Large codebase; OAuth1, OAuth2, OIDC, PKCE, SAML, providers (~64); integrations (Django, FastAPI, Flask); 0.core–3.advance.
- **Docs:** REF_01_REQ, REF_22_PROJECT (this file), REF_13_ARCH, REF_14_DX, REF_15_API, REF_35_REVIEW; guides and deployment under docs/.
- **XWOAuth role:** Centralized universal authorization system; Firebase Auth replacement; ≥100 connectors target.

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core OAuth 2.0 and providers | v0.0.1 | Done |
| M2 — API server and integrations | v0.0.1 | Done |
| M3 — REF_* and doc placement | v0.0.1 | Done |
| M4 — Security audit (OWASP) | Future | Ongoing |
| **M5 — Reach ≥100 connectors** | Future | Current ~64; add ~36+ |
| **M6 — New standards (e.g. DCE) + “extremely fast” optimization** (Exonware libs) | Future | In scope |

**DoD (M5):** At least 100 connectors documented and usable; gap from current ~64 filled.  
**DoD (M6):** Performance optimized with Exonware libraries; DX “extremely short and seamless” validated.

---

## Traceability

- **Requirements:** [REF_01_REQ.md](REF_01_REQ.md)
- **Idea/context:** [REF_12_IDEA.md](REF_12_IDEA.md)
- **Architecture:** [REF_13_ARCH.md](REF_13_ARCH.md)
- **Developer experience:** [REF_14_DX.md](REF_14_DX.md)
- **API reference:** [REF_15_API.md](REF_15_API.md)
- **Competitive strategy:** [REF_23_COMPETITIVE_PARITY_WIN_PLAN.md](REF_23_COMPETITIVE_PARITY_WIN_PLAN.md)
- **Ops execution plan:** [REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md](REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md)
- **Ops tier/profile contract:** [REF_60_OPS_TIER_PROFILE_CONTRACT.md](REF_60_OPS_TIER_PROFILE_CONTRACT.md)
- **Ops telemetry schema:** [REF_61_OPS_TELEMETRY_SCHEMA.md](REF_61_OPS_TELEMETRY_SCHEMA.md)
- **Ops SLI registry:** [REF_62_OPS_SLI_REGISTRY_V1.md](REF_62_OPS_SLI_REGISTRY_V1.md)
- **Review evidence:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/](logs/reviews/)

---

*See GUIDE_22_PROJECT.md for requirements process.*
