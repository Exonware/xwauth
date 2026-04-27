# Requirements Reference (REF_01_REQ)

**Project:** xwauth (exonware-xwauth-connector) â€” **XWOAuth** (centralized universal authorization system)  
**Sponsor:** eXonware.com / eXonware Backend Team  
**Version:** 0.0.1  
**Last Updated:** 08-Feb-2026  
**Produced by:** [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and planning artifacts. Template structure: [GUIDE_01_REQ.md](../../docs/guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | **XWOAuth (xwauth)** is the **centralized, universal authorization system** for eXonware: not only a library but a full authorization system with APIs and user interfaces, supporting almost any authorization standard (OAuth 1, OAuth 2, OIDC, future standards, DCE), more connectors than any other system, seamless Exonware integration (xwstorage.connect, xwbase, all future APIs), backward compatibility with legacy systems, and the power to replace Firebase Auth and more. |
| Primary users/beneficiaries | eXonware developers and apps; xwstorage.connect, xwbase, and all future APIs/systems that need auth; developers integrating with legacy or external systems; end-users of apps using xwauth. |
| Success (6 mo / 1 yr) | **Success = universal + maximum connectivity:** (1) Supports the broadest set of authorization standards (OAuth1, OAuth2, OIDC, new ones as they come, DCE). (2) **More connectors than anything that exists** â€” target **at least 100 connectors** (current codebase: ~64 provider modules; gap ~36). (3) Easily integrated with other Exonware packages; used in xwstorage.connect, xwbase, all future APIs. (4) Backward use with old systems (extending the authorization provider). (5) Replaces Firebase Auth and more. |
| Top 3â€“5 goals (ordered) | 1) **Universal standards:** Support OAuth 1, OAuth 2, OIDC, and future standards (e.g. DCE) â€” extend as new ones emerge. 2) **Maximum connectors:** At least 100 connectors; connect to more things than anything else online. 3) **Exonware integration:** Used in xwstorage.connect, xwbase, all future APIs; easy, seamless integration. 4) **Backward compatibility:** Work with systems developed before xwauth by extending the authorization provider. 5) **Firebase Auth replacement and beyond.** 6) **Developer experience:** Extremely short and seamless code for auth; really small, really powerful, highest efficiency. 7) **Performance:** Extremely fast, using everything available in Exonware libraries. |
| Problem statement | No single centralized, universal authorization system supports (a) almost every major standard (OAuth1, OAuth2, OIDC, future/DCE), (b) more connectors than any existing solution, (c) deep Exonware integration, (d) backward compatibility with legacy systems, and (e) Firebase Auth replacement â€” with a developer experience that is extremely short, seamless, small, and efficient. |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| **Standards:** OAuth 1, OAuth 2, OIDC, future standards (e.g. DCE), SAML (present in codebase); grant types, PKCE, PAR, DCR, device code, token exchange; RFC 7521/7662/7009/8628/9068/9101/9207/9126/9449/8705. **Connectors:** At least **100 connectors** (current: ~64 provider modules; add ~36+). **System shape:** Library + authorization system with APIs + user interfaces. **Integration:** xwentity, xwstorage.connect, xwaction, xwstorage.connect, xwbase, all future Exonware APIs. **Backward:** Extend auth provider for legacy systems. **DX:** Extremely short, seamless developer code; small, powerful, highest efficiency. **Performance:** Extremely fast using all Exonware libraries. **Existing:** Token/session management, RBAC/ABAC/ReBAC, MFA, API server, 4-layer tests. | Nothing explicitly out of scope for standards or connector growth; out of scope to be non-universal or to have fewer connectors than target. | xwentity, xwstorage.connect, xwaction; xwbase; Exonware libraries (for performance and DX). | Not to be â€œjust a libraryâ€ without APIs and UIs; not to cap connectors below â€œmost on Earthâ€; not to compromise on DX (must stay extremely short and seamless) or efficiency. |

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|----------------|
| eXonware.com; eXonware Backend Team (author, maintainer, final say on scope and priorities). | eXonware library and app teams (xwstorage.connect, xwbase, xwentity, xwaction, xwquery, etc.); xwauth-server maintainers; developers integrating auth. | Future: open-source adopters; apps replacing Firebase Auth or needing universal connectors. | Developers and internal eXonware teams; AI agents; downstream REF_22 / REF_13 / REF_15 owners. |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| Deferred â€” same as eXonware norm. OAuth/OIDC RFCs and standards as implemented. | OWASP alignment; token encryption; secure sessions; CSRF; rate limiting; credential handling; input validation (REF_22). | Deferred â€” no additional certifications required unless production/government need arises. |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1â€“3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| (1) **Integrate auth in minimal code:** Developer adds xwauth and gets sign-in in 1â€“3 lines. (2) **Add a new connector:** Configure or plug a provider; system supports 100+ connectors. (3) **Replace Firebase Auth:** Migrate app to xwauth with parity and more. (4) **Connect legacy systems:** Use xwauth as extending auth provider for pre-existing systems. (5) **Use across Exonware:** xwstorage.connect, xwbase, future APIs use xwauth as the single auth system. | Developer who needs auth with minimal code: **extremely short and seamless** â€” authenticate or use the code in the smallest, most efficient way; small surface, high power, highest efficiency. | **DX is a top priority:** extremely short, seamless flows; really small API surface; really powerful; highest efficiency. Docs and errors must support that. | â€œExtremely short and seamlessâ€; â€œreally small, really powerful, very efficient, highest efficiencyâ€; replace Firebase Auth; more connectors than anything else. |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1â€“3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| **Facade:** XWAuth, XWAuthConfig. **Endpoints:** authorize, token, introspect_token, revoke_token; device authorization (RFC 8628). **Auth methods:** EmailPassword, MagicLink, PhoneOTP; MFA (TOTP, SMS, Email, BackupCodes); WebAuthn/passkeys. **Authorization:** RBAC, ABAC, ReBAC; FGA. **Tokens/sessions:** TokenManager, SessionManager; JWT and opaque. **Providers:** 100+ connectors (current ~64); registry and pluggable adapters. **Server:** APIs and UIs for the authorization system. (From REF_15 and codebase.) | **Easy (1â€“3 lines):** Authenticate or obtain token with minimal code; add a connector; use from xwstorage.connect/xwbase. **Advanced:** Custom grant types, ReBAC/FGA, PAR, DCR, token exchange, per-RFC options. | Exonware (xwstorage.connect, xwbase, xwentity, xwaction); legacy systems via extending auth provider; Firebase Auth replacement surface where applicable. | Internal registry/storage details; unstable or experimental APIs until documented. |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Use **everything available in Exonware libraries** for speed and efficiency. No cap on supported standards or connectors. | Contracts/base/facade; provider abstraction; three-tier (library + authorization system with APIs + UIs). Pluggable connectors; registry. | **Extremely fast:** use all Exonware libraries for highest efficiency; really small footprint, really powerful. No explicit SLA stated; â€œhighest efficiencyâ€ and â€œextremely fastâ€ are requirements. | Python reference implementation; Exonware ecosystem (xwstorage.connect, xwbase, etc.). Multi-language via APIs/servers. |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| OWASP alignment; credential handling; token storage; input validation; secure sessions; CSRF; rate limiting (per REF_22). | **Top priority:** **Developer experience** â€” extremely short and seamless code; really small surface; really powerful; highest efficiency. Clear API, REF_15_API, guides. | Contracts/base/facade; REF_*; logs; pluggable provider modules. | **Top priority:** **Extremely fast;** use everything available in Exonware libraries; highest efficiency; really small, really powerful. | Pluggable providers (100+ connectors); new standards as they emerge (OAuth1, OAuth2, OIDC, DCE, future); custom grant types; backward compatibility with legacy systems. |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| **Done:** M1 Core OAuth + providers; M2 API server + integrations; M3 REF_* and docs. **Current/Future:** M4 Security audit; **M5 Reach â‰¥100 connectors** (current ~64; add ~36+); M6 New standards (e.g. DCE) and â€œextremely fastâ€ optimization using all Exonware libs. | M5 DoD: At least 100 connectors documented and usable; gap from current ~64 filled. M6 DoD: Performance optimized with Exonware libraries; DX â€œextremely short and seamlessâ€ validated. | Scope (universal standards, â‰¥100 connectors, DX, performance) is fixed; dates flexible unless stated. |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|---------------------|
| (1) **Connector growth:** Reaching and maintaining 100+ connectors â€” mitigate with registry pattern, clear provider contract, community or internal contributions. (2) **Performance vs breadth:** Supporting every standard and 100+ connectors while staying â€œreally smallâ€ and â€œextremely fastâ€ â€” mitigate by using Exonware libs and lazy/optional loading. (3) **DX vs flexibility:** Keeping 1â€“3 line ease while supporting advanced flows â€” mitigate with facade and layered API. | Exonware libraries (xwentity, xwstorage.connect, xwaction, xwbase, etc.) remain available and performant; xwstorage.connect and xwbase (and future APIs) will use xwauth; sponsor prioritizes universal standards + max connectors + DX + speed. | If Exonware abandons unified auth or caps connector/standard scope, or if DX/performance goals cannot be met. |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 08-Feb-2026 | REF_01 discovery | Requirements Collector | REF_01_REQ created; draft from REF_22, REF_13, REF_15; full question set posed |
| 08-Feb-2026 | REF_01 discovery | Sponsor | Vision: XWOAuth = centralized universal authorization system (library + APIs + UIs); OAuth1/OAuth2/OIDC/future/DCE; **â‰¥100 connectors** (most on Earth); Exonware integration; backward compatibility; Firebase replacement; **DX = extremely short, seamless, small, powerful, highest efficiency**; **performance = extremely fast** using all Exonware libs. Reverse-engineered: ~64 provider modules today; OAuth1, OAuth2, OIDC, SAML, DCR, PAR, device code, token exchange, RFC 7521/7662/7009/8628/9068/9101/9207/9126 in codebase. REF_01 updated. |
| 08-Feb-2026 | REF_01 feed | Requirements Collector | Compliance Section 4 set to deferred (eXonware norm). Clarity checklist 14/14; Ready to fill downstream docs. Fed REF_01 into REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API. |

## 12. Clarity Checklist

| # | Criterion | â˜ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | â˜‘ |
| 2 | Primary users and success criteria defined | â˜‘ |
| 3 | Top 3â€“5 goals listed and ordered | â˜‘ |
| 4 | In-scope and out-of-scope clear | â˜‘ |
| 5 | Dependencies and anti-goals documented | â˜‘ |
| 6 | Sponsor and main stakeholders identified | â˜‘ |
| 7 | Compliance/standards stated or deferred | â˜‘ |
| 8 | Main user journeys / use cases listed | â˜‘ |
| 9 | API / "key code" expectations captured | â˜‘ |
| 10 | Architecture/technology constraints captured | â˜‘ |
| 11 | NFRs (Five Priorities) addressed | â˜‘ |
| 12 | Milestones and DoD for first milestone set | â˜‘ |
| 13 | Top risks and assumptions documented | â˜‘ |
| 14 | Sponsor confirmed vision, scope, priorities | â˜‘ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** â˜‘ Yes

---

## Requirements Understood â€” Summary (for sponsor confirmation)

- **Vision:** XWOAuth (xwauth) is the **centralized, universal authorization system** for eXonware: library + APIs + UIs; supports OAuth 1, OAuth 2, OIDC, future standards (e.g. DCE); **more connectors than anything else** (target **â‰¥100**; current ~64); seamless Exonware integration (xwstorage.connect, xwbase, all future APIs); backward compatibility with legacy systems; replaces Firebase Auth and more.
- **In scope:** Universal standards support; â‰¥100 connectors; Exonware integration; backward compatibility; Firebase replacement; **DX = extremely short, seamless, small, powerful, highest efficiency**; **performance = extremely fast** using all Exonware libraries.
- **Out of scope:** Being non-universal; capping connectors below â€œmost on Earthâ€; compromising on DX or efficiency.
- **Top goals (ordered):** (1) Universal standards (OAuth1, OAuth2, OIDC, new ones, DCE). (2) Maximum connectors (â‰¥100). (3) Exonware integration. (4) Backward compatibility. (5) Firebase Auth replacement and beyond. (6) DX: extremely short, seamless, small, powerful, highest efficiency. (7) Performance: extremely fast with Exonware libs.
- **Main constraints:** Dependencies on xwentity, xwstorage.connect, xwaction, xwbase, Exonware libs; anti-goals = not â€œjust a library,â€ not fewer connectors than target, not weak DX or efficiency.

*Requirements confirmed; compliance deferred to eXonware norm. Downstream docs fed from this REF_01.*

---


