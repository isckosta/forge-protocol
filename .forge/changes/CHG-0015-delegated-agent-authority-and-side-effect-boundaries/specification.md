---
forge:
  artifact: specification
  schema: 1
change: CHG-0015
status: complete
---

# Specification — Delegated Agent Authority and Side-Effect Boundaries

## Terminology

**Capability.** What an Execution is technically able to do, given its
harness, tools, and process/filesystem/Git access — e.g., "can call a
filesystem-write tool." Capability is a fact about the runtime environment.
It carries no normative weight on its own (FR-002). Forge already has one
legitimate, narrower meaning of this word (the Adapter `persistent_
instructions`/`commands`/`skills`/`hooks`/`agent_roles`/`generated_files`
projection-capability model, `protocol/schemas/adapter.schema.json`); this
Specification's use of "Capability" is the broader, general sense the
originating instruction's §3.1 describes, and MUST NOT be confused with the
Adapter-specific one.

**Authority.** What a specific Execution is normatively permitted to do,
for this delegation, under the Engineering Contract. Authority is always
relative to a delegation: it does not exist independent of who granted it,
to whom, over what, and for what purpose. An Execution may possess a
Capability without possessing the Authority to exercise it in a particular
Execution — the property this whole Change exists to make checkable
(originating instruction §33).

**Delegation.** The act of one Execution (the *delegator*) instructing
another Execution (the *delegate*) to perform bounded work, at any depth
(Human → primary Execution, primary Execution → subagent, subagent → nested
subagent). A Human's delegation to a primary Execution is the root of every
chain and is not itself bounded by this Specification's Delegation Ceiling
(FR-007) — a Human is not an Execution and does not derive Authority from
one.

**Authorized Scope.** The concrete, declared boundary of what a delegate
Execution's Authority permits it to mutate for this delegation: a set of
repository-relative paths it may write (possibly empty — pure investigation
carries an empty write scope), reusing and generalizing the existing
`scope` field already present in `forge/execution-provenance@1`
(`protocol/schemas/execution-provenance.schema.json`), today interpreted
only for `role: resolution` (Protocol 2 §11). This Specification does not
introduce a new field name; it extends where an existing one applies (see
Compatibility).

**Execution Boundary.** The pre-delegation and post-delegation repository
state pair against which a delegate Execution's Observed Effect is
computed. Generalizes Protocol 2 §5's frozen-subject-vs-current-workspace
comparison (today anchored to a Review subject freeze, applicable only
post-Implementation) into a stage-agnostic concept anchored to a
delegation's own start and end, usable at any lifecycle stage including
Discovery — this is the mechanism that would have covered the motivating
incident, which occurred before any Review-subject freeze existed for that
Change (see Discovery, "Would an existing validator have caught it?").

**Observed Effect.** The actual, committed-or-working-tree-visible
repository mutation a delegate Execution produced, computed the same
Git-native way `_reviewable_workspace_delta`/`_resolution_delta` already
compute a diff today (`src/forge_cli/validation/__init__.py`): committed
deltas, staged deltas, unstaged deltas, tracked deletions/renames, and
Git-visible untracked files, excluding Git-ignored paths.

**Out-of-Scope Mutation.** An Observed Effect path not covered by the
Execution's declared Authorized Scope. Directly generalizes Protocol 2
§11's existing term of the same name from "Resolution Delta vs Resolution
Scope" to "any delegate Execution's Observed Effect vs its Authorized
Scope."

**Authority Violation.** Any of: an Out-of-Scope Mutation; an Execution
mutating an Authority-Defining Artifact that governs its own current
delegation (self-authorization, FR-006); or a delegation whose granted
Authorized Scope exceeds the delegator's own (Delegation Ceiling breach,
FR-007).

**Authority-Defining Artifact.** Any Forge Change Artifact whose content
declares, evidences, or grants Authority for an Execution — at minimum
`manifest.yml`'s `flow`, `state`, `review`, and `decisions` fields,
`provenance.yml`, and any Review or Decision record. Defined by function,
not by a fixed enumerated filename list, so the rule in FR-006 remains
correct as new Artifact types are introduced (originating instruction §10).

**Declared / Recorded / Verified.** Reuses Protocol 2 §4's existing
`assurance` vocabulary (`claimed`/`recorded`/`verified`) rather than
introducing the originating instruction's suggested `declared/enforced/
verified` triad as new terms — see FR-014 for why the existing vocabulary
already says what is needed and a fourth new term is unnecessary duplication.

**Delegation Ceiling.** The invariant that a delegating Execution's granted
Authorized Scope to a delegate MUST NOT exceed its own Authorized Scope
(FR-007, INV-003).

## Conceptual model

```
Human
  |  (root delegation; not bounded by Delegation Ceiling)
  v
Primary Execution  --- Authorized Scope S0 (from Human's Intent/Flow/stage)
  |  (delegates; grantable scope <= S0)
  v
Delegate Execution (e.g. research subagent) --- Authorized Scope S1 (S1 subset-or-eq S0)
  |  (may further delegate; grantable scope <= S1)
  v
Nested Delegate --- Authorized Scope S2 (S2 subset-or-eq S1)
```

For any Execution in the chain:

```
Execution Boundary opens (baseline captured)
        |
     Execution runs, using whatever Capability it happens to hold
        |
Execution Boundary closes (Observed Effect computed as a diff)
        |
Observed Effect ⊆ Authorized Scope ?
     /                    \
   yes                     no
    |                       |
 valid product      Authority Violation (FR-012):
                     evidence preserved, product not
                     silently accepted, Unresolved
                     Decision opened when restoration
                     is not deterministically safe
```

This directly matches the two canonical chains the originating instruction
names in §33; nothing here invents a third.

## Functional requirements

### FR-001 — Authority is a declared property distinct from Capability

Every delegation covered by this mechanism MUST have a determinable
Authorized Scope, recorded as data, not only as a natural-language
instruction. A natural-language-only boundary (exactly what the motivating
incident had) does not satisfy this requirement. "Covered by this
mechanism" has two independent boundaries: a subject-matter boundary
(FR-017 — repository/Git-observable mutation only, in v1) and a
rollout-timing boundary, resolved by DEC-001 (human decision,
Alternative 4): mandatory immediately for delegations a primary Execution
creates to a distinct sub-Execution, not for a primary Execution's own
direct, undelegated work.

### FR-002 — Capability MUST NOT be treated as Authority

Forge Core, validators, and normative documentation MUST NOT infer, and
MUST NOT permit an Execution to claim, that possessing a technical
Capability (filesystem write access, shell access, Git access) constitutes
Authority to exercise it for a given delegation. This is the direct
Contract-level statement of the property in the originating instruction's
§33 and Discovery's confirmed finding that the Adapter capability model is
unrelated to this concept.

### FR-003 — Authorized Scope is representable for any delegated Execution

Forge MUST be able to represent an Authorized Scope (a set of exact
repository-relative paths, or an explicitly empty write set for read-only
delegation) for a delegated Execution, reusing `forge/execution-
provenance@1`'s existing `scope` field, generalized in interpretation (not
in shape) beyond `role: resolution`. Wildcard/glob scope declarations
remain disallowed for the same reason Protocol 2 §11 already disallows
them for Resolution Scope: a broad-enough glob defeats the purpose entirely.

### FR-004 — Execution Boundary generalizes beyond Review-subject freeze
(recommended; formally pending DEC-002)

This Specification's recommended position, carried at `high` Confidence
into DEC-002 below, is: Forge MUST be able to compute an Observed Effect
for a delegated Execution independent of Change lifecycle stage —
including before any Review-subject freeze exists (e.g., during Discovery,
exactly where the motivating incident occurred) — generalizing the
existing freeze-and-diff mechanism (`_reviewable_workspace_delta`,
`_resolution_delta`) from "frozen commit vs. current workspace" to
"delegation-start baseline vs. delegation-end state," using the same
Git-native primitives (committed/staged/unstaged/untracked diffing,
Git-ignore exclusion) already proven correct for the narrower case.

This FR is stated in normative `MUST` language because that is what the
recommended design requires *if adopted*, matching how every other FR in
this Specification is phrased — but its adoption is not yet a Decision:
`decision.yml`'s ownership rule assigns this question's Class
(`architectural`) to Architecture, which does not exist yet in this
Change (DEC-002, R006). Every other requirement in this Specification that
depends on Execution Boundary reaching pre-freeze stages (this one
specifically) is therefore provisional on Architecture ratifying or
overriding DEC-002's Recommendation — every requirement that does *not*
depend on pre-freeze reach (FR-001, FR-002, FR-005 through FR-017) is not
affected by DEC-002 either way.

### FR-005 — Out-of-Scope Mutation MUST NOT be silently valid

Any Observed Effect path outside a delegated Execution's Authorized Scope
is an Out-of-Scope Mutation. A Change, Gate, or Review MUST NOT treat an
Execution's product as validly produced while an unresolved Out-of-Scope
Mutation attributable to it exists, directly generalizing C-047/C-048's
existing Out-of-Scope Mutation handling for Resolution to any delegated
Execution.

### FR-006 — Self-authorization is prohibited

An Execution MUST NOT use write access to an Authority-Defining Artifact to
**declare or expand** the Authority governing its own current delegation
beyond what was actually granted by its delegator. This is the direct
Contract-level closure of the originating instruction's §16 concern ("o
agente pode modificar o próprio documento que define quais operações ele
está autorizado a executar") and is structurally the same shape as C-026:
just as a Resolver must not review its own Resolution, an Execution must
not author the grant of its own Authority.

This is narrower than "MUST NOT mutate an Authority-Defining Artifact" at
all — that broader phrasing would contradict existing, sanctioned Protocol
2 practice: an Execution routinely and legitimately writes its own
self-recorded provenance record into `provenance.yml` (`assurance:
recorded, observed_by: self`, the Protocol 2 §4 norm, exercised by every
`implementation-*`/`review-*` record in every existing `provenance.yml` in
this repository), and a Reviewer legitimately appends review-control
metadata under Protocol 2 §5's existing exception. Both are **self-
attestation of Authority already granted and of action actually taken**,
not self-expansion of Authority — and both remain permitted. FR-006
prohibits only the latter: using that same write access to change what
Scope a record *claims was granted*, as opposed to recording what actually
happened under a Scope granted by someone else.

### FR-007 — Delegation Ceiling

A delegating Execution MUST NOT grant a delegate an Authorized Scope
exceeding its own current Authorized Scope. This is adopted as a
requirement, not left open, because rejecting it would allow trivial
privilege escalation through an added delegation hop — a classic confused-
deputy pattern the originating instruction's §24 explicitly asks this
Specification to guard against — and no legitimate engineering scenario in
this repository's Discovery required a delegate to hold broader Authority
than its delegator. The Human root of a delegation chain is exempt (see
Delegation terminology above): the ceiling bounds Agent-to-Agent delegation,
not Human-to-primary-Execution authorization.

This invariant is only checkable when the delegator's own Authorized Scope
has a value to compare against. Per DEC-001's resolution, a primary
Execution's own Scope is *not* required to be declared by FR-001 (only
its grants to sub-Executions are); an undeclared delegator Scope
MUST NOT be treated as unbounded for the purpose of checking a grant to a
delegate — doing so would silently defeat this invariant exactly where it
matters most (a primary Execution delegating to a subagent, the incident's
own shape) by letting an absence of declaration stand in for infinite
Authority. Architecture MUST define a conservative default (for example,
the delegating Change's own governed Artifact and source paths, not the
full repository) rather than leaving this case fail-open; this
Specification requires only that the default be conservative, not that
Architecture pick a specific one here.

### FR-008 — Nested delegation inherits and narrows only

At every depth, a sub-delegate's Authorized Scope MUST be a subset of its
immediate delegator's Authorized Scope (FR-007 applied recursively).
Provenance for a delegated Execution SHOULD record which Execution
delegated it, so a delegation chain is reconstructable; this Specification
does not mandate a specific chain-encoding shape (deferred to Architecture).

### FR-009 — Attribution has graduated assurance

Forge MUST be able to record, for an Execution producing a repository
mutation, at minimum a `claimed` identity and declared Scope (self-
asserted); `recorded` when self-recorded as durable repository-native
provenance (today's Protocol 2 minimum for `review_passed`); and `verified`
when a harness or Adapter independently observed and can attest to the
Execution's actual boundary (e.g., a harness-enforced sandbox). This reuses
Protocol 2 §4's existing three-level vocabulary rather than adding new
terms (see Terminology).

### FR-010 — Harness-enforced prevention is an optional strengthening

Where an installed Harness Adapter declares (or a future capability
addition allows it to declare) a capability equivalent to technically
constraining a delegate Execution's effective Capability to match its
Authorized Scope (e.g., a genuinely read-only sub-Execution mode, a scoped
filesystem sandbox), Forge Adapters MAY project a delegation's Authorized
Scope into that mechanism. This MUST remain MAY, not MUST: Discovery
confirmed the Codex Adapter declares `agent_roles: false` and no Claude
Code Adapter — the harness the motivating incident and this very Change
run under — exists at all. A MUST here would be an unenforceable, false
guarantee (originating instruction §32/§8.1).

### FR-011 — Post-execution effect verification is the mandatory floor

Independent of any harness Prevention capability, Forge Core MUST be able
to determine, using only local Git-native repository state (no harness
cooperation, no external service, consistent with C-037/C-038/ARCHITECTURE
§21), whether a delegated Execution's Observed Effect stayed within its
declared Authorized Scope. This is the harness-agnostic baseline every
supported harness gets for free, and is a direct generalization of the
already-proven `_resolution_delta`/`_uncovered_paths` mechanism (FR-004).
This requirement holds for a single attributable Execution Boundary; its
behavior under concurrent Executions mutating the same working tree is a
distinct, currently unresolved question (see "Deferred to Architecture" —
TOCTOU/concurrency), bounded in the interim only by FR-013's fail-closed
default.

### FR-012 — Authority Violation failure semantics

Detecting an Authority Violation MUST:

- prevent the affected Execution's product from being silently treated as
  a valid, accepted Change contribution;
- preserve the Observed Effect (the diff) as evidence rather than
  discarding it, so it remains auditable — an automatic silent rollback
  that destroys the diff before it is recorded MUST NOT be the only
  response;
- when the prior state can be restored deterministically and safely (e.g.,
  the Out-of-Scope Mutation is isolated, uncommitted, and does not overlap
  in-progress legitimate work), restoration MAY proceed, with the violation
  and the discarded diff both recorded;
- when safe deterministic restoration is not established, or the violation
  is structurally ambiguous (e.g., overlapping legitimate concurrent
  mutation — see FR-011's concurrency caveat below), Forge MUST record an
  Unresolved Decision rather than guess. `protocol/policies/decision.yml`'s
  `materiality.material_when_changes` already lists `security_posture` and
  `ownership_or_authority_boundary` — an Authority Violation is material by
  existing policy without this Specification needing to argue the point.
- an Authority Violation is not automatically a BLOCKER Review Finding by
  construction (this Specification does not create a second parallel
  severity system); where it surfaces during Strict Review, existing
  Finding severity and evidence rules (C-025, `protocol/policies/
  review.yml`) apply to it like any other Finding, informed by the
  preserved evidence above.

### FR-013 — Fail-closed default for indeterminate authorization

When Forge cannot reliably determine whether an Observed Effect was
authorized — most concretely, when the Git history needed to establish a
delegation's baseline is shallow or unavailable — Core MUST treat that
Execution's product as not verified and MUST NOT default to treating it as
authorized. This is not a new posture invented for this Change; it is the
same fail-closed rule Protocol 2 §5 already states for review-subject
baselines ("Core MUST fail closed" when required Git history is
unavailable), applied to the same underlying data need. Project
configuration MUST NOT relax this default (C-042; `security_posture` is
already a `may_not_relax_below_human_for`-adjacent concern by its
materiality classification).

### FR-014 — Harness honesty

Forge, Adapters, and generated Harness projections MUST NOT represent a
Detection-only outcome (FR-011) as if it were Prevention (FR-010).
User/agent-facing language describing authority enforcement MUST be
qualifiable by the same `claimed`/`recorded`/`verified` assurance level
already used for provenance (FR-009), so "this delegation's scope was
enforced" and "this delegation's scope was checked after the fact" remain
distinguishable statements. This directly satisfies AC-08 without inventing
new vocabulary Protocol 2 does not already have.

### FR-015 — Backward compatibility

An Execution or Change instance that predates this Change's mechanism, or
that does not declare an Authorized Scope, is unaffected by FR-001–FR-014
and remains valid exactly as before. These invariants bind prospectively,
once a Change or Execution actually participates in the mechanism —
identical in shape to how C-047–C-050 bind "only once a Change opts into
Resolution Verification classification" and C-051–C-059 bind "only once a
Change records a `decisions[]` entry." No historical Change (`CHG-0001`–
`CHG-0014`) is retroactively invalidated (AC-10).

### FR-016 — Authority-Defining Artifacts are defined functionally

FR-006 applies to any Artifact meeting the Authority-Defining Artifact
definition above, not to a fixed enumerated filename list. A future new
Artifact type that declares or evidences Authority is automatically
in-scope without a Specification amendment.

### FR-017 — Effect boundary of this mechanism (v1)

This mechanism governs repository filesystem and Git-observable mutation
of Forge-governed material only. Network operations, external service
calls, PR/issue mutation, and other non-repository side effects are
explicitly out of scope for v1 (Intent Non-goals) and MUST NOT be
represented, implied, or silently assumed as covered by any authority
declaration this mechanism produces.

## Invariants

### INV-001 — Capability is not Authority

No Core validation, Gate, or documentation MAY treat evidence of technical
Capability as evidence of Authority.

### INV-002 — No self-authorization

No Execution's product satisfies FR-005/validity while it includes a
mutation that declares or expands the Authority-Defining Artifact content
governing that same Execution's current delegation (FR-006). A mutation
that only self-attests an Execution's own already-granted Authority or
already-performed action (e.g., a self-recorded provenance record, or a
review-control-metadata update under Protocol 2 §5's existing exception)
does not by itself violate this invariant.

### INV-003 — Delegation Ceiling holds at every depth

For every delegation edge in a chain, the delegate's Authorized Scope is a
subset of the delegator's Authorized Scope, checked transitively.

### INV-004 — Out-of-Scope Mutation blocks silent validity

No Out-of-Scope Mutation is part of a Change's accepted product without
either a recorded Resolution bringing it in scope, an explicit Unresolved
Decision, or a recorded restoration — never by omission.

### INV-005 — Fail-closed on indeterminacy

Indeterminate authorization state MUST NOT resolve to "authorized" by
default at any Gate this mechanism participates in.

## Unresolved Decisions

Two genuine multi-alternative material questions were found while writing
this Specification. Per `protocol/specification.md` (Unresolved Decision
Management, C-051–C-059) and this Change's own Non-goal against choosing
silently, both were recorded as Decision records rather than resolved by
authorial preference alone. `DEC-001` was subsequently resolved by an
explicit human act during this same session, after Adversarial
Specification Review; `DEC-002` remains open, owned by the not-yet-existing
Architecture artifact (see `specification-review.md` R006).

### DEC-001 — Rollout posture: mandatory-by-default vs. phased adoption

**Question.** Once this mechanism exists (post-Architecture/Implementation),
should declaring an Authorized Scope become a mandatory new Contract
obligation immediately for every delegation Forge's lifecycle can observe,
or should it roll out phased (e.g., required only for FULL-flow Changes
first, or only opt-in via project configuration, expanding later)?

**Class.** `contract` — this determines whether a new Contract-level MUST
applies universally. **Materiality.** `material` (`security_posture`,
`domain_invariant` per `protocol/policies/decision.yml`). **Authority.**
`human` — `decision.yml`'s `authority_floor` fixes `contract`-class
Decisions to human authority regardless of project override; this cannot be
resolved autonomously (C-055).

**Alternatives.**

1. **Mandatory immediately, all Flows.** Every delegation this mechanism
   can observe must declare Scope from the first Change that ships this
   capability onward. Strongest closure of the exact gap the incident
   exposed; highest immediate ceremony, including for small FAST-flow
   delegations that today carry none.
2. **Mandatory immediately, FULL flow only; STANDARD/FAST unaffected until
   a later Change extends it.** Matches this Change's own FULL classification
   and the precedent that FAST explicitly disqualifies `architectural_
   change`/`security_model_change` work — but the motivating incident
   happened inside a STANDARD-flow Change (`CHG-0014`), so this alternative
   would not have prevented the actual incident that motivated the Change.
3. **Opt-in via project configuration (`.forge/forge.yml`), default off.**
   Lowest ceremony and risk of breaking existing dogfooding flow; weakest
   guarantee — a project that never opts in gets no protection at all,
   which is arguably true of every historical Change including the one that
   was harmed.
4. **Mandatory immediately, but only for delegations a primary Execution
   creates to a distinct sub-Execution (subagent or equivalent) — not for
   the primary Execution's own direct, undelegated work.** Targets exactly
   the incident's shape without adding declaration ceremony to the common
   case of one Execution working directly, which Protocol 2's existing
   `implementation`/`resolution`/`review` provenance already covers
   adequately. Narrower than Alternative 1, and — unlike Alternative 2 —
   applies regardless of Flow, so it would have covered the actual
   `CHG-0014` incident (a STANDARD-flow Change).

**Trade-offs.** Alternative 1 best satisfies C-039's "material engineering
value" only if the ceremony cost is actually proportional — Discovery found
no existing per-delegation declaration UX to build on, so "mandatory
immediately" has real, currently-unmeasured authoring cost. Alternative 2
is internally inconsistent with this Change's own motivating evidence.
Alternative 3 risks the mechanism existing but never actually protecting
anything, which would fail this Specification's own quality bar
(originating instruction §34, "não considere a Change bem-sucedida apenas
porque existe... um campo").

**Recommendation.** Alternative 4. **Confidence: medium** —
sound as an engineering position given available evidence, but this
Specification cannot verify actual authoring-ceremony cost without a
working prototype, which is Architecture/Implementation-stage work, not
available yet.

**Status.** `resolved`, `resolved_via: human_decision`. Owning Artifact:
this Specification — `decision.yml`'s `owning_artifact_by_class` assigns
`contract`-class questions to Specification.

**Decision.** Alternative 4, accepted as presented (`decision ==
recommendation`, permitted under FR-009's non-laundering rule because
`resolved_via: human_decision` records an actual human act, not an
autonomous one): declaring an Authorized Scope becomes a mandatory new
Contract obligation immediately, but only for delegations a primary
Execution creates to a distinct sub-Execution (subagent or equivalent) —
not for a primary Execution's own direct, undelegated work. Recorded via
the human's explicit selection among the four Alternatives above (not an
open-ended "proceed"), matching FR-010's structured-alternatives
presentation format and C-055's requirement that a human-authority Decision
reach `resolved` only through an explicit human act.

**Consequence.** With DEC-001 resolved, `forge validate`'s C-051 finding
against this Change's own manifest (`specification_review_passed` withheld
while DEC-001 was `awaiting_decision`) is expected to clear — re-verified
directly below, not merely asserted. Architecture, when it begins, MUST
treat "mandatory for sub-delegations, not for direct Execution work" as the
settled rollout boundary for whatever concrete mechanism it designs;
revisiting DEC-001 itself would require a new Decision, not a silent
Architecture-stage override.

### DEC-002 — Lifecycle coverage boundary: does v1 reach pre-freeze stages?

**Question.** Should this mechanism's Execution Boundary (FR-004) cover
delegations occurring before any Change lifecycle Gate has frozen a
subject (i.e., during Intent/Discovery, exactly where the motivating
incident occurred), or should v1 be limited to stages where frozen-subject/
provenance machinery already exists (Implementation, Resolution, Review),
leaving pre-freeze coverage as documented future work?

**Class.** `architectural`. **Materiality.** `material`
(`ownership_or_authority_boundary`, `domain_invariant`). **Authority.**
`agent_with_review` per `decision.yml`'s default for `architectural`
Decisions. This Authority level governs *who* may resolve it, not *when* —
`decision.yml`'s `owning_artifact_by_class` fixes the owning Artifact for
`architectural` questions to **Architecture**, not Specification, and
`ownership.downstream_must_not_resolve_upstream_owned_decision` (C-052)
means Specification MUST NOT resolve a Decision it does not own even when
it holds sufficient Authority in the abstract — ownership and authority are
independent axes. This Specification's own first draft got this wrong (see
`specification-review.md` R006) by resolving DEC-002 here directly; running
`forge validate` against this Change's own manifest caught it mechanically
(a C-051 finding), which is itself a small, direct demonstration of this
Change's own thesis: a self-declared resolution is not the same as a
verified one.

**Alternatives considered.**

1. Limit v1 to post-freeze stages only (reuse Protocol 2 §5 machinery
   as-is, extended only to non-`resolution` roles).
2. Cover every lifecycle stage via a stage-agnostic Execution Boundary
   (FR-004), independent of whether any Review-subject freeze exists yet.

**Trade-offs.** Alternative 1 is less new machinery (pure reuse) but
explicitly does not cover the incident that motivated this Change — a
mechanism that cannot detect the exact failure mode it was commissioned to
address fails this Specification's own quality bar (originating
instruction §34, criterion 10: "resolve a classe de problema revelada pelo
incidente original"). Alternative 2 requires generalizing the diff
mechanism's anchor from "a frozen commit" to "a delegation's own start/end
boundary," which Discovery found is a natural generalization of already-
proven Git-native primitives (`_reviewable_workspace_delta`'s existing
committed/staged/unstaged/untracked diffing), not a new invention.

**Recommendation.** Alternative 2, **Confidence: high** — Discovery
established the generalization as a natural, low-risk extension of
already-proven Git-native primitives, and Alternative 1 concretely fails to
cover the incident that motivated this Change. This is a Recommendation,
not a Decision (C-054): DEC-002's owning Artifact is Architecture, which
does not exist yet in this Change. **Status: `open`**, `owning_artifact:
architecture`, `discovered_in: specification`. Architecture MUST resolve
this Decision (accepting, rejecting, or refining this Recommendation) as
part of its own stage; it is not resolved by this Specification, and does
not block entry into Architecture (`before_architecture`'s dependency set
does not include the Architecture artifact itself), but MUST resolve
before the Architecture Gate itself may pass (C-051).

## Compatibility

- `forge/execution-provenance@1`'s `scope` and `targets` fields are already
  schema-unrestricted by `role` — only Protocol 2 §11 prose narrows their
  interpretation to `role: resolution`. Extending their interpretation to
  cover any delegated Execution (FR-003) requires a Protocol/Contract text
  change, not a schema change, for that part.
- Representing a delegation chain (FR-008, "who delegated whom") and an
  explicit Authorized-Scope-vs-Capability distinction on a provenance
  record are genuinely new data this Change's eventual Architecture will
  need a field for. Per `protocol/compatibility.md`'s independent-axes
  rule, this is additive schema surface and belongs in a new schema suffix
  (`forge/execution-provenance@2`), not a new integer Protocol version,
  provided (a) it does not retroactively require the field on historical
  `@1` records (`@1` remains valid, exactly as `forge/change@1` remains
  valid alongside `@2`), and (b) DEC-001's resolution (mandatory for
  sub-delegations only) binds only prospectively (FR-015). Both conditions
  are satisfiable by
  construction, following the exact precedent `CHG-0008`/`CHG-0011` already
  set for `forge/change@1` → `@2` and C-047–C-059's additive-invariant
  pattern.
- New Contract invariants FR-002/FR-005/FR-006/FR-007/FR-011/FR-013 as
  stated are new `MUST`s. Per `protocol/compatibility.md`'s breaking-change
  test, none of them "remove or weaken" an existing invariant, "make a
  previously optional field... mandatory for existing instances" (they bind
  new/opted-in delegations only, not historical ones), or "invalidate a
  previously valid conforming instance." No new integer Protocol identifier
  is required by this Specification as currently scoped. Architecture MUST
  re-verify this conclusion once concrete schema/field shapes are chosen
  (originating instruction §18) — this Specification's compatibility
  analysis is necessary but not sufficient; it does not replace
  Architecture's own pass.
- No historical Change (`CHG-0001`–`CHG-0014`) declares any Authorized
  Scope today; none becomes non-conforming (AC-10).
- `forge/execution-provenance@1`'s `role` enum is closed to
  `implementation`/`resolution`/`review` (`protocol/schemas/execution-
  provenance.schema.json`). None of these fits a non-review-cycle delegated
  Execution such as the incident's research subagent. Representing such an
  Execution's provenance under this mechanism therefore also requires
  either widening the `role` enum or introducing a distinct, additional
  provenance concept for delegated (non-Role) Executions — an open schema
  question left to Architecture, not resolved by this Specification, and
  listed accordingly below.

## Deferred to Architecture (explicitly not decided here)

Per this Change's own boundary and the originating instruction §5/§22, the
following remain open and MUST NOT be treated as decided by this
Specification:

- The exact new schema field names/shapes for Authorized Scope-on-any-role,
  delegation-chain encoding, and Execution Boundary baseline capture,
  including whether `forge/execution-provenance@2`'s `role` enum widens to
  admit non-Review-cycle delegated Executions or a distinct provenance
  concept is introduced instead (Compatibility, above).
- Which concrete harness/Adapter mechanisms (if any) satisfy FR-010's MAY
  for Prevention, and how an Adapter would declare that capability (a new
  boolean in `adapter.schema.json`'s `capabilities`? a new artifact? —
  undecided).
- TOCTOU/concurrency handling specifics for FR-004/FR-011 when multiple
  Executions mutate the repository concurrently or use separate worktrees
  — the originating instruction §23's concern is real and unresolved; this
  Specification only requires (FR-013) that indeterminate attribution
  fail closed, not that concurrency be fully solved.
- Exact CLI/validator implementation surface (new `validation/__init__.py`
  functions, new `forge validate` findings codes, whether a new Contract
  rule ID range like C-060+ is allocated — allocation itself is
  Architecture/Implementation bookkeeping, not a Specification concern).
- Whether an ADR is required: `protocol/policies/architecture.yml`'s
  `adr.required_when` includes `core_boundary_changes`, which this
  Specification's subject plausibly is — Architecture stage makes that
  determination with the concrete design in hand, not Specification in the
  abstract.

## Acceptance criteria

- **AC-001** (= originating AC-01, explicit delegation boundary): A
  delegation this mechanism covers has a determinable Authorized Scope
  recorded as data (FR-001, FR-003), not only as a natural-language
  instruction.
- **AC-002** (= AC-02, capability is not authority): No Core validation
  path infers authorization from technical capability (FR-002, INV-001).
- **AC-003** (= AC-03, unauthorized mutation detection): A covered
  delegation declared without write Authority that nonetheless mutates
  Forge-governed content cannot conclude as a silently accepted, valid
  product (FR-005, FR-012, INV-004) — the direct acceptance test for the
  incident class itself.
- **AC-004** (= AC-04, scoped writes): Forge can represent Authority
  limited to a declared subset of paths, not only a binary read/write
  split (FR-003, Terminology "Authorized Scope").
- **AC-005** (= AC-05, escalation protection): An Execution cannot expand
  its own Authority via an Artifact it is permitted to modify for other
  reasons (FR-006, INV-002).
- **AC-006** (= AC-06, delegation ceiling): A delegator cannot grant
  Authority it does not itself hold (FR-007/FR-008, INV-003) — adopted, not
  rejected; rationale given inline at FR-007 rather than as a separate
  Unresolved Decision, since Discovery found no legitimate scenario
  requiring its rejection.
- **AC-007** (= AC-07, evidence preservation): An Authority Violation's
  Observed Effect is preserved as evidence, not silently discarded
  (FR-012).
- **AC-008** (= AC-08, harness honesty): No statement of enforcement
  overstates Detection as Prevention (FR-010, FR-011, FR-014).
- **AC-009** (= AC-09, lifecycle integration): This mechanism uses the
  existing Change lifecycle, existing provenance schema family, and
  existing Unresolved Decision Management rather than a second parallel
  workflow (Compatibility section; FR-003/FR-004 build on existing
  primitives).
- **AC-010** (= AC-10, historical compatibility): `CHG-0001`–`CHG-0014`
  remain valid, unaffected instances (FR-015, Compatibility).
- **AC-011** (= AC-11, independent verification): Future Test Strategy
  (next FULL stage) must demonstrate detection mechanically (e.g., a real
  Git-backed fixture with an actual Out-of-Scope Mutation observed and
  flagged), not merely assert that instructional prompt text forbids
  mutation. This Specification does not itself contain tests (Test
  Strategy is a distinct, later FULL stage) but constrains what that stage
  must prove.
- **AC-012** (= AC-12, original incident class): A future Test Strategy
  MUST include a scenario semantically equivalent to the motivating
  incident — a delegation restricted to research/read-only Authority whose
  delegate attempts to mutate a Forge Artifact outside that Scope — verified
  mechanically (FR-004/FR-011), independent of any specific AI provider,
  matching FR-004's stage-agnostic Execution Boundary so the scenario can
  be anchored at a Discovery-equivalent (pre-freeze) point, not only at a
  post-freeze Review point.

## Representative scenarios for the future Test Strategy (non-normative)

Recorded here so Test Strategy does not have to rediscover them: read-only
delegate that only reads (valid); read-only delegate that writes (AC-012);
scoped writer within its declared paths (valid); scoped writer outside its
declared paths (AC-003); an Execution attempting to edit the Artifact
defining its own Authority (AC-005); a delegator attempting to grant
broader Authority than it holds (AC-006); nested delegation narrowing
correctly and nested delegation attempting to widen (AC-006 at depth);
mutation of an Authority-Defining Artifact under Protocol 2's existing
review-control-metadata exception (must remain distinguishable from a
genuine self-authorization attempt); a harness with no enforcement
capability (Detection-only path, AC-008); a harness capable of Prevention
(FR-010 path, if/when an Architecture-stage Adapter capability exists);
violation surfaced only after the fact vs. an attempted violation that the
Execution itself reverts before completion (does self-correction change
auditability — left for Test Strategy to decide, not prejudged here);
concurrent/untracked-file edge cases per the TOCTOU deferral above.
