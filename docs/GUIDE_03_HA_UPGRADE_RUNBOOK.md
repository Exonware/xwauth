# GUIDE_03 — HA, backup, and upgrade runbook (auth stack)

**Audience:** Operators of **xwauth** + **xwlogin** + **xwauth-api** (reference server or embedded FastAPI).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#12**.  
**Deeper ops program:** [REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md](REF_24_OPS_PERFECT_SCORE_EXECUTION_PLAN.md), [REF_60_OPS_TIER_PROFILE_CONTRACT.md](REF_60_OPS_TIER_PROFILE_CONTRACT.md).

This is a **starter** runbook: expand with your storage backend, orchestrator, and compliance requirements.

---

## 1. What to back up

| Asset | Typical location | Notes |
|-------|------------------|--------|
| **Auth persistence** | `XWAUTH_API_STORAGE_PATH` (JSON / xwstorage-backed dir) | Codes, refresh handles, sessions — **treat as confidential**. |
| **JWT / signing material** | Secret manager / env (`XWAUTH_API_JWT_SECRET`, optional PEM for asymmetric id_tokens) | Loss = re-issuance; rotation = invalidates outstanding JWTs signed with old key (plan overlap if dual-key). |
| **OAuth client registry** | `XWAUTH_API_REGISTERED_CLIENTS_JSON` or your DB | Required to restore identical client behavior. |
| **Config** | Env, ConfigMaps, `.env` (not in git with secrets) | Version alongside app image tag. |

---

## 2. Backup / restore (minimal procedure)

1. **Quiesce** (optional): stop new logins at the edge, or accept short inconsistency window.  
2. **Snapshot** storage directory or database **after** fsync / consistent backup API.  
3. **Export** client JSON and non-secret config references.  
4. **Restore:** deploy previous **image tag** + restore storage + restore secrets + restart. Validate `/health` and discovery (`/.well-known/openid-configuration`).

### 2a. File-backed JSON storage (default xwstorage path)

When `XWAUTH_API_STORAGE_PATH` (or your app’s `base_path`) points at a **directory** of JSON files:

1. **Stop** all writer instances (single-writer recommended) or rely on crash-consistent copy only if you accept risk.  
2. **Archive** the whole directory: `tar -czf xwauth-storage-$(date -u +%Y%m%d).tgz "$XWAUTH_API_STORAGE_PATH"`.  
3. **Restore:** extract to the same path, fix **ownership/permissions** for the container user, start instances.  
4. **Validate:** token issuance + one read path (e.g. introspection) against a known test client.

For **PVC** backups in Kubernetes, snapshot the volume or use your storage class’s backup job; see **xwauth-api** [deploy/k8s/README.md](https://github.com/exonware/xwauth-api/blob/main/deploy/k8s/README.md).

---

## 3. Upgrade path

1. Read **release notes** / changelog for breaking changes (protocol profiles, config keys).  
2. Run **tests** in staging with the same `XWAUTH_PROTOCOL_PROFILE` as production.  
3. Bump **container image** or `pip install -U` with pinned versions in lockfile.  
4. **Migrate** storage only if the release documents a migration (otherwise file-backed state is usually forward-compatible within minor versions — verify).  
5. **Smoke:** authorize + token + introspect on a test client.

---

## 4. Key rotation (symmetric JWT)

- Rotating `jwt_secret` **invalidates** all access/id tokens signed with the old secret.  
- Plan **overlap** only if you introduce **asymmetric** signing (JWKS) or dual-secret validation — not the default HS256-only path.  
- Prefer **short access token TTL** + refresh rotation so users recover without full re-enrollment.

---

## 5. Rollback

1. Redeploy **previous image** and **previous config** revision.  
2. Restore **storage snapshot** taken before the failed upgrade if schema or write path changed.  
3. Confirm **issuer** URL and TLS certs unchanged to avoid client mis-cache.

---

## 6. HA notes

- Run **multiple replicas** only with **shared** storage (not local disk per pod) or stateless token strategy you have validated.  
- Put **sticky sessions** only if your deployment uses in-memory session stores without replication.  
- Terminate **TLS** at ingress; preserve `Forwarded` / `X-Forwarded-Proto` so discovery URLs stay HTTPS. See [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md).

---

## Related

- Reference server golden path: **exonware-xwauth-api** package / repo — `docs/GOLDEN_PATH_DEPLOY.md`.  
- Integrator checklist: [INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md).
