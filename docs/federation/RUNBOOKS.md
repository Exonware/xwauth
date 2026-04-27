# Federation operator runbooks

## IdP signing certificate rollover (SAML)

1. Fetch new IdP metadata and compute SHA-256 fingerprints (`SamlMetadataTrustSnapshot` via `SAMLManager.parse_idp_metadata_xml`).
2. Add **new** pins or PEM entries alongside old ones in configuration (`saml_idp_certificate_pins_sha256` / `saml_idp_signing_certificates_pem`).
3. Deploy; confirm logins succeed against IdPs that already use the new cert.
4. Remove retired pins/PEMs after the IdP confirms the old key is unused.

## IdP outage or mass login failure

1. Check upstream HTTP/latency and error rates; classify using `FederationUpstreamCode` (for example `upstream_timeout`, `upstream_rate_limited`).
2. Enable maintenance page or fallback auth path per tenant policy.
3. If SAML signatures fail after config change, verify PEM/pin sets match current metadata (no typos, no expired metadata `validUntil` ignored in runtime).
4. Capture a **mapping trace** (`FederatedIdentity.mapping_trace`, DSL v1 under `dsl_v1`) for support tickets; avoid logging raw assertions or passwords.

## Clock skew incidents

1. NTP drift on app servers causes `NotOnOrAfter` / `NotBefore` failures. Increase `saml_clock_skew_seconds` temporarily only after confirming skew is the root cause.
2. Fix time sync; restore strict skew.

## LDAP bind storms

1. Confirm `use_ssl=True` and reasonable timeouts; rate-limit login endpoints.
2. For AD, verify `user_dn_template` / `search_filter_template` match the deployment.
