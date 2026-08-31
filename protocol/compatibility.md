# Forge Protocol Compatibility

Status: Stable

This document defines the compatibility boundary between integer Forge Protocol versions. Protocol version and artifact schema version are independent axes.

## Independent versions

Forge has four independent version axes:

- **Protocol version** — integer Core semantic compatibility contract used by projects and Adapters.
- **Schema version** — suffix in an artifact identifier such as `forge/change@1` or `forge/change@2`; it versions that artifact shape, not the entire Protocol.
- **CLI version** — Semantic Versioning of the installable implementation.
- **Adapter version** — Adapter-specific Semantic Versioning, with an explicit half-open Protocol interval.

A schema suffix MUST NOT be used to conceal a breaking Core semantic change that belongs at the integer Protocol boundary.

## Protocol 1 — frozen semantic meaning

Protocol 1 remains valid and preserves its published meaning. In particular, C-026 means that Reviewer and Resolver are distinct conceptual Roles. Protocol 1 does not retroactively require independent Execution identifiers, independent Execution Context identifiers, revision-bound provenance, or a provenance ledger.

Previously valid conforming Protocol 1 projects and completed Change instances MUST remain valid merely because Protocol 2 exists. `forge/change@1` preserves its historical shape and meaning.

Compatible Protocol 1 maintenance may still include editorial corrections, implementation fixes that enforce already-published semantics, optional artifacts whose absence preserves existing meaning, and independently versioned schema additions that do not invalidate Protocol 1 instances.

## Protocol 2 — review-independence boundary

Protocol 2 intentionally strengthens Strict Review from conceptual Role separation to revision-bound independent Execution and Execution Context provenance. Because this invalidates states that were valid under Protocol 1, the stronger obligation is identified as integer Protocol `2` rather than being relabeled as a compatible Protocol 1 revision.

Protocol 2 active Changes use `forge/change@2` and declare `protocol: 2`. A Protocol 2 repository MAY retain completed historical `forge/change@1` Changes without retroactive migration or fabricated provenance. An active Protocol 2 Change MUST NOT downgrade to `forge/change@1` to bypass the Protocol 2 Strict Review Gate.

The `forge/execution-provenance@1` artifact is the repository-native ledger for Protocol 2 execution records. Its schema version is independent from Protocol 2; a future compatible provenance shape could receive another schema suffix without necessarily creating Protocol 3.

## Breaking Protocol evolution

A new integer Protocol identifier is required to:

- remove or weaken a Contract invariant;
- remove a previously supported required capability or artifact;
- make a previously optional field or evidence source mandatory for existing instances;
- change the meaning of an existing required field, stage, Gate, severity, or ownership mode;
- invalidate a previously valid conforming instance;
- change Adapter compatibility interval semantics;
- authorize a Flow to bypass applicable TDD/RED, Verification, Strict Review, blocking external-review reconciliation, Documentation Impact, or truthful Completion.

If an artifact-shape change also changes Core semantic obligations, both the relevant schema version and integer Protocol version must be selected correctly.

## Deprecation

A deprecation record must state the affected construct, replacement or migration path, first release or Protocol revision marking it deprecated, compatibility period, and earliest removal boundary. Deprecation does not authorize early removal.

## Stable lifecycle vocabulary

Protocol 1 and Protocol 2 both retain FAST, STANDARD, and FULL and the common quality obligations: applicable TDD, Verification beyond passing tests, adversarial Strict Review, blocking-thread reconciliation on active external review surfaces, Documentation Impact evaluation, and truthful Completion.

Protocol 2 adds the same review-provenance quality invariant to FAST, STANDARD, and FULL. FAST reduces ceremony, not quality.

## Protocol 2 — Resolution Verification boundary (CHG-0011)

CHG-0011 adds Resolution Verification scoping and review convergence
termination semantics entirely as optional fields on `forge/change@2`
(`review.iterations[].kind`, `.full_review_required`,
`.new_material_findings`, `.finding_classes`, top-level `review.convergence`)
and `forge/execution-provenance@1` (`scope`, `targets`). No integer Protocol
identifier changes and no new schema suffix is introduced. This falls under
"optional artifacts whose absence preserves existing meaning": it removes no
invariant, changes the meaning of no existing required field, and does not
invalidate a previously valid conforming instance — verified directly
against this repository's own `CHG-0008` (completed) and `CHG-0010`
(in-flight) manifests, neither of which sets any of the new fields and both
of which continue to validate unchanged. A manifest that never declares
`kind` makes no claim this Change's new Contract rules (C-047–C-050) speak
to, and is therefore unaffected by them. There is no migration and no future
intent to force `kind` classification onto historical or Protocol 1 data;
legacy semantics are permanent, not a transitional grace period.

## Unresolved Decision Management (CHG-0013)

CHG-0013 adds a top-level, optional `decisions` array to both `forge/change@1`
and `forge/change@2`, a new `forge/policy/decision@1` canonical Policy, and
Contract rules C-051–C-059. Unlike CHG-0011, this capability is not scoped to
Protocol 2: it depends on nothing in Protocol 2's Execution/Context
independence model, so it applies identically to a Protocol 1 or Protocol 2
project and its Contract rules live in the shared canonical
`protocol/contract/engineering.md`. This is again "optional artifacts whose
absence preserves existing meaning": every historical manifest in this
repository (`CHG-0001`–`CHG-0012`) declares no `decisions` field and
continues to validate and mean exactly what it meant before. No integer
Protocol identifier changes and no new `forge/change@N` schema suffix is
introduced.

This Change also backfills C-047–C-050 (introduced by CHG-0011) into
`protocol/versions/2/contract/engineering.md`, which — despite CHG-0011's own
`discovery.md` asserting otherwise — already existed at the time CHG-0011
was authored and is the file `resolve_effective_contract` actually resolves
for a `protocol: 2` project (as this repository's own `.forge/forge.yml`
declares). The backfill copies already-normative, already-shipped rule text
into the one place Protocol 2's own resolver requires it; it changes no rule's
meaning and adds no new obligation beyond what `protocol/contract/engineering.md`
already stated.

## Delegated Execution Authority (CHG-0015)

CHG-0015 adds `forge/execution-provenance@2`, a new schema suffix additive
over `@1`: `role` gains `delegated_task`; `execution` gains optional
`delegated_by`; a new optional `baseline` object; and `scope`'s `minItems`
is relaxed from `1` to unset (`0`) so a `delegated_task` record can declare
zero write Authority (`scope: []`) — a legitimate declaration `@1` could
not represent, since Resolution (`@1`'s only current `scope` consumer)
always fixes something and never needed an empty grant. `@1` itself is
unchanged and remains valid; a `@1` record's `scope`, if present, still
requires at least one entry exactly as before. This Change also adds
Contract rules C-060–C-066 to both `protocol/contract/engineering.md` and
`protocol/versions/2/contract/engineering.md`, following the same dual-file
pattern CHG-0011/CHG-0013 already established, and a new `protocol/
specification.md` §40.

Every rule in C-060–C-066 binds a Change only once it records a
`role: delegated_task` provenance entry — the same "optional artifacts
whose absence preserves existing meaning" pattern `protocol/compatibility.md`
already recognizes for CHG-0011's C-047–C-050 and CHG-0013's C-051–C-059.
Verified directly against this repository's own historical provenance:
`CHG-0001`–`CHG-0015` declare no `delegated_task` record and are
unaffected. No integer Protocol identifier changes; `forge/execution-
provenance@1` is not deprecated and continues to mean exactly what it
meant before.

## Canonical Artifact Structure (CHG-0016)

CHG-0016 adds one new canonical file, `protocol/artifact-structure.md`,
a new `protocol/specification.md` §41, and Contract rules C-067–C-069 to
both `protocol/contract/engineering.md` and `protocol/versions/2/contract/
engineering.md`, following the same dual-file pattern CHG-0011/CHG-0013/
CHG-0015 already established. Unlike CHG-0015, this Change adds no new
Schema, Schema suffix, or Gate: C-067 states explicitly that conformance
to the new guidance MUST NOT be treated as a Gate condition and MUST NOT
be validated by `forge validate`. This is the same "optional artifact
whose absence preserves existing meaning" pattern already used three
times: every historical Change (`CHG-0001`–`CHG-0015`) is silent on
`protocol/artifact-structure.md` and continues to validate and mean
exactly what it meant before. No integer Protocol identifier changes and
no new `forge/change@N` schema suffix is introduced.

This resolution reflects `CHG-0016`'s own Specification DEC-001
(`contract`-class, `human`-authority): the alternative considered —
elevating the Verification/Review outcome-heading recommendation to a
`MUST`, Gate-checked obligation — was evaluated and not selected. Had it
been selected, it would have required a new integer Protocol under this
document's own "change the meaning of an existing required field, stage,
Gate" criterion above, prospectively binding only Changes that opted into
that Protocol integer; it would not have retroactively invalidated
`CHG-0001`–`CHG-0015`, exactly as Protocol 2 itself did not retroactively
invalidate Protocol 1's completed Changes.

### CHG-0025 — Plan authorization semantics

CHG-0025 adds a prospective C-077 check for active approved Plans. It reuses
the existing Decision vocabulary and requires a Plan/provenance record, while
lower-numbered historical Changes remain valid. The rule applies to both
Protocol 1 and Protocol 2 representations without changing their schemas.

### CHG-0037 — Specification layout and optional User Stories

CHG-0037 updates the non-binding artifact-structure guidance and the new
Change scaffold's Specification presentation. It introduces no new Protocol
integer, Schema field, Gate, lifecycle stage, or Markdown validator. User
Stories are optional context; existing Requirements, Acceptance Criteria,
historical Specifications, and `traceability.yml` semantics remain valid.

### CHG-0048 — Proportional Review Profiles

CHG-0048 (RFC-0007, accepted for Protocol 2) decouples "Review is
required" from "Review is strict/adversarial": C-022 and C-023 now
scope the exhaustive adversarial-search obligation to the `strict`
Review Profile (FULL), while `focused` (FAST) and `standard`
(STANDARD) remain genuine Review with identical rejection authority on
any material Finding actually observed. This is treated as a
Protocol-2-compatible clarification, not a new Protocol integer: no
historical Change's already-recorded Review is invalidated (a
`profile`-less historical record is interpreted as `strict`, the
previously universal behavior), Reviewer/Resolver independence
(C-026), evidence requirements (C-025), Finding severities, Resolution
Verification (C-047–C-050), and the Convergence Limit are unconditioned
on profile and unchanged for all three Flows. `protocol/schemas/policy-review.schema.json`
(Protocol 1) and `protocol/contract/engineering.md` (Protocol 1) are
untouched — Review Profiles are a Protocol 2 concept only. Schema
changes are additive in three of the four touched files
(`change-v2.schema.json`'s `review.iterations[].profile`,
`policy-review-v2.schema.json`, `project-flow.schema.json`); the fourth
(`flow.schema.json`, replacing `strict`/`adversarial`'s `const: true`
with a `profile` enum plus boolean fields) narrows a previously
unconditional schema guarantee, but only three live canonical Flow
files exist to apply it to — no historical Flow-file population is
invalidated. See `docs/rfcs/0007-proportional-review-profiles.md` for the full
resolved normative question (no separate ADR: this RFC already
satisfies F-008 for this Change) and
`.forge/changes/CHG-0048-proportional-review-profiles/architecture.md`
for the component-level design.

### CHG-0050 — Review Experience Modes

CHG-0050 (RFC-0008, accepted for Protocol 2) adds a developer-facing
UX layer over CHG-0048's Review Profile model: three named Review
Experience Modes (`recommended`, default; `fast`; `thorough`),
selectable per Change (`manifest.yml` `review.mode`) and as a
persistent project preference (`.forge/forge.yml` `review.preferred_mode`).
`recommended`/`fast` always resolve to exactly the Change's existing
Flow-derived Review Profile floor; `thorough` resolves one profile
rank higher, capped at `strict` -- there is no code path by which a
mode can resolve below the floor. A new, schema-tracked
`review.current_phase` field (`scanning | findings_recorded |
resolving | re_reviewing | converged | stopped`) makes Review's
Discovery/Findings/Resolution/Re-review phases observable and
Core-validated for status consistency; `stopped` records that a
developer ended further processing and carries no Completion or
approval authority (C-035 is unmodified). A new `forge change
review-status <slug>` command reports a Change's live mode, resolved
profile, phase, and outstanding Finding counts.

All schema changes (`review.mode`, `review.current_phase` on
`change-v2.schema.json`; `review.preferred_mode` on
`project.schema.json`) are additive and optional; a manifest or project
file that predates them is interpreted exactly as before (`recommended`
mode, no phase tracked), so no historical Change's recorded Review is
invalidated or reinterpreted. No Engineering Contract text changes:
the never-below-floor guarantee is a structural property of the new
`resolve_effective_review_profile` function, not a new invariant.
`protocol/schemas/policy-review.schema.json` (Protocol 1) is untouched
-- Review Experience Modes, like the Review Profiles they sit on top
of, are a Protocol 2 concept only. See
`docs/rfcs/0008-review-experience-modes.md` for the full design (no
separate ADR: this RFC already satisfies F-008 for this Change) and
`.forge/changes/CHG-0050-review-experience-modes/architecture.md` for
the component-level design, including `DEC-004`'s correction of the
Adapter-projection mechanism from a per-Change to a per-Flow design.

## Schema catalog

`schemas/catalog.yml` is the portable list of schemas shipped by the distribution. Catalog presence does not imply that every schema is normative for every Protocol version. Applicability is defined by the selected Protocol contract and the artifact's own identifier. Cross-field semantic constraints that JSON Schema cannot express remain deterministic Core validation responsibilities.
