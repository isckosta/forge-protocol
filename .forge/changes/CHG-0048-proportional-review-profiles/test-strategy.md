---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0048
status: complete
---

# Test Strategy — CHG-0048

## Objective

Prove each FR's actual observable behavior — not just that a string
appears somewhere. Four test levels, matching the four kinds of claim
this Change makes:

- **Validation-behavior tests** (pytest, real `_validate_review_profile_floor`/
  `validate_project` invocations against `tmp_path` fixtures) — FR-010's
  fail-closed claim, FR-007's "no new conditioning" negative claim.
- **Schema round-trip tests** (`jsonschema` validate calls against small
  literal documents) — FR-008's additive/narrowing claims for the four
  touched Schemas.
- **Rendering-shape tests** (pytest, no real Git repository, mirroring
  CHG-0045's own pattern) — FR-002–FR-004/FR-009's per-Flow instruction
  text claims.
- **Repository-state tests** (pytest against this repository's own
  current `.forge/changes/*/manifest.yml` population) — FR-011's
  no-historical-regression claim.

## TDD-001 · Profile floor rejects a weaker-than-canonical project override
FR-010 / AC-010. Given a `tmp_path` Forge project with `.forge/flows/full.yml` (`schema: forge/project-flow@1`) declaring `review: {profile: focused}`, when `validate_project` runs, then a Finding referencing the weaker-than-floor profile is present — assert on the Finding's presence and its two named profiles (`focused`, `strict`), not merely non-zero Finding count.

## TDD-002 · Profile floor accepts a stricter-than-canonical project override
FR-010 / AC-010. Given the same fixture shape but `.forge/flows/fast.yml` declaring `review: {profile: strict}` (FAST's canonical floor is `focused`), when `validate_project` runs, then no Finding referencing profile floor is present.

## TDD-003 · Profile floor is silent when a project declares no profile override
FR-010's Boundary. Given `.forge/flows/standard.yml` present but with no `review.profile` key at all (only `review: {blocking: [...]}`, today's real shape), when `validate_project` runs, then no profile-floor Finding is produced — confirms the new check does not regress the existing, unrelated `blocking` override path.

## TDD-004 · `change-v2.schema.json` accepts and validates `profile`
FR-008 / AC-008. Given three minimal `manifest.review` documents differing only in `profile` (`focused`, `standard`, `strict`) and one omitting `profile` entirely, when each validates against the updated schema, then all four pass; a fifth document with `profile: "adversarial"` (an invalid enum value) fails validation.

## TDD-005 · `policy-review-v2.schema.json` and `project-flow.schema.json` accept `profile`
FR-008 / AC-008. Given a minimal Protocol 2 review-policy document and a minimal project-flow document, each with and without `profile`, when validated, then presence and omission both pass; an invalid enum value fails on both.

## TDD-006 · `flow.schema.json` no longer forces `strict`/`adversarial` to `true`, but still requires `profile`
FR-008 / AC-008 (Specification Review SR-003). Given a minimal Flow `review` document with `profile: focused, strict: false, adversarial: false, required: true`, when validated, then it passes (today's schema would reject `strict: false`); given the same document with `profile` omitted, then it fails (profile becomes required, replacing the removed `const: true` guarantee with an explicit one).

## TDD-007 · The three canonical Flow files and the canonical review policy still validate after editing
FR-001 / AC-001. Given the edited `protocol/flows/{fast,standard,full}.yml` and `protocol/versions/2/policies/review.yml`, when each validates against `flow.schema.json`/`policy-review-v2.schema.json` respectively, then all pass, and each declares exactly the canonical `profile` FR-001 specifies (`focused`/`standard`/`strict`).

## TDD-008 · `policy-review.schema.json` (Protocol 1) is byte-identical
FR-008's Boundary / AC-008. Given the pre-Change and post-Change content of `protocol/schemas/policy-review.schema.json`, when diffed, then there is no difference.

## TDD-009 · `resolve_effective_flow`'s return value round-trips through the new floor check unchanged for non-review keys
FR-010's Boundary. Given a project Flow file also declaring `testing: {approach: tdd_first}`, when `validate_project` runs, then the existing `testing`-related validation behavior (if any) and the new profile-floor check both evaluate independently — the new function does not read or affect non-`review` keys.

## TDD-010 · Adapter-projected instruction text is profile-specific per Flow
FR-002/FR-003/FR-004, FR-009 / AC-002, AC-003, AC-004, AC-009. Given a project with `fast`, `standard`, `full` all enabled under Protocol 2, when the Claude Code Adapter's generated `SKILL.md` renders, then the FAST gate-obligation section contains the `focused`-profile instruction text, STANDARD's contains the `standard`-profile text, FULL's contains text equivalent in substance to today's `"Completion requires Strict Review to pass."` — and the three are pairwise distinct strings.

## TDD-011 · Codex Adapter output matches Claude Code's per-Flow instruction text
FR-009 / AC-009 (parity, mirroring CHG-0045's TDD-003 pattern). Given both Adapters render for the same project, when their per-Flow review-instruction lines are compared, then they are identical in substance (same profile-instruction source, not independently authored copies that could drift).

## TDD-012 · Reviewer/Resolver independence block remains single, shared, and unchanged
FR-009's Boundary / AC-009. Given the same rendered `SKILL.md`, when the independence block is located, then it occurs exactly once (mirroring CHG-0045's TDD-001) and its content is unchanged from the pre-Change baseline — confirms this Change does not reopen CHG-0045's consolidation.

## TDD-013 · `MR-004`'s diagnostic label is profile-neutral; trigger condition is unchanged
FR-013 / AC-013. Given a Change with `review.status` not `passed`, when `merge_readiness.evaluator` runs, then an `MR-004` diagnostic is produced whose message text does not contain the substring `"Strict Review"`; given the existing `blockers > 0` / `majors > 0` trigger-condition tests in `tests/unit/test_merge_readiness*.py` (if they assert on message text, they are updated to match; if they assert only on the `MR-004` code and trigger condition, they continue passing unmodified).

## TDD-014 · Review Profile is derived from the Change's effective Flow at render time, not cached
FR-012 / AC-012 (Specification Review SR-006). Given a Change manifest with `flow.current: fast` at one point in time and `flow.current: full` at a later point (simulating a C-005 escalation between two Adapter-render calls), when the per-Flow instruction is rendered both times, then the second render reflects `full`'s `strict` profile — the function reads `manifest.flow.current` fresh each call, with no module-level cache keyed only on Change id.

## TDD-015 · No historical Change manifest is invalidated
FR-011 / AC-011. Given every `.forge/changes/*/manifest.yml` in this repository with `state.current: complete` at the start of this Change, when `forge validate` runs against the post-Change repository state, then no new Finding is attributed to any of those paths.

## Non-mechanical Validation

### Manual Acceptance — Contract prose coherence
FR-005/FR-006 (C-022, C-023, C-031 revised text). A maintainer reads the revised Contract text in context (surrounding rules, cross-references from Flow/policy files) and confirms it reads as a coherent, unambiguous obligation for a future agent or human Reviewer — not merely that specific words appear. This cannot be reduced to a string-match test without risking exactly the "looks compliant, isn't" failure mode Specification Review SR-004 already flagged as a known residual risk (CON-003). Evidence: the Strict Review Iteration itself, reading the diff.

## Completion Criteria

Every FR-001–FR-013 maps to at least one TDD case above (Manual Acceptance covers FR-005/FR-006's prose-quality dimension in addition to their mechanical AC checks in TDD-004/006/007). No TDD case is presented as proof of a property (semantic equivalence, exhaustive-search compliance) it cannot actually establish — TDD-004 (Adapter parity) is an early-warning drift guard, not proof of independent authorship never diverging; the Manual Acceptance entry is explicitly non-mechanical, not disguised as automated coverage.
