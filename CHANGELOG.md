# Changelog

All notable Forge changes will be documented here.

CLI releases follow [PEP 440](https://peps.python.org/pep-0440/) (see
`RELEASING.md`). Protocol versions are tracked independently
(`protocol/compatibility.md`). A released version's heading looks like
`## [0.1.0a1] - YYYY-MM-DD`; entries accumulate under `## Unreleased`
until then.

## Unreleased

### Verification Layout, Coverage, and Traceability

Updated newly generated `verification.md` (FAST/STANDARD/FULL) with an
Acceptance Coverage table (`Acceptance | Requirement | Result |
Evidence`), a conditional Requirement Coverage table, a distinct Manual
Evidence section, guidance to reference `TDD-xxx` cycles by id instead
of renarrating RED/GREEN, and Conclusion guidance against implying
Completion under FAIL/SKIPPED. `Result` remains the first substantive
section, restricted to `PASS`/`FAIL`/`SKIPPED`/`NOT APPLICABLE`.
Historical `verification.md` files, Schemas, Protocol integers, and
`forge validate` semantics remain unchanged.

Also fixes two real defects found while remediating CHG-0036 through
CHG-0039's stacked PRs: the Merge Readiness gate's review-subject
staleness check (`MR-015`) diffed the entire repository instead of the
Change's own directory, making it mechanically impossible for two
sequentially stacked Changes to both stay non-stale; and Flow stages
were loaded from the wrong YAML root, so the required-artifact-per-stage
check (`MR-009`) never fired for any Change.

### Tasks Layout, Plan Grouping, and Traceability

Updated newly generated `tasks.md` (FULL) with an Overview, an Execution
section grouping the `T-xxx` checklist under the Plan item each group
executes, and compact optional per-Task traceability metadata
(`Plan`/`Requirements`/`Stories`/`Test Design`, using the `TDD-xxx`
convention). Historical `tasks.md` files, `plan.md`, `test-strategy.md`,
Schemas, Protocol integers, and `forge validate` semantics remain
unchanged.

### Test Design Verification Contract

Updated newly generated `test-design.md` (FAST/STANDARD) with an Overview,
Test Strategy, Coverage Map, self-contained `TD-xxx` scenarios (Purpose,
Preconditions, Scenario, Evidence, Failure Condition, Boundary), a
Requirement Coverage table, Coverage Gaps, and a Test Design Gate,
distinguishing automated scenarios from Manual Acceptance and defining
valid RED. `test-strategy.md` (FULL), historical `test-design.md` files,
Schemas, Protocol integers, and `forge validate` semantics remain
unchanged.

### Specification Layout and User Story Traceability

Updated newly generated Specifications with a clearer engineering-contract
layout, optional User Stories, local Acceptance content, and traceability
guidance. Historical Specifications, Schemas, Protocol integers, and
`forge validate` semantics remain unchanged.

### Merge Readiness Gate

Added a separate `forge change merge-check` evaluation with deterministic
revision/provenance diagnostics, material-change policy, Plan content-digest
binding, and a GitHub Actions required-check workflow. `forge validate`
retains its existing validity semantics, and release provenance remains
independent.

## [0.1.0b1] - 2026-08-23

### Structured Intent Artifacts

Added:

- a structured human-facing `intent.md` layout with Change identity,
  executive intent, Overview metadata, Problem, Goal, Scope, Out of Scope,
  and Success Criteria;
- conditional guidance for Business Impact, behavior comparisons, business
  rules, expected outcomes, operational boundaries, and references;
- matching Intent authoring guidance for Codex and Claude Code Adapters;
- representative business and technical Intent examples.

Changed:

- preserved `schema: 1`, YAML front matter, historical artifacts, and Forge
  lifecycle semantics while improving Intent presentation and scanability.

### Change Scaffolding CLI

Added `forge change new <slug>` with active-Flow-aware artifact generation,
plan-before-mutation output, collision-safe publication, rollback, and offline
installed-wheel support. `--non-behavioral` is available for Changes that do
not modify behavior.

### Adapter Reference Schema Projection

Added:

- Both Harness Adapters (Codex, Claude Code) now project a new
  `references/decision-rules.md` (`skills/forge/references/decision-rules.md`
  for Claude Code), documenting the `decisions[]` structural rules
  `forge validate` actually enforces (`class`/`materiality`/`status`/
  `authority`/`resolved_via` enums, `class` -> valid `owning_artifact`,
  `class` -> authority floor) -- rendered directly from
  `forge_cli.validation`'s own constants, never a hand-duplicated copy,
  so it cannot drift from what `forge validate` really checks.

Changed:

- `forge validate`'s invalid-`resolved_via` error message now states the
  expected values, matching the existing `owning_artifact` message's
  convention.

`CHG-0021`, prompted by the first real external validation of Forge
outside this repository (a Laravel/PHP project's `CHG-0001`), whose
after-action report found these exact two rules undiscoverable from an
Adapter installation alone.

## [0.1.0a2] - 2026-08-20

### README accuracy

Changed:

- `README.md` updated to reflect the real `v0.1.0a1` release: `pip
  install forge-protocol` as the primary installation path (source
  install kept as a secondary "Development installation" section);
  `## Status` corrected from Protocol `1`/vague pre-release wording to
  Protocol `2` and the actual published version; a new "Claude Code
  Adapter" section added alongside the existing "Codex Adapter" one,
  since only one of the two real Harness Adapters was previously
  documented; the examples pointer now names `examples/README.md`'s
  five-category mapping instead of a single directory; Dogfooding's
  closing line now credits `CHG-0018` for the second Harness Adapter.

No code change. This release exists because PyPI project metadata
(including the README, embedded via `pyproject.toml`'s `readme =
"README.md"`) is immutable per version -- `v0.1.0a1` could not be
edited in place.

## [0.1.0a1] - 2026-08-20

### End-to-End Examples (Curated Real Evidence)

Added:

- `examples/strict-review-remediation/README.md`: a guided tour of
  `CHG-0016`'s real Strict Review `REQUEST CHANGES` (1 BLOCKER, 2 MAJOR,
  6 MINOR, 3 OBSERVATION) → Resolution → PASS cycle;
- `examples/full-feature/README.md`: a guided tour of `CHG-0018`'s real
  FULL-flow evidence (two Core-leak fixes, a new Harness Adapter, a
  genuinely independent dogfooded bug-catch);
- addenda on `examples/golden-path-standard/README.md` and
  `examples/golden-path-claude-code/README.md` naming which additional
  ROADMAP-named example categories each already satisfies;
- `examples/README.md` rewritten with a mapping table from all five
  ROADMAP-named example categories to their real evidence.

No fabricated scenario was introduced — every commit hash, Finding ID,
and quoted excerpt in the two new READMEs cites this repository's own
real history, independently checked against `git show`/file content
both by Implementation and by a fresh, independent Strict Review
subagent. The External validation matrix remains open (see
`ROADMAP.md`).

### Release Engineering & v1 Release Candidate (Infrastructure)

Added:

- `[tool.hatch.version]` dynamic version sourcing: `pyproject.toml` no
  longer declares its own static `version`; it reads `CLI_VERSION` out
  of `src/forge_cli/version.py` via a regex pattern, so the CLI/package
  version has one source of truth instead of two independently
  hardcoded strings;
- `pyproject.toml` gains `authors`, `[project.urls]`
  (Homepage/Repository/Issues/Changelog), `classifiers`, and `keywords`
  — conventional PyPI-listing metadata that was previously entirely
  absent;
- `forge migrate` / `forge migrate --check`: a new repository-native
  migration mechanism recognizing exactly one schema family today,
  `forge/execution-provenance@1` → `@2` (a byte-identical superset for
  any record whose `role` isn't `delegated_task`), plus a new
  non-blocking `forge doctor` advisory (`migration_available`) when a
  candidate exists;
- Contract rule `C-075`: a migration MUST NOT fabricate, infer, or
  reconstruct data absent from the instance being migrated, generalizing
  `CHG-0007`'s own one-off truth-preserving migration discipline into a
  durable rule now that `forge migrate` is a reusable mechanism;
- `.github/workflows/publish.yml`: builds wheel and sdist, smoke-tests
  both offline, and publishes to PyPI via OIDC trusted publishing (no
  stored token) — triggers only on a published GitHub Release, which
  does not exist yet and which this Change does not create;
- `RELEASING.md`: the PEP 440 version scheme and the manual release
  checklist a human will follow later.

Fixed:

- `.github/workflows/verification.yml` no longer triggers on two stale,
  deleted branch names; it now also builds and smoke-tests an sdist
  install alongside the pre-existing wheel-only check;
- `ROADMAP.md`'s release-progression sketch corrected from hyphenated
  pre-release strings (`0.1.0-alpha.1`) to valid PEP 440
  (`0.1.0a1`/`0.1.0b1`/`1.0.0rc1`).

Known limitation (accepted, documented deferral — see
`docs/adr/0017-release-engineering-infrastructure.md`):

- `forge migrate` does not (and, per `compatibility.md`, must not)
  migrate `forge/change@1`; `forge/adapter-installation@1` is deferred
  pending a real installed-Adapter case to drive a design for its
  non-derivable `publication_root` field. No release has actually been
  cut — this Change is infrastructure only.

### Second Harness Adapter (Claude Code)

Added:

- `src/forge_cli/adapters/claude_code/`, Forge's second concrete Harness
  Adapter, registered alongside the existing Codex Adapter in
  `adapters/packaged.py`. `adapter.yml`/`capabilities.yml` declare a
  materially richer, dated (2026-08-19, `code.claude.com`) capability
  profile than Codex's — all six of `persistent_instructions`, `commands`,
  `skills`, `hooks`, `agent_roles`, and `generated_files` are `supported`,
  versus Codex's `skills`/`generated_files` only;
- three real projection mechanisms, all `forge_owned` under one shared
  publication root (`.claude`): a Skill (`.claude/skills/forge/SKILL.md` +
  `references/*`, content-parallel to Codex's own projection, including
  the Protocol 2 Reviewer/Resolver-independence guidance), a CLAUDE.md
  pointer (`.claude/CLAUDE.md`, short, references the Skill rather than
  restating it), and an illustrative `PreToolUse` enforcement hook
  (declared in the Skill's own frontmatter — no separate
  `.claude/settings.json` merge needed) that denies in-place shell
  mutation of `.forge/changes/*/{manifest.yml,provenance.yml,review.md}`
  without blocking ordinary `git add`/`git commit`/`cat`/`ls`/`grep` of
  the same paths — the one mechanism Codex (`hooks: false`) structurally
  cannot offer;
- Contract rule `C-074`: a Change introducing a new Harness Adapter MUST
  pass the shared conformance test suite before Completion;
- a new shared, Harness-agnostic conformance test suite
  (`tests/unit/test_adapter_driver_conformance.py`, parametrized over
  both concrete Drivers) — the literal ROADMAP exit criterion "both
  Adapters pass shared conformance tests", not previously built for even
  one Adapter;
- `examples/golden-path-claude-code/` and
  `tests/golden_path/test_golden_path_claude_code.py` (Layer A/B, mirrors
  `golden-path-standard`'s proven shape) plus genuine, executed Layer C
  evidence — a real, independent `claude -p` session, running cold
  against a scratch repository with this Adapter installed, autonomously
  recognized the repository as Forge-governed, classified a FAST Flow,
  performed a real RED→GREEN TDD cycle, produced repository-native Change
  artifacts, and correctly identified that Strict Review requires a
  separate Execution/Context — see this Change's own `verification.md`.

Fixed (generic Adapter Core, both pre-dating this Change):

- a `.codex` reserved-path rule hardcoded in the generic
  `adapters/configuration.py` and
  `protocol/schemas/adapter-configuration.schema.json` (whose regex also
  had a latent unescaped-`.` bug, matching `Xcodex` too) — not scoped to
  Codex at all. Removed from the generic Core; Codex's own
  `codex/targets.py` keeps its own, now-sole, correctly-scoped copy;
- `assess_invariant`/`to_generic_limitation` (100% generic invariant-
  assessment logic, zero Codex references) relocated from
  `codex/assessment.py` to a new `adapters/assessment.py`, so a second
  Adapter does not need to import across Adapter packages.

### Interaction Language Resolution

Added:

- an optional, additive `interaction.language` field on `forge/project@1`
  (`protocol/schemas/project.schema.json`), accepting the sentinel `auto`
  or a BCP-47-shaped lowercase-language[-REGION] code — absent behaves
  identically to `auto`;
- Contract rules C-070 (canonical identifiers stay invariant regardless
  of interaction language), C-071 (Gate semantics MUST NOT vary by
  interaction language), C-072 (deterministic project configuration
  takes precedence over any Harness-observed language signal), and C-073
  (Harness honesty: an Adapter projecting this guidance MUST NOT claim to
  guarantee the Harness's actual output language) — all added to both
  `protocol/contract/engineering.md` and
  `protocol/versions/2/contract/engineering.md`; neither C-072 nor C-073
  is validated by `forge validate`, matching C-067's own disclaimer for a
  different concern;
- `protocol/specification.md` §42, defining a three-level precedence
  chain (explicit project configuration → Harness-observed chat hint →
  English fallback) — a deliberate reduction from `ROADMAP.md`'s original
  four-level sketch; the repository/context-language heuristic level is
  explicitly deferred (`docs/adr/0015-interaction-language-resolution.md`,
  DEC-001, human decision) rather than built as a non-deterministic
  mechanism inside Core;
- the Codex Adapter now projects the effective interaction-language
  instruction as one interpolated `SKILL.md` line, reusing the same
  generic `AdapterProjectionContext` → `CodexProjectionInput` pipeline
  `CHG-0016` established (`interaction_language: str = ""`, an additive
  default field at every layer) — unlike `CHG-0016`'s
  `artifact_structure_content`, this is a small per-project scalar, not a
  static document, so it is rendered inline rather than as a new
  `references/*.md` resource file (DEC-002, `architecture.md`).

Known limitation (accepted, documented deferral — see DEC-001,
`docs/adr/0015-interaction-language-resolution.md`):

- Forge Core implements no repository/context-content language-detection
  heuristic; a project without an explicit `interaction.language` relies
  entirely on the Harness's own chat-observed language, falling back to
  English if the Harness has none.

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
