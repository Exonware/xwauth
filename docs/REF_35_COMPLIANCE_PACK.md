# REF_35 — Compliance pack (regulated buyers)

**Purpose:** REF_25 #11 — accelerate **DPA**, **ROPA**, and **subprocessor** conversations for deployments using xwauth / xwauth-api.  
**API:** `exonware.xwauth.ops.compliance_pack` — `compliance_pack_checklist()`, `compliance_evidence_template()`  
**Tests:** `tests/1.unit/ops_tests/test_compliance_pack.py`

---

## Not legal advice

Templates and checklists are **technical prompts** for your counsel and DPO. They do not satisfy any statute by themselves.

---

## How to use

1. Walk `compliance_pack_checklist()` with security and privacy owners; tick items in your GRC tool.  
2. Copy `compliance_evidence_template()` fields into your customer portal or PDF packet; fill **controller/processor** names, regions, and links.  
3. Cross-link **data residency** ([REF_31_DATA_RESIDENCY.md](REF_31_DATA_RESIDENCY.md)) and **security** ([SECURITY.md](../SECURITY.md), [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md)).

---

## Hosted tier note

If you operate a **managed** auth service, subprocessors and SCCs become **first-class**; self-hosters inherit customer-controlled infrastructure.

---

*Last updated: 2026-04-03*
