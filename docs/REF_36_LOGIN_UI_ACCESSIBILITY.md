# REF_36 — Reference login UI accessibility (WCAG 2.2 AA)

**Purpose:** REF_25 #10 — procurement-ready **accessibility** expectations for login, MFA, and error states.  
**Checklist API:** `exonware.xwauth.connector.ops.login_ui_accessibility.login_ui_accessibility_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_login_ui_accessibility.py`

---

## Scope

- Applies to **HTML templates** you ship (e.g. xwlogin forms, future `xwauth-web`), not to JSON APIs.
- This is **not** a substitute for axe/Playwright audits or a signed VPAT; it is the **engineering checklist** that feeds those artifacts.

---

## Related

- Email content accessibility: [REF_28_EMAIL_MAGIC_LINK_OPS.md](REF_28_EMAIL_MAGIC_LINK_OPS.md) (multipart / language).

---

*Last updated: 2026-04-03*
