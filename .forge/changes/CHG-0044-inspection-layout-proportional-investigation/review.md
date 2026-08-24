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
| **Iterations** | 1 |
| **Current Subject** | `80d72e5` |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 0 |
| **Final Iteration** | 1 |
| **Result** | PENDING |

## Current Subject

| | |
|---|---|
| **Subject SHA** | `80d72e5d0a5997ced518dc21318d7ee4d71885f4` |
| **Frozen** | Yes |
| **Iteration** | 1 (resolution refrozen; Iteration 2 pending) |

## Reviewer Independence

Iteration 1 was performed by a freshly spawned `general-purpose` Agent (agent id `af9fd4c8f208c6a50`) with no prior conversation context and no shared reasoning context with the Implementation session — see `provenance.yml` record `reviewer-001`.

## Open Findings

No open findings. R001 and R002 (MAJOR) and R003 (MINOR) were all resolved in the refrozen subject `80d72e5`; resolution is pending independent Iteration 2 confirmation.

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

**Resolution applied (subject refrozen at `80d72e5d0a5997ced518dc21318d7ee4d71885f4`, `implementation-subject-002`):** R001 fixed by re-attributing `Observation` to `CHG-0028`'s "Current state" only, and adding the real `Evidence` (`CHG-0024`/`CHG-0029`) and `Root Cause` (`CHG-0024`/`CHG-0012`) precedent citations. R002 fixed by removing both `§39` references and replacing the `§1` citation with a direct quote of this document's own "Intent" entry convention. R003 fixed by correcting the CHG-0005 description to "two short paragraphs... three sentences total" and the CHG-0012 line count back to 86, consistently across `protocol/artifact-structure.md`, `discovery.md`, `specification.md`, `test-design.md`, `verification.md`, and `plan.md`. Independent Iteration 2 confirmation pending.

## Conclusion

Iteration 1 is REQUEST CHANGES; all three findings (R001, R002 MAJOR; R003 MINOR) have been addressed in the refrozen subject. The Change is not ready for Completion until an independent Iteration 2 confirms the resolution.
