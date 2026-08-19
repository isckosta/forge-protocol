---
forge:
  artifact: verification
  schema: 1
change: CHG-0017
status: passed
---
# Verification — CHG-0017

## Result

**PASS.**

## Summary

| Acceptance Criterion | Result |
| --- | --- |
| AC-001 — schema accepts explicit code, `auto`, and absent `interaction` | PASS |
| AC-002 — schema rejects a malformed `interaction.language` value | PASS |
| AC-003 — C-070–C-073 in both Contract files, verified against precedent | PASS |
| AC-004 — `protocol/specification.md` §42 added after §41 | PASS |
| AC-005 — explicit-language `SKILL.md` line, citing C-072 | PASS |
| AC-006 — auto/fallback `SKILL.md` line, citing C-070–C-073 | PASS |
| AC-007 — existing Codex projection tests unaffected except the one new line | PASS |
| AC-008 — no new `forge validate`/`forge doctor` finding on historical Changes | PASS |
| AC-009 — `docs/adr/0015-*.md` exists, records DEC-001 | PASS |
| AC-010 — `CHANGELOG.md`/`ROADMAP.md` updated | PASS |

## Test Evidence

- `pytest -q` (full suite): **437 passed, 0 failed** — up from the
  pre-Implementation baseline of 430. 7 new tests added by this Change:
  `test_accepts_absent_interaction_language`,
  `test_accepts_explicit_interaction_language`,
  `test_accepts_auto_interaction_language`,
  `test_rejects_malformed_interaction_language`,
  `test_projection_bundle_renders_auto_interaction_language_by_default`,
  `test_projection_bundle_renders_explicit_interaction_language_when_provided`,
  `test_codex_projection_renders_effective_interaction_language`.
- TDD-001 and TDD-002 (`tdd-evidence.yml`): both GREEN. RED validly
  observed for TDD-001's three projection-layer tests (`AssertionError`/
  `TypeError` for the expected, not-yet-implemented reason). No RED was
  observed for TDD-001's four schema-layer companion tests in
  `test_project_configuration.py` — the schema edit landed in the same
  commit batch as the Contract/Specification/ADR text, before these
  tests were written; recorded honestly in `tdd-evidence.yml`'s notes as
  a process ordering gap, not a legitimate non-applicability.
- No pre-existing test required modification (unlike `CHG-0016`'s wheel
  probe update) — this Change's `SKILL.md` output change is additive
  content on an existing line-position rather than a new file, and no
  existing test asserted the exact absence of that line.

## Forge Evidence

- `forge validate` — **"Forge project is valid"** (exit 0), unchanged
  from the pre-Implementation baseline, including this Change's own
  manifest.
- `forge doctor` — **7/7 checks PASS**, unchanged.
- End-to-end CLI verification (beyond unit tests): two real scratch
  Git repositories, each through `forge init` → `forge adapter install
  codex` (or `forge adapter update codex` after editing
  `.forge/forge.yml`). Auto case: rendered `SKILL.md` line reads
  `Interaction language: auto -- use the active chat's observed language
  if there is one, otherwise English (C-070-C-073).`. Explicit
  `interaction.language: pt-BR` case: `Interaction language: pt-BR
  (project configuration takes precedence -- C-072).`. `forge doctor`
  reported `adapter:codex:generated_drift` PASS in both cases.

## Compatibility

No file under `protocol/schemas/` other than `project.schema.json`
changed (CON-002). No historical Change (`CHG-0001`–`CHG-0016`) reports
a new `forge validate` finding. `AdapterProjectionContext` and
`CodexProjectionInput` both gained the new field as an additive default,
confirmed by every pre-existing caller/test continuing to pass unchanged
except the one intentional new `SKILL.md` line.

## What Required Correction During Implementation Itself

None beyond what `architecture.md` already anticipated (all four
`service.py`/`driver.py`/`projection.py` touch points were named in
advance, unlike `CHG-0016`'s Plan, which undercounted its own file list).

## Limitations

Per DEC-001, the repository/context-language heuristic precedence level
`ROADMAP.md` originally sketched is not implemented — a project without
an explicit `interaction.language` depends entirely on the Harness's own
chat-observed language, falling back to English. Per C-073/INV-001, this
Verification (and no other Forge Artifact) can confirm what language a
live Harness session actually produced — only that the correct
instruction was projected.

## Conclusion

All 10 Acceptance Criteria verified PASS. Zero regressions in the 430
pre-existing tests; 7 new tests added and passing. `forge validate` and
`forge doctor` unchanged, confirmed both by unit tests and by two
independent real end-to-end CLI runs. Ready for independent Strict
Review.
