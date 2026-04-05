# REF_27 — Enterprise IdP OIDC quirks (interop lab notes)

**Purpose:** Capture **configuration patterns** that commonly break federation if handled naively.  
**Code:** `exonware.xwauth.federation.idp_quirks` (REF_25 #9).  
**Tests:** `tests/1.unit/federation_tests/test_idp_quirk_contracts.py`.

---

## Issuer URL normalization

Always normalize issuer strings with `normalize_oidc_issuer_url()` before building discovery URLs or comparing to token `iss`. Trailing slashes and stray whitespace break string equality and produce bad `/.well-known` paths.

`fetch_openid_configuration()` applies this normalization internally.

---

## Microsoft Entra ID (Azure AD) — `/common` and `/organizations`

- **Symptom:** Discovery and authorization used `https://login.microsoftonline.com/common/v2.0` (or `organizations`) but the **id_token `iss`** is **tenant-specific**, e.g. `https://login.microsoftonline.com/{tenant-guid}/v2.0`.
- **Fix:** After you obtain the id_token (or decode it unverified once), compute  
  `suggested_entra_multitenant_additional_issuers(discovery_issuer, token["iss"])`  
  and pass the result as `OidcIdTokenValidationParams.additional_allowed_issuers` together with `issuer=discovery_issuer`.
- **Tests:** `test_entra_common_discovery_accepts_tenant_token_iss`, `test_entra_common_discovery_fails_without_additional_issuer`.

---

## Okta — custom authorization server path

- **Symptom:** Issuer mismatch when operators paste `https://dev-xxx.okta.com/oauth2/default/` with a trailing slash but tokens use the canonical form without it (or vice versa).
- **Fix:** Normalize with `okta_authorization_server_base()` (same as issuer normalization today). The token `iss` must still match the configured issuer after normalization.

---

## Google

- **Issuer:** `GOOGLE_OIDC_ISSUER` (`https://accounts.google.com`).
- **Audience:** Usually a **single string** client id (`*.apps.googleusercontent.com`). Multi-audience tokens need `expected_azp` per OIDC rules (already covered in `OidcIdTokenValidationParams`).
- **Test:** `test_google_shaped_string_audience_accepted`.

---

## Next steps (interop lab)

- Record **real** JWKS + id_token samples from staging tenants (redacted) under `docs/logs/reviews/` when available.
- Extend this REF with vendor-specific claim mapping notes (groups, `tid`, etc.) as broker features harden.

---

*Last updated: 2026-04-03*
