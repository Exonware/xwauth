# GUIDE_10 — SAML enterprise kit (metadata, signing, vendors)

**Audience:** Operators integrating **SAML 2.0** IdPs with the **XW** stack (`exonware-xwauth-connector` + `exonware-xwauth-identity` HTTP mixins + `xwauth-connector-api` routes).  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#6**.  
**Standards trace:** [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](REF_53_PROTOCOL_TRACEABILITY_MATRIX.md) (SAML row); core tests `xwauth/tests/1.unit/core_tests/test_saml_manager.py`.

---

## 1. Install surface

| Goal | Command / wiring |
|------|------------------|
| **SAML dependencies** | `pip install "exonware-xwauth-connector[saml]"` (`signxml`, `lxml`) — see [REF_39_EDITION_AND_SKUS.md](REF_39_EDITION_AND_SKUS.md). |
| **Full self-hosted AS embedding** | `pip install "exonware-xwauth-connector[enterprise]"` (SAML + storage + login handlers). |
| **Env hygiene** | Do not install the unrelated PyPI package **`rpython`** in the same environment (breaks `lxml` / `signxml`); see `pyproject.toml` comment and GUIDE_53. |

**HTTP surfaces (reference server):** SAML metadata, ACS, and discovery are registered under **`/v1/auth/sso/...`** via `xwauth-connector-api` `AUTH_SERVICES` (e.g. `.../sso/saml/metadata`, `.../sso/saml/acs`, `.../sso/discovery`). Route family **`saml`** for ops headers / SLIs ([REF_62](REF_62_OPS_SLI_REGISTRY_V1.md)).

---

## 2. Metadata lifecycle (IdP and SP)

| Concern | Practice |
|---------|----------|
| **IdP metadata source** | Prefer **HTTPS URL** with periodic refresh (scheduled job or startup + TTL), not a one-time download only — IdPs rotate signing certs. |
| **Validity** | Track `validUntil` / cache TTL; alert before expiry; fail closed if metadata is stale and signatures cannot be verified. |
| **Fingerprint / pinning** | Optional extra guard on top of PKIX; when IdP rotates, update pins in the same change window as metadata refresh. |
| **SP metadata you publish** | Keep **`/sso/saml/metadata`** stable URL; version **signing certificates** with overlap (two certs) before retiring the old key. |
| **Entity IDs** | Treat **`entityID`** (IdP and SP) as immutable contract with the IdP admin; changing them is a **new federation**, not a silent deploy. |

---

## 3. Signing and encryption profiles

| Topic | Guidance |
|-------|----------|
| **Assertions** | Verify **IdP signing** over assertions/responses; reject missing or weak algorithms per your **protocol profile** (A/B/C — [REF_55](REF_55_PROTOCOL_PROFILE_SCHEMA_NOTES.md)). |
| **Encryption** | If the IdP encrypts assertions, align SP private keys and metadata; rotate with the same dual-cert pattern as signing. |
| **RelayState** | Treat as **opaque**; validate length and charset; do not embed secrets. |
| **Clock skew** | `NotOnOrAfter` / `NotBefore` — allow small skew (e.g. 60–120s) at validation; log and alert on large drift (NTP on all nodes). |

---

## 4. Operational checklist

1. **ACS URL** allow-listed on IdP side matches **exact** public URL (including path, no accidental trailing slash mismatch).  
2. **Audience** / **Recipient** constraints match SP **entity ID** / ACS URL per IdP documentation.  
3. **NameID / attribute mapping** documented — map to internal `sub` / org claims consistently with OIDC paths.  
4. **Logout** — if using SAML SLO, test both SP- and IdP-initiated flows; many deployments use **OIDC logout** for apps while SAML is IdP-only (document your choice).  
5. **Audit** — emit federation events per [REF_61](REF_61_OPS_TELEMETRY_SCHEMA.md) §8 (`xwauth.federation.*`).  
6. **Secrets** — SP private keys in **Secret** store (K8s Secret, HSM, or vault); never in git. Align with [INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md).

---

## 5. Vendor notes (starter matrix)

Use this as a **starting point**; always confirm against the vendor’s current admin UI and docs.

| Vendor | Typical gotchas |
|--------|-----------------|
| **Microsoft Entra ID** | App Federation Metadata URL vs manual cert upload; token encryption optional; group claims require app-role / optional claims configuration. |
| **Okta** | Multiple cert slots for rollover; NameID format policy; SAML Attribute Statements vs OIDC for app auth (hybrid orgs). |
| **Keycloak** | Realm-specific entity IDs; client vs broker SAML settings; clock skew in dev containers. |
| **AD FS** | Claim rules (claims issuance policy); certificate rollover notifications; modern browser cookie behavior with WS-Fed vs SAML SP-initiated. |
| **Ping / ForgeRock / others** | Metadata aggregation, signing algorithm whitelist, and **NameID** persistence policies — validate in staging with **trace** logging off in prod. |

*Expand this table with versioned validation notes per vendor as you harden interop (see [REF_33](REF_33_PARTNER_INTEGRATION_MATRIX.md) / roadmap #19).*

---

## 6. Related docs

- Federation / OIDC quirks (parallel reading): [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md)  
- Partner / edge: [REF_33_PARTNER_INTEGRATION_MATRIX.md](REF_33_PARTNER_INTEGRATION_MATRIX.md)  
- HA / cutover: [GUIDE_03_HA_UPGRADE_RUNBOOK.md](GUIDE_03_HA_UPGRADE_RUNBOOK.md)

---

## Expand next

- **SP key generation** runbook (openssl / HSM) and **metadata publishing** CI check.  
- **Golden-path** Docker/Helm env vars for SAML IdP metadata URL (reference server profile).  
- Redacted **IdP metadata** sample for interop: `tests/fixtures/interop_lab/samples/saml_idp_metadata.redacted.xml` ([GUIDE_12](GUIDE_12_FEDERATION_INTEROP_LAB.md)).
