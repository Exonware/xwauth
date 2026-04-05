# REF_55 - Protocol Profile Schema Notes

**Project:** `xwauth`  
**Last Updated:** 01-Apr-2026  
**Audience:** `xwauth` and `xwauth-api` maintainers

---

## Purpose

Define strictness profiles `A/B/C` and startup enforcement semantics for protocol rigor.

---

## Config Schema (Current)

The protocol rigor schema is enforced via `XWAuthConfig`:

- `protocol_profile`: `A | B | C`
- `protocol_strict_startup_validation`: `bool`
- `saml_strict_validation`: `bool`
- `default_scopes`: `list[str]`

Supporting profile requirements are defined in config constants and validated through `XWAuthConfig.validate()`.

---

## Profile Contract

| Profile | Min conformance target | Required controls |
|---|---:|---|
| `A` | 98.0% | OAuth 2.1 baseline (`oauth21_compliant`, strict redirect URI, `state`, `PKCE-S256`) |
| `B` | 99.0% | Profile A + FAPI controls (`fapi20_compliant`, `fapi20_require_par`) |
| `C` | 99.5% | Profile B + stronger sender-constraining/JAR and strict SAML validation |

---

## Startup Enforcement Behavior

`xwauth-api` startup enforces profile rigor in two stages:

1. Config validation (`XWAuthConfig.validate()`) validates profile/flag coherence.
2. Route registration strict contract validation ensures all handlers have valid `xwaction` endpoint metadata when strict mode is enabled.

Strict mode source of truth:

- `strict_protocol_profile_validation` argument to `register_auth_routes_from_services`, or
- `config.protocol_strict_startup_validation` fallback.

---

## Discovery Alignment

`/.well-known/oauth-authorization-server` now includes active FAPI signals from runtime config:

- `fapi20_compliant`
- `fapi20_require_par`
- `fapi20_require_jar`
- `fapi20_require_dpop_or_mtls`

This prevents profile drift between enforcement and published metadata.

Additional alignment now enforced:

- `grant_types_supported` omits `password` when `allow_password_grant=False`.
- `scopes_supported` is sourced from runtime `default_scopes`.
- `jwks` endpoint supports lifecycle publication from config:
  - `jwks_active_keys`
  - `jwks_next_keys`
  - `jwks_publish_next_keys`

---

## Conformance Gate Artifacts

`xwauth-api` publishes protocol scorecard artifacts through CI:

- Workflow: `xwauth-api/.github/workflows/protocol-conformance.yml`
- Generator: `xwauth-api/scripts/protocol_scorecard.py`
- Outputs (per profile matrix `A/B/C`):
  - `artifacts/protocol-junit-<profile>.xml`
  - `artifacts/protocol-scorecard-<profile>.json`
  - `artifacts/protocol-scorecard-<profile>.json.sha256`
  - `artifacts/protocol-interop-matrix-<profile>.json`

Gate thresholds are profile-bound (`A=98.0`, `B=99.0`, `C=99.5`) and enforced via scorecard generation.

---

## Release checklist (protocol rigor)

Before tagging or promoting a release that claims profile conformance:

- Confirm `xwauth-api` workflow **Protocol Conformance Gate** passed for the same commit on all matrix profiles (`A`, `B`, `C`).
- Download or retain CI artifacts: JUnit XML, signed scorecard JSON (and `.sha256`), and interop matrix JSON for the release build.
- Run `xwauth/scripts/protocol_governance_check.py --profile C` locally if you changed protocol-facing code; ensure no new open critical/high deviation rows without an approved register entry (`REF_54`).

---

## Environment Variables

- `XWAUTH_PROTOCOL_PROFILE` (`A` default)
- `XWAUTH_PROTOCOL_STRICT_STARTUP_VALIDATION` (`true` default)
- `XWAUTH_SAML_STRICT_VALIDATION` (`false` default)
- `XWAUTH_DEFAULT_SCOPES` (comma-separated, default: `openid,profile,email`)

---

## Related References

- `REF_53_PROTOCOL_TRACEABILITY_MATRIX.md`
- `REF_54_PROTOCOL_DEVIATION_REGISTER.md`
- `REF_60_OPS_TIER_PROFILE_CONTRACT.md`
