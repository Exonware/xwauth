# GUIDE_12 — Federation interop lab (recorded contracts + CI layers)

**Audience:** Engineers validating **federation** (OIDC upstream, SAML SP, SCIM SP) against **enterprise IdPs** without relying only on live clicks.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#8**.  
**Target matrix:** [docs/federation/INTEROP_MATRIX.md](federation/INTEROP_MATRIX.md) · **IdP quirks:** [REF_27_IDP_OIDC_QUIRKS.md](REF_27_IDP_OIDC_QUIRKS.md).

---

## 1. Three layers (use all three)

| Layer | What it proves | Where |
|-------|----------------|--------|
| **A. In-repo protocol suites** | AS/OIDC/SCIM behavior against **TestClient** + matrix tests | `xwauth-api` `protocol-conformance.yml`, `test_oauth_interop_matrix.py`, `test_oauth_endpoint_matrix.py` |
| **B. Library smoke** | Federation + SAML **unit** coverage without live IdPs | `xwauth` `.github/workflows/federation-interop-smoke.yml` |
| **C. Recorded contracts** | **Redacted** request/response artifacts from real IdPs, replayed in tests or mocks | `tests/fixtures/interop_lab/` + manifest (below) |

Layer **C** is what this guide grows over time; **A/B** should stay green on every PR.

---

## 2. Recorded contract manifest

- **Path:** `tests/fixtures/interop_lab/manifest.json`  
- **Schema:** top-level `schema_version` (`"1.0"`) and `contracts` (array).  
- Each contract entry (when present) should include at least: **`id`**, **`protocol`** (`oidc` \| `saml` \| `scim`), **`idp`** (short slug), **`artifact`** (path relative to `interop_lab/`), optional **`notes`**.

**Redaction rules before commit:**

- Remove **access_token**, **refresh_token**, **id_token**, **client_secret**, **passwords**, **private keys**, and **PII**; replace with placeholders like `"REDACTED"` or truncate JWT segments.  
- Keep **HTTP status**, **Content-Type**, **JSON shape**, and **claim names** that matter for parsing.  
- Record **IdP version** / tenant type in `notes` when known.

**CI:** `tests/1.unit/interop_lab_tests/test_interop_fixture_manifest.py` validates the manifest and that every listed **`artifact`** file exists.

---

## 3. Adding a new contract (checklist)

1. Capture traffic in a staging tenant (proxy, HAR, or scripted curl) during one successful flow.  
2. Redact per §2; save under `tests/fixtures/interop_lab/<your-dir>/...`.  
3. Append an entry to **`manifest.json`**.  
4. Add or extend a **unit/integration** test that loads the file and asserts parsers / validators behave (avoid asserting on redacted token *values*).  
5. Link the contract **`id`** from [INTEROP_MATRIX.md](federation/INTEROP_MATRIX.md) row notes when it maps to a named row (O-1, S-1, …).

---

## 4. Live IdP runs (optional CI)

- **Secrets:** Never store client secrets in fixtures; use **GitHub Actions secrets** + scheduled workflow against a **dedicated test app registration**.  
- **Flake:** Gate live jobs on **manual** or **nightly** schedule, not on every PR, unless you own a stable test tenant SLA.  
- **SCIM / SAML:** Align with [GUIDE_11_SCIM_HARDENING.md](GUIDE_11_SCIM_HARDENING.md) and [GUIDE_10_SAML_ENTERPRISE_KIT.md](GUIDE_10_SAML_ENTERPRISE_KIT.md).

---

## 5. Related

- Disclosure / fuzzing scope: [REF_29_INTEROP_BOUNTY_AND_FUZZING.md](REF_29_INTEROP_BOUNTY_AND_FUZZING.md)  
- Protocol traceability: [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](REF_53_PROTOCOL_TRACEABILITY_MATRIX.md)

---

## Expand next

- **Done:** redacted **OIDC** token body, **SCIM** `ListResponse`, and **SAML 2.0 IdP metadata** skeleton (`samples/*.redacted.*`) + shape tests in `interop_lab_tests/`.  
- **Next:** HTTP **replay** / mocks (e.g. `respx`) using JSON bodies; optional **nightly** live IdP workflow (secret-gated).
