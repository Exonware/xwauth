# REF_28 — Email & magic-link operational playbook

**Purpose:** Reduce production incidents from **undelivered or abused** magic-link / email-OTP flows (REF_25 #16).  
**Machine-readable checklist:** `exonware.xwauth.connector.ops.email_magic_link_ops.magic_link_email_ops_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_email_magic_link_ops.py`

---

## Quick integration

```python
from exonware.xwauth.connector.ops import magic_link_email_ops_checklist, recommended_magic_link_ttl_seconds_bounds

print(recommended_magic_link_ttl_seconds_bounds())  # (60, 86400) guidance
doc = magic_link_email_ops_checklist()  # JSON-serializable dict for portals / CI
```

---

## DNS: SPF, DKIM, DMARC

- **SPF:** List only senders you control. A common failure mode is ``+all`` or stale includes after changing ESP.
- **DKIM:** Rotate keys on a schedule; keep private keys out of app repos (secret manager).
- **DMARC:** Collect aggregate reports before tightening policy; align DKIM/SPF with the **From** domain users see.
- **Subdomain:** Sending `auth.yourdomain.com` can isolate reputation from marketing mail.

---

## Infrastructure

- Prefer ESP **webhooks** for bounces/complaints over guessing from SMTP codes alone.
- **PTR / EHLO** alignment matters for dedicated IP sends.
- **Suppression lists:** hard-bounce immediately; cap soft-bounce retries.

---

## Magic-link–specific security

- **Short TTL** reduces window for token theft; balance with slow mail providers.
- **Single-use** tokens (or explicit invalidation after success).
- **HTTPS only**; validate redirect allowlists.
- **Never log** full URLs containing secrets.
- **Rate limits** on “send link” and “verify” to slow credential stuffing and harassment.

---

## Content and phishing resistance

- Explain *why* the email was sent (sign-in request, invite, etc.).
- Multipart **text + HTML**; avoid tracking pixels as the only proof of open.
- Localize and keep templates accessible (WCAG aligns with REF_25 #10).

---

## Related

- Integrator security checklist: [REF_26_INTEGRATOR_SECURITY_CHECKLIST.md](REF_26_INTEGRATOR_SECURITY_CHECKLIST.md)
- xwauth magic-link handlers are wired via **xwlogin** (`exonware.xwauth.identity.handlers.mixins.magic_link`); this REF is **transport-agnostic** ops guidance.

---

*Last updated: 2026-04-03*
