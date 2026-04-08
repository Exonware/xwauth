# REF_29 — Interop disclosure scope & fuzzing guidance

**Purpose:** REF_25 #20 — give researchers and customers a **clear technical scope** for protocol/interop findings and suggested fuzz targets.  
**Machine-readable:** `exonware.xwauth.ops.research_program` (`interop_bounty_policy`, `fuzzing_recommendations`)  
**Tests:** `tests/1.unit/ops_tests/test_research_program.py`

---

## Status

Policy ``status`` is **`draft`** until any paid bounty is announced. **Coordinated disclosure is always welcome** via [SECURITY.md](SECURITY.md).

---

## Interop / bounty scope (summary)

**In scope (examples):** spec violations with security impact, JWT/JWKS verification bugs, SAML/SCIM flaws when enabled, reproducible breaks against major IdPs.

**Out of scope (examples):** third-party-only bugs without our fix path, pure volumetric DoS without a compelling default-config story, social engineering, unsupported versions.

Full lists are in `interop_bounty_policy()` so CI can assert they stay non-empty.

---

## Fuzzing

Recommended targets are listed in `fuzzing_recommendations()["targets"]` — OAuth/OIDC parsers, JWT headers/claims, redirect URI handling, SAML/SCIM when extras are on.

We do **not** ship a fuzz binary; use **Hypothesis** (property tests), **Atheris**, or HTTP black-box tools against a local **xwauth-api** instance.

---

## Advisories

Fixed issues may receive **EXONWARE-SA-** identifiers per [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md).

---

*Last updated: 2026-04-03*
