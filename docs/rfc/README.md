# RFCs and public design process

**Roadmap:** [.references/ROADMAP_SCORE_20.md](../../.references/ROADMAP_SCORE_20.md) item **#18**.

## Where decisions live today

- **Product / scorecard backlog:** [ROADMAP_SCORE_20.md](../../.references/ROADMAP_SCORE_20.md) and [REF_25_COMPETITIVE_ADVANCE_BACKLOG.md](../REF_25_COMPETITIVE_ADVANCE_BACKLOG.md).  
- **Protocol truth:** [REF_53_PROTOCOL_TRACEABILITY_MATRIX.md](../REF_53_PROTOCOL_TRACEABILITY_MATRIX.md), [REF_54_PROTOCOL_DEVIATION_REGISTER.md](../REF_54_PROTOCOL_DEVIATION_REGISTER.md).  
- **Security:** [SECURITY.md](../SECURITY.md), [SECURITY_ADVISORIES.md](../SECURITY_ADVISORIES.md).

## Proposing a change

1. Open a **GitHub Discussion** or **issue** with problem statement, constraints, and alternatives.  
2. For substantial auth-protocol or breaking API behavior, add a short markdown file under **`docs/rfc/`** using name **`YYYY-MM-short-title.md`** (or PR adding the same).  
3. Link the RFC from the roadmap or deviation register when it affects conformance.

## Releases & CHANGELOG

- Prefer a **CHANGELOG** or GitHub **Releases** notes per package (`exonware-xwauth`, `exonware-xwlogin`, `exonware-xwauth-api`) so security rows in [SECURITY_ADVISORIES.md](../SECURITY_ADVISORIES.md) can link to “what changed.”

This folder may start empty except for this README; that is intentional.
