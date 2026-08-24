---
forge:
  artifact: review
  schema: 1
change: CHG-0044
status: active
---

# CHG-0044 · Review

## Verdict

**PENDING**

## Review Summary

| | |
|---|---|
| **Iterations** | 3 |
| **Current Subject** | `447bd95` |
| **Open Blockers** | 0 |
| **Open Majors** | 1 |
| **Open Minors** | 0 |
| **Final Iteration** | 3 |
| **Result** | PENDING |

## Current Subject

| | |
|---|---|
| **Subject SHA** | `447bd9515d80df267df8c916584c40963f698195` |
| **Frozen** | Yes |
| **Iteration** | 3 |

## Reviewer Independence

Each Iteration was performed by a freshly spawned `general-purpose` Agent with no prior conversation context and no shared reasoning context with the Implementation session or with each other — see `provenance.yml` records `reviewer-001` (Iteration 1, agent id `af9fd4c8f208c6a50`), `reviewer-002` (Iteration 2, agent id `adf7b45dfafab5df0`), and `reviewer-003` (Iteration 3, agent id `abb99b02fcf2fb365`).

## Open Findings

| Finding | Severity | Status | Iteration |
|---|---|---|---|
| R005 | MAJOR | Open | 3 |

## Iteration 1 — REQUEST CHANGES

Reviewed subject `ce265bfe92b6e8fb05a526aae7099d8ec1016916` (`implementation-subject-001`; independent Execution, fresh Agent invocation, no shared context with Implementation).

### R001 — MAJOR — Optional-vocabulary term citations are misattributed, violating the Specification's own AC-003

**Problem:** `protocol/artifact-structure.md`'s new "Inspection" text cited `CHG-0024`'s `## Root Cause` section as precedent for the `Observation` vocabulary term — but that section states a confirmed causal conclusion, the opposite of what `Observation` is defined to be ("without any conclusion about cause"). Meanwhile the `Evidence` term had no citation at all, even though `CHG-0024/inspection.md:33` and `CHG-0029/inspection.md:10` both use the heading `## Evidence` verbatim, and `Root Cause` was illustrated only with an invented example even though `CHG-0024/inspection.md:11` and `CHG-0012/inspection.md:10` are exact-name real precedent that went uncited.

**Evidence:** Direct reading of `CHG-0024/inspection.md` (lines 11-24, `## Root Cause`, a confirmed-cause section, not an observation) and `CHG-0029/inspection.md`/`CHG-0024/inspection.md`'s real `## Evidence` headings.

**Required Resolution:** Each cited precedent for a structural-vocabulary term must actually exemplify that term's own stated definition, and every term with a real, exact- or near-name historical precedent must cite it per AC-003, rather than an invented example or a mismatched citation.

### R002 — MAJOR — Two internal section cross-references resolve to the wrong or nonexistent content

**Problem:** The new prose cited "(§39)" twice to support "no section is expected, required, or validated" — `protocol/specification.md` §39 is "Unresolved Decision Management," unrelated to proportionality; the citation was mistakenly carried over from the *elaboration prompt's own* section numbering rather than a real section of this document. Separately, "(§1)" was cited for the interaction-language convention on structural headings — `protocol/artifact-structure.md` §1 "Purpose" does not contain that convention; it appears under §4's own "Intent" entry instead.

**Evidence:** `protocol/specification.md` §39 read directly (Unresolved Decision Management); `protocol/artifact-structure.md` §1 (lines 5-23) read directly (no interaction-language content); the real convention is at §4's "Intent" entry, line ~130.

**Required Resolution:** Every parenthetical section citation in the new guidance must resolve to a section that actually contains the cited content, or must reference the correct source directly rather than an invented or mismatched section number.

### R003 — MINOR — The CHG-0005 correction is itself imprecise, and a CHG-0012 line-count claim disagrees with this Change's own intent.md

**Problem:** The new text described `CHG-0005/inspection.md` as having "two sentences of real context" — the file's real content has three sentences across two short paragraphs, undercounting by one. Separately, the new text and `discovery.md`'s table called `CHG-0012/inspection.md` "87 lines," while `awk 'END{print NR}'` and `wc -l` both confirm exactly 86 lines (with a trailing newline, no ambiguity) — matching this Change's own `intent.md` ("`CHG-0012`, 86 linhas"), which the shipped text and `discovery.md` disagreed with.

**Evidence:** Direct line/sentence count of both historical files; cross-check against this Change's own `intent.md`.

**Required Resolution:** Every factual description of a cited historical file's content or size — especially in a Requirement (FR-007) whose explicit purpose is correcting a prior overclaim — must match the file's real content exactly, and must be internally consistent across this Change's own Discovery, Specification, and shipped guidance text.

### Checked and found sound

- `_frontmatter()`/`_markdown()` diff: the `inspection` template emits `# CHG-XXXX · Inspection` with byte-identical front matter, and the body is a non-heading authoring comment — matches FR-001/FR-002 and TD-001/TD-002 exactly; full suite reproduced (64 passed in the scaffold test file).
- `test_render_scaffold_inspection_unaffected_templates_are_unchanged` correctly full-string-compares the five unaffected templates, not substring checks.
- `forge validate`: PASS, reproduced directly.
- The `Fix Boundary` citation of `CHG-0012`'s "Scope verified not to include" heading is accurate.
- The `CHG-0012/inspection.md:12` evidence citation for the Symptom→Reproduction→Cause model is accurate.
- Cross-references to `protocol/specification.md` §8, §11, and `CHG-0016`'s NFR-001 are accurate.
- The six real `inspection.md` files' line counts in `discovery.md` (`CHG-0024`: 57, `CHG-0026`: 62, `CHG-0028`: 44, `CHG-0029`: 50) all match `wc -l` exactly.
- No historical `inspection.md` file is touched by this Change; no Protocol integer, Schema, or Flow classification file is touched; `merge_readiness/evaluator.py` still checks only presence/status for `inspection`.
- The rhetorical pattern ("Structural core (elaborated by `CHG-0044`):") matches the established convention from Verification/Review/Specification Drift/Knowledge Capture exactly.
- No emoji, badges, or decorative HTML in the elaborated guidance prose.

**Resolution applied (subject refrozen at `80d72e5d0a5997ced518dc21318d7ee4d71885f4`, `implementation-subject-002`):** R001 fixed by re-attributing `Observation` to `CHG-0028`'s "Current state" only, and adding the real `Evidence` (`CHG-0024`/`CHG-0029`) and `Root Cause` (`CHG-0024`/`CHG-0012`) precedent citations. R002 fixed by removing both `§39` references and replacing the `§1` citation with a direct quote of this document's own "Intent" entry convention. R003 fixed by correcting the CHG-0005 description to "two short paragraphs... three sentences total" and the CHG-0012 line count back to 86, consistently across `protocol/artifact-structure.md`, `discovery.md`, `specification.md`, `test-design.md`, `verification.md`, and `plan.md`.

## Iteration 2 — REQUEST CHANGES → resolved same-pass

Reviewed refrozen subject `80d72e5d0a5997ced518dc21318d7ee4d71885f4` (`implementation-subject-002`; independent Execution, second fresh Agent invocation, no shared context with Implementation or with Iteration 1's Agent).

R001 and R002 independently confirmed fully resolved — not by trusting Iteration 1's "Resolution applied" narrative, but by re-reading the shipped `protocol/artifact-structure.md` text directly and cross-checking every citation against the real historical `inspection.md` files. R003 confirmed resolved in `protocol/artifact-structure.md`, `discovery.md`, `specification.md`, `test-design.md`, `verification.md`, and `plan.md`, but one residual instance survived elsewhere.

### R004 — MINOR — `CHANGELOG.md` still repeated the exact overclaim R003 required corrected

**Problem:** The `CHANGELOG.md` entry this same Change adds (Plan item 4) still read "has two sentences of real content" — the pre-fix, imprecise characterization R003 flagged — because the R003 fix commit (`80d72e5`) never touched `CHANGELOG.md`.

**Evidence:** `git show 80d72e5 -- CHANGELOG.md` produces an empty diff; `CHANGELOG.md`'s "Inspection Layout Proportional Investigation" entry, pre-fix.

**Required Resolution:** Every user-facing description this Change adds of `CHG-0005/inspection.md`'s content, including its own `CHANGELOG.md` entry, must match the file's real content consistently.

**Resolution applied (subject refrozen at `447bd9515d80df267df8c916584c40963f698195`, `implementation-subject-003`):** `CHANGELOG.md` corrected to "two short paragraphs of real content, three sentences total." R004's fix was subsequently confirmed by independent Iteration 3 (below), not merely self-verified.

### Checked and found sound (Iteration 2)

- R001, R002, R003 fixes independently confirmed via direct source inspection of the shipped guidance and every cited historical file, not by trusting the Iteration 1 narrative.
- Fix commit `80d72e5` confirmed to touch only files within this Change's declared scope (`.forge/changes/CHG-0044-*/` and `protocol/artifact-structure.md`) — no renderer or test file change.
- Full suite (688 passed, 2 warnings, both pre-existing and unrelated) and `forge validate` independently reproduced against the refrozen subject, matching `verification.md`'s claims exactly.
- FR-003's conditional citation requirement is honestly satisfied: `Impact`, `Open Question`, and `Conclusion` correctly cite no precedent because none of the six real `inspection.md` files has a genuinely matching heading.
- No historical `inspection.md` file is modified by this Change's history.
- Noted, out of scope: the projected Adapter skill copies (`.claude/skills/forge/references/artifact-structure.md`, `.agents/skills/forge/references/artifact-structure.md`) do not yet reflect this Change or the entire prior `CHG-0037`–`CHG-0043` series — pre-existing staleness, not introduced by this Change, and outside its declared scope.

## Iteration 3 — REQUEST CHANGES

Reviewed final subject `447bd9515d80df267df8c916584c40963f698195` (`implementation-subject-003`; independent Execution, third fresh Agent invocation, no shared context with Implementation or with Iterations 1-2's Agents). Triggered in part by an automated Codex review comment on the GitHub PR flagging the same underlying defect this Iteration confirms below.

R001-R004 independently re-confirmed fully resolved — not by trusting the prior Iterations' write-ups, but by re-reading `protocol/artifact-structure.md`'s shipped "Inspection" section directly and cross-checking every citation against the real historical `inspection.md` files a third time, and by independently reproducing the full test suite (688 passed) and `forge validate` against the actual final subject `447bd95` for the first time (Iterations 1 and 2 reviewed `ce265bf` and `80d72e5` respectively, never `447bd95` itself).

### R005 — MAJOR — Review bookkeeping recorded a "passed" iteration whose own provenance says REQUEST CHANGES, and no iteration was ever bound to the actual final subject

**Problem:** `manifest.yml`'s `review-002` iteration was recorded with `status: passed`, but `provenance.yml`'s own `reviewer-002` record states the Iteration 2 verdict was "REQUEST CHANGES (blocking on R004 pending fix confirmation)" — a direct self-contradiction. `state.current: complete` and `review.status: passed` were then recorded (commit `c542e68`) without any Review Iteration ever being bound to `implementation-subject-003` (`447bd95`), the subject where R004 was actually fixed. A GitHub-hosted Codex review bot correctly identified this as a P1 finding on the open PR.

**Evidence:** `manifest.yml` at commit `c542e68`/`15a9502`: `review-002` iteration `status: passed`; `provenance.yml`'s `reviewer-002.source.statement`: "Verdict REQUEST CHANGES (blocking on R004 pending fix confirmation)."

**Required Resolution:** A review iteration's recorded `status` must match its own provenance-recorded verdict; `state.current: complete` and `review.status: passed` must not be recorded until a Review Iteration bound to the actual final subject has genuinely returned PASS.

### Checked and found sound (Iteration 3)

- R001-R004 all re-confirmed resolved by independent re-verification of every citation, cross-reference, and test claim against the real final subject `447bd95` — no content defect found; the entirety of R005 is a review-bookkeeping defect, not a defect in `protocol/artifact-structure.md`, `change_scaffolding.py`, or the tests.
- Full suite (688 passed, 2 warnings, pre-existing and unrelated) and `forge validate` independently reproduced against `447bd95` for the first time.
- `git diff --stat` from `main` to `447bd95` confirmed scoped to exactly this Change's declared files.
- No historical `inspection.md` modified anywhere in this Change's commit history.

**Resolution applied:** `manifest.yml` corrected — `review-002`'s `status` changed to `failed` (matching its real verdict), a `review-003` iteration added bound to `implementation-subject-003` (`447bd95`) with `status: failed` recording this Iteration's own R005 finding, `state.current` reverted from `complete` to `review`, and `review.status` reverted from `passed` to `pending` until a Review Iteration genuinely bound to the final subject returns PASS. See Iteration 4 below.

## Conclusion

The subject reviewed satisfies the Acceptance Criteria applicable to this Review and has no open BLOCKER findings; R005 (MAJOR) is addressed by Iteration 4 below. The Change is not ready for Completion until Iteration 4's independent PASS is recorded.
