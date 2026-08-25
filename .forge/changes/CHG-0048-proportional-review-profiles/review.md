---
forge:
  artifact: review
  schema: 1
change: CHG-0048
status: complete
---

# CHG-0048 · Review

## Verdict

**PASS.** Iteration 1: REQUEST CHANGES — R-001 (BLOCKER) and R-002 (MAJOR) found and resolved; 3 non-blocking OBSERVATIONs (1 accepted/disclosed, 2 corrected). Iteration 2 (Resolution Verification): **PASS** — both fixes independently re-verified adversarially; one further non-blocking OBSERVATION (R-003, a residual off-by-one in `verification.md`'s own file-count correction) recorded and accepted, not fixed, per C-039. Strict Review for CHG-0048 is closed.

## Review Summary

| | |
|---|---|
| **Iterations** | 2 |
| **Current Subject** | `493371cb00979a19253b3b2ce7c4e03af9f2c524` (Iteration 2's reviewed, passed subject) |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 0 |
| **Final Iteration** | 2 (PASS) |
| **Result** | PASS |

## Current Subject

| | |
|---|---|
| **Subject SHA** | `493371cb00979a19253b3b2ce7c4e03af9f2c524` (Resolution, Iteration 2) |
| **Frozen** | Yes — `provenance.yml`'s `resolution-001` |
| **Iteration** | 2 |

## Reviewer Independence

`provenance.yml`'s `reviewer-001` (Execution `ad6eed539bea23e77`) and `reviewer-002` (Execution `aa5fd11c14137d34e`) records — each a fresh agent invocation in its own isolated Git worktree, sharing no Execution or Execution Context identifier with the Implementation, the Resolution, or each other.

## Open Findings

No open findings. R-003 (OBSERVATION, non-blocking) is recorded and accepted, not fixed, per C-039.

## Iteration 1 — REQUEST CHANGES

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-ad6eed539bea23e77`, no shared context with the Implementation that produced this revision), per C-026. This Review itself ran at the `strict` profile (this Change's own Flow is FULL — `strict` applies unchanged, exactly as it always has), fully adversarial.

**Commit reviewed**: `8c1f0503ca4eae81860664dc887a86fbc3ffca17`.

**Baseline for diff**: `88290f2` (main, i.e. the merged CHG-0047).

### R-001 · BLOCKER — Adapter Review-Profile instruction leaks into Protocol 1 projections, contradicting this Change's own Protocol-1-untouched boundary

`_gate_instructions()` in both `claude_code/projection.py` and `codex/projection.py` substituted `REVIEW_PROFILE_INSTRUCTION[review_profile]` unconditionally — with no `protocol_id` gate, unlike the adjacent Reviewer/Resolver independence block, which already gates on `protocol_id >= 2`. Since Protocol 1 and Protocol 2 projects read the same canonical Flow files (confirmed: no `protocol/versions/1/flows/` directory exists), a Protocol 1 project running `forge adapter install` for either Harness would receive a scoped `focused`/`standard` review instruction that Protocol 1's own unconditional C-022/C-023 ("Every Change MUST undergo Strict Review" / "... MUST actively search for reasons to reject") does not authorize — reproduced directly by calling `_gate_instructions([("fast", open("protocol/flows/fast.yml").read())], protocol_id=1)` and observing the `focused`-profile text in the output.

**Resolution**: both `_gate_instructions()` functions now check `protocol_id >= 2` before substituting the profile-specific instruction; below that, they always render the fixed `"Completion requires Strict Review to pass."` line, mirroring the existing independence-block gate exactly. New regression tests in both Adapters' test suites (`test_projection_uses_fixed_strict_review_instruction_under_protocol_1_even_with_a_profile`) reproduce R-001 as valid RED against the pre-fix code and pass after. See `tdd-evidence.yml`'s `TDD-005`.

### R-002 · MAJOR — `manifest.yml`'s `documentation.impact_evaluated: false` contradicted repository reality and its own `artifacts.documentation: complete`

`manifest.yml` declared `artifacts.documentation: complete` while `documentation.impact_evaluated` remained `false` — even though Documentation Impact evaluation demonstrably occurred (`protocol/compatibility.md` and `CHANGELOG.md` both gained real entries, confirmed by diff). Live-reproduced via `evaluate_merge_readiness()`: `MR-009 | Documentation impact has not been evaluated` fired against the frozen subject, a genuine C-028/C-029 violation, not a "not yet done" condition like the other (expected, pending-Review) diagnostics.

**Resolution**: `documentation.impact_evaluated` corrected to `true`, with a `reason` field matching the convention used by every other historical Change manifest with a completed documentation stage.

### OBSERVATION 1 — `flow.schema.json` allows `profile` to silently diverge from `strict`/`adversarial`; the four touched Schemas are not loaded by any runtime code

Independently confirmed (`grep -rln "flow.schema.json" src/`: no hits) that this is a pre-existing repository pattern, not something this Change introduced — none of `change-v2.schema.json`, `flow.schema.json`, `policy-review-v2.schema.json`, or `project-flow.schema.json` is ever loaded by `src/forge_cli` at runtime. Consequently nothing currently prevents a Flow file from declaring `profile: strict, strict: false` (or any other inconsistent pairing). Blast radius is low (three maintainer-edited canonical Flow files; the only live consumer of `strict`/`adversarial` — `strict_review_required`/`has_strict_review` aggregation — is saturated by the unrelated `"strict_review" in stages` check regardless, independently verified).

**Not fixed** — accepted, disclosed limitation (`verification.md`), consistent with F-010/NFR-001: inventing new schema-loading enforcement is out of this Change's scope. A candidate for a future, narrowly-scoped Change if it ever matters in practice.

### OBSERVATION 2 — `verification.md`'s diff file-count claim was wrong (33 claimed, 35 actual)

Independently reproduced `git diff --stat main..HEAD` against the real frozen subject: **35 files**, not 33; the stated category breakdown itself summed to 34, and omitted the two `docs/rfcs/` files entirely. Every file in the real diff is legitimate and traces to a Functional Requirement — this was a counting/arithmetic error, not a scope or content defect.

**Resolution**: `verification.md`'s Forge Evidence section corrected to the accurate count and category breakdown.

### OBSERVATION 3 — `architecture.md`'s described `flow.schema.json` `required` array didn't match what shipped

Architecture stated `strict`/`adversarial` would stop being `required` once their `const` was relaxed; the shipped schema keeps all four keys (`required`, `profile`, `strict`, `adversarial`) in `required` — stricter, not weaker, than described, and consistent with the actual Specification (FR-008 never promised removing them from `required`).

**Resolution**: `architecture.md` §4 corrected to describe the shipped shape accurately.

### Checked and found sound (Iteration 1)

- Full suite (fresh venv): 784 passed, 2 pre-existing warnings — exact match to the claim at the time of review.
- `tests/contract/`: 52 passed — exact match.
- `forge validate`: PASS — exact match.
- FR-007 ("nothing else changed") verified directly from the diff: `_validate_resolution_verification`/`_validate_protocol2_review_provenance` carry zero new lines.
- C-022/C-023/C-031 Contract text matches FR-005/FR-006 in substance.
- Protocol 1 textual isolation confirmed via empty `git diff` on `protocol/contract/engineering.md`, `protocol/schemas/policy-review.schema.json`, `.claude/skills/forge/references/engineering-contract.md`.
- `review_independence.py`'s independence block confirmed byte-unchanged; only the new `REVIEW_PROFILE_INSTRUCTION` dict was appended.
- `fast.yml`/`standard.yml`'s `strict: false`/`adversarial: false` confirmed not to put Adapter conformance code (`strict_review_required`/`has_strict_review`) at risk, since the `strict_review` stage id remains present in all three Flows regardless.
- TDD-002/TDD-003's retroactively-reconstructed RED evidence independently reproduced against the actual pre-edit commit (`8f15363`).
- `_gate_instructions()` degrades sensibly (no crash) for a Flow document with `review` missing or `null`.
- `_validate_review_profile_floor` fails closed for an unrecognized/typo'd profile string.
- No forbidden pattern (`ReviewProfileEngine`/`Registry`/`Pipeline`) anywhere in code.
- RFC-0005 correctly superseded — content preserved, only status/notice added.
- RFC-0007's rebuttal of RFC-0005's calibration-pilot objection independently judged sound: the pilot existed to bound the risk of an under-calibrated *numeric* threshold; RFC-0007 introduces no score or data-derived threshold at all.
- FR-012 ("derived fresh, never cached") independently reproduced.
- DEC-001's `agent`-authority classification consistent with the actual mechanical rule (`_DEC_AUTHORITY_FLOOR`).
- The three additive Schema changes (`change-v2`, `policy-review-v2`, `project-flow`) verified genuinely additive by reading their diffs.
- `MR-004`'s cosmetic rename verified both statically and live.

## Resolution

R-001 and R-002 were fixed in a Resolution Execution distinct from Iteration 1's Reviewer Execution, in direct response to Iteration 1 (per C-026's Resolver-independence requirement). OBSERVATION 2 and OBSERVATION 3 were corrected in the same session (non-blocking documentation-accuracy fixes, not requiring independent resolution); OBSERVATION 1 was evaluated and explicitly left unfixed as a disclosed, accepted limitation. `tdd-evidence.yml` gained `TDD-005` documenting R-001's RED→GREEN cycle. The resolved revision will be frozen and referenced by `provenance.yml`'s next `resolution-*` record; Iteration 2 (once recorded) independently re-reviews that exact revision.

## Iteration 2 — PASS (Resolution Verification)

**Reviewer**: Independent Reviewer execution (fresh agent invocation, isolated Git worktree at `/home/isckosta/forge-protocol/.claude/worktrees/agent-aa5fd11c14137d34e`, no shared context with the Resolution Execution or with Iteration 1's Reviewer Execution), per C-026. `kind: resolution_verification`, scoped per C-047 to R-001, R-002, defects within the Resolution Delta, and Out-of-Scope Mutation.

**Commit reviewed**: `493371cb00979a19253b3b2ce7c4e03af9f2c524` (frozen Resolution revision).

**Resolution Delta inspected**: `git diff 8c1f0503ca4eae81860664dc887a86fbc3ffca17..493371cb00979a19253b3b2ce7c4e03af9f2c524`.

### R-001 re-verification

Both Adapters now gate the profile-instruction substitution on `protocol_id >= 2`, mirroring the existing independence-block gate exactly. Independently constructed an adversarial matrix (`protocol_id` ∈ {-1, 0, 1, 2, 3}) calling the real public entry points (`generate_claude_code_skill_bundle`/`generate_codex_projection_bundle`) end-to-end, not just the internal function — every value below 2 (including out-of-range `-1`/`0`) correctly falls back to the fixed strict-only line in both Adapters, with identical behavior across both. Confirmed the fixed string exists in exactly one place in `src/` (`review_independence.py`), so the new regression tests cannot pass vacuously. Genuinely fixed.

### R-002 re-verification

Independently confirmed (not trusting the manifest's own claim) that `protocol/compatibility.md` and `CHANGELOG.md` both contain real, substantive CHG-0048 entries matching the `reason` text. Re-ran `evaluate_merge_readiness()` live against this revision: the R-002-related `MR-009` diagnostics from Iteration 1 are gone; only the expected, still-pending `review`/`knowledge_capture` diagnostics remain. Genuinely fixed.

### R-003 · OBSERVATION (non-blocking) — `verification.md`'s corrected file count is itself still off (35/12 claimed, 36/13 actual)

The fix for Iteration 1's OBSERVATION 2 corrected 33→35 files but the real count (independently reproduced: `git diff --stat main HEAD`) is 36 — `discovery.md` was omitted from the Artifacts sub-count (12 claimed vs. 13 actual). Every other category in the breakdown is independently confirmed correct. No bearing on scope, R-001, or R-002 — `discovery.md` is legitimately part of this Change's own Artifact set, already covered by `implementation-subject-001`'s provenance statement.

**Not fixed further** — a second consecutive minor arithmetic slip in the same sentence is genuinely worth a follow-up, but `verification.md` is a reviewable file: correcting it now would require refreezing and a third independent Resolution Verification cycle for a one-line cosmetic number, which is disproportionate (C-039) for something two independent Reviewers have now separately classified non-blocking. Recorded here as a known, accepted inaccuracy instead.

### No Out-of-Scope Mutation

`resolution-001.scope` (9 files) matches commit `493371c`'s own diff exactly, 9-for-9, independently confirmed via `git show 493371c --stat`.

### Checked and found sound (Iteration 2)

- Fresh-venv full suite: 786 passed, 2 warnings — exact match, independently reproduced.
- `tests/unit/test_{claude_code,codex}_projection_gates.py`: 41 passed — exact match to `TDD-005`.
- `forge validate`: PASS.
- Both `projection.py` diffs and the `manifest.yml` diff in commit `493371c` are minimal and surgical (C-013) — no unrelated changes bundled in.
- OBSERVATION 3's `architecture.md` correction independently confirmed accurate against the shipped `flow.schema.json`.

### Verdict

**PASS.** R-001 and R-002 are both genuinely, adversarially fixed with independently reproduced evidence beyond the shipped tests. R-003 (non-blocking) is recorded and accepted, not fixed, per C-039. This closes Strict Review for CHG-0048.

## Conclusion

Iteration 1 (REQUEST CHANGES) and Iteration 2 (Resolution Verification, PASS) are both closed. No BLOCKER or MAJOR finding remains open. Strict Review is complete for this Change; remaining Completion Gate checks (blocking review threads resolved — trivially satisfied, no external review surface — and TDD compliance, already `compliant`) are satisfied.
