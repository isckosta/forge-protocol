---
forge:
  artifact: specification
  schema: 1
change: CHG-0013
status: complete
---

# Specification — Unresolved Decision Management

## Terminology

**Unresolved Decision.** A material decision required for an Artifact or
Gate to be considered sufficiently determined, whose answer does not yet
have valid normative authority. A question is a possible surface form of an
Unresolved Decision; not every question rises to one (see Materiality).

**Decision Class.** One of four values governing default Decision Authority:
`product`, `contract`, `architectural`, `technical`. See FR-002 for why this
Change deliberately does not adopt a `evidence` or `discovery` class (both
suggested by prior art on this pattern) as a fifth and sixth member.

**Materiality.** A binary property (`material` / `non_material`) with a
mandatory rationale. Only `material` Unresolved Decisions receive a Decision
record and participate in Gate blocking (FR-003).

**Decision Authority.** Who may resolve a Decision of a given Class:
`human`, `agent`, or `agent_with_review`. Governed by
`protocol/policies/decision.yml` and overridable, within Contract limits, by
project configuration (FR-017).

**Evidence Resolution.** Resolving an Unresolved Decision by citing an
already-existing, explicit source of normative authority (a Contract rule,
Specification clause, Policy statement, prior Decision record, or
unambiguous established repository convention) that already determines the
answer — meaning the question was never actually unresolved, only
undiscovered. Not a Decision Class; a resolution path available regardless
of Class (FR-004, FR-005).

**Recommendation.** A structured engineering opinion — a preferred
Alternative, its Rationale, the Alternatives actually considered, their
Trade-offs, the Evidence consulted, and a Confidence level (`high`,
`medium`, `low`) — produced when there is sufficient basis to prefer one
Alternative, whether or not the agent is authorized to enact it (FR-008).

**Decision.** The act, and its durable record, of actually resolving an
Unresolved Decision — either by a human (`human_decision`), or by an agent
where Decision Authority explicitly permits it (`autonomous_decision`), or
by Evidence Resolution (`evidence`). Recorded in the `resolved_via` field.
A Recommendation is never itself a Decision (FR-009).

**Owning Artifact.** The Artifact type that has semantic authority over an
Unresolved Decision's subject matter (FR-014): Specification for `product`
questions, Specification or `protocol/compatibility.md`-scoped analysis for
`contract` questions, Architecture for `architectural` questions, and
Plan/Tasks for `technical` questions local to execution decomposition.

**Discovered-in Artifact.** The Artifact or stage active when the
Unresolved Decision was found. May differ from the Owning Artifact; when it
does, this is exactly the backward-invalidation case (FR-014).

**Decision Lifecycle state.** One of `open`, `analyzing`,
`awaiting_decision`, `resolved`, `superseded` (FR-011).

**Open-blocking states.** `{open, analyzing, awaiting_decision}` — the
subset of Decision Lifecycle states that participate in Gate blocking
(FR-013). `resolved` and `superseded` are both non-blocking: a `resolved`
Decision has an answer; a `superseded` Decision's answer is no longer
authoritative but the obligation to have an answer is carried forward by
whichever Decision superseded it, not by the stale record itself.

This Change deliberately does not reuse "Resolution" as the verb or noun for
answering a Decision. Protocol 2 already gives "Resolution" a distinct,
narrower meaning (C-026 family: the act of fixing a Reviewer Finding) with
its own `resolution_verification` machinery (CHG-0011). Reusing it here
would create exactly the terminological collision §19 of this Change's
governing prompt warns against. "Resolved" (lower-case, generic English,
already used for Findings under C-027) is retained as the Decision Lifecycle
terminal state name; the field naming a Decision's resolution path is
`resolved_via`, not `resolution`.

## Decision taxonomy — rationale for four classes, not six

Prior art proposed six candidate classes: `PRODUCT`, `CONTRACT`,
`ARCHITECTURAL`, `TECHNICAL`, `EVIDENCE`, `DISCOVERY`. Investigation (see
`discovery.md`) found two of the six do not belong in the same taxonomy as
the other four:

- **`EVIDENCE` is not a Class.** It answers "how was this resolved," not
  "who owns this subject matter." A `product`-class question can be resolved
  by Evidence exactly as easily as a `technical`-class one (Scenario A of
  this Change's governing prompt is explicitly class-agnostic). Modeling it
  as a Class would force every Decision through a false choice between "this
  is a product question" and "this is an evidence question" when both can be
  true. Evidence Resolution is instead a resolution path attempted first,
  regardless of Class (FR-004).
- **`DISCOVERY` collides with an existing Flow stage name.** `Discovery` is
  already a required FULL/STANDARD stage (`specification.md` §9–§10 of the
  shared canonical spec). Reusing the word for a Decision Class would breach
  C-032/C-033 (no parallel vocabulary/competing pattern) and the same
  discipline CHG-0011's own Discovery applied to itself ("no... vocabulary
  exists... this is new vocabulary, not a rename"). No distinct semantic
  content survives dropping it: what remains of "discovery" as a candidate
  Decision Class is fully covered by Evidence Resolution plus ordinary
  `technical` classification.

The remaining four Classes are retained because each maps to a distinct
Owning Artifact and a distinct default Decision Authority, which is the
entire operational purpose of classification (FR-002):

| Class          | Owning Artifact                              | Default Authority   |
|----------------|-----------------------------------------------|----------------------|
| `product`      | Specification                                  | `human`              |
| `contract`     | Specification (compatibility-scoped) / `protocol/compatibility.md` | `human` |
| `architectural`| Architecture                                   | `agent_with_review`  |
| `technical`    | Plan / Tasks                                   | `agent`              |

`product` and `contract` are kept distinct even though both default to
`human`: a `product` Decision concerns behavior ("what should happen"); a
`contract` Decision concerns an external-facing interface, compatibility, or
Protocol-identifier boundary obligation ("what does this promise, and to
whom, going forward"). They can require different investigation (compatibility
analysis vs. domain analysis) and different owning documentation
(`protocol/compatibility.md` for Protocol-level `contract` Decisions). Both
default to `human` for the same underlying reason (irreversible or
externally-visible commitment), but a project MAY, within Contract limits,
diverge their Authority independently — collapsing them into one Class would
remove that degree of freedom for no benefit.

## Functional requirements

### FR-001 — Unresolved Decision creation trigger

An agent MUST create an Unresolved Decision record when it identifies a
question meeting the Materiality test (FR-003) and does not already hold a
valid normative answer for it. An agent MUST NOT silently choose an answer
to a Material question and represent it as settled fact in any Artifact.

### FR-002 — Decision Class

Every Unresolved Decision MUST be classified as exactly one of `product`,
`contract`, `architectural`, `technical`. Classification determines the
Owning Artifact and the default Decision Authority (see taxonomy table
above). Misclassification to obtain a more permissive default Authority is
a Contract violation (C-054) discoverable by Strict Review.

### FR-003 — Materiality test

A question is Material if resolving it differently would change, or would
plausibly let two independently competent engineers produce incompatibly
different: a Requirement, an Acceptance Criterion, a public or API Contract,
a Schema, a Compatibility boundary, Security posture, a domain Invariant, an
ownership or authority boundary, failure/error semantics, a state
transition, Architecture, Verification Strategy, rollout/migration behavior,
or other operational behavior. A question that does not meet this test is
Non-material: it MUST NOT receive a Decision record, MUST NOT block a Gate,
and MUST NOT interrupt the workflow (C-058). Every Decision record MUST
carry a `materiality_rationale` explaining why the test was met; recording a
Decision without one is itself a defect a Reviewer can raise.

### FR-004 — Evidence investigation precedes escalation

Before an Unresolved Decision may reach `awaiting_decision`, the agent MUST
attempt Evidence Resolution: search the repository for an existing Contract
rule, Specification clause, Policy statement, prior Decision record (this
Change's own mechanism, once populated), or unambiguous established
repository convention that already determines the answer. This investigation
MUST be recorded (what was checked, what was found or not found) regardless
of outcome.

### FR-005 — Evidence Resolution

When investigation under FR-004 finds an explicit source of existing
normative authority that determines the answer, the Decision is `resolved`
with `resolved_via: evidence`, citing the specific source. This applies
regardless of Decision Class — `product` and `contract` Decisions may be
Evidence-resolved exactly as `technical` ones can. Evidence Resolution MUST
NOT be recorded on the basis of the agent's own inference, preference, or
unstated judgment; only a citable existing source qualifies. An agent that
cannot cite a specific source MUST NOT record `resolved_via: evidence`.

### FR-006 — Delegated (autonomous) decision path

When Evidence Resolution does not apply and the Decision's Class has
Authority `agent` or `agent_with_review` (by default or by permitted project
override, FR-017), the agent MUST perform Analysis, MAY produce Alternatives
when a real choice exists, MUST produce a Recommendation (FR-008), and MAY
then resolve the Decision itself (`resolved_via: autonomous_decision`),
recording the Recommendation it enacted and its Confidence. An
`agent_with_review` Decision additionally requires the Decision record and
its Rationale to be reviewable — at minimum present in the Change's
`decisions.md` where Strict Review will see it — and, when the Decision also
matches an `architecture.yml` `adr.required_when` trigger, an ADR is
required at Documentation per that existing policy (not duplicated here).

### FR-007 — Human-authority decision path

When the Decision's Class has Authority `human` (by default or unchanged
project configuration), or Evidence Resolution and the autonomous path both
do not apply, the agent MUST perform Analysis, produce Alternatives when a
real choice exists, analyze Trade-offs, and produce a Recommendation with
Confidence (FR-008) before transitioning the Decision to
`awaiting_decision`. The agent MUST NOT resolve the Decision itself. The
workflow MUST stop and present the Decision using the structured format in
FR-010, not an open-ended question, whenever Alternatives exist.

### FR-008 — Recommendation shape

A Recommendation, when produced, MUST include: the preferred Alternative;
its Rationale; every Alternative actually considered (MAY be a single
Alternative when no real choice exists, e.g. only one option satisfies
existing Invariants); the Trade-offs of each Alternative considered
material enough to record; the Evidence consulted (even when inconclusive);
and a Confidence of `high`, `medium`, or `low`. Confidence MUST NOT be
expressed as a numeric score (C-040 explicit trade-offs; avoiding false
precision).

### FR-009 — Recommendation is not Decision

A Decision record MUST distinguish its `recommendation` field from its
`decision` field. `decision` MUST NOT be populated with the same value as
`recommendation` unless `resolved_via` is `autonomous_decision` (Authority
permitted it) or the human Decision-maker independently chose the
recommended Alternative and `resolved_via: human_decision` records that
explicitly. A `decision` field populated while `resolved_via` is absent, or
while Authority is `human` and `resolved_via` is not `human_decision`, is a
Contract violation (C-054/C-055) — "recommendation laundering."

### FR-010 — Human clarification presentation format

When a Decision reaches `awaiting_decision` and Alternatives exist, Forge
MUST present: the Question; why it matters (which Requirement/Contract/
Architecture/etc. it affects, from the Materiality rationale); each
Alternative with its Advantages and Disadvantages; the Recommendation and
its Rationale; the Confidence; the Decision Authority; and an explicit
statement that the human MAY accept the Recommendation, choose a different
Alternative, supply an answer outside the presented Alternatives, or request
further analysis. An open-ended question with no investigation and no
Alternatives MUST NOT be the first form of escalation when investigation
under FR-004/FR-006/FR-007 could have produced Alternatives; it remains
available only when a real choice genuinely could not be narrowed (e.g. the
question is open-ended by nature, such as "what should this be named").

### FR-011 — Decision Lifecycle

States: `open` (created, not yet investigated), `analyzing` (FR-004/FR-006/
FR-007 investigation in progress), `awaiting_decision` (human-authority path
reached FR-007's stop point), `resolved` (a Decision exists via `evidence`,
`autonomous_decision`, or `human_decision`), `superseded` (a later Decision
replaces this one; the earlier record is retained, not deleted — see
FR-014). Valid transitions: `open` → `analyzing`; `analyzing` →
`resolved` (via `evidence` or `autonomous_decision`) or → `awaiting_decision`;
`awaiting_decision` → `resolved` (via `human_decision`) or → `analyzing`
(human requests further analysis); `resolved` → `superseded` (only when a
new Decision replaces it — a `resolved` Decision MUST NOT be silently
edited in place). Non-material questions never enter this lifecycle
(FR-003).

### FR-012 — Decision record placement

Unresolved Decisions for a Change are recorded as dated, ID-stable sections
(`DEC-NNN`) appended to a single `decisions.md` file in the Change directory
— mirroring the existing `review.md` convention (one prose ledger per
Change, append-only in meaning once a section's outcome is committed,
sections never rewritten to change what was actually decided). Each section
MUST contain: Class, Materiality + rationale, Owning Artifact,
Discovered-in Artifact, Decision Authority, Question, Evidence investigated,
Alternatives (with Advantages/Disadvantages) when present, Recommendation +
Rationale + Confidence when present, `resolved_via`, Decision, Decision
rationale, and — when applicable — `invalidates` (FR-014) and `supersedes`/
`superseded_by`. A compact index MUST additionally exist in `manifest.yml`
under a new top-level `decisions` array (`id`, `class`, `materiality`,
`status`, `authority`, `owning_artifact`, `discovered_in`, `resolved_via`,
`invalidates`) sufficient for Core to mechanically check Gate-blocking
conditions (FR-013) without parsing Markdown.

### FR-013 — Gate blocking

A Gate that depends on an Artifact MUST NOT be asserted passed while that
Artifact has, in its owning capacity, a `decisions[]` entry with
`materiality: material` and `status` in an Open-blocking state (C-051). This
applies
at minimum to `specification_review_passed` (blocks on `product`/`contract`
Decisions owned by Specification), the `before_implementation` Gate (blocks
on `architectural` Decisions owned by Architecture), `review_passed`, and
`before_completion`. Absence of any `decisions[]` entry — the case for every
Change that predates or does not use this mechanism — trivially satisfies
this requirement (compatibility, see §Compatibility). The mechanically
checkable slice of this requirement (manifest shape and internal
consistency) is enforced by `forge validate`; whether an agent *should have*
recorded a Decision it did not is not mechanically checkable and remains a
Strict Review responsibility (see Discovery's "Limitations" finding and
FR-015).

### FR-014 — Ownership and backward invalidation

A Decision's `owning_artifact` MUST be the Artifact type with semantic
authority over its subject matter (taxonomy table), regardless of
`discovered_in`. A downstream Artifact (e.g. Tasks) MUST NOT set
`owning_artifact` to itself for a Decision whose Class maps to an earlier
Artifact type (e.g. `product`) — doing so is exactly the silent
downstream-resolution failure mode this Change exists to prevent (C-052).
When `discovered_in` differs from `owning_artifact`, the owning Artifact
MUST be revisited: its own stage is re-entered, its content revised, and any
Gate that already asserted it passed (including `specification_review_passed`
when `owning_artifact: specification`) MUST be re-satisfied by a new
Review Iteration before the Change may proceed past it again — the
Decision's resolution does not itself substitute for that Gate. Once the
Decision is `resolved` there, the agent MUST explicitly declare, in the
Decision record,
which already-`complete`/`approved` downstream `artifacts.*` entries this
resolution `invalidates`. Core MUST reject `state.current`/Gate assertions
where a downstream artifact remains `complete`/`approved` while listed under
an unresolved `invalidates` obligation (C-057); the artifact's status
convention becomes `invalidated` until the agent revises it and the owning
stage's own Gate is satisfied again. This Change does not attempt to
mechanically compute invalidation scope from a diff — this is an explicit,
reviewable engineering judgment recorded at Decision-resolution time, not an
inferred blast radius (avoiding both under- and over-invalidation by making
the choice auditable rather than automatic).

### FR-015 — Specification Review integration

When Adversarial Specification Review (or any Review) discovers a Material
Unresolved Decision (a gap the Specification should have settled but did
not), the Reviewer MUST record a Finding and select REQUEST CHANGES (or the
equivalent outcome for the review type); the Reviewer MUST NOT resolve the
Decision within the same Review (C-059), preserving Reviewer/Resolver
separation (C-026) for this new Finding class exactly as for any other. A
new Decision record with `discovered_in: specification_review` and
`owning_artifact: specification` MUST exist before the Specification returns
for a new independent Review.

### FR-016 — Interaction with Assumptions

A Material Assumption (per the generalized form of the existing
`security.yml` `assumptions.must_be_explicit_when_material` rule, no longer
security-scoped only) MUST be registered as an Unresolved Decision; stating
an Assumption MUST NOT substitute for creating or resolving the Decision it
is material to (C-056, "assumption laundering"). A Non-material Assumption
needs no Decision record, symmetric with FR-003.

### FR-017 — Decision Authority policy

Default Decision Authority per Class is defined in a new canonical policy,
`protocol/policies/decision.yml` (schema `forge/policy/decision@1`):
`product: human`, `contract: human`, `architectural: agent_with_review`,
`technical: agent`. This default requires no project configuration to
function (C-039 proportional process; no mandatory setup). A project MAY
strengthen (move toward `human`) or, only where the Contract does not
forbid it, relax Authority via `.forge/policies/decision.yml`, mirroring
the existing project-extension pattern for every other canonical Policy.
`product` and `contract` Authority MUST NOT be relaxed below `human` by
project configuration (this Change's Contract addition, C-055, makes
human-authority Decisions non-negotiable at the project-configuration
layer, consistent with C-042: project configuration cannot weaken canonical
invariants).

### FR-018 — Convergence and non-interruption for non-material questions

Forge MUST NOT require a Decision record, escalation, or human interruption
for a question that fails the Materiality test (C-058). This is the primary
mechanism preventing "question dumping" and unbounded clarification loops:
the boundary is sufficient determinacy for the next governed stage, not
exhaustive resolution of every future implementation detail.

## Invariants

### INV-001 — No Gate passes with an open Material Decision it depends on
A Gate MUST NOT be asserted passed while a `decisions[]` entry with
`materiality: material` and `owning_artifact` within that Gate's dependency
set has `status` in an Open-blocking state (`open`, `analyzing`, or
`awaiting_decision`). `resolved` and `superseded` entries do not block.

### INV-002 — Evidence Resolution requires a citable source
`resolved_via: evidence` MUST reference a specific existing normative
source (Contract rule ID, Specification section, Policy path, or prior
Decision ID). An agent's own inference, however confident, is not Evidence.

### INV-003 — Owning Artifact cannot be later than the Owning Class's canonical stage
A Decision's `owning_artifact` MUST correspond to the Class's canonical
Owning Artifact (taxonomy table) regardless of which stage discovered it.
It MUST NOT be set to a stage later in canonical Flow order than that
Owning Artifact.

### INV-004 — Decision identity is append-only once committed
A committed `DEC-NNN` section's Class, Materiality, Owning Artifact, and
recorded Decision MUST NOT later be rewritten to mean something different;
correction happens by superseding (`superseded_by` a new `DEC-NNN`), never
by silent edit — mirroring the append-only provenance/Review-Iteration
precedent already established by Protocol 2 (C-026 family).

### INV-005 — Confidence is categorical, not numeric
Confidence MUST be exactly one of `high`, `medium`, `low`.

## Compatibility

This Change adds:

- an optional top-level `decisions` array to `forge/change@1` and
  `forge/change@2` (both currently `additionalProperties: false` at the top
  level; the field is new and additive to both, not schema-breaking);
- new conventional (documented, not schema-enum-enforced — `artifacts` has
  no enum today in either schema) `artifacts.*` status values `invalidated`
  and `revised`;
- a new canonical Policy `forge/policy/decision@1` (an entirely new artifact
  type; adds nothing to any existing schema);
- Contract rules C-051–C-059, applying only once a Change actually records a
  `decisions[]` entry — a Change that never does (every Change predating
  this one) makes no claim these rules speak to and is unaffected, exactly
  the "optional artifacts whose absence preserves existing meaning" category
  `protocol/compatibility.md` already recognizes for CHG-0011's C-047–C-050;
- a new `protocol/specification.md` §39 (this concept is Protocol-version-
  independent baseline Core semantics — unlike CHG-0011's review-provenance
  machinery, nothing here depends on Protocol 2's Execution/Context
  independence model, so it belongs in the shared canonical Specification,
  not `protocol/versions/2/specification.md`, which is reserved for
  Protocol-2-only elaboration per that file's own established scope).

No removed or weakened invariant, no changed meaning of an existing required
field or Gate, no invalidated previously-valid conforming instance. Verified
directly against this repository's own `CHG-0001` through `CHG-0012`
manifests: none sets `decisions`, all continue to validate and mean exactly
what they meant before. No new integer Protocol identifier and no new
`forge/change@N` schema suffix is required.

The `protocol/versions/2/contract/engineering.md` backfill described in
`discovery.md` (adding C-047–C-050 and C-051–C-059 to that file) is a
correction bringing an already-canonical, already-shipped rule set into the
one place Protocol 2's own resolver requires it — it does not change what
those rules mean or add new obligations beyond what `protocol/contract/
engineering.md` already states.

## Acceptance criteria

- **AC-001** (Scenario A — evidence resolves it): A question with an
  existing Contract/Specification/Policy answer resolves via
  `resolved_via: evidence`, citing the source, with no human interruption.
- **AC-002** (Scenario B — delegated technical decision): A `technical`
  Decision with real Alternatives produces Analysis, a Recommendation, and
  an autonomous Decision, recorded with full provenance, without stopping
  the workflow.
- **AC-003** (Scenario C — product decision): A `product` Decision with no
  existing authority produces Analysis, Alternatives, Trade-offs, a
  Recommendation, reaches `awaiting_decision`, and blocks the dependent
  Gate.
- **AC-004** (Scenario D — human accepts recommendation): `decision` equals
  `recommendation`, `resolved_via: human_decision`, the Owning Artifact is
  updated, and the workflow resumes.
- **AC-005** (Scenario E — human rejects recommendation): `decision` differs
  from `recommendation`, is recorded with the human's own rationale, and is
  not "corrected" back toward the Recommendation absent an actual Contract/
  Invariant violation.
- **AC-006** (Scenario F — ambiguity discovered during Tasks): a `product`-
  class Decision discovered while working on Tasks is not resolved in
  Tasks; `owning_artifact: specification` is set; Specification is revisited;
  affected downstream artifacts are explicitly `invalidates`-listed and
  marked `invalidated` until revised.
- **AC-007** (Scenario G — review discovers ambiguity): Reviewer records a
  Finding and REQUEST CHANGES; a new Decision record exists;
  Reviewer/Resolver separation holds — the same Execution/Context that
  raised the Finding does not also resolve the Decision.
- **AC-008** (Scenario H — non-material question): no Decision record is
  created; the workflow does not pause.
- **AC-009** (Scenario I — high confidence does not authorize): a `human`-
  authority Decision with `confidence: high` still requires
  `resolved_via: human_decision`; `resolved_via: autonomous_decision` on a
  `human`-authority Decision is a Contract violation (C-055).
- **AC-010** (Scenario J — gate bypass attempt): a Gate asserted passed
  while a `material` `decisions[]` entry in an Open-blocking state exists in
  its dependency set is a `forge validate` finding (C-051, INV-001).
