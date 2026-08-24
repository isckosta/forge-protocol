---
forge:
  artifact: specification
  schema: 1
change: CHG-0045
status: pending
---

# CHG-0045 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0045 |
| **Flow** | FULL |
| **Status** | Draft |

## Summary

The Claude Code Agent Adapter's generator
(`src/forge_cli/adapters/claude_code/projection.py`) already composes
`SKILL.md` from real Core sources, but its own code duplicates the
Reviewer/Resolver independence text once per effective Flow and,
independently, the Codex Adapter (`codex/projection.py`) hand-maintains a
second, unlinked copy of the same text. This Change makes both Adapters
render that text — and the CHG-0025/C-077 Plan Decision sentence — from
one shared source, restructures the generated `SKILL.md` around
Authority/Bootstrap/Operating-Model/Evidence/Human-Authority/Review-
Independence/Completion sections instead of one block per Flow, adds an
explicit bootstrap instruction to check the Adapter's own already-existing
digest-based drift record (`installation.yml`, `forge doctor`) before
trusting `references/*`, and widens the existing mechanical guard's tool
coverage from `Bash`-only to also match `Edit`/`Write` against the same
three protected paths — without changing what any Contract rule, Flow
gate, or Review-independence requirement means.

## Classification

**Flow: FULL.** Per `protocol/flows/full.yml`'s own description ("High-
rigor flow for architecture, security, integrations, major domain
behavior... and other high-impact work"), this Change touches: the shared,
harness-agnostic Adapter generation pipeline consumed by every Harness
Adapter (integration surface); the mechanical `PreToolUse` guard
(security-adjacent, C-064–C-066); and the projected representation of
Contract/Review-independence semantics that every agent operating this
repository reads before doing anything else (major domain behavior for a
protocol whose product *is* governing agent behavior). C-044 ("Forge
dogfoods Forge") and F-001 additionally require this Change to use Forge
FULL rigor because it is material development of Forge itself. This
classification is fixed at Intent per the governing prompt's explicit
instruction and is not discretionary for this Change.

## Self-Hosting Boundary (recorded per governing-prompt Section 2)

The Forge Protocol 2 / FULL Flow / Engineering Contract effective at this
Change's `intent` stage — the `main` commit this branch forked from —
governs this Change's own gates, TDD obligations, Strict Review
independence requirements, and Plan/Implementation boundary (C-077),
in full, for the entire lifecycle of CHG-0045. This reuses, rather than
restates, the `forge` skill's own existing instruction: *"Repository-
native Forge state remains authoritative. Use the effective Flow and
Engineering Contract references in this skill as derived, repository-
local representations; do not redefine their lifecycle here."* No
`SKILL.md`, reference, hook, or documentation this Change produces —
including a regenerated `SKILL.md` installed mid-Change by a future
`forge adapter update` — retroactively changes this Change's own Flow,
Gate requirements, Review-independence requirements, or Plan Decision
authority. If this Change's own Implementation causes the installed
Adapter to be regenerated before this Change reaches `complete`, this
Change's own governance continues to be evaluated against the Forge state
recorded at its `intent` stage, not the newly generated one.

## User Stories

### US-001 · Agent bootstrap resolves effective state before mutating

As an agent operating in a Forge-governed repository, I want to resolve
the effective Change, Flow, Gate requirements, and Adapter drift state
before making any repository-mutating tool call, so that I never cross a
Gate I have not actually satisfied.

**Acceptance:** AC-001, AC-002.

### US-002 · Human authority is never inferred

As the human operator, I want the agent to stop at the Plan/Implementation
boundary and any other human-authority Gate rather than infer my approval
from artifact status, prior enthusiasm, or conversational continuation, so
that no approval is fabricated.

**Acceptance:** AC-003.

### US-003 · Self-review cannot be recorded as Strict Review

As a maintainer, I want the projected Reviewer/Resolver-independence
requirement to remain complete and singular — not fragmented across three
near-duplicate Flow-specific copies that could individually drift — so
that self-review can never be recorded as Strict Review under any Flow.

**Acceptance:** AC-004, AC-005.

### US-004 · Adapter drift is detected and never silently trusted

As a maintainer, I want an agent that is about to rely on `SKILL.md`'s
`references/*` to first check whether the installed Adapter has drifted
from canonical Core content (using the digest ledger that already exists
in `installation.yml`), so that stale generated content is never treated
as current Forge state.

**Acceptance:** AC-006, AC-007.

### US-005 · Guard coverage is honestly stated and, where reasonable, widened

As a maintainer, I want the mechanical `PreToolUse` guard's real coverage
(which tools, which paths, which activation window) stated accurately,
and widened to cover `Edit`/`Write` mutation of the same three
review-control paths it already protects for `Bash`, so that switching
tools is not a trivial way to bypass a guard whose narrowness is otherwise
undisclosed.

**Acceptance:** AC-008, AC-009.

### US-006 · Worktree-correct resolution

As a developer working inside a Git worktree, I want `forge doctor`,
`forge adapter doctor`, and Adapter drift detection to operate against the
worktree's own effective checkout, not silently against the main
checkout's state, so that diagnostics reflect the repository I am actually
in.

**Acceptance:** AC-010.

### US-007 · Adapter evolution does not require hand-editing every SKILL.md

As a Forge maintainer, I want a Contract, Flow, or Decision Rules change
to propagate to every installed Adapter's generated output through
`forge adapter update` alone, without hand-editing `claude_code/
projection.py` and `codex/projection.py` identically to keep
Reviewer/Resolver-independence or Plan-Decision text in sync, so that
Core and Adapter text cannot silently diverge the way it already has once
in this repository (Discovery, "installed Adapters are currently
drifted").

**Acceptance:** AC-011, AC-012.

## Functional Requirements

### FR-001 · Single-source Reviewer/Resolver-independence rendering per Adapter
Stories: US-003, US-007
Origin: Discovery, "The duplication is in the generator, confirmed on two axes"

#### Requirement
The Claude Code Adapter's generated `SKILL.md` MUST contain the
Reviewer/Resolver-independence content exactly once, regardless of how
many effective Flows are projected, and that content MUST be resolvable
by every Flow section rather than re-emitted per Flow.

#### Expected Behavior
`_gate_instructions()` (or its successor) MUST stop calling
`lines.extend(_REVIEWER_RESOLVER_INDEPENDENCE_LINES)` inside the per-Flow
loop. Flow-specific gate bullets remain per-Flow (they are genuinely
Flow-specific, per Discovery's authority map); the independence block is
not.

#### Boundary
This requirement governs rendering only. It MUST NOT change C-026's
meaning, the set of Flows it applies to (Protocol ≥ 2, fast/standard/full,
unchanged from today), or remove the independence content from any Flow
that currently receives it.

#### Acceptance
AC-004
Given the generated `SKILL.md` for a project with all three Flows enabled
under Protocol 2
When the Adapter projection runs
Then the string `"### Reviewer/Resolver independence"` appears exactly
once in the rendered output, and each per-Flow gate-obligation section
that requires it (fast/standard/full, Protocol ≥ 2) contains an explicit
pointer to that single section rather than silently omitting the
requirement from a Flow-scoped reader's view.

### FR-002 · Single-source Reviewer/Resolver-independence text shared across Adapters
Stories: US-007
Origin: Discovery, "The duplication is in the generator, confirmed on two axes"

#### Requirement
The Reviewer/Resolver-independence text rendered by the Claude Code
Adapter and the Codex Adapter MUST originate from one shared definition
consumed by both drivers, not two independently maintained Python
constants.

#### Expected Behavior
A shared module under `src/forge_cli/adapters/` (harness-agnostic,
alongside `ownership.py`/`plan.py`) exposes the independence text; both
`claude_code/projection.py` and `codex/projection.py` import it instead of
each defining their own `_REVIEWER_RESOLVER_INDEPENDENCE_LINES`.

#### Boundary
Wording differences that exist today for a real, harness-specific reason
(if any are found during Architecture/Plan) MAY remain harness-specific,
but MUST be justified explicitly, not silently reintroduced by copy-paste.

#### Acceptance
AC-005
Given the Claude Code and Codex Adapters both project a Reviewer/Resolver-
independence section
When their rendered text is diffed
Then the normative bullet content is identical, sourced from a single
shared definition verified by a test that fails if the two Adapters'
source constants diverge.

### FR-003 · Plan Decision (C-077) sentence sourced once, consistent with the generator
Stories: US-007
Origin: Discovery, "CHG-0025/C-077 Plan Decision sentence follows the same shape"

#### Requirement
The CHG-0025/C-077 Plan Decision boundary sentence MUST be projected from
exactly one generation path (already `resources/skills/workflow.md`), and
MUST NOT be separately hand-duplicated inside per-Flow gate-obligation
rendering.

#### Expected Behavior
`_gate_instructions()`'s successor MUST NOT re-embed the CHG-0025 sentence
per Flow. The historical-compatibility rule ("from CHG-0025 onward") MUST
be resolved from the Contract's own C-077 text (already stated once,
centrally, in `protocol/contract/engineering.md`), not reconstructed by
the Adapter.

#### Boundary
This requirement fixes present staleness (installed `SKILL.md` contains
the sentence twice, hand-written; the current generator emits it zero
times in gate-instruction rendering and once in `workflow.md`); it does
not change C-077's applicability window or its `human_decision` /
`resolved_via` semantics.

#### Acceptance
AC-003
Given the generated `SKILL.md`
When its content is inspected
Then the CHG-0025/C-077 Plan Decision sentence appears exactly once, and
`forge adapter plan`/`forge adapter update` regenerate `SKILL.md` content
that is byte-identical to what a fresh `forge adapter install` on this
Change's final state would produce (no drift between generator and
installed file, closing Discovery's stale-file finding).

### FR-004 · Bootstrap instructs the agent to check Adapter drift before trusting references
Stories: US-001, US-004
Origin: Discovery, "The installed Adapters are currently drifted"

#### Requirement
The generated `SKILL.md` MUST instruct an operating agent to treat its own
`references/*` as potentially stale and to check the Adapter's recorded
drift state (via `forge doctor` or `forge adapter doctor`) before relying
on them for a state-changing decision, and MUST state what to do when
drift is detected (stop and surface it; do not silently self-heal by
running `forge adapter update` without telling the human — that is a
modification of persistent repository configuration).

#### Expected Behavior
This is a Bootstrap-section instruction, not a new mechanical check —
Core's existing `generated_drift` diagnostic (`ownership.py:153-174`,
already surfaced by `forge doctor`/`forge adapter doctor`) remains the
single source of truth; the Adapter is not asked to reimplement drift
detection in the Skill's own prose.

#### Boundary
This requirement does not create automatic remediation. An agent
detecting drift reports it and stops advancing on the affected reference;
it does not unilaterally run `forge adapter update`.

#### Acceptance
AC-006
Given an installed Adapter whose `installation.yml` digest for
`references/engineering-contract.md` no longer matches the file's current
content
When an agent follows the generated `SKILL.md`'s Bootstrap instructions
Then it runs (or is instructed to run) a drift check before treating that
reference as current, and reports the mismatch rather than proceeding as
if the reference were authoritative.

AC-007
Given `forge doctor` reports `generated_drift: PASS` for an Adapter
When an agent follows the same Bootstrap instructions
Then no additional friction or false-positive stop is introduced — a
clean drift state does not block normal operation.

### FR-005 · SKILL.md restructured around Authority/Bootstrap/Operating-Model sections
Stories: US-001, US-002, US-004
Origin: Governing prompt §25; Discovery authority map

#### Requirement
The generated `SKILL.md` MUST be organized so that Authority (repository-
native Forge state is authoritative; this Skill is a derived projection),
Effective References, Bootstrap (resolve state before mutating), Operating
Model, Evidence Discipline, Human Authority, TDD Boundary, Review
Independence, Flow Execution, Artifact Discipline, Mechanical Enforcement,
Failure Behavior, Completion, and Interaction are each identifiable
sections or clearly subsumed by an existing one — reflecting this
repository's actual implementation, not the governing prompt's illustrative
heading list verbatim where the two would conflict.

#### Expected Behavior
Content that is already correctly Adapter-owned and non-duplicative
(`workflow.md`'s branch/PR, first-commit-baseline, chat-cadence, artifact-
publication, and FER guidance) is retained and organized under an
appropriate section rather than deleted or relocated to Core.

#### Boundary
This requirement is presentation/organization, not new normative content.
It MUST NOT introduce a new obligation not already present in Contract,
Flow, or existing Adapter guidance.

#### Acceptance
AC-001
Given the generated `SKILL.md`
When read top-to-bottom
Then a reader can locate, without searching multiple Flow-specific
sections, the single statement of: what is authoritative, what to resolve
before mutating, what to do at a human-authority boundary, and what to do
on guard denial.

### FR-006 · Guard tool-coverage honesty and widening
Stories: US-005
Origin: Discovery, "Guard coverage: Bash-only, and only after Skill invocation"

#### Requirement
`SKILL.md`'s guard disclosure MUST accurately state the guard's tool
coverage after this Change, and the generated `PreToolUse` hook
registration and script MUST match `Edit` and `Write` tool calls
targeting the same three protected paths
(`.forge/changes/*/{manifest.yml,provenance.yml,review.md}`), in addition
to the existing `Bash` matcher.

#### Expected Behavior
`_hook_frontmatter_lines()` registers additional matchers for `Edit` and
`Write`; the generated hook script gains logic to read `tool_input.file_path`
(or the applicable field for each tool) and deny when it targets a
protected path — reusing the existing bounded-proximity matching
philosophy from the `Bash` case where applicable, adapted to each tool's
actual input shape.

#### Boundary
This requirement does not claim complete coverage. The disclosure MUST
continue to state explicitly that this remains a partial, illustrative
guard (not a security boundary), name the tools it now covers, and name
what remains uncovered: Codex parity (Out of Scope — see below); any
mutation of the three protected paths through a tool other than
Bash/Edit/Write (e.g. an MCP filesystem tool, or `NotebookEdit`, neither
of which this Change adds coverage for); and whether a subagent's own
tool calls are subject to the same session's `PreToolUse` hook at all —
this Change MUST NOT assert subagent coverage without verifying it, and
MUST state explicitly if it remains unverified.

#### Acceptance
AC-008
Given a `manifest.yml` edit attempted through the `Edit` tool
When the `PreToolUse` guard evaluates it
Then it denies the same way the existing `Bash` case already denies an
equivalent in-place mutation, with the same class of honest deny reason.

AC-009
Given a read-only or version-control-equivalent `Edit`/`Write` call not
targeting a protected path
When the guard evaluates it
Then it allows the call, matching the existing `Bash` case's false-
positive-avoidance behavior (Discovery: `check-manifest-edit.sh`'s R001
history).

### FR-007 · Completion and human-authority boundary reporting format
Stories: US-002
Origin: Governing prompt §24, §22

#### Requirement
`SKILL.md` MUST instruct that, on reaching a human-authority Gate, a
blocked state, or a missing-evidence condition, the agent reports Current
Change, Effective Flow, Current State, Boundary, Required Decision/
Evidence, and Next Permitted Action — and MUST instruct that a Change,
phase, or Review MUST NOT be declared complete from narrative assertion
alone; completion requires resolving the actual Gate evidence (manifest
state, Verification, Review, blocking threads, Documentation Impact).

#### Expected Behavior
This is procedural instruction, consistent with the existing "Illustrative
enforcement hook" pattern of stating scope honestly; it does not add a new
Contract rule (C-035 "No false Completion" already governs the substance).

#### Boundary
None beyond what C-035 and existing Gate definitions already require.

#### Acceptance
AC-002
Given an agent operating this Adapter reaches a human-authority Gate
When it reports status to the operator
Then the report names the Change, Flow, current state, the boundary
reached, what decision or evidence is required, and what it is and is not
permitted to do next.

## Non-functional Requirements

### NFR-001 · No Core-owned duplication introduced into shared modules
The shared independence-text module introduced by FR-002 remains
hand-authored English prose — this Change does not attempt automatic
natural-language derivation from C-026's Contract paragraphs, which would
be exactly the kind of hidden automation F-010 disfavors. It MUST instead
be a single, shared rendering, verified by a test that asserts the shared
text and the currently-effective C-026 paragraph agree on the specific
mechanically-checkable claims both make (independent Execution/Context
requirement; the `claimed`/`recorded`/`verified` assurance levels; Role
changes inside one Execution being insufficient) — so the two cannot
silently diverge in substance even though the rendering is not literally
generated from Contract prose.

### NFR-002 · Existing Codex behavior does not regress
Every existing Codex Adapter test and generated-content guarantee MUST
continue to pass unchanged except where FR-002 intentionally unifies its
independence-text source.

### NFR-003 · Generated `SKILL.md` size does not grow
The post-Change generated `SKILL.md`, for the same project configuration
this repository currently uses (three Flows, Protocol 2), MUST NOT be
larger (by line count) than the file the pre-Change generator would
produce for the same configuration, given FR-001/FR-003 remove verbatim
duplication with no compensating new bulk.

## Constraints

### CON-001 · No new Protocol identifier
This Change MUST NOT require a new integer Protocol identifier (C-046).
It changes projection, not Contract meaning.

### CON-002 · No paraphrase of Contract or Flow content
Per the existing `artifact-structure.md` INV-001 pattern and C-070/C-071,
any restructured `SKILL.md` section referencing Contract or Flow content
MUST link/include it rather than restate it in different words.

### CON-003 · Shared Adapter machinery remains harness-agnostic
Any change to `src/forge_cli/adapters/*.py` (non-harness-specific modules)
MUST remain usable by both the Claude Code and Codex drivers without
harness-specific conditionals leaking into shared code (mirrors the
existing `ownership.py`/`planner.py` design already in place).

### CON-004 · No premature multi-Adapter abstraction
Per F-010 and the governing prompt's Non-goals, this Change MUST NOT
introduce a plugin system or generalized third-party-Adapter registration
mechanism beyond what FR-002's shared-module extraction already requires.

## Traceability Matrix

Per `artifact-structure.md` §4 (Specification), the Markdown Traceability
section is intentionally omitted here; `traceability.yml` (schema
`forge/traceability@1`) is this Change's authoritative FR↔Task↔Test↔
Evidence mapping and is populated once Tasks exist (Plan/Tasks stage).

## Compatibility Statement

No Protocol identifier changes (CON-001). No Contract rule's meaning
changes. No Flow gate's meaning changes. `.forge/adapters/*/installation.yml`
schema (`forge/adapter-installation@2`) is unchanged; no forced/automatic
regeneration is introduced (F-009 compatibility awareness; user
customization is never silently overwritten — `planner.py`'s existing
CONFLICT semantics already enforce this for `forge_owned` paths).

**Corrected by Specification Drift after Strict Review Iteration 1 (R004
— see `specification-drift.md`):** this section originally asserted that
"a `forge adapter update` after this Change's Implementation will show
`UPDATE` (not `CONFLICT`)... resolving Discovery's live drift as an
ordinary consequence of republishing, not a special-cased patch." This
Change's own dogfooded Implementation directly contradicted that claim:
`forge adapter update`/`forge adapter install` refused to run for *both*
Adapters via `AdapterService`'s own `_reject_drift`/`_reject_conflicts`
guards, and required a one-time, human-authorized bypass of that
production code to republish (see `verification.md`'s "Adapter Republish"
section). Any other Forge-governed repository with this Adapter already
installed and a similarly stale, never-committed `installation.yml` (the
condition DEC-004 found is not unique to this repository) will hit the
identical refusal, with no supported CLI recovery path short of the same
kind of manual bypass this Change required. That gap is real, currently
undocumented for such adopters, and is Out of Scope for this Change to
build a fix for (a `forge adapter update --acknowledge-stale-baseline`-
shaped command, or an equivalent, is follow-up work — see
`knowledge-capture.md`).

## Specification Gate

This Specification is internally consistent with Discovery's evidence
(every FR cites a Discovery finding or governing-prompt section), does not
invent Contract, Flow, or Decision-Rules content beyond what Discovery
found, and defines acceptance criteria for every FR. It proceeds to
Specification Review next per the FULL Flow's `before_architecture` Gate
(`discovery_complete`, `specification_complete`,
`specification_review_passed`).

## Out of Scope

- Building a new Harness Adapter (Cursor, VS Code, or otherwise).
- Extending mechanical guard coverage to the Codex Adapter — Codex's
  generated bundle currently has no `PreToolUse` hook artifact at all
  (Discovery), and adding one is a materially separate Change, not a
  same-Change side effect of widening Claude Code's existing hook.
- A `forge internal guard-check` (or similarly named) centralized policy
  subcommand that the hook script would call into instead of embedding
  path/pattern logic directly. Architecture will record this as a
  considered-and-deferred option with rationale, not silently adopt or
  silently reject it.
- Any change to Strict Review's substance, TDD's substance, or Review
  Convergence semantics.
- Fixing the 6 pre-existing `forge migrate --check` candidates unrelated
  to this Change's scope (Discovery).
- Worktree defects, if FR-related investigation during Architecture/Plan
  finds one: recorded as a finding and, if material, escalated as its own
  Unresolved Decision rather than silently folded into this Change's
  scope beyond a verifying test (US-006/AC-010 is a *verification*
  requirement, not a presumption that a defect exists).
