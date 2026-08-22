---
forge:
  artifact: test_design
  schema: 1
change: CHG-0024
status: complete
---

# Test Design — Adapter Readiness Doctor Check

## Objective

Prove that an initialized workspace with no Adapter installation record emits
one actionable warning, while the existing installed-Adapter diagnostics stay
covered.

## Regression Case

Update `tests/unit/test_doctor_diagnostics.py`'s zero-Adapter case to assert:

- exactly one `adapter:` check is emitted;
- its status is `warning`;
- its message identifies that no Adapter is installed and suggests
  `forge adapter install`.

The test must run against the current implementation before the production
edit and fail for the expected reason: the current implementation emits zero
Adapter checks.

## Existing-Path Guard

Keep the installed-Codex readiness tests unchanged. They verify that the
existing Adapter-specific path remains active and preserves warning statuses.

## Completion Criteria

The focused regression test reaches GREEN after the minimum production change;
the doctor test module and full applicable test suite pass, with any
environment-only distribution limitation recorded in Verification.
