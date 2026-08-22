---
forge:
  artifact: intent
  schema: 1
change: CHG-0024
status: complete
---

# Intent — Adapter Readiness Doctor Check

## Summary

Make `forge doctor` signal when an initialized Forge workspace has no
installed Harness Adapter.

## Problem

`_adapter_readiness_checks()` currently skips every packaged Adapter that has
no installation record. When none is installed, the function returns no
Adapter checks, so a healthy-looking diagnostic gives no onboarding signal.

## Desired Outcome

An initialized workspace with zero Adapter installation records emits one
non-blocking warning that names the missing installation state and suggests
`forge adapter install`.

## Scope

- Add the warning only to the zero-installed-Adapter branch.
- Preserve the existing diagnostics when one or more Adapters are installed.
- Add a regression test for the zero-Adapters case.

## Out of Scope

- Changes to `forge init`; `forge doctor` is the existing read-only diagnostic
  boundary and is sufficient for this item.
- Changes to installed-Adapter diagnostics.
- Changes to the Contract, Schemas, adapter CLI commands, or other roadmap
  remediation items.

## Success Criteria

- Initialized, zero-Adapter workspaces produce exactly one Adapter-readiness
  warning with an actionable `forge adapter install` suggestion.
- Installed-Adapter behavior remains covered and unchanged.
- The focused regression test is RED before the production edit and GREEN
  after it; Verification and independent Strict Review pass.
