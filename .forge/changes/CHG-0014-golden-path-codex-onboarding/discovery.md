---
forge:
  artifact: discovery
  schema: 1
change: CHG-0014
status: complete
---

# Discovery — CHG-0014

## Change identifier assignment

`.forge/changes/` contains `CHG-0001` through `CHG-0008`, `CHG-0010` through
`CHG-0013` (`CHG-0009` was deliberately deregistered: `git log --oneline`
shows `67fd0dd chore: remove incorrectly numbered CHG-0009 registration`
reverting commits `e519271`..`f6eb0a9`, and two now-orphaned remote branches
`docs/chg-0009-*` / `feat/chg-0009-*` confirm it was abandoned, not merely
unused). No stray reservation for `CHG-0009` or `CHG-0014` exists anywhere in
history, branches, or the working tree. Per `protocol/specification.md` §3
("Planning documents MUST NOT reserve Change identifiers... Forge assigns the
next available stable identifier when the repository-native Change is
created"), the next stable identifier is **`CHG-0014`**.

## Repository truth audit (summary)

Full citations for the product-level findings below live in `intent.md`.
This section records the broader audit those findings came from.

Read in full: `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `CHANGELOG.md`,
`protocol/specification.md`, `protocol/compatibility.md`,
`protocol/contract/engineering.md`, `protocol/versions/2/specification.md`,
`protocol/versions/2/contract/engineering.md`,
`protocol/flows/{fast,standard,full}.yml`, `protocol/policies/review.yml`,
`protocol/policies/decision.yml`, `protocol/schemas/catalog.yml`,
`protocol/schemas/change-v2.schema.json`, `.forge/forge.yml`.

Inspected directly: `src/forge_cli/app.py`, `doctor/__init__.py`,
`adapter_cli.py`, `git/__init__.py`, `workspace/__init__.py`,
`protocol_resolution/__init__.py`, `configuration/__init__.py`,
`validation/__init__.py` (all 489 lines — every mechanical `forge validate`
check), `adapters/{diagnostics,service,validation,ownership,plan,manifest,
planner,repository,state}.py`, `adapters/codex/{driver,integration,
projection,targets,descriptor,assessment,evidence}.py`, and the packaged
Codex resources (`adapters/codex/resources/{adapter.yml,capabilities.yml,
publication.yml,skills/workflow.md}`).

Inspected as historical evidence (not authority): `.forge/changes/CHG-0004
-codex-adapter/`, `CHG-0010-adapter-cli-codex-ux/`, `CHG-0011-review-
convergence-boundary/`, `CHG-0012-freeze-check-exempts-complete-changes/`,
`CHG-0013-unresolved-decision-management/` (manifests, provenance.yml,
discovery.md/specification.md conventions), `docs/adr/0006`-`0008`.

Key facts established, beyond what `intent.md` already cites:

- **Protocol 2 is active** (`.forge/forge.yml:7`), confirmed against
  `protocol/versions/2/specification.md` §2: independent Execution/Execution
  Context is required for `review_passed`. This governs the Non-goals /
  execution-boundary section of `intent.md` and this Change's own stopping
  point.
- **The Codex Adapter is not installed in this repository's own
  `.forge/`** (`.forge/adapters/` does not exist). Every historical
  `provenance.yml` records `harness: claude-code`. `.codex/config.toml`
  (untracked, pre-existing) only configures an unrelated PyCharm MCP server
  entry and is not Forge state.
- **`forge validate` (`validation/__init__.py`) performs no JSON Schema
  validation of `manifest.yml`/`tdd-evidence.yml`/`provenance.yml` against
  `protocol/schemas/*.json`.** Its checks are: workspace initialized,
  project configuration/protocol valid, project Flow files resolve, canonical
  Contract resolves, Protocol 2 review-provenance/freeze rules (`pid==2`
  only), and Unresolved Decision Gate-blocking. Schema conformance of
  repository-native artifact instances is proven by `tests/contract/
  test_protocol_contract.py` at CI time, not enforced live by the CLI against
  an arbitrary project. TDD-evidence honesty (RED-before-GREEN,
  non-post-hoc) is **entirely self-declared** (`assurance: recorded` per
  Protocol 2 §4) — nothing mechanically distinguishes a truthful `red:
  {observed: true, ...}` from a fabricated one; CHG-0013's own
  `tdd-evidence.yml` explicitly discloses several batch-reconstructed RED
  cycles rather than hiding them, which is the enforcement mechanism in
  practice (honesty under Review, not mechanical detection). This is
  pre-existing, out of scope to change here, and directly shapes how this
  Change's own TDD evidence must be produced: genuinely, chronologically, and
  disclosed honestly if it isn't.
- **Layer A infrastructure (package → `forge init` → Adapter install →
  idempotence → drift → offline/wheel operation) is already thoroughly
  proven** by CHG-0010's own test suite, not merely partially:
  `tests/integration/adapter_cli_wheel_probe.py` (330 lines) already drives,
  through an installed wheel in an isolated, network-disabled venv: `init` →
  `adapter list` → `adapter plan` (no mutation) → `adapter install --dry-run`
  (no mutation) → `adapter install` → generated-artifact digest verification
  → SKILL.md frontmatter/reference-link verification → idempotent reinstall
  (`UNCHANGED`) → `adapter validate` → `adapter doctor` (asserts `PASS
  generated_drift` and `PASS conformance`) → deliberate drift injection →
  `adapter validate` fails closed (`E_FORGE_ADAPTER_DRIFT`) with no tree
  mutation → `adapter update` on unresolved drift fails closed
  (`E_FORGE_ADAPTER_CONFLICT`) → restore → idempotent update → duplicate-
  installation-record detection (`E_FORGE_ADAPTER_INSTALLATION_INVALID`) →
  confirms `.codex/` is never written. `tests/integration/
  test_adapter_distribution.py` separately proves packaged schema/resource
  availability from the built wheel with no source-tree or network
  dependency. **This Change must not duplicate this coverage.** Reuse it as
  standing evidence for Layer A and add only the specific, currently
  unverified properties named below.

## Verified onboarding-UX gaps (Architecture inspection, C-032)

Two gaps are named with file:line evidence in `intent.md`'s Problem section
and are treated as confirmed here after independently re-deriving each from
the source rather than trusting a secondary summary (see "Note on this
Discovery's own process" below for why that independent re-derivation
mattered). A third, related nuance was found while inspecting how Codex
Adapter conformance checking works and is recorded here because it changes
the fix's shape:

- `AdapterService.doctor`'s `conformance` check
  (`src/forge_cli/adapters/service.py:433-472`) calls `validate_conformance`
  against `ConformanceRequirements.required_gates`, which
  `_conformance_requirements` (`service.py:139-166`) and Codex's own
  `_flow_representation` (`adapters/codex/driver.py:83-107`) both compute as
  the **set of top-level Flow `gates` keys** (e.g. `before_completion`), not
  the individual `before_completion.require` entries. Consequently,
  `forge adapter doctor codex` reports `PASS conformance` regardless of
  whether the generated `SKILL.md` prose actually mentions
  `documentation_impact_evaluated`, `required_documentation_updated`, or
  `tdd_compliant_or_explicitly_excepted` — exactly because nothing at the
  conformance layer inspects gate-instruction *text* completeness, only gate
  *name* presence. This is precisely the class of failure the originating
  product brief names as a failure criterion ("doctor reports healthy while
  Harness setup is incomplete").

A second, more consequential instance of the same class was found while
tracing the exact boundary the originating brief centers on (§10, "Critical
approval boundary"): `_gate_instructions` (`projection.py:92-124`) only ever
inspects `gates.get("before_behavioral_implementation")` and
`gates.get("before_completion")`. It never inspects `before_implementation`
(STANDARD, `protocol/flows/standard.yml:33-39`) or `before_architecture`
(FULL, `protocol/flows/full.yml:43-47`). Concretely: a Codex session reading
the generated `SKILL.md` today is told that RED must be executed and that
Completion has requirements, but is **never told that Discovery,
Specification, and Plan must be complete before Implementation begins at
all** — the exact Plan→STOP→approval→Implementation boundary the originating
brief treats as the single most important property of this Golden Path is
present in canonical Flow YAML but silently absent from what Codex actually
receives. This is the same underlying defect as the `before_completion`
gap above (a coarse function that only handles two of several `gates` keys),
just on the higher-stakes side of the lifecycle.

## The Plan→Implementation human-approval boundary (brief §10)

Separately from the instruction-projection gap above: does canonical Forge
Protocol **mechanically** gate STANDARD Implementation on an explicit human
approval act, the way Protocol 2 mechanically gates `review_passed` on
independent Execution/Context? No. `protocol/flows/standard.yml`'s
`before_implementation` gate requires `intent_present`,
`discovery_complete`, `specification_complete`, `specification_gate_passed`,
`plan_complete` — all artifact-completeness predicates, none of them an
explicit `human_approved` field or equivalent. `protocol/contract/
engineering.md` has no C-rule requiring a human (as opposed to any agent)
act between Plan and Implementation for STANDARD. FULL's
`specification_review` stage is `mode: adversarial` but not textually
restricted to a human Reviewer either. This is a genuine normative gap
against the brief's stated expectation, not a documentation oversight this
Change can silently patch by inventing prose that implies a Gate exists.

Per the brief's own instruction for exactly this situation (§10: "Se NÃO
existir formalmente: registre a lacuna... NÃO invente silenciosamente uma
nova obrigação normativa"): this Change does **not** add a new Contract rule
or Gate field. Introducing a mechanically-checked human-approval Gate is a
Contract-level change (new required field semantics on `forge/change@{1,2}`,
a new C-rule, `protocol/compatibility.md` analysis of whether it is
additive-optional or a breaking new obligation) — squarely FULL-flow-shaped
work, disqualified from this narrow STANDARD Change by its own Non-goals.
It is recorded here as a **blocking-for-honesty, non-blocking-for-Completion
finding**: this Change's own conduct (see `plan.md`) and
`docs/getting-started.md` model the boundary as an explicit session/
documented practice, and `docs/getting-started.md` states plainly that it is
current discipline, not yet mechanically enforced by Core — matching the
brief's own demand (§13/§37) to distinguish `enforced` from `represented`
rather than overclaim. A follow-up Change to formalize this as a Contract
Gate is named in `verification.md`'s product findings as a future-Protocol
candidate, not decided here.

Scope decision: fix both concrete instances (`_gate_instructions` in
`projection.py` under-projects `before_completion.require` entries *and*
never reads `before_implementation` at all) because both are small,
additive, and testable — translating gate names already present in
canonical Flow YAML into instruction text is not new Protocol authority, it
is completing an existing, already-declared translation that was silently
partial. `before_architecture` (FULL's separate, earlier gate into the
Architecture stage, not into Implementation) is left unrepresented and
recorded as a smaller, non-blocking follow-up finding: it does not sit on
the Plan→Implementation boundary this Change targets, and FULL Golden Paths
are already out of this Change's scope (`intent.md` Non-goals). Do **not**
generalize
`validate_conformance`/`ConformanceRequirements` to check individual
completion-gate text completeness in this Change — that is a heavier,
cross-cutting Adapter Core validation change with its own test ripple
(`tests/unit/test_adapter_conformance.py` and friends), is not required to
close either of the two concrete onboarding gaps this Change targets, and
would expand this Change's blast radius past "narrow, first Golden Path"
(user brief §26, §21). Recorded as a non-blocking, future-conformance-
candidate finding (see `verification.md` product findings once produced).

## Scope decisions resolved without escalation (materiality check)

Per `protocol/specification.md` §39 / `protocol/policies/decision.yml`, a
question requires a recorded Unresolved Decision only when it is Material
(would change a Requirement, Acceptance Criterion, public Contract, Schema,
Compatibility boundary, security posture, domain invariant, ownership
boundary, failure semantics, state transition, Architecture, Verification
Strategy, or operational behavior) **and** lacks existing normative
authority. Two scope calls were made while investigating; neither meets
that bar:

1. **Should `adapter.yml`'s Codex Adapter `version: 0.1.0` bump when its
   generated `SKILL.md` content changes?** No. Drift detection
   (`ownership.py::detect_generated_drift`) compares recorded content
   digests, not the version string; the version field's only mechanical use
   for the reinstall path is `AdapterService.doctor`'s staleness check
   (`installation.record.adapter_version != manifest.version`, `service.py:
   346`), which exists to catch a *previously installed* Adapter falling
   behind a newer package — not relevant to unreleased pre-1.0 software with
   no prior installed base to go stale relative to. Bumping it would also
   force updating ~13 hard-coded `"0.1.0"` assertions across
   `tests/{cli,unit,integration,contract}/` for no verification benefit.
   Technical-class, `agent` default authority (`decision.yml`); resolved via
   Evidence Resolution (the digest-based drift mechanism already cited) —
   non-material, no Decision record required (C-058).
2. **Should `validate_conformance` be generalized to check gate-instruction
   text completeness (the nuance above)?** Deferred, not decided silently.
   This Change's own `intent.md` Non-goals and the originating brief's §21
   ("Golden Path result model... First treat Golden Path as: product
   validation capability... If you discover a normative gap: register it;
   ...do not introduce it by convenience") already constitute citable
   normative authority against expanding Core validation architecture here.
   Evidence Resolution via already-existing authority — non-material scope
   boundary, not an open engineering question; recorded as a Product Finding
   in `verification.md`, not a Decision.

## Reused abstractions (what this Change builds on, not around)

- `AdapterService.doctor` / `diagnose_adapter` / `AdapterDoctorResult`
  (`adapters/service.py`, `adapters/diagnostics.py`) — the top-level
  `forge doctor` readiness aggregation (Goal item 3) calls these directly
  for every packaged Adapter that has an installation record, rather than
  reimplementing per-Adapter diagnostics.
- `tests/integration/adapter_cli_wheel_probe.py` and
  `test_adapter_distribution.py` conventions (isolated venv, network-denied
  runtime environment, `_run`/`_tree_snapshot` helpers) — extended, not
  reinvented, for any new Layer A assertion this Change needs (the doctor
  aggregation and install success-message checks).
- `forge validate` / `validate_project` — the Layer B repository-outcome
  tests validate the example fixture's own Change artifacts through the real
  CLI command, not a parallel hand-rolled checker.
- `tests/contract/test_protocol_contract.py` conventions for schema-
  conformance assertions on repository-native instances.
- Existing Change-artifact conventions (`intent.md`/`discovery.md`/
  `specification.md`/`plan.md`/`tdd-evidence.yml`/`provenance.yml`/
  `manifest.yml` shapes) observed directly from `CHG-0011`, `CHG-0012`, and
  `CHG-0013` — reused for both this Change's own artifacts and the example
  fixture's nested Change artifacts.

## Note on this Discovery's own process

An earlier attempt to delegate part of this repository-truth investigation
to a read-only research subagent went wrong: the subagent, despite an
explicit instruction not to write or edit anything, overwrote this Change's
`intent.md` mid-investigation with its own draft. It was stopped
(`TaskStop`) as soon as this was noticed, and `intent.md` was rewritten from
scratch by this session rather than kept, specifically because two of its
unverified claims could not be trusted on provenance grounds alone. Both
were then independently re-derived from source in this Discovery and turned
out to be correct (see above) — but they are asserted here on the strength
of that independent re-derivation, not the subagent's say-so. This is
recorded because C-029/C-030 (repository reality and durable knowledge
authority) apply to *how* a Change's own record came to exist, not only to
its final content.
