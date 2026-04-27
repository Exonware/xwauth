# REF_33 — Partner & edge integration matrix (“works with”)

**Purpose:** High-level placement of **XW (xwauth + xwlogin + xwauth-connector-api)** behind common edge and observability components.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#19**.  
**Not** a certification matrix — validate in **your** environment.

---

## Reverse proxy / load balancer

| Product / pattern | Typical use | Notes for OAuth/OIDC AS |
|-------------------|-------------|-------------------------|
| **nginx** | TLS termination, path routing | Preserve `Host`; set `X-Forwarded-Proto https`; long timeouts on `/authorize` user flows if needed. |
| **HAProxy** | L4/L7, health checks | HTTP check on `/health`; ensure sticky sessions **only** if you use non-replicated in-memory state. |
| **Envoy / Istio** | Service mesh, mTLS | Optional mTLS to AS; align `forward_client_cert` with `XWAuth` mTLS features if enabled. |
| **Caddy** | Auto TLS | Same forwarded headers; watch **issuer** URL vs public hostname. |

---

## CDN / WAF

| Product / pattern | Typical use | Notes |
|-------------------|-------------|--------|
| **Cloudflare** (or similar CDN/WAF) | DDoS, bot, OWASP rules | **Do not** cache OAuth endpoints (`/v1/oauth2/*`, `/.well-known/*` may be cacheable briefly for discovery — prefer short TTL or bypass). Rate-limit **`/token`**, **`/authorize`**. |
| **AWS WAF / Azure Front Door** | IP / geo / managed rules | Log token endpoint abuse separately; correlate with `X-Request-Id` from xwauth-connector-api ops headers. |

---

## API gateway

| Product / pattern | Typical use | Notes |
|-------------------|-------------|--------|
| **Kong / Tyk / Apigee** | External API façade | Often sits **in front** of AS for throttling; keep **client credentials** and **PKCE** validation on the AS (do not strip parameters). |
| **Azure API Management** | Policy + OAuth | JWT validate at gateway **or** trust AS introspection — pick one pattern to avoid double-drift. |

---

## SIEM / logging

| Product / pattern | Typical use | Notes |
|-------------------|-------------|--------|
| **Splunk / Elastic / OpenSearch** | Central logs | Ship **structured** logs; **never** index access/refresh tokens or passwords. Use correlation IDs (`X-Correlation-Id`, `X-Request-Id` from xwauth-connector-api). |
| **Datadog / New Relic** | APM + logs | Enable **OTEL** hooks where documented (`XWAUTH_OPS_OTEL` in xwauth-connector-api README). |

---

## Reference-server CORS (SPAs)

Browser clients calling the AS cross-origin: use xwauth-connector-api **`XWAUTH_API_CORS_ORIGINS`** (explicit list). See [INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md).

---

## Contributing

Add a row when you have **validated** a deployment pattern; link an internal runbook or public blog. Prefer **versioned** product names when behavior differs by release.
