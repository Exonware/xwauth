# Federation interoperability matrix (target)

**How to run / extend:** [GUIDE_12_FEDERATION_INTEROP_LAB.md](../GUIDE_12_FEDERATION_INTEROP_LAB.md) (ROADMAP #8 — recorded contracts + CI layers).

This matrix defines **minimum** enterprise IdP rows the project aims to keep green in CI (smoke) and in periodic full runs. Rows are expanded over time; exit criteria focus on secure defaults and predictable claim mapping.

## Enterprise protocol coverage (summary)

| Capability | Role in xwauth | Primary surfaces |
|------------|----------------|------------------|
| **OAuth 2.0 + PKCE (RFC 7636)** | Authorization server enforces PKCE on authorization-code grants; federation **client** uses `code_verifier` on start + token exchange | `core/grants/authorization_code.py`, `core/pkce.py`, `FederationBroker.start_oauth2` / `complete_oauth2`, `providers/base.py` (`get_authorization_url`, `exchange_code_for_token`) |
| **OpenID Connect** | Discovery, userinfo, id_token validation (JWKS) for upstream IdPs and for this stack via `docs/REF_53_*` | `oauth_http/discovery.py`, `handlers/mixins/oidc.py`, `FederationBroker` + per-provider `oidc_issuer` / `oidc_jwks_uri` |
| **SAML 2.0** | SP-side assertion validation (enterprise IdPs) | `core/saml.py`, `exonware-xwauth[saml]` for XML-DSig; rows below |
| **LDAP / Active Directory** | Directory bind + search, JIT attributes | `LDAPProvider`, `ActiveDirectoryProvider`, `authenticate_federated_*` |
| **SCIM 2.0** | User/group provisioning API (service provider) | `scim/*`, `XWAuth.scim_users` / `scim_groups`, `handlers/mixins/scim.py`; traceability `REF_53` |
| **WebAuthn / passkeys** | Registration + assertion, discoverable credentials, attestation policy | `exonware-xwlogin`: `authentication/webauthn.py`, `handlers/mixins/passkeys.py`; `REF_MFA_WEBAUTHN_THREAT_MODEL` |

## OIDC (OAuth 2.0 + OpenID Connect)

| Row | IdP | Flow | Pass criteria (smoke) |
|-----|-----|------|------------------------|
| O-1 | Microsoft Entra ID | Authorization code + PKCE | State required; token exchange 200; userinfo or id_token claims map to `sub` + `email` |
| O-2 | Okta | Authorization code + PKCE | Same as O-1; nonce validated when `expected_nonce` is supplied |
| O-3 | Auth0 | Authorization code + PKCE | Same as O-1 |
| O-4 | Google | Authorization code + PKCE | Same as O-1 (workspace / consumer tenant quirks documented in mapping rules) |
| O-5 | Apple Sign in | Authorization code + PKCE + `response_mode=form_post` | Same as O-1 for token exchange; **no userinfo endpoint** — rely on validated `id_token` (`AppleProvider.oidc_issuer` / `oidc_jwks_uri`); include `openid` in scope; merge first-login `user` JSON with id_token claims via `merge_apple_sign_in_profile` |

**Generic OIDC:** Any standards-compliant IdP works with `ABaseProvider` subclasses or configured endpoints when `get_authorization_url` / `exchange_code_for_token` accept **`code_verifier`** (e.g. Auth0, Okta, Entra, Keycloak) — register the provider on `FederationBroker` and supply issuer/JWKS for id_token validation where applicable.

**Library hooks:** `FederationBroker.start_oauth2` / `complete_oauth2`, optional `claim_mapping_rules`, `expected_nonce`, **PKCE** (`code_verifier` on start + complete), and **JWKS-backed id_token validation** (automatic when the provider exposes `oidc_issuer` + `oidc_jwks_uri` and an `id_token` is returned — e.g. `MicrosoftProvider`, `GoogleProvider`, `AppleProvider`). Use `validate_id_token=False` to skip signature verification (not recommended in production). Inline JWKS is supported via `OidcIdTokenValidationParams(jwks=...)`.

## SAML 2.0

| Row | IdP | Pass criteria (smoke) |
|-----|-----|------------------------|
| S-1 | Entra ID / ADFS | Strict mode: audience, `NotOnOrAfter`, `InResponseTo`, replay cache; optional XML-DSig with `exonware-xwauth[saml]` |
| S-2 | Okta SAML | Same as S-1 |
| S-3 | Ping Identity / PingFederate, Shibboleth, other metadata-driven IdPs | Metadata trust snapshot + pin rotation path exercised in unit tests |

**Configuration:** `saml_strict_validation`, `saml_entity_id` / `saml_expected_audiences`, `saml_clock_skew_seconds`, `saml_idp_signing_certificates_pem`, `saml_idp_certificate_pins_sha256`, `saml_idp_ca_bundle_pem`.

## LDAP / Active Directory

| Row | Directory | Pass criteria (smoke) |
|-----|-----------|------------------------|
| L-1 | OpenLDAP | Bind + search; JIT user info; TLS default on |
| L-2 | AD | Same with `LDAPMappingContract` for `userPrincipalName` / `memberOf` |

**Flags:** `jit_provisioning`, `directory_sync_enabled` on `LDAPProvider` (sync implementation is integration-specific).

## SCIM 2.0 (user and group provisioning)

Enterprise IdPs (Okta, Entra ID, Ping, OneLogin, etc.) push user lifecycle to a SCIM endpoint. xwauth exposes **service-provider** SCIM 2.0 resources (`Users`, `Groups`), filter grammar, and PATCH semantics aligned with RFC 7644.

| Row | Target | Pass criteria (smoke / unit) |
|-----|--------|------------------------------|
| C-1 | `/Users` CRUD + list | Correct SCIM error envelopes; weak ETag semantics where configured |
| C-2 | `/Groups` + membership | Group PUT/PATCH reflects membership in backing store |
| C-3 | Filter + PATCH | `scim/filtering.py`, `scim/patch.py` covered in `tests/1.unit/scim_tests/*`; API policy in `xwauth-api` integration tests per `REF_53` |

**Entry points:** `XWAuth.scim_users`, `XWAuth.scim_groups`, HTTP mixin `handlers/mixins/scim.py`.

## WebAuthn / FIDO2 / Passkeys (first-factor MFA)

Ceremony interop targets align with **W3C WebAuthn Level 2** and consumer **passkey** behavior (platform authenticators, synced credentials policy, conditional UI). Competitors (Keycloak, Okta, Entra) converge on: strict **rpId** + **origin** binding, **UV** policy, optional **attestation** for enterprise, and **discoverable** credentials for username-less UX.

| Row | Surface | Pass criteria (smoke / unit) |
|-----|---------|------------------------------|
| W-1 | Registration (`create`) | `webauthn_rp_id` lowercased; challenge via `webauthn_challenge_handle`; `excludeCredentials` for re-enroll; duplicate `credential_id` → `credential_duplicate` |
| W-2 | Authentication (`get`) | `expected_origin` allowlist; failed crypto verify does **not** consume challenge (retry within TTL); success invalidates challenge |
| W-3 | Discoverable / conditional UI | Login options without `user_id` / empty `allowCredentials`; verify may omit `user_id` when `webauthn_discoverable_login` and credential id resolves (see `resolve_user_for_webauthn_credential` / `rebuild_webauthn_credential_index`) |
| W-4 | Enterprise attestation | Non-`none` attestation verifies when `webauthn_trusted_attestation_ca_pem` supplies PEM roots (`pem_root_certs_bytes_by_fmt` via py_webauthn) |
| W-5 | Policy | `webauthn_allow_passkey_sync=False` rejects `credential_backed_up` at registration; `webauthn_user_verification=required` maps to py_webauthn `require_user_verification` |
| W-6 | HA | `webauthn_challenge_backend=redis` + `webauthn_redis_url` for shared challenges; **`webauthn_credential_index_backend=redis`** + same URL (optional `webauthn_redis_credential_key_prefix`) for shared **credential_id → user_id** index across workers; optional **`XWAUTH_WEBAUTHN_REBUILD_CRED_INDEX=true`** on xwauth-api startup to warm index from storage |

**HTTP / config:** `exonware.xwlogin.handlers.mixins.passkeys` + `XWAuthConfig` (`webauthn_*`, `mfa_*`). **Threat model:** `docs/REF_MFA_WEBAUTHN_THREAT_MODEL.md`. **Unit coverage:** `xwlogin` repo `tests/1.unit/security_tests/test_mfa_passkeys_security.py` (CI: `.github/workflows/unit.yml` in **xwlogin**).

## TOTP / backup codes (second factor)

| Row | Mechanism | Pass criteria (smoke / unit) |
|-----|-----------|------------------------------|
| M-1 | TOTP at rest | Secret envelope encryption (`mfa_totp_secret_enc`); lockout after `mfa_totp_max_failed_attempts` |
| M-2 | Backup codes | SHA-256 digests only; single use; required on first verify for protocol profile B/C when configured |
| M-3 | Audit | `mfa.totp.*` and `webauthn.*` events logged via `AuditLogManager` when `_audit_manager` is present |

## CI

- Workflow: `.github/workflows/federation-interop-smoke.yml` runs federation + SAML unit tests in **xwauth** (with optional `[saml]` extra for XML-DSig cases).
- WebAuthn/MFA rows **W-1–W-6** / **M-1–M-3** are covered by **xwlogin** unit tests (`tests/1.unit/security_tests/test_mfa_passkeys_security.py`); run **xwlogin** CI (`.github/workflows/unit.yml`) or `pytest` in the xwlogin package checkout.
