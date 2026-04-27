<!-- docs/REF_15_API.md (output of GUIDE_15_API) -->
# xwauth (XWOAuth) API Reference

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1.0  
**Last Updated:** 08-Feb-2026  
**Requirements source:** [REF_01_REQ.md](REF_01_REQ.md)

**DX goal:** **Extremely short and seamless** — authenticate or obtain tokens in 1–3 lines where possible. **Connectors:** Target **≥100** (current ~64); see providers module and registry.

---

## Easy (1–3 lines)

| Task | Code |
|------|------|
| Configure and get facade | `from exonware.xwauth.connector import XWAuth, XWAuthConfig`; `auth = XWAuth(config=XWAuthConfig(jwt_secret="secret"))` |
| Handle authorize/token | `auth.authorize(request)`; `auth.token(request)` |
| Introspect / revoke token | `auth.introspect_token(token)`; `auth.revoke_token(token)` |
| Use a provider (e.g. Google) | Register provider in config; use authorize flow — minimal code for sign-in. |

Advanced: custom grant types, ReBAC/FGA, PAR, DCR, token exchange, per-RFC options.

---

## Core Classes

### XWAuth

Main facade class for xwauth.

```python
from exonware.xwauth.connector import XWAuth, XWAuthConfig

auth = XWAuth(config=XWAuthConfig(jwt_secret="secret"))
```

#### Methods

- `authorize(request: dict) -> dict` - Handle authorization endpoint  
- `token(request: dict) -> dict` - Handle token endpoint  
- `introspect_token(token: str) -> dict` - Introspect token (RFC 7662)  
- `revoke_token(token: str, token_type_hint: Optional[str]) -> None` - Revoke token (RFC 7009)  

### XWAuthConfig

Configuration class for xwauth.

```python
config = XWAuthConfig(
    jwt_secret="your-secret-key",
    access_token_lifetime=3600,
    refresh_token_lifetime=604800,
    enable_pkce=True,
    enable_csrf=True,
)
```

## Authentication Methods

### EmailPasswordAuthenticator

Email/password authentication.

```python
from exonware.xwauth.identity.authentication.email_password import EmailPasswordAuthenticator

authenticator = EmailPasswordAuthenticator(auth)
user_id = await authenticator.authenticate({
    'email': 'user@example.com',
    'password': 'password'
})
```

### MagicLinkAuthenticator

Passwordless authentication via magic links.

```python
from exonware.xwauth.identity.authentication.magic_link import MagicLinkAuthenticator

authenticator = MagicLinkAuthenticator(auth)
magic_link = await authenticator.generate_magic_link(
    email="user@example.com",
    base_url="https://myapp.com"
)
user_id = await authenticator.authenticate({'token': magic_link_token})
```

### PhoneOTPAuthenticator

Phone number OTP authentication.

```python
from exonware.xwauth.identity.authentication.phone_otp import PhoneOTPAuthenticator

authenticator = PhoneOTPAuthenticator(auth)
otp_code = await authenticator.generate_otp("+1234567890")
user_id = await authenticator.authenticate({
    'phone_number': '+1234567890',
    'otp': otp_code
})
```

## MFA Methods

### TOTPMFA, SMSMFA, EmailMFA, BackupCodesMFA

See facade and authentication.mfa modules. Time-based OTP, SMS OTP, email OTP, backup codes.

## Authorization

### RBACAuthorizer, ABACAuthorizer, ReBACAuthorizer

Role-, attribute-, and relationship-based access control. See authorization module.

## Token Management

TokenManager (generate_access_token, generate_refresh_token, validate_token). SessionManager (create_session, get_session, revoke_session, list_user_sessions).

## OAuth Providers (Connectors)

**Target ≥100 connectors** (current ~64). GoogleProvider, GitHubProvider, Microsoft, Apple, and many more (social, enterprise, gaming, AI, payments, etc.). See `providers` module and provider registry. Detailed integration: _archive/guides/ (GUIDE_PROVIDER_INTEGRATION_XWAUTH).

## Error Handling

All errors inherit from `XWAuthError`: XWOAuthError, XWTokenError, XWInvalidCredentialsError, XWInvalidRequestError.

---

*Output of GUIDE_15_API. Endpoint details and deployment: see docs/_archive/api/ and docs/_archive/deployment/.*
