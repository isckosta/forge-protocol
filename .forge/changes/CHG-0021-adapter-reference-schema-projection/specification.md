---
forge:
  artifact: specification
  schema: 1
change: CHG-0021
status: complete
---

# Specification — Adapter Reference Schema Projection

## Summary

Add a Markdown reference documenting the Decision structural rules
`forge validate` enforces (`class`, `materiality`, `status`, `authority`,
`resolved_via` enums; `class` → valid `owning_artifact`; `class` →
authority floor), generated directly from the existing validation
constants, and project it into both the Claude Code and Codex Adapters'
`references/`. Sharpen the `resolved_via` invalid-value error message to
state the expected values.

## Classification

**FULL.** Direct precedent: `CHG-0016` (`canonical-artifact-structure`)
is the closest real analog in this repository's history — one new
derived reference, projected into both Adapters, with the accompanying
skill-link and resource-inclusion changes — and it also classified FULL
(reasoning in its own prose, not by naming a specific disqualifier).
This Change's own reasoning is explicit: it touches
`validation/__init__.py`, both Adapters' `projection.py` and
`driver.py`, and `adapters/driver.py`/`adapters/service.py` — five
modules, matching `significant_cross_module_change`, one of FAST's
disqualifiers (`protocol/flows/fast.yml`). The projected `references/`
surface is also consumer-facing across every project that installs
either Adapter, and `protocol/flows/standard.yml` has no
`specification_review` stage at all, so FULL is the only canonical Flow
under which this Review is even a required Gate. See `discovery.md`
"Flow Classification Finding".

## Functional Requirements

### FR-001

A new public function renders Markdown documenting the Decision
structural rules directly from the live validation constants
(`_DEC_CLASSES`, `_DEC_MATERIALITY`, `_DEC_STATUSES`, `_DEC_AUTHORITIES`,
`_DEC_RESOLVED_VIA`, `_DEC_OWNING_BY_CLASS`, `_DEC_AUTHORITY_FLOOR`) —
no enum value or mapping is duplicated as a second, independently
maintained string literal anywhere in the new code or its tests.

### FR-002

The Claude Code Adapter projects this content as
`skills/forge/references/decision-rules.md` when non-empty, and links it
from `SKILL.md`'s "Effective Forge references" section, using the same
conditional-inclusion pattern (`has_*` gates both the resource and the
link) `CHG-0016` already established for `artifact-structure.md`.

### FR-003

The Codex Adapter projects the same content as
`references/decision-rules.md` when non-empty, linked the same way, so
both Adapters stay at parity for this reference the way they already do
for `artifact-structure.md` and `engineering-contract.md`.

### FR-004

`forge validate`'s invalid-`resolved_via` error message states the
expected values, in the same `"(expected one of {sorted(...)})"`
convention the existing `owning_artifact` message
(`validation/__init__.py:439`) already uses.

### FR-005

The new resource is additive-only: a caller of either Adapter's bundle
generator that does not pass the new content parameter produces
byte-identical projection output to before this Change — the same
compatibility contract `CHG-0016` established for
`artifact_structure_content`.

## Non-functional Requirements

### NFR-001

The rendered reference and the constants it documents cannot drift
apart structurally: the render function reads the constants directly
(no copy-pasted enum literal in the renderer itself), and its tests
assert the rendered output against the same imported constants rather
than against a second hand-typed expectation.

### NFR-002

No import cycle is introduced. `validation/__init__.py` already imports
from `protocol_resolution` (`discovery.md` "A real constraint: import
direction"); the render function's placement must not create an edge in
the opposite direction.

## Security Requirements

None. This Change adds a documentation-generation function and an error
message; it does not change what `forge validate` accepts or rejects,
what any Adapter enforces, or any authorization/authentication surface.

## Constraints / Invariants

### CON-001

No file under `protocol/schemas/` changes. Promoting
`_DEC_OWNING_BY_CLASS`/`_DEC_AUTHORITY_FLOOR` into
`change-v2.schema.json` (`discovery.md` "Candidate A") is explicitly
deferred, not attempted here.

### CON-002

No new Gate, Finding severity, Decision semantic, or Flow stage is
introduced or altered.

### INV-001

The projected reference documents only the mechanical rules
`forge validate` enforces. It MUST NOT restate Engineering Contract
prose already covered by `references/engineering-contract.md` — the
same non-restatement principle `protocol/artifact-structure.md` itself
follows (its own §1).

## Acceptance Criteria

- **AC-001** (FR-001): a unit test imports the real validation
  constants and asserts the rendered Markdown contains every value from
  each, and every `class` → `owning_artifact` pair from
  `_DEC_OWNING_BY_CLASS` — the test fails if a constant changes and the
  renderer does not follow.
- **AC-002** (FR-002): `generate_claude_code_skill_bundle` includes
  `skills/forge/references/decision-rules.md` with the exact rendered
  content when a non-empty value is passed, and includes its reference
  link in `SKILL.md`.
- **AC-003** (FR-003): `generate_codex_skill_bundle` includes
  `references/decision-rules.md` with the exact rendered content when a
  non-empty value is passed, and includes its reference link.
- **AC-004** (FR-004): a unit test asserts an invalid `resolved_via`
  finding message contains `"expected one of"` and the sorted expected
  values.
- **AC-005** (FR-005): both Adapters' existing "resource omitted when
  content not provided" tests are extended to cover the new resource;
  full suite passes with only the deliberate, additive new tests
  changing the count.
- **AC-006** (FR-002, FR-003): the same rendered content, resolved once
  and threaded through `AdapterProjectionContext` the way
  `artifact_structure_content` already is (`adapters/service.py:445,612`),
  produces byte-identical `skills/forge/references/decision-rules.md`
  and `references/decision-rules.md` resources across both Adapters —
  checked at the composition-root wiring level, not only per-bundle-
  generator.
- **AC-007**: `forge validate` and `forge doctor` report the same
  overall project-valid status before and after Implementation
  (regression baseline; see `test-strategy.md` TDD-004), matching
  `CHG-0016`'s own `AC-013` convention for this exact check.

## Out of Scope

See `intent.md` "Out of Scope" — unchanged here.
