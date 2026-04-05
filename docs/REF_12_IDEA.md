# Idea Reference — exonware-xwauth (XWOAuth)

**Company:** eXonware.com  
**Producing guide:** GUIDE_12_IDEA  
**Last Updated:** 08-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)

---

## Overview

**XWOAuth (xwauth)** is the **centralized, universal authorization system** for eXonware: library + APIs + UIs; supports OAuth 1, OAuth 2, OIDC, future standards (e.g. DCE), **more connectors than any other system** (target **≥100**); seamless Exonware integration (xwstorage, xwbase, all future APIs); backward compatibility with legacy systems; replaces Firebase Auth and more. **DX:** Extremely short and seamless code; really small, really powerful, highest efficiency. **Performance:** Extremely fast using all Exonware libraries. This document captures product direction and ideas; approved ideas flow to [REF_22_PROJECT.md](REF_22_PROJECT.md) and [REF_13_ARCH.md](REF_13_ARCH.md).

### Alignment with eXonware 5 Priorities

- **Security:** OWASP; credential handling; token storage; input validation; secure sessions; CSRF; rate limiting.
- **Usability (top priority):** Developer experience — extremely short, seamless; small surface; powerful; highest efficiency.
- **Maintainability:** Contracts/base/facade; REF_*; logs; pluggable providers.
- **Performance (top priority):** Extremely fast; use all Exonware libraries; highest efficiency.
- **Extensibility:** 100+ connectors; new standards as they emerge; custom grant types; backward compatibility.

**Related Documents:**
- [REF_01_REQ.md](REF_01_REQ.md) — Requirements (source)
- [REF_22_PROJECT.md](REF_22_PROJECT.md) — Project requirements
- [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture
- [REF_14_DX.md](REF_14_DX.md) — Developer experience
- [REF_15_API.md](REF_15_API.md) — API reference
- [REF_35_REVIEW.md](REF_35_REVIEW.md) — Review summary

---

## Product Direction (from REF_01 / REF_22)

### ✅ [IDEA-001] Centralized universal authorization system (XWOAuth)

**Status:** ✅ Approved → Implemented (evolving)  
**Date:** 08-Feb-2026

**Problem:** No single system offers universal standards (OAuth1, OAuth2, OIDC, future/DCE), maximum connectors, Exonware integration, backward compatibility, and Firebase replacement with extremely short DX and extremely fast performance.

**Proposed Solution:** xwauth as XWOAuth — not only a library but authorization system with APIs and UIs; OAuth1, OAuth2, OIDC, SAML, future standards; **≥100 connectors**; xwentity, xwstorage, xwaction, xwbase integration; extend auth provider for legacy systems; Firebase Auth replacement.

**Outcome:** Implemented (M1–M3 done); M5 (≥100 connectors) and M6 (new standards + performance) in scope.

---

### ✅ [IDEA-002] Maximum connectors (≥100)

**Status:** ✅ Approved → In progress  
**Date:** 08-Feb-2026

**Problem:** Sponsor goal: connect to more things than anything else online.

**Proposed Solution:** Target **at least 100 connectors**; current codebase ~64 provider modules; add ~36+; registry pattern; pluggable provider contract.

**Outcome:** M5 milestone; DoD = 100 connectors documented and usable.

---

### ✅ [IDEA-003] Developer experience — extremely short, seamless

**Status:** ✅ Approved → In progress  
**Date:** 08-Feb-2026

**Problem:** Auth must be trivial for developers — minimal code, small surface, powerful, highest efficiency.

**Proposed Solution:** Facade and layered API; 1–3 line happy paths for authenticate/token; really small, really powerful; highest efficiency; clear REF_15_API and REF_14_DX.

**Outcome:** REF_14_DX and REF_15_API define key code and easy vs advanced; M6 DoD includes DX validation.

---

### ✅ [IDEA-004] Performance — extremely fast (Exonware libs)

**Status:** ✅ Approved → In progress  
**Date:** 08-Feb-2026

**Problem:** System must be extremely fast and efficient while supporting universal standards and 100+ connectors.

**Proposed Solution:** Use **everything available in Exonware libraries** for speed and efficiency; really small footprint; lazy/optional loading for connectors; no cap on standards or connectors.

**Outcome:** M6 milestone; performance optimization with Exonware libs.

---

### ✅ [IDEA-005] Backward compatibility and Firebase replacement

**Status:** ✅ Approved → In scope  
**Date:** 08-Feb-2026

**Problem:** Must work with systems developed before xwauth and replace Firebase Auth where needed.

**Proposed Solution:** Extend the authorization provider for legacy systems; Firebase Auth parity and beyond (sign-in methods, token lifecycle, multi-tenant where applicable).

**Outcome:** Documented in REF_01, REF_22; implementation ongoing.

---

*See [REF_01_REQ.md](REF_01_REQ.md), [REF_22_PROJECT.md](REF_22_PROJECT.md), and [REF_13_ARCH.md](REF_13_ARCH.md). Per GUIDE_12_IDEA.*
