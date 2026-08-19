# Changelog

All notable Forge changes will be documented here.

CLI releases will follow Semantic Versioning when releases begin. Protocol versions are tracked independently.

## Unreleased

### Canonical Artifact Structure

Added:

- `protocol/artifact-structure.md`: canonical, non-binding guidance for
  the information architecture of human Forge Artifacts (Progressive
  Disclosure, Artifact Responsibility, Result-Before-Evidence,
  Scanability, Proportionality, Extensibility), plus recommended
  structure per Artifact type — motivated by a measured regression in
  this repository's own history: `CHG-0001/verification.md` opened with
  a `## Result` heading; `CHG-0015/verification.md` did not
  (`docs/adr/0014`);
- Contract rules C-067 (conformance MUST NOT be a Gate condition or a
  `forge validate` check), C-068 (Verification/Review SHOULD present
  outcome before evidence), and C-069 (an approved Plan SHOULD NOT
  silently absorb Implementation-time discoveries) — all `SHOULD`-level,
  none Gate-checked; every historical Change remains unaffected;
  `protocol/specification.md` §41 points to the new guidance;
- the Codex Adapter now projects the guidance by reference (a new,
  optional `references/artifact-structure.md` resource, included only
  when the canonical file resolves) using the same mechanism already
  used for Flow and Contract content — `AdapterProjectionContext` and
  `CodexProjectionInput` both gained the new field as an additive
  default, so every existing caller keeps generating exactly the
  resource set it always did;
- `examples/canonical-artifacts/`: two annotated, illustrative examples
  (`verification.md`, `review.md`) demonstrating outcome-first structure
  — not a reformatting of any historical Change.

### Delegated Agent Authority and Side-Effect Boundaries

Added:

- a normative distinction between Capability (what an Execution can
  technically do) and Authority (what a specific delegation permits it to
  do), motivated by a real incident: a research subagent explicitly
  delegated read-only work during `CHG-0014`'s Discovery overwrote that
  Change's `intent.md` directly, detected only because a human-equivalent
  Execution happened to notice — no Forge mechanism could have caught it
  (`docs/adr/0013`);
- `forge/execution-provenance@2`: a new `role: delegated_task`, an
  `execution.delegated_by` chain reference, a `baseline` field capturing
  Execution Boundary open-state (a commit plus a content-identity map of
  already-dirty paths, so a delegating Execution's own concurrent work is
  never misattributed to its delegate), and a `scope` `minItems: 0`
  relaxation so zero-write-authority (read-only) delegation is
  representable at all — `@1` is unchanged and remains valid;
- Contract rules C-060 through C-066 (Capability is not Authority,
  Out-of-Scope Mutation for delegated Executions, no self-authorization,
  Delegation Ceiling, Detection as the mandatory floor with Prevention
  optional, fail-closed on indeterminate authorization, harness honesty),
  binding only once a Change records a `role: delegated_task` provenance
  entry — every historical Change remains unaffected;
- `forge validate` now mechanically detects Out-of-Scope Mutation and
  self-authorization for delegated Executions using local Git-native state
  only, independent of Change lifecycle stage (including before any
  Review-subject freeze, the exact point the motivating incident occurred
  at) — no Harness cooperation required, no Harness capability change
  added (none currently supports Prevention).

### Golden Path Baseline and Codex Onboarding Validation

Added:

- `docs/getting-started.md`, the primary install-to-first-Change onboarding
  path, and `examples/golden-path-standard/` (a disposable starter fixture,
  deterministic Layer A/B automated tests under `tests/golden_path/`, and a
  behaviorally-specified manual Codex acceptance procedure) — the first
  reproducible, evidence-backed Golden Path for Forge + Codex
  (`ROADMAP.md`'s "End-to-End Examples & External Project Validation" §Golden
  path, STANDARD/Codex slice);
- `forge doctor` now aggregates every installed Harness Adapter's own
  diagnostics (reusing `AdapterService.doctor`) so one command answers "is
  this repository ready to begin a Forge Change through this Harness?"
  instead of requiring a separate `forge adapter doctor <id>` call a
  first-time user would not know to run;
- `forge adapter install <adapter>` now prints a success confirmation naming
  the installed target and the next action when it actually mutates the
  repository, closing a real gap in the "no manual prompt copying" v1
  onboarding promise (`ROADMAP.md`'s Adapter CLI & Codex Installation UX
  exit criteria);
- the generated Codex `SKILL.md` now represents the complete
  `before_completion` gate set (Documentation Impact evaluation, required
  documentation updates, TDD compliance or exception — previously silently
  absent) and, more materially, the `before_implementation` boundary itself:
  a Codex session previously received no instruction that Discovery,
  Specification, and Plan must be complete before Implementation begins at
  all.

Known limitations (accepted, documented follow-up — see CHG-0014's
`verification.md` Product findings):

- Adapter conformance checking (`validate_conformance`) verifies gate
  *names* are represented, not that every individual completion-gate
  *instruction* is textually present, so a future regression of the class
  this Change fixes would not be mechanically caught by `forge adapter
  doctor`'s conformance check;
- Forge's canonical Protocol still has no mechanically-enforced human
  approval Gate between Plan and Implementation; the new instructions and
  `docs/getting-started.md` represent that boundary but do not yet make
  Core capable of proving it on its own;
- `forge validate` still performs no JSON Schema validation of
  `manifest.yml`/`tdd-evidence.yml`/`provenance.yml` against
  `protocol/schemas/*` for an arbitrary project (pre-existing, independently
  reconfirmed while building this Change's own Layer B evidence).

### Unresolved Decision Management

Added:

- a new normative Protocol concept, **Unresolved Decision**: a material
  decision required for an Artifact or Gate to be sufficiently determined,
  whose answer has no valid normative authority yet — classified into
  `product`, `contract`, `architectural`, or `technical`, each with a
  default Decision Authority (`human`, `agent`, or `agent_with_review`,
  `protocol/policies/decision.yml`);
- Contract rules C-051–C-059 (`protocol/contract/engineering.md` and
  `protocol/versions/2/contract/engineering.md`, the latter also backfilled
  with the previously-missing C-047–C-050 from CHG-0011) requiring
  evidence-first investigation before escalation, a Recommendation distinct
  from a Decision, a non-negotiable human-authority floor for `product`/
  `contract` Decisions, and explicit backward invalidation when an upstream
  Decision changes after downstream Artifacts already depended on its
  absence;
- `protocol/specification.md` §39 and a new `forge/policy/decision@1`
  canonical Policy and schema;
- an optional, additive `decisions[]` field on both `forge/change@1` and
  `forge/change@2`, and a new `forge validate` mechanical boundary
  (`_validate_unresolved_decisions`) enforcing Gate-blocking, `resolved_via`/
  authority consistency, and invalidation-target shape.

Known limitation (accepted, documented follow-up — see
`.forge/changes/CHG-0013-unresolved-decision-management/knowledge-capture.md`):

- `supersedes`/`superseded_by` are schema-declared but not yet mechanically
  cross-checked for existence/consistency; Decision findings are all tagged
  with the single umbrella code `C-051`; an `artifacts` value of `null`
  (as opposed to absent or a real status) still bypasses the invalidation
  check — none reachable through any code path in this repository today.

### Freeze check exempts complete Changes

Fixed:

- `forge validate`'s Protocol 2 review-subject freeze-drift check no longer
  fires for a passed Review Iteration once its Change's `state.current` is
  `complete`; unrelated, expected commits from other Changes continuing
  development on the same branch no longer resurrect a closed, already
  independently-reviewed Change as a validation failure.

Known limitation (accepted, documented trade-off — see CHG-0012's
`specification-drift.md`):

- once a Change's `state.current` reaches `complete`, the freeze-drift check
  no longer inspects further activity on that Change's own previously
  reviewed files, including a hand-edited `state.current` that was never
  genuinely earned through Completion. This mirrors Protocol 2's existing
  `assurance: recorded` (self-declared) trust model rather than closing a
  gap no other layer of `forge validate` defends against either.

### Adapter CLI and Codex Installation UX

Added:

- an Adapter CLI command group — `forge adapter list`, `configure`, `plan`,
  `install`, `validate`, `doctor`, `update` — completing the documented
  `forge init` → `forge adapter install codex` v1 onboarding path;
- deterministic plan-before-mutation, ownership-aware publication, collision
  and stale-state protection, drift diagnostics, and safe/idempotent updates
  for Adapter installation through the generic Adapter Core;
- stable `E_FORGE_*` exit codes for publication conflicts, unsafe paths, and
  stale on-disk installation records, replacing internal-error fallthrough
  for expected, well-understood domain/validation failures.

Fixed:

- a class of TOCTOU (time-of-check/time-of-use) defects in adapter
  publication where a path resolved once and reused across preflight,
  authorization, mutation, and rollback allowed a directory-to-symlink swap
  to redirect installation-record reads/writes, or a rollback restore,
  outside the repository root, including cases that could forge the
  authorization used for a publication or exfiltrate original file content
  during rollback. Closed through six independent Strict Review iterations
  (`.forge/changes/CHG-0010-adapter-cli-codex-ux/review.md`) that each
  re-resolve the affected path immediately before use rather than reusing a
  path captured earlier in the operation.

### Protocol 2 — Verifiable Review Independence

Added:

- integer **Protocol 2** as the compatibility boundary for mandatory independent Strict Review Execution and Execution Context;
- version-specific Protocol 2 Contract, Specification, and Review Policy resources under `protocol/versions/2/`;
- `forge/execution-provenance@1`, a provider-independent repository-native ledger for Implementation, Resolution, and Review execution provenance;
- explicit provenance assurance levels: `claimed`, `recorded`, and `verified`, with at least `recorded` required for Protocol 2 `review_passed`;
- iteration-aware Protocol 2 Review state in `forge/change@2`, linking each passed Review to subject and Reviewer provenance for the revision under review;
- FAST, STANDARD, and FULL Protocol 2 validation for missing/forged provenance, wrong revision binding, shared Execution, shared Context, partial evidence, contaminated re-review, active schema downgrade, and dirty frozen review subjects;
- effective Git review-subject freeze validation across committed, staged, unstaged, deleted/renamed, and Git-visible untracked reviewable paths while respecting Git ignore rules;
- exact Change-local review-control metadata exception for `manifest.yml`, `provenance.yml`, and `review.md`, with rename/lookalike/symlink bypass protection;
- Protocol-aware canonical Contract resolution in validation and Doctor;
- Protocol-aware Codex projection so Protocol 2 provenance/freeze semantics are projected for FAST/STANDARD/FULL without leaking into Protocol 1.

Changed:

- restored Protocol 1 C-026, Specification §25, Review Policy, and `forge/change@1` to their historical pre-CHG-0008 semantics instead of retroactively strengthening Protocol 1;
- Protocol 2 review-subject binding now describes the effective reviewable workspace, not only committed `<subject>..HEAD` history;
- Codex Adapter compatibility interval covers integer Protocols 1 and 2 and now instructs Protocol 2 harnesses to finish reviewable material, ensure the effective workspace is clean, freeze, record provenance, and re-check the freeze before independent Review;
- compatibility documentation explicitly distinguishes Protocol version from artifact schema version and documents the Protocol 1 → 2 breaking boundary.

Security/trust boundary:

- pairwise-distinct execution/context strings are no longer treated as sufficient evidence of independence;
- post-freeze staged, unstaged, untracked, deletion, rename, and path-based metadata bypasses cannot silently alter the Protocol 2 subject presented for Review;
- Forge Core verifies durable provenance linkage and consistency but does not claim self-recorded provenance is cryptographic/external proof; `verified` provenance is reserved for observer-backed evidence.

Migration:

- completed historical Protocol 1 Changes remain unchanged and require no fabricated provenance;
- active Protocol 2 Changes use `forge/change@2` and may not downgrade to `forge/change@1` to bypass the Strict Review Gate.

### Protocol 1 Contract Freeze

Changed:

- stabilized the human-readable Protocol label as `1` while preserving integer Protocol compatibility;
- published Protocol 1 compatibility, breaking-change, and deprecation rules;
- added a portable schema catalog and offline contract coverage for canonical schemas and repository-native artifacts;
- migrated historical artifact structures to their canonical schemas without changing recorded engineering outcomes.

### Foundation

Added:

- Forge Manifesto and Core Architecture;
- Forge Core Protocol, Engineering Contract, FAST/STANDARD/FULL Flows, TDD-first development model, RED → GREEN → REFACTOR lifecycle, Verification, adversarial Strict Review, and canonical Policies/Schemas;
- official Python CLI with `version`, `init`, `validate`, and `doctor`;
- repository-native Change lifecycle, configuration resolution, offline packaged Protocol resources, Distribution Verification, Harness Adapter architecture, Codex Adapter, and deterministic Adapter planning/publication/drift detection.
