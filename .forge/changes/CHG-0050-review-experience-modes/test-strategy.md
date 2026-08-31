---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0050
status: complete
---

# Test Strategy — CHG-0050

## Objective

Demonstrate, before Implementation, that (a) mode-to-profile resolution
can never rank below a Change's Flow-derived floor, (b) the new
schema-tracked phase field is validated for both invalid values and
status inconsistency, (c) the persistent project preference seeds new
scaffolds without ever overriding an already-set per-Change mode, (d)
both Adapters project mode/profile/phase text while leaving the
independence/convergence blocks byte-identical across modes, and (e)
`forge change review-status` reports correctly for a populated,
freshly-scaffolded, and non-existent Change, including the
non-authoritative `stopped` state.

## Strategy

| Layer | Scope | Method |
|---|---|---|
| Layer A · Core | `compute_review_profile_floor`, `resolve_effective_review_profile`, `_validate_review_current_phase`, schema acceptance/rejection | Automated (pytest, `tests/unit/`, `tests/contract/`) |
| Layer B · CLI | `forge change new` scaffolding with `review.mode`/`review.preferred_mode`, `forge change review-status` | Automated (pytest, `tests/cli/`) |
| Layer C · Adapters | `claude_code`/`codex` projection text for mode/profile/phase; independence/convergence block invariance | Automated (pytest, `tests/unit/test_claude_code_projection_gates.py`, `tests/unit/test_codex_projection_gates.py`) |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-002 | TDD-001, TDD-002, TDD-003 | Automated |
| FR-001 | TDD-004, TDD-005 | Automated |
| FR-004 | TDD-006, TDD-007, TDD-008 | Automated |
| FR-003 | TDD-009, TDD-010, TDD-011 | Automated |
| FR-005 | TDD-012 | Automated |
| FR-006 | TDD-013 | Automated |
| FR-007 | TDD-014 | Automated |

## Layer A · Core

### TDD-001 · `compute_review_profile_floor` extraction is behavior-preserving
Requirements: FR-002
Type: Unit

#### Purpose
Prove the extracted floor-computation function returns exactly what
`_validate_review_profile_floor`'s inline logic returns today for both
the no-override and valid-override cases — a wrong extraction would
silently change floor computation for every existing Flow.

#### Scenario
Given an effective Flow dict with only a canonical `review.profile`
When `compute_review_profile_floor(effective)` is called
Then it returns the canonical profile; and given the same dict with a
valid project-flow `review.profile` override
When called again
Then it returns the project override's profile, matching
`_validate_review_profile_floor`'s existing pass-through behavior for
both cases

#### Evidence
Unit test assertions on the function's return value; existing
`tests/unit/test_validation_review_profile.py` cases re-run unchanged
against the refactored validator to confirm no regression.

#### Failure Condition
Any divergence from `_validate_review_profile_floor`'s pre-refactor
behavior for either input shape.

### TDD-002 · `recommended`/`fast` never rank below the floor
Requirements: FR-002

#### Purpose
Prove the structural guarantee Specification's AC-003/AC-006 state: no
Flow/mode combination can resolve below the floor.

#### Scenario
Given each of the three floor profiles (`focused`, `standard`, `strict`)
When `resolve_effective_review_profile(floor, "recommended")` and
`resolve_effective_review_profile(floor, "fast")` are called
Then both return exactly `floor` in all three cases (six assertions)

#### Evidence
Parametrized unit test asserting equality for all 3×2 combinations.

#### Failure Condition
Any returned value with `_PROFILE_RANK` lower than the input floor's
rank.

### TDD-003 · `thorough` steps up one rank, capped at `strict`
Requirements: FR-002

#### Purpose
Prove AC-004/AC-005: `thorough` raises rigor by exactly one step and
never exceeds the closed three-value enum.

#### Scenario
Given floor `focused`
When `resolve_effective_review_profile(floor, "thorough")` is called
Then it returns `standard`; given floor `standard`, it returns
`strict`; given floor `strict`, it returns `strict` (unchanged, already
the ceiling)

#### Evidence
Parametrized unit test, three cases.

#### Failure Condition
Returning a value outside `{focused, standard, strict}`, or returning
`focused` for a `strict` floor with `thorough` (a below-floor
regression).

### TDD-004 · Schema accepts `review.mode`, rejects an invalid value
Requirements: FR-001

#### Purpose
Prove the schema change is real and enforced, not documentation-only.

#### Scenario
Given a `manifest.yml` fixture with `review.mode: thorough`
When validated against `change-v2.schema.json`
Then it is schema-valid; given `review.mode: nonexistent`
When validated
Then it is schema-invalid

#### Evidence
`tests/contract/test_review_profile_schemas.py` (existing file, new
cases) — schema validation result (pass/fail) asserted directly.

#### Failure Condition
Either fixture validating against expectation reversed.

### TDD-005 · Absent `review.mode` behaves as `recommended`
Requirements: FR-001

#### Purpose
Prove AC-001: omission is not merely schema-legal but actually treated
as `recommended` by every consumer, not left as `None`/`null` and
mishandled downstream.

#### Scenario
Given a manifest with no `review` key at all (a pre-CHG-0050 historical
manifest shape)
When `resolve_effective_review_profile` and the Adapter projection
helpers read its (absent) mode
Then both behave identically to an explicit `review.mode: recommended`

#### Evidence
Unit test constructing a manifest dict missing the key; direct
function-return comparison against the explicit-`recommended` case.

#### Failure Condition
A `KeyError`/`AttributeError`, or a different resolved profile/prose
than the explicit-`recommended` case.

### TDD-006 · Consistent `current_phase`/`status` combinations pass
Requirements: FR-004

#### Purpose
Prove AC-010 and AC-012b: both a fully-converged Change and a
not-yet-started Change validate cleanly.

#### Scenario
Given a manifest with `current_phase: converged` and `review.status:
passed`
When `_validate_review_current_phase` runs
Then it returns no finding; given a manifest with no `current_phase`
and an empty `review.iterations`
When it runs
Then it also returns no finding

#### Evidence
Unit test, two fixtures, empty finding list asserted for both.

#### Failure Condition
A finding raised for either valid combination (false positive).

### TDD-007 · Inconsistent `current_phase`/`status` is flagged
Requirements: FR-004

#### Purpose
Prove AC-011: the one consistency rule Specification actually commits
to is mechanically enforced, not merely described.

#### Scenario
Given a manifest with `current_phase: converged` and `review.status:
failed`
When `_validate_review_current_phase` runs
Then it returns exactly one finding naming the inconsistency

#### Evidence
Unit test asserting finding count and finding code/message content.

#### Failure Condition
No finding raised (false negative) or a finding raised for an
unrelated reason.

### TDD-008 · Invalid `current_phase` enum value is schema-rejected
Requirements: FR-004

#### Purpose
Prove AC-012.

#### Scenario
Given a manifest with `review.current_phase: not_a_real_value`
When validated against `change-v2.schema.json`
Then it is schema-invalid

#### Evidence
`tests/contract/test_review_profile_schemas.py`, schema validation
result.

#### Failure Condition
Fixture validates successfully against the schema.

## Layer B · CLI

### TDD-009 · `forge change new` seeds `review.mode` from `review.preferred_mode`
Requirements: FR-003

#### Purpose
Prove AC-007: the persistent preference actually reaches new scaffolds,
not only the schema accepting it.

#### Preconditions
A temporary Forge-initialized repository with `.forge/forge.yml`
`review.preferred_mode: thorough`.

#### Scenario
Given that repository
When `forge change new some-slug` runs
Then the created `manifest.yml` contains `review.mode: thorough`

#### Evidence
CLI integration test (`tests/cli/`) invoking the Typer command,
reading back the generated `manifest.yml`.

#### Failure Condition
The generated manifest has `review.mode: recommended` or omits the
field.

### TDD-010 · `forge change new` defaults to `recommended` without a preference
Requirements: FR-003

#### Purpose
Prove AC-008 and NFR-001: the common case (no preference set) is
unchanged from today's scaffold shape in every other respect.

#### Scenario
Given a Forge-initialized repository with no `review.preferred_mode`
When `forge change new some-slug` runs
Then the created `manifest.yml` explicitly carries `review.mode:
recommended` (the shipped scaffold always writes it, rather than
omitting it — AC-001/AC-008's "or omits it" alternative is satisfied
by every *consumer*'s interpretation, not by the scaffold's own
output) and every other field is unchanged from a pre-CHG-0050
scaffold

#### Evidence
CLI integration test; diff against the existing scaffold fixture used
by today's `forge change new` tests, confirming only `review.mode` is
new and no other field's shape changed.

#### Failure Condition
Any field other than `review.mode` changes shape in the generated
manifest.

### TDD-011 · An existing Change's `review.mode` is not retroactively overridden
Requirements: FR-003

#### Purpose
Prove AC-009: `review.preferred_mode` is read only at scaffold time,
never merged into an already-created Change's manifest.

#### Scenario
Given an already-scaffolded Change with `review.mode: fast` committed
When the project's `.forge/forge.yml` `review.preferred_mode` is
subsequently changed to `thorough` and `forge validate` (or any other
command reading that Change) runs
Then the existing Change's `manifest.yml` `review.mode` remains `fast`
on disk and as read by every consumer

#### Evidence
Unit/integration test asserting no code path in `validate_project`,
Adapter projection, or `review-status` re-derives `review.mode` from
project configuration for an existing manifest.

#### Failure Condition
Any consumer's resolved mode for the existing Change changes after the
project preference changes.

## Layer C · Adapters

### TDD-012 · Adapter projection includes the mode-resolution table and phase vocabulary; independence/convergence blocks stay byte-identical
Requirements: FR-005

#### Purpose
Prove AC-013/AC-014 (the projected text is real, not aspirational) and
— most importantly — AC-015: the one guarantee this Change must not
accidentally weaken is that independence and Convergence Limit
instructions are unaffected by the new projected content. (Corrected
per `DEC-004`: `_gate_instructions` projects per-Flow floor/thorough
values and one shared phase-vocabulary section, not a specific
Change's live `review.mode`/`current_phase` — see `architecture.md`.)

#### Scenario
Given the FAST Flow (floor `focused`)
When `claude_code/projection.py` and `codex/projection.py` each
project their FAST gate instructions
Then the output states the floor is `focused` and that `thorough`
resolves to `standard`; and given `protocol_id >= 2`
When the shared Review Experience Modes section is rendered
Then it names all six phase values with their human labels and names
`forge change review-status`; and when the independence and
Convergence Limit blocks specifically are extracted from the
projected output before and after this Change's projection changes
Then they are byte-identical

#### Evidence
Existing `tests/unit/test_claude_code_projection_gates.py` and
`test_codex_projection_gates.py`, extended with Flow-floor fixtures;
direct string-equality assertion on the independence/convergence
substrings.

#### Failure Condition
Any byte difference in the independence/convergence blocks from
today's output, or a resolved `thorough` value in the projected text
that does not match `resolve_effective_review_profile`'s actual return
value for that Flow's floor.

## Manual Acceptance

### TDD-013 · `forge change review-status` end states
Requirements: FR-006
Type: Manual Acceptance

#### Purpose
`review-status`'s terminal output formatting (human-readable text
layout) is reasonably covered by automated field-presence assertions,
but a human check that the printed next-step hint actually reads as
useful guidance — not just non-empty — is the property this scenario
proves.

#### Preconditions
A populated Change (mode, resolved profile, phase, one BLOCKER
Finding), a freshly scaffolded Change (no Review yet), and a
nonexistent Change slug.

#### Scenario
Given each of the three Changes above
When `forge change review-status <slug>` runs against each
Then the populated case prints mode/profile/phase/BLOCKER-count/a
next-step hint naming Resolution (AC-016); the fresh case states
"Review not yet started" explicitly (AC-016b); the nonexistent case
exits non-zero with a clear error and no side effect (AC-017)

#### Evidence
Automated assertions on exit code and the presence of each required
field/string (part of `tests/cli/`); a human operator additionally
confirms the next-step hint text is not misleading before this
scenario is marked covered.

#### Failure Condition
Any required field/string absent from automated output, or an operator
judging the next-step hint actively misleading (not merely terse).

### TDD-014 · `stopped` phase carries no approval authority
Requirements: FR-007

#### Purpose
Prove AC-018/AC-019: this is a pure observability statement, never a
path to a false Completion claim — the single most safety-relevant
property in this Specification.

#### Scenario
Given a Change with `review.current_phase: stopped` and `review.status:
failed`
When `forge validate` runs
Then it passes with no `current_phase`-attributable finding and
separately still reports the Change incomplete via existing Completion
checks; and when `forge change review-status <slug>` runs on the same
Change
Then its output states plainly that the Change is not complete and
names the last recorded outcome

#### Evidence
Unit test on `forge validate`'s combined output; CLI integration test
on `review-status`'s printed text.

#### Failure Condition
`forge validate` reporting the Change as complete, or `review-status`
omitting the incompleteness statement, for a `stopped` Change.

## Valid RED

Each Layer A/B/C automated scenario's RED is valid only when it fails
because the referenced function/field/command does not yet exist or
does not yet behave as specified (`ImportError`, `AttributeError`,
schema-validation-passes-when-it-should-fail, or an assertion on wrong
output) — never a fixture/import/environment failure unrelated to the
behavior under test (C-011). TDD-013's Manual Acceptance component has
no RED in the automated-test sense; its automated field-presence
assertions do carry ordinary RED/GREEN.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TDD-004, TDD-005 | — | Covered |
| FR-002 | TDD-001, TDD-002, TDD-003 | — | Covered |
| FR-003 | TDD-009, TDD-010, TDD-011 | — | Covered |
| FR-004 | TDD-006, TDD-007, TDD-008 | — | Covered |
| FR-005 | TDD-012 | — | Covered |
| FR-006 | (field-presence assertions) | TDD-013 | Covered |
| FR-007 | TDD-014 | — | Covered |

## Coverage Gaps

None. Every Functional Requirement has at least one scenario, and
FR-002 (the Specification's single most safety-relevant guarantee —
never resolving below the Flow floor) has three, covering all three
mode values against all three floor values.

## Test Strategy Gate

Every mandatory Requirement has a verification strategy; every
critical scenario (TDD-002, TDD-003, TDD-012, TDD-014) states a Purpose
that names the consequence of a wrong Implementation, not just the
mechanism; every scenario states a Failure Condition including its
false-positive/false-negative risk, not only "assertion fails";
automated and the one genuinely human-dependent scenario (TDD-013) are
separated and explicitly labeled; Valid RED is defined. Ready for Plan.
