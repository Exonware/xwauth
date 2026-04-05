# MFA and WebAuthn threat model (reference)

This document summarizes threats, data classification, and security profiles for TOTP and passkeys in xwauth. It aligns with the MFA/WebAuthn hardening plan and common IdP practice (origin binding, discoverable credentials, audit trails).

## Data classification

| Asset | Sensitivity | At-rest expectation |
|--------|-------------|---------------------|
| TOTP seed | High | Envelope-encrypted (`mfa_totp_secret_enc`); optional dedicated `mfa_at_rest_key_b64` |
| WebAuthn private keys | N/A (client-only) | Server stores public key + credential metadata only |
| WebAuthn challenges | High (ephemeral) | TTL + `webauthn_challenge_handle`; challenge removed only after **successful** crypto verify (failed verify can retry within TTL). Optional **Redis** backend (`webauthn_challenge_backend=redis`) for HA. |
| Backup codes | High | Only SHA-256 digests stored; plaintext shown once at enrollment (profiles B/C) |
| Credential id → user map | Medium | In-process index on `XWAuth` plus lazy rebuild from `list_users` on miss; optional **Redis** secondary index (`webauthn_credential_index_backend=redis`, same URL as challenges) for multi-worker discoverable login; run `rebuild_webauthn_credential_index` or enable **`XWAUTH_WEBAUTHN_REBUILD_CRED_INDEX`** on API startup after bulk import |

## Threats and mitigations

- **Account takeover (password + no MFA):** Policy engine hooks (`mfa_policy`) and step-up (`aal` / `amr` on tokens) reduce impact; enforce MFA per tenant in consuming apps.
- **Phishing / replay (WebAuthn):** Explicit `rp_id` (normalized lowercase) and origin allowlist; `require_user_verification` passed through to py_webauthn when policy is `required`; optional `Origin` header check on verify endpoints.
- **Passkey sync / enterprise policy:** `webauthn_allow_passkey_sync=False` rejects credentials with `credential_backed_up` at registration (iCloud/Google Password Manager sync).
- **TOTP secret disclosure:** Encrypted attributes; legacy plaintext `mfa_totp_secret` is removed on new setup; decrypt uses xwsystem at-rest envelope format.
- **Brute-force TOTP:** `mfa_totp_max_failed_attempts` and `mfa_totp_lockout_seconds` on verify; optional `mfa_failure_delay_ms` on failed verify.
- **Credential cloning (passkeys):** Sign counter regression triggers `webauthn_clone_detected`.
- **User enumeration (passkey login):** With `webauthn_anti_enumeration_login=True`, login verify returns a generic OAuth `access_denied` for common failure codes; **audit** events still record `error_code` for operators.
- **Enterprise attestation:** Optional `webauthn_trusted_attestation_ca_pem` supplies PEM CA material to py_webauthn `pem_root_certs_bytes_by_fmt` for non-`none` attestation formats (operator CA bundle, not automatic FIDO MDS fetch).

## Discoverable / conditional UI (passkeys)

- **`webauthn_resident_key`:** Maps to WebAuthn `residentKey` (`discouraged` | `preferred` | `required`). `preferred`/`required` align with consumer passkey and “usernameless-friendly” enrollment (competitor defaults).
- **`webauthn_discoverable_login`:** When true, **login/verify** may omit `user_id` if `authentication_response.id` resolves to a user via the credential index (or a one-time `list_users` scan on cold cache). Use **conditional mediation** on the client (`mediation: conditional`) together with login options issued **without** `user_id` / `allowCredentials` for the autofill UX.
- **Challenge binding:** Authentication challenges record optional `user_id`. If options were created for a known user (e.g. after email lookup), verify must use that same user; discoverable options use `user_id=None` so resolution from the assertion is consistent with the stored challenge.

## Audit events (security monitoring)

Structured events (see `AuditLogManager.EVENT_TYPES`) include:

| Event | When |
|-------|------|
| `mfa.totp.setup.completed` | TOTP enrollment started (pending verify) |
| `mfa.totp.verify.completed` / `.failed` | Successful or failed TOTP/backup verify |
| `webauthn.register.completed` / `.failed` | Passkey registration outcome |
| `webauthn.login.completed` / `.failed` | Passkey authentication outcome |

Success attributes use **credential id preview** only, not full credential ids.

## Security profiles (config)

- **A:** TOTP envelope encryption, WebAuthn with default attestation `none`, backup codes optional.
- **B:** Attestation `indirect`, backup codes required on first successful TOTP verify, stricter ceremony defaults recommended in deployment.
- **C:** Attestation `direct`; combine with authenticator allowlists and hardware policies in operator runbooks.

## Operator notes

- Set `webauthn_rp_id` and `webauthn_allowed_origins` (or `app.state` via `register_auth_routes_from_services`) in production. Use `webauthn_allow_insecure_defaults` only for local development.
- Prefer `mfa_at_rest_key_b64` (32-byte key, base64) over jwt-derived keys for multi-tenant production.
- Scale-out: set `webauthn_challenge_backend=redis` and `webauthn_redis_url`; tune `webauthn_redis_key_prefix` for multi-tenant key isolation if needed.
- Large user bases: plan a **durable** credential-id index (table or cache) if `list_users` scans become costly; the built-in index is updated on registration and warmed on first resolution miss. After bulk import or cold workers, call `rebuild_webauthn_credential_index(auth)` (exported from `exonware.xwauth`) to repopulate the in-process map from storage.
- Set `webauthn_anti_enumeration_login=False` only in controlled debugging environments if you need distinct error codes in API responses.
