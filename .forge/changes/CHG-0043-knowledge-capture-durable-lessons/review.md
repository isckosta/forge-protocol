---
forge:
  artifact: review
  schema: 1
change: CHG-0043
status: active
---

# CHG-0043 · Review

## Verdict

**PASS**

## Review Summary

| | |
|---|---|
| **Iterations** | 3 |
| **Current Subject** | `15a5b459` |
| **Open Blockers** | 0 |
| **Open Majors** | 0 |
| **Open Minors** | 2 |
| **Final Iteration** | 3 |
| **Result** | PASS |

## Current Subject

| | |
|---|---|
| **Subject SHA** | `15a5b459ab7ff5b25a12c76f0bae5632ab028bcb` |
| **Frozen** | Yes |
| **Iteration** | 3 |

## Reviewer Independence

Each Iteration was performed by an independent Execution and Execution Context (isolated Git worktree, fresh agent, no shared context with the Implementation session or with each other) — see `provenance.yml` records `reviewer-001` (Iteration 1), `reviewer-002` (Iteration 2), and `reviewer-003` (Iteration 3).

## Open Findings

| Finding | Severity | Status | Iteration |
| --- | --- | --- | --- |
| R005 | OBSERVATION | Open | 2 |
| R006 | MINOR | Open | 2 |
| R007 | MINOR | Open | 3 |

## Iteration 1 — REQUEST CHANGES

Reviewed subject `ca4d50132e58c46c7fb85f8d13727bb7662d4a01` (`implementation-subject-001`; independent Execution, isolated worktree, no shared context with Implementation).

### R001 — MAJOR — Protection test does not establish the "byte-identical" claim it is cited for

**Problem:** `verification.md` cites `test_render_scaffold_knowledge_capture_unaffected_templates_are_unchanged` as confirming the five unaffected templates are byte-identical, but the test used a tail-only `.endswith()` check for `review.md` (missing four of its six subsections — `Verdict`, `Review Summary`, `Current Subject`, `Reviewer Independence` were entirely unchecked) and a bare substring check for `tasks.md` (`"No task has started." in ...`, no equality at all, leaving the Overview table, Execution section, and `T-001` checklist item unchecked). This is exactly the anti-pattern `test-design.md`'s own TD-007 Failure Condition warns against. Direct source inspection confirmed no actual regression exists in either template, but the automated evidence backing the claim was incomplete for 2 of 5 templates.

**Evidence:** `tests/unit/test_change_scaffolding.py:895-925` (pre-fix) — the `review.md` assertion covered only its last two headings; the `tasks.md` assertion was `assert "No task has started." in plan.files["tasks.md"]`.

**Required Resolution:** The protection test must establish full-section equality for every one of the five unaffected templates, not a tail fragment or bare substring.

### R002 — MINOR — Overclaimed uniformity in a precedent citation

**Problem:** `protocol/artifact-structure.md`'s new "Knowledge Capture" section stated `CHG-0013`, `CHG-0015`, `CHG-0016`, `CHG-0036` "all reference" a `docs/adr/`/`docs/rfcs/` entry "this way" (via a structured `References` section) — only `CHG-0036` actually has a `## References` heading; `CHG-0013`/`CHG-0015`/`CHG-0016` predate the structural redesign and mention the same real ADR practice in unstructured prose, with no section headings at all.

**Evidence:** Direct reading of all four historical `knowledge-capture.md` files.

**Required Resolution:** Describe the two real forms accurately rather than implying structural uniformity across all four.

### R003 — MINOR — Unresolved cross-reference placeholder

**Problem:** `discovery.md` line 31 left a literal `§?` placeholder citing `protocol/specification.md`'s minimum-lifecycle list, never filled in with the real section number.

**Evidence:** `protocol/specification.md` §10 ("FULL") is the real section.

**Required Resolution:** Fill in the real section number.

### Checked and found sound

- All rendered-output structural claims independently verified true via a direct `render_scaffold` call, not the test suite alone.
- Tests pass at the claimed counts (61 / 685); `forge validate` clean.
- The five unaffected templates confirmed genuinely byte-identical by direct diff inspection (the finding is about the test's coverage, not an actual regression).
- The `CHG-0016` (multi-lesson) and `CHG-0033`/`35`/`36` (single-lesson prose) precedent citations substantively accurate.
- FER characterization accurate against `docs/experience-reporting.md`.
- `CHANGELOG.md` entry accurate.
- Diff scope outside the Change's own directory confirmed exactly the 4 claimed files.
- The new test's `re.split(r"(?m)^## ", ...)` section-splitting logic confirmed sound — independently verified that the literal `### K-xxx` substring inside the `Durable Knowledge` paragraph never triggers a false split, since it is not at the start of a line.

### OBSERVATION — R004: AC-002 ambiguity between scaffold and documentation

`specification.md`'s AC-002 required the "generated guidance" to cite a real precedent for each `Durable Knowledge` mode, without specifying whether that meant the rendered scaffold template or the elaborated `protocol/artifact-structure.md` documentation; `test-design.md`'s TD-002 silently narrowed this to the scaffold only, which never literally cites `CHG-0016`/`CHG-0033`/`35`/`36`. Not blocking (the citations do exist within the Change's scope, in the documentation), but addressed alongside R001-R003 by splitting FR-002/AC-002 explicitly between the two surfaces.

## Iteration 2 — PASS

Reviewed refrozen subject `3b1a553aa12931d74b2399ae3307f13fbb9cb8c7` (`implementation-subject-002`; independent Execution, isolated worktree, no shared context with Implementation or with Iteration 1).

R001 confirmed fully resolved — not merely by reading the diff, but by an injected temporary regression (one word changed deep inside `review.md`'s `## Current Subject` guidance sentence in `change_scaffolding.py`), confirming the strengthened protection test actually fails when it should, then confirming it passes again after reverting. R002, R003, and R004 confirmed fully resolved by direct source inspection. No Out-of-Scope Mutation: the fix commit `3b1a553` touches exactly the four files claimed (`discovery.md`, `specification.md`, `protocol/artifact-structure.md`, `tests/unit/test_change_scaffolding.py`) — no renderer behavior change.

### R005 — OBSERVATION — `verification.md`/`test-design.md` were not updated for the AC-002 split

**Problem:** When FR-002/AC-002 was split between scaffold-content and documentation-content claims (resolving R004), `verification.md`'s Acceptance Coverage still cites only `TDD-001` for AC-002, which does not distinguish the two clauses the split introduced.

**Evidence:** `verification.md`'s Acceptance Coverage table, AC-002 row.

**Required Resolution:** Not required to unblock this Change (OBSERVATION, non-blocking) — a future pass over `verification.md` could cite the documentation-inspection evidence for AC-002's second clause distinctly from `TDD-001`.

### R006 — MINOR — Same overclaim pattern left uncorrected in `discovery.md`

**Problem:** `discovery.md` (lines ~147-149, untouched by the R002 fix) still states real References sections "already point to these (`CHG-0013`, `CHG-0015`, `CHG-0016` all reference...)" — the same structural-uniformity overclaim R002 corrected in `protocol/artifact-structure.md`, left uncorrected in the non-normative Discovery artifact.

**Evidence:** `discovery.md`, "Promotion to permanent documentation" subsection.

**Required Resolution:** Not required to unblock this Change (MINOR, non-blocking, confined to a non-normative artifact) — left open per C-049's deterministic termination, matching this repository's own established precedent (`CHG-0041`'s Iteration 3) of not chasing a non-blocking finding into a further iteration cycle.

### Checked and found sound (Iteration 2)

- R001's fix independently proven via injected regression, not just diff-reading.
- R002, R003, R004 fixes independently confirmed via direct source inspection.
- Full suite (685 passed, 2 warnings) and `forge validate` reproduced against the refrozen subject.
- Fix commit scope confirmed exactly the 4 claimed files, no renderer change.
- Overall diff scope from `main` confirmed unchanged: `CHANGELOG.md`, `protocol/artifact-structure.md`, `src/forge_cli/change_scaffolding.py`, `tests/unit/test_change_scaffolding.py`, outside the Change's own directory.

## Iteration 3 — PASS

Reviewed refrozen subject `15a5b459ab7ff5b25a12c76f0bae5632ab028bcb` (`implementation-subject-003`; independent Execution, isolated worktree, no shared context with Implementation or with Iterations 1-2). Triggered by an automated Codex review on the GitHub PR (not one of R001-R006): `protocol/artifact-structure.md` claimed all 25 real `knowledge-capture.md` files "already use" the exact four-heading structured form; only 7 actually do.

Independently re-counted: a script scanning `##` headings across all 25 real `knowledge-capture.md` files confirmed exactly 7 match precisely (`CHG-0021`, `CHG-0022`, `CHG-0023`, `CHG-0030`, `CHG-0033`, `CHG-0035`, `CHG-0036`), matching the fix's claim exactly; spot-checked 3 of the other 18 (`CHG-0016`: zero headings; `CHG-0007`: 6 different headings; `CHG-0001`: one different heading with `###` sub-headings) and confirmed all genuinely non-matching. Fix commit `15a5b45` confirmed to touch only `protocol/artifact-structure.md`. Full suite (685 passed, 2 warnings) and `forge validate` reproduced against the refrozen subject.

### R007 — MINOR — Pre-existing miscount of `CHG-0016`'s lesson count

**Problem:** `protocol/artifact-structure.md`'s Knowledge Capture section states `CHG-0016`'s `knowledge-capture.md` has "seven distinct lessons"; the actual top-level bullet count is 9. Discovered during the full-section read this Iteration required, not introduced by the `15a5b45` fix itself (present verbatim in the parent commit too).

**Evidence:** Direct count of `CHG-0016/knowledge-capture.md`'s top-level bullets.

**Required Resolution:** Not required to unblock this Change (MINOR, non-blocking) — left open per C-049's deterministic termination, matching the same pattern already applied to R005/R006.

### Checked and found sound (Iteration 3)

- The "exactly 7 of 25" claim independently re-verified true via an independent script, not by trusting the commit message.
- Corrected guidance text confirmed accurate and internally consistent with the surrounding `CHG-0016`/`CHG-0033`/`35`/`36` precedent discussion.
- Fix commit scope confirmed exactly 1 file; overall diff scope from `main` confirmed unchanged.
- `CHANGELOG.md` checked and confirmed it does not repeat the "all 25" overclaim — no update needed there.

## Conclusion

The subject reviewed satisfies the Acceptance Criteria applicable to this Review and has no open BLOCKER or MAJOR findings; one non-blocking OBSERVATION (R005) and two non-blocking MINORs (R006, R007) remain open, consistent with C-049's deterministic termination. The Change is ready for the next gate defined by its Flow.
