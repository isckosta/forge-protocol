---
forge:
  artifact: intent
  schema: 1
change: CHG-0021
status: complete
---

# Intent — Adapter Reference Schema Projection

## Summary

Project the Decision structural rules (`class`, `materiality`, `status`,
`authority`, `resolved_via` enums; `class` → valid `owning_artifact`;
`class` → authority floor) that `forge validate` actually enforces —
today real only as Python constants in `src/forge_cli/validation/__init__.py`
— into both Harness Adapters' generated `references/`, and sharpen the
`resolved_via` validation error to state the expected values.

## Problem

A first real external validation of Forge (`crud-produtos`, Laravel 13,
`CHG-0001-sanctum-authentication`, conducted 2026-08-20 with only the
Claude Code Adapter installed — no checkout of this repository's Python
source) produced two `forge validate` rejections of `manifest.yml` while
finishing that Change:

1. `resolved_via: 'explicit_human_act'` — not a member of the enum
   `evidence | autonomous_decision | human_decision | null`.
2. `class: architectural` with `owning_artifact: specification` — invalid,
   because `architectural` Decisions must be owned by `architecture`,
   which the STANDARD Flow that Change used never produces.

Both rules are real and correctly enforced. Neither is discoverable from
what an agent with only the Adapter installed can read: the Claude Code
Adapter already projects `references/engineering-contract.md` (Contract
prose) and `references/artifact-structure.md` (this repository's own
`CHG-0016` guidance), but neither document states these enums or this
class→owning-Artifact mapping. They exist solely as the Python constants
`_DEC_CLASSES`, `_DEC_MATERIALITY`, `_DEC_STATUSES`, `_DEC_AUTHORITIES`,
`_DEC_RESOLVED_VIA`, `_DEC_OWNING_BY_CLASS`, and `_DEC_AUTHORITY_FLOOR`
in `src/forge_cli/validation/__init__.py`.

## Desired Outcome

An agent operating a Change with only a Harness Adapter installed — no
access to this repository's Python source — can construct a valid
`decisions[]` entry in `manifest.yml` on the first attempt, and a
`resolved_via` rejection states which values are valid instead of only
that the given value is invalid.

## Scope

- a Markdown reference documenting the Decision structural rules above,
  generated programmatically from the existing validation constants (not
  hand-duplicated as a second, driftable document);
- projection of that reference into both the Claude Code and Codex
  Adapters' generated `references/`, linked from each Adapter's skill
  entry point, mirroring the existing `artifact-structure.md` pattern
  (`CHG-0016`);
- a sharpened `resolved_via` invalid-value error message in
  `forge validate`, stating the expected values, matching the existing
  `owning_artifact` error message's convention.

## Out of Scope

- promoting `_DEC_OWNING_BY_CLASS` / `_DEC_AUTHORITY_FLOOR` into
  `protocol/schemas/change-v2.schema.json` as JSON Schema constraints —
  materially larger, Protocol-schema-level surface requiring its own RFC
  per `CONTRIBUTING.md` ("Protocol interoperability");
- `forge change new` Change scaffolding — a separate roadmap item that
  depends on this Change's output, not a prerequisite for it;
- sharpening the `class`, `materiality`, `status`, or `authority`
  invalid-value error messages — only `resolved_via` was the reported
  failure; sweeping the others is noted as a real follow-up candidate in
  Knowledge Capture, not silently absorbed into this Change's scope.

## Success Criteria

- a new public function renders the Decision structural rules from the
  live validation constants, with no enum value duplicated as a string
  literal anywhere else;
- both Adapters project the same rendered content, byte-for-byte;
- a caller that does not opt in to the new content sees unchanged
  projection output (additive-only, matching `CHG-0016`'s compatibility
  contract for `artifact_structure_content`);
- the `resolved_via` error message states the expected values;
- full test suite, `forge validate`, and `forge doctor` remain green.
