# REF_33 — Abuse resistance

**Purpose:** REF_25 #13 — slow **credential stuffing**, OTP spam, and client-registration abuse.  
**Checklist:** `exonware.xwauth.connector.ops.abuse_resistance.abuse_resistance_checklist()`  
**Helper:** `exonware.xwauth.connector.ops.abuse_resistance.exponential_backoff_delay_ms`  
**Tests:** `tests/1.unit/ops_tests/test_abuse_resistance.py`

---

## Integration

- **Handlers:** xwauth mixins already declare ``rate_limit`` strings; enforce them in **xwaction** / **xwauth-connector-api** engines and at the **edge**.
- **Backoff:** use ``exponential_backoff_delay_ms`` after failed password or OTP verify (sleep/async sleep in the transport layer, not in hot library paths).

---

## Related

- Magic-link rate limits: [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md)  
- Ops telemetry: `xwauth-connector-api` route families and anomaly endpoints

---

*Last updated: 2026-04-03*
