---
forge:
  artifact: specification
  schema: 1
change: CHG-0046
status: pending
---

# CHG-0046 · Specification

> **Change Contract**
>
> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.

## Overview

| | |
|---|---|
| **Change** | CHG-0046 |
| **Flow** | FULL |
| **Status** | Draft |

## Summary

`forge change merge-check` (the `forge-merge-readiness` CI gate) must stop
flagging MR-015 (`REVIEW SUBJECT STALE`) against a Change whose only
post-Review-freeze commits are Change-local artifacts belonging to Flow
stages that canonically run after `strict_review`, while continuing,
without regression, to flag MR-015 against any Change whose actual
implementation or pre-Review artifacts change after the freeze. Separately,
the materiality policy the gate loads must resolve the ten Agent
Adapter–generated paths identified in Discovery to a definite `material` or
`non_material` classification instead of `ambiguous` (MR-017), without
loosening the classifier's fail-closed default for any other path.

## Classification

**Flow: FULL.** This Change modifies `src/forge_cli/merge_readiness/evaluator.py`
and `protocol/policies/merge-readiness.yml` — the mechanical enforcement of
the Reviewer/Resolver independence invariant (C-026) that gates every
Change's mergeability in this repository, including this one's own.
CHG-0036, which originally built this gate, used FULL for the same reason;
this Change follows that precedent. A mistake here does not just affect one
Change's outcome, it can silently weaken (or wrongly tighten) the integrity
guarantee every future Change's merge depends on — the disqualifier profile
`fast.yml` describes (`security_model_change`, `significant_cross_module_change`)
applies directly, and STANDARD carries no explicit classification criteria
to justify a lower bar for security/integrity-adjacent tooling.

## Functional Requirements

### FR-001 · MR-015 tolerates post-freeze Change-local artifacts only when covered by an explicit, anchored renewal record
Origin: Discovery, "MR-015: the CI gate and `forge validate` implement the
same invariant, and disagree"; corrected twice — first by Specification
Review SR-001 (a per-Flow-stage artifact mapping cannot cover `tasks.md`,
a continuously-updated checklist not tied to one stage, or
`specification-drift.md`, which `protocol/artifact-structure.md:436-441`
documents as having no Flow stage or code representation at all); then by
**Specification Drift** (`specification-drift.md`), after an external,
independent reviewer (Codex, on PR #37) found that the `state.current`-keyed
temporal-boundary design SR-001 led to directly contradicts Protocol §5's
explicit text: "The only post-freeze paths that MAY differ without
renewing subject provenance are" the three literal files; "The exception
MUST NOT be inferred from... membership in the Change directory
generally." §14: "A manifest claim such as `state.current: complete`...
is not sufficient authorization."
Priority: must

#### Requirement
For a Change whose Review subject was frozen at commit `S`, MR-015 MUST NOT
report `REVIEW SUBJECT STALE` for a specific Change-local path (inside the
Change's own `.forge/changes/CHG-xxxx-*/` directory) that differs from `S`
at `head_revision`, when — and only when — an explicit provenance record
with `role: implementation` or `role: resolution` exists whose
`revision.commit` (or `revision.immutable_ref.value`) equals
`head_revision` exactly, that record is anchored (its first committed
representation is unchanged, per the same `_first_committed_record` check
MR-021 already applies to subject records), and that record declares a
`scope` (a list of exact repository-relative paths, mirroring §11's
existing `resolution` scope shape) that includes the specific path in
question. A renewal record's tolerance is scoped to exactly the paths it
names — it does not blanket-cover the Change's entire uncovered delta
merely by existing and naming the right commit. `manifest.yml`/
`provenance.yml`/`review.md` remain tolerated unconditionally, per
Protocol §5's own literal three-file exception — unchanged from before
this Change existed.

#### Expected Behavior
Per Protocol §5 ("Appending a new provenance record... remains allowed
when previously anchored subject records and Iteration subject bindings
remain unchanged") and §8 ("Completion MUST NOT occur when... the frozen
reviewable workspace has changed **without renewed provenance**" —
implying it MAY occur when provenance *is* renewed): a Change whose
Documentation Impact / Knowledge Capture stage writes Change-local
artifacts after Review passes must record an explicit new subject-
provenance entry naming the exact resulting commit, self-attested
(`assurance: recorded`, matching how `implementation-subject-001`/
`verification-001`-shaped records already work elsewhere in this Protocol)
— not rely on an implicit `state.current` flag. This is deliberately not
the `role: resolution`/`resolution_verification` mechanism (§11): that
machinery is Finding-specific (`targets` are Finding identifiers) and does
not fit ordinary Flow-scheduled bookkeeping that targets no Finding.
`manifest.state` is no longer read by MR-015 at all.

#### Boundary
This requirement governs only Change-local paths inside the Change's own
directory (AC-002 remains unaffected: this check still never inspects
`change_root`-external paths). A renewal record's mere self-attested
*existence* is what MR-015 checks — like every other self-attested
provenance record already accepted elsewhere in this Protocol (§4:
`recorded` is "the minimum for review_passed"), it is not independently
re-verified content-by-content, and is not a claim that the *content* of
whatever changed is itself correct — that remains, as always, Verification
and Strict Review's responsibility, only for the parts of the Change that
are actually reviewable material in the first place.

#### Acceptance
AC-001
Given a Change whose Review subject is frozen at commit `S`
When commits after `S` modify a Change-local path (e.g.
`knowledge-capture.md`), and a `role: implementation` provenance record,
anchored, exists with `revision.commit` equal to `head_revision` exactly
and `scope` including that exact path
Then MR-015 does not fire.

AC-007
Given the same setup as AC-001, but the renewal record's `scope` names a
different Change-local path than the one that actually changed (e.g. the
record declares `scope: [knowledge-capture.md]` but `specification.md`
also changed in the same commit)
Then MR-015 still fires — for `specification.md` specifically, since it
is outside the renewal's declared scope. A renewal record's existence
does not blanket-authorize every Change-local path changed in the same
commit, only the ones it names.

AC-002
Given the same Change and frozen commit `S`
When a commit after `S` modifies a file outside the Change's own directory
(e.g. `src/forge_cli/...`)
Then MR-015's behavior toward that file is unchanged by this Change in
either direction. **This is not a claim that MR-015 detects such a
change** — Discovery confirms it structurally cannot: its `git diff`
pathspec is `-- change_root`, so paths outside the Change's directory are
never part of what this check inspects, independent of this Change. AC-002
exists to bound this Change's own blast radius, not to assert a protection
this repository does not currently have.

AC-003
Given a Change whose Review subject is frozen at commit `S`
When a commit after `S` modifies any Change-local path outside
`manifest.yml`/`provenance.yml`/`review.md`, and **no** provenance record
of role `implementation` or `resolution` names `head_revision` exactly
Then MR-015 still fires — regardless of `manifest.yml: state.current`'s
value. There is no tolerance without an explicit, anchored renewal record;
`state.current` is never consulted.

AC-006
Given the same setup as AC-001, but the candidate renewal record is not
anchored (e.g. a later, differently-committed provenance edit claims to
redefine which record has that id, or the record was not present in the
first committed representation of `provenance.yml` that introduced its id)
Then MR-015 still fires — a renewal claim that is not itself anchored
provides no tolerance, mirroring MR-021's existing anchoring requirement
for subject records.

### FR-002 · Agent Adapter–generated paths resolve to a definite classification
Origin: Discovery, "MR-017: ten Adapter-generated paths have no
classification rule"
Priority: must

#### Requirement
`classify_path()` MUST resolve each of the ten paths identified in
Discovery — `.claude/CLAUDE.md`, `.claude/skills/forge/**`,
`.agents/skills/forge/**`, `.forge/adapters/*/installation.yml` — to
`material` or `non_material`, never `ambiguous`.

#### Expected Behavior
The classification chosen for each path family must be consistent with
what that path actually is: fully generated, digest-tracked Adapter output
whose drift is already independently detected by `forge doctor` /
`forge adapter doctor` is a different kind of change than hand-authored
source, and the policy's classification should say so explicitly rather
than defaulting to `ambiguous` for lack of a rule.

#### Boundary
This requirement resolves only the ten specific paths Discovery identified
as currently ambiguous and material to CHG-0045's PR. It does not require
auditing or reclassifying any path the policy already resolves to
`material`, `permitted`, or `change`.

#### Acceptance
AC-004
Given each of the ten paths identified in Discovery
When `classify_path()` evaluates it against the updated policy
Then it returns `material` or `non_material`, never `ambiguous`.

AC-005
Given a path not in the ten identified paths and not already matched by an
existing policy rule
When `classify_path()` evaluates it
Then it still returns `ambiguous` — the fix adds specific, scoped rules; it
does not loosen the classifier's fail-closed fallback for anything else.

## Non-functional Requirements

None. This Change alters gate logic and policy data only; it introduces no
new runtime behavior with performance, availability, or scalability
properties distinct from what `forge change merge-check` already does.

## Constraints

### CON-001
This Change MUST NOT alter the meaning of C-026 (Reviewer/Resolver
independence) or any other Engineering Contract invariant — only how
MR-015/MR-017 mechanically *detect* conformance to invariants that remain
exactly as defined in `protocol/contract/engineering.md`. No Contract edit
is in scope.

### CON-002
MR-015 MUST NOT read `manifest.yml: state.current` at all, for any
purpose — corrected by **Specification Drift** after Codex's PR #37
finding that `state.current` is exactly the "membership in the Change
directory generally"-style inference Protocol §5 forbids, and that §14
explicitly names `state.current: complete` as insufficient authorization
on its own. Tolerance for a Change-local post-freeze delta MUST instead
depend only on an explicit, individually anchored provenance record
naming the exact commit (FR-001) — auditable per-commit, not a single
mutable manifest field covering every future commit once flipped once.
This constraint superseded, not narrowed, this Constraint's two earlier
revisions (original: forbid `state.current` outright; SR-002's revision:
permit it if corroborated by MR-005/MR-016) — both were reasoning about
the wrong axis. The concern in [[project-merge-readiness-scoping-bug]]
finding 6 (a status field trusted with no corroboration) is now moot for
MR-015 specifically: there is no field to trust, only individually
anchored records.

### CON-004
Per Protocol §11, `role: resolution` remains reserved, by convention, for
records declaring `scope`/`targets` naming actual Review Findings;
non-Finding-driven Change-local bookkeeping (Documentation Impact,
Knowledge Capture) should use `role: implementation` instead. MR-015's own
mechanical check accepts either role for the renewal lookup (FR-001) —
it does not itself enforce `scope`/`targets` presence on a `role:
resolution` renewal record, since that enforcement already exists,
unmodified, for `resolution_verification` Iterations specifically
(§11, MR-018/MR-019-adjacent checks this Change does not touch). This
Constraint documents the intended authoring convention; it does not add a
new mechanical check beyond FR-001's own.

### CON-003
Both fixes apply identically across `fast`, `standard`, and `full` Flows —
this Change must not special-case FULL; the false positive Discovery found
is a property of every canonical Flow's stage ordering, not of FULL's
extra stages specifically.

## Traceability Matrix

| Requirement | Discovery Finding | Acceptance |
|---|---|---|
| FR-001 | MR-015 allowed-file set vs. Protocol §5's literal three-file exception (evaluator.py, protocol/versions/2/specification.md §5) | AC-001, AC-002, AC-003, AC-006, AC-007 |
| FR-002 | MR-017 policy gap (policy.py:29-43, protocol/policies/merge-readiness.yml) | AC-004, AC-005 |

## Compatibility Statement

No Protocol version change (C-046 preserved — this is Adapter/CLI-internal
gate logic, not a Protocol-schema or Contract change). No change to any
`.forge/changes/*` artifact schema. Existing passing merge-readiness
behavior for every other MR-xxx check is unaffected; only MR-015's
allowed-file computation and the materiality policy's prefix/path tables
change. Changes already merged to `main` are unaffected retroactively —
this Change only affects future `forge change merge-check` evaluations,
including of CHG-0045's still-open PR #36.

## Specification Gate

Requirements are independently derived from Discovery's direct code and
Git evidence, and — after Specification Drift — directly from Protocol
2's own normative text (`protocol/versions/2/specification.md` §5, §8,
§11, §14), not from an unchecked precedent assumption. AC-001/AC-003/AC-006
together specify both the fix (tolerance requires an explicit, anchored
renewal record) and its regression boundary (no tolerance without one,
regardless of `state.current`; an unanchored renewal claim does not
count) as equally load-bearing, verifiable conditions. This revision
superseded the version adversarial Specification Review (SR-001/SR-002)
originally passed — that Review's own findings (the stage-mapping design
cannot cover `tasks.md`/`specification-drift.md`) remain correctly
resolved by the *replacement* design too; only the state-conditioned
mechanism SR-002 endorsed as CON-002's implementation was itself found
non-conformant, by evidence outside this Specification's own re-reading
of itself. Ready for a fresh adversarial Specification Review pass over
the corrected FR-001/CON-002/CON-004.

## Out of Scope

- MR-006 and MR-008: confirmed in Discovery as genuine CHG-0045 provenance
  gaps, not gate defects. Not addressed by any requirement here.
- **MR-015 provides no protection today against a completed Change's
  implementation changing outside its own `change_root` directory**
  (Discovery, "A more severe, orthogonal, pre-existing gap..."),
  confirmed by direct reproduction against a disposable fixture repository.
  This is real, already live on `main`, and independent of everything
  CHG-0045 triggered — but closing it means resolving the same repo-wide-
  vs-per-Change tension CHG-0036 already fought once, for the *completed*
  state specifically, which is a materially larger problem than either FR
  here. Left unaddressed, named explicitly rather than silently carried
  forward as an assumed protection.
- Any other deferred merge-readiness finding on record
  ([[project-merge-readiness-scoping-bug]]).
- Redesigning the materiality policy's schema, or reclassifying any path
  the policy does not currently resolve to `ambiguous`.
