---
forge:
  artifact: specification
  schema: 1
change: CHG-0050
status: complete
---

# CHG-0050 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0050 |
| **Flow** | FULL |
| **Status** | Draft |

## Summary

Add a developer-facing Review Experience Mode (`recommended` default,
`fast`, `thorough`) resolvable per Change and, optionally, as a
persistent project preference; resolve it to an effective Review
Profile that can never rank below the Change's Flow-derived floor;
make Review phase (Discovery/Findings/Resolution/Re-review, internally
`scanning`/`findings_recorded`/`resolving`/`re_reviewing`/`converged`/
`stopped`) a schema-tracked, Core-validated field; project both into
the Harness Adapters; and add a read-only CLI status command. This
Specification implements RFC-0008 (`docs/rfcs/0008-review-experience-modes.md`,
accepted) and is bound by Discovery's findings
(`discovery.md`) — no Engineering Contract text changes, no new
Review Profile values, no change to Convergence Limit, independence,
evidence, or Finding-severity mechanics.

## Classification

**FULL**, per the escalation already recorded in `manifest.yml`
(`DEC-001`): this Change adds persistent schema surface, a new
cross-Adapter Harness-observability contract, and a new
default-visible developer experience for every Forge-enabled
repository — matching `fast.yml`'s disqualifiers
(`architectural_change`, `major_public_contract_change`).

## User Stories

**US-001** — As a developer running a typical Change, I want Review to
default to the right rigor automatically, so I never have to name a
Flow or profile to get a correct outcome.

**US-002** — As a developer who wants to merge a low-risk Change
quickly, I want to ask for `Fast` review without being able to
accidentally weaken the assurance my Change's Flow actually requires.

**US-003** — As a developer mid-Review, I want to see what phase is
active and what remains, so I am not left guessing why another cycle
is happening.

## Functional Requirements

### FR-001 · Per-Change Review Mode field
Stories: US-001, US-002

#### Requirement
`forge/change@2`'s `manifest.yml` schema MUST accept an optional
`review.mode` field, enum `recommended | fast | thorough`. A manifest
that omits it MUST be interpreted as `recommended`.

#### Boundary
This field only selects a mode; it never itself sets the effective
Review Profile (FR-002 does).

#### Acceptance
AC-001
Given a `manifest.yml` with no `review.mode` field
When it is validated or read by any consumer (Adapter projection, CLI, resolution function)
Then it is treated identically to `review.mode: recommended`

AC-002
Given a `manifest.yml` with `review.mode: fast` or `review.mode: thorough`
When `forge validate` runs
Then the manifest is accepted as schema-valid (additive field, no other constraint at the schema level)

### FR-002 · Mode-to-profile resolution never ranks below the Flow floor
Stories: US-002
Origin: RFC-0008 §2

#### Requirement
A function MUST resolve a Change's effective Review Profile from its
Flow-derived floor (today's existing computation, including any
project-flow stricter-than-floor override) and its `review.mode`:
`recommended` and `fast` resolve to exactly the floor; `thorough`
resolves to one profile rank above the floor
(`focused→standard→strict`), capped at `strict`.

#### Expected Behavior
The function must be expressible as `max(floor_rank, mode_offset)`
over the existing `_PROFILE_RANK` ordering — there must be no code
path, for any Flow/mode combination, that returns a profile ranked
below `floor`.

#### Boundary
This requirement does not change how `floor` itself is computed
(`resolve_effective_flow`, the existing project-flow override, and
`_validate_review_profile_floor` are unmodified inputs to this
function, not superseded by it).

#### Acceptance
AC-003
Given a Change whose Flow floor profile is `strict`
When `review.mode` is `fast`
Then the resolved effective profile is `strict`, not `focused` or `standard`

AC-004
Given a Change whose Flow floor profile is `focused`
When `review.mode` is `thorough`
Then the resolved effective profile is `standard`

AC-005
Given a Change whose Flow floor profile is `strict`
When `review.mode` is `thorough`
Then the resolved effective profile remains `strict` (already the ceiling)

AC-006
Given any Flow floor profile and any of the three mode values
When the effective profile is resolved
Then its `_PROFILE_RANK` is always `>=` the floor's rank

### FR-003 · Persistent project-level mode preference
Stories: US-001

#### Requirement
`.forge/forge.yml`'s schema (`forge/project@1`) MUST accept a new,
independent, optional field `review.preferred_mode` (same enum as
FR-001). `forge change new` MUST use it to seed a new Change
scaffold's `manifest.yml` `review.mode` when present; when absent, the
scaffold MUST default to `recommended`.

#### Boundary
This field MUST NOT be read as an override for an already-set
per-Change `review.mode` on an existing Change, and MUST NOT change
the existing, untouched `review.strict` field's meaning or value.

#### Acceptance
AC-007
Given a project with `.forge/forge.yml` `review.preferred_mode: thorough`
When `forge change new <slug>` scaffolds a Change
Then the new Change's `manifest.yml` has `review.mode: thorough`

AC-008
Given a project with no `review.preferred_mode` set
When `forge change new <slug>` scaffolds a Change
Then the new Change's `manifest.yml` has `review.mode: recommended` (or omits the field, per FR-001's default interpretation)

AC-009
Given an existing Change with `review.mode: fast` already set
When the project's `review.preferred_mode` is later changed to `thorough`
Then the existing Change's already-set `review.mode` is unaffected

### FR-004 · Schema-tracked Review phase
Stories: US-003
Origin: Discovery OQ-2 (resolved: schema-tracked)

#### Requirement
`manifest.yml` MUST accept an optional `review.current_phase` field,
enum `scanning | findings_recorded | resolving | re_reviewing |
converged | stopped`. `forge validate` MUST reject a value outside
this enum, and MUST flag an inconsistency between `current_phase` and
the latest recorded `review.iterations[]` entry / `review.status`
(e.g. `current_phase: converged` while `review.status` is not
`passed`).

#### Expected Behavior
Harness-facing and developer-facing prose MAY present these six
values under the human labels Discovery/Findings/Resolution/Re-review/
Converged/Stopped; the schema enum values above are the sole
machine-checked identifiers and are intentionally distinct from the
Change-lifecycle `discovery` Artifact identifier to avoid collision
(RFC-0008 §4).

#### Boundary
This field does not drive any Gate condition by itself; it is a
readable, validated observability signal, not a new blocking
mechanism.

#### Acceptance
AC-010
Given a `manifest.yml` with `review.current_phase: converged` and `review.status: passed`
When `forge validate` runs
Then it passes with no `current_phase`-related finding

AC-011
Given a `manifest.yml` with `review.current_phase: converged` and `review.status` not `passed`
When `forge validate` runs
Then it reports a finding for the inconsistency

AC-012
Given a `manifest.yml` with `review.current_phase: not_a_real_value`
When `forge validate` runs
Then it reports a schema-validation finding

AC-012b
Given a `manifest.yml` that omits `review.current_phase` and has an empty `review.iterations: []`
When `forge validate` runs
Then it passes with no consistency finding — an absent phase before any Review Iteration exists is the valid initial state, not an inconsistency

### FR-005 · Adapter projection of the mode-to-profile table and phase vocabulary
Stories: US-001, US-003

#### Requirement
`_gate_instructions` in `src/forge_cli/adapters/claude_code/projection.py`
and `codex/projection.py` runs once per canonical Flow at `forge
adapter install` time, with no specific Change in scope — it MUST NOT
be designed as if it could read a particular Change's live
`manifest.review.mode`/`current_phase` (Implementation-time correction
to this Requirement's original framing; see `DEC-004`). Instead, for
each Flow it projects, when `protocol_id >= 2`, a per-Flow line stating
that Flow's Review Profile floor (FR-002's `floor`) and the concrete
profile `thorough` resolves to for that floor (via
`resolve_effective_review_profile(floor, "thorough")`); and, once,
after the per-Flow loop (mirroring how the shared independence section
is appended once today), a single shared, Flow-invariant "Review
Experience Modes" section explaining the `review.mode` vocabulary, the
`review.current_phase` vocabulary and its human labels, and pointing
at `forge change review-status <slug>` for a given Change's actual
live selection and phase. The shared Reviewer/Resolver-independence
and Convergence-Limit instruction blocks (`review_independence.py`)
MUST remain byte-for-byte unchanged and mode-invariant.

#### Boundary
Projection is instructional text generation; it MUST NOT alter
`forge validate`'s own independent enforcement of independence,
evidence, severity, or convergence rules (mirrors RFC-0007 decision
point 10's existing separation of concerns). Projection MUST NOT claim
to know any specific Change's live `review.mode`/`current_phase` value
— only `forge change review-status` (FR-006) reads a specific Change.

#### Acceptance
AC-013
Given the FAST Flow (floor `focused`)
When the `claude_code` Adapter projects its FAST gate instructions
Then the generated text states the floor is `focused` and that `thorough` resolves to `standard` for this Flow

AC-014
Given either Adapter's projected instructions for `protocol_id >= 2`
When the shared Review Experience Modes section is rendered
Then it lists all six `current_phase` values with their human-facing labels (Discovery/Findings/Resolution/Re-review/Converged/Stopped) and names `forge change review-status`

AC-015
Given any Flow and `protocol_id`
When either Adapter projects Reviewer/Resolver independence or Convergence Limit instructions
Then the generated text is identical to today's output for those specific blocks — unaffected by the new per-Flow mode-resolution line or the shared Review Experience Modes section

### FR-006 · `forge change review-status` CLI command
Stories: US-003

#### Requirement
A new subcommand `forge change review-status {slug}` MUST print, for
a local, uncommitted-or-committed Change: its `review.mode`, resolved
effective profile, `review.current_phase` (human label), outstanding
Finding counts by severity, and a next-step hint derived from existing
`merge_readiness` diagnostics plus `current_phase`. It MUST operate
entirely on local Git-native repository state (no remote dependency,
C-038).

#### Boundary
This command is read-only; it MUST NOT mutate `manifest.yml` or any
other Change artifact. For a Change with no `review.current_phase` and
no `review.iterations` yet (freshly scaffolded, Review not started),
the command MUST print an explicit "Review not yet started" state
rather than an empty or misleading field.

#### Acceptance
AC-016
Given a Change with `review.mode: thorough`, resolved profile `strict`, `current_phase: findings_recorded`, and one recorded BLOCKER Finding
When `forge change review-status <slug>` runs
Then its output includes the mode, `strict`, the human label for `findings_recorded`, a BLOCKER count of 1, and a next-step hint naming Resolution

AC-016b
Given a freshly scaffolded Change with no `review.current_phase` and an empty `review.iterations`
When `forge change review-status <slug>` runs
Then its output states plainly that Review has not started, without printing a blank or default-looking phase value

AC-017
Given a Change directory that does not exist
When `forge change review-status <slug>` runs
Then it exits non-zero with a clear error, performing no filesystem or network mutation

### FR-007 · Explicit `stopped` phase carries no approval authority
Stories: US-003
Origin: Intent — "developer can end processing without a false success claim"

#### Requirement
A developer MUST be able to set `review.current_phase: stopped` on a
Change whose `review.status` is not `passed`. Setting this value MUST
NOT, by itself or in combination with any other field this Change
introduces, cause `review.status` to become `passed` or cause
Completion to be assertable (C-035 is unmodified by this Change).

#### Boundary
This requirement does not introduce a new Convergence-Limit option;
`abort_or_supersede` (existing, C-049) remains the correct choice
specifically at the Convergence Limit boundary. `stopped` is a
general, always-available observability statement, not a
Convergence-specific one.

#### Acceptance
AC-018
Given a Change with `review.current_phase: stopped` and `review.status: failed`
When `forge validate` runs
Then it passes with no finding attributable to `stopped` itself, and separately continues to report the Change as incomplete via existing Completion checks

AC-019
Given a Change with `review.current_phase: stopped`
When `forge change review-status <slug>` runs
Then its output states plainly that the Change is not complete and names the last recorded outcome (e.g. remaining BLOCKER/MAJOR Findings)

## Security Requirements

None. This Change adds read-only local CLI output, schema fields, and
Adapter-projected instruction text; it introduces no new input trust
boundary, credential, network call, or write path beyond what
`manifest.yml` editing already requires today.

## Non-functional Requirements

### NFR-001 · Compatible evolution
Every schema change in this Specification (`review.mode`,
`review.preferred_mode`, `review.current_phase`) MUST be optional and
default to today's behavior when absent, so no existing valid
`forge/change@2` manifest or `forge/project@1` project file becomes
invalid or changes meaning (C-045).

### NFR-002 · No new remote dependency
`forge change review-status` MUST operate without any network or
Forge-hosted-backend dependency (C-038).

## Constraints

### CON-001 · No Engineering Contract text change
This Change MUST NOT modify `protocol/versions/2/contract/engineering.md`
or `protocol/contract/engineering.md`. RFC-0008's Compatibility section
establishes that the never-below-floor guarantee is a structural
property of FR-002's resolution function, not a new invariant
requiring its own Contract clause.

### CON-002 · Mode-blind enforcement mechanics
This Change MUST NOT alter `_validate_resolution_verification`'s
targeted-re-review escalation logic, the Convergence Limit
(`consecutive_unconverged_verifications`, limit 2), Reviewer/Resolver
independence checks, evidence requirements, or Finding-severity
semantics in `src/forge_cli/validation/__init__.py`. These remain
identical for every `review.mode` value, exactly as they are already
identical for every `review.profile` value (RFC-0007 decision point 6).

## Traceability Matrix

| Requirement | Story | Discovery/RFC Origin | Acceptance |
|---|---|---|---|
| FR-001 | US-001, US-002 | RFC-0008 §1 | AC-001, AC-002 |
| FR-002 | US-002 | RFC-0008 §2 | AC-003–AC-006 |
| FR-003 | US-001 | RFC-0008 §3 | AC-007–AC-009 |
| FR-004 | US-003 | Discovery OQ-2 / RFC-0008 §4 | AC-010–AC-012 |
| FR-005 | US-001, US-003 | RFC-0008 §5 | AC-013–AC-015 |
| FR-006 | US-003 | RFC-0008 §6 | AC-016, AC-017 |
| FR-007 | US-003 | RFC-0008 §7 / Intent | AC-018, AC-019 |

## Compatibility Statement

All three new schema fields (`review.mode`, `review.preferred_mode`,
`review.current_phase`) are optional and additive across
`forge/change@2` and `forge/project@1`; omission is interpreted as
today's universal behavior. No historical Change's recorded Review is
reinterpreted (C-045). `protocol/schemas/policy-review.schema.json`
(Protocol 1) is untouched, consistent with RFC-0007's scoping of the
underlying profile concept to Protocol 2 — this Specification inherits
that scoping rather than revisiting it. No Adapter beyond
`claude_code` and `codex` exists to update; any future Adapter is
bound by C-074's conformance-suite obligation independent of this
Change.

## Specification Gate

Every Functional Requirement above has at least two Acceptance
Criteria in Given/When/Then form; every AC maps to exactly one FR
(Traceability Matrix); Non-functional Requirements and Constraints are
present because they are materially applicable (compatibility and
mode-blind-enforcement guarantees this Change must not violate), not
padding. No Requirement lacks a verification strategy — Test Strategy
is the next Artifact. This gate is ready to proceed to Specification
Review.

## Out of Scope

- Redefining `focused`/`standard`/`strict` themselves, or introducing
  a fourth Review Profile value (RFC-0007's enum is closed by this
  Change).
- Any change to Flow classification, Flow escalation, or the
  disqualifier list in `fast.yml`/`standard.yml`/`full.yml`.
- Any change to Reviewer/Resolver independence, evidence requirements,
  Finding severities, Resolution Verification scoping, or the
  Convergence Limit (CON-002).
- A full Review-phase state-machine transition validator; `forge
  validate` checks enum membership and status/phase consistency only
  (FR-004), not every legal transition path.
- Any Adapter beyond `claude_code` and `codex`.
- A graphical or web Harness UI; this Specification's UX surface is
  Adapter-projected chat instruction text and a terminal CLI command.
