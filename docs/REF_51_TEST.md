<!-- docs/REF_51_TEST.md (output of GUIDE_51_TEST) -->
# xwauth — Test Status and Coverage

**Last Updated:** 03-Apr-2026

Test status and coverage (output of GUIDE_51_TEST).

---

## Test layers

xwauth uses 4-layer tests per GUIDE_51_TEST:

| Layer | Path | Purpose |
|-------|------|---------|
| **0.core** | `tests/0.core/` | Fast, high-value: installation, OAuth2 flow, device code, session ID; **import sanity and REF_14 key code** (test_import.py). |
| **1.unit** | `tests/1.unit/` | Unit tests: authentication, authorization, core, config, tokens, sessions, providers, security, **bench** (`bench_tests/test_microbench.py` — REF_25 #6), **ops** (`ops_tests/test_email_magic_link_ops.py` — REF_25 #16; `test_research_program.py` — REF_25 #20; `test_airgap_deployment.py` — REF_25 #17; `test_data_residency.py` — REF_25 #12; `test_multi_region_auth.py` — REF_25 #18; `test_abuse_resistance.py` — REF_25 #13; `test_b2b_delegated_admin.py` — REF_25 #15; `test_compliance_pack.py` — REF_25 #11; `test_login_ui_accessibility.py` — REF_25 #10; `test_tco_evidence.py` — REF_25 #19; `test_pen_test_engagement.py` — REF_25 #1; `test_oidc_self_cert_readiness.py` — REF_25 #2; `test_infra_as_code_tenants.py` — REF_25 #3; `test_kubernetes_operator_readiness.py` — REF_25 #4; `test_admin_api_openapi_parity.py` — REF_25 #7; `test_extension_model_readiness.py` — REF_25 #8; `test_session_device_reference_ui.py` — REF_25 #14), etc. |
| **2.integration** | `tests/2.integration/` | End-to-end and cross-component tests. |
| **3.advance** | `tests/3.advance/` | Security and advance checks. |

See repo `tests/` and `docs/logs/tests/` for run evidence.

## Evidence

- **Test run reports:** [logs/tests/](logs/tests/) (when present) or _archive/tests/
- **Benchmark artifacts (REF_25 #6):** [logs/benchmarks/](logs/benchmarks/) — published JSON / load summaries when tracked
- **Coverage and summaries:** See _archive/tests/ for NEW_FEATURES_TEST_COVERAGE and TEST_* summaries.

## Protocol Rigor Suites

- OAuth/OIDC matrix and negative-path integration suites run in `xwauth-api/tests/2.integration/`:
  - `test_oauth_endpoint_matrix.py`
  - `test_oauth_oidc_negative_conformance.py`
  - `test_oauth_advanced_conformance.py`
  - `test_oauth_interop_matrix.py`
  - `test_route_registration_contract.py`
  - `test_scim_policy_api.py`
- Discovery metadata field contracts (RFC 8414 / OIDC Discovery / RFC 9728 builders): `xwauth/tests/1.unit/oauth_http_tests/test_discovery_metadata_contract.py`
- Live discovery parity (issuer / `jwks_uri` across AS + OIDC docs), JWKS envelope, `jwks_uri` path fetch parity, RSA JWK field checks, active/next dedup: `xwauth-api/tests/2.integration/test_oauth_endpoint_matrix.py`
- Token endpoint client auth interop (Basic vs POST client credentials): `xwauth-api/tests/2.integration/test_oauth_interop_matrix.py`
- Introspect missing `token`, revoke client-auth failures: `xwauth-api/tests/2.integration/test_oauth_oidc_negative_conformance.py`
- IdP OIDC quirks (Entra /common, Google aud, Okta issuer normalize): `xwauth/tests/1.unit/federation_tests/test_idp_quirk_contracts.py`
- SAML strict-validation, replay checks, invalid metadata XML: `xwauth/tests/1.unit/core_tests/test_saml_manager.py`
- SCIM filter/patch interop edge cases: `xwauth/tests/1.unit/scim_tests/test_scim_filtering.py`, `xwauth/tests/1.unit/scim_tests/test_scim_patch.py`; list Users invalid `filter` / invalid `startIndex` / negative `count` (400): `xwauth-api/tests/2.integration/test_scim_policy_api.py`
- Federation interop lab (ROADMAP #8 / [GUIDE_12](GUIDE_12_FEDERATION_INTEROP_LAB.md)): `xwauth/tests/1.unit/interop_lab_tests/test_interop_fixture_manifest.py` (manifest + OIDC/SCIM/SAML sample shapes)

## Protocol CI Gate

- Discovery metadata builders (fast, no API stack): run `pytest xwauth/tests/1.unit/oauth_http_tests/test_discovery_metadata_contract.py` locally or in your pipeline (`xwauth` repo workflows match `xwsystem`: version checks + PyPI publish on tag).
- Workflow: `xwauth-api/.github/workflows/protocol-conformance.yml`
- Signed artifact outputs:
  - `artifacts/protocol-scorecard-<profile>.json`
  - `artifacts/protocol-scorecard-<profile>.json.sha256`
  - `artifacts/protocol-interop-matrix-<profile>.json`

---

*Per GUIDE_00_MASTER and GUIDE_51_TEST.*
