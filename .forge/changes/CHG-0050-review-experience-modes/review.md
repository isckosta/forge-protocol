---
forge:
  artifact: review
  schema: 1
change: CHG-0050
status: complete
---

# CHG-0050 · Review

## Verdict

**PASS**. Iteration 1: REQUEST CHANGES — R-001 (MAJOR) and R-002 (MINOR) found and resolved; R-003 (OBSERVATION) accepted/disclosed, R-004 (OBSERVATION) corrected. Iteration 2 (Resolution Verification): R-001/R-002/R-004 independently re-verified as fixed; R-005/R-006 (MINOR, non-blocking) accepted, disclosed, not fixed (C-026/C-039). After Iteration 2 passed, Codex's automated review of the open GitHub PR (an external review surface, C-027) found three further real, reproducible correctness defects (R-007/R-008/R-009, elevated to MAJOR — see "External Review Surface" below); all three were fixed in `resolution-002` (commit `082b81a`). Iteration 3 (Resolution Verification of `resolution-002`): all three independently reproduced RED-before/GREEN-after, R-007/R-009 additionally verified end-to-end against a real `forge init` project, no Out-of-Scope Mutation, no new findings. Strict Review for CHG-0050 is closed.

## Review Summary

| | |
|---|---|
| **Iterations** | 3 |
| **Current Subject** | `082b81ab98ed54d602843284dff59c1457f339a6` (`resolution-002`, Iteration 3's reviewed, passed subject) |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 2 (R-005, R-006 — accepted, disclosed, non-blocking) |
| **Final Iteration** | 3 (PASS) |
| **Result** | PASS |

## Reviewer Independence

`provenance.yml`'s `reviewer-001` (Execution `a9c707c9110126514`), `reviewer-002` (Execution `a55345cff0321b96f`), and `reviewer-003` (Execution `a75fefa6bdb33fcb9`) records — each a fresh agent invocation in its own isolated Git worktree, sharing no Execution or Execution Context with the Implementation, the Resolution(s), or each other.

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

## Post-Review Correction — `plan.md` restored to its originally-approved wording

While fixing an unrelated `forge-merge-readiness` gap (MR-008), it emerged that Plan item 9's text had been directly edited during Implementation to reflect DEC-004's corrected mechanism (see `architecture.md`), diverging from the wording the human maintainer actually approved via `AskUserQuestion` and that `provenance.yml`'s `plan-approval-001` content digest was computed against. Per C-069 ("An approved Plan SHOULD NOT be edited to silently absorb an Implementation-time discovery... SHOULD be recorded in Verification, a Decision record, or a documented re-Plan"), `plan.md` has been restored byte-for-byte to its originally-approved content (matching commit `153b0d9`); DEC-004's mechanism correction remains recorded where it belongs, in `architecture.md` and `manifest.yml`'s `decisions[]`, not in the approved Plan text itself. `plan-approval-001`'s content digest is unchanged by this restoration (it now matches the restored file exactly, as it always should have).

## Resolution (Iteration 2 findings)

R-005 and R-006 were both non-blocking MINOR findings discovered within the Resolution Delta itself (not unrelated latent findings under C-050, and not requiring escalation under C-048). Unlike Iteration 1's findings, fixing either would require mutating an already-committed provenance record (R-005) or editing a non-review-control-metadata file after its subject was already reviewed and passed (R-006) — both of which C-026 itself forbids or would invalidate. Both are therefore recorded and accepted as disclosed limitations rather than fixed, consistent with `blocking: [blocker, major]` (neither blocks) and C-039 (proportionality: a third independent iteration for two cosmetic/record-keeping findings is not warranted).

## External Review Surface — Codex automated PR review (GitHub PR #44)

After Strict Review closed with PASS, Codex's automated review of the open GitHub PR (an active external review surface, C-027) posted three findings against the merged/passed subject. Each is real, reproducible, and was missed by both independent Strict Review iterations above.

### R-007 · MAJOR — `compute_review_profile_floor` did not clamp an invalid, weaker-than-canonical project override

An invalid project-flow override (e.g. `focused` under a canonical `standard` floor — already rejected by `forge validate` as `E_FORGE_REVIEW_PROFILE_BELOW_FLOOR`) made `compute_review_profile_floor` return the invalid value verbatim. `forge change review-status` calls this helper directly, without re-running the floor validator, so it could print a resolved profile below the Change's real canonical floor for a misconfigured project — a direct violation of FR-002's own never-below-floor guarantee, on the specific path where the stored configuration is itself invalid.

**Resolution**: `compute_review_profile_floor` now clamps to the canonical floor whenever the project override's rank is lower. `_validate_review_profile_floor` was refactored to read the raw project override directly (not through `compute_review_profile_floor`) so its own below-floor detection is unaffected by the new clamp — verified by an unchanged `tests/unit/test_validation_review_profile.py` suite. See `tdd-evidence.yml`'s `TDD-015`.

### R-008 · MAJOR — `_validate_review_current_phase` only checked one direction

`review.status: passed` paired with a non-converged `current_phase` (`stopped`, `findings_recorded`, ...) passed validation silently — the reverse of the already-checked `converged`-requires-`passed` direction. This is a real gap against FR-007's own guarantee: a manifest could claim `status: passed` while `current_phase: stopped` contradicted it, and nothing caught the contradiction.

**Resolution**: `_validate_review_current_phase` now also flags `status: passed` with any non-`None`, non-`converged` phase. See `tdd-evidence.yml`'s `TDD-016`.

### R-009 · MAJOR — Adapter projection reflected the canonical Review Profile, not the effective one

`AdapterService._effective_flows` yaml-dumped only `effective["canonical"]` into the per-Flow content `_gate_instructions` parses, discarding any project-flow profile override before it ever reached the Adapter layer. A project that validly raised a Flow's floor above canonical (e.g. FAST from `focused` to `strict`) still received Harness instructions describing the weaker canonical value — for both the pre-existing (CHG-0048) profile instruction and this Change's own new mode-resolution line, since both read the same per-Flow `review_profile` variable.

**Resolution**: `_effective_flows` now projects `compute_review_profile_floor(effective)`'s clamped, effective profile into the dumped `review.profile` field before handing it to `_gate_instructions`. See `tdd-evidence.yml`'s `TDD-017`. This also resolves R-003 (previously accepted as a disclosed limitation in Iteration 2) as a side effect of the same fix — R-003 is superseded, not separately re-verified.

### Classification

Elevated to MAJOR (not MINOR/OBSERVATION like R-003/R-005/R-006): each finding is a genuine correctness defect undermining a guarantee this Change explicitly advertises (never-below-floor, `stopped` carries no authority, Adapter instructions match actual requirements), not a documentation-accuracy or record-keeping gap. All three are fixed, not disclosed-and-accepted.

In the same Resolution scope, CHG-0051's canonical-review-profile-nesting fix (the same root cause as R-007, independently discovered and already fixed on a separate branch/PR for `main`) was applied to this branch's own `_canonical_review_profile`, since this branch extracted that logic before the fix existed.

## Iteration 3 — PASS (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree, no shared context with the Resolution Execution that produced `resolution-002` or with Iteration 1/2's Reviewer Executions), per C-026. `kind: resolution_verification`, scoped per C-047 to R-007, R-008, R-009, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `082b81ab98ed54d602843284dff59c1457f339a6` (frozen Resolution revision, `resolution-002`).

**Baseline for diff**: `aece3063bcd60289e152057af42cad0abcd7b84f` (Iteration 2's passed subject, after the post-Review corrections above).

R-007, R-008, and R-009 were each independently reproduced as valid RED against the parent commit and confirmed GREEN on the fixed commit. R-007 and R-009 were additionally verified end-to-end against a real `forge init` project with a project-flow profile override: `compute_review_profile_floor` correctly clamps a weaker override to canonical while `forge validate` still independently rejects that same weaker override (confirming the clamp did not silently disable the write-path's own rejection); `forge adapter install` for both `claude_code` and `codex` now generates Harness instructions reflecting the effective, project-raised profile, not the canonical one. The diff matched `resolution-002`'s declared scope exactly (no Out-of-Scope Mutation, unlike Iteration 2's own disclosed R-005 gap). No new findings.

### Checked and found sound (Iteration 3)

- `082b81a` confirmed a direct child of `aece3063`; `git diff --stat` matches `resolution-002`'s declared scope exactly.
- R-007: clamp behavior confirmed live; `_validate_review_profile_floor`'s own below-floor rejection confirmed still firing (reads the raw override directly, not through the now-clamping helper).
- R-008: both non-converged phases (`stopped`, `findings_recorded`) confirmed flagged when paired with `status: passed`; original `converged`-requires-`passed` direction confirmed unregressed.
- R-009: end-to-end `forge adapter install` run confirmed both the pre-existing profile instruction and the new mode-resolution line reflect the effective profile for both Adapters.
- Full suite (861 passed) and `forge validate` (PASS) independently reproduced.
- `tdd-evidence.yml`'s `cycle_count: 14` matches its 14 listed cycles; no new identifier collisions beyond the already-disclosed R-006.
- Only `manifest.yml`/`provenance.yml`/`review.md` touched after the `082b81a` freeze (commit `7620b20`), matching the C-026 exception exactly.

## Conclusion

`resolution-002` genuinely and correctly fixes R-007, R-008, and R-009 within its declared scope, with no Out-of-Scope Mutation and no regression to `forge validate`'s own below-floor rejection. Strict Review for CHG-0050 is closed with a PASS across three iterations.
