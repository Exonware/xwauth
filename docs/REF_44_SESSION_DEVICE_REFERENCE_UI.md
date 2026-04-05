# REF_44 — Session and device management (reference UI)

**Purpose:** REF_25 #14 — end-user **“my sessions” / “my devices”** in the reference stack (`xwlogin` + `xwauth-api`).  
**Checklist API:** `exonware.xwauth.ops.session_device_reference_ui.session_device_reference_ui_checklist()`  
**Tests:** `tests/1.unit/ops_tests/test_session_device_reference_ui.py`

---

## Scope

- Defines UX, API, and privacy expectations; **HTML templates** for an account area still belong in `xwlogin` (or your app).
- Accessibility themes cross-reference [REF_36_LOGIN_UI_ACCESSIBILITY.md](REF_36_LOGIN_UI_ACCESSIBILITY.md).

## Reference HTTP API (xwauth)

Bearer-authenticated **session management** mixins live in the library (wire via your FastAPI app / xwauth-api):

| Method | Path | OpenAPI `operationId` |
|--------|------|------------------------|
| `GET` | `/auth/sessions` | `auth_sessions_list` |
| `GET` | `/auth/sessions/view` | `auth_sessions_list_html` (HTML table; Bearer **or** documented cookie `xwauth_reference_access_token` for same-origin browser use) |
| `DELETE` | `/auth/sessions/{session_id}` | `auth_sessions_revoke` |
| `DELETE` | `/auth/sessions/exclude-current` | `auth_sessions_revoke_others` |

Source: `src/exonware/xwauth/handlers/mixins/sessions.py`.

## Integration tests (xwauth-api)

Bearer-authenticated list/revoke behavior is covered in `xwauth-api/tests/2.integration/test_api_services.py` (`TestAuthSessionsWithBearer`; uses password grant enabled only in that fixture for test isolation).

---

*Last updated: 2026-04-03*
