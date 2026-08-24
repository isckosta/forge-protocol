---
forge:
  artifact: review
  schema: 1
change: CHG-0038
status: complete
---

# Review — CHG-0038 Test Design Verification Contract

## Verdict

**PASS** (Iteration 1: REQUEST CHANGES, resolved; Iteration 2: PASS)

## Iteration 1 — REQUEST CHANGES

An independent Reviewer (fresh execution, isolated git worktree, no shared context with the Implementation) evaluated the frozen implementation subject `6cf4ef5342c9b67eb36eb738737a01cbe70dadac`.

### R001 — BLOCKER — Frozen subject fails `forge validate` and the full test suite; `verification.md` claims did not reproduce

Reproduced independently: checking out `6cf4ef5` alone and running `forge validate` fails C-077 ("Plan authorization is missing ... MUST record ... explicit confirmation in plan.md and provenance.yml"), and `python -m pytest -q` reports `1 failed, 652 passed` (`tests/unit/test_unresolved_decisions.py::test_legacy_manifests_are_unaffected`). This is because `provenance.yml` did not exist yet at that commit — it was only added in the next commit, `0e56e5b`. `verification.md`'s "PASS" / "653 passed" claims do not reproduce against the exact subject reviewed.

### R002 — Observation — `Coverage Map` and `Requirement Coverage` overlap with no mechanical consistency check

Acknowledged as an accepted design trade-off (CON-001 explicitly rules out a Markdown parser/validator, per C-067). Not blocking; no action taken.

### R003 — Observation — `protocol/artifact-structure.md`'s "Test Design" entry doesn't enumerate the standalone `## Manual Acceptance` / `## Valid RED` guidance headings in its bullet list

Minor doc-completeness gap in non-binding guidance. Not blocking; no action taken (may be picked up by a future Change if it proves confusing in practice).

### R004 — Observation — Scenario ordering in CHG-0038's own `test-design.md` is non-monotonic (TD-007 appears before TD-006 in document body)

Harmless; Layers are semantic groupings, not required to be numerically ordered. Not blocking; no action taken.

### Checked and found sound

- `test_strategy` template in `_markdown()` is byte-identical to `main`.
- The new `test_design` template's structure matches the updated `protocol/artifact-structure.md` guidance exactly.
- The six new unit tests are substantive (not vacuous), including a `startswith` assertion pinning the exact frontmatter/heading/blockquote prefix.
- `tdd-evidence.yml`'s RED (`5 failed, 1 passed, 25 deselected`, failing for the claimed reason) and GREEN (`31 passed`) evidence reproduced independently.
- No Protocol integer, Change Schema, or `protocol/schemas/` file touched; no parser/validator/BDD framework added.
- Historical `test-design.md` files untouched; no dangling reference to the old heading format or to the removed ERP example anywhere in the repository.
- No dangling `TD-008` references in CHG-0038's own `test-design.md` after its removal.
- `CHANGELOG.md` entry accurate; no scope creep — exactly the 13 declared files touched.

## Resolution Applied

R001 was addressed by adding a **new** `provenance.yml` record, `implementation-subject-002`, pointing at commit `0e56e5ba800cab1d5389473537172e7b3424662a` — the commit whose tree already includes a working `provenance.yml`, so `forge validate` and the full suite (`653 passed`) are independently reproducible when it is checked out directly. `implementation-subject-001` (the record Iteration 1 was reviewed against, permanently bound to `6cf4ef5342c9b67eb36eb738737a01cbe70dadac` since its first commit) was deliberately left untouched: an earlier draft of this fix tried to edit `implementation-subject-001` in place to point at `0e56e5b`, and `forge validate`'s own C-026 check correctly rejected that as rewriting an already-committed subject record. Adding a new record instead of mutating the old one is the correct, C-026-compliant way to advance a frozen subject after resolving a blocking finding. This is a governance-metadata addition only — no renderer, test, or documentation content changed. R002–R004 are non-blocking observations; no change was made for them.

## Iteration 2 — PASS

The same independent Reviewer re-checked out the corrected frozen subject `0e56e5ba800cab1d5389473537172e7b3424662a` (`implementation-subject-002`) in a fresh worktree checkout and confirmed: the working tree is clean at that commit; `git diff 6cf4ef5..0e56e5b --stat` shows only `provenance.yml` (54 insertions) — no renderer, test, or documentation content changed since Iteration 1's content review, so R002–R004 and the "Checked and found sound" list carry forward unchanged; `forge validate` reports "Forge project is valid" (exit 0) and the full suite reports `653 passed, 2 warnings` when run directly at this commit. R001 is resolved and independently reproduced.

### R005 — Minor (non-blocking, resolved) — stale commit/record reference in this file's prose

An intermediate draft of the "Resolution Applied" section above briefly cited a since-superseded record name while the provenance rebind was still being corrected. This did not affect any mechanically-checked field and never appeared in a commit reviewed by the Reviewer; the section above reflects the final, `forge validate`-passing state. No further action needed.

**Strict Review for CHG-0038 is closed with a PASS verdict.**
