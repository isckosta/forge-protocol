---
forge:
  artifact: inspection
  schema: 1
change: CHG-0024
status: complete
---

# Inspection — Adapter Readiness Doctor Check

## Root Cause

In `src/forge_cli/doctor/__init__.py`, `diagnose()` invokes
`_adapter_readiness_checks(repository_root)` only when `.forge/` is present.
That function iterates the packaged registry and executes:

```python
if load_optional_installation_record(repository_root, adapter_id) is None:
    continue
```

With no installation records, every driver reaches `continue`, so no
`DoctorCheck` is emitted. The caller then reports the remaining project
checks without any Adapter-readiness signal.

## Existing Pattern

`_migration_advisory_checks()` already emits a single `warning` check for an
advisory condition. The new zero-Adapter signal should use the same severity
tier and remain read-only. The installed-Adapter path must continue through
`AdapterService.doctor()` exactly as it does today.

## Evidence

- `diagnose()` calls the readiness helper only for initialized workspaces.
- The current helper skips uninstalled drivers and returns an empty list when
  all drivers are skipped.
- `tests/unit/test_doctor_diagnostics.py` currently asserts that initialized
  workspaces with no Adapter checks have no `adapter:` entries; that test is
  the direct regression surface to update.
- The repository's current local `.forge/adapters/` state means the root
  checkout itself is not a zero-install fixture, so the test uses a temporary
  initialized Git repository.

## Classification

**FAST.** This is a localized validation/diagnostic bugfix in one function
with one focused test. It does not meet FAST's disqualifiers in
`protocol/flows/fast.yml`: no architecture, security or authorization model,
domain invariant, integration, broad business rule, major public contract,
or significant cross-module change is introduced.

## Documentation Impact

Required: update `ROADMAP-REMEDIATION.md` item #4 to Done and link this Change.
No Contract, README, Schema, RFC, ADR, or `forge init` documentation update is
needed for this localized diagnostic correction.
