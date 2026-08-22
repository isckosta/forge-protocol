---
forge:
  artifact: intent
  schema: 1
change: CHG-0025
status: complete
---

# Intent — Plan Approval Semantics

## Summary

Define and implement an unambiguous authority boundary between Plan
completion and Implementation for Forge Changes. A Plan must not appear to
be human-approved merely because an agent wrote `status: approved`.

## Problem

The Standard and Full Flows require `plan_complete` before Implementation,
but the repository has no canonical evidence describing who or what made
that assertion. The existing Contract already rejects autonomous resolution
of a human-authority Decision (C-055), while the analogous Plan boundary is
silent. This permits an agent to write an apparently approved Plan and
continue without a distinguishable human act.

## Desired Outcome

Forge's canonical lifecycle vocabulary distinguishes technical Plan
completion from authorization to cross the Plan/Implementation boundary, and
the resulting rule is represented consistently in the applicable Contract,
Flow guidance, validation or execution evidence, and Change artifacts.

## Scope

- Resolve whether the rule is a canonical Contract/Gate requirement or an
  honest naming and guidance correction.
- Investigate the corresponding meaning of `specification_gate_passed`.
- If a Contract or Gate-semantics change is selected, follow the repository's
  RFC process before the material change.
- Add the smallest repository-native mechanism that makes the selected
  semantics reviewable and testable when behavior is executable.

## Out of Scope

- Changes to the scaffolding command, `app.py`, `adapter_cli.py`, or Doctor.
- Changes to examples or unrelated roadmap items.
- A provider-specific approval mechanism or a new hosted service.

## Success Criteria

1. The selected Plan boundary semantics are stated with explicit authority
   and evidence requirements.
2. The analogous `specification_gate_passed` question is explicitly resolved
   rather than silently omitted.
3. Existing valid Change records remain compatible or receive an explicit,
   justified migration boundary.
4. Independent review can determine whether an agent self-approval is being
   mistaken for human authorization.
