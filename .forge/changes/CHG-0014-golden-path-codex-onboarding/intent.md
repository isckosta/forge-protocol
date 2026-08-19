---
forge:
  artifact: intent
  schema: 1
change: CHG-0014
status: complete
---

# Intent — Golden Path Baseline and Codex Onboarding Validation

## Problem

Forge already has a Core Protocol, an Engineering Contract, three canonical
Flows, a bootstrap CLI, a generic Harness Adapter Core, and a concrete Codex
Adapter (`README.md:13-115`). Each has been proven independently, largely
through FULL-flow dogfooded Changes (`CHG-0001`-`CHG-0013`; every historical
Change in `.forge/changes/` is FAST or FULL, never STANDARD). None of them
has been proven **together**, end to end, from the perspective of a developer
who did not build Forge.

`ROADMAP.md:183-234` already names this gap ("End-to-End Examples & External
Project Validation", with a "golden path" of exactly this shape) and
`ROADMAP.md:407-428` makes it the project's stated primary v1 success metric.
It has not been executed: `docs/getting-started.md` does not exist,
`examples/` contains only a placeholder `README.md` (`examples/README.md`),
and nothing in `tests/` drives Forge through a full install-to-Change
lifecycle as one reproducible scenario.

This Change's own repository-truth audit also found two small, concrete,
independently verified onboarding-UX defects that sit directly on the
CLI-to-Codex hand-off this Golden Path is meant to validate:

1. `forge adapter install codex` (`src/forge_cli/adapter_cli.py:201-221`)
   prints only its plan's operation lines on a real install and otherwise
   only "No changes required."; there is no success/next-step confirmation
   comparable to `forge init`'s `Forge initialized at {path}`. A user who
   just ran the install has no CLI-emitted answer to "what do I do now?" —
   exactly the gap `ROADMAP.md`'s "Adapter CLI & Codex Installation UX"
   exit criteria ("onboarding requires no manual prompt copying") assumes is
   closed but the code does not actually close.
2. The generated Codex `SKILL.md` gate instructions
   (`src/forge_cli/adapters/codex/projection.py::_gate_instructions`, lines
   92-124) only translate five of every Flow's `before_completion.require`
   entries (`verification_passed`, `review_passed`,
   `blocking_review_threads_resolved`, plus the two RED checks from
   `before_behavioral_implementation`). `documentation_impact_evaluated`,
   `required_documentation_updated`, and `tdd_compliant_or_explicitly_excepted`
   — present in `protocol/flows/fast.yml`, `standard.yml`, and `full.yml`
   alike — are silently absent from what Codex ever sees. A Codex session
   following only the generated skill has no instruction that Documentation
   Impact evaluation (C-028, a universal Contract obligation) is required at
   all.

Neither defect blocks the Adapter's existing automated coverage (which never
asserts a success message exists, and never asserts on Documentation/TDD-
exception gate text), which is exactly why they survived undetected: nothing
in the current test suite treats "the user knows what to do next" or
"Codex is told the whole gate set" as a property worth checking. That absence
is itself evidence for why a Golden Path — validating the composition, not
just each part — is a distinct, needed capability.

Protocol correctness and product usability are different properties. Forge
has invested heavily in the first. This Change is the first Change whose
Intent is explicitly the second.

## Goal

Establish a canonical, reproducible, evidence-backed Golden Path: install
Forge, initialize a repository, install/configure the Codex Adapter, confirm
readiness, open Codex, request one small behavioral Change in natural
language, and carry it through Forge's real STANDARD lifecycle — Discovery,
Specification, Plan, an explicit human-approval boundary, TDD, Verification,
Strict Review, and Completion — without the developer copying an internal
prompt, editing Adapter internals, or reconstructing `protocol/` from
scratch.

Concretely, this Change must:

1. Produce a short, accurate `docs/getting-started.md` sufficient on its own
   to complete the golden path, without requiring `ARCHITECTURE.md`,
   `protocol/specification.md`, `protocol/contract/*`, Adapter internals, or
   Change schemas to be read first.
2. Produce one small, self-contained example fixture with a real RED-capable
   scenario (`examples/golden-path-standard/`).
3. Close the two verified onboarding-UX gaps above generically (in
   `adapter_cli.py` and `projection.py`, not inside Golden-Path-specific
   code), and extend `forge doctor` to aggregate installed-Adapter
   diagnostics so it can answer "is this repository ready to begin a Forge
   Change through Codex?" — reusing `AdapterService.doctor`
   (`src/forge_cli/adapters/service.py:223`) rather than inventing new
   readiness logic.
4. Produce deterministic, automated tests for the parts of the golden path
   that are mechanically checkable (Layer A infrastructure, Layer B
   repository outcome), reusing existing test infrastructure — the wheel/
   subprocess probes already proven by CHG-0010
   (`tests/integration/adapter_cli_wheel_probe.py`,
   `tests/integration/test_adapter_distribution.py`) — rather than building a
   parallel harness.
5. Define an explicit, behaviorally specified manual acceptance procedure for
   the one layer that cannot be mechanically checked from this session or CI:
   whether a real Codex session, given the installed projection, actually
   picks up Forge semantics and stops at the correct human-approval boundary
   before Implementation. This session has no Codex tool access and cannot
   execute that step itself.
6. Record product findings honestly, separating what is blocking for this
   Change from what is deferred follow-up.

## Non-goals

- This is not a benchmark platform, an LLM judge, or a conformance suite. One
  canonical scenario, one Harness (Codex), one primary Flow (STANDARD).
- This does not add lifecycle CLI commands (`forge specify`, `forge
  implement`, `forge verify`, `forge review`). Chat remains the lifecycle
  runtime (`README.md:69`, `ROADMAP.md:33`).
- This does not introduce a new Protocol artifact, schema suffix, or integer
  Protocol identifier. If Discovery surfaces a normative gap that truly
  requires one, it is recorded and deferred to its own Change, not folded in
  here for convenience (`protocol/compatibility.md`, C-046).
- This does not attempt a Claude Code Adapter or any second Harness.
  `ROADMAP.md:236` already scopes that to its own future Change ("Second
  Harness Adapter").
- This does not implement Interaction Language Resolution
  (`ROADMAP.md:143`), even though it sits earlier in the Roadmap's
  recommended execution order; this Change was explicitly requested now and
  is independent of it.
- This does not install the Codex Adapter into `forge-protocol`'s own
  `.forge/` workspace as a side effect. This repository's own dogfooding uses
  the `claude-code` harness (every `provenance.yml` under `.forge/changes/`
  records `harness: claude-code`); the Golden Path's subject is a separate,
  disposable example fixture, not this repository's own governance.
- This session does not perform this Change's own Strict Review. Protocol 2
  (`.forge/forge.yml:7`, `protocol/versions/2/specification.md` §2: "A Strict
  Review that can satisfy `review_passed` MUST run in an Execution and
  Execution Context distinct from the Implementation or Resolution that
  produced the review subject. Role switching inside one context is
  self-review.") makes independent self-review impossible by construction.
  This Change stops at Verification, prepares the frozen review subject, and
  hands off to an independent Execution/Context for Strict Review. See the
  final message of this session for the exact next step.

## Flow

STANDARD. Semantic-impact analysis against `protocol/specification.md` §6,
`protocol/flows/fast.yml`, and `protocol/flows/full.yml`:

- Not FAST: FAST's `classification.disqualifiers`
  (`protocol/flows/fast.yml:19-27`) explicitly exclude `new_integration` and
  `significant_cross_module_change`. This Change coordinates a new onboarding
  document, a new example fixture, a new test surface, and small but
  coordinated changes across three modules (`forge doctor`, the Adapter CLI's
  install messaging, and the Codex Adapter's projection content) — genuinely
  cross-module even though each individual edit is small.
- Not FULL: FULL is reserved for architecture, security, authorization,
  integrations, persistence, and public-contract-changing work
  (`protocol/flows/full.yml:1-9`; `ARCHITECTURE.md` §28 non-goals). Nothing
  here changes a Protocol schema, a Contract invariant, or an Adapter
  manifest capability, and no new architectural pattern is introduced: every
  code change identified above completes already-declared behavior that was
  silently incomplete (a missing CLI confirmation message, a partially
  projected gate set, an unaggregated diagnostic) rather than adding a new
  abstraction. C-032 ("existing Architecture must be inspected") is satisfied
  by this Discovery without requiring FULL's mandatory Architecture stage.
- STANDARD fits: "ordinary behavioral Changes and small-to-medium features"
  (`protocol/flows/standard.yml:6`) — exactly this Change's shape, and the
  Flow the originating prompt requested absent contrary evidence. It is also,
  deliberately, the first Change in this repository's history to exercise
  STANDARD end to end (every prior dogfooded Change was FAST or FULL — see
  above), which is itself Golden-Path-relevant: if STANDARD's own artifact
  set cannot be produced cleanly by dogfooding, that is a finding in its own
  right, not an incidental side effect.
