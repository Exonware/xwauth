# REF_39 — Edition packaging & install SKUs

**Purpose:** Clarify **how to install** the right slice of the XW auth stack for **library**, **self-hosted AS**, and **enterprise** scenarios.  
**Roadmap:** [.references/ROADMAP_SCORE_20.md](../.references/ROADMAP_SCORE_20.md) item **#2**.

---

## SKUs (conceptual)

| SKU | Who | Install | Notes |
|-----|-----|---------|--------|
| **Library** | App embeds OAuth/OIDC logic | `pip install exonware-xwauth` | Connector only; wire your own HTTP layer. |
| **+ Login façade** | Same + IdPs / FastAPI mixins | `pip install "exonware-xwauth[login]"` | Pulls `exonware-xwlogin[handlers]` (GUIDE_32 boundary). |
| **+ SAML** | Enterprise federation | `pip install "exonware-xwauth[saml]"` | `signxml` + `lxml`; avoid env conflict with unrelated `rpython` (see `pyproject` comment). Ops kit: [GUIDE_10_SAML_ENTERPRISE_KIT.md](GUIDE_10_SAML_ENTERPRISE_KIT.md). |
| **+ Storage** | Durable local/file-backed state | `pip install "exonware-xwauth[storage]"` | `exonware-xwstorage`. |
| **Enterprise bundle** | Typical self-hosted AS **embedding** | `pip install "exonware-xwauth[enterprise]"` | SAML + storage + login handlers (see `pyproject.toml`); add **`redis`** extra if you need Redis-backed features. SCIM ops: [GUIDE_11_SCIM_HARDENING.md](GUIDE_11_SCIM_HARDENING.md). |
| **Reference API** | Standalone AS process | `pip install exonware-xwauth-api` | Separate **PyPI** package; bundles FastAPI app + xwauth + xwlogin deps. |

`full` in `pyproject.toml` remains **all-in** including **redis**; **`enterprise`** is the same stack **without** forcing Redis.

---

## What is *not* an extra

- **exonware-xwauth-api** is **not** installed via `exonware-xwauth[api]` — use the **`exonware-xwauth-api`** distribution for the runnable server.  
- **Hosted SaaS** / **migration playbooks** (Keycloak-shaped, etc.) are roadmap **#3** / **#4**, not pip extras.

---

## Related

- Architecture diagrams: [GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md](GUIDE_04_REFERENCE_ARCHITECTURE_DIAGRAMS.md)  
- Multi-tenant: [REF_37_MULTI_TENANT_REFERENCE_STACK.md](REF_37_MULTI_TENANT_REFERENCE_STACK.md)  
- Migrations: [GUIDE_05](GUIDE_05_MIGRATION_KEYCLOAK_SHAPED.md) / [06](GUIDE_06_MIGRATION_AUTH0_SHAPED.md) / [07](GUIDE_07_MIGRATION_SUPABASE_SHAPED.md)  
- Competitive stack: [.references/COMPETITIVE_STACK.md](../.references/COMPETITIVE_STACK.md)
