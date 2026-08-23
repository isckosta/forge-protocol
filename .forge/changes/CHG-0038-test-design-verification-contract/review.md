---
forge:
  artifact: review
  schema: 1
change: CHG-0038
status: active
---

# Review — CHG-0038 Test Design Verification Contract

## Verdict

**PENDING** (Iteration 1: REQUEST CHANGES, resolved; Iteration 2: pending)

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

R001 was addressed by rebinding `provenance.yml` (commit `4ec7e0b1751b47368908ed646d4190d026c82cde`) so `implementation-subject-002` and `verification-001` reference commit `4ec7e0b1751b47368908ed646d4190d026c82cde` (built on `0e56e5b`, the commit whose tree already includes a working `provenance.yml`). This is a governance-metadata rebind only — no renderer, test, or documentation content changed. `forge validate` and the full suite (`653 passed`) are independently reproducible when `4ec7e0b` is checked out directly. R002–R004 are non-blocking observations; no change was made for them.

Iteration 2 re-review of the corrected subject is pending.
