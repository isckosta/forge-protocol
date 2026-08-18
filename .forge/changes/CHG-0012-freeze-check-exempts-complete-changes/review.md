---
forge:
  artifact: review
  schema: 1
change: CHG-0012
status: failed
iteration: 1
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
