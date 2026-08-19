---
forge:
  artifact: architecture
  schema: 1
change: CHG-0015
status: complete
---

# Architecture — Delegated Agent Authority and Side-Effect Boundaries

## Reuse over parallel subsystem (C-032/C-033)

Per C-032 ("existing Architecture must be inspected... REQUIRED" for FULL),
this design extends four already-proven mechanisms rather than building a
parallel one:

- `forge/execution-provenance@1`'s `scope`/`targets` fields — already
  schema-general, narrowed today only by Protocol 2 §11 prose to
  `role: resolution`.
- `_reviewable_workspace_delta`/`_resolution_delta`/`_uncovered_paths`/
  `_review_control_metadata_paths`/`_committed_history_mappings`
  (`src/forge_cli/validation/__init__.py`) — the existing Git-native
  diff-and-cover primitives and the existing committed-history-walking
  machinery C-026's "first committed representation is authority" rule
  already established (a sibling function reuses the walk, not
  `_first_committed_provenance_record` itself — see Validator changes,
  step 6, for why that one specifically does not fit).
- Protocol 2 §4's `claimed`/`recorded`/`verified` assurance vocabulary.
- Unresolved Decision Management (`decisions[]`, C-051–C-059) — used below
  to actually resolve `DEC-002`, now that Architecture (its owning
  Artifact) exists.

No new subsystem, no new top-level Protocol concept beyond what
Specification already named (Authority, Authorized Scope, Execution
Boundary, Observed Effect).

## DEC-002 — Lifecycle coverage boundary (resolution)

### Question
Recap (`specification.md`): does v1's Execution Boundary cover delegations
before any Review-subject freeze exists (Discovery, where the incident
occurred), or only stages with existing frozen-subject machinery
(Implementation/Resolution/Review)?

### Evidence investigated (Architecture-stage addition to Specification's)
Traced exactly how `_reviewable_workspace_delta` establishes its baseline
(`src/forge_cli/validation/__init__.py:68-82`): a single commit `c` plus
`git diff`/`git status`-equivalent primitives against the *current*
workspace. Confirmed this generalizes cleanly to an arbitrary two-point
comparison (see "Execution Boundary capture," below) without touching Git
plumbing beyond what `_diff_paths`/`_untracked_paths` already do. Also
confirmed the generalization does **not** require a Change lifecycle Gate
to exist at all — it only needs two points in time and a working tree,
which exist from the first keystroke of any session.

### Alternatives
Unchanged from Specification: (1) post-freeze only; (2) stage-agnostic.

### Decision
**Alternative 2**, `resolved_via: autonomous_decision` — properly this
time: this Decision's owning Artifact is Architecture, which now exists
and is the Execution making this call, satisfying C-052/`decision.yml`'s
`owning_artifact_by_class` (`architectural` → `architecture`) without the
ownership violation `specification-review.md` R006 found and corrected in
the prior draft. `agent_with_review` Authority is satisfied by this
Architecture document itself being subject to Strict Review later in this
Change's own lifecycle (C-026/Protocol 2 §2) — a genuinely independent
Execution/Context, unlike Specification Review, which Protocol 2 does not
require to be independent (see `specification-review.md`'s own note on
this). If that later independent Review disagrees, this Decision is
revisited then, not treated as final now.

## Execution Boundary capture (concrete design)

**Baseline** (captured at delegation-open, by the delegating primary
Execution, before invoking the delegate):

1. `head`: current `HEAD` commit SHA (`git rev-parse HEAD`).
2. `dirty`: a sorted map of `{path -> content-identity}` for every path
   currently different from `head` — committed-but-unpushed is irrelevant
   here (only local state matters); staged, unstaged, and untracked paths
   all included, reusing `_diff_paths(root)` (no ref = worktree-vs-index)
   and `_untracked_paths(root)` exactly as already implemented, plus one
   new primitive (`git hash-object` per path, or `git status
   --porcelain=v2` which already reports blob OIDs for staged entries) for
   the content-identity half — no existing function needs modification,
   only composition of the four already-proven primitives with a per-path
   hash appended.

This baseline is itself written into `provenance.yml` as part of the
delegate's own provenance record (`baseline`, new field — see schema
below), *before* the delegate runs, by the delegating Execution — the only
Execution that can observe the true pre-delegation state, and the same
"self-recorded, `assurance: recorded`" pattern Protocol 2 already uses for
everything else in that file.

**Close** (captured at delegation-end, same primitives, same shape,
recorded as this delegation's own `revision`) — captured **before** the
delegating primary Execution appends this delegate's own provenance
record to `provenance.yml`, so that append itself (a primary-Execution
act, not the delegate's) falls outside the `[baseline, close]` window and
never appears in the delegate's own Observed Effect. This ordering
requirement is a precondition Test Strategy must exercise directly (a
misordered capture would either produce a false Out-of-Scope Mutation
against the delegate for the primary's own bookkeeping, or — the more
dangerous failure — hide a genuine violation inside noise), not an
implementation detail assumed to be self-evidently correct.

**Observed Effect** = the union of:
1. the committed diff `baseline.head..close.head` (reusing `_diff_paths`
   exactly as `_resolution_delta` already does), and
2. every path present in `close.dirty` whose content-identity differs from
   (or is absent from) `baseline.dirty` — i.e., newly dirty, or dirtied
   further, since baseline was captured.

**The review-control-metadata exclusion applies here too, restored after a
second, deeper correction** — reusing `_review_control_metadata_paths`
verbatim to exclude `manifest.yml`/`provenance.yml`/`review.md` from the
*path-diff* Observed Effect. An intermediate draft of this section removed
that exclusion entirely, reasoning (correctly, as far as it went) that
reusing it verbatim would make those files invisible to Out-of-Scope
Mutation detection. Writing this Change's own fixture-repo Test Strategy
cases immediately afterward surfaced why *removing* it entirely is also
wrong, for a structural reason neither the original design nor that first
correction accounted for: the delegating primary Execution's own act of
*writing the delegate's provenance record* necessarily mutates
`provenance.yml` itself, and that write unavoidably happens after the
delegate's baseline was captured — so a path-diff with no exclusion at all
flags **every** `delegated_task` record as an Out-of-Scope Mutation of
`provenance.yml`, universally, including the fully legitimate case,
because the bookkeeping act of recording a delegation is indistinguishable
from an attack at the path level. Excluding these three paths from the
*path-diff* is genuinely necessary and correct for exactly this reason.

This does not reopen the self-authorization blind spot the intermediate
correction was right to worry about, because C-062 (self-authorization) is
**not** implemented as part of the path-diff at all — see "Self-
authorization (C-062)" in Validator changes below, which instead compares
a `delegated_task` record's own declared fields against its first
committed representation, walking committed history the same way
`_first_committed_provenance_record` does (the same "immutable once
committed" authority Protocol 2 §5/C-026 already established for exactly
this purpose — see Validator changes step 6 for why a sibling function,
not that one verbatim, is what actually gets reused). A delegate rewriting
its own already-committed `scope` to claim a broader grant is caught there,
by content comparison against history — not by flagging the mere
existence of a `provenance.yml` diff, which cannot distinguish legitimate
bookkeeping from an attack in the first place. `_reviewable_workspace_delta`/
`_resolution_delta` keep their own existing use of this same exclusion,
unaffected.

The `dirty` content-identity baseline separately and correctly excludes a
delegating Execution's *own* pre-existing uncommitted work-in-progress from
being misattributed to its delegate (the realistic shape of the actual
incident: the primary Execution was mid-Discovery, with its own draft edits
already present, when it delegated) — a bare "diff HEAD vs. now" baseline
would have wrongly attributed the primary Execution's own concurrent edits
to the subagent, or symmetrically hidden the subagent's overwrite inside
them. This is a distinct concern from the review-control-metadata question
above and remains exactly as designed.

## Schema: `forge/execution-provenance@2`

Additive over `@1` (new file `execution-provenance-v2.schema.json`,
`catalog.yml` entry `{id: forge/execution-provenance@2, file:
execution-provenance-v2.schema.json}`; `@1` unchanged and still valid,
per `protocol/compatibility.md`'s independent-schema-axis rule):

- `role` enum gains one value: `delegated_task` — deliberately singular
  and generic (not `research`/`investigation`/etc.) because Authority is
  expressed entirely through `scope` (empty = read-only, non-empty =
  scoped write), not through a role-name taxonomy of delegation purposes;
  a fixed enum of delegation *purposes* would be exactly the kind of
  premature, disproportionate taxonomy §20/C-039 warn against.
- `execution.delegated_by`: new optional string, the `execution.id` of the
  record that performed the delegation (FR-008 chain reconstruction). Only
  meaningful (and only required — see Validator changes) for
  `role: delegated_task` records.
- `baseline`: new optional object, `{head: <git commit sha, 40 hex>,
  dirty: [{path: <string>, hash: <string>}]}`, required together with
  `execution.delegated_by` whenever `role: delegated_task`.
- `scope`: **one real shape change from `@1`**, found while designing this
  section: `@1`'s `scope` has `minItems: 1`, adequate for Resolution (a
  Resolution always fixes *something*) but wrong for `delegated_task`,
  where the incident's own scenario — pure read-only research, zero write
  Authority — needs to declare an *empty* Authorized Scope. `minItems: 1`
  was never load-bearing against the actual glob/wildcard loophole Protocol
  2 §11 guards against (that is prevented by the existing "exact paths
  only" prose, not by array length); it only incidentally blocked a
  legitimate empty declaration. `@2` sets `scope`'s `minItems: 0` for every
  role, disclosed here as a deliberate, evidence-based relaxation, not an
  oversight: `scope: []` on a `delegated_task` record means "zero write
  Authority" and MUST be validated identically to any other declared Scope
  (Observed Effect MUST still be empty), not treated as "no restriction."
  `scope` remains **absent** (the field entirely missing) with a different
  meaning — "no Scope declared" — relevant only to non-`delegated_task`
  roles per DEC-001, where FR-001 does not require one.
- `targets`: unchanged shape, reused as-is.

No change to `revision`, `source`, or any other `@1` required field. A `@1`
record remains valid under `@1`'s own (unrelaxed) `scope` constraint;
nothing in `@2` retroactively requires any field on it or reinterprets an
existing `@1` record's `scope`.

## Validator changes (`src/forge_cli/validation/__init__.py`)

New function `_delegated_execution_effect(root, mpath, baseline,
close_revision)` — **`mpath` restored**, used only to compute the
review-control-metadata exclusion (see "Execution Boundary capture" above
for why excluding these three paths from the *path-diff* is necessary
regardless of who mutated them, and why this no longer reopens the
self-authorization gap — that is checked separately, below):

1. Computes committed diff `baseline["head"]..close_revision`
   (`_diff_paths`, reused).
2. Computes current `dirty` set the same way `baseline["dirty"]` was
   captured (composition of `_diff_paths(root)` + `_untracked_paths(root)`
   + per-path hash).
3. Returns the union described in "Execution Boundary capture" above,
   minus `_review_control_metadata_paths(root, mpath)` (reused, same three
   exact paths, same reasoning Protocol 2 §5 already established — applied
   here for a different but equally valid reason: unavoidable primary-
   Execution bookkeeping noise, not Reviewer self-recording).
4. Fails closed (returns `None`, propagated by the caller as "cannot
   verify") when `git cat-file -e` on `baseline["head"]` fails (shallow/
   missing history — same fail-closed condition `_git_exists` already
   guards elsewhere), directly implementing FR-013/C-065 below.

New function `_validate_delegated_authority(root, mpath, manifest)`,
called from `validate_project` for every Protocol id where `decisions`
already is (this concept, like Unresolved Decision Management, does not
depend on Protocol 2's Execution/Context independence model, so it is not
gated on `protocol == 2`):

1. Loads `provenance.yml` if present; returns immediately with no findings
   if absent, or if no record has `role: delegated_task` — the
   compatibility invariant (every historical Change and every Change that
   never delegates is unaffected, structurally identical to how
   `_validate_unresolved_decisions` returns immediately when `decisions` is
   absent).
2. Per DEC-001 (resolved: mandatory only for sub-delegations), this
   function's findings apply only to `role: delegated_task` records; a
   primary `implementation`/`resolution`/`review` record with no
   `delegated_task` children in the same ledger produces no findings here
   regardless of whether it declares `scope`.
3. For each `role: delegated_task` record: requires `execution.
   delegated_by`, `baseline`, and `scope` **present** (C-060, schema-shape
   half — `scope` may be `[]`, meaning zero write Authority, per the
   `minItems: 0` relaxation above, but MUST NOT be simply absent for this
   role); a `delegated_task` record missing `scope` entirely is itself a
   C-060 finding (FR-001), independent of anything below. Then looks up
   the named delegator record in the same ledger — missing delegator
   reference is a finding (provenance gap, cannot establish the Delegation
   Ceiling at all, fail-closed per C-065).
4. **Delegation Ceiling (C-063/INV-003):** if the delegator record is
   itself `role: delegated_task` (a nested hop — always has its own
   `scope` by step 3), the delegate's `scope` MUST be a path-subset of the
   delegator's `scope` (reusing `_uncovered_paths`' exact-path-match logic,
   no globs, same as Resolution Scope) — checked transitively at every
   depth (FR-008). If the delegator record is a primary
   `implementation`/`resolution`/`review` record — necessarily the first
   hop, since only a `delegated_task` delegator is required to declare
   `scope` under DEC-001 — and it declares no `scope` of its own (the
   common case: primary Executions are not required to), the first
   delegate's grant is checked against the **conservative default**
   Specification's FR-007 correction requires. **Implementability
   correction, made while writing GREEN**: the originally-worded default
   ("the Change's own governed Artifact and source paths... plus whatever
   `src`/`tests` paths the Change's own `intent.md`/`specification.md`
   name as in-scope") is not deterministically extractable from free-form
   Markdown prose — parsing it would itself be an unreliable heuristic,
   not the deterministic check C-039/C-065's fail-closed discipline
   requires. The implemented default is narrower and fully deterministic:
   exactly the paths whose repository-relative form is prefixed
   `.forge/changes/<change_id>/` (the Change's own directory, computed
   from `provenance.yml`'s own `change` field — no parsing required). A
   first-hop delegate granted write Scope outside its own Change's
   directory, when its delegator declares no `scope`, is conservatively
   rejected; a Change that genuinely needs a first-hop delegate to touch
   `src`/`tests` directly MUST have its primary Execution declare an
   explicit `scope` instead of relying on the default — the default is a
   safety floor, not a substitute for declaration when broader access is
   actually needed. If the primary record *does* declare a `scope` (it
   may, optionally), the first delegate's grant is checked against it
   exactly like any other hop, not the conservative default — the default
   applies only when nothing else is available.
5. **Out-of-Scope Mutation (C-061/INV-004):** calls
   `_delegated_execution_effect`; any returned path not covered by the
   delegate's `scope` is a finding. `None` (fail-closed) is itself a
   finding (C-065), distinct in message from an actual Out-of-Scope
   Mutation so a human can tell "we don't know" from "we know it violated
   scope."
6. **Self-authorization (C-062/INV-002) — a separate check, not part of
   the path-diff at all:** for each `delegated_task` record, a new
   function `_deleg_first_committed_scope(root, provenance_path,
   record_id)` fetches the record's own first committed `scope` by
   walking committed history the same way `_first_committed_provenance_record`
   already does (`_committed_history_mappings`, reused). **Found while
   writing GREEN, not anticipated here originally:** the obvious move —
   reusing `_first_committed_provenance_record` itself verbatim — fails for
   every `delegated_task` record, because that function's acceptance check
   calls `_record_fields`, which hardcodes the Protocol-2 Reviewer/Resolver
   role set (`implementation`/`resolution`/`review`) and rejects any other
   `role` value by design (correct for C-026's own purpose; wrong for this
   one). `_deleg_first_committed_scope` is the narrower, correct sibling:
   same "first committed representation is authority" rule (C-026
   precedent, `_committed_history_mappings` genuinely reused), a
   `role: delegated_task`-only acceptance check instead. If a first
   committed `scope` exists and is not equal (as a set, not merely
   coverage — narrowing one's own already-committed grant is not an
   attack, widening it is) to the current record's `scope`, that is a
   C-062 finding: the record rewrote the declaration of its own Authority
   after the fact. This is the mechanism that actually catches self-
   authorization: it compares a record's declared Authority against its
   own history, independent of whether `manifest.yml`/`provenance.yml`
   happen to be excluded from the unrelated path-diff computation in step
   5 — the two checks are deliberately orthogonal, so excluding those
   paths from one cannot silently defeat the other. History that cannot be
   determined (`_HISTORY_ERROR`) is itself a C-065 fail-closed finding
   here too, matching `_first_committed_provenance_record`'s own existing
   C-026 callers.

This mirrors `_validate_resolution_verification`'s shape exactly: small,
pure functions operating on already-loaded YAML mappings and local Git
state, no network, no Harness SDK, unit-testable with fixture repositories
the same way `tests/unit/test_validation.py` already covers the Resolution
Delta / Out-of-Scope Mutation logic this generalizes.

## Contract and Specification placement

- `protocol/contract/engineering.md` — append **C-060** through **C-066**
  after C-059 (shared canonical Contract):
  - **C-060 — Capability is not Authority.** No Core validation, Gate, or
    documentation may treat evidence of technical capability as evidence
    of Authority. (FR-002/INV-001)
  - **C-061 — Delegated-Execution Out-of-Scope Mutation blocks silent
    validity.** Generalizes C-047/C-048 from Resolution to any
    `delegated_task` Execution. (FR-005/INV-004)
  - **C-062 — No self-authorization.** A delegated Execution MUST NOT use
    write access to declare or expand the Authority governing its own
    current delegation. (FR-006/INV-002)
  - **C-063 — Delegation Ceiling.** A delegating Execution MUST NOT grant
    a delegate an Authorized Scope exceeding its own. (FR-007/INV-003)
  - **C-064 — Detection is the mandatory floor; Prevention is optional.**
    Core MUST be able to verify a delegated Execution's Observed Effect
    against its declared Scope using only local Git-native state; harness-
    enforced Prevention MAY additionally exist but MUST NOT be required.
    (FR-010/FR-011)
  - **C-065 — Fail-closed on indeterminate delegated-Execution
    authorization.** When required Git history for a baseline is
    unavailable, Core MUST NOT default to treating the Execution's product
    as authorized. (FR-013/INV-005)
  - **C-066 — Harness honesty for authority claims.** No statement of
    delegated-Execution authority enforcement may represent Detection as
    Prevention. (FR-014)

  Each of C-060–C-066 binds a Change only once it records a
  `role: delegated_task` provenance entry — identical in shape to how
  C-047 binds only once a Change opts into Resolution Verification, and
  C-051 binds only once `decisions[]` is used. **C-063 additionally binds
  only where the delegate is a `role: delegated_task` record** (DEC-001's
  resolution) — a primary Execution's own direct, undelegated work never
  triggers it, at any depth. This deliberately does not exempt nested
  delegation: a `delegated_task` record delegating to a further
  `delegated_task` record is still delegate-to-delegate and remains fully
  bound by C-063/FR-008, checked transitively (Validator changes, step 4).
  Only the *first* hop — Human or primary Execution granting to its first
  delegate — is exempt from needing its own declared Scope to compare
  against (the conservative-default fallback in Validator changes step 4
  covers exactly that hop, not any later one).
- `protocol/versions/2/contract/engineering.md` — append the identical
  C-060–C-066 text (same rationale CHG-0011/CHG-0013 already established
  for keeping this file's copy current, since `.forge/forge.yml` declares
  `protocol: 2` and Core's `_versioned_protocol_root` resolves rules from
  here for this repository).
- `protocol/specification.md` — new §40 ("Delegated Execution Authority"),
  Specification-density summary of Terminology + C-060–C-066, mirroring
  §39's existing treatment of Unresolved Decision Management.
- `protocol/schemas/execution-provenance-v2.schema.json` (new) +
  `catalog.yml` entry, per "Schema" above.
- `protocol/compatibility.md` — new subsection, same "additive fields, no
  invalidated instance, prospective-only binding" argument CHG-0011's and
  CHG-0013's subsections already establish as precedent.
- `ARCHITECTURE.md` §27 (Security boundary) — one added sentence: Core's
  Detection floor (C-064) is local and Git-native; Prevention remains
  Harness-dependent, consistent with this section's existing language, not
  a strengthening of it.
- **ADR required**: yes — `protocol/policies/architecture.yml`'s
  `adr.required_when` includes `core_boundary_changes`, and this design
  changes what Core's provenance ledger represents and what `forge
  validate` mechanically checks. Next available number per `docs/adr/`'s
  existing highest (`0012-unresolved-decision-management.md`) is **0013**
  (`docs/adr/0013-delegated-execution-authority-boundaries.md`), to be
  authored at this Change's Documentation stage once field names are
  final post-Implementation — not fabricated now as a placeholder file,
  consistent with how CHG-0013's own Architecture stage named its ADR
  requirement without pre-writing it (verified: no ADR-authoring step
  appears in `CHG-0013/architecture.md`).

## Adapter/Harness integration (FR-010) — deliberately not built now

No change to `protocol/schemas/adapter.schema.json`'s `capabilities` in
this Change. Discovery/Specification already established no Adapter
(Codex: `agent_roles: false`; no Claude Code Adapter exists) could use a
new Prevention-capability boolean today. Adding one now would be
speculative machinery with no consumer — exactly what §20/C-039 warn
against. A future Change, once a concrete harness Prevention mechanism
exists to project, adds the capability then, against real evidence.

## Compatibility mechanics (re-verified with concrete shapes)

`_validate_delegated_authority` returns immediately, no findings, when
`provenance.yml` is absent or contains no `role: delegated_task` record —
true of `CHG-0001`–`CHG-0015`'s own provenance to date. `@1` execution-
provenance records remain valid; nothing new is required on them. C-060–
C-066 bind prospectively only. No new integer Protocol identifier:
re-checked against `protocol/compatibility.md`'s breaking-change list with
concrete field names now in hand (Specification's compatibility analysis
flagged this as necessary-but-not-sufficient and asked Architecture to
re-verify) — none of C-060–C-066 removes/weakens an existing invariant,
makes an existing optional field mandatory for existing instances, or
invalidates a previously valid conforming instance. Conclusion unchanged
from Specification, now confirmed against the actual schema/field design.

## What this Change deliberately does not build

- No automatic-rollback engine. FR-012's "MAY restore when deterministically
  safe" remains a MAY; this Change does not implement restoration logic,
  only detection, evidence preservation, and Unresolved-Decision escalation
  when restoration isn't attempted.
- No general-purpose "who may edit which file" permission matrix. Only the
  functional Authority-Defining Artifact rule (FR-006/FR-016) exists;
  ordinary Change Artifacts remain governed by existing Contract rules
  (e.g., C-026), not a new file-ACL system.
- C-062's self-authorization check (Validator changes, step 6) only
  detects a `delegated_task` record's own `scope` field being rewritten
  from its first committed representation. It does not detect every
  conceivable way an Authority-Defining Artifact's *other* content could
  be manipulated to the same effect (e.g., a delegate tampering with a
  *different* record's fields, or with non-schema-tracked prose in
  `manifest.yml`) — those remain covered, if at all, only incidentally by
  ordinary Strict Review, not by this mechanism. Scoped deliberately to
  the concrete escalation vector this Change's own incident and adversarial
  review actually found, not generalized speculatively.
- No network/external-service coverage (FR-017, unchanged).
- No concurrency/TOCTOU solution beyond fail-closed on ambiguity (FR-013);
  parallel delegated Executions mutating overlapping paths remain a known,
  disclosed limitation, not silently assumed solved.
- No CLI command surface change. `_validate_delegated_authority` runs
  inside the existing `forge validate`, consistent with `ARCHITECTURE.md`
  §20's CLI boundary.
