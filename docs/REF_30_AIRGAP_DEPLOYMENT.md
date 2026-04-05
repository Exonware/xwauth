# REF_30 — Air-gapped / offline deployment

**Purpose:** REF_25 #17 — run **xwauth / xwlogin / xwauth-api** without outbound internet access.  
**Machine-readable checklist:** `exonware.xwauth.ops.airgap_deployment.airgap_deployment_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_airgap_deployment.py`

---

## Summary

Air-gapped installs are **supported in principle** as a **packaging and operations** exercise: you must supply wheels, trust anchors, time sync, and (if used) inline JWKS/metadata. The libraries do not phone home by design, but **federation** and **lazy install** paths assume you either allow specific internal endpoints or pre-provision data.

---

## Python artifacts

- Mirror **all** dependencies (including platform-specific wheels for `cryptography`, `lxml` if SAML is enabled) into a wheelhouse.
- Install with ``pip install --no-index --find-links=...``.

---

## Federation

- Prefer **inline JWKS** or an **internal** JWKS/metadata URL.
- Plan **manual key rotation** when IdP keys change and public discovery is unavailable.

---

## Time and TLS

- Run **reliable clocks**; OAuth/JWT and SAML are time-sensitive.
- Use a proper **private CA** trust chain for internal HTTPS/mTLS.

---

## Related

- Magic-link email in disconnected sites: [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md) (internal SMTP).
- Integrator checklist: [REF_26_INTEGRATOR_SECURITY_CHECKLIST.md](REF_26_INTEGRATOR_SECURITY_CHECKLIST.md).

---

*Last updated: 2026-04-03*
