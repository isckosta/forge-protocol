---
forge:
  artifact: intent
  schema: 1
change: CHG-0026
status: complete
---

# Intent — Skill Propagation Diagnostics

## Summary

Make Adapter installation honest about a possible session-scoped delay before
the newly published Forge skill is discoverable through a Harness-native skill
invocation mechanism.

## Problem

`forge adapter install` currently reports that installation is complete and
that no further Forge-side step is required. The first external validation
found that Claude Code did not expose the newly installed skill through its
skill catalog in the same session that performed the install. The agent had
to discover the limitation experimentally and read the generated `SKILL.md`
directly.

## Desired Outcome

After installation, the operator sees an actionable diagnostic: the Harness
may need a later turn/session to refresh its skill catalog, and the generated
`SKILL.md` path is the immediate fallback. The same limitation is disclosed
inside the projected skill without claiming that Forge controls Harness
catalog refresh.

## Scope

- Update the install completion output with harness-accurate propagation
  guidance.
- Add the same honest runtime limitation to both Adapter workflow templates,
  which are projected into `SKILL.md`.
- Add regression tests for the install output and projected content.
- Record the limitation and the inability to directly verify Codex's live
  session behavior in the Change artifacts.

## Out of Scope

- Changing any Harness skill/catalog refresh mechanism.
- Changing `change-scaffolding-cli` or the Doctor, Contract, Schema, or Flow
  implementations.
- Claiming that Codex has the same observed delay when no live Codex session
  is available to verify it.

## Success Criteria

- Installation output names the possible same-session discovery delay and gives
  the generated skill path as fallback.
- Both projected skills carry the same non-enforcement disclosure.
- Focused regression tests pass and no existing Adapter behavior regresses.
