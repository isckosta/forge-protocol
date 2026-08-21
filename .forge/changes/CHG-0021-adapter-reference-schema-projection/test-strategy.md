---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0021
status: approved
---

# Test Strategy — Adapter Reference Schema Projection

## Objective

Every Functional and Non-functional Requirement in `specification.md`
is executable, so every one is covered by a RED-then-GREEN TDD cycle;
none requires Non-mechanical Validation.

## Strategy

Follow `CHG-0016`'s own precedent test shape: extend the two existing
projection-bundle test modules (`test_claude_code_projection_bundle.py`,
`test_codex_projection_bundle.py`) with the same "includes when provided
/ omits when not provided" pair already used for
`artifact_structure_content`, add a small dedicated module asserting the
renderer's content against the live constants (not a second hand-typed
expectation — that would itself violate NFR-001), and extend
`test_unresolved_decisions.py` for the sharpened error message. A final
regression cycle re-runs the full suite, `forge validate`, and
`forge doctor` against the pre-Implementation Baseline recorded in
`discovery.md`.

## TDD-001 — Renderer output matches the live constants (FR-001, AC-001)

**Covers:** `render_decision_rules_reference()` contains every value
from `_DEC_CLASSES`, `_DEC_MATERIALITY`, `_DEC_STATUSES`,
`_DEC_AUTHORITIES`, `_DEC_RESOLVED_VIA`, and every `class` →
`owning_artifact` pair from `_DEC_OWNING_BY_CLASS`.

**RED:** `ImportError`/`AttributeError` — the function does not exist
yet.

**GREEN:** the test imports the real constants (not a re-typed literal)
and asserts `str(value) in rendered` for each member of each set, and
each `f"{cls}"`/`f"{artifact}"` pair from `_DEC_OWNING_BY_CLASS`. This
is the test that would fail if a constant changed and the renderer did
not follow — the mechanical form of NFR-001.

**Expected Result:** GREEN once the renderer names all seven constants
explicitly.

## TDD-002 — Claude Code Adapter includes the resource and link when provided (FR-002, AC-002)

**Covers:** `generate_claude_code_skill_bundle(..., decision_rules_content=<non-empty>)`
includes a `skills/forge/references/decision-rules.md` resource with the
exact content, and `SKILL.md`'s "Effective Forge references" section
includes its link.

**RED:** `TypeError: generate_claude_code_skill_bundle() got an
unexpected keyword argument 'decision_rules_content'`.

**GREEN:** resource and link present, content byte-identical to the
input.

**Expected Result:** GREEN.

## TDD-003 — Codex Adapter includes the resource and link when provided (FR-003, AC-003)

**Covers:** the same pair for `generate_codex_skill_bundle`.

**RED:** same `TypeError` shape for the Codex bundle generator.

**GREEN:** resource and link present, content byte-identical to the
input.

**Expected Result:** GREEN.

## TDD-004 — `resolved_via` error message states expected values (FR-004, AC-004)

**Covers:** an invalid `resolved_via` finding message contains
`"expected one of"` and the sorted `_DEC_RESOLVED_VIA` values.

**RED:** `AssertionError` — today's message
(`validation/__init__.py:418`) only states
`"has an invalid resolved_via {resolved_via!r}."`, with no expected-
values clause.

**GREEN:** message updated per `architecture.md` "Error message change";
existing `test_unresolved_decisions.py` cases that only check for the
substring `"has an invalid resolved_via"` continue to pass unchanged
(the new clause is appended, not a replacement).

**Expected Result:** GREEN, with zero regressions in existing
`resolved_via`-adjacent test cases.

## TDD-005 — Additive-only: resource omitted when content not provided, both Adapters (FR-005, AC-005)

**Covers:** a caller that does not pass `decision_rules_content` (or
passes `""`) produces a bundle with no `decision-rules.md` resource and
no reference link, for both Adapters — the same shape
`test_projection_bundle_omits_artifact_structure_resource_when_not_provided`
already protects for the sibling resource.

**RED:** not applicable — this is a compatibility guard mirroring
`CHG-0016`'s own `TDD-002`, which recorded `red.observed: false` for the
identical reason: the omitted-resource set is true by construction both
before and after this Change for a caller that never opts in.

**GREEN:** new/extended assertions pass; the full pre-existing suite is
otherwise unaffected.

**Expected Result:** GREEN; `red.observed: false` recorded honestly in
`tdd-evidence.yml`, matching `CHG-0016`'s own precedent for this exact
shape of guard.

## TDD-006 — Cross-Adapter content parity at the wiring level (AC-006)

**Covers:** the same rendered string, resolved once via
`render_decision_rules_reference()` and threaded through
`AdapterProjectionContext`, produces byte-identical
`skills/forge/references/decision-rules.md` and
`references/decision-rules.md` resources when both Adapters' bundle
generators are called with that one resolved value — not merely that
each generator independently echoes whatever it is given (`TDD-002`/
`TDD-003` already cover that).

**RED:** not applicable — like `TDD-005`, this is a compatibility/parity
guard, not new behavior; nothing today produces divergent content
because the wiring does not exist yet for either Adapter to diverge on.

**GREEN:** a single resolved value from `render_decision_rules_reference()`
passed to both `generate_claude_code_skill_bundle` and
`generate_codex_skill_bundle` yields identical `decision-rules.md`
resource content in both bundles.

**Expected Result:** GREEN; `red.observed: false` recorded honestly, for
the same reason as `TDD-005`.

## TDD-007 — Regression baseline unchanged (AC-007)

**Covers:** `forge validate` and `forge doctor` report the same overall
project-valid status before and after Implementation, and the full
`pytest -q` suite passes with only this Change's own deliberate,
additive new tests changing the count from the `discovery.md` Baseline
(524 passed).

**RED:** not applicable — regression guard, matching `CHG-0016`'s own
`TDD-003` methodology exactly.

**GREEN:** pre/post comparison recorded in `verification.md`.

**Expected Result:** GREEN, no new `forge validate`/`forge doctor`
finding anywhere in this repository's history from `CHG-0001` through
`CHG-0020`.

## Non-mechanical Validation

None. Every Functional Requirement in `specification.md` is executable
Python behavior; no prose/normative-only deliverable exists in this
Change's scope (contrast `CHG-0016`, which also had `protocol/
artifact-structure.md`'s prose content itself to validate by Review
rather than by test).

## Completion Criteria

- TDD-001 through TDD-007 all GREEN;
- AC-001 through AC-007 satisfied;
- full suite, `forge validate`, `forge doctor` green per TDD-007;
- Strict Review passes with zero blocking (blocker/major) findings.
