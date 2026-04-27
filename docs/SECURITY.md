# Security policy

## Supported versions

Security fixes are applied to the **latest minor** on the active development branch and, when an LTS line exists, to the documented LTS branch. See release notes for the exact supported range.

## Reporting a vulnerability

**Please do not** file a public GitHub issue for security vulnerabilities.

Email: **connect@exonware.com** with subject line `[SECURITY] xwauth`.

Include:

- Description of the issue and impact
- Steps to reproduce (proof-of-concept if possible)
- Affected component (`xwauth`, `xwlogin`, `xwauth-connector-api`) and version/commit if known

We aim to acknowledge receipt within **5 business days** and coordinate disclosure after a fix is available.

## Advisories

Published security notices and identifiers are tracked in **[SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md)**.

## Deploying the stack (integrators)

Production-oriented checklist (tokens, clients, TLS, storage): **[INTEGRATOR_SECURITY_CHECKLIST.md](INTEGRATOR_SECURITY_CHECKLIST.md)**.

## Interop scope & fuzzing (draft program)

Technical **in-scope / out-of-scope** lists and fuzzing target hints (machine-readable, versioned) live in **`exonware.xwauth.connector.ops.research_program`** and are documented in **[REF_29_INTEROP_BOUNTY_AND_FUZZING.md](REF_29_INTEROP_BOUNTY_AND_FUZZING.md)**.

Paid bounty tiers are **not** active while program `status` is `draft`; coordinated disclosure via the email above is still appreciated and may be credited in [SECURITY_ADVISORIES.md](SECURITY_ADVISORIES.md) when applicable.
