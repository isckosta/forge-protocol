---
forge:
  artifact: architecture
  schema: 1
change: CHG-0011
status: complete
---
# Architecture — Review Convergence Boundary

## Reuse over parallel subsystem

Protocol 2 (CHG-0008) already computes "everything that changed since a
frozen commit, excluding review-control metadata" via
`_reviewable_workspace_delta` (committed `<subject>..HEAD` ∪ staged ∪
unstaged ∪ untracked, minus the exact Change-local
`manifest.yml`/`provenance.yml`/`review.md` paths) to detect drift between a
frozen commit and the *current* workspace. Resolution Delta compares two
already-frozen historical commits instead, so it only needs the committed-diff
half of that machinery: `src/forge_cli/validation/__init__.py` gains
`_resolution_delta(root, manifest_path, from_commit, to_commit)`, which calls
the existing `_diff_paths(root, f"{from_commit}..{to_commit}")` directly and
subtracts the same metadata-exclusion set `_reviewable_workspace_delta`
already computes inline. No new Git-walking logic, and no staged/unstaged/
untracked re-check (that remains §5's job against the *current* subject,
unchanged).

Path containment is exact-match against the same POSIX-style repo-relative
paths `_diff_paths`/`_untracked_paths` already decode to — no glob library,
no new dependency (see CHG-0011-R003 correction below for why glob matching
was rejected, not just deferred).

## Manifest shape (`forge/change@2`, additive)

```yaml
review:
  iterations:
    - id: review-002
      revision: chg-0011-resolution-001
      subject_provenance: resolution-001
      reviewer_provenance: review-002
      kind: resolution_verification        # NEW, optional
      status: failed
      full_review_required: true           # NEW, optional
      new_material_findings: 1             # NEW, optional, required-if-kind+failed
      finding_classes: [resolution_regression]   # NEW, optional, informational
      evidence_gap: "CHG-0011-R002 (class B): ..."
    - id: review-003                       # the Iteration immediately after
      revision: chg-0011-fullreview-001    # a Non-Convergence episode ends
      subject_provenance: fullreview-001
      reviewer_provenance: review-003
      kind: initial_review
      status: passed
      convergence_decision:                # NEW, optional, PER-ITERATION —
        option: new_full_review            # not a manifest-wide field (see
        reason: "..."                      # CHG-0011-R001 correction)
        recorded_at: 2026-08-17T00:00:00Z
  convergence:                             # NEW, optional block
    state: nominal                         # current trailing state only
    consecutive_unconverged_verifications: 0
```

`review.convergence.state` and `.consecutive_unconverged_verifications` are
**advisory mirrors** of a Core-derived truth, not authoritative inputs. Core
recomputes both from `iterations` on every `validate_project` run and raises
a finding if the manifest's declared value disagrees. This directly answers
the Discovery risk (§Adversarial self-check risk) that a self-declared
counter is resettable — it is not self-declared as far as enforcement is
concerned; it is checked.

`convergence_decision` deliberately lives on the specific Iteration it
authorizes, not on `review.convergence` (a manifest-wide field was the
original design — Strict Review Iteration 1 found, CHG-0011-R001 BLOCKER,
that a single early decision could then silently authorize every later,
independent Non-Convergence episode in the same manifest, because Core only
checked "does *a* valid decision exist anywhere," not "does *this episode's*
following Iteration carry one"). Per-Iteration placement closes this for
free: committed Iterations are already immutable history (Protocol 2,
CHG-0008), so a decision recorded for episode 1's following Iteration cannot
be reinterpreted as authorizing episode 2's.

## Provenance shape (`forge/execution-provenance@1`, additive)

```yaml
records:
  - id: resolution-001
    role: resolution
    scope: ["src/forge_cli/validation/__init__.py", "tests/unit/test_resolution_verification.py"]  # NEW, optional, EXACT paths only
    targets: ["CHG-0011-R001"]                                              # NEW, optional
    execution: {...}
    revision: {...}
    source: {...}
```

`scope` entries are exact repository-relative paths, not glob patterns.
Strict Review Iteration 1 found (CHG-0011-R003, MAJOR) that the original
`fnmatch`-based implementation let `scope: ["*"]` cover every path,
mechanically defeating Out-of-Scope Mutation detection entirely; `fnmatch`
was removed rather than hardened against degenerate patterns, since exact
paths are already what FR-003's motivating use case needs and glob
specificity heuristics are their own adversarial surface this Change
deliberately avoids building.

`scope`/`targets` are ordinary fields on an existing record type. They
inherit the existing Git-history-anchoring machinery
(`_first_committed_provenance_record`) automatically — no new immutability
mechanism is written; once a resolution record's first committed
representation exists, `scope`/`targets` are frozen exactly like `revision`
or `source` already are.

## Validator changes (`src/forge_cli/validation/__init__.py`)

New function `_validate_resolution_verification(r, mpath, m, ppath, p, its,
idx)`, called from `_validate_protocol2_review_provenance` only for
manifests where at least one Iteration sets `kind`. It runs after (never
instead of) the existing FR-002–FR-019 (CHG-0008) checks, so scope/
convergence logic only executes once basic provenance/independence/freeze
integrity is already established for that Iteration — a `resolution_
verification` Iteration inherits every existing Protocol 2 guarantee before
this Change's additional guarantees apply.

Per-Iteration checks (only for `kind: resolution_verification`):
1. Position: not first in `iterations` (FR-002).
2. Subject provenance `role == resolution` (FR-002).
3. Subject provenance declares non-empty `scope` and `targets` (FR-003).
4. Compute Resolution Delta against the immutable revision of the
   *immediately preceding* Iteration's subject provenance (FR-004).
5. Compute uncovered paths = Resolution Delta − paths exactly matching a
   declared `scope` entry (FR-005; exact match only — CHG-0011-R003).
6. If uncovered paths exist: Iteration MUST be `status: failed` AND
   `full_review_required: true`, else finding (FR-006).
7. If `status == passed`: `new_material_findings` MUST be absent or `0`
   (a passed Verification asserts nothing new/material was found).
8. If `status == failed` and `kind == resolution_verification`:
   `new_material_findings` MUST be a non-negative integer (FR-013); its
   presence/positivity feeds step 9's manifest-level pass.

Manifest-level check (after per-Iteration checks), computed once as a
per-index streak array, then walked twice:
9. Derive `streaks[i]` = length of the run of `kind == resolution_verification`,
   `status == failed`, `new_material_findings > 0` entries ending at index
   `i` (FR-011); `consecutive_unconverged_verifications` = `streaks[-1]`
   (current trailing state only).
10. If `streaks[-1] >= 2`: manifest MUST declare
    `review.convergence.state == review_convergence_failed`; any declared
    mismatching value or mismatching `consecutive_unconverged_verifications`
    is a finding. `review.status: passed` is a finding.
11. **For every historical index `i` where `streaks[i] >= 2`** (not only the
    last one — CHG-0011-R001), if `iterations[i+1]` exists: it is valid only
    if `iterations[i+1].convergence_decision.option` and `.reason` are
    present **on that specific Iteration** and it is `kind: initial_review`
    (or unclassified) — a `resolution_verification` at `i+1` is always a
    finding, decision or not (FR-012, FR-014). A decision is read fresh from
    each `i+1` Iteration; nothing is cached or reused across different `i`.
12. If `iterations[i+1].convergence_decision.option == accept_residual_risk`:
    the effective review policy must permit it. Because policy YAML is not
    parsed by Core today (Discovery finding — it is agent-followed, not
    machine-enforced), and this Change does not introduce a policy-YAML
    loader into Core (out of scope; would be new machinery for one boolean),
    Core instead reads a project-local, already-`forge validate`-loaded
    signal: `.forge/forge.yml` gains an optional
    `review.convergence.allow_residual_risk_acceptance: bool` (default
    `false`/absent = not permitted), loaded through the existing
    `load_project_configuration` used by `validate_project`. This keeps the
    "policy permits it" check inside the one config file Core already
    parses, instead of adding a second YAML-loading path.

`kind`-unclassified manifests (every manifest today, including `CHG-0008`
and `CHG-0010`) hit none of the above — `_validate_resolution_verification`
returns immediately when no Iteration declares `kind` (INV-006, AC-001,
AC-012).

## Contract and Specification placement

New Contract rules are appended to the shared `protocol/contract/
engineering.md` (C-047–C-050), following the C-045/C-046 precedent set by
CHG-0008: they are process obligations that only bind a Change once it opts
into the `kind` vocabulary; they do not create a new mandatory Gate for
Changes that do not.

- **C-047 — Resolution Verification is scoped.** A Review Iteration
  classified `resolution_verification` MUST NOT be conducted as an
  unrestricted re-audit of the review subject; its authority is bounded to
  the Findings it targets, defects within its Resolution Delta, and
  Out-of-Scope Mutation.
- **C-048 — Material out-of-scope mutation requires Full Review Escalation.**
  A Resolution that materially mutates the review subject outside its
  declared scope MUST NOT receive approval through a scoped Resolution
  Verification; it MUST escalate to a new Initial Review.
- **C-049 — Review convergence has deterministic termination semantics.** A
  Resolution → Resolution Verification cycle MUST NOT continue automatically
  and indefinitely; reaching the Convergence Limit MUST stop automatic
  progression and require an explicit engineering decision.
- **C-050 — Unrelated latent findings are recorded, not discarded or
  amplified.** A Resolution Verification MUST record a Finding unrelated to
  the Resolution under review rather than silently ignore it, and MUST NOT
  treat that Finding alone as license to become an unrestricted re-audit.

Protocol-2-specific mechanics (the manifest/provenance field shapes, the
Core-derivation rule, the exact Convergence Limit) are appended to
`protocol/versions/2/specification.md` as new §10–§13, extending the existing
Protocol-2-only elaboration surface rather than creating a new document.
`protocol/versions/2/policies/review.yml` gains a `resolution_verification`
block mirroring the existing `reviewer_resolver_separation` block's
descriptive style (informs the agent; Core enforcement lives in Python, per
the existing split documented in Discovery).

## Compatibility mechanics

`protocol/schemas/change-v2.schema.json`: `kind`, `full_review_required`,
`new_material_findings`, `finding_classes` added as optional properties to
the iteration item schema; `convergence` added as an optional top-level
`review` property. `protocol/schemas/execution-provenance.schema.json`:
`scope` (array of strings) and `targets` (array of strings) added as optional
record properties. All additions are optional; `additionalProperties: false`
already present on both schemas continues to reject genuinely unknown
fields, so the schemas stay strict while accepting exactly the new,
documented shape. `protocol/compatibility.md` gains a short explicit
subsection recording this reasoning (F-009 requires evaluating backward
compatibility for Schema changes) so the decision is not only implicit in
this Change's artifacts.

## What this Change deliberately does not build

No `forge/decision@1` schema, no generic Decision Gate reusable from
Specification/Architecture stages, no recommendation engine. The decision
record (`iterations[].convergence_decision`) is a fixed-shape, four-option object
scoped only to this one convergence-failure state — it has no independent
schema identity and is validated inline as part of `change-v2.schema.json`.
