# REF_54 - Protocol Deviation Register

**Project:** `xwauth`  
**Last Updated:** 01-Apr-2026  
**Status:** Active register (must be reviewed weekly)

---

## Purpose

Track protocol deviations and waivers with explicit owners and closure dates. This register is release-governing for profile `B` and `C`.

---

## Severity Model

- `critical`: Standards break with security/interoperability risk. Release blocking.
- `high`: Material interoperability risk. Must have bounded closure plan.
- `medium`: Non-blocking but tracked remediation.
- `low`: Cosmetic/documentation-only gaps.

---

## Register

| ID | Standard | Surface | Severity | Description | Owner | Opened | Target Closure | Status |
|---|---|---|---|---|---|---|---|---|
| DEV-2026-001 | RFC 8414 | OAuth discovery metadata | medium | Discovery metadata was not consistently carrying active FAPI flags from runtime config. | Auth Platform | 01-Apr-2026 | 05-Apr-2026 | Closed |
| DEV-2026-002 | Internal profile contract (`A/B/C`) | API startup route contract | high | Startup path accepted handlers without strict endpoint profile contract checks in strict mode. | Auth Platform | 01-Apr-2026 | 06-Apr-2026 | Closed |
| DEV-2026-003 | SAML 2.0 strict validation | SAML assertion pipeline | medium | `saml_strict_validation` existed as implicit behavior but was not first-class in config schema and profile requirements. | Identity Team | 01-Apr-2026 | 10-Apr-2026 | Closed |
| DEV-2026-004 | SAML 2.0 core | `/v1/auth/sso/*` assertion handling | medium | XML digital signature verification and full IdP trust-chain validation are not implemented; strict mode covers structural checks, replay, and time bounds only. | Identity Team | 01-Apr-2026 | TBD | Open |

---

## Governance Rules

- **Weekly review (SLA):** Each Monday (or first business day), triage open rows, update target dates, and attach evidence links for closures. Owners respond within **5 business days** on new `high` items.
- All `critical` items must be `Closed` before release.
- `high` items require documented waiver approval for any release.
- Each deviation must map to:
  - one standards clause,
  - one code anchor,
  - one test anchor,
  - one explicit owner.

Automated governance gate:

- `xwauth/.github/workflows/protocol-governance.yml`
- checker: `xwauth/scripts/protocol_governance_check.py`
- behavior: build fails when unresolved `critical` deviations exist.
  - profile-aware rule: profile `C` also fails on unresolved `high` deviations.

---

## Related References

- `REF_53_PROTOCOL_TRACEABILITY_MATRIX.md`
- `REF_55_PROTOCOL_PROFILE_SCHEMA_NOTES.md`
- `REF_51_TEST.md`
