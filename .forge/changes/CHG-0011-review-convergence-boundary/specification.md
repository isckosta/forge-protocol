---
forge:
  artifact: specification
  schema: 1
change: CHG-0011
status: complete
---

# Specification — Review Convergence Boundary

## Terminology

- **Initial Review** — a Strict Review Iteration with `kind: initial_review`
  (or, for legacy manifests, any Iteration without a `kind`, which retains
  exactly today's unrestricted authority). It may examine the entire surface
  defined by the applicable review policy and Flow. It has full authority to
  raise any legitimate Finding within that surface.
- **Resolution** — the execution that addresses blocking Findings from a
  preceding Review Iteration, producing a new frozen subject (unchanged from
  Protocol 2 — CHG-0008 §5–§6).
- **Resolution Verification** — a Strict Review Iteration with
  `kind: resolution_verification`. It is an independent Strict Review
  Iteration (same Execution/Context independence, freeze, and provenance
  invariants as any Protocol 2 Review — see Invariants) whose *purpose and
  scope* are bound to the Resolution it follows, as defined below. It is not
  a weaker review; it is a *targeted* one.
- **Resolution Scope** — the set of repository-relative paths a Resolution
  declares, prospectively, as the boundary of its legitimate mutation
  (`provenance.yml` resolution record field `scope`, §Resolution Scope
  below). Declared alongside `targets`, the Finding IDs (from `review.md`)
  the Resolution claims to address.
- **Resolution Delta** — the effective reviewable workspace delta (in the
  existing Protocol 2 §5 sense: committed + staged + unstaged + untracked,
  excluding the exact Change-local `manifest.yml`/`provenance.yml`/
  `review.md` paths) between the prior reviewed subject's frozen commit and
  the Resolution's own frozen commit.
- **Out-of-Scope Mutation** — any path present in the Resolution Delta that
  is not covered by the declared Resolution Scope (and is not the standard
  review-control metadata exception).
- **Full Review Escalation** — the explicit, mechanically visible outcome
  (`full_review_required: true` on the Resolution Verification Iteration)
  required when a Resolution Verification finds material Out-of-Scope
  Mutation, or when the Convergence Limit (below) is reached. It requires the
  *next* Iteration to be a new `initial_review`, not another
  `resolution_verification`.
- **Convergence** — the property that the Resolution → Resolution
  Verification cycle for one originating set of Findings terminates within a
  bounded number of iterations, either by reaching PASS or by explicit Full
  Review Escalation / engineering decision.
- **Non-Convergence** — the Core-derived state (`review_convergence_failed`,
  §Convergence Policy) reached when that bound is exceeded.

## Finding taxonomy (Resolution Verification only)

An Initial Review's Findings are not classified by this taxonomy; it exists
only to give Resolution Verification a bounded, auditable way to react to
what it discovers, per FR-011–FR-014:

- **A — Unresolved Finding.** A Finding from the Iteration the Resolution was
  supposed to address, still present.
- **B — Resolution Regression.** A new defect inside the Resolution's own
  delta, or a direct, evidenced consequence of the change the Resolution
  made (e.g. a fix that breaks an adjacent invariant).
- **C — Out-of-Scope Mutation.** A material mutation the Resolution Delta
  contains that is not covered by the declared Resolution Scope. "Material"
  is a Reviewer judgment call, evidenced per C-025, exactly like BLOCKER/
  MAJOR severity already is; the mechanical layer only proves *containment*
  (is the path in scope or not), never proves *materiality* by itself. A
  mechanically-incidental change strictly required to keep the repository
  consistent as a direct syntactic side effect of an in-scope change (e.g.
  updating `traceability.yml` to reference a task the Resolution added) is
  not, by itself, material — but it must still be inside the declared scope;
  undeclared paths are what trigger review, not a separate "triviality"
  carve-out.
- **D — Unrelated Latent Finding.** A real, pre-existing problem, not caused
  by the Resolution and not required to verify the Findings under
  Verification. It could, in principle, have been found by the Initial
  Review.

## Functional requirements

### FR-001 — Iteration kind is optional and additive
`forge/change@2` Review Iterations MAY declare `kind`
(`initial_review` | `resolution_verification`). Absence of `kind` MUST be
interpreted exactly as Protocol 2 behaves today (no scope/convergence
semantics apply). This field MUST NOT become required for existing or future
Iterations that do not use it.

### FR-002 — Resolution Verification scope binding
A Review Iteration with `kind: resolution_verification` MUST reference, via
`subject_provenance`, a provenance record with `role: resolution`. Core MUST
reject `kind: resolution_verification` whose subject provenance role is
`implementation` (that is definitionally an Initial Review). A
`resolution_verification` Iteration MUST NOT be the first entry in the
manifest's `iterations` array (there is, by definition, no prior reviewed
subject to compute a Resolution Delta against); Core MUST reject that case.

### FR-003 — Resolution declares scope and targets
A `role: resolution` provenance record referenced by a
`resolution_verification` Iteration MUST declare `scope` (non-empty array of
repository-relative paths or `fnmatch`-style path globs) and MUST declare
`targets` (non-empty array of Finding IDs). A `resolution_verification`
Iteration whose subject provenance omits `scope` or `targets` MUST fail
validation with an explicit finding (it cannot be mechanically verified as
scoped; it must be reclassified `initial_review` or corrected).

### FR-004 — Resolution Delta computation
The Resolution Delta compares two already-frozen, immutable historical
commits (the prior Iteration's subject and this Iteration's subject) — not
the current workspace — so it MUST be computed as the plain committed diff
`git diff --name-status <prior_commit>..<this_commit>` (rename-aware, same
decoding as the existing `_diff_paths`/`_untracked_paths` helpers), excluding
only the exact Change-local `manifest.yml`/`provenance.yml`/`review.md`
paths. Staged/unstaged/untracked workspace state is a distinct, already-
covered concern (Protocol 2 §5's effective-workspace freeze against the
*current* subject); Resolution Delta does not re-check it. "Prior Iteration"
is the Iteration immediately preceding the current one in manifest order;
Core MUST fail closed (same as the existing freeze mechanism) when required
Git history cannot be established.

### FR-005 — Out-of-scope containment is mechanically checked
Core MUST verify each path in the Resolution Delta is covered by at least one
declared `scope` entry (exact path or glob match). Core MUST record which
Resolution Delta paths, if any, are not covered.

### FR-006 — Out-of-scope mutation forces escalation, never a silent pass
A `resolution_verification` Iteration MUST NOT be `status: passed` while its
Resolution Delta contains a path not covered by declared scope. When
uncovered paths exist, the Iteration MUST be `status: failed` and MUST carry
`full_review_required: true`, signaling that the *next* Iteration for that
manifest must be `kind: initial_review` (FR-010). There is no mechanism by
which an Iteration that detected out-of-scope mutation can itself be
`passed`; approval can only come from the subsequent unrestricted Initial
Review.

### FR-007 — Resolution Verification is not a re-audit by default
`kind: resolution_verification` MUST NOT, by itself, grant authority to
raise Findings outside: (a) the `targets` Findings (class A), (b) defects
inside the Resolution Delta or its direct evidenced consequences (class B),
(c) Out-of-Scope Mutation already covered by FR-005/FR-006 (class C). This is
a Contract/process obligation (new Contract rule, see Compatibility) followed
by the agent conducting the review; Core cannot mechanically prove a human's
reasoning stayed in scope, only that the *mutation* did.

### FR-008 — Unrelated latent findings do not silently disappear
When a Resolution Verification identifies a class D Finding, it MUST be
recorded in `review.md` with its class explicit. It MUST NOT be discarded.

### FR-009 — Unrelated latent findings do not by themselves force escalation
A class D Finding MUST NOT, by itself, set `full_review_required: true` or
increment the convergence counter (§Convergence Policy), unless its severity
is BLOCKER or MAJOR, in which case existing C-027 already prevents
Completion regardless of class — the Iteration MUST record it and MAY target
it with its own scoped Resolution (still classifiable
`resolution_verification` against a new Resolution scoped to that specific
Finding) rather than being forced into `initial_review`.

### FR-010 — Full Review Escalation resets classification, not independence
Once `full_review_required: true` is recorded, the next Iteration for that
manifest MUST be `kind: initial_review` (or unclassified, legacy-equivalent)
if it is to review the same subject family going forward. This changes
*scope authority*, not Reviewer/Resolver independence: FR-002 through FR-010
of Protocol 2 (CHG-0008; Execution/Context independence, freeze, provenance
authority) remain fully in force for every Iteration regardless of `kind`.

### FR-011 — Convergence counter is Core-derived, not self-declared
Core MUST compute `consecutive_unconverged_verifications` deterministically
from the manifest's `iterations` array: the length of the trailing run of
iterations that are all `kind: resolution_verification`, `status: failed`,
and have `new_material_findings > 0` (a Reviewer-declared, evidence-backed
count of class B + C Findings on that Iteration — see FR-013). Core MUST
treat any self-declared `review.convergence.consecutive_unconverged_...`
value as informational only and MUST report a validation finding if it
disagrees with the Core-derived value.

### FR-012 — Convergence limit and non-convergence
The Convergence Limit is 2. When Core's derived
`consecutive_unconverged_verifications` reaches 2, Core MUST require
`review.convergence.state == review_convergence_failed` and MUST reject
`review.status: passed`. Any Iteration appended after the second such failed
Iteration is valid only if both hold: a valid `review.convergence.decision`
(§Failure Semantics) is present, and the new Iteration is `kind:
initial_review` (or unclassified/legacy). A third `resolution_verification`
— with or without a decision record — is always rejected once
Non-Convergence is reached: Full Review Escalation, not another scoped
Verification, is the only mechanized way to continue the review lifecycle.
This check is evaluated against every point in `iterations` history where the
limit was reached, not only the current trailing state — a later
`initial_review` Iteration resets the *trailing* counter (FR-011) but MUST
NOT retroactively excuse an earlier non-convergence episode that was never
accompanied by a decision record.

### FR-013 — `new_material_findings` requires evidence
`new_material_findings` MUST be a non-negative integer. When it is greater
than zero, the Iteration's `evidence_gap` (or `review.md`) MUST identify at
least that many class B/C Findings with IDs. Core does not re-derive the
semantic truth of the count (same trust boundary as existing blocker/major/
minor/observation counts); it only requires the count to be present,
consistent (`>0` implies at least one B/C class recorded), and used
consistently in the derived convergence run.

### FR-014 — Non-convergence returns authority to the engineer
While `review.convergence.state == review_convergence_failed` and no valid
decision is recorded, Core MUST NOT allow `review.status: passed`, and no
new `resolution_verification` Iteration may legally continue the automatic
cycle. Forge MUST NOT itself select an option; the Change's own artifacts
MUST NOT auto-populate `decision.option` without an explicit, attributable
engineering statement in `reason`.

### FR-015 — Decision record shape (minimal, non-generic)
`review.convergence.decision`, when present, MUST contain `option` (one of
`new_full_review`, `return_to_earlier_phase`, `accept_residual_risk`,
`abort_or_supersede`) and a non-empty `reason`. This is the minimal escape
valve required by this Change; it is not a general Decision Gate/Decision
Analysis framework, has no recommendation engine, and has no delegation
semantics. `accept_residual_risk` additionally requires the project's
effective review policy to permit it (new optional policy field, defaulting
to not-permitted/absent — see Compatibility); Core MUST reject
`accept_residual_risk` when that policy permission is absent.

### FR-016 — No retroactive effect
None of FR-001–FR-015 apply to a Review Iteration that does not declare
`kind`, or to a provenance record that does not declare `scope`/`targets`.
Existing completed and in-flight manifests (including `CHG-0008` and
`CHG-0010`) remain valid exactly as before without modification.

## Invariants

- **INV-001 — Scope is declared before it is checked.** A `resolution`
  provenance record referenced by a `resolution_verification` Iteration MUST
  declare `scope`/`targets` prospectively (they are part of that resolution
  record, anchored by the same Git-history-authority mechanism as every other
  provenance field — CHG-0008 §5); scope cannot be widened after the fact to
  legalize an already-discovered out-of-scope mutation without that widening
  itself being a new, separately anchored provenance write subject to the
  same immutability rule.
- **INV-002 — Containment is mechanical; materiality is evidenced judgment.**
  Core proves path containment. It never asserts that an in-scope change is
  correct or that an out-of-scope change is unimportant.
- **INV-003 — The convergence counter cannot be reset by self-declaration.**
  Core recomputes it from `iterations` on every validation; a manifest cannot
  escape Non-Convergence by simply writing a lower number or removing
  `convergence.state`.
- **INV-004 — Reviewer/Resolver independence is unaffected.** Every
  invariant from Protocol 2 §2–§8 (CHG-0008) applies identically to
  `initial_review` and `resolution_verification` Iterations. Nothing in this
  Change permits self-review, weaker assurance, or a Resolver verifying its
  own Resolution.
- **INV-005 — No silent Completion.** `review.status: passed` MUST NOT occur
  while a manifest is in `review_convergence_failed` without a decision, nor
  while any `resolution_verification` Iteration is `passed` despite uncovered
  Resolution Delta paths without `full_review_required: true`.
- **INV-006 — Legacy manifests are unaffected.** A manifest with zero
  `kind`-classified Iterations produces zero new findings from this Change's
  validation logic.

## Compatibility

This Change does not introduce a new integer Protocol identifier and does
not introduce a new `forge/change@N` or `forge/execution-provenance@N` schema
suffix. All new fields (`kind`, `full_review_required`, `new_material_findings`,
`review.convergence`, provenance `scope`/`targets`) are optional additions to
`forge/change@2` and `forge/execution-provenance@1`. Per
`protocol/compatibility.md`, this is "optional artifacts whose absence
preserves existing meaning" — compatible Protocol 2 evolution, not a breaking
change: it removes no invariant, changes the meaning of no existing required
field, and invalidates no previously valid conforming instance (verified
directly against `CHG-0008`'s and `CHG-0010`'s current manifests, neither of
which sets any new field). New Contract rules (FR-007's process obligation,
and the definitional rules in `architecture.md`) are added to the shared
`protocol/contract/engineering.md`, following the CHG-0008/C-045/C-046
precedent: they define what a Change *claims* when it opts into the new
vocabulary; a Change that never opts in makes no such claim and is
unaffected. No migration is required. Legacy Protocol 2 records retain
legacy semantics permanently, not merely until some future migration; there
is no intent to eventually force `kind` classification onto historical data.

## Acceptance criteria

- AC-001: a manifest with no `kind`-classified Iterations validates
  identically before and after this Change (regression baseline).
- AC-002: a `resolution_verification` Iteration whose subject provenance role
  is `implementation` fails validation.
- AC-003: a `resolution_verification` Iteration whose subject provenance
  lacks `scope` or `targets` fails validation.
- AC-004: a Resolution Delta fully covered by declared scope, verified by an
  independent Reviewer (distinct Execution/Context), reaching `passed`,
  validates successfully.
- AC-005: a Resolution Delta containing a path outside declared scope, marked
  `passed` without `full_review_required: true`, fails validation.
- AC-006: the same case marked `status: failed` with `full_review_required:
  true` validates (explicit escalation, not silent approval); the same
  uncovered-path case marked `status: passed` — with or without
  `full_review_required: true` — fails validation.
- AC-007: two consecutive `resolution_verification` Iterations with
  `new_material_findings > 0` produce a Core-derived
  `consecutive_unconverged_verifications == 2`; a manifest asserting
  `review.status: passed` at that point fails validation.
- AC-008: the same case, with `review.convergence.state` written as anything
  other than `review_convergence_failed`, or omitted, still fails validation
  (state is cross-checked, not trusted).
- AC-009: after Non-Convergence, appending a third `resolution_verification`
  Iteration without a `decision` record fails validation; appending a new
  `initial_review` Iteration (with or without a decision record) is legal.
- AC-010: `accept_residual_risk` without effective policy permission fails
  validation.
- AC-011: a class D (unrelated latent) Finding recorded on a
  `resolution_verification` Iteration with `new_material_findings: 0` does
  not affect the convergence counter and does not require
  `full_review_required`.
- AC-012: `CHG-0008`'s and `CHG-0010`'s actual current manifests continue to
  validate with zero new findings from this Change's logic.
- AC-013: Execution/Context independence, freeze, and provenance-authority
  regressions from CHG-0008 (R001–R008 equivalents) remain green.
- AC-014: `pytest -q`, `forge validate`, `forge doctor` are green on the
  final Resolution subject.
