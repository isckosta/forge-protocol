# Test Strategy — CHG-0017

## Objective

This Change's deliverable is mostly prose (a schema field, four Contract
rules, one Specification section, one ADR) plus one small, genuinely
executable surface (Codex Adapter projection: `AdapterProjectionContext`,
`CodexProjectionInput`, `_skill_content`, `service.py` wiring). Per
Protocol §19, TDD is `not_applicable` for the prose deliverables;
Verification/Strict Review remain mandatory for them regardless. TDD
applies fully to the schema validation behavior and to the Adapter
projection change.

## Strategy

Two TDD cases, both mechanically checkable:

## TDD-001 — Codex Adapter projects the effective interaction-language instruction

**Covers:** FR-004, AC-005, AC-006, AC-007.

**RED:** A test asserting `generate_codex_projection_bundle`/`CodexDriver`
output changes with `interaction_language` set: a case with
`interaction_language="pt-BR"` produces a `SKILL.md` line naming `pt-BR`
and citing C-072; a case with `interaction_language=""` (or `"auto"`)
produces the auto/fallback line citing C-070–C-073. Fails today: the
field, and `_skill_content`'s parameter, do not exist.

**GREEN:** Add the field at both dataclasses and the rendering branch in
`_skill_content`; wire `service.py`'s two construction sites to read
`configuration.get("interaction", {}).get("language", "auto")`.

**Expected Result:** The generated `SKILL.md` differs only by the one
new, intentional line in both cases; every other existing field
(`flow_content`, `contract_content`, `artifact_structure_content`) and
their rendered output are byte-identical to before this Change.

Also covers schema-level validation (AC-001, AC-002): a companion test
in the project-configuration test module confirms
`load_project_configuration` accepts an explicit code, `auto`, and an
absent `interaction` key, and rejects a malformed value.

## TDD-002 — Repository-wide `forge validate` / `forge doctor` / `pytest` baseline is unchanged

**Covers:** AC-008, CON-004.

**RED:** Record the exact current output of `forge validate`, `forge
doctor`, and `pytest -q` against this repository (including every
historical `CHG-0001`–`CHG-0016` manifest) as the pre-Implementation
baseline, before any edit lands.

**GREEN:** After Implementation, `forge validate`/`forge doctor` report
the identical overall status against every historical Change, plus a
successful result against `CHG-0017` itself once its own `manifest.yml`
is populated; `pytest -q` passes with only the new tests added, zero
regressions.

**Expected Result:** No historical Change transitions from valid to
invalid; any difference is investigated before Verification proceeds.

**Baseline recorded now, before Implementation** (HEAD `85c8ce0`, working
tree otherwise clean except this Change's own new, untracked planning
directory): `forge validate` reports **"Forge project is valid"** (exit
0); `forge doctor` reports all 7 checks `PASS`; `pytest -q` (full suite)
reports **430 passed**. Any regression against these exact figures during
Implementation is investigated before Verification proceeds.

## Non-mechanical Validation

Reviewed by Strict Review, not by an automated test, because the subject
is normative prose rather than executable behavior:

- `project.schema.json`'s new `interaction` property against FR-001 and
  against AC-001/AC-002 (pattern correctness, additive-only shape).
- New Contract rule wording (`C-070`–`C-073`) against FR-002, DEC-001's
  and DEC-002's actual resolutions, and SR-001's disclaimer requirement.
- `protocol/specification.md` §42 against FR-003 and against §2/§29/§33's
  existing "Core cannot observe the chat runtime" framing.
- `docs/adr/0015-*.md` against DEC-001's full record and this
  repository's own ADR style (`docs/adr/0012-unresolved-decision-management.md`,
  `docs/adr/0014-canonical-artifact-structure.md` as the closest
  structural precedents).
- INV-001 (no false compliance claim) checked directly against every
  Artifact this Change produces, not only the ones that name it.

## Completion Criteria

All of AC-001 through AC-010 satisfied; TDD-001/TDD-002 GREEN;
Non-mechanical Validation items reviewed and accepted at Strict Review;
`tdd-evidence.yml` and `traceability.yml` produced during Implementation
from what actually happened, not authored in advance (C-016/C-021).

## Traceability (informal — `traceability.yml` itself is Plan/Tasks-stage-onward work)

FR-001 → AC-001/AC-002 → TDD-001 (schema companion test). FR-002 →
AC-003 → content review + specification-review.md SR-002 precedent
check. FR-003 → AC-004 → content review. FR-004 → AC-005/AC-006/AC-007 →
TDD-001. FR-005 → AC-009/AC-010 → Documentation Impact review.
CON-004 → AC-008 → TDD-002.
