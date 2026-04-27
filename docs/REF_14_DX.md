# Developer Experience Reference â€” xwauth (XWOAuth) (REF_14_DX)

**Library:** exonware-xwauth-connector  
**Last Updated:** 08-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md) sec. 5â€“6, sec. 8  
**Producing guide:** [GUIDE_14_DX.md](../../docs/guides/GUIDE_14_DX.md)

---

## Purpose

DX contract for xwauth (XWOAuth): **extremely short and seamless** code for authentication and authorization; **really small** surface, **really powerful**, **highest efficiency**. Filled from REF_01_REQ. Developer experience is a **top priority** â€” developers authenticate or use the code in the smallest, most efficient way.

---

## Key code (1â€“3 lines)

| Task | Code |
|------|------|
| Configure and get facade | `from exonware.xwauth.connector import XWAuth, XWAuthConfig`; `auth = XWAuth(config=XWAuthConfig(jwt_secret="secret"))` |
| Handle authorization | `auth.authorize(request)` |
| Handle token | `auth.token(request)` |
| Introspect token | `auth.introspect_token(token)` |
| Revoke token | `auth.revoke_token(token)` |
| Email/password sign-in | `EmailPasswordAuthenticator(auth).authenticate({"email": "...", "password": "..."})` |
| Magic link sign-in | `MagicLinkAuthenticator(auth).generate_magic_link(email=..., base_url=...)` then `authenticate({"token": ...})` |
| Use a provider (e.g. Google) | Configure provider; use authorize flow â€” minimal code for sign-in. |

---

## Developer persona (from REF_01_REQ sec. 5)

Developer who needs **auth with minimal code**: **extremely short and seamless** â€” authenticate or use the code in the smallest, most efficient way; small surface, high power, highest efficiency. Primary users: eXonware developers and apps; xwstorage.connect, xwbase, future APIs; developers integrating with legacy or external systems.

---

## Easy vs advanced

| Easy (1â€“3 lines) | Advanced |
|------------------|----------|
| `XWAuth(config)`; `authorize(request)`; `token(request)`; `introspect_token`; `revoke_token`; authenticators (EmailPassword, MagicLink, PhoneOTP); add/use a connector from registry. | Custom grant types; ReBAC/FGA; PAR; DCR; token exchange; per-RFC options (DPoP, mTLS, FAPI 2.0 JAR); device authorization flow; SAML/OAuth1 endpoints. |

---

## Main entry points (from REF_01_REQ sec. 6)

- **Facade:** `XWAuth`, `XWAuthConfig` â€” main API; authorize, token, introspect_token, revoke_token; device authorization (RFC 8628).
- **Authentication:** EmailPasswordAuthenticator, MagicLinkAuthenticator, PhoneOTPAuthenticator; MFA (TOTP, SMS, Email, BackupCodes); WebAuthn/passkeys.
- **Authorization:** RBACAuthorizer, ABACAuthorizer, ReBACAuthorizer; FGA.
- **Tokens/sessions:** TokenManager, SessionManager; JWT and opaque.
- **Providers:** Registry and pluggable adapters; **â‰¥100 connectors** (current ~64).
- **Server:** APIs and UIs for the authorization system (xwauth-server).

---

## Usability expectations (from REF_01_REQ sec. 5, sec. 8)

**DX is a top priority:** extremely short, seamless flows; really small API surface; really powerful; highest efficiency. Docs and errors must support that. Clear API; REF_15_API; guides (GUIDE_01_USAGE, _archive/guides); deployment (_archive/deployment).

---

## User journeys (from REF_01_REQ sec. 5)

1. **Integrate auth in minimal code:** Developer adds xwauth and gets sign-in in 1â€“3 lines.
2. **Add a new connector:** Configure or plug a provider; system supports 100+ connectors.
3. **Replace Firebase Auth:** Migrate app to xwauth with parity and more.
4. **Connect legacy systems:** Use xwauth as extending auth provider for pre-existing systems.
5. **Use across Exonware:** xwstorage.connect, xwbase, future APIs use xwauth as the single auth system.

---

*See [REF_01_REQ.md](REF_01_REQ.md), [REF_15_API.md](REF_15_API.md), and [REF_22_PROJECT.md](REF_22_PROJECT.md). Per GUIDE_14_DX.*


