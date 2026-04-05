# Interop lab fixtures

**Guide:** [docs/GUIDE_12_FEDERATION_INTEROP_LAB.md](../../docs/GUIDE_12_FEDERATION_INTEROP_LAB.md) (ROADMAP #8).

- **`manifest.json`** — index of recorded (redacted) contracts; validated by `tests/1.unit/interop_lab_tests/`.
- Add subfolders per IdP or flow (`entra/`, `okta/`, …) and reference them from manifest entries.

Do **not** commit secrets, raw tokens, or private keys.
