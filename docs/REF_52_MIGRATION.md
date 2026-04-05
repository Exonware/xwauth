# REF_52_MIGRATION - XWAuth Artifact Versioning Strategy

## Purpose

Define a migration-safe strategy for persisted auth artifacts so `xwauth` can evolve without breaking existing data in `xwstorage`-backed environments.

## Artifact Scope

- Users
- Sessions
- Tokens (access/refresh metadata)
- Authorization/device codes
- Audit logs

## Versioning Rules

- Each persisted aggregate must carry `schema_version` (integer).
- Reader paths must support `current_version` and at least one prior version.
- Writer paths must always emit `current_version`.
- Unknown future versions must fail closed with explicit errors.

## Compatibility Policy

- `N` release supports reading `N` and `N-1`.
- `N+1` may drop `N-1` only after one full release cycle and migration notice.
- Breaking field removals require a migration function and changelog entry.

## Migration Flow

1. Read blob from storage.
2. Detect `schema_version` (default to `1` when absent).
3. Apply sequential migrations up to current.
4. Continue runtime with upgraded in-memory model.
5. Persist back using current version.

## Boundary Ownership

- `xwauth` owns auth-domain schema definitions and migrations.
- `xwstorage` owns persistence mechanics only.
- `xwapi` consumes normalized contracts and must not depend on storage schema internals.

## Required Tests

- Golden fixtures for old versions deserialize into current models.
- Roundtrip tests preserve required fields and indexes.
- Contract regression tests confirm `AuthContext` compatibility across `xwauth` and `xwapi`.

