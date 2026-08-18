---
forge:
  artifact: review
  schema: 1
change: CHG-0012
status: passed
iteration: 5
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

## Iteration 3 — REQUEST CHANGES

Reviewed revision: `e243604a1bc65bca30e4d11589e71253d0842740` (`resolution-002`, per `provenance.yml`), a Resolution of Resolution Verification Iteration 2's BLOCKER (`targets: [CHG-0012-R002]`).

Reviewer Execution: `review-exec-chg0012-20260818-03`.
Reviewer Execution Context: `review-context-chg0012-20260818-03`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

This is a Strict Review Iteration with `kind: resolution_verification` (CHG-0011), independent in Execution and Execution Context from `resolution-002`, `review-002`, `resolution-001`, `review-001`, and `implementation-001`. Authority is bound to: (a) whether CHG-0012-R002 was genuinely fixed; (b) whether `resolution-002`'s own delta (or its direct evidenced consequences, per FR-007(b)) introduced a new defect (class B); (c) whether the Resolution Delta stayed within its declared `scope`; (d) provenance/revision/subject correctness for this Iteration.

### Verification performed

- Read `intent.md`, `inspection.md`, `specification-drift.md`, `verification.md`, `review.md` (Iterations 1-2), `provenance.yml`, `manifest.yml` in full, focused on the Resolution 2 sections.
- Read `git show e243604a1bc65bca30e4d11589e71253d0842740` in full: the rewritten `_first_commit_where_state_complete` (`src/forge_cli/validation/__init__.py` lines 236-284) and its new regression test.
- Computed the Resolution Delta directly: `git diff --name-status e0b4b141f3cd164299710a4249cbd71430592abf..e243604a1bc65bca30e4d11589e71253d0842740` → `manifest.yml`, `provenance.yml`, `review.md` (review-control metadata, excluded per the standard exception), `specification-drift.md`, `verification.md`, `src/forge_cli/validation/__init__.py`, `tests/unit/test_freeze_check_exempts_complete_changes.py`. Excluding review-control metadata, this is **exactly** `resolution-002`'s declared `scope` (4 paths) — no more, no less. No Out-of-Scope Mutation (class C: 0).
- `.venv/bin/python -m pytest -q`: **377 passed**, matching `verification.md`.
- `.venv/bin/forge validate`: exit 0, "Forge project is valid".
- `.venv/bin/forge doctor`: exit 0, all 7 checks PASS.
- Built independent, hand-written, real-Git-backed reproductions against the actual `validate_project` (not mocked, not reusing the shipped tests as-is), reusing `tests/unit/test_freeze_check_exempts_complete_changes.py`'s helpers:
  - **CHG-0012-R002's own scenario** (seal → revert → tamper → reseal, single cycle): correctly detected. Confirms the shipped `test_reverting_and_resealing_complete_cannot_hide_tampering`.
  - **Double revert/reseal cycle** (seal → revert → reseal → revert → tamper → reseal): correctly detected — the first revert alone is sufficient to make `_first_commit_where_state_complete` fail closed (return `None`), regardless of how many cycles follow.
  - **Tampering in the same commit as the revert** (one commit both reverts `state.current` and edits the reviewed file): correctly detected.
  - **A post-seal commit with genuinely malformed YAML in `manifest.yml`, followed by tampering, followed by a commit restoring a valid `complete` manifest at HEAD**: correctly detected — the `yaml.YAMLError` branch (lines 272-275) fails closed exactly as designed.
  - **CHG-0012-R001's original scenario** (single tamper before the first seal): still correctly detected.
  - **The original CI false positive** (a later, independent edit to the same file, occurring cleanly after a genuine, non-reverted seal): still silently accepted, as intended.

### Findings

- **CHG-0012-R003 — BLOCKER (class B — direct evidenced consequence of `resolution-002`'s own delta, FR-007(b)) — `_first_commit_where_state_complete` walks only commits `git log --diff-filter=AM` returns for the manifest path, which never includes a deletion commit; deleting `manifest.yml`, tampering with the reviewed file, then recreating `manifest.yml` with `state.current: complete` produces zero findings, defeating the exact "walks the entire history... fails closed on an ambiguous history" guarantee `resolution-002`'s own docstring (lines 248-257) claims to provide.**

  Reproduced directly against `validate_project` (real Git repo, not mocked): C1 freezes `reviewed_module.py`. C2 seals `state.current: complete` cleanly (`manifest.yml` created here — this is the commit the function returns). C3 **deletes** `manifest.yml` entirely (a `D`-type diff, invisible to `--diff-filter=AM`, so it is never inspected by the loop at all — unlike a revert or a parse failure, which the loop's `sealed is not None: return None` branches do catch). C4 tampers `reviewed_module.py`. C5 recreates `manifest.yml` (an `A`-type diff, so it *is* visible) with `state.current: complete` again. The history walk sees only C2 (`sealed = C2`, `current == "complete"`) then C5 (`current == "complete"`, `elif current!="complete"` is false, no `return None`) — the entire C3-C4 window is structurally absent from the walk, not merely unexamined. `_first_commit_where_state_complete` returns C2, `_resolution_delta` compares the frozen subject only against C2, and the tampering at C4 is invisible. `validate_project` produces zero findings. Confirmed reproducible with a single delete/recreate cycle and with two consecutive delete/recreate cycles (tampering hidden in the second window).

  This is squarely a **direct evidenced consequence** of `resolution-002`'s delta, not a bare pre-existing/unrelated (class D) condition: the `git log --diff-filter=AM` construction itself is unchanged since `resolution-001` (confirmed: it does not appear in `resolution-002`'s diff hunk, `git show e243604a1bc65bca30e4d11589e71253d0842740`), but `resolution-002`'s *new* code and its *new* docstring (added in this delta) make an explicit, general claim of comprehensiveness — "walks the *entire* [post-seal] history," "fails closed rather than silently trusting an ambiguous history" — that the shipped fix does not deliver. The new `sealed`-tracking loop explicitly enumerates and closes two ambiguity classes it is responsible for (a reverted `current` value; an unparseable snapshot) but omits a third, equally reachable one it does not mention or guard: a missing snapshot, reachable via deletion, which the same actor R001/R002 were written against (anyone who can hand-edit `manifest.yml` can also delete it) can trivially produce. Whether `_first_commit_where_state_complete`'s underlying history source should instead use `--diff-filter=AMD` (or otherwise treat a deletion commit as an unconditional `return None` once `sealed is not None`, matching the same pattern already used for the other two ambiguity classes) is a Resolution decision, not this Iteration's to make — but the gap is real, reproduces cleanly, and defeats the exact guarantee this Resolution's own text asserts.

- **(class D, OBSERVATION, unrelated to `_first_commit_where_state_complete`) — a `manifest.yml` that is genuinely malformed YAML *at HEAD* causes `validate_project` to produce zero findings for that Change entirely** (not merely to skip the freeze-drift check), rather than surfacing a diagnostic about the unparseable manifest. Observed as a side effect while constructing the malformed-YAML repro above (a manifest left broken at HEAD, rather than repaired by a later commit, produced no findings at all for that Change). This is not inside `resolution-002`'s delta — `_validate_protocol2_review_provenance`'s top-level manifest-scanning loop (not `_first_commit_where_state_complete`) predates CHG-0012 entirely and is unrelated to this Change's own fix — and is not, by itself, BLOCKER or MAJOR severity on the evidence gathered here, so per FR-009 it does not force escalation or affect the convergence counter. Recorded per FR-008 so it is not silently dropped; not pursued further, as doing so would exceed this Iteration's bounded authority.

### Assessment against Resolution Verification's bounded authority

- **(a) Is CHG-0012-R002 fixed?** Yes, for the scenario R002 actually demonstrated (a single revert-then-reseal cycle) and for the variants adjacent to it tested here (multiple revert cycles, revert-and-tamper in one commit, mid-history YAML corruption with a later valid HEAD) — independently reproduced and reconfirmed.
- **(b) Resolution regression?** Yes — CHG-0012-R003 above, a defect that is a direct evidenced consequence of `resolution-002`'s own delta (its new fail-closed design omits the deletion/missing-snapshot ambiguity class it otherwise claims to close).
- **(c) Resolution Scope respected?** Yes — the Resolution Delta is exactly the declared 4-path `scope`, no Out-of-Scope Mutation.
- **(d) Provenance/revision/subject correctness?** `resolution-002` correctly declares `role: resolution`, `targets: [CHG-0012-R002]`, a non-empty exact-path `scope`, and an Execution/Context (`resolution-exec-chg0012-20260818-02`/`resolution-context-chg0012-20260818-02`) distinct from every prior record. No defect found here.

### Verdict

**REQUEST CHANGES**

Finding counts (this Iteration):

- BLOCKER: 1 (CHG-0012-R003, class B)
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 1 (class D, malformed-manifest-at-HEAD producing zero findings — not counted per FR-013, recorded per FR-008)
- new_material_findings: 1 (CHG-0012-R003; the class D observation does not count per FR-013)

Per C-027, Completion MUST NOT proceed with an unresolved BLOCKER finding present. **This is the second consecutive `resolution_verification` Iteration with `new_material_findings > 0`** (Iteration 2 found CHG-0012-R002; this Iteration finds CHG-0012-R003), reaching the Convergence Limit referenced in Iteration 2's verdict. Per the engineer's own stated policy for this cycle, this Iteration does not proceed to attempt a fourth automatic fix; it reports CHG-0012-R003 and returns authority to the engineer to make an explicit decision (accept as documented residual risk, pursue a further scoped Resolution, or another course) rather than triggering another automatic Resolution attempt.

## Iteration 4 — REQUEST CHANGES (`kind: initial_review`)

Reviewed revision: `03b51d1b251c11e1d52d6fefd5b40287213fb286` (`resolution-003`, per `provenance.yml`), the engineer's Resolution of CHG-0012's Non-Convergence.

Reviewer Execution: `review-exec-chg0012-20260818-04`.
Reviewer Execution Context: `review-context-chg0012-20260818-04`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

Per `protocol/versions/2/specification.md` Section 13, the Iteration immediately following a Non-Convergence episode MUST be `kind: initial_review` (a `resolution_verification` is invalid at this position) and MUST carry its own `convergence_decision`. This Iteration is independent in Execution and Execution Context from `resolution-003`, `review-003`, `resolution-002`, `review-002`, `resolution-001`, `review-001`, and `implementation-001`.

### Verification performed

- Read `review.md` (Iterations 1-3), `specification-drift.md`, `intent.md`, `inspection.md`, `knowledge-capture.md`, `verification.md`, `manifest.yml`, `provenance.yml`, `CHANGELOG.md` in full.
- Read `protocol/versions/2/specification.md` Sections 12-13 (Convergence/Non-convergence), `protocol/versions/2/policies/review.yml`, `protocol/policies/review.yml`, and `protocol/contract/engineering.md` C-040/C-041 in full.
- Read `.forge/forge.yml` (effective project configuration) and confirmed `review.convergence.allow_residual_risk_acceptance: true`.
- Read `src/forge_cli/validation/__init__.py` in full, including `_validate_resolution_verification` and `_residual_risk_permitted` (the CHG-0011 machinery gating this very Iteration's `convergence_decision`).
- Read `tests/unit/test_freeze_check_exempts_complete_changes.py` in full.
- `git show 03b51d1` in full (complete diff, not a summary).
- `grep -rn` across `src/`, `tests/`, `docs/` for leftover references to `_first_commit_where_state_complete`, `_implementation_touched_paths`, and CHG-0012-R001/R002/R003 — none found outside expected historical narrative.
- `.venv/bin/python -m pytest -q`: **375 passed**. `.venv/bin/forge validate`: exit 0, "Forge project is valid". `.venv/bin/forge doctor`: all 7 PASS.
- `git diff --check` on the reviewed commit: clean. `git diff --check` across the full branch since `830b0dc6` (`diff_only_review: false`): one hit, a trailing blank line at EOF in `inspection.md`.

### Assessment

1. **Procedural validity of the Non-Convergence decision — sound.** `.forge/forge.yml` explicitly enables `allow_residual_risk_acceptance`, changed in this exact commit; `_residual_risk_permitted()` reads exactly that field, so the precondition is mechanically enforced, not decorative. `manifest.yml`/`provenance.yml`/`review.md` at the reviewed revision correctly do not yet contain a formal Iteration-4 entry — consistent with the Resolver recording it after this verdict. The decision's human origin is documented in `specification-drift.md` and `knowledge-capture.md` ("an explicit, justified engineering decision was made by the engineer, not fabricated by the agent") — a self-declared (`assurance: recorded`) claim, consistent with every other provenance record in this system; no stronger proof exists or is expected anywhere in this codebase. Documentation across `specification-drift.md`, `intent.md`, `knowledge-capture.md`, `verification.md`, and `CHANGELOG.md` is specific and does not understate the accepted risk.
2. **Reverted code — correct and clean.** `_first_commit_where_state_complete` and any Attempt-4 helper (`_implementation_touched_paths`) are completely absent from the tree (confirmed via `grep`). The final shape at `src/forge_cli/validation/__init__.py:348` is byte-for-byte the same logical condition as Attempt 1 (`CHG-0012-R001`'s originally-rejected shape) — not stronger, not weaker than `specification-drift.md` describes.
3. **Test honesty — confirmed.** The three shipped tests accurately reflect final behavior, including `test_documented_residual_risk_tampering_a_complete_changes_own_file`, which explicitly asserts *non-detection* of post-completion tampering and names it as the accepted risk rather than pretending it is still caught.
4. **Full adversarial pass — 1 new MAJOR, 2 non-blocking observations** (below). No issues found across the remaining dimensions (correctness, edge_cases, invalid_states, domain_invariants, architecture, authorization, security, persistence, data_integrity, concurrency, transactions, performance, maintainability, backward_compatibility, requirement_compliance, tdd_compliance, test_quality) — the diff is narrowly scoped, and `forge validate`/`forge doctor`/the full suite all reproduce independently.

### Findings

- **CHG-0012-R004 — MAJOR (dimension: documentation, C-041 knowledge consistency) — `inspection.md`'s "Correction after Strict Review Iteration 1" section was not updated by `resolution-003` and still asserts, as current fact, that `_first_commit_where_state_complete` "preserves detection for any tampering between freeze and the genuine seal point."** This is false about the shipped code, which no longer contains that function — that is precisely the residual risk the engineer accepted, not a preserved protection. `intent.md`, `specification-drift.md`, `verification.md`, `knowledge-capture.md`, and `CHANGELOG.md` were all correctly updated in `resolution-003`; `inspection.md` alone was missed. This is the exact class of false safety claim Iteration 1 flagged as `CHG-0012-R001` in `intent.md`'s original text — now surfacing in a sibling artifact the final revert missed. Does not affect the shipped code's correctness or the Non-Convergence decision's validity; a documentation-only fix.
- **OBSERVATION (trivial) — trailing blank line at EOF in `inspection.md`** (`git diff --check`), swept up by the same fix.
- **OBSERVATION (non-blocking, verifiability) — `knowledge-capture.md`'s "Follow-up" section describes Attempt 4 as "implemented, verified against all three prior BLOCKERs," but the code was reverted before being committed, so no artifact in this repository lets an independent reviewer reproduce that verification.** Does not affect the shipped code (Attempt 4 is not part of what's running); recorded for completeness in a review chain that otherwise insisted on independent, hand-built reproduction at every step.

### Verdict

**REQUEST CHANGES**

Finding counts (this Iteration):

- BLOCKER: 0
- MAJOR: 1 (CHG-0012-R004)
- MINOR: 0
- OBSERVATION: 2
- new_material_findings: 1 (CHG-0012-R004; `kind: initial_review`, so this does not feed the `resolution_verification`-only convergence counter)

Per `blocking: [blocker, major]`, this MAJOR must be resolved before Completion. The Non-Convergence decision itself — Section 13 procedure, `accept_residual_risk` eligibility, the reverted code, and the test suite — is independently confirmed sound and honestly documented; this is not a re-litigation of the accepted trade-off, only a cross-file documentation-consistency gap the revert missed.

**`convergence_decision`:** `option: accept_residual_risk`. **Reason:** recorded verbatim in `manifest.yml`'s `review.iterations[3].convergence_decision.reason` (this Iteration independently confirms it is procedurally valid per Section 13 and factually accurate against the reviewed code).

## Iteration 5 — PASS (`kind: resolution_verification` of `resolution-004`)

Reviewed revision: `dad362b6713f42e84db0062ed5687a6ef3adb937` (`resolution-004`, per `provenance.yml`), a Resolution of Strict Review Iteration 4's MAJOR (`targets: [CHG-0012-R004]`).

Reviewer Execution: `review-exec-chg0012-20260818-05`.
Reviewer Execution Context: `review-context-chg0012-20260818-05`.
Assurance: `recorded` (self-recorded repository-native provenance; no cryptographic/external attestation claimed).

Independent in Execution and Execution Context from `resolution-004`, `review-004`, `resolution-003`, `review-003`, `resolution-002`, `review-002`, `resolution-001`, `review-001`, and `implementation-001`. This is the first `resolution_verification` Iteration in a fresh sequence: Iteration 4 (`kind: initial_review`) reset the convergence counter (it does not feed the `resolution_verification`-only streak), so this Iteration does not reopen the already-resolved Non-Convergence episode. Authority is bound to the same four questions as prior Resolution Verifications: (a) is CHG-0012-R004 genuinely fixed; (b) did `resolution-004` introduce a new defect (class B); (c) did the Resolution Delta stay within its declared `scope`; (d) provenance/revision/subject correctness.

### Verification performed

- Read `review.md` (Iterations 1-4, especially Iteration 4) and `provenance.yml`'s `resolution-004` entry in full.
- Read `inspection.md` in full and cross-checked its "Correction after Strict Review Iteration 1, and the final decision" section against the actual shipped code.
- Computed the Resolution Delta directly: `git diff --name-status 03b51d1..dad362b` → `inspection.md` only.
- `grep -rn "_first_commit_where_state_complete\|preserves detection"` across `src/`, `tests/`, `docs/`, and this Change's own artifacts — confirmed every remaining hit is correctly-framed historical narrative, with no stale current-fact claim anywhere, including in `inspection.md` itself.
- `.venv/bin/python -m pytest -q`: **375 passed**. `.venv/bin/forge validate`: exit 0. `.venv/bin/forge doctor`: all 7 PASS. `git diff --check`: clean, both commit-level and across the full branch range.
- Confirmed `resolution-004`'s Execution/Context IDs are distinct from all 8 other provenance records in this Change.

### Assessment against Resolution Verification's bounded authority

- **(a) Is CHG-0012-R004 fixed?** Yes. `inspection.md` now correctly narrates all four attempts and the final decision, explicitly states `_first_commit_where_state_complete` does not exist in the shipped code, and no longer claims pre-seal tampering detection is preserved. Matches the actual shipped code exactly. The trailing-blank-line-at-EOF observation is also fixed.
- **(b) Resolution regression?** No. The diff is a single-file, two-hunk prose edit; no code, test, or config touched.
- **(c) Resolution Scope respected?** Yes — the Resolution Delta is exactly the declared 1-path `scope`, no Out-of-Scope Mutation.
- **(d) Provenance/revision/subject correctness?** `resolution-004` correctly declares `role: resolution`, `targets: [CHG-0012-R004]`, non-empty exact-path `scope`, and an Execution/Context distinct from every prior record. No defect found here.

### Verdict

**PASS**

Finding counts (this Iteration):

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- OBSERVATION: 0
- new_material_findings: 0

CHG-0012-R004 is genuinely closed. Combined with Iteration 4's independent confirmation that the Non-Convergence decision itself is procedurally valid, honestly documented, and correctly implemented, zero unresolved BLOCKER or MAJOR findings remain across all five Iterations. Per C-027, Completion may proceed.
