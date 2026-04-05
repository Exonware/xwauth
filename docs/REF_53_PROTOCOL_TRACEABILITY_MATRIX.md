# REF_53 - Protocol Traceability Matrix

**Project:** `xwauth`  
**Last Updated:** 01-Apr-2026  
**Scope:** OAuth2/OIDC/SAML/SCIM protocol surfaces for `xwauth` + `xwauth-api`

---

## Purpose

Define a standards-to-endpoint traceability baseline that maps protocol requirements to concrete code anchors and test coverage targets.

---

## Matrix (Baseline v1)

| Standard Clause | Endpoint/Surface | Primary Code Anchor | Current Test Anchor | Status |
|---|---|---|---|---|
| RFC 6749 authorize/token core | `/v1/oauth2/authorize`, `/v1/oauth2/token` | `src/exonware/xwauth/handlers/mixins/auth_core.py` + `core/grants/authorization_code.py` | `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py`, `test_oauth_oidc_negative_conformance.py` | In progress |
| RFC 6750 bearer semantics | Token-protected routes (`userinfo`, `/users/me`) | `src/exonware/xwauth/handlers/mixins/users.py` | `xwauth/tests/2.integration/test_oauth_flow.py` | In progress |
| RFC 7009 revocation | `/v1/oauth2/revoke` | `src/exonware/xwauth/handlers/mixins/auth_core.py` | `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py`, `test_oauth_oidc_negative_conformance.py` (client auth negatives) | In progress |
| RFC 7662 introspection | `/v1/oauth2/introspect` | `src/exonware/xwauth/handlers/mixins/auth_core.py` | `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py`, `test_oauth_oidc_negative_conformance.py` (missing token) | In progress |
| RFC 8414 discovery metadata | `/.well-known/oauth-authorization-server` | `src/exonware/xwauth/oauth_http/discovery.py` + `xwauth-api/src/exonware/xwauth_api/server.py` | `xwauth/tests/1.unit/oauth_http_tests/test_discovery_metadata_contract.py`, `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py` (`test_discovery_issuer_and_jwks_uri_parity_across_metadata`) | In progress |
| OAuth client auth interop | token/introspect/revoke/PAR auth transport (Basic vs form) | `src/exonware/xwauth/handlers/_common.py` (`require_client_auth`) | `xwauth-api/tests/2.integration/test_oauth_interop_matrix.py` (`test_token_client_credentials_client_auth_interop`, introspect/revoke/PAR matrix) | In progress |
| OIDC discovery + userinfo | `/.well-known/openid-configuration`, `/v1/oidc/userinfo` | `src/exonware/xwauth/oauth_http/discovery.py` + `src/exonware/xwauth/handlers/mixins/oidc.py` | `xwauth/tests/1.unit/oauth_http_tests/test_discovery_metadata_contract.py`, `xwauth/tests/1.unit/core_tests/test_oidc.py` | In progress |
| PKCE (RFC 7636) | `/v1/oauth2/authorize` + `/v1/oauth2/token` exchange | `core/grants/authorization_code.py`, `core/pkce.py` | `xwauth/tests/2.integration/test_oauth_flow.py`, `xwauth-api/tests/2.integration/test_oauth_oidc_negative_conformance.py` | In progress |
| SAML 2.0 assertion validation | `/v1/auth/sso/*` | `src/exonware/xwauth/core/saml.py` | `xwauth/tests/1.unit/core_tests/test_saml_manager.py` | In progress — integrator kit [GUIDE_10_SAML_ENTERPRISE_KIT.md](GUIDE_10_SAML_ENTERPRISE_KIT.md) |
| SCIM 2.0 filter + patch | `/v1/scim/v2/*` | `src/exonware/xwauth/scim/filtering.py`, `src/exonware/xwauth/scim/patch.py` | `xwauth/tests/1.unit/scim_tests/test_scim_filtering.py`, `xwauth-api/tests/2.integration/test_scim_policy_api.py` | In progress — hardening guide [GUIDE_11_SCIM_HARDENING.md](GUIDE_11_SCIM_HARDENING.md) |
| RFC 7517 JWKS publishing | `GET /v1/oauth2/jwks` | `handlers/mixins/auth_core.py` (`jwks`), `config/config.py` (`jwks_*`) | `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py` (`test_discovery_jwks_uri_path_returns_operational_jwks`, `test_jwks_rsa_keys_include_rfc7517_public_fields`, `test_jwks_dedup_prefers_active_key_when_same_kid_in_next`, lifecycle tests) | In progress |
| RFC 8628 device flow | `POST .../device_authorization`, device grant on token | `core/grants/device_code.py`, `handlers/mixins/auth_core.py` | `xwauth-api/tests/2.integration/test_oauth_oidc_negative_conformance.py`, `xwauth/tests/2.integration/test_new_features_integration.py` | In progress |

---

## Coverage Completion Rules

- Every critical endpoint must have:
  - Positive path tests,
  - Negative path tests,
  - One traceable standards clause reference.
- Discovery metadata must reflect active runtime profile flags (`A/B/C` and FAPI toggles).
- Any unresolved mismatch between endpoint behavior and standards clause must be logged in `REF_54_PROTOCOL_DEVIATION_REGISTER.md`.

---

## Related References

- `REF_01_REQ.md`
- `REF_13_ARCH.md`
- `REF_15_API.md`
- `REF_54_PROTOCOL_DEVIATION_REGISTER.md`
- `REF_55_PROTOCOL_PROFILE_SCHEMA_NOTES.md`
