# GUIDE_09 — OIDC thin-client patterns (minimal code, production disclaimer)

**Audience:** Integrators who need **authorize URL + PKCE + token exchange** without pulling a heavy SDK first.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#16**.  
**Important:** For production, prefer **maintained libraries** (e.g. Authlib, MSAL, `openid-client`, `oidc-client-ts`) — they handle edge cases (clock skew, metadata refresh, form encoding). This guide shows the **mechanical steps** only.

---

## 1. Common parameters

| Name | Typical source |
|------|----------------|
| `issuer` | AS issuer URL (ends without slash) |
| `client_id` | Your public client id |
| `redirect_uri` | One entry from `redirect_uris` |
| `scope` | e.g. `openid profile email` |
| `code_verifier` | 43–128 char high-entropy string |
| `code_challenge` | Base64url(SHA256(code_verifier)), no padding |

Discovery: `GET {issuer}/.well-known/openid-configuration` → read `authorization_endpoint`, `token_endpoint`.

---

## 2. Python (stdlib + httpx-style outline)

```python
import base64
import hashlib
import secrets
import urllib.parse

def pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge

def authorize_url(issuer_auth: str, client_id: str, redirect_uri: str, scope: str, challenge: str, state: str) -> str:
    q = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{issuer_auth}?{q}"

# POST application/x-www-form-urlencoded to token_endpoint with:
# grant_type=authorization_code, code, redirect_uri, client_id, code_verifier
```

Use **`httpx.post(..., data={...})`** for the token request; parse JSON for `access_token`, `id_token`, `refresh_token`.

---

## 3. TypeScript (browser / Node)

```typescript
async function sha256base64url(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest("SHA-256", data);
  const b64 = btoa(String.fromCharCode(...new Uint8Array(hash)));
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function randomVerifier(): string {
  const a = new Uint8Array(32);
  crypto.getRandomValues(a);
  return btoa(String.fromCharCode(...a)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
```

Build the authorize URL with `URLSearchParams`, then `fetch(tokenEndpoint, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({...}) })`.

---

## 4. Security notes

- **Never** put `client_secret` in SPA or mobile — use **public client + PKCE**.  
- Validate **`state`** and **`nonce`** (if using implicit/hybrid patterns; prefer code + PKCE).  
- Pin **issuer** and validate JWT **`iss`**, **`aud`**, **`exp`** on the resource server.

---

## 5. Refresh tokens (grant + rotation)

After the authorization-code exchange, the token response may include **`refresh_token`**. Use it to obtain a new **access** token without another browser redirect.

### 5.1 Token endpoint request (outline)

`POST` `token_endpoint` with `Content-Type: application/x-www-form-urlencoded`:

| Field | Value |
|-------|--------|
| `grant_type` | `refresh_token` |
| `refresh_token` | Current refresh token string |
| `client_id` | Same client as original code exchange |
| `scope` | Optional; if omitted, AS typically returns the same scope as before (policy-specific) |

**Confidential clients:** send `client_secret` in the body or use **HTTP Basic** on the token request, matching how your AS registered the client (same rules as the code exchange).

**Python (httpx):**

```python
# resp = httpx.post(token_url, data={
#     "grant_type": "refresh_token",
#     "refresh_token": stored_refresh,
#     "client_id": client_id,
# })
# data = resp.json()
# access = data["access_token"]
# new_refresh = data.get("refresh_token")  # present if AS rotates refresh tokens
```

### 5.2 Rotation and storage boundaries

- **Rotation:** If the response includes a **new** `refresh_token`, treat it as the only valid refresh credential — **discard the old one atomically** (single commit to your secret store). If you keep the old token after rotation, the next refresh may fail with `invalid_grant` depending on AS policy.  
- **Reuse detection:** On `400` / `invalid_grant` for refresh, clear local session state and send the user through **authorize + PKCE** again (do not retry the same refresh token indefinitely).  
- **Where to store (product choice):**  
  - **Server-side BFF:** refresh token stays on the server (HTTP-only session or vault); browser holds only a session id.  
  - **Native apps:** OS secure storage (Keychain / Keystore).  
  - **SPAs without BFF:** storing refresh tokens in the browser is **high XSS risk**; prefer **BFF**, short-lived access-only in memory, or AS-specific patterns (e.g. cookie-based refresh behind `HttpOnly` on same-site) — align with your threat model and [INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md).

### 5.3 Standards and conformance mapping

Server-side behavior (lifetimes, rotation, revocation) is product-specific; trace AS endpoints to RFCs via [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](REF_53_PROTOCOL_TRACEABILITY_MATRIX.md) and run integration tests in CI where applicable (`xwauth-api` protocol workflows).

---

## Expand next

- Dedicated **npm** / **PyPI** thin packages under Exonware org (if product decides to ship).
