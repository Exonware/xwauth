# GUIDE_04 — Reference architecture diagrams

**Purpose:** End-to-end **placement** diagrams for common deployment shapes using the XW auth stack.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#20**.  
**Not** performance benchmarks — see [../benchmarks/README.md](../benchmarks/README.md).

---

## 1. B2B SaaS (org-bound tokens)

Organizations are represented in **token claims** or **path-scoped APIs**; the AS issues tokens with org context. Tenancy helpers live in **xwsystem** (`tenancy` module). See [REF_37_MULTI_TENANT_REFERENCE_STACK.md](REF_37_MULTI_TENANT_REFERENCE_STACK.md).

```mermaid
flowchart LR
  subgraph clients [Clients]
    SPA[Browser SPA]
    SVC[Backend services]
  end
  subgraph edge [Edge]
    GW[API Gateway / WAF]
  end
  subgraph auth [Auth plane]
    AS[xwauth-api AS]
    ST[(Tenant-scoped storage)]
  end
  subgraph app [App plane]
    API[Product APIs]
  end
  SPA --> GW
  SVC --> GW
  GW --> AS
  GW --> API
  AS --> ST
  API --> AS
```

---

## 2. SPA with BFF (recommended for browser)

The **browser** talks to a **same-origin BFF**; the BFF performs OAuth/OIDC with the AS using **server-side** client credentials or PKCE as appropriate. Reduces token exposure compared to public client-only SPAs calling the AS directly.

```mermaid
flowchart LR
  B[Browser]
  BFF[BFF API same-site]
  AS[Authorization server]
  B --> BFF
  BFF --> AS
```

---

## 3. Microservices with central AS

Multiple resource servers validate JWTs (JWKS or shared validation) and call **introspection** when tokens are opaque.

```mermaid
flowchart TB
  AS[AS xwauth-api]
  RS1[Service A]
  RS2[Service B]
  AS --> RS1
  AS --> RS2
  Client[Client] --> AS
  Client --> RS1
  Client --> RS2
```

---

## 4. Enterprise bridge (federation sketch)

Upstream **IdP** (SAML/OIDC) federates into the connector; your AS remains the **relying party** for applications. Details vary by IdP — see [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md).

```mermaid
flowchart LR
  IdP[Enterprise IdP]
  AS[XW AS]
  App[Applications]
  IdP --> AS
  AS --> App
```

---

## 5. Mobile / native public client

Native app uses **system browser** or **ASWebAuthenticationSession** / Custom Tabs; **PKCE** required for public clients (enforced in connector profiles).

```mermaid
sequenceDiagram
  participant App as Native app
  participant Browser as System browser
  participant AS as Authorization server
  App->>Browser: Open authorize URL
  Browser->>AS: User auth
  AS->>App: Redirect with code
  App->>AS: Token + PKCE verifier
```

---

## Related

- Edge integration: [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md)  
- Ops: [REF_63_AUTH_OBSERVABILITY_CONTRACT.md](REF_63_AUTH_OBSERVABILITY_CONTRACT.md)
