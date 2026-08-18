---
forge:
  artifact: review
  schema: 1
change: CHG-0012
status: failed
iteration: 2
---

# Strict Review — Freeze check exempts complete Changes

## Iteration 1 — REQUEST CHANGES

Reviewed revision: `47468fec276ceb4ab1137aa94f5a2b26760fc6da` (`implementation-001`, per `provenance.yml`).

Reviewer Execution: `review-exec-chg0012-20260818-01`.
Reviewer Execution Context: `review-context-chg0012-20260818-01`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is CHG-0012's own first Strict Review Iteration (`kind: initial_review`), independent in Execution and Execution Context from the Implementation session that produced `implementation-001`.

### Verification performed

- Read `intent.md`, `inspection.md`, `verification.md`, `manifest.yml`, `provenance.yml` in full, then `git show 47468fec276ceb4ab1137aa94f5a2b26760fc6da` for the actual diff.
- Read `src/forge_cli/validation/__init__.py` in full for `_validate_protocol2_review_provenance` (lines 288-362) and its helpers (`_changed`, `_reviewable_workspace_delta`, `_record_fields`, `_review_control_metadata_paths`), not just the two cited lines.
- `.venv/bin/python -m pytest -q`: **374 passed**, matching `verification.md`'s claim.
- `.venv/bin/forge validate`: exit 0, "Forge project is valid" — independently reproduces the fix closing GitHub Actions run `32091880352`'s exact two findings (CHG-0008, CHG-0011).
- `.venv/bin/forge doctor`: exit 0, all 7 checks PASS.
- `git show 47468fec... --stat`: confirmed the delta is exactly the two Change artifacts (`intent.md`, `inspection.md`) already committed as part of the frozen subject, plus `manifest.yml`, `verification.md`, `CHANGELOG.md`, the one-line fix to `src/forge_cli/validation/__init__.py`, and the new test module — nothing outside what `provenance.yml`'s `implementation-001.revision.description` and `manifest.yml`'s `documentation.reason` claim.
- Root cause and precedent independently confirmed: line 296's `forge/change@1` exemption (`st.get("current")!="complete"`) and the fixed line 348 use the exact same field, the exact same string comparison, and the exact same `state` mapping (`st`) already loaded once per manifest at the top of the loop (line 294) — not a superficial resemblance; it is literally the same pattern applied to a second, independent condition in the same function.
- Adversarially probed the central risk this review was directed to evaluate (below), with a hand-built, real-Git-backed reproduction against the actual `validate_project`, not mocked.

### Findings

- **CHG-0012-R001 — BLOCKER — `state.current: complete` is a self-declared field with zero programmatic gate anywhere in this codebase, and this fix turns it into a total bypass of C-026's freeze-drift protection for the Change's *own* reviewed subject files, not merely for unrelated repository activity.**

  `_changed(r, mpath, sim[1])` / `_reviewable_workspace_delta` (lines 67-84) compute the diff between the frozen implementation commit and current HEAD across the **entire repository**, excluding only that Change's own three review-control-metadata paths (`manifest.yml`, `provenance.yml`, `review.md`). It is not scoped to the files the Change's own implementation commit actually touched. This is the real root cause of the CI breakage (any other Change's commits trip it), but it also means the check was — before this fix — incidentally also the *only* mechanism in the entire codebase that detects a reviewed file being silently edited after its Review passed. This fix disables that check unconditionally once `state.current == "complete"`, which removes both the false positive (unrelated files) and the true positive (this Change's own reviewed files being tampered with post-freeze) at the same time.

  Confirmed by direct reproduction (`validate_project`, real Git repo, not mocked): a Change with a passed Review Iteration frozen at commit C1, `state.current: strict_review`, whose own reviewed file (`reviewed_module.py`, part of C1) is edited afterward — correctly fires `"C-026 review subject changed after its immutable revision freeze"`. The identical scenario with only `state.current: complete` changed — same tampered file, same edit — produces **zero findings**. `forge validate` passes silently.

  No other check in `_validate_protocol2_review_provenance` catches this once `state.current == "complete"`: the `sa`/`ia` first-committed-authority checks (lines 332-340) protect the *provenance/manifest records* from being rewritten, not the source files they point to; the reviewer-independence checks (350-359) are gated on `status == "passed"` and unaffected either way, but they only check that Reviewer and subject provenance records reference different Execution/Context — they say nothing about whether the code still matches what was reviewed. Repository-wide, no `forge complete` command, no Completion Gate, and no validator for C-027 ("Blocking review evidence blocks Completion") or C-035 ("No false Completion") exist in `src/forge_cli/` (confirmed: `grep -rn "C-035\|C-027" src/ tests/` returns nothing). `state.current` is set by hand in `manifest.yml` with no independent verification anywhere that Completion was legitimately reached before the freeze exemption applies to it.

  `intent.md`'s Goal section ("After Completion, the Change is closed history; unrelated, expected activity elsewhere in the repository must not resurrect it") and `inspection.md`'s "Scope verified not to include" both frame the tradeoff as safe because only "unrelated" activity is exempted — but the mechanism does not and cannot distinguish "unrelated" drift from drift in the Change's own reviewed files; both are silenced identically. This is not a hypothetical: it is the exact class of finding the review brief was directed to construct, and it reproduces on the first attempt.

  A precise fix exists in this same codebase's own idiom: scope `_changed`/`_reviewable_workspace_delta` to the set of paths the frozen implementation commit itself touched (analogous to how `_resolution_delta`/`_uncovered_paths`, added by CHG-0011 for Resolution Scope, already compare a specific commit range rather than the whole repository) rather than exempting the check outright by `state.current`. That would eliminate the false positive (other Changes' unrelated commits) while preserving the true positive (this Change's own files drifting post-freeze) for Changes at any `state.current` value, including `complete`.

### Assessment against the Change's own declared terms

- The root-cause diagnosis (`intent.md`, `inspection.md`) is accurate and independently verified against the code, not just plausible-sounding.
- The precedent claim (line 296 mirrors line 348) is accurate, not superficial — confirmed by reading both branches.
- `test_active_change_still_detects_freeze_drift` genuinely proves the freeze is unweakened for a *non-complete* Change with an *unrelated* file drifting; it does not, and was not designed to, prove anything about a *complete* Change's *own* reviewed files, which is the actual gap.
- The fix closes the real, urgent CI failure and the regression suite (`374 passed`), `forge validate` (exit 0), and `forge doctor` (all PASS) all reproduce cleanly.
- However, the fix as shipped trades a false-positive bug for a silent, unbounded true-negative in a Contract-level (C-026) freeze invariant, with no compensating control anywhere in the codebase, and the Change's own artifacts do not disclose or accept this tradeoff — they assert (incorrectly) that only "unrelated" activity is affected.

### Verdict

**REQUEST CHANGES**

Finding counts:

- BLOCKER: 1 (CHG-0012-R001)
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0

Per C-027, Completion MUST NOT proceed with an unresolved BLOCKER finding present. A Resolution scoping the freeze-drift check to the frozen implementation commit's own touched paths (rather than exempting it entirely for `complete` Changes) — or an equally effective alternative that closes CHG-0012-R001 without reintroducing the CI false-positive — is required before the next Strict Review Iteration.

## Iteration 2 — REQUEST CHANGES

Reviewed revision: `e0b4b141f3cd164299710a4249cbd71430592abf` (`resolution-001`, per `provenance.yml`), a Resolution of Strict Review Iteration 1's BLOCKER (`targets: [CHG-0012-R001]`).

Reviewer Execution: `review-exec-chg0012-20260818-02`.
Reviewer Execution Context: `review-context-chg0012-20260818-02`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is a Strict Review Iteration with `kind: resolution_verification` (CHG-0011), independent in Execution and Execution Context from `resolution-001` (this Resolution's own execution) and from `review-001` (Iteration 1's Reviewer). Per CHG-0011's Resolution Verification framing, authority is bound to: (a) whether CHG-0012-R001 was genuinely fixed; (b) whether `resolution-001`'s own delta introduced a new defect (class B, Resolution Regression); (c) whether the Resolution Delta stayed within its declared `scope`; (d) provenance/revision/subject correctness for this Iteration. A pre-existing, unrelated (class D) issue would be recorded, not silently dropped, but does not by itself expand this into an unrestricted re-audit.

**On the framing itself:** it meaningfully narrowed this review relative to Iteration 1. I read the whole diff and the whole rewritten function for context, but I did not re-walk unrelated C-026 machinery (Iteration/provenance identity authority, Execution/Context independence checks) that Iteration 1 already exhaustively covered and `resolution-001` did not touch — the taxonomy gave a principled reason not to re-litigate that surface, while still leaving room to pursue the one place a genuinely new, in-scope defect turned out to live: the new function itself.

### Verification performed

- Read `intent.md`, `inspection.md`, `specification-drift.md`, `verification.md`, `review.md` (Iteration 1), `provenance.yml`, `manifest.yml` in full, then `git show e0b4b141f3cd164299710a4249cbd71430592abf` for the actual diff.
- Computed the Resolution Delta directly: `git diff --name-status 47468fec276ceb4ab1137aa94f5a2b26760fc6da..e0b4b141f3cd164299710a4249cbd71430592abf` →  `inspection.md`, `intent.md`, `provenance.yml` (A), `specification-drift.md`, `verification.md`, `src/forge_cli/validation/__init__.py`, `tests/unit/test_freeze_check_exempts_complete_changes.py`. Excluding `provenance.yml` (review-control metadata, per the standard exception), this is **exactly** `resolution-001`'s declared `scope` (6 paths) — no more, no less. No Out-of-Scope Mutation (class C: 0).
- Read the new `_first_commit_where_state_complete` and the rewritten freeze-drift branch (`src/forge_cli/validation/__init__.py` lines 236-263, 373-384) in full, not just the two cited hunks.
- `.venv/bin/python -m pytest -q`: **376 passed**, matching `verification.md`. Ran `tests/unit/test_freeze_check_exempts_complete_changes.py` individually (`-v`): all 4 tests pass, including `test_tampering_between_freeze_and_completion_is_still_detected` (independently confirms CHG-0012-R001's own scenario — the Change's own reviewed file tampered with *before* the genuine completion seal — is now caught) and `test_tampering_after_completion_is_a_disclosed_residual_limitation` (confirms the accepted false-positive-avoidance case: the same file legitimately edited by a *later* Change *after* this Change's seal is still silently accepted).
- `.venv/bin/forge validate`: exit 0, "Forge project is valid".
- `.venv/bin/forge doctor`: exit 0, all 7 checks PASS.
- Adversarially probed `_first_commit_where_state_complete`'s history walk with a hand-built, real-Git-backed reproduction against the actual `validate_project` (not mocked, not reusing the shipped test as-is): shallow-clone/absent-history and malformed-`state`-block cases fail closed correctly (`sealed is None` → falls back to `_changed`, the strict pre-exemption comparison, never a silent pass); cross-Change path collision is not possible (the history walk is scoped to this Change's own `manifest.yml` path). Re-derived independently (not trusting `inspection.md`'s framing): choosing the **first** commit where `complete` appears, rather than the most recent one, is the *more conservative* choice for a manifest that is edited again post-seal while remaining `complete` (it minimizes the protected window rather than needlessly extending it) — but that conservative property assumes `state.current` only ever moves forward once. It does not.

### Findings

- **CHG-0012-R002 — BLOCKER (class B, Resolution Regression) — `_first_commit_where_state_complete` anchors on the *first* commit where `state.current` is `complete`, with no check that the manifest never reverted from `complete` afterward; toggling `state.current` back and forth hides post-seal tampering inside the now-unmonitored gap.**

  Reproduced directly against `validate_project` (real Git repo, not mocked; script preserved this session): C1 freezes `reviewed_module.py` (subject). C2 records the passed Review (`strict_review`). C3 legitimately seals `state.current: complete` (file untouched — this is the commit `_first_commit_where_state_complete` will return). C4 reverts `state.current` back to `strict_review` in the same manifest. C5 tampers `reviewed_module.py`'s content. C6 re-seals `state.current: complete`. `validate_project` on this repository produces **zero findings** — the tampering in C5 is completely invisible, because `_resolution_delta` only ever compares the frozen subject (C1) against C3 (the *first* complete commit), and nothing re-examines the manifest's own `state.current` field for having moved backward in between.

  This is not a hypothetical corner case disconnected from the threat model this Change itself operates under: Iteration 1 already established, and this Resolution's own fix accepts, that `state.current` is "a self-declared field with zero programmatic gate anywhere in this codebase" — anyone who can hand-edit `manifest.yml` (the exact actor R001 was written against) can perform this revert/re-seal sequence with two extra commits. The Resolution closes the specific attack R001 demonstrated (single tamper, single seal) but the same trust assumption it relies on — that the *first* recorded `complete` is authoritative — is not itself protected against the manifest's own `state.current` field being non-monotonic, unlike the analogous "first committed wins" pattern used elsewhere in this file for provenance/Iteration identity (`_first_committed_provenance_record`, `_first_committed_review_iteration`), where the *current* value is checked to still equal the first-committed one. `_first_commit_where_state_complete` has no equivalent check.

  This finding is squarely inside the Resolution's own delta — `_first_commit_where_state_complete` is new code introduced by `resolution-001`, not a pre-existing (class D) condition — so it is in scope for this Resolution Verification under FR-007(b).

### Assessment against Resolution Verification's bounded authority

- **(a) Is CHG-0012-R001 fixed?** Yes, for the scenario R001 actually demonstrated (a single tamper between freeze and a single, non-reverted completion seal) — independently reproduced and reconfirmed via the shipped regression test plus direct code reading.
- **(b) Resolution regression?** Yes — CHG-0012-R002 above, a new defect living entirely inside `resolution-001`'s own delta.
- **(c) Resolution Scope respected?** Yes — the Resolution Delta is exactly the declared 6-path `scope`, no Out-of-Scope Mutation.
- **(d) Provenance/revision/subject correctness?** `resolution-001` correctly declares `role: resolution`, `targets: [CHG-0012-R001]`, non-empty exact-path `scope`, and an Execution/Context (`resolution-exec-chg0012-20260818-01`/`resolution-context-chg0012-20260818-01`) distinct from both `implementation-001` and `review-001`. No defect found here.

### Verdict

**REQUEST CHANGES**

Finding counts (this Iteration):

- BLOCKER: 1 (CHG-0012-R002, class B)
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0
- new_material_findings: 1 (CHG-0012-R002; class A/D findings, of which there are none this Iteration, would not count per FR-013)

Per C-027, Completion MUST NOT proceed with an unresolved BLOCKER finding present. This Iteration does not, by itself, require Full Review Escalation (`full_review_required: true`) — CHG-0012-R002 is a class B Resolution Regression, not an Out-of-Scope Mutation (FR-006), and the Convergence Limit (2 consecutive `resolution_verification` Iterations with `new_material_findings > 0`) has not been reached at this Iteration (only 1 so far). A further Resolution scoped to CHG-0012-R002 — for example, tracking the manifest commit where `state.current` first became `complete` *and never subsequently reverted before the diff endpoint used*, or otherwise making `_first_commit_where_state_complete`'s anchor robust to non-monotonic `state.current` — followed by another `resolution_verification` Iteration, remains available before Full Review Escalation would be required.
