---
forge:
  artifact: review
  schema: 1
change: CHG-0043
status: active
---

# CHG-0043 · Review

## Verdict

**REQUEST CHANGES**

## Review Summary

| | |
|---|---|
| **Iterations** | 1 |
| **Current Subject** | `ca4d5013` |
| **Open Blockers** | 0 |
| **Open Majors** | 1 |
| **Open Minors** | 2 |
| **Final Iteration** | 1 |
| **Result** | REQUEST CHANGES |

## Current Subject

| | |
|---|---|
| **Subject SHA** | `ca4d50132e58c46c7fb85f8d13727bb7662d4a01` |
| **Frozen** | Yes |
| **Iteration** | 1 |

## Reviewer Independence

Independent Execution and Execution Context (isolated Git worktree, fresh agent, no shared context with the Implementation session) — see `provenance.yml` record `reviewer-001`.

## Open Findings

| Finding | Severity | Status | Iteration |
| --- | --- | --- | --- |
| R001 | MAJOR | Open | 1 |
| R002 | MINOR | Open | 1 |
| R003 | MINOR | Open | 1 |

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

## Conclusion

R001 (MAJOR) blocks advance. R002/R003 (MINOR) are non-blocking but were addressed in the same Resolution. A Resolution has corrected all three plus the related R004 observation; independent re-review of the refrozen subject is required before this Change can advance.
