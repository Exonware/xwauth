# Security advisories

**Maintainer:** eXonware Backend Team · **Contact:** connect@exonware.com

This index lists **published** security notices for **exonware-xwauth-connector**, **exonware-xwauth-identity**, and related packages. When no CVE-style entry exists yet, coordinated disclosure is handled via email (see [SECURITY.md](SECURITY.md)).

| ID / date | Affected | Severity | Summary | Fixed in |
|-----------|----------|----------|---------|----------|
| — | — | — | *No published advisories in this table yet.* | — |

## Process

1. Report privately per [SECURITY.md](SECURITY.md).  
2. After a fix ships, add a row above with version range and upgrade guidance.  
3. Link release notes or GitHub Security Advisory when used.

## Row template (copy into the table)

| `XW-2026-NNNN` | exonware-xwauth-connector x.y.z | High / Medium / Low | One-line impact; no exploit steps in public text | ≥ x.y.(z+1) or commit `abc1234` |

## Versioning and identifiers

- **Packages:** Advisories refer to **PyPI** release versions of `exonware-xwauth-connector`, `exonware-xwauth-identity`, and `exonware-xwauth-connector-api` (semver).  
- **Monorepo:** When fixes land before a publish, note the **commit SHA** or pre-release tag in the “Fixed in” column.  
- **CVE / GHSA:** Reserve an identifier when disclosure is coordinated; otherwise use a dated in-repo ID (e.g. `XW-2026-0001`) until one is assigned.  
- **Upgrade path:** Each row should name the **minimum safe version** (or “rebuild from SHA …”) and any **config/migration** steps.

**Related:** [INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md) · [REF_29_INTEROP_BOUNTY_AND_FUZZING.md](REF_29_INTEROP_BOUNTY_AND_FUZZING.md) (draft interop scope) · [../.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) (item 10).
