---
forge:
  artifact: review
  schema: 1
change: CHG-0050
status: complete
---

# CHG-0050 · Review

## Verdict

**PASS.** Iteration 1: REQUEST CHANGES — R-001 (MAJOR) and R-002 (MINOR) found and resolved; R-003 (OBSERVATION) accepted/disclosed, R-004 (OBSERVATION) corrected. Iteration 2 (Resolution Verification): R-001/R-002/R-004 independently re-verified as genuinely and durably fixed (including a live before/after reproduction of the R-001 crash and a temporary revert-and-restore of its one-line fix); two further non-blocking findings within the Resolution Delta itself (R-005 MINOR, R-006 MINOR) were found and evaluated. Fixing either would require touching a non-review-control-metadata file (`tdd-evidence.yml`, or `provenance.yml`'s already-committed `resolution-001` record, both outside the `manifest.yml`/`provenance.yml`/`review.md` exception C-026 grants after a subject freeze) — doing so post-freeze would itself invalidate the already-passed Iteration 2 subject and require a new Resolution and a third independent iteration, disproportionate to two non-blocking findings (C-039). Both are recorded and accepted, disclosed limitations instead, per the same standard as R-003. Neither R-005 nor R-006 is a BLOCKER/MAJOR under `protocol/versions/2/policies/review.yml`'s `blocking: [blocker, major]`, so no further iteration is required. No Out-of-Scope Mutation triggering C-048 (`full_review_required: false`). Strict Review for CHG-0050 is closed.

## Review Summary

| | |
|---|---|
| **Iterations** | 2 |
| **Current Subject** | `86a4f25812adc6a5766ee12dc0b2abdf715c4d89` (Iteration 2's reviewed, passed subject) |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 2 (R-005, R-006 — accepted, disclosed, non-blocking) |
| **Final Iteration** | 2 (PASS) |
| **Result** | PASS |

## Reviewer Independence

`provenance.yml`'s `reviewer-001` (Execution `a9c707c9110126514`) and `reviewer-002` (Execution `a55345cff0321b96f`) records — each a fresh agent invocation in its own isolated Git worktree, sharing no Execution or Execution Context with the Implementation, the Resolution, or each other.

## Open Findings

No blocking findings open. R-003 (OBSERVATION), R-005 (MINOR), and R-006 (MINOR) are recorded and accepted, not fixed, per C-039 — see their entries below for why each was left unfixed. None is in `blocking: [blocker, major]`.

## Iteration 1 — REQUEST CHANGES

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a9c707c9110126514`, no shared context with the Implementation that produced this revision), per C-026. This Review ran at the `strict` profile (this Change's own Flow is FULL), fully adversarial.

**Commit reviewed**: `817cda3913d789da3a8d6d0ba28f1b4d47d1fd3a`.

**Baseline for diff**: `94b75b4` (Plan approval provenance commit, i.e. the last commit before Implementation began).

### R-001 · MAJOR — `forge change review-status` crashes with an unhandled `KeyError` instead of failing cleanly

`resolve_effective_review_profile` (`protocol_resolution/__init__.py`) does `PROFILE_RANK[floor]` with no guard. `review_status()`'s call chain can supply an *unvalidated* `floor` — `compute_review_profile_floor` returns a project-flow override's `review.profile` value verbatim, without checking it against the enum — and `review_status()`'s surrounding `try/except` did not catch `KeyError`. Live-reproduced: a `.forge/flows/standard.yml` override of `review.profile: super-strict` (a value `forge validate` already rejects with `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`) made `forge change review-status` dump a raw Python traceback and exit 1, instead of degrading the way the adjacent configuration-error handling already does. FR-006's Boundary explicitly requires this command to be safe to run on a project in a bad state.

**Resolution**: added `KeyError` to `review_status()`'s existing `except` tuple, so an unrecognized floor degrades exactly like every other caught configuration error (the "Resolved profile" line is omitted; the rest of the report still renders). New regression test `test_review_status_does_not_crash_on_an_invalid_project_flow_override_profile` (`tests/cli/test_change_review_status.py`) reproduces R-001 as valid RED against the pre-fix code (`KeyError('super-strict')`, exit 1) and passes after. See `tdd-evidence.yml`'s `TDD-015`.

### R-002 · MINOR — `compute_review_profile_floor` did not eliminate the duplication Architecture claimed it removed

`_validate_review_profile_floor` still independently re-derived the canonical-profile chain inline instead of the extraction actually removing it, per `architecture.md`'s Component Map claim. Not a functional bug (the duplicate branch was dead code on the only path exercised), purely a maintainability concern.

**Resolution**: extracted the shared `_canonical_review_profile(effective)` helper, used by both `compute_review_profile_floor` and `_validate_review_profile_floor`; behavior-preserving (existing `TDD-001` tests pass unchanged).

### R-003 · OBSERVATION — the per-Flow mode-resolution line reflects the canonical Flow's profile, not a project's stricter override

`render_mode_resolution_line` is computed from the canonical Flow only; a project using a stricter-than-canonical `.forge/flows/<flow>.yml` override would see Adapter-projected text that doesn't reflect that override, even though FR-002's own "floor" definition includes it. Confirmed pre-existing: the adjacent, unmodified `REVIEW_PROFILE_INSTRUCTION` line has the identical characteristic, and `_gate_instructions` only ever receives canonical Flow content at this call site (traced via `adapters/service.py`'s `_effective_flows`).

**Not fixed** — accepted, disclosed limitation, consistent with this being a pre-existing Adapter-projection characteristic this Change did not introduce, not a regression. A candidate for a future, narrowly-scoped Change if a project's own stricter override in practice needs to be reflected in install-time projected text.

### R-004 · OBSERVATION — `test-strategy.md`'s TDD-010 prose overstated "byte-identical"

The scaffold always writes an explicit `review.mode: recommended` field regardless of whether a project preference is set, so a no-preference scaffold is not literally byte-identical to a pre-CHG-0050 scaffold — permitted by AC-008's own "(or omits it)" alternative, but the Test Strategy prose overstated what was verified.

**Resolution**: `test-strategy.md`'s TDD-010 Scenario/Evidence/Failure Condition corrected to describe the shipped behavior accurately.

### Checked and found sound (Iteration 1)

- Full suite (independent run): 856 passed, 2 pre-existing warnings — exact match to `verification.md`'s claim.
- `forge validate`: PASS — exact match.
- FR-002's never-below-floor guarantee independently re-derived by code inspection and live reproduction across garbage `mode` values (no crash; always resolves to `floor` or one rank above).
- FR-004's `_validate_review_current_phase` scope confirmed to match AC-010–AC-012b exactly, no more and no less.
- FR-005/DEC-004's claim independently re-derived, not trusted: generated Adapter projections at both the parent and target commits from archived trees, diffed them, and confirmed the `### Reviewer/Resolver independence` block is byte-for-byte identical; confirmed `_gate_instructions` only ever receives canonical Flow content (immune to the R-001-class crash at that call site).
- FR-007 confirmed by absence: zero references to `"stopped"` anywhere in `validation/__init__.py`'s Completion/`review_passed` gating logic.
- FR-006's exit-code/error-path ordering (`passed` → `stopped` → blockers/majors → `resolving` → fallback) traced and found sound and non-overlapping.
- Both new schema additions confirmed genuinely additive (`required` arrays and `additionalProperties: false` unchanged).
- AC-009 (no retroactive override) confirmed structurally: `preferred_mode` is read at exactly one call site in the entire `src/forge_cli/` tree.
- `rfc-acceptance-001`/`plan-approval-001` provenance records independently spot-checked (content digest recomputation, referenced commits exist and substantiate the claimed events).
- `tdd-evidence.yml`'s claimed RED states for TDD-001–004 independently reproduced against the parent commit's archived tree.
- CON-001/CON-002 confirmed: no Contract file touched; independence, evidence/severity handling, and the FR-010 targeted-re-review escalation logic are unmodified.

## Resolution

R-001 and R-002 were fixed, and R-004's documentation inaccuracy corrected, in a Resolution Execution distinct from Iteration 1's Reviewer Execution, in direct response to Iteration 1 (per C-026's Resolver-independence requirement). R-003 was evaluated and explicitly left unfixed as a disclosed, accepted, pre-existing limitation. `tdd-evidence.yml` gained `TDD-015` documenting R-001's RED→GREEN cycle. The resolved revision is frozen and referenced by `provenance.yml`'s `resolution-001` record; Iteration 2 independently re-reviews that exact revision.

## Iteration 2 — REQUEST CHANGES → corrected in-session (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-a55345cff0321b96f`, no shared context with the Resolution Execution or with Iteration 1's Reviewer Execution), per C-026. `kind: resolution_verification`, scoped per C-047 to R-001, R-002, R-004, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `86a4f25812adc6a5766ee12dc0b2abdf715c4d89` (frozen Resolution revision).

**Baseline for diff**: `817cda3913d789da3a8d6d0ba28f1b4d47d1fd3a` (Iteration 1's reviewed subject).

R-001, R-002, and R-004 were each independently re-verified as genuinely fixed — including a live end-to-end reproduction of the exact crash Iteration 1 found (isolated test repository, invalid `.forge/flows/standard.yml` override, confirmed traceback on the pre-fix commit and clean degradation on the Resolution commit) and a temporary revert-and-restore of the one-line fix in the reviewer's own isolated worktree to confirm the regression test genuinely fails without it. The full suite (857 passed) and `forge validate` (PASS) were independently re-run on the Resolution commit, not trusted from `verification.md`'s or `resolution-001`'s claims.

### R-005 · MINOR — `resolution-001`'s declared `scope` omitted `provenance.yml`, which the Resolution commit actually modified

`git diff 817cda39 86a4f25 --stat` shows 8 files changed; `resolution-001`'s declared `scope` listed only 7, omitting `provenance.yml` itself (which gained the `implementation-subject-001` and `reviewer-001` records in that same commit). Materiality assessed as non-blocking: the omitted file is pure review-control metadata (recording an already-completed reviewer's own provenance), not production code, a test, or other behavioral change — so it does not trigger C-048's Out-of-Scope-Mutation escalation to a full Initial Review. The scope declaration itself should still be accurate, since C-047 verification relies on it to bound its own authority.

**Not fixed** — `resolution-001` is an already-committed provenance record; per C-026, "existing subject records and committed Review Iteration revision/subject_provenance bindings are append-only in meaning" — rewriting its `scope` field post-commit would itself be exactly the kind of provenance rewrite C-026 forbids. Accepted, disclosed limitation of the historical record: the true scope of `resolution-001` is the 7 declared paths plus `provenance.yml`, recorded here as the authoritative correction without mutating the original entry.

### R-006 · MINOR — the Resolution introduced a colliding `TDD-011` identifier

`tdd-evidence.yml`'s new cycle documenting R-001's fix was filed as `TDD-011` — but `test-strategy.md` already had a pre-existing, unrelated `TDD-011` (FR-003, "An existing Change's `review.mode` is not retroactively overridden"), untouched by the Resolution and still present. Two unrelated pieces of TDD evidence sharing one identifier breaks the `TDD-xxx` cross-reference this repository's own Artifact Structure convention relies on for traceability.

**Not fixed** — `tdd-evidence.yml` is not review-control metadata (only `manifest.yml`, `provenance.yml`, and `review.md` may differ from the frozen subject per C-026); editing it now, after Iteration 2 already reviewed and passed commit `86a4f25`, would itself invalidate that passed subject and require a new Resolution plus a third independent iteration — disproportionate to one colliding identifier between two non-blocking evidence files (C-039). Accepted, disclosed limitation: readers should treat `tdd-evidence.yml`'s `TDD-011` (R-001's regression cycle) and `test-strategy.md`'s `TDD-011` (FR-003) as two distinct, unrelated entries that happen to share a number: a future Change touching either file should renumber the newer one.

### Checked and found sound (Iteration 2)

- Commits verified reachable and correctly parent/child; diff matches the declared scope except for `provenance.yml` itself (R-005, disclosed).
- R-001's fix independently reproduced end-to-end, including a temporary revert-and-restore of the one-line fix to confirm the regression test's own validity.
- R-002's `_canonical_review_profile` extraction independently confirmed behavior-preserving; `tests/unit/test_validation_review_profile.py` re-run unchanged.
- R-004's corrected prose independently confirmed accurate against `change_scaffolding.py::_manifest()`'s actual unconditional `"mode": review_mode` write.
- The added `KeyError` catch independently traced across every call inside `review_status()`'s try block and confirmed not to mask any exception other than the one R-001 targets.
- No material Out-of-Scope Mutation (`full_review_required: false`).

## Resolution (Iteration 2 findings)

R-005 and R-006 were both non-blocking MINOR findings discovered within the Resolution Delta itself (not unrelated latent findings under C-050, and not requiring escalation under C-048). Unlike Iteration 1's findings, fixing either would require mutating an already-committed provenance record (R-005) or editing a non-review-control-metadata file after its subject was already reviewed and passed (R-006) — both of which C-026 itself forbids or would invalidate. Both are therefore recorded and accepted as disclosed limitations rather than fixed, consistent with `blocking: [blocker, major]` (neither blocks) and C-039 (proportionality: a third independent iteration for two cosmetic/record-keeping findings is not warranted). Strict Review for CHG-0050 is closed.
